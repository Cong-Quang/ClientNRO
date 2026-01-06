import asyncio
import time
import math
from typing import Dict, List, Optional, Tuple, Callable
from enum import Enum
from logs.logger_config import logger


class BossState(Enum):
    """Enum cho các trạng thái của Auto Boss"""
    IDLE = "IDLE"
    SEARCHING = "SEARCHING"
    NAVIGATING = "NAVIGATING"
    ZONE_SCANNING = "ZONE_SCANNING"
    GATHERING = "GATHERING"
    ATTACKING = "ATTACKING"
    RECOVERING = "RECOVERING"


class BossHuntCoordinator:
    """
    Singleton quản lý phối hợp giữa nhiều user khi săn boss.
    Chỉ phối hợp giữa các user trong cùng group.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BossHuntCoordinator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Map boss_name -> list of hunters
        self.active_hunts: Dict[str, List['AutoBoss']] = {}
        
        # Map boss_name -> (map_id, zone_id) when found
        self.boss_found_events: Dict[str, Tuple[int, int]] = {}
        
        # Map boss_name -> {group_id -> {username -> [zone_ids]}}
        self.zone_assignments: Dict[str, Dict[str, Dict[str, List[int]]]] = {}
        
        # SYNC BARRIER: Track hunters ready for zone assignment
        # Map boss_name -> {group_id -> set(usernames)}
        self.ready_hunters: Dict[str, Dict[str, set]] = {}
        
        self._initialized = True
    
    def register_hunter(self, boss_name: str, hunter: 'AutoBoss'):
        """Đăng ký user vào nhóm săn boss"""
        if boss_name not in self.active_hunts:
            self.active_hunts[boss_name] = []
        
        if hunter not in self.active_hunts[boss_name]:
            self.active_hunts[boss_name].append(hunter)
            logger.info(f"[Coordinator] Đăng ký {hunter.username} vào săn boss '{boss_name}'")
    
    def unregister_hunter(self, boss_name: str, hunter: 'AutoBoss'):
        """Hủy đăng ký user"""
        if boss_name in self.active_hunts and hunter in self.active_hunts[boss_name]:
            self.active_hunts[boss_name].remove(hunter)
            logger.info(f"[Coordinator] Hủy đăng ký {hunter.username} khỏi săn boss '{boss_name}'")
            
            # Cleanup empty entries
            if not self.active_hunts[boss_name]:
                del self.active_hunts[boss_name]
                if boss_name in self.boss_found_events:
                    del self.boss_found_events[boss_name]
                if boss_name in self.zone_assignments:
                    del self.zone_assignments[boss_name]
    
    def get_hunters_in_group(self, boss_name: str, group_id: str) -> List['AutoBoss']:
        """Lấy danh sách hunters trong cùng group"""
        if boss_name not in self.active_hunts:
            return []
        
        return [h for h in self.active_hunts[boss_name] if h.group_id == group_id]
    
    def assign_zones(self, boss_name: str, group_id: str, total_zones: int) -> Dict[str, List[int]]:
        """
        Chia zone cho các hunter - ROUND-ROBIN để spread out
        Returns: Dict mapping username -> list of zone IDs
        """
        hunters = self.get_hunters_in_group(boss_name, group_id)
        if not hunters:
            return {}
        
        # Initialize assignment structure
        if boss_name not in self.zone_assignments:
            self.zone_assignments[boss_name] = {}
        if group_id not in self.zone_assignments[boss_name]:
            self.zone_assignments[boss_name][group_id] = {}
        
        assignments = {}
        num_hunters = len(hunters)
        
        # Sort hunters by username for consistency
        sorted_hunters = sorted(hunters, key=lambda h: h.username)
        
        # ROUND-ROBIN: Spread accounts across zones
        # Example: 12 zones, 3 accounts
        # Account 0: [0, 3, 6, 9]
        # Account 1: [1, 4, 7, 10]
        # Account 2: [2, 5, 8, 11]
        for i in range(total_zones):
            hunter_idx = i % num_hunters
            hunter = sorted_hunters[hunter_idx]
            username = hunter.username
            
            if username not in assignments:
                assignments[username] = []
            assignments[username].append(i)
        
        self.zone_assignments[boss_name][group_id] = assignments
        logger.info(f"[Coordinator] Chia {total_zones} zones cho {num_hunters} hunters (round-robin spread)")
        for username, zones in assignments.items():
            logger.info(f"[Coordinator]   {username}: zones {zones} ({len(zones)} zones)")
        
        return assignments
    
    def mark_ready(self, boss_name: str, group_id: str, username: str):
        """Mark hunter as ready for zone assignment"""
        if boss_name not in self.ready_hunters:
            self.ready_hunters[boss_name] = {}
        if group_id not in self.ready_hunters[boss_name]:
            self.ready_hunters[boss_name][group_id] = set()
        
        self.ready_hunters[boss_name][group_id].add(username)
        logger.info(f"[Coordinator] {username} marked ready ({len(self.ready_hunters[boss_name][group_id])} ready)")
    
    async def wait_for_all_ready(self, boss_name: str, group_id: str, timeout: float = 5.0) -> bool:
        """
        Wait for all registered hunters to mark ready
        Returns True if all ready, False if timeout
        """
        hunters = self.get_hunters_in_group(boss_name, group_id)
        expected_count = len(hunters)
        
        if expected_count == 0:
            return True
        
        logger.info(f"[Coordinator] Waiting for {expected_count} hunters to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            ready_set = self.ready_hunters.get(boss_name, {}).get(group_id, set())
            ready_count = len(ready_set)
            
            if ready_count >= expected_count:
                logger.info(f"[Coordinator] All {expected_count} hunters ready!")
                return True
            
            await asyncio.sleep(0.1)
        
        # Timeout - proceed with whoever is ready
        ready_count = len(self.ready_hunters.get(boss_name, {}).get(group_id, set()))
        logger.info(f"[Coordinator] Timeout - proceeding with {ready_count}/{expected_count} hunters")
        return False
    
    def broadcast_boss_found(self, boss_name: str, group_id: str, map_id: int, zone_id: int):
        """Thông báo tìm thấy boss tới tất cả hunters trong group"""
        key = f"{boss_name}_{group_id}"
        self.boss_found_events[key] = (map_id, zone_id)
        
        hunters = self.get_hunters_in_group(boss_name, group_id)
        logger.info(f"[Coordinator] 📢 Broadcast boss '{boss_name}' tại zone {zone_id} tới {len(hunters)} hunters trong group '{group_id}'")
        
        for hunter in hunters:
            asyncio.create_task(hunter._on_boss_found_by_team(map_id, zone_id))
    
    def get_boss_location(self, boss_name: str, group_id: str) -> Optional[Tuple[int, int]]:
        """Lấy vị trí boss nếu đã tìm thấy (trong group)"""
        key = f"{boss_name}_{group_id}"
        return self.boss_found_events.get(key)
    
    def is_boss_found(self, boss_name: str, group_id: str) -> bool:
        """Kiểm tra boss đã được tìm thấy chưa (trong group)"""
        key = f"{boss_name}_{group_id}"
        return key in self.boss_found_events
    
    def get_hunter_count(self, boss_name: str, group_id: str) -> int:
        """Đếm số user trong group đang săn boss này"""
        return len(self.get_hunters_in_group(boss_name, group_id))


class AutoBoss:
    """
    State machine quản lý quy trình săn boss cho 1 user.
    Bao gồm: tìm boss, di chuyển, quét zone, tập hợp team, attack.
    """
    
    def __init__(self, controller):
        self.controller = controller
        self.username = controller.account.username
        
        # State management
        self.state = BossState.IDLE
        self.is_running = False
        
        # Target boss info
        self.target_boss_name = ""
        self.target_map_id = -1
        self.target_zone_id = -1
        
        # Boss queue for sequential hunting
        self.boss_queue: List[str] = []
        self.current_boss_index = 0
        self.use_queue_mode = False  # True if using queue, False if single boss
        
        # Group coordination
        self.group_id = ""
        self.coordinator = BossHuntCoordinator()
        
        # Zone scanning
        self.assigned_zones: List[int] = []
        self.current_zone_index = 0
        self.zone_change_retry_count = 0
        self.max_zone_retry = 3
        
        # Death recovery
        self.last_scanned_map_id = -1
        self.last_scanned_zone_id = -1
        
        # Team gathering
        self.gathering_timeout = 10.0  # 10 seconds
        self.gathering_start_time = 0
        
        # Boss status monitoring
        self.last_boss_check_time = 0
        self.boss_check_interval = 5.0  # Check every 5 seconds
        
        # Main loop task
        self.loop_task = None
    
    def start(self, boss_name: str):
        """Bắt đầu săn boss (single mode)"""
        if self.is_running:
            logger.info(f"[{self.username}] Auto boss đang chạy, dừng trước khi start mới")
            self.stop()
        
        self.use_queue_mode = False
        self.target_boss_name = boss_name
        self.group_id = self._get_group_id()
        self.state = BossState.SEARCHING
        self.is_running = True
        
        # Register vào coordinator
        self.coordinator.register_hunter(boss_name, self)
        
        # Start main loop
        self.loop_task = asyncio.create_task(self._main_loop())
        
        logger.info(f"[{self.username}] 🎯 Bắt đầu Auto Boss: '{boss_name}' (Group: {self.group_id})")
    
    def add_to_queue(self, boss_name: str, use_fuzzy: bool = True):
        """Thêm boss vào queue, hỗ trợ fuzzy matching"""
        if not use_fuzzy:
            # Exact match mode
            if boss_name not in self.boss_queue:
                self.boss_queue.append(boss_name)
                logger.info(f"[{self.username}] ➕ Thêm vào queue: '{boss_name}' (Vị trí: {len(self.boss_queue)-1})")
            else:
                logger.info(f"[{self.username}] Boss '{boss_name}' đã có trong queue")
        else:
            # Fuzzy matching mode: tìm tất cả boss chứa keyword
            from logic.boss_manager import BossManager
            boss_manager = BossManager()
            
            matching_bosses = boss_manager.find_bosses_by_keyword(boss_name)
            
            if not matching_bosses:
                logger.info(f"[{self.username}] Không tìm thấy boss nào chứa '{boss_name}'")
                return 0
            
            added_count = 0
            for boss in matching_bosses:
                full_boss_name = boss['name']
                if full_boss_name not in self.boss_queue:
                    self.boss_queue.append(full_boss_name)
                    added_count += 1
            
            if added_count > 0:
                logger.info(f"[{self.username}] ➕ Tìm thấy {len(matching_bosses)} boss chứa '{boss_name}', thêm {added_count} boss mới vào queue")
            else:
                logger.info(f"[{self.username}] Tất cả {len(matching_bosses)} boss chứa '{boss_name}' đã có trong queue")
            
            return added_count
    
    def clear_queue(self):
        """Xóa toàn bộ queue"""
        self.boss_queue.clear()
        self.current_boss_index = 0
        logger.info(f"[{self.username}] 🗑️ Đã xóa queue")
    
    def show_queue(self) -> str:
        """Hiển thị queue hiện tại"""
        if not self.boss_queue:
            return "Queue trống"
        
        result = f"Boss Queue ({len(self.boss_queue)} bosses):\n"
        for i, boss_name in enumerate(self.boss_queue):
            marker = ">>> " if i == self.current_boss_index and self.is_running else "    "
            result += f"{marker}[{i}] {boss_name}\n"
        return result
    
    def start_queue(self):
        """Bắt đầu săn boss theo queue"""
        if not self.boss_queue:
            logger.info(f"[{self.username}] Queue trống! Dùng 'autoboss queue <tên boss>' để thêm boss")
            return
        
        if self.is_running:
            logger.info(f"[{self.username}] Auto boss đang chạy, dừng trước khi start queue")
            self.stop()
        
        self.use_queue_mode = True
        self.current_boss_index = 0
        self.target_boss_name = self.boss_queue[0]
        self.group_id = self._get_group_id()
        self.state = BossState.SEARCHING
        self.is_running = True
        
        # Register vào coordinator
        self.coordinator.register_hunter(self.target_boss_name, self)
        
        # Start main loop
        self.loop_task = asyncio.create_task(self._main_loop())
        
        logger.info(f"[{self.username}] 🎯 Bắt đầu Queue Mode: {len(self.boss_queue)} bosses")
        logger.info(f"[{self.username}] Boss đầu tiên: '{self.target_boss_name}'")
    
    def stop(self):
        """Dừng auto boss"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Unregister khỏi coordinator
        if self.target_boss_name:
            self.coordinator.unregister_hunter(self.target_boss_name, self)
        
        # Cancel loop task
        if self.loop_task and not self.loop_task.done():
            self.loop_task.cancel()
        
        # Stop XMap if running
        if self.controller.xmap.is_xmapping:
            self.controller.xmap.finish()
        
        # Stop AutoPlay if running (check interval attribute)
        if self.controller.auto_play.interval:
            self.controller.toggle_autoplay(False)
        
        self.state = BossState.IDLE
        logger.info(f"[{self.username}] ⏹️ Đã dừng Auto Boss")
    
    def _get_group_id(self) -> str:
        """
        Xác định group_id - TẤT CẢ hunters săn cùng boss = cùng group!
        Để enable zone distribution cooperation
        """
        # Group = Boss name → Tất cả accounts hunt cùng boss sẽ chia việc
        return f"boss_{self.target_boss_name}"
    
    async def _main_loop(self):
        """Main async loop xử lý state machine"""
        try:
            while self.is_running:
                # Boss status monitoring
                if not await self._check_boss_alive():
                    logger.info(f"[{self.username}] ⚠️ Boss '{self.target_boss_name}' đã chết!")
                    
                    # Nếu đang dùng queue, chuyển boss tiếp theo
                    if self.use_queue_mode:
                        await self._next_boss_in_queue()
                        if not self.is_running:  # Hết queue
                            return
                        continue
                    else:
                        self.stop()
                        return
                
                # State machine
                if self.state == BossState.SEARCHING:
                    await self._state_searching()
                elif self.state == BossState.NAVIGATING:
                    await self._state_navigating()
                elif self.state == BossState.ZONE_SCANNING:
                    await self._state_zone_scanning()
                elif self.state == BossState.GATHERING:
                    await self._state_gathering()
                elif self.state == BossState.ATTACKING:
                    await self._state_attacking()
                elif self.state == BossState.RECOVERING:
                    await self._state_recovering()
                
                await asyncio.sleep(0.1)  # Prevent CPU spinning
        
        except asyncio.CancelledError:
            logger.info(f"[{self.username}] Auto boss loop cancelled")
        except Exception as e:
            logger.info(f"[{self.username}] Lỗi trong auto boss loop: {e}")
            import traceback
            traceback.print_exc()
            self.stop()
    
    async def _check_boss_alive(self) -> bool:
        """Kiểm tra boss còn sống trong BossManager"""
        # Throttle check để không spam
        current_time = time.time()
        if current_time - self.last_boss_check_time < self.boss_check_interval:
            return True  # Assume alive, chưa đủ interval
        
        self.last_boss_check_time = current_time
        
        # Check trong BossManager (case-insensitive)
        from logic.boss_manager import BossManager
        boss_manager = BossManager()
        
        target_name_lower = self.target_boss_name.lower()
        
        for boss in boss_manager.get_bosses():
            if boss['name'].lower() == target_name_lower:
                if boss['status'] == 'Chết':
                    return False
                # Boss còn sống
                return True
        
        # Không tìm thấy boss trong danh sách = đã bị xóa = đã chết lâu
        return False
    
    async def _state_searching(self):
        """State: Tìm boss trong BossManager"""
        logger.info(f"[{self.username}] 🔍 Đang tìm boss '{self.target_boss_name}'...")
        
        boss_info = self._find_boss_in_manager()
        
        if boss_info is None:
            logger.info(f"[{self.username}] ❌ Không tìm thấy boss '{self.target_boss_name}' trong danh sách")
            self.stop()
            return
        
        self.target_map_id = boss_info['map_id']
        self.target_zone_id = boss_info.get('zone', -1)
        
        logger.info(f"[{self.username}] ✅ Tìm thấy boss tại map {self.target_map_id}, zone {self.target_zone_id}")
        
        # Chuyển sang state NAVIGATING
        self.state = BossState.NAVIGATING
    
    def _find_boss_in_manager(self) -> Optional[dict]:
        """Tìm boss 'Sống' trong BossManager (case-insensitive)"""
        from logic.boss_manager import BossManager
        boss_manager = BossManager()
        
        target_name_lower = self.target_boss_name.lower()
        
        for boss in boss_manager.get_bosses():
            if boss['name'].lower() == target_name_lower and boss['status'] == 'Sống':
                return boss
        
        return None
    
    async def _state_navigating(self):
        """State: Di chuyển tới map boss"""
        current_map = self.controller.tile_map.map_id
        
        if current_map == self.target_map_id:
            logger.info(f"[{self.username}] ✅ Đã tới map {self.target_map_id}")
            # Chuyển sang ZONE_SCANNING
            self.state = BossState.ZONE_SCANNING
            return
        
        # Nếu XMap chưa chạy, start XMap
        if not self.controller.xmap.is_xmapping:
            logger.info(f"[{self.username}] 🚶 Đang di chuyển tới map {self.target_map_id}...")
            await self.controller.xmap.start(self.target_map_id)
        
        # Đợi XMap hoàn thành
        await asyncio.sleep(1)
    
    async def _state_zone_scanning(self):
        """State: Quét các zone được assign"""
        # Lần đầu vào state này, cần lấy danh sách zone và assign
        if not self.assigned_zones:
            await self._initialize_zone_scanning()
            return
        
        # Check xem team đã tìm thấy boss chưa
        if self.coordinator.is_boss_found(self.target_boss_name, self.group_id):
            location = self.coordinator.get_boss_location(self.target_boss_name, self.group_id)
            if location:
                map_id, zone_id = location
                logger.info(f"[{self.username}] 📢 Team đã tìm thấy boss tại zone {zone_id}")
                self.target_zone_id = zone_id
                self.state = BossState.GATHERING
                return
        
        # Scan zone tiếp theo
        if self.current_zone_index >= len(self.assigned_zones):
            logger.info(f"[{self.username}] Đã quét hết {len(self.assigned_zones)} zone, không tìm thấy boss")
            self.stop()
            return
        
        target_zone = self.assigned_zones[self.current_zone_index]
        
        logger.info(f"[{self.username}] 🔍 Quét zone {target_zone} ({self.current_zone_index + 1}/{len(self.assigned_zones)})...")
        
        # Request đổi zone với verification
        success = await self._request_zone_change_with_verify(target_zone)
        
        if not success:
            logger.info(f"[{self.username}] Không thể vào zone {target_zone}, skip")
            self.current_zone_index += 1
            return
        
        # Lưu vị trí để recovery nếu chết
        self.last_scanned_map_id = self.controller.tile_map.map_id
        self.last_scanned_zone_id = target_zone
        
        # Check xem zone này có boss không
        logger.info(f"[{self.username}] 🔎 Kiểm tra boss trong zone {target_zone}...")
        if await self._check_zone_for_boss():
            # Tìm thấy boss!
            logger.info(f"[{self.username}] 🎯 PHÁT HIỆN BOSS tại Zone {target_zone}!")
            self.target_zone_id = target_zone
            
            # Broadcast tới team
            self.coordinator.broadcast_boss_found(
                self.target_boss_name, 
                self.group_id, 
                self.target_map_id, 
                target_zone
            )
            
            # Chuyển sang GATHERING (đợi team)
            self.state = BossState.GATHERING
            self.gathering_start_time = time.time()
        else:
            # Không có boss, chuyển zone tiếp theo
            logger.info(f"[{self.username}] ❌ Không có boss trong zone {target_zone}")
            self.current_zone_index += 1
            await asyncio.sleep(1.0)  # Đợi 1 giây trước khi scan zone tiếp
    
    async def _initialize_zone_scanning(self):
        """Khởi tạo zone scanning: lấy danh sách zone và assign"""
        logger.info(f"[{self.username}] Lấy danh sách zone...")
        
        # Request zone list
        await self.controller.account.service.open_zone_ui()
        await asyncio.sleep(1.5)  # Đợi server response
        
        # Get zone list from controller (set by process_zone_list)
        zone_list = getattr(self.controller, 'zone_list', None)
        
        if not zone_list:
            logger.info(f"[{self.username}] Không lấy được danh sách zone")
            self.stop()
            return
        
        total_zones = len(zone_list)
        logger.info(f"[{self.username}] Tổng số zone: {total_zones}")
        
        # SYNC BARRIER: Mark ready và đợi team
        logger.info(f"[{self.username}] Marking ready và đợi team...")
        self.coordinator.mark_ready(self.target_boss_name, self.group_id, self.username)
        
        # Wait for all hunters to be ready (with timeout)
        await self.coordinator.wait_for_all_ready(self.target_boss_name, self.group_id, timeout=2.0)
        
        # Assign zones - CHỈ 1 lần cho tất cả hunters
        assignments = self.coordinator.assign_zones(
            self.target_boss_name, 
            self.group_id, 
            total_zones
        )
        
        self.assigned_zones = assignments.get(self.username, list(range(total_zones)))
        self.current_zone_index = 0
        
        logger.info(f"[{self.username}] Được assign scan zones: {self.assigned_zones} (Tổng: {len(self.assigned_zones)}/{total_zones})")
    
    async def _request_zone_change_with_verify(self, zone_id: int) -> bool:
        """Request đổi zone và verify thành công. Returns True nếu thành công."""
        logger.info(f"[{self.username}] 🔄 Request đổi sang zone {zone_id}...")
        
        for attempt in range(self.max_zone_retry):
            # Send request
            await self.controller.account.service.request_change_zone(zone_id)
            
            # Wait longer for zone change AND char spawn (bosses need time!)
            await asyncio.sleep(3.0)  # Tăng lên 3s để chars (bosses) spawn
            
            current_zone = self.controller.map_info.get('zone', -1)
            
            if current_zone == zone_id:
                logger.info(f"[{self.username}] ✅ Xác nhận zone hiện tại: {zone_id}")
                return True
            else:
                logger.info(f"[{self.username}] Zone chưa đổi (hiện tại: {current_zone}), retry {attempt + 1}/{self.max_zone_retry}...")
        
        # Failed after max retries
        logger.info(f"[{self.username}] ❌ Không thể vào zone {zone_id} sau {self.max_zone_retry} lần thử")
        return False
    
    async def _check_zone_for_boss(self) -> bool:
        """Kiểm tra chars (characters/bosses) trong zone có boss target không"""
        # Get boss template from manager
        boss_info = self._find_boss_in_manager()
        if not boss_info:
            return False
        
        boss_name = boss_info['name']
        boss_name_lower = boss_name.lower()
        
        # Check chars in current zone (SILENT - chỉ print khi tìm thấy boss)
        for char_id, char in self.controller.chars.items():
            char_name = char.get('name', '')
            char_hp = char.get('hp', 0)
            char_type_pk = char.get('type_pk', 0)
            
            # Check by type_pk == 5 (BOSS) AND name match (case-insensitive) AND HP > 0
            if char_type_pk == 5 and char_name.lower() == boss_name_lower and char_hp > 0:
                current_zone = self.controller.map_info.get('zone', -1)
                print(f"[{self.username}] Tìm thấy boss '{char_name}' tại zone {current_zone}")
                return True
        
        return False
    
    async def _state_gathering(self):
        """State: Tập hợp team về zone có boss"""
        current_zone = self.controller.map_info.get('zone', -1)
        
        # Nếu đã ở đúng zone, đợi team
        if current_zone == self.target_zone_id:
            await self._wait_for_team()
            return
        
        # Di chuyển về target zone
        logger.info(f"[{self.username}] Đang di chuyển tới zone {self.target_zone_id}...")
        success = await self._request_zone_change_with_verify(self.target_zone_id)
        
        if not success:
            logger.info(f"[{self.username}] Không thể vào zone {self.target_zone_id}")
            self.stop()
            return
        
        logger.info(f"[{self.username}] Đã tới zone {self.target_zone_id}, ready to attack")
        
        # Đợi team
        await self._wait_for_team()
    
    async def _wait_for_team(self):
        """Đợi team tập hợp, sau đó chuyển sang ATTACKING"""
        hunter_count = self.coordinator.get_hunter_count(self.target_boss_name, self.group_id)
        hunters_in_zone = sum(
            1 for h in self.coordinator.get_hunters_in_group(self.target_boss_name, self.group_id)
            if h.state == BossState.GATHERING or h.state == BossState.ATTACKING
        )
        
        logger.info(f"[{self.username}] Đang đợi team tập hợp... ({hunters_in_zone}/{hunter_count} ready)")
        
        # Check timeout
        if time.time() - self.gathering_start_time > self.gathering_timeout:
            logger.info(f"[{self.username}] Timeout đợi team, bắt đầu attack")
            self.state = BossState.ATTACKING
            return
        
        # Nếu đủ team hoặc chỉ 1 người, bắt đầu attack
        if hunters_in_zone >= hunter_count or hunter_count == 1:
            logger.info(f"[{self.username}] Team đã tập hợp đầy đủ ({hunters_in_zone}/{hunter_count}), bắt đầu tấn công!")
            self.state = BossState.ATTACKING
        else:
            await asyncio.sleep(0.5)
    
    async def _state_attacking(self):
        """State: Attack boss"""
        # Check if character died
        if self.controller.account.char.is_die:
            await self._handle_death()
            return
        
        # Kiểm tra boss còn sống không (trong zone)
        # Sequential kill: Chỉ attack 1 boss tại 1 thời điểm
        boss_char = await self._get_target_boss_in_zone()
        
        if not boss_char:
            logger.info(f"[{self.username}] Boss '{self.target_boss_name}' đã bị tiêu diệt!")
            
            # Nếu dùng queue mode, chuyển boss tiếp theo
            if self.use_queue_mode:
                await self._next_boss_in_queue()
                return
            else:
                # Single mode: dừng
                self.stop()
                return
        
        # Set char_focus = boss để AutoAttack attack
        my_char = self.controller.account.char
        my_char.char_focus = boss_char
        
        boss_x = boss_char.get('x', my_char.cx)
        boss_y = boss_char.get('y', my_char.cy)
        boss_name = boss_char.get('name', 'Boss')
        
        # Tele vào boss
        logger.info(f"[{self.username}] Tele tới boss {boss_name} ({boss_x}, {boss_y})")
        my_char.cx = boss_x
        my_char.cy = boss_y
        my_char.cdir = 1 if boss_x > my_char.cx else -1
        await self.controller.account.service.char_move()
        await asyncio.sleep(0.1)
        
        # Bật AutoAttack nếu chưa bật
        if self.controller.auto_attack is None or not self.controller.auto_attack.is_running:
            logger.info(f"[{self.username}] Bật Auto Attack để tấn công boss...")
            self.controller.toggle_auto_attack(True)
        
        # Monitor trong state này
        await asyncio.sleep(1.0)
    
    async def _state_recovering(self):
        """State: Recovery sau khi chết"""
        logger.info(f"[{self.username}]  Đang recovery: quay lại map {self.last_scanned_map_id}, zone {self.last_scanned_zone_id}")
        
        # XMap về map cũ
        if self.controller.tile_map.map_id != self.last_scanned_map_id:
            await self.controller.xmap.start(self.last_scanned_map_id)
            
            # Đợi XMap hoàn thành
            while self.controller.xmap.is_xmapping:
                await asyncio.sleep(1)
        
        # Đổi về zone cũ
        if self.last_scanned_zone_id != -1:
            await self._request_zone_change_with_verify(self.last_scanned_zone_id)
        
        # Resume scanning
        logger.info(f"[{self.username}] Recovery hoàn tất, tiếp tục scan")
        self.state = BossState.ZONE_SCANNING
    
    async def _handle_death(self):
        """Xử lý khi character chết"""
        logger.info(f"[{self.username}]  Nhân vật đã chết! Đang recovery...")
        
        # Lưu vị trí hiện tại
        self.last_scanned_map_id = self.controller.tile_map.map_id
        self.last_scanned_zone_id = self.controller.map_info.get('zone', -1)
        
        # Return town
        await self.controller.account.service.return_town_from_dead()
        
        # Chờ hồi sinh
        await asyncio.sleep(3.0)
        
        # Chuyển sang state RECOVERING
        self.state = BossState.RECOVERING
    
    async def _on_boss_found_by_team(self, map_id: int, zone_id: int):
        """Callback khi team tìm thấy boss"""
        # Chỉ xử lý nếu đang ở state ZONE_SCANNING
        if self.state != BossState.ZONE_SCANNING:
            return
        
        print(f"[{self.username}] Boss đã được tìm thấy tại zone {zone_id} bởi team!")
        
        # Cập nhật target và chuyển sang GATHERING
        self.target_zone_id = zone_id
        self.state = BossState.GATHERING
        self.gathering_start_time = time.time()
    
    async def _is_boss_killed(self) -> bool:
        """Kiểm tra boss còn trong zone không (dùng để detect kill)"""
        boss_mob = await self._get_target_boss_in_zone()
        return boss_mob is None
    
    async def _get_target_boss_in_zone(self):
        """
        Lấy boss target trong zone (sequential kill logic).
        Nếu có nhiều boss cùng tên, chỉ trả về 1 boss (HP thấp nhất) để attack.
        """
        matching_bosses = []
        
        boss_name_lower = self.target_boss_name.lower()
        
        # Kiểm tra trong chars hiện tại (BOSSES ARE CHARS with type_pk == 5!)
        for char_id, char in self.controller.chars.items():
            char_name = char.get('name', '')
            char_hp = char.get('hp', 0)
            char_type_pk = char.get('type_pk', 0)
            
            # Check type_pk == 5 (BOSS) AND name match AND HP > 0
            if char_type_pk == 5 and char_name.lower() == boss_name_lower and char_hp > 0:
                matching_bosses.append((char_id, char))
        
        if not matching_bosses:
            return None
        
        # Nếu có nhiều boss, chọn boss có HP thấp nhất (sắp chết)
        if len(matching_bosses) > 1:
            matching_bosses.sort(key=lambda x: x[1].get('hp', 0))
        logger.info(f"[{self.username}] Phát hiện {len(matching_bosses)} boss '{self.target_boss_name}', đang attack boss HP thấp nhất")
        
        return matching_bosses[0][1]  # Return char dict
    
    async def _next_boss_in_queue(self):
        """Chuyển sang boss tiếp theo trong queue"""
        self.current_boss_index += 1
        
        if self.current_boss_index >= len(self.boss_queue):
            logger.info(f"[{self.username}] Đã hoàn thành toàn bộ {len(self.boss_queue)} bosses trong queue!")
            self.stop()
            return
        
        # Unregister boss cũ
        self.coordinator.unregister_hunter(self.target_boss_name, self)
        
        # Chuẩn bị boss mới
        next_boss = self.boss_queue[self.current_boss_index]
        logger.info(f"[{self.username}] Chuyển sang boss tiếp theo [{self.current_boss_index}/{len(self.boss_queue)-1}]: '{next_boss}'")
        
        # Reset state
        self.target_boss_name = next_boss
        self.target_map_id = -1
        self.target_zone_id = -1
        self.assigned_zones = []
        self.current_zone_index = 0
        self.state = BossState.SEARCHING
        
        # Register boss mới
        self.coordinator.register_hunter(next_boss, self)
        
        # Đợi 2 giây trước khi bắt đầu boss mới
        await asyncio.sleep(1.0)
