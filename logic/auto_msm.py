import asyncio
import time
from logs.logger_config import TerminalColors as C, logger

class AutoMsm:
    def __init__(self, controller):
        self.controller = controller
        self.is_running = False
        self.target = "banthan" # "banthan" hoặc "detu"
        self.task = None
        self.state = "INIT"
        self.last_action_time = 0
        
        # Mapping theo hành tinh (gender 0: Trái Đất, 1: Namek, 2: Xayda)
        # Nhà (Nơi có NPC nhận vàng): Trái Đất=21 (Nhà Gôhan), Namek=22 (Nhà Moori), Xayda=23 (Nhà Broly)
        self.home_map_ids = {0: 21, 1: 22, 2: 23}
        self.home_npc_ids = {0: 0, 1: 2, 2: 1}
        # Nâng giới hạn luôn ở Vách núi Moori (Map 43), NPC Quốc vương (ID 42) cho mọi hành tinh
        self.limit_map = 43
        self.limit_npc = 42

    def start(self, target="banthan"):
        if self.is_running:
            logger.info(f"[{self.controller.account.username}] AutoMsm đang chạy. Bỏ qua.")
            return
            
        self.target = target
        self.is_running = True
        self.state = "CHECK_LOCATION"
        self.task = asyncio.create_task(self._run_loop())
        logger.info(f"[{self.controller.account.username}] Đã BẬT AutoMsm (Mục tiêu: {target})")

    def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.task:
            self.task.cancel()
        self.state = "INIT"
        logger.info(f"[{self.controller.account.username}] Đã TẮT AutoMsm")

    def on_server_message(self, text: str):
        if not self.is_running: return
        # Nếu đang ở State chờ nâng cấp và bị báo thiếu vàng
        if "không đủ" in text.lower() and "vàng" in text.lower():
            logger.warning(f"[{self.controller.account.username}] Hết vàng! Chuyển sang trạng thái về làng nhận vàng.")
            self.state = "GO_HOME"
        # Báo nâng thành công
        elif "chúc mừng" in text.lower() or "giới hạn" in text.lower():
            logger.info(f"[{self.controller.account.username}] {text}")
            
    async def _run_loop(self):
        while self.is_running:
            try:
                await self._tick()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Lỗi AutoMsm: {e}")
            await asyncio.sleep(0.1)

    async def _tick(self):
        char = self.controller.account.char
        if not char: return
        
        gender = char.gender
        limit_map = self.limit_map
        limit_npc = self.limit_npc
        home_map = self.home_map_ids.get(gender, 7)
        home_npc = self.home_npc_ids.get(gender, 2)
        
        current_map = self.controller.tile_map.map_id

        if self.state == "CHECK_LOCATION":
            if getattr(char, 'xu', -1) == 0:
                logger.warning(f"[{self.controller.account.username}] Vàng bằng 0! Chuyển sang trạng thái về làng nhận vàng.")
                print(f"[{C.YELLOW}{self.controller.account.username}{C.RESET}] Vàng bằng 0! Chuyển sang trạng thái về làng nhận vàng.")
                self.state = "GO_HOME"
                return
                
            if current_map != limit_map:
                logger.info(f"[{self.controller.account.username}] Di chuyển tới map {limit_map} để nâng giới hạn...")
                await self.controller.xmap.start(limit_map)
                self.state = "MOVING_TO_LIMIT"
            else:
                self.state = "TALK_TO_LIMIT_NPC"
                
        elif self.state == "MOVING_TO_LIMIT":
            if not getattr(self.controller.xmap, 'is_xmapping', False):
                if current_map == limit_map:
                    self.state = "TALK_TO_LIMIT_NPC"
                else:
                    self.state = "CHECK_LOCATION" # Thử lại
                    
        elif self.state == "TALK_TO_LIMIT_NPC":
            if current_map != limit_map:
                self.state = "CHECK_LOCATION"
                return
                
            logger.info(f"[{self.controller.account.username}] Dịch chuyển tới NPC {limit_npc}...")
            await self.controller.movement.teleport_to_npc(limit_npc, search_by_template=True)
            await asyncio.sleep(0.1)

            logger.info(f"[{self.controller.account.username}] Đang mở menu NPC {limit_npc} để nâng sức mạnh...")
            self.controller.ui_menu_event.clear()
            await self.controller.account.service.open_menu_npc(limit_npc)
            
            try:
                await asyncio.wait_for(self.controller.ui_menu_event.wait(), timeout=2.0)
                options = self.controller.last_ui_options
                
                target_str = "bản thân" if self.target == "banthan" else "đệ tử"
                idx1 = -1
                for i, opt in enumerate(options):
                    if target_str in opt.lower().replace("\n", " ").strip():
                        idx1 = i
                        break
                        
                if idx1 != -1:
                    self.controller.ui_menu_event.clear()
                    await self.controller.account.service.confirm_menu_npc(limit_npc, idx1)
                    await asyncio.wait_for(self.controller.ui_menu_event.wait(), timeout=2.0)
                    options = self.controller.last_ui_options
                    chat = getattr(self.controller, 'last_ui_chat', '')
                    
                    if "đạt đến giới hạn" in chat.lower():
                        msg = f"Đã đạt đến giới hạn sức mạnh, tự động TẮT AutoMsm."
                        logger.info(f"[{self.controller.account.username}] {msg}")
                        print(f"[{C.YELLOW}{self.controller.account.username}{C.RESET}] {msg}")
                        self.stop()
                        return
                        
                    idx2 = -1
                    for i, opt in enumerate(options):
                        if "nâng ngay" in opt.lower():
                            idx2 = i
                            break
                            
                    if idx2 != -1:
                        self.controller.ui_menu_event.clear()
                        await self.controller.account.service.confirm_menu_npc(limit_npc, idx2)
                        msg = "Đã bấm Nâng ngay. Chờ kết quả..."
                        logger.info(f"[{self.controller.account.username}] {msg}")
                        print(f"[{C.YELLOW}{self.controller.account.username}{C.RESET}] {msg}")
                        
                        try:
                            await asyncio.wait_for(self.controller.ui_menu_event.wait(), timeout=2.0)
                            chat_after = getattr(self.controller, 'last_ui_chat', '')
                            if "đạt đến giới hạn" in chat_after.lower():
                                msg = f"Đã đạt đến giới hạn sức mạnh, tự động TẮT AutoMsm."
                                logger.info(f"[{self.controller.account.username}] {msg}")
                                print(f"[{C.YELLOW}{self.controller.account.username}{C.RESET}] {msg}")
                                self.stop()
                                return
                        except asyncio.TimeoutError:
                            pass
                            
                        self.state = "WAIT_RESULT"
                        self.last_action_time = time.time()
                    else:
                        self.state = "CHECK_LOCATION"
                else:
                    self.state = "CHECK_LOCATION"
            except asyncio.TimeoutError:
                self.state = "CHECK_LOCATION"
                
        elif self.state == "WAIT_RESULT":
            # Chờ 0.5s xem có báo hết vàng không. Nếu không, tiếp tục lặp lại
            if time.time() - self.last_action_time > 0.5:
                self.state = "CHECK_LOCATION"
                
        elif self.state == "GO_HOME":
            if current_map != home_map:
                logger.info(f"[{self.controller.account.username}] Di chuyển về nhà (Map {home_map}) để nhận vàng...")
                print(f"[{C.YELLOW}{self.controller.account.username}{C.RESET}] Di chuyển về nhà (Map {home_map}) để nhận vàng...")
                await self.controller.xmap.start(home_map)
                self.state = "MOVING_HOME"
            else:
                self.state = "TALK_TO_HOME_NPC"
                
        elif self.state == "MOVING_HOME":
            if not getattr(self.controller.xmap, 'is_xmapping', False):
                if current_map == home_map:
                    self.state = "TALK_TO_HOME_NPC"
                else:
                    self.state = "GO_HOME"
                    
        elif self.state == "TALK_TO_HOME_NPC":
            if current_map != home_map:
                self.state = "GO_HOME"
                return
                
            logger.info(f"[{self.controller.account.username}] Dịch chuyển tới NPC {home_npc} để nhận vàng...")
            await self.controller.movement.teleport_to_npc(home_npc, search_by_template=True)
            await asyncio.sleep(0.2)

            logger.info(f"[{self.controller.account.username}] Đang xin vàng NPC {home_npc}...")
            self.controller.ui_menu_event.clear()
            await self.controller.account.service.open_menu_npc(home_npc)
            
            try:
                await asyncio.wait_for(self.controller.ui_menu_event.wait(), timeout=2.0)
                options = self.controller.last_ui_options
                
                idx = -1
                for i, opt in enumerate(options):
                    opt_lower = opt.lower().replace("\n", " ").strip()
                    if "vàng" in opt_lower and ("nhận" in opt_lower or "xin" in opt_lower or "15 tỷ" in opt_lower):
                        idx = i
                        break
                
                # Fallback: chọn bất kỳ nút nào có chữ vàng
                if idx == -1:
                    for i, opt in enumerate(options):
                        if "vàng" in opt.lower():
                            idx = i
                            break
                        
                if idx != -1:
                    await self.controller.account.service.confirm_menu_npc(home_npc, idx)
                    msg = "Đã bấm nhận vàng. Đợi kết quả..."
                    logger.info(f"[{self.controller.account.username}] {msg}")
                    print(f"[{C.YELLOW}{self.controller.account.username}{C.RESET}] {msg}")
                    self.last_action_time = time.time()
                    self.state = "WAIT_GOLD"
                else:
                    msg = f"Không tìm thấy nút nhận vàng. Các nút hiện có: {options}"
                    logger.warning(f"[{self.controller.account.username}] {msg}")
                    print(f"[{C.RED}{self.controller.account.username}{C.RESET}] {msg}")
                    await asyncio.sleep(5)
                    self.state = "GO_HOME"
            except asyncio.TimeoutError:
                await asyncio.sleep(2)
                self.state = "GO_HOME"
                
        elif self.state == "WAIT_GOLD":
            if getattr(char, 'xu', -1) > 0:
                msg = "Đã nhận được vàng! Quay lại nâng sức mạnh..."
                logger.info(f"[{self.controller.account.username}] {msg}")
                print(f"[{C.GREEN}{self.controller.account.username}{C.RESET}] {msg}")
                self.state = "CHECK_LOCATION"
            elif time.time() - self.last_action_time > 3.0:
                msg = "Quá thời gian đợi vàng. Thử lại..."
                logger.warning(f"[{self.controller.account.username}] {msg}")
                self.state = "GO_HOME"
