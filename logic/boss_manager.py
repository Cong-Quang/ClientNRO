from datetime import datetime, timedelta
import threading

class BossManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(BossManager, cls).__new__(cls)
                    cls._instance.bosses = []
        return cls._instance

    def add_boss(self, name: str, map_name: str, zone_id: int = -1):
        """Thêm boss mới vào danh sách."""
        # Kiểm tra trùng lặp (nếu boss cùng tên ở cùng map xuất hiện trong thời gian ngắn < 1 phút thì update time)
        now = datetime.now()
        
        # Check logic trùng (đơn giản hoá: cùng tên, cùng map)
        for b in self.bosses:
            if b['name'] == name and b['map'] == map_name:
                # Update time
                b['time'] = now 
                if zone_id != -1:
                    b['zone'] = zone_id
                return

        # Lookup map_id
        from logic.map_data import MAP_NAME_TO_ID
        # Try exact match first, then partial match?
        # Map names from server might have variations.
        map_id_val = MAP_NAME_TO_ID.get(map_name, -1)
        
        # If not found, try to find case-insensitive or partial
        if map_id_val == -1:
             for name_key, id_val in MAP_NAME_TO_ID.items():
                 if name_key.lower() == map_name.lower():
                     map_id_val = id_val
                     break
        
        new_boss = {
            'name': name,
            'map': map_name,
            'map_id': map_id_val,
            'zone': zone_id,
            'time': now,
            'status': 'Sống'  # Status: Sống / Chết
        }
        self.bosses.append(new_boss)
        # Giới hạn danh sách 15 boss mới nhất
        if len(self.bosses) > 15:
            self.bosses.pop(0)

    def mark_boss_dead(self, boss_name: str):
        """Đánh dấu boss đã bị tiêu diệt."""
        # Tìm boss sống gần nhất có tên trùng khớp
        # Ưu tiên boss mới xuất hiện nhất
        for b in self.bosses:
            if b['name'] == boss_name and b['status'] == 'Sống':
                b['status'] = 'Chết'
                # b['time'] = datetime.now() # Optional: Update time to death time?
                return True
        return False

    def get_bosses(self):
        """Trả về danh sách boss, sắp xếp mới nhất trước."""
        return sorted(self.bosses, key=lambda x: x['time'], reverse=True)
    
    def find_bosses_by_keyword(self, keyword: str):
        """
        Tìm tất cả boss có tên chứa keyword (case-insensitive).
        Trả về list của boss đang sống, sắp xếp theo thời gian mới nhất.
        
        Ví dụ: keyword="Super Broly" sẽ match "Super Broly 1", "Super Broly 25"
        """
        keyword_lower = keyword.lower()
        matching_bosses = [
            b for b in self.bosses 
            if keyword_lower in b['name'].lower() and b['status'] == 'Sống'
        ]
        return sorted(matching_bosses, key=lambda x: x['time'], reverse=True)

    def clear_expired(self, minutes: int = 60):
        """Xóa boss đã xuất hiện quá lâu."""
        now = datetime.now()
        self.bosses = [b for b in self.bosses if (now - b['time']).total_seconds() < minutes * 60]
