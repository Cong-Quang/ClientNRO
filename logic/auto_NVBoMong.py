from logs.logger_config import logger
import re
import asyncio
from enum import Enum
import time
import math

MOB_LOCATION_DATA = {
    "mộc nhân": (14, 0), "khủng long": (1, 1), "lợn lòi": (8, 2), "quỷ đất": (15, 3),
    "khủng long mẹ": (2, 4), "lợn lòi mẹ": (9, 5), "quỷ đất mẹ": (16, 6),
    "thằn lằn bay": (3, 7), "phi long": (11, 8), "quỷ bay": (17, 9), "thằn lằn mẹ": (4, 10),
    "phi long mẹ": (12, 11), "quỷ bay mẹ": (18, 12), "ốc mượn hồn": (29, 13),
    "ốc sên": (33, 14), "heo xayda mẹ": (37, 15), "heo rừng": (28, 16),
    "heo da xanh": (32, 17), "heo xayda": (36, 18), "heo rừng mẹ": (6, 19),
    "heo xanh mẹ": (10, 20), "alien": (19, 21), "bulon": (30, 22), "ukulele": (34, 23),
    "quỷ mập": (38, 24), "tambourine": (6, 25), "drum": (10, 26), "akkuman": (19, 27),
    "không tặc": (29, 31), "quỷ đầu to": (33, 32), "quỷ địa ngục": (37, 33),
    "không tặc": (29, 31), "quỷ đầu to": (33, 32), "quỷ địa ngục": (37, 33),
    "nappa": (68, 39), "soldier": (70, 40), "appule": (71, 41), "raspberry": (71, 42),
    "thằn lằn xanh": (72, 43), "quỷ đầu nhọn": (64, 44), "quỷ đầu vàng": (63, 45),
    "quỷ da tím": (66, 46), "quỷ già": (67, 47), "cá sấu": (73, 48),
    "dơi da xanh": (67, 49), "quỷ chim": (81, 50), "lính đầu trọc": (74, 51),
    "lính tai dài": (76, 52), "lính vũ trụ": (77, 53), "khỉ lông đen": (82, 54),
    "khỉ giáp sắt": (83, 55), "khỉ lông đỏ": (79, 56), "khỉ lông vàng": (80, 57),
    "xên con cấp 1": (92, 58), "xên con cấp 2": (93, 59), "xên con cấp 3": (94, 60),
    "xên con cấp 4": (96, 61), "xên con cấp 5": (97, 62), "xên con cấp 6": (98, 63),
    "xên con cấp 7": (99, 64), "xên con cấp 8": (100, 65), "tai tím": (106, 66),
    "abo": (107, 67), "kado": (109, 68), "da xanh": (110, 69),
    "ếch mặt đỏ": (166, 86), "jinai": (166, 87),
    "khỉ lông xanh": (155, 78), "taburine đỏ": (155, 79),
}
BO_MONG_MAP_ID = 47
BO_MONG_NPC_TEMPLATE_ID = 17

class AutoState(Enum):
    IDLE = "Đang nghỉ"
    GET_QUEST = "Đi nhận nhiệm vụ"
    NAVIGATE_TO_MAP = "Di chuyển đến map"
    EXECUTE_QUEST = "Thực hiện nhiệm vụ"
    REPORT_QUEST = "Đi trả nhiệm vụ"

class QuestInfo:
    def __init__(self):
        self.is_valid = False
        self.mob_name = ""
        self.map_name = ""
        self.target_count = 0
        self.initial_count = 0 
        self.kill_count = 0
        self.quests_remaining = 0  # Số NV còn lại trong ngày
        self.quests_total = 0      # Tổng số NV trong ngày

    @property
    def current_progress(self):
        return self.initial_count + self.kill_count

    def __str__(self):
        if not self.is_valid:
            return "QuestInfo(Không có nhiệm vụ)"
        return (f"NV: 'Hạ {self.mob_name}', Map: '{self.map_name}', "
                f"Tiến độ: {self.current_progress}/{self.target_count}")

class AutoQuest:
    def __init__(self, controller):
        self.controller = controller
        self.account = controller.account
        self.quest_info = QuestInfo()
        self.current_state = AutoState.IDLE
        self.is_running = False
        self.task = None
        
        # Thống kê
        self.start_time = None
        self.quests_completed = 0
        self.total_kills = 0

    def start(self):
        if self.is_running:
            logger.info(f"[{self.account.username}] Auto Quest đã chạy rồi.")
            return
        self.is_running = True
        
        # Reset thống kê khi bắt đầu
        self.start_time = time.time()
        self.quests_completed = 0
        self.total_kills = 0
        
        logger.info(f"[{self.account.username}] Bắt đầu Auto Quest.")
        self.current_state = AutoState.GET_QUEST
        logger.info(f"[{self.account.username}] AutoQuest -> {self.current_state.value}")
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self._run_loop())

    def stop(self):
        if not self.is_running: return
        self.is_running = False
        logger.info(f"[{self.account.username}] Đã dừng Auto Quest.")
        if self.task:
            self.task.cancel()
            self.task = None
        self.controller.toggle_autoplay(False)
        self.current_state = AutoState.IDLE
        logger.info(f"[{self.account.username}] AutoQuest -> {self.current_state.value}")
    
    def get_stats(self) -> dict:
        """Trả về thống kê hiện tại"""
        elapsed = 0
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
        
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        
        if hours > 0:
            time_str = f"{hours}h{minutes:02d}m{seconds:02d}s"
        elif minutes > 0:
            time_str = f"{minutes}m{seconds:02d}s"
        else:
            time_str = f"{seconds}s"
        
        return {
            "quests_completed": self.quests_completed,
            "total_kills": self.total_kills,
            "elapsed_time": elapsed,
            "time_str": time_str,
            "quests_remaining": self.quest_info.quests_remaining,
            "quests_total": self.quest_info.quests_total
        }
    async def _interact_with_npc_menu(self, npc_template_id: int, menu_options: list[int] = None) -> bool:
        """
        Hàm helper chung để tương tác với NPC:
        1. Kiểm tra vị trí & khoảng cách (tự động teleport nếu > 60px).
        2. Mở menu NPC.
        3. Lần lượt chọn các option trong menu_options (nếu có).
        """
        try:
            # 1. Logic khoảng cách và Teleport
            should_teleport = True
            
            # Tìm NPC để check khoảng cách
            target_npc = None
            for _, npc_data in self.controller.npcs.items():
                if npc_data.get('template_id') == npc_template_id:
                    target_npc = npc_data
                    break
            
            if target_npc:
                dist = math.sqrt((target_npc['x'] - self.account.char.cx)**2 + 
                                 (target_npc['y'] - self.account.char.cy)**2)
                if dist <= 60:
                    should_teleport = False
            
            if should_teleport:
                await self.controller.movement.teleport_to_npc(npc_template_id)
                await asyncio.sleep(1.0) # Wait for teleport
                
                # Re-check distance after teleport
                if target_npc:
                   # Update target_npc position just in case
                   for _, npc_data in self.controller.npcs.items():
                        if npc_data.get('template_id') == npc_template_id:
                            target_npc = npc_data
                            break
                   
                   dist = math.sqrt((target_npc['x'] - self.account.char.cx)**2 + 
                                     (target_npc['y'] - self.account.char.cy)**2)
                   if dist > 60:
                       logger.warning(f"[{self.account.username}] Khoảng cách tới NPC {npc_template_id} vẫn quá xa ({dist:.1f}). Không thể tương tác.")
                       return False

            # 2. Mở Menu
            await self.controller.account.service.open_menu_npc(npc_template_id)
            await asyncio.sleep(0.5)

            # 3. Chọn Options
            if menu_options:
                for opt_idx in menu_options:
                    await self.controller.account.service.confirm_menu_npc(npc_template_id, opt_idx)
                    await asyncio.sleep(0.5)
            
            return True
        except Exception as e:
            logger.error(f"[{self.account.username}] Lỗi tương tác NPC {npc_template_id}: {e}")
            return False

    async def refresh_quest_info(self) -> bool:
        """
        Query NPC Bố Mộng để lấy thông tin quest hiện tại.
        Sử dụng helper _interact_with_npc_menu.
        """
        if self.account.char.map_id != BO_MONG_MAP_ID:
            logger.info(f"[{self.account.username}] Đang di chuyển về Bò Mộng để refresh quest...")
            await self.go_to_map(BO_MONG_MAP_ID)
            if self.account.char.map_id != BO_MONG_MAP_ID:
                return False

        # Option 1: Nhiệm vụ Hàng ngày
        success = await self._interact_with_npc_menu(BO_MONG_NPC_TEMPLATE_ID, [1])
        if success:
            logger.info(f"[{self.account.username}] Đã query NPC refresh quest info.")
        return success

    async def transition_to(self, new_state: AutoState):
        self.current_state = new_state
        logger.info(f"[{self.account.username}] AutoQuest -> {new_state.value}")
        await asyncio.sleep(0.1)

    async def _run_loop(self):
        logger.info(f"[{self.account.username}] Vòng lặp AutoQuest đã bắt đầu.")
        while self.is_running:
            try:
                await self.update()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[{self.account.username}] Lỗi trong vòng lặp AutoQuest: {e}", exc_info=True)
                self.stop()
                break
            await asyncio.sleep(0.5)
        logger.info(f"[{self.account.username}] Vòng lặp AutoQuest đã kết thúc.")

    async def update(self):
        if self.account.char.is_die:
            logger.warning(f"[{self.account.username}] Nhân vật đã chết, tạm dừng 10s.")
            self.controller.toggle_autoplay(False)
            await asyncio.sleep(10)
            await self.transition_to(AutoState.GET_QUEST)
            return

        state_handler = getattr(self, f"handle_{self.current_state.name.lower()}", None)
        if state_handler:
            await state_handler()

    async def handle_idle(self):
        await asyncio.sleep(0.5)
    
    async def handle_get_quest(self):
        self.quest_info = QuestInfo()
        if self.account.char.map_id != BO_MONG_MAP_ID:
            await self.go_to_map(BO_MONG_MAP_ID)
            return

        logger.info(f"[{self.account.username}] Nhận nhiệm vụ hàng ngày (Siêu khó)...")
        # Sử dụng helper: Chọn Option 1 (Nhiệm vụ hàng ngày) -> Option 4 (Siêu khó)
        await self._interact_with_npc_menu(BO_MONG_NPC_TEMPLATE_ID, [1, 4])
        
        await asyncio.sleep(2)

        if self.quest_info.is_valid:
            await self.transition_to(AutoState.NAVIGATE_TO_MAP)
        else:
            logger.warning(f"[{self.account.username}] Không nhận được thông tin NV mới. Thử lại sau 5s.")
            await asyncio.sleep(5)

    async def handle_navigate_to_map(self):
        if not self.quest_info.is_valid:
            await self.transition_to(AutoState.GET_QUEST)
            return
            
        map_id, _ = self.get_quest_target_ids()
        if map_id == -1:
            logger.warning(f"[{self.account.username}] Không tìm thấy map cho NV '{self.quest_info.mob_name}'. Dừng.")
            self.stop()
            return
        
        # Kiểm tra xem có thể đi đến map đích không (Tương Lai, Cold, Ngục Tù...)
        if not self._can_access_map(map_id):
            logger.warning(f"[{self.account.username}] Không thể vào map {map_id} (chưa đủ điều kiện). Huỷ NV và nhận NV mới.")
            await self._cancel_and_get_new_quest()
            return
        
        if self.account.char.map_id != map_id:
            await self.go_to_map(map_id)
        else:
            await self.transition_to(AutoState.EXECUTE_QUEST)

    async def handle_execute_quest(self):
        # Kiểm tra nếu đã đủ số quái cần giết thì chuyển sang trả nhiệm vụ
        if self.quest_info.is_valid and self.quest_info.current_progress >= self.quest_info.target_count:
            logger.info(f"[{self.account.username}] Đã hoàn thành mục tiêu ({self.quest_info.current_progress}/{self.quest_info.target_count})! Chuyển sang trả nhiệm vụ.")
            self.controller.toggle_autoplay(False)
            await self.transition_to(AutoState.REPORT_QUEST)
            return
        
        # Luôn đảm bảo target_mobs đúng với nhiệm vụ hiện tại
        _, mob_id = self.get_quest_target_ids()
        current_targets = self.controller.auto_play.target_mobs
        
        # Debug log 
        logger.info(f"[{self.account.username}] [DEBUG] Quest mob: {self.quest_info.mob_name}, need template_id={mob_id}, current target_mobs={current_targets}")
        
        if mob_id != -1:
            # Luôn set target_mobs để đảm bảo đúng
            if mob_id not in current_targets or len(current_targets) != 1:
                self.controller.auto_play.target_mobs.clear()
                self.controller.auto_play.target_mobs.add(mob_id)
                logger.info(f"[{self.account.username}] Đã set target_mobs = {{{mob_id}}} ({self.quest_info.mob_name})")
        
        if not self.controller.auto_play.interval:
            logger.info(f"[{self.account.username}] Bắt đầu tự động đánh quái: {self.quest_info.mob_name} (Tiến độ: {self.quest_info.current_progress}/{self.quest_info.target_count})")
            self.controller.toggle_autoplay(True)

    async def handle_report_quest(self):
        self.controller.toggle_autoplay(False)
        if self.account.char.map_id != BO_MONG_MAP_ID:
            await self.go_to_map(BO_MONG_MAP_ID)
            return

        logger.info(f"[{self.account.username}] Tiến hành trả nhiệm vụ (Tiến độ local: {self.quest_info.current_progress}/{self.quest_info.target_count}).")
        
        old_quest_info = self.quest_info
        
        # 1. Trả nhiệm vụ: [1] Nhiệm vụ hằng ngày -> [0] Trả nhiệm vụ
        await self._interact_with_npc_menu(BO_MONG_NPC_TEMPLATE_ID, [1, 0])
        await asyncio.sleep(2)
        
        # 2. Kiểm tra kết quả trả NV từ server
        # Nếu quest_info vẫn giữ nguyên mob cũ với progress < target -> Server báo chưa đủ
        if self.quest_info.is_valid and self.quest_info.mob_name == old_quest_info.mob_name:
            if self.quest_info.initial_count < self.quest_info.target_count:
                # Server báo chưa đủ số lượng, tiếp tục farm
                logger.info(f"[{self.account.username}] Server: chưa đủ ({self.quest_info.initial_count}/{self.quest_info.target_count}). Tiếp tục farm!")
                await self.transition_to(AutoState.NAVIGATE_TO_MAP)
                return
        
        # 3. Trả NV thành công -> Reset data cũ
        logger.info(f"[{self.account.username}] Trả NV thành công! Reset và nhận NV mới...")
        self.quests_completed += 1
        self.quest_info = QuestInfo()  # Reset data cũ
        
        # 4. Nhận NV mới: [1] Nhiệm vụ hằng ngày -> [4] Siêu khó
        await self._interact_with_npc_menu(BO_MONG_NPC_TEMPLATE_ID, [1, 4])
        await asyncio.sleep(2)
        
        if self.quest_info.is_valid:
            # Kiểm tra điều kiện map trước khi đi
            map_id, _ = self.get_quest_target_ids()
            if map_id != -1 and not self._can_access_map(map_id):
                logger.warning(f"[{self.account.username}] NV mới yêu cầu map {map_id} không thể vào. Huỷ và nhận NV khác...")
                await self._cancel_and_get_new_quest()
                return
            
            logger.info(f"[{self.account.username}] Đã nhận NV mới: {self.quest_info.mob_name} (Tổng hoàn thành: {self.quests_completed})")
            await self.transition_to(AutoState.NAVIGATE_TO_MAP)
        else:
            logger.warning(f"[{self.account.username}] Không nhận được NV mới. Thử lại...")
            await self.transition_to(AutoState.GET_QUEST)

    def parse_quest_info(self, menu_text: str):
        lower_text = menu_text.lower()
        
        # Debug log để xem raw text
        logger.info(f"[{self.account.username}] parse_quest_info raw: {repr(menu_text[:300])}...")
        
        # Check hết nhiệm vụ trong ngày
        if "hết nhiệm vụ cho hôm nay" in lower_text:
            logger.info(f"[{self.account.username}] Đã hết nhiệm vụ hàng ngày. Dừng auto.")
            self.stop()
            return
        
        # Check số nhiệm vụ còn lại = 0
        match_remaining = re.search(r"số nhiệm vụ còn lại của hôm nay\s+(\d+)/(\d+)", lower_text)
        if match_remaining:
            remaining = int(match_remaining.group(1))
            total = int(match_remaining.group(2))
            logger.info(f"[{self.account.username}] Nhiệm vụ còn lại: {remaining}/{total}")
            # Lưu thông tin NV còn lại
            self.quest_info.quests_remaining = remaining
            self.quest_info.quests_total = total
            if remaining <= 0:
                logger.info(f"[{self.account.username}] Đã hết nhiệm vụ trong ngày ({remaining}/{total}). Dừng auto.")
                self.stop()
                return
            
        if "nhiệm vụ của bạn" not in lower_text:
            return

        quest = QuestInfo()
        
        # Raw text dùng newline \n làm separator giữa các dòng
        # Format: "Nhiệm vụ của bạn  Tiêu diệt 2154 dơi da xanh\nĐịa điểm nhiệm vụ..."
        match_task = re.search(r"nhiệm vụ của bạn\s+tiêu diệt\s+\d+\s+([^\n]+)", lower_text)
        if match_task:
            quest.is_valid = True
            quest.mob_name = match_task.group(1).strip()
            logger.info(f"[{self.account.username}] Regex match mob_name: '{quest.mob_name}'")
        else:
            logger.warning(f"[{self.account.username}] Regex không khớp được với mô tả nhiệm vụ. Text: {repr(lower_text[:300])}")
            return

        match_location = re.search(r"địa điểm nhiệm vụ\s+([^\n]+)", lower_text)
        if match_location:
            quest.map_name = match_location.group(1).strip()
            
        match_progress = re.search(r"tiến độ nhiệm vụ\s+(\d+)/(\d+)", lower_text)
        if match_progress:
            quest.initial_count = int(match_progress.group(1))
            quest.target_count = int(match_progress.group(2))
        
        quest.kill_count = 0
        self.quest_info = quest
        logger.info(f"[{self.account.username}] Nhiệm vụ được cập nhật: {self.quest_info}")

    def increment_kill_count(self, mob_template_id: int):
        # Debug: Log mọi lần gọi hàm này
        _, quest_mob_id = self.get_quest_target_ids()
        
        # Kiểm tra điều kiện
        if not self.is_running:
            return
        if not self.quest_info.is_valid:
            return
        if self.current_state != AutoState.EXECUTE_QUEST:
            return
        
        # Log chi tiết để debug khi template_id không khớp
        if mob_template_id != quest_mob_id:
            logger.warning(f"[{self.account.username}] Giết quái template_id={mob_template_id}, cần={quest_mob_id} ({self.quest_info.mob_name}) - KHÔNG KHỚP")
            return
            
        self.quest_info.kill_count += 1
        self.total_kills += 1  # Thống kê tổng số quái đã giết
        logger.info(f"[{self.account.username}] Đã diệt {self.quest_info.mob_name} ({self.quest_info.current_progress}/{self.quest_info.target_count})")
        
        # Khi đủ mục tiêu, dừng autoplay - handle_execute_quest sẽ xử lý chuyển trạng thái
        if self.quest_info.current_progress >= self.quest_info.target_count:
            logger.info(f"[{self.account.username}] Đã đủ mục tiêu! Dừng đánh quái...")
            self.controller.toggle_autoplay(False)

    def get_quest_target_ids(self) -> (int, int):
        if not self.quest_info or not self.quest_info.mob_name:
            return -1, -1
        
        target_name_lower = self.quest_info.mob_name.lower().strip()
        
        for name, ids in MOB_LOCATION_DATA.items():
            if name.lower() == target_name_lower:
                return ids
        
        # Fallback for partial match
        for name, ids in MOB_LOCATION_DATA.items():
            if target_name_lower in name.lower():
                logger.info(f"[{self.account.username}] Tìm thấy quái '{name}' khớp một phần với '{target_name_lower}'")
                return ids
        
        logger.warning(f"[{self.account.username}] Không tìm thấy dữ liệu cho quái: '{self.quest_info.mob_name}'")
        return -1, -1

    def _can_access_map(self, map_id: int) -> bool:
        """Kiểm tra xem nhân vật có thể vào map đích không dựa trên điều kiện."""
        char = self.account.char
        xmap = self.controller.xmap
        
        # Sử dụng logic kiểm tra từ XMap
        return xmap._is_map_accessible(map_id, char)

    async def _cancel_and_get_new_quest(self):
        """Huỷ nhiệm vụ hiện tại và nhận nhiệm vụ mới."""
        logger.info(f"[{self.account.username}] Huỷ nhiệm vụ không thể hoàn thành...")
        
        if self.account.char.map_id != BO_MONG_MAP_ID:
            await self.go_to_map(BO_MONG_MAP_ID)
            if self.account.char.map_id != BO_MONG_MAP_ID:
                return  # Không về được map, thử lại sau
        
        # Huỷ NV: [1] Nhiệm vụ hằng ngày -> [1] Huỷ nhiệm vụ
        await self._interact_with_npc_menu(BO_MONG_NPC_TEMPLATE_ID, [1, 1])
        await asyncio.sleep(1)
        
        # Reset quest info
        self.quest_info = QuestInfo()
        
        # Nhận NV mới ngay: [1] Nhiệm vụ hằng ngày -> [4] Siêu khó
        await self._interact_with_npc_menu(BO_MONG_NPC_TEMPLATE_ID, [1, 4])
        await asyncio.sleep(2)
        
        if self.quest_info.is_valid:
            # Kiểm tra lại xem NV mới có vào được map không
            map_id, _ = self.get_quest_target_ids()
            if map_id != -1 and not self._can_access_map(map_id):
                logger.warning(f"[{self.account.username}] NV mới vẫn không thể vào map {map_id}. Huỷ tiếp...")
                # Gọi đệ quy để huỷ và nhận NV khác
                await self._cancel_and_get_new_quest()
                return
            
            logger.info(f"[{self.account.username}] Đã nhận NV mới: {self.quest_info.mob_name}")
            await self.transition_to(AutoState.NAVIGATE_TO_MAP)
        else:
            await self.transition_to(AutoState.GET_QUEST)

    async def go_to_map(self, map_id: int):
        if self.account.char.map_id == map_id:
            return
        logger.info(f"[{self.account.username}] Bắt đầu di chuyển đến map ID {map_id}")
        await self.controller.xmap.start(map_id)
        while self.controller.xmap.is_xmapping:
            if not self.is_running:
                self.controller.xmap.finish()
                return
            await asyncio.sleep(0.5)
        
        if self.account.char.map_id != map_id:
            # Thử lại 1 lần nếu thất bại
            logger.warning(f"[{self.account.username}] Di chuyển đến map {map_id} thất bại. Thử lại...")
            await self.controller.xmap.start(map_id)
            # Wait check loop again or simple check? let's just return and let main loop handle retry
            if self.account.char.map_id != map_id:
                 logger.error(f"[{self.account.username}] Di chuyển vẫn thất bại. Dừng AutoQuest.")
                 self.stop()
        else:
            logger.info(f"[{self.account.username}] Di chuyển đến map {map_id} thành công.")
