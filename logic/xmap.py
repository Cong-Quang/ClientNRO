import time
import asyncio
import random
import heapq
from typing import List, Dict, Optional, Tuple
from logs.logger_config import logger, TerminalColors as C
from network.service import Service

class NextMap:
    """Cấu trúc dữ liệu lưu thông tin để di chuyển sang bản đồ kế tiếp"""
    def __init__(self, map_id: int, npc_id: int = -1, select_name: str = "", select_name2: str = "", select_name3: str = "", 
                 walk: bool = False, x: int = -1, y: int = -1, item_id: int = -1, 
                 index_npc: int = -1, index_npc2: int = -1, index_npc3: int = -1,
                 capsule_index: int = -1):
        self.map_id = map_id
        self.npc_id = npc_id
        self.select_name = select_name
        self.select_name2 = select_name2
        self.select_name3 = select_name3
        self.walk = walk
        self.x = x
        self.y = y
        self.item_id = item_id
        self.index_npc = index_npc
        self.index_npc2 = index_npc2
        self.index_npc3 = index_npc3
        self.capsule_index = capsule_index

class XMap:
    def __init__(self, controller):
        self.controller = controller
        self.link_maps: Dict[int, List[NextMap]] = {}
        self.is_xmapping = False
        self.target_map_id = -1
        self.path = []
        self.history = []
        self.capsule_history = []
        self.last_update = 0
        self.update_interval =  0 # Tối ưu tốc độ
        self.processing_map_change = False
        self.expected_next_map_id = -1
        self.last_action_time = 0
        
        self.dangerous_maps = set() # Lưu danh sách bản đồ có Boss/Nguy hiểm
        self.zone_changed_in_map = False
        self.find_npc_in_future = False
        
        # --- Dữ liệu validation map ---
        self.power_60b_maps = {155, 166}
        self.power_40b_maps = {153, 154, 156, 157, 158, 159}
        self.cold_maps = {105, 106, 107, 108, 109, 110}
        self.future_maps = {102, 92, 93, 94, 96, 97, 98, 99, 100, 103}
        self.clan_maps = {
            # Khu vực bang hội
            53, 54, 55, 56, 57, 58, 59, 60, 61, 62,
            # Khí gas
            147, 148, 149, 151, 152,
            # Mảnh vỡ bông tai
            153, 156, 157, 158, 159
        }
        
        self.init_map_data()

    def init_map_data(self):
        """Khởi tạo dữ liệu kết nối giữa các bản đồ"""
        # Định nghĩa các trường hợp ngoại lệ về hướng đi (Tuple: (From, To) -> Direction)
        self.direction_overrides = {}
        
        # Các map có cổng nằm dọc (Trên/Dưới)
        self.direction_overrides[(73, 74)] = "Up"   # Thung lũng chết -> Đồi cây Fide (Cổng trên)
        self.direction_overrides[(74, 73)] = "Left" # Đồi cây Fide -> Thung lũng chết (Cổng trái - Fix theo yêu cầu)
        self.direction_overrides[(47, 1)] = "Left"

        # Danh sách các map đi ngược (Cổng bên Trái thay vì Phải như mặc định)
        # 71->72, 72->64, 64->65...
        left_sequence = [71, 72, 64, 65, 63, 66, 67, 73]
        for i in range(len(left_sequence) - 1):
            u, v = left_sequence[i], left_sequence[i+1]
            self.direction_overrides[(u, v)] = "Left"
            self.direction_overrides[(v, u)] = "Right" # Chiều về thì đi bên Phải

        # Phân nhóm bản đồ để xác định hướng di chuyển (Trái/Phải/Giữa)
        self.map_groups = [
            [42, 21, 0, 1, 2, 3, 4, 5, 6, 27, 28, 29, 30, 47, 42, 24, 53, 58, 59, 60, 61, 62, 55, 56, 54, 57], # Trái Đất
            [43, 22, 7, 8, 9, 11, 12, 13, 10, 31, 32, 33, 34, 43, 25], # Namek
            [44, 23, 14, 15, 16, 17, 18, 20, 19, 35, 36, 37, 38, 52, 44, 26, 84, 113, 127, 129], # Xayda
            [102, 92, 93, 94, 96, 97, 98, 99, 100, 103], # Tương Lai
            [109, 108, 107, 110, 106, 105], # Cold
            [68, 69, 70, 71, 72, 64, 65, 63, 66, 67, 73, 74, 75, 76, 77, 81, 82, 83, 79, 80, 131, 132, 133], # Nappa
            [46, 45, 48, 50, 154, 155, 166], # Tháp Leo
            [153, 156, 157, 158, 159], # Mảnh Vỡ
            [149, 147, 152, 151, 148], # Khí Gas
            [173, 174, 175], # Noel
            [123, 124, 122]  # Ngũ Hành Sơn (123 -> 124 -> 122)
        ]

        # Đăng ký các liên kết bản đồ cơ bản (đi bộ/cổng chào)
        self.add_link_maps(0, 21)
        # self.add_link_maps(1, 47) # Disable auto-link, manual override below
        self.add_link_maps(47, 111)

        # ... (keep other lines)

        # Manual link 47 <-> 1
        # 47 -> 1: Waypoint bên trái (Override direction = Left)
        self.add_link_maps(47, 1)
 


        self.add_link_maps(47, 111)
        self.add_link_maps(2, 24)
        self.add_link_maps(5, 29)
        self.add_link_maps(7, 22)
        self.add_link_maps(9, 25)
        self.add_link_maps(13, 33)
        self.add_link_maps(14, 23)
        self.add_link_maps(16, 26)
        self.add_link_maps(20, 37)
        self.add_link_maps(39, 21)
        self.add_link_maps(40, 22)
        self.add_link_maps(41, 23)
        self.add_link_maps(109, 105)
        self.add_link_maps(109, 106)
        self.add_link_maps(106, 107)
        self.add_link_maps(108, 105)
        self.add_link_maps(80, 105)
        self.add_link_maps(84, 104)
        self.add_link_maps(139, 140)

        self.add_link_maps(3, 27, 28, 29, 30)
        self.add_link_maps(11, 31, 32, 33, 34)
        self.add_link_maps(17, 35, 36, 37, 38)
        self.add_link_maps(109, 108, 107, 110, 106)
        self.add_link_maps(47, 46, 45, 48)
        # Fix lỗi kẹt ở 45/46/47 không về được 0 (Làng Aru)
        self.add_link_maps(0, 45) # Link ảo/logic để thoát nhánh cụt
        self.add_link_maps(131, 132, 133)
        self.add_link_maps(160, 161, 162, 163)

        self.add_link_maps(42, 0, 1, 2, 3, 4, 5, 6)
        # Đảo Kame (5) có 4 waypoint đi đến: Rừng Xương (4), Name Kamê (29), Rừng nhiệt đới (217), Đông Karin (6)
        self.add_link_maps(5, 4)   # Đảo Kame <-> Rừng Xương
        self.add_link_maps(5, 29)  # Đảo Kame <-> Name Kamê
        self.add_link_maps(5, 217) # Đảo Kame <-> Rừng nhiệt đới
        self.add_link_maps(5, 6)   # Đảo Kame <-> Đông Karin
        self.add_link_maps(43, 22, 7, 8, 9, 11, 12, 13, 10)
        self.add_link_maps(52, 44, 14, 15, 16, 17, 18, 20, 19)
        self.add_link_maps(53, 58, 59, 60, 61, 62, 55, 56, 54, 57)
        self.add_link_maps(68, 69, 70, 71, 72, 64, 65, 63, 66, 67, 73, 74, 75, 76, 77, 81, 82, 83, 79, 80)
        self.add_link_maps(102, 92, 93, 94, 96, 97, 98, 99, 100, 103)

        self.add_link_maps(153, 156, 157, 158, 159)
        self.add_link_maps(46, 45, 48, 50, 154, 155, 166)
        self.add_link_maps(149, 147, 152, 151, 148)
        self.add_link_maps(173, 174, 175)
        self.add_link_maps(7, 197)

        # Đăng ký các liên kết thông qua NPC (Tàu vũ trụ, đối thoại)
        self.add_npc_link(19, 68, 12, "Đến Nappa", select_name3="Đồng ý", index_npc=1, index_npc2=0)
        self.add_npc_link(68, 19, 12, index_npc=0)
        self.add_npc_link(19, 109, 12, "Đến Cold", index_npc=0)
        
        # Nhóm cổng dịch chuyển đặc biệt (Trạm tàu vũ trụ)
        self.add_portal_group(24, [25, 26, 84], 10, [0, 1, 2])
        self.add_portal_group(25, [24, 26, 84], 11, [0, 1, 2])
        self.add_portal_group(26, [24, 25, 84], 12, [0, 1, 2])
        self.add_portal_group(84, [24, 25, 26], 10, [0, 0, 0])

        self.add_npc_link(27, 102, 38, index_npc=1)
        self.add_npc_link(28, 102, 38, index_npc=1)
        self.add_npc_link(29, 102, 38, index_npc=1)
        self.add_npc_link(102, 27, 38, index_npc=1)

        self.add_npc_link(27, 53, 25, "Vào (miễn phí)", select_name2="Tham Gia", select_name3="OK", index_npc=0, index_npc2=0)

        self.add_npc_link(52, 127, 44, "OK")
        self.add_npc_link(52, 129, 23, "Đại Hội Võ Thuật Lần thứ 23")
        self.add_npc_link(52, 113, 23, "Giải Siêu Hạng")
        self.add_npc_link(113, 52, 22, "Về Đại Hội Võ Thuật")
        self.add_npc_link(127, 52, 44, "Về Đại Hội Võ Thuật")
        self.add_npc_link(129, 52, 23, "Về Đại Hội Võ Thuật")

        self.add_npc_link(80, 131, 60, index_npc=0)
        self.add_npc_link(131, 80, 60, index_npc=1)

        self.add_npc_link(5, 153, 13, "Nói chuyện", "Về khu vực bang", index_npc=1)
        self.add_npc_link(153, 5, 10, "Đảo Kame")
        self.add_npc_link(153, 156, 47, "OK")

        self.add_npc_link(45, 48, 19, index_npc=3)
        self.add_npc_link(48, 45, 20, index_npc=3, index_npc2=0)
        self.add_npc_link(48, 50, 20, index_npc=3, index_npc2=1)
        self.add_npc_link(50, 48, 44, index_npc=0)
        self.add_npc_link(50, 154, 44, index_npc=1)
        self.add_npc_link(154, 50, 55, index_npc=0)
        self.add_npc_link(154, 155, 44, index_npc=1)
        self.add_npc_link(155, 154, 44, index_npc=0)

        self.add_npc_link(155, 166, walk=True, x=1400, y=600)
        self.add_npc_link(46, 47, walk=True, x=80, y=700)
        self.add_npc_link(45, 46, walk=True, x=80, y=700)
        self.add_npc_link(46, 45, walk=True, x=380, y=90)

        self.add_npc_link(0, 149, 67, "OK", select_name2="Đồng ý", index_npc=0, index_npc2=0)

        self.add_npc_link(24, 139, 63, index_npc=0)
        self.add_npc_link(139, 24, 63, index_npc=0)
        
        self.add_npc_link(126, 19, 53, "OK", index_npc=0)
        self.add_npc_link(19, 126, 53, "OK", index_npc=0)
        self.add_npc_link(52, 181, 44, "Bình hút năng lượng", "OK", index_npc=0, index_npc2=0)
        self.add_npc_link(181, 52, 44, "Về nhà", index_npc=0)

        # Liên kết sử dụng vật phẩm (Item) để chuyển map
        self.add_npc_link(160, 161, item_id=992)
        self.add_npc_link(181, 52, item_id=1852)

        # --- Thêm liên kết cho Ngủ Hành Sơn (maps 123/124/122)
        # Từ map 0 vào Ngủ Hành Sơn 1 (map 123) thông qua NPC id=49, chọn ô trọn (index 1)
        self.add_npc_link(0, 123, 49, "Đồng ý", index_npc=0)
        # Link quay về từ 123 -> 0 (Giả định NPC 49, index 0)
        self.add_npc_link(123, 0, 49, index_npc=0)

        # Kết nối các map Ngủ Hành Sơn: 123 <-> 124 <-> 122
        # (Khi đang ở 124, bấm trái về 123, bấm phải qua 122)
        self.add_link_maps(123, 124, 122)


    def add_link_maps(self, *args):
        """Tạo chuỗi liên kết 2 chiều giữa các bản đồ: map1 <-> map2 <-> map3..."""
        maps = args
        for i in range(len(maps)):
            u = maps[i]
            if u not in self.link_maps:
                self.link_maps[u] = []
            
            if i > 0:
                v_prev = maps[i-1]
                self.link_maps[u].append(NextMap(v_prev))
            
            if i < len(maps) - 1:
                v_next = maps[i+1]
                self.link_maps[u].append(NextMap(v_next))

    def add_npc_link(self, current, next_map, npc_id=-1, select_name="", select_name2="", select_name3="", 
                     walk=False, x=-1, y=-1, item_id=-1, index_npc=-1, index_npc2=-1, index_npc3=-1, capsule_index=-1):
        """Thêm một liên kết chuyển map cụ thể thông qua NPC hoặc đi bộ tọa độ"""
        if current not in self.link_maps: self.link_maps[current] = []
        self.link_maps[current].append(NextMap(
            next_map, npc_id, select_name, select_name2, select_name3, walk, x, y, item_id, index_npc, index_npc2, index_npc3, capsule_index
        ))

    def add_portal_group(self, from_map, to_maps, npc_id, indices):
        """Hỗ trợ thêm nhanh nhóm liên kết từ một trạm tàu đến nhiều hành tinh khác"""
        for i, to_map in enumerate(to_maps):
            idx = indices[i] if i < len(indices) else -1
            self.add_npc_link(from_map, to_map, npc_id, index_npc=idx)

    def get_map_direction(self, current_id: int, next_id: int) -> str:
        """Xác định hướng của bản đồ kế tiếp (Trái, Phải, hoặc Giữa) dựa trên map_groups"""
        for group in self.map_groups:
            if current_id in group and next_id in group:
                indices_curr = [i for i, x in enumerate(group) if x == current_id]
                indices_next = [i for i, x in enumerate(group) if x == next_id]
                
                for ic in indices_curr:
                    for inext in indices_next:
                        if inext == ic + 1: return "Right" # Bên phải trong danh sách
                        if inext == ic - 1: return "Left"  # Bên trái trong danh sách
        
        return "Center" # Mặc định ở giữa
        
    def check_has_capsule(self) -> Tuple[bool, int]:
        """Kiểm tra xem nhân vật có Capsule (ID 194) không. Trả về (Has, BagIndex)."""
        char = self.controller.account.char
        if not char.arr_item_bag:
            return False, -1
        for i, item in enumerate(char.arr_item_bag):
            if item and item.item_id == 194:
                return True, i
        return False, -1

    def get_capsule_destinations(self) -> List[Tuple[int, int]]:
        """
        Trả về danh sách các điểm đến của Capsule với Index ĐỘNG.
        Logic: 
        1. Lấy danh sách map chuẩn từ server.
        2. Lọc ra các map trùng với map hiện tại.
        3. Xác định index dựa trên việc có "Về chỗ cũ" hay không.
        """
        gender = self.controller.account.char.gender
        current_map_id = self.controller.tile_map.map_id
        
        home_map = {0: 21, 1: 22, 2: 23}.get(gender, 21)
        station_map = {0: 24, 1: 25, 2: 26}.get(gender, 24)
        
        # Danh sách chuẩn theo thứ tự server (Master List)
        # Key: Map ID, Value: Tên map (để debug)
        master_maps = {
            home_map: "Về nhà",
            47: "Rừng Karin",
            48: "Hành tinh Kaio",
            0: "Làng Aru",
            7: "Làng Mori",
            14: "Làng Kakarot",
            5: "Đảo Kame",
            20: "Vách núi đen",
            13: "Đảo Guru",
            station_map: "Trạm tàu vũ trụ",
            27: "Rừng Bamboo",
            19: "Thành phố Vegeta",
            79: "Núi khỉ đỏ",
            84: "Siêu Thị",
            83: "Hang khỉ đen",
            166: "Hành tinh ngục tù",
            121: "Đấu trường Jiren",
            103: "Võ đài Xên bọ hung",
            110: "Hang băng",
        }
        
        available_dests = []
        for map_id in master_maps.keys():
            if map_id != current_map_id:
                available_dests.append(map_id)
        
        # Logic "Về chỗ cũ": nếu map hiện tại là map vừa capsule tới,
        # server sẽ thêm dòng "Về chỗ cũ" ở index 0.
        # Điều này làm các index khác bị dịch xuống 1.
        ui_offset = 0
        if self.capsule_history and self.capsule_history[-1] == current_map_id:
            ui_offset = 1

        result = []
        for i, map_id in enumerate(available_dests):
            result.append((map_id, i + ui_offset))
            
        return result

    async def start(self, map_id: int, keep_dangerous: bool = False):
        """Bắt đầu tiến trình XMap đến bản đồ mục tiêu với thuật toán tối ưu (Dijkstra + Capsule)"""
        char = self.controller.account.char
        gender = char.gender
        home_map_ids = {0: 21, 1: 22, 2: 23} # TD, NM, XD

        # Kiểm tra xem map mục tiêu có phải là nhà của hành tinh khác không
        is_a_home_map = map_id in home_map_ids.values()
        is_own_home_map = (map_id == home_map_ids.get(gender))

        if is_a_home_map and not is_own_home_map:
            planet_names = {0: "Trái Đất", 1: "Namek", 2: "Xayda"}
            target_planet_name = "Không xác định"
            for p_gender, p_map_id in home_map_ids.items():
                if p_map_id == map_id:
                    target_planet_name = planet_names.get(p_gender, "Không xác định")
                    break
            
            username = getattr(self.controller.account, 'username', 'Unknown')
            msg = f"Không thể vào nhà của hành tinh khác. Điểm đến ({target_planet_name}) không phù hợp."
            
            if logger.disabled:
                print(f"\n[{C.YELLOW}{username}{C.RESET}] {C.RED}{msg}{C.RESET} {' ' * 20}")
            else:
                logger.error(f"[{username}] {msg}")
            return

        self.is_xmapping = True
        self.target_map_id = map_id
        current_map = self.controller.tile_map.map_id
        self.history = [current_map]
        self.capsule_history = []
        
        if not keep_dangerous:
            self.dangerous_maps.clear()
        
        logger.info(f"Bắt đầu XMap (Smart): {current_map} -> {map_id}")
        
        if current_map == map_id:
            self.finish()
            return

        # Tìm đường đi tối ưu
        self.path = self.find_path(current_map, map_id)
        
        if not self.path:
            logger.error(f"Không tìm thấy đường đi từ {current_map} đến {map_id}")
            self.finish()
        else:
            # Format log đường đi cho gọn
            path_str = " -> ".join(str(p) for p in self.path)
            logger.info(f"Đường đi tối ưu ({len(self.path)-1} bước): {path_str}")
            asyncio.create_task(self.run_loop())

    async def go_home(self):
        """Tự động xác định map nhà dựa trên hành tinh (gender) và di chuyển về."""
        gender = self.controller.account.char.gender
        home_map_ids = {0: 21, 1: 22, 2: 23} # Map ID nhà: 21 (TD), 22 (NM), 23 (XD)
        target_home = home_map_ids.get(gender, 21)
        logger.info(f"Về nhà: {target_home}")
        await self.start(target_home)

    async def run_loop(self):
        """Vòng lặp chính duy trì trạng thái XMap"""
        while self.is_xmapping:
            await self.update()
            await asyncio.sleep(0.01)

    def finish(self):
        """Kết thúc XMap và hiển thị lộ trình đã đi"""
        self.is_xmapping = False
        self.processing_map_change = False
        username = getattr(self.controller.account, 'username', 'Unknown')
        
        current_map = self.controller.tile_map.map_id
        
        # Format lịch sử map đã đi
        history_str = " -> ".join(map(str, self.history))
        
        # Format thông tin capsule nếu có dùng
        capsule_str = ""
        if self.capsule_history:
            capsule_str = f" [{C.CYAN}Capsule: {', '.join(map(str, self.capsule_history))}{C.RESET}]"

        if current_map == self.target_map_id:
            msg = f"Đã đến bản đồ mục tiêu: {C.GREEN}{self.target_map_id}{C.RESET}{capsule_str} {C.GREY}[{history_str}]{C.RESET}"
            log_func = logger.info
        else:
            msg = f"XMap kết thúc. {C.RED}(Chưa đến đích: {current_map} -> {self.target_map_id}){C.RESET} {C.GREY}[{history_str}]{C.RESET}"
            log_func = logger.warning

        if logger.disabled:
            print(f"[{C.YELLOW}{username}{C.RESET}] {msg} {' ' * 20}")
        else:
            log_func(f"\n[{C.YELLOW}{username}{C.RESET}] {msg} {' ' * 20}")
      

    def _has_item(self, item_id: int) -> bool:
        """Kiểm tra nhân vật có vật phẩm cụ thể không."""
        char = self.controller.account.char
        if not char.arr_item_bag:
            return False
        for item in char.arr_item_bag:
            if item and item.item_id == item_id:
                return True
        return False

    def _is_map_accessible(self, map_id: int, char) -> bool:
        """Kiểm tra xem một bản đồ có thể truy cập được không dựa trên các yêu cầu."""
        try:
            # 1. Yêu cầu Sức mạnh
            # Map 155, 166: >= 60 Tỷ
            if map_id in self.power_60b_maps and char.c_power < 60_000_000_000:
                return False
            # Map 153-159 (trừ 155): >= 40 Tỷ
            if map_id in self.power_40b_maps and char.c_power < 40_000_000_000:
                return False

            # 2. Yêu cầu Nhiệm vụ
            task_id = char.task_main.id if hasattr(char, 'task_main') else 0
            
            # Map Tương Lai: Task ID > 24
            if map_id in self.future_maps and task_id <= 24:
                return False
            
            # Map Cold (105-110): Xong Task 30 (tức là Task ID > 30)
            if map_id in self.cold_maps and task_id <= 30:
                return False
            
            # Map Fide ( núi khỉ vàng) (80): Yêu cầu Task ID >= 21
            if map_id == 80 and task_id < 21:
                return False

            # 3. Yêu cầu Bang hội: Map 53-62
            # Lưu ý: self.clan_maps hiện tại có thể chứa nhiều map hơn, 
            # nhưng yêu cầu user chỉ định rõ 53-62. 
            # Ta sẽ check cứng dải map 53-62 để đảm bảo đúng yêu cầu.
            if 53 <= map_id <= 62:
                has_clan = hasattr(char, 'clan') and char.clan is not None and char.clan.id != -1
                if not has_clan:
                    return False
            
            # 4. Yêu cầu Vật phẩm
            # Map 160: Có item 992 (Nhẫn thời không)
            if map_id == 160:
                if not self._has_item(992):
                    return False
                
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra map {map_id}: {e}")
            return False

        return True

    def find_path(self, start: int, end: int) -> List[int]:
        """
        Thuật toán tìm đường đi ngắn nhất (Dijkstra) kết hợp đi bộ và Capsule.
        - Chi phí đi bộ/npc: 1
        - Chi phí dùng capsule: 1.5 (Ưu tiên hơn đi bộ 2 map, nhưng kém hơn đi bộ 1 map)
        """
        if start == end:
            return [start]

        char = self.controller.account.char
        costs: Dict[int, float] = {start: 0}
        pq: List[Tuple[float, int]] = [(0, start)]
        came_from: Dict[int, Optional[int]] = {start: None}

        has_capsule, _ = self.check_has_capsule()
        capsule_dests = []
        if has_capsule:
            capsule_dests = [dest[0] for dest in self.get_capsule_destinations()]

        while pq:
            current_cost, current_node = heapq.heappop(pq)

            if current_cost > costs.get(current_node, float('inf')):
                continue

            if current_node == end:
                break

            # 1. Khám phá các đường đi bộ/NPC
            if current_node in self.link_maps:
                for next_map_obj in self.link_maps[current_node]:
                    neighbor_node = next_map_obj.map_id
                    if not self._is_map_accessible(neighbor_node, char):
                        continue

                    new_cost = current_cost + 1
                    if new_cost < costs.get(neighbor_node, float('inf')):
                        costs[neighbor_node] = new_cost
                        came_from[neighbor_node] = current_node
                        heapq.heappush(pq, (new_cost, neighbor_node))

            # 2. Khám phá các đường đi bằng Capsule (nếu có)
            # Chi phí = 5.0 để chỉ dùng khi đường đi bộ dài hơn 5 bước
            if has_capsule:
                CAPSULE_COST = 5.0
                for dest_map in capsule_dests:
                    if dest_map == current_node:
                        continue
                    if not self._is_map_accessible(dest_map, char):
                        continue
                        
                    new_cost = current_cost + CAPSULE_COST
                    if new_cost < costs.get(dest_map, float('inf')):
                        costs[dest_map] = new_cost
                        came_from[dest_map] = current_node
                        heapq.heappush(pq, (new_cost, dest_map))

        if end not in came_from:
            return None

        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = came_from.get(curr)
        path.reverse()
        
        if path and path[0] == start:
            return path
        return None

    async def update(self):
        """Cập nhật trạng thái nhân vật và thực hiện bước di chuyển tiếp theo"""
        if not self.is_xmapping: return
        
        if not self.controller.account.session.connected:
            self.finish()
            return

        current_map = self.controller.tile_map.map_id

        # --- Xử lý logic đặc biệt cho map Siêu Thị (84) ---
        if current_map == 84 and self.target_map_id != 84:
            gender = self.controller.account.char.gender
            station_map = {0: 24, 1: 25, 2: 26}.get(gender)

            # Nếu đường đi không bắt đầu bằng việc thoát ra trạm vũ trụ, hãy tính toán lại
            if not self.path or len(self.path) < 2 or self.path[1] != station_map:
                logger.info("Đang ở Siêu Thị (84), định tuyến lại qua trạm vũ trụ...")
                path_from_station = self.find_path(station_map, self.target_map_id)
                
                if path_from_station:
                    self.path = [84] + path_from_station
                    path_str = " -> ".join(str(p) for p in self.path)
                    logger.info(f"Đường đi mới từ Siêu Thị: {path_str}")
                else:
                    logger.error(f"Không tìm thấy đường đi từ trạm vũ trụ ({station_map}) đến {self.target_map_id}")
                    self.finish()
                    return
        
        # Logic Tương Lai: _is_map_accessible đã block future_maps nếu task_id <= 24
        # Không cần logic đặc biệt thêm như code C# gốc

        self.last_update = time.time()
        
        # Theo dõi lịch sử di chuyển
        if self.history and current_map != self.history[-1]:
            self.history.append(current_map)

        try:
            if getattr(self.controller.account.char, 'is_die', False) or getattr(self.controller.account.char, 'c_hp', 1) == 0:
                self.handle_death()
                return
        except Exception:
            pass

        # Reset cờ đổi khu vực nếu đã sang map mới
        if not self.path or current_map != self.path[0]:
             self.zone_changed_in_map = False

        # Xử lý né Boss
        if current_map in self.dangerous_maps and not self.zone_changed_in_map:
            current_zone = self.controller.map_info.get('zone', 0)
            next_zone = random.randint(0, 10)
            while next_zone == current_zone:
                next_zone = random.randint(0, 10)
            await self.controller.account.service.request_change_zone(next_zone)
            self.zone_changed_in_map = True
            return 

        if current_map == self.target_map_id:
            self.finish()
            return
            
        # Kiểm tra trạng thái đang chờ đổi map
        if self.processing_map_change:
            if current_map == self.expected_next_map_id:
                 self.processing_map_change = False
                 self.last_action_time = 0
            elif time.time() - self.last_action_time > 5.0:
                 # Thử tính toán lại đường đi thay vì dừng ngay
                 logger.warning(f"XMap timeout: Thử tính toán lại đường đi từ {current_map}")
                 self.processing_map_change = False
                 self.path = self.find_path(current_map, self.target_map_id)
                 if not self.path:
                     logger.error(f"XMap thất bại: Không thể tìm đường từ {current_map} đến {self.target_map_id}")
                     self.finish()
                     return
            else:
                 return 
        
        # Tính toán lại đường đi nếu bị lạc
        if not self.path or self.path[0] != current_map:
             if current_map in self.path:
                 idx = self.path.index(current_map)
                 self.path = self.path[idx:]
             else:
                 # Recalculate path from current location
                 self.path = self.find_path(current_map, self.target_map_id)
                 if not self.path:
                     self.finish()
                     return

        if len(self.path) < 2:
            return 

        next_map_id = self.path[1]
        
        # 1. Tìm liên kết vật lý có sẵn
        connection = None
        if current_map in self.link_maps:
            for nm in self.link_maps[current_map]:
                if nm.map_id == next_map_id:
                    connection = nm
                    break
        
        # 2. Nếu không có liên kết vật lý, kiểm tra xem có phải là pha nhảy Capsule không
        if connection:
            await self.process_next_map(connection)
        else:
            # Kiểm tra xem next_map_id có trong danh sách Capsule không
            has_capsule, _ = self.check_has_capsule()
            if has_capsule:
                capsules = self.get_capsule_destinations()
                capsule_idx = -1
                for map_dest, idx in capsules:
                    if map_dest == next_map_id:
                        capsule_idx = idx
                        break
                
                if capsule_idx != -1:
                    logger.info(f"Phát hiện đường đi Capsule: {current_map} -> {next_map_id} (Index {capsule_idx})")
                    virtual_connection = NextMap(next_map_id, capsule_index=capsule_idx)
                    await self.process_next_map(virtual_connection)
                    return

            logger.error(f"Không tìm thấy liên kết từ {current_map} đến {next_map_id}")
            self.finish()

    def handle_death(self):
        current_map = self.controller.tile_map.map_id
        logger.warning(f"XMap: Nhân vật chết tại map {current_map}. Đánh dấu nguy hiểm.")
        self.dangerous_maps.add(current_map)
        if self.is_xmapping:
            asyncio.create_task(self.controller.account.service.return_town_from_dead())
            self.finish()
            self.path = []
            self.processing_map_change = False
            self.expected_next_map_id = -1

    async def process_next_map(self, next_map: NextMap):
        """Quyết định phương thức di chuyển"""
        current_map_id = self.controller.tile_map.map_id
        
        # Logic đặc biệt: Capsule Move
        if next_map.capsule_index != -1:
             await self.handle_capsule_move(next_map)
             self.processing_map_change = True
             self.expected_next_map_id = next_map.map_id
             self.last_action_time = time.time()
             return

        if current_map_id != self.path[0]:
             self.processing_map_change = False
             return

        action_performed = False
        username = getattr(self.controller.account, 'username', 'Unknown')
        
        # Verbose Log
        if not logger.disabled:
             logger.info(f"[{C.YELLOW}{username}{C.RESET}] [XMAP] Moving: {C.CYAN}{current_map_id}{C.RESET} -> {C.GREEN}{next_map.map_id}{C.RESET} (Type: {'NPC' if next_map.npc_id != -1 else 'Walk' if next_map.walk else 'Item' if next_map.item_id != -1 else 'Waypoint'})")

        if next_map.npc_id != -1:
            action_performed = await self.handle_npc_move(next_map)
        elif next_map.walk:
            await self.handle_walk_move(next_map)
            action_performed = True
        elif next_map.item_id != -1:
            await self.handle_item_move(next_map)
            action_performed = True 
        else:
            await self.handle_waypoint_move(next_map)
            action_performed = True

        if action_performed:
            self.processing_map_change = True
            self.expected_next_map_id = next_map.map_id
            self.last_action_time = time.time()
            if not logger.disabled:
                logger.info(f"[{C.YELLOW}{username}{C.RESET}] [XMAP] Action performed. Waiting for map {next_map.map_id}...")

    async def handle_capsule_move(self, next_map: NextMap):
        """Thực hiện quy trình sử dụng Capsule"""
        has_item, bag_index = self.check_has_capsule()
        if not has_item or bag_index == -1:
            logger.error("XMap: Cần dùng Capsule nhưng không tìm thấy item trong hành trang.")
            return

        idx_select = next_map.capsule_index
        logger.info(f"Sử dụng Capsule (Slot {bag_index}) -> Chọn dòng {idx_select}")
        
        # Lưu vào lịch sử dùng capsule
        self.capsule_history.append(next_map.map_id)
        
        # 1. Use Item
        # useItem(type=0[bag], where=1[me], index=bag_index, template=-1)
        await self.controller.account.service.use_item(0, 1, bag_index, -1)
        
        # Wait a bit for server to process item usage (Menu opens)
        await asyncio.sleep(0.1) 
        
        # 2. Select Map
        await self.controller.account.service.request_map_select(idx_select)
        
        # Wait for map change logic in update()
        
    async def handle_waypoint_move(self, next_map: NextMap):
        """Xử lý di chuyển qua các điểm chuyển map (Waypoints)"""
        waypoints = self.controller.tile_map.waypoints
        if not waypoints: return

        current_map_id = self.controller.tile_map.map_id
        next_map_id = next_map.map_id
        direction = self.get_map_direction(current_map_id, next_map_id)
        
        if (current_map_id, next_map_id) in self.direction_overrides:
            direction = self.direction_overrides[(current_map_id, next_map_id)]
        
        sorted_wps = sorted(waypoints, key=lambda w: w.center_x)
        target_wp = None
        
        # Xử lý đặc biệt map 7 (Làng Mori) đi map 197
        if current_map_id == 7 and next_map_id == 197 and len(waypoints) >= 3:
            target_wp = waypoints[2] 
        
        # Xử lý đặc biệt map 5 (Đảo Kame) có 4 waypoint
        # Thứ tự waypoint (sorted by x): [Rừng Xương(4)] [Name Kamê(29)] [Rừng nhiệt đới(217)] [Đông Karin(6)]
        if current_map_id == 5 and len(waypoints) >= 4:
            kame_waypoint_map = {
                4: 0,    # Rừng Xương -> waypoint index 0 (ngoài cùng bên trái)
                29: 1,   # Name Kamê -> waypoint index 1
                217: 2,  # Rừng nhiệt đới -> waypoint index 2
                6: 3,    # Đông Karin -> waypoint index 3 (ngoài cùng bên phải)
            }
            if next_map_id in kame_waypoint_map:
                wp_idx = kame_waypoint_map[next_map_id]
                target_wp = sorted_wps[wp_idx]
                logger.info(f"Map Kame: Chọn waypoint {wp_idx} để đến map {next_map_id}") 

        if target_wp is None:
            BASE_MAPS = {42, 43, 44}
            if next_map_id in BASE_MAPS:
                 for wp in sorted_wps:
                     if wp.is_enter or wp.is_offline:
                         target_wp = wp
                         break
            
            if target_wp is None:
                if direction == "Left": target_wp = sorted_wps[0] 
                elif direction == "Right": target_wp = sorted_wps[-1] 
                elif direction == "Up": target_wp = sorted(waypoints, key=lambda w: w.center_y)[0]
                elif direction == "Down": target_wp = sorted(waypoints, key=lambda w: w.center_y)[-1]
                elif direction == "Center": target_wp = sorted_wps[len(sorted_wps) // 2] if len(sorted_wps) > 1 else sorted_wps[0]
        
        if target_wp is None and waypoints: target_wp = waypoints[0]

        await self.controller.movement.enter_waypoint(waypoint_index=waypoints.index(target_wp))

    async def handle_npc_move(self, next_map: NextMap) -> bool:
        """Xử lý tương tác với NPC để chuyển map (Tối ưu)"""
        
        # 1. Đợi NPC load (nếu mới vào map)
        for _ in range(10):  # 10 lần * 0.01s = 0.1s
            await asyncio.sleep(0.01)
            found = any(npc['template_id'] == next_map.npc_id for npc in self.controller.npcs.values())
            if found:
                break
        
        # 2. Teleport đến NPC (dùng teleport_to_npc để đảm bảo mở được menu)
        success = await self.controller.movement.teleport_to_npc(next_map.npc_id)
        if not success:
            logger.warning(f"Không tìm thấy NPC {next_map.npc_id} để teleport.")
            return False
        
        # 3. Mở menu NPC
        await self.controller.account.service.open_menu_npc(next_map.npc_id)
        
        if next_map.index_npc != -1:
             await self.controller.account.service.confirm_menu_npc(next_map.npc_id, next_map.index_npc)
             if next_map.index_npc2 != -1:
                 await self.controller.account.service.confirm_menu_npc(next_map.npc_id, next_map.index_npc2)
        
        return True

    async def handle_walk_move(self, next_map: NextMap):
        char = self.controller.account.char
        char.cx = next_map.x
        char.cy = next_map.y
        await self.controller.account.service.char_move()
        
        # Thử gửi request change map sau khi đi bộ đến tọa độ (phòng trường hợp là cổng)
        await asyncio.sleep(0.2)
        await self.controller.account.service.request_change_map()