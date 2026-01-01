import time
import asyncio
import random
from typing import List, Dict, Optional
from logs.logger_config import logger, TerminalColors as C
from network.service import Service

class NextMap:
    """Cấu trúc dữ liệu lưu thông tin để di chuyển sang bản đồ kế tiếp"""
    def __init__(self, map_id: int, npc_id: int = -1, select_name: str = "", select_name2: str = "", select_name3: str = "", 
                 walk: bool = False, x: int = -1, y: int = -1, item_id: int = -1, 
                 index_npc: int = -1, index_npc2: int = -1, index_npc3: int = -1):
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

class XMap:
    def __init__(self, controller):
        self.controller = controller
        self.link_maps: Dict[int, List[NextMap]] = {}
        self.is_xmapping = False
        self.target_map_id = -1
        self.path = []
        self.last_update = 0
        self.update_interval =  0.1 # Khoảng thời gian giữa các hành động (1 giây)
        self.processing_map_change = False
        self.expected_next_map_id = -1
        self.last_action_time = 0
        
        self.dangerous_maps = set() # Lưu danh sách bản đồ có Boss/Nguy hiểm
        self.zone_changed_in_map = False
        
        self.init_map_data()

    def init_map_data(self):
        """Khởi tạo dữ liệu kết nối giữa các bản đồ"""
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
        self.add_link_maps(1, 47)
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
        self.add_link_maps(131, 132, 133)
        self.add_link_maps(160, 161, 162, 163)

        self.add_link_maps(42, 0, 1, 2, 3, 4, 5, 6)
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
        # Kết nối các map Ngủ Hành Sơn: 123 <-> 124 <-> 122
        # (Khi đang ở 124, bấm trái về 123, bấm phải qua 122)
        self.add_link_maps(123, 124, 122)

        # --- Liên kết Ngũ Hành Sơn ---
        # Từ Map 0 sang Map 123 qua NPC 49, chọn dòng 1 (index_npc=0)
        self.add_npc_link(0, 123, 49, index_npc=0) 

        # Liên kết chuỗi các map Ngũ Hành Sơn (Đi bộ qua Waypoint)
        # Thứ tự: 123 <-> 124 <-> 122
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
                     walk=False, x=-1, y=-1, item_id=-1, index_npc=-1, index_npc2=-1, index_npc3=-1):
        """Thêm một liên kết chuyển map cụ thể thông qua NPC hoặc đi bộ tọa độ"""
        if current not in self.link_maps: self.link_maps[current] = []
        self.link_maps[current].append(NextMap(
            next_map, npc_id, select_name, select_name2, select_name3, walk, x, y, item_id, index_npc, index_npc2, index_npc3
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

    async def start(self, map_id: int, keep_dangerous: bool = False):
        """Bắt đầu tiến trình XMap đến bản đồ mục tiêu"""
        self.is_xmapping = True
        self.target_map_id = map_id
        current_map = self.controller.tile_map.map_id
        
        # Xóa dữ liệu bản đồ nguy hiểm cũ khi bắt đầu hành trình mới, trừ khi được yêu cầu giữ lại
        if not keep_dangerous:
            self.dangerous_maps.clear()
        
        logger.info(f"Bắt đầu XMap: {current_map} -> {map_id}")
        
        if current_map == map_id:
            self.finish()
            return

        # Tìm đường đi bằng thuật toán BFS
        self.path = self.find_path(current_map, map_id)
        if not self.path:
            logger.error(f"Không tìm thấy đường đi từ {current_map} đến {map_id}")
            self.finish()
        else:
            logger.info(f"Đường đi: {self.path}")
            asyncio.create_task(self.run_loop())

    async def run_loop(self):
        """Vòng lặp chính duy trì trạng thái XMap"""
        while self.is_xmapping:
            await self.update()
            await asyncio.sleep(self.update_interval)

    def finish(self):
        """Kết thúc XMap"""
        self.is_xmapping = False
        self.processing_map_change = False
        # nếu người dùng không bật logger, in dòng ra thông báo cho người dùng biết là đã tới
        username = getattr(self.controller.account, 'username', 'Unknown')
        if logger.disabled:
            print(f"\n[{C.YELLOW}{username}{C.RESET}] Đã đến bản đồ mục tiêu: {C.GREEN}{self.target_map_id}{C.RESET} {' ' * 20}")
        else:
            logger.info(f"\n[{C.YELLOW}{username}{C.RESET}] Đã đến bản đồ mục tiêu: {C.GREEN}{self.target_map_id}{C.RESET} {' ' * 20}")
      

    def find_path(self, start, end):
        """Thuật toán tìm đường đi ngắn nhất (BFS)"""
        if start == end: return [start]
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            (vertex, path) = queue.pop(0)
            if vertex not in self.link_maps: continue
            
            for next_map_obj in self.link_maps[vertex]:
                neighbor = next_map_obj.map_id
                if neighbor not in visited:
                    if neighbor == end:
                        return path + [neighbor]
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    async def update(self):
        """Cập nhật trạng thái nhân vật và thực hiện bước di chuyển tiếp theo"""
        if not self.is_xmapping: return
        
        # Giới hạn tốc độ cập nhật
        if time.time() - self.last_update < self.update_interval:
            return
        self.last_update = time.time()

        current_map = self.controller.tile_map.map_id
        
        # Nếu nhân vật đang chết, xử lý ngay (về nhà và dừng XMap)
        try:
            if getattr(self.controller.account.char, 'is_die', False):
                logger.warning("XMap: Phát hiện nhân vật đã chết (HP == 0). Thực hiện về nhà và dừng XMap.")
                self.handle_death()
                return
        except Exception:
            # Fall back to direct HP check if property missing
            if getattr(self.controller.account.char, 'c_hp', 1) == 0:
                logger.warning("XMap: Phát hiện nhân vật đã chết (HP == 0). Thực hiện về nhà và dừng XMap.")
                self.handle_death()
                return

        # Reset cờ đổi khu vực nếu đã sang map mới
        if not self.path or current_map != self.path[0]:
             self.zone_changed_in_map = False

        # Xử lý né Boss: Nếu bản đồ này bị đánh dấu nguy hiểm, tự động đổi khu ngẫu nhiên
        if current_map in self.dangerous_maps and not self.zone_changed_in_map:
            current_zone = self.controller.map_info.get('zone', 0)
            next_zone = random.randint(0, 10)
            while next_zone == current_zone:
                next_zone = random.randint(0, 10)
            
            logger.warning(f"XMap: Bản đồ {current_map} nguy hiểm. Đang đổi sang khu {next_zone} để né Boss.")
            await self.controller.account.service.request_change_zone(next_zone)
            self.zone_changed_in_map = True
            return 

        if current_map == self.target_map_id:
            self.finish()
            return
            
        # Kiểm tra trạng thái đang chờ đổi map
        if self.processing_map_change:
            if current_map == self.expected_next_map_id:
                 logger.info(f"Đã sang map {current_map}. Tiếp tục hành trình.")
                 logger.info(f"Đã sang map {current_map}. Tiếp tục hành trình.")
                 self.processing_map_change = False
                 self.last_action_time = 0
            elif time.time() - self.last_action_time > 5.0: 
                 logger.warning("Quá thời gian đổi map. Đang thử lại...")
                 self.processing_map_change = False
            else:
                 return 
        
        # Tính toán lại đường đi nếu bị lạc
        if not self.path or self.path[0] != current_map:
             if current_map in self.path:
                 idx = self.path.index(current_map)
                 self.path = self.path[idx:]
             else:
                 self.path = self.find_path(current_map, self.target_map_id)
                 if not self.path:
                     self.finish()
                     return

        if len(self.path) < 2:
            return 

        next_map_id = self.path[1]
        
        # Tìm đối tượng kết nối tương ứng
        connection = None
        if current_map in self.link_maps:
            for nm in self.link_maps[current_map]:
                if nm.map_id == next_map_id:
                    connection = nm
                    break
        
        if connection:
            await self.process_next_map(connection)
        else:
            logger.error(f"Không tìm thấy liên kết từ {current_map} đến {next_map_id}")
            self.finish()

    def handle_death(self):
        """Được gọi khi nhân vật chết - Đánh dấu bản đồ này là nguy hiểm, gửi lệnh về nhà và dừng XMap."""
        current_map = self.controller.tile_map.map_id
        logger.warning(f"XMap: Nhân vật chết tại map {current_map}. Đánh dấu nguy hiểm.")
        self.dangerous_maps.add(current_map)

        # Nếu đang trong quá trình XMap, gửi lệnh về nhà và kết thúc XMap
        if self.is_xmapping:
            try:
                asyncio.create_task(self.controller.account.service.return_town_from_dead())
            except Exception as e:
                logger.error(f"Lỗi khi cố gắng gửi ME_BACK sau khi chết: {e}")

            # Dừng việc di chuyển tự động và xóa đường đi hiện tại
            self.finish()
            self.path = []
            self.processing_map_change = False
            self.expected_next_map_id = -1

    async def process_next_map(self, next_map: NextMap):
        """Quyết định phương thức di chuyển (NPC, Đi bộ, hay Điểm chuyển map)"""
        current_map_id = self.controller.tile_map.map_id
        if current_map_id != self.path[0]:
             logger.warning(f"XMap: Lệch đường! Hiện tại: {current_map_id}, Mong đợi: {self.path[0]}")
             self.processing_map_change = False
             return

        action_performed = False
        # Hiển thị trạng thái di chuyển ra console cho người dùng khi logger tắt
        if logger.disabled:
            username = getattr(self.controller.account, 'username', 'Unknown')
            logger.info(f"[{C.YELLOW}{username}{C.RESET}] Đang di chuyển: {C.CYAN}{current_map_id}{C.RESET} -> {C.GREEN}{next_map.map_id}{C.RESET}...", end="\r")
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
            # Đợi cho đến khi hệ thống ghi nhận việc đổi map thành công
            start_wait = time.time()
            while self.controller.tile_map.map_id == current_map_id:
                if time.time() - start_wait > 5.0:
                    logger.warning("Hết thời gian chờ đổi map trong process_next_map.")
                    break
                await asyncio.sleep(0.5)
            
            self.processing_map_change = True
            self.expected_next_map_id = next_map.map_id
            self.last_action_time = time.time()

    async def handle_waypoint_move(self, next_map: NextMap):
        """Xử lý di chuyển qua các điểm chuyển map (Waypoints)"""
        waypoints = self.controller.tile_map.waypoints
        if not waypoints:
            logger.warning("Không tìm thấy điểm chuyển map nào.")
            return

        current_map_id = self.controller.tile_map.map_id
        next_map_id = next_map.map_id
        direction = self.get_map_direction(current_map_id, next_map_id)
        
        # Sắp xếp các điểm chuyển map theo trục X
        sorted_wps = sorted(waypoints, key=lambda w: w.center_x)
        target_wp = None
        
        # Xử lý các trường hợp đặc biệt (ví dụ: Map 7 đi map 197 qua waypoint số 3)
        if current_map_id == 7 and next_map_id == 197:
            if len(waypoints) >= 3:
                target_wp = waypoints[2] 

        if target_wp is None:
            # Ưu tiên tìm điểm chuyển map ở trung tâm đối với các map nhà (42, 43, 44)
            BASE_MAPS = {42, 43, 44}
            if next_map_id in BASE_MAPS:
                 for wp in sorted_wps:
                     if wp.is_enter or wp.is_offline:
                         target_wp = wp
                         break
            
            # Logic chọn waypoint theo hướng Left/Right/Center
            if target_wp is None:
                if direction == "Left":
                    target_wp = sorted_wps[0] 
                elif direction == "Right":
                    target_wp = sorted_wps[-1] 
                elif direction == "Center":
                    if len(sorted_wps) > 1:
                        target_wp = sorted_wps[len(sorted_wps) // 2]
                    else:
                        target_wp = sorted_wps[0]
        
        # Dự phòng cuối cùng
        if target_wp is None and waypoints:
            target_wp = waypoints[0]

        logger.info(f"XMap: Đi {current_map_id}->{next_map_id} (Hướng: {direction}). Chọn WP: {target_wp.name}")
        await self.controller.movement.enter_waypoint(waypoint_index=waypoints.index(target_wp))

    async def handle_npc_move(self, next_map: NextMap) -> bool:
        """Xử lý tương tác với NPC để chuyển map"""
        target_npc = None
        max_retries = 10
        # Tìm NPC cụ thể trong map
        for _ in range(max_retries):
            for npc in self.controller.npcs.values():
                if npc['template_id'] == next_map.npc_id:
                    target_npc = npc
                    break
            
            if target_npc:
                logger.info(f"Tìm thấy NPC {next_map.npc_id}. Đang tiến tới...")
                await self.controller.movement.teleport_to(target_npc['x'], target_npc['y'] - 3)
                break
            await asyncio.sleep(0.1)
        else:
            logger.warning(f"Không tìm thấy NPC {next_map.npc_id} sau nhiều lần thử.")
            return False 
        
        # Mở menu và chọn các tùy chọn tương ứng
        await self.controller.account.service.open_menu_npc(next_map.npc_id)
        
        if next_map.index_npc != -1:
             await self.controller.account.service.confirm_menu_npc(next_map.npc_id, next_map.index_npc)
             if next_map.index_npc2 != -1:
                 await self.controller.account.service.confirm_menu_npc(next_map.npc_id, next_map.index_npc2)
        
        return True

    async def handle_walk_move(self, next_map: NextMap):
        """Xử lý đi bộ đến tọa độ để kích hoạt chuyển map"""
        char = self.controller.account.char
        char.cx = next_map.x
        char.cy = next_map.y
        await self.controller.account.service.char_move()

    async def handle_item_move(self, next_map: NextMap):
        """Xử lý sử dụng vật phẩm (Chưa triển khai logic cụ thể)"""
        pass