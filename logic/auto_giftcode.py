import asyncio
import re
from logs.logger_config import logger
from constants.cmd import Cmd
from model.map_objects import Waypoint

class AutoGiftcode:
    def __init__(self, controller):
        self.controller = controller
        self.account = controller.account
        self.codes = []
        self.is_running = False
        self.current_code_index = 0
        self.step = 0 # 0: Check map, 1: Find NPC, 2: Open Menu, 3: Select Menu, 4: Input Code, 5: Done/Next

    def start(self, codes: list[str]):
        if self.is_running:
            return
        self.codes = codes
        self.is_running = True
        self.current_code_index = 0
        self.step = 0
        logger.info(f"[{self.account.username}] Bắt đầu Auto Giftcode: {codes}")
        asyncio.create_task(self.process())

    def stop(self):
        self.is_running = False
        logger.info(f"[{self.account.username}] Dừng Auto Giftcode.")

    async def process(self):
        while self.is_running and self.current_code_index < len(self.codes):
            try:
                char = self.account.char
                current_code = self.codes[self.current_code_index]
                
                # Step 0: Check Map (Home Map: 21, 22, 23)
                home_maps = [21, 22, 23]
                if char.map_id not in home_maps:
                    logger.info(f"[{self.account.username}] Không ở map nhà ({char.map_id}). Đang về nhà...")
                    await self.account.service.return_town_from_dead() # Or use capsule if available
                    # Wait for map change
                    await asyncio.sleep(5)
                    continue

                # Step 1: Find Help NPC (Gohan: 0, Moori: 1, Paragus: 2)
                npc_id = -1
                if char.map_id == 21: npc_id = 0
                elif char.map_id == 22: npc_id = 1
                elif char.map_id == 23: npc_id = 2
                
                if npc_id == -1:
                     logger.warning(f"[{self.account.username}] Không xác định được NPC tại map {char.map_id}")
                     self.stop()
                     return

                # Check distance to NPC
                npc = self.controller.npcs.get(npc_id)
                if not npc:
                    logger.warning(f"[{self.account.username}] Không tìm thấy NPC {npc_id}")
                    # Try waiting potentially loading
                    await asyncio.sleep(2)
                    continue
                
                dist = abs(char.cx - npc['x']) + abs(char.cy - npc['y'])
                if dist > 100:
                     logger.info(f"[{self.account.username}] NPC ở xa ({dist}). Dịch chuyển tới ({npc['x']}, {npc['y']})")
                     char.cx = npc['x']
                     char.cy = npc['y']
                     await self.account.service.char_move()
                     await asyncio.sleep(1)
                     continue

                # Step 2: Open Menu
                logger.info(f"[{self.account.username}] Mở menu NPC {npc_id}")
                await self.account.service.open_menu(npc_id)
                await asyncio.sleep(1)

                # Step 3: Select "Nhap giftcode" (Menu ID 2 generally)
                # We assume the bot knows the menu index for Giftcode is 2. 
                # Better approach: wait for OPEN_UI_CONFIRM or similar, but for now hardcode select 2.
                # Actually, Service.open_menu sends request, server responds with CMD 33 (OPEN_MENU) or CMD 40 (TASK_GET??)
                
                # Logic: Open Menu -> Server sends Menu Options -> Select Option
                # Since we don't have a robust menu handler waiting here, we'll optimistically select menu 2
                # But correct flow is: OPEN_MENU (Cmd 27) -> SERVER (Cmd 33/Cmd 22?) -> Confirm (Cmd 22)
                
                await self.account.service.confirm_menu(npc_id, 2)
                logger.info(f"[{self.account.username}] Chọn menu 2 (Giftcode)")
                await asyncio.sleep(1)

                # Step 4: Input Code
                # Wait for Input Dialog? We can just send input.
                logger.info(f"[{self.account.username}] Nhập code: {current_code}")
                await self.account.service.send_client_input([current_code])
                await asyncio.sleep(2) # Wait for server processing
                
                logger.info(f"[{self.account.username}] Đã nhập code {current_code}. Chuyển sang code tiếp theo.")
                self.current_code_index += 1
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"[{self.account.username}] Lỗi Auto Giftcode: {e}")
                await asyncio.sleep(2)
        
        logger.info(f"[{self.account.username}] Hoàn thành danh sách Giftcode.")
        self.stop()
