"""
Shared Memory - Multi-Agent Communication & Coordination
Pure Python - Thread-safe in-memory storage
Enables swarm intelligence, goal management, and zone distribution
"""

import threading
from typing import Dict, List, Any, Optional


class SharedMemory:
    """
    Singleton pattern shared memory for multi-agent coordination.
    Thread-safe with threading.Lock for concurrent access.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Target sharing
        self.shared_targets: List[Dict[str, Any]] = []
        
        # Team coordination
        self.team_leader: Optional[str] = None
        self.bot_registry: Dict[str, Dict[str, Any]] = {}  # account_id -> {capabilities, role}
        
        # Group management
        self.groups: Dict[int, List[str]] = {}  # group_id -> [account_ids]
        self.active_groups: List[int] = []  # Which groups are AI-controlled
        
        # Zone/Map distribution
        self.zone_assignments: Dict[str, int] = {}  # account_id -> zone_id
        self.zone_distribution: Dict[int, Dict[int, List[str]]] = {}  # map_id -> {zone_id -> [account_ids]}
        
        # Goal management
        self.current_goal: Optional[Dict[str, Any]] = None
        self.goal_progress: Dict[str, Any] = {}  # account_id -> progress_data
        
        # Bot status tracking
        self.bot_status: Dict[str, Dict[str, Any]] = {}  # account_id -> status_dict
        
        self.shared_trainer_enabled = False
        
        # Zone Density Manager (Hive Architecture)
        self.zone_density = ZoneDensityManager()
        
        self._initialized = True
        print("[SharedMemory] Initialized (Singleton)")
    
    # ===== Target Sharing =====
    
    def broadcast_target(self, account_id: str, target_info: Dict[str, Any]) -> None:
        """Broadcast a target (boss, mob, location) to all bots"""
        with self._lock:
            target_info['broadcaster'] = account_id
            self.shared_targets.append(target_info)
            
            # Keep only last 10 targets
            if len(self.shared_targets) > 10:
                self.shared_targets = self.shared_targets[-10:]
    
    def get_shared_targets(self) -> List[Dict[str, Any]]:
        """Get list of shared targets from other bots"""
        with self._lock:
            return self.shared_targets.copy()
    
    def clear_targets(self) -> None:
        """Clear all shared targets"""
        with self._lock:
            self.shared_targets = []
    
    # ===== Team Coordination =====
    
    def set_team_leader(self, account_id: str) -> None:
        """Designate a team leader"""
        with self._lock:
            self.team_leader = account_id
            print(f"[SharedMemory] Team leader set: {account_id}")
    
    def get_team_leader(self) -> Optional[str]:
        """Get current team leader"""
        with self._lock:
            return self.team_leader
    
    def register_bot(self, account_id: str, capabilities: Dict[str, Any]) -> None:
        """Register a bot with its capabilities (tank/dps/support)"""
        with self._lock:
            self.bot_registry[account_id] = capabilities
    
    def get_team_formation(self) -> Dict[str, Any]:
        """Get current team formation"""
        with self._lock:
            return {
                "leader": self.team_leader,
                "bots": self.bot_registry.copy()
            }
    
    # ===== Group Management =====
    
    def assign_to_group(self, account_id: str, group_id: int) -> None:
        """Assign bot to a group (1-5 users per group)"""
        with self._lock:
            if group_id not in self.groups:
                self.groups[group_id] = []
            
            # Remove from other groups
            for gid, members in self.groups.items():
                if account_id in members:
                    members.remove(account_id)
            
            # Add to new group
            self.groups[group_id].append(account_id)
            print(f"[SharedMemory] {account_id} assigned to group {group_id}")
    
    def get_group_members(self, group_id: int) -> List[str]:
        """Get list of bots in a group"""
        with self._lock:
            return self.groups.get(group_id, []).copy()
    
    def set_active_groups(self, group_ids: List[int]) -> None:
        """Set which groups are AI-controlled"""
        with self._lock:
            self.active_groups = group_ids.copy()
            print(f"[SharedMemory] Active groups: {group_ids}")
    
    def is_bot_in_active_group(self, account_id: str) -> bool:
        """Check if bot is in an active group"""
        with self._lock:
            for group_id in self.active_groups:
                if account_id in self.groups.get(group_id, []):
                    return True
            return False
    
    # ===== Zone/Map Distribution =====
    
    def assign_zone(self, account_id: str, zone_id: int) -> None:
        """Manually assign bot to a zone"""
        with self._lock:
            self.zone_assignments[account_id] = zone_id
    
    def get_zone_distribution(self, map_id: int) -> Dict[int, List[str]]:
        """Get zone distribution for a map"""
        with self._lock:
            return self.zone_distribution.get(map_id, {}).copy()
    
    def auto_distribute_zones(self, map_id: int, bot_ids: List[str], num_zones: int = 3) -> None:
        """Auto distribute bots across zones using round-robin"""
        with self._lock:
            distribution = {zone: [] for zone in range(1, num_zones + 1)}
            
            for i, bot_id in enumerate(bot_ids):
                zone_id = (i % num_zones) + 1
                distribution[zone_id].append(bot_id)
                self.zone_assignments[bot_id] = zone_id
            
            self.zone_distribution[map_id] = distribution
            print(f"[SharedMemory] Auto-distributed {len(bot_ids)} bots to {num_zones} zones")
    
    # ===== Goal Management =====
    
    def set_global_goal(self, goal_type: str, goal_data: Dict[str, Any]) -> None:
        """
        Set global goal for team.
        goal_type: 'farm_items', 'hunt_boss', 'complete_quest'
        goal_data: {'item_ids': [1,5,10]} or {'boss_name': 'Fide'}
        """
        with self._lock:
            self.current_goal = {
                'type': goal_type,
                'data': goal_data
            }
            self.goal_progress = {}  # Reset progress
            print(f"[SharedMemory] Global goal set: {goal_type} - {goal_data}")
    
    def get_current_goal(self) -> Optional[Dict[str, Any]]:
        """Get current global goal"""
        with self._lock:
            return self.current_goal.copy() if self.current_goal else None
    
    def update_goal_progress(self, account_id: str, progress: Any) -> None:
        """Update progress for an account"""
        with self._lock:
            self.goal_progress[account_id] = progress
    
    def clear_goal(self) -> None:
        """Clear current goal"""
        with self._lock:
            self.current_goal = None
            self.goal_progress = {}
    
    # ===== Status Tracking =====
    
    def update_status(self, account_id: str, status: Dict[str, Any]) -> None:
        """Update bot status"""
        with self._lock:
            self.bot_status[account_id] = status
    
    def get_team_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all bots"""
        with self._lock:
            return self.bot_status.copy()


class ZoneDensityManager:
    """
    Hive Architecture - Mental Map chia sẻ về mật độ zone.
    Ngăn chặn "dẫm đạp" khi nhiều bot cùng chọn 1 zone trống.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Intent tracking: account -> {map_id, zone_id, timestamp}
        self.zone_intents: Dict[str, Dict[str, Any]] = {}
        
        # Actual positions: account -> {map_id, zone_id, timestamp}
        self.zone_positions: Dict[str, Dict[str, Any]] = {}
        
        # Scan history: (map_id, zone_id) -> {last_scan_time, scanned_by}
        self.scan_history: Dict[tuple, Dict[str, Any]] = {}
        
        # Configuration
        self.intent_timeout = 30.0  # Intent expires after 30s
        self.scan_cooldown = 60.0   # Don't rescan same zone within 60s
    
    def register_intent(self, account_id: str, map_id: int, zone_id: int) -> None:
        """Đăng ký ý định di chuyển đến zone (ngăn race condition)"""
        import time
        with self._lock:
            self.zone_intents[account_id] = {
                'map_id': map_id,
                'zone_id': zone_id,
                'timestamp': time.time()
            }
    
    def update_real_position(self, account_id: str, map_id: int, zone_id: int) -> None:
        """Cập nhật vị trí thực tế của bot"""
        import time
        with self._lock:
            self.zone_positions[account_id] = {
                'map_id': map_id,
                'zone_id': zone_id,
                'timestamp': time.time()
            }
            
            # Clear intent khi đã đến nơi
            if account_id in self.zone_intents:
                intent = self.zone_intents[account_id]
                if intent['map_id'] == map_id and intent['zone_id'] == zone_id:
                    del self.zone_intents[account_id]
    
    def mark_zone_scanned(self, account_id: str, map_id: int, zone_id: int) -> None:
        """Đánh dấu zone đã được quét (cho Auto Boss)"""
        import time
        with self._lock:
            key = (map_id, zone_id)
            self.scan_history[key] = {
                'last_scan_time': time.time(),
                'scanned_by': account_id
            }
    
    def _clean_expired_intents(self) -> None:
        """Xóa các intent đã hết hạn (internal, gọi trong lock)"""
        import time
        current_time = time.time()
        expired = [
            acc_id for acc_id, intent in self.zone_intents.items()
            if current_time - intent['timestamp'] > self.intent_timeout
        ]
        for acc_id in expired:
            del self.zone_intents[acc_id]
    
    def get_zone_density(self, map_id: int, zone_id: int) -> int:
        """
        Tính mật độ zone (số bot hiện tại + số bot dự định đến).
        Returns: số lượng bot trong zone (thực tế + ý định)
        """
        import time
        with self._lock:
            self._clean_expired_intents()
            
            count = 0
            current_time = time.time()
            
            # Đếm bot đang ở zone
            for acc_id, pos in self.zone_positions.items():
                if pos['map_id'] == map_id and pos['zone_id'] == zone_id:
                    count += 1
            
            # Đếm bot dự định đến zone
            for acc_id, intent in self.zone_intents.items():
                if intent['map_id'] == map_id and intent['zone_id'] == zone_id:
                    # Chỉ đếm nếu bot chưa ở zone đó
                    pos = self.zone_positions.get(acc_id)
                    if not (pos and pos['map_id'] == map_id and pos['zone_id'] == zone_id):
                        count += 1
            
            return count
    
    def is_zone_recently_scanned(self, map_id: int, zone_id: int) -> bool:
        """Kiểm tra zone đã được quét gần đây chưa"""
        import time
        with self._lock:
            key = (map_id, zone_id)
            if key not in self.scan_history:
                return False
            
            scan_data = self.scan_history[key]
            elapsed = time.time() - scan_data['last_scan_time']
            return elapsed < self.scan_cooldown
    
    def get_zone_score(
        self, 
        map_id: int, 
        zone_id: int,
        current_num_players: int = 0,
        max_players: int = 15,
        normalize: bool = True
    ) -> float:
        """
        Chấm điểm zone dựa trên nhiều yếu tố.
        
        Score càng CAO = zone càng TỐT để chọn.
        
        Factors:
        - Mật độ bot (càng ít càng tốt)
        - Số người chơi khác trong zone (càng ít càng tốt)
        - Lịch sử quét (đã quét gần đây = điểm thấp)
        """
        # 1. Bot density penalty (0 bot = 1.0, nhiều bot = 0.0)
        bot_density = self.get_zone_density(map_id, zone_id)
        density_score = max(0, 1.0 - (bot_density / 5.0))  # Normalize: 5 bots = 0 score
        
        # 2. Player density score (ít người chơi = điểm cao)
        if max_players > 0:
            player_ratio = current_num_players / max_players
            player_score = 1.0 - player_ratio
        else:
            player_score = 1.0
        
        # 3. Scan history penalty (quét gần đây = điểm thấp)
        scan_penalty = 0.5 if self.is_zone_recently_scanned(map_id, zone_id) else 0.0
        
        # Công thức tổng hợp (weight: bot density 50%, player 30%, scan history 20%)
        final_score = (
            0.5 * density_score +
            0.3 * player_score -
            0.2 * scan_penalty
        )
        
        return max(0.0, final_score)
    
    def get_best_zone(
        self, 
        map_id: int,
        zone_list: List[Dict[str, Any]],
        account_id: str = ""
    ) -> Optional[int]:
        """
        Chọn zone TỐT NHẤT từ danh sách.
        
        zone_list format: [{'zone_id': 0, 'num_players': 5, 'max_players': 15}, ...]
        
        Returns: zone_id tốt nhất, hoặc None nếu không có
        """
        if not zone_list:
            return None
        
        best_zone = None
        best_score = -1.0
        
        for zone_data in zone_list:
            zone_id = zone_data['zone_id']
            num_players = zone_data.get('num_players', 0)
            max_players = zone_data.get('max_players', 15)
            
            # Bỏ qua zone đầy
            if num_players >= max_players:
                continue
            
            score = self.get_zone_score(map_id, zone_id, num_players, max_players)
            
            if score > best_score:
                best_score = score
                best_zone = zone_id
        
        return best_zone
    
    def clear_account_data(self, account_id: str) -> None:
        """Xóa toàn bộ dữ liệu của 1 account (khi logout)"""
        with self._lock:
            self.zone_intents.pop(account_id, None)
            self.zone_positions.pop(account_id, None)


# Example usage
if __name__ == "__main__":
    print("Testing SharedMemory...")
    
    # Create instance (singleton)
    mem1 = SharedMemory()
    mem2 = SharedMemory()
    
    print(f"Singleton test: mem1 is mem2 = {mem1 is mem2}")
    
    # Test group management
    print("\n--- Group Management ---")
    mem1.assign_to_group("acc_0", 1)
    mem1.assign_to_group("acc_1", 1)
    mem1.assign_to_group("acc_2", 2)
    mem1.set_active_groups([1, 2])
    
    print(f"Group 1 members: {mem1.get_group_members(1)}")
    print(f"acc_0 in active group: {mem1.is_bot_in_active_group('acc_0')}")
    
    # Test zone distribution
    print("\n--- Zone Distribution ---")
    bot_ids = [f"acc_{i}" for i in range(10)]
    mem1.auto_distribute_zones(map_id=5, bot_ids=bot_ids, num_zones=3)
    
    distribution = mem1.get_zone_distribution(5)
    for zone, bots in distribution.items():
        print(f"  Zone {zone}: {bots}")
    
    # Test goal management
    print("\n--- Goal Management ---")
    mem1.set_global_goal("farm_items", {"item_ids": [1, 5, 10], "target_mob_id": 12})
    goal = mem1.get_current_goal()
    print(f"Current goal: {goal}")
    
    # Test target sharing
    print("\n--- Target Sharing ---")
    mem1.broadcast_target("acc_0", {"type": "boss", "name": "Fide", "map_id": 5, "x": 500, "y": 300})
    targets = mem1.get_shared_targets()
    print(f"Shared targets: {targets}")
    
    print("\n[SUCCESS] SharedMemory test complete!")
