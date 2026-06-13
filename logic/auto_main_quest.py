import asyncio
import json
import math
import time
from logs.logger_config import logger

class AutoMainQuest:
    def __init__(self, account):
        self.account = account
        self.is_running = False
        self.task = None
        self.config_data = self._load_config()
        self.blacklist_mobs = {} # Lưu id quái bị lỗi và thời gian hết hạn blacklist

    def _load_config(self):
        try:
            with open('maps_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Lỗi tải maps_config.json: {e}")
            return {"maps": []}

    def _find_map_by_mob_name(self, step_name):
        step_name_lower = step_name.lower()
        possible_matches = []
        for map_info in self.config_data.get("maps", []):
            for mob in map_info.get("mobs", []):
                # Kiểm tra nếu tên mob trong json có xuất hiện trong dòng nhiệm vụ
                if mob["mob_name"].lower() in step_name_lower:
                    possible_matches.append({
                        "map_id": map_info["map_id"],
                        "mob_id": mob["mob_id"],
                        "count": mob.get("count", 1)
                    })
        
        if possible_matches:
            # Sort descending by count to get the map with the most mobs
            possible_matches.sort(key=lambda x: x["count"], reverse=True)
            best_match = possible_matches[0]
            return best_match["map_id"], best_match["mob_id"]
            
        return None, None

    def _get_nearest_valid_mob(self, target_mob_id):
        mobs = self.account.controller.mobs
        char = self.account.char
        best_mob = None
        min_dist = float('inf')
        current_time = time.time()

        for mob_id, mob in mobs.items():
            # Kiểm tra trạng thái: status > 1 (đang sống) và hp > 0
            if getattr(mob, 'template_id', -1) != target_mob_id or getattr(mob, 'hp', 0) <= 0 or getattr(mob, 'status', 0) <= 1:
                continue
            # Kiểm tra xem có trong Blacklist không
            if mob_id in self.blacklist_mobs and current_time < self.blacklist_mobs[mob_id]:
                continue
            
            # Tính khoảng cách (Nearest Neighbor)
            dist = math.hypot(mob.x - char.cx, mob.y - char.cy)
            if dist < min_dist:
                min_dist = dist
                best_mob = mob

        return best_mob

    async def start(self):
        if self.is_running:
            return
        # Load lại config để nhận dữ liệu map mới nếu có cập nhật
        self.config_data = self._load_config()
        self.is_running = True
        self.current_status_msg = "Đang khởi động..."
        print(f"[{self.account.username}] [AutoQuest] Đã kích hoạt tính năng tự động làm nhiệm vụ chính.")
        self.task = asyncio.create_task(self._quest_loop())

    async def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        self.current_status_msg = "Đã tắt"
        print(f"[{self.account.username}] [AutoQuest] Đã TẮT tính năng tự động làm nhiệm vụ chính.")
        if self.task and not self.task.done():
            self.task.cancel()

    def get_status(self):
        if not self.is_running:
            return "Đang tắt"
        return getattr(self, 'current_status_msg', "Không rõ")

    async def _quest_loop(self):
        while self.is_running:
            try:
                if not self.account.is_logged_in or not self.account.char.task:
                    await asyncio.sleep(1)
                    continue

                # 1. Đọc thông tin nhiệm vụ (Quest Checker)
                task = self.account.char.task
                if task.index >= len(task.sub_names):
                    # print("[AutoQuest] Nhiệm vụ hiện tại đã hoàn thành toàn bộ bước.")
                    await asyncio.sleep(5)
                    continue

                step_name = task.sub_names[task.index]
                
                # Có thể tiến độ nằm ở task.count hoặc parse từ step_name
                # Ví dụ "Tiêu diệt 100 nappa (0/100)".
                # Ở đây dựa vào việc task.index thay đổi khi xong bước
                
                target_map_id, target_mob_id = self._find_map_by_mob_name(step_name)

                if target_map_id is not None:
                    # 2. Di chuyển thông minh (XMap)
                    if self.account.char.map_id != target_map_id:
                        if getattr(self, 'last_target_map', None) != target_map_id:
                            print(f"[{self.account.username}] [AutoQuest] Đang di chuyển tới Map {target_map_id} để làm NV...")
                            self.last_target_map = target_map_id
                        self.current_status_msg = f"Đang di chuyển tới Map {target_map_id}"
                        if hasattr(self.account.controller, 'xmap'):
                            if not self.account.controller.xmap.is_xmapping:
                                await self.account.controller.xmap.start(target_map_id)
                        else:
                            # Tạm xử lý fallback nếu ko có xmap obj chuyên biệt, gọi service gomap
                            await self.account.service.request_change_map()
                        await asyncio.sleep(2) # Chờ load map
                        continue

                    # 3. Tự động tàn sát & Tối ưu hóa (Auto Kill)
                    target_mob = self._get_nearest_valid_mob(target_mob_id)
                    if target_mob:
                        # Di chuyển tới tọa độ quái
                        self.account.char.cx = target_mob.x
                        self.account.char.cy = target_mob.y
                        await self.account.service.char_move()
                        await asyncio.sleep(0.05) # Delay ngắn chờ server cập nhật vị trí
                        
                        # Timeout kiểm tra chống kẹt
                        attack_time = time.time()
                        last_hp = target_mob.hp
                        while self.is_running and target_mob.hp > 0 and target_mob.status > 1:
                            # Gửi gói tin đánh liên tục
                            await self.account.service.send_player_attack(mob_ids=[target_mob.mob_id])
                            
                            if time.time() - attack_time > 5: # Anti-stuck 5 giây
                                if target_mob.hp == last_hp:
                                    print(f"[{self.account.username}] [AutoQuest] Quái {target_mob.mob_id} không mất máu (Lỗi/Kẹt). Đưa vào Blacklist 30s!")
                                    self.blacklist_mobs[target_mob.template_id] = time.time() + 30
                                    break
                                else:
                                    # Cập nhật máu mới và đánh tiếp
                                    last_hp = target_mob.hp
                                    attack_time = time.time()
                            
                            await asyncio.sleep(0.3) # Đánh mỗi 0.3s
                            
                            # Kiểm tra xem nhiệm vụ đã chuyển bước chưa để ngắt
                            if self.account.char.task.index > task.index:
                                print(f"[{self.account.username}] [AutoQuest] Bước nhiệm vụ đã hoàn thành. Chuyển mục tiêu...")
                                break
                    else:
                        # Kiểm tra xem có phải đang chờ respawn không
                        task_info = self.account.char.task
                        if hasattr(task_info, 'count') and hasattr(task_info, 'counts') and 0 <= task_info.index < len(task_info.counts):
                            progress_str = f"[{task_info.count}/{task_info.counts[task_info.index]}]"
                        else:
                            progress_str = f"[{getattr(task_info, 'count', 0)}/???]"
                        
                        self.current_status_msg = f"Tiến độ {progress_str}. Đang chờ '{step_name}' hồi sinh..."
                        await asyncio.sleep(1) # Không có quái, chờ respawn
                else:
                    if getattr(self, 'last_error_map_msg', None) != step_name:
                        print(f"[{self.account.username}] [AutoQuest] Không tìm thấy dữ liệu Map cho nhiệm vụ: '{step_name}'. Vui lòng thêm vào maps_config.json")
                        self.last_error_map_msg = step_name
                    self.current_status_msg = f"Thiếu data map: {step_name}"
                    await asyncio.sleep(10)

                await asyncio.sleep(0.1) # Loop delay
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[{self.account.username}] [AutoQuest] Lỗi vòng lặp: {e}")
                await asyncio.sleep(2)
