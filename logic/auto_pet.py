import asyncio
from logs.logger_config import logger 
from model.game_objects import Char
from network.service import Service

BEAN_ITEM_ID = 595  # Template ID for "đậu thần" (magic bean)
STAMINA_THRESHOLD = 50  # Use bean when stamina is below this value
CHECK_INTERVAL = 2  # Seconds to wait between checks

class AutoPet:
    def __init__(self, controller):
        self.controller = controller
        self.is_running = False
        self.task: asyncio.Task = None

    def start(self):
        """Starts the auto-pet leveling task."""
        if not self.is_running:
            pet = self.controller.account.pet
            if not pet.have_pet:
                logger.warning(f"[{self.controller.account.username}] AutoPet: Không có đệ tử để bắt đầu.")
                return None

            self.is_running = True
            self.task = asyncio.create_task(self.loop())
            logger.info(f"[{self.controller.account.username}] Bắt đầu Auto-level Đệ tử.")
            return self.task
        return None

    def stop(self):
        """Stops the auto-pet leveling task."""
        if self.is_running:
            self.is_running = False
            if self.task:
                self.task.cancel()
            logger.info(f"[{self.controller.account.username}] Đã dừng Auto-level Đệ tử.")

    async def loop(self):
        """The main loop for checking pet status and taking action."""
        logger.info(f"[{self.controller.account.username}] Vòng lặp AutoPet đang chạy...")
        service = self.controller.account.service

        # Command the pet to attack initially
        await service.pet_status(1)
        logger.info(f"[{self.controller.account.username}] AutoPet: Đã ra lệnh cho đệ tử bảo vệ.")

        while self.is_running:
            try:
                await service.pet_info()
                await asyncio.sleep(0.5)

                await self.check_and_feed()
                await asyncio.sleep(CHECK_INTERVAL)
            except asyncio.CancelledError:
                logger.info(f"[{self.controller.account.username}] Vòng lặp AutoPet đã bị hủy.")
                break
            except Exception as e:
                logger.error(f"[{self.controller.account.username}] Lỗi trong vòng lặp AutoPet: {e}")
                await asyncio.sleep(CHECK_INTERVAL)

    async def check_and_feed(self):
        """Kiểm tra thể lực của đệ tử và cho ăn đậu nếu cần."""
        pet = self.controller.account.pet
        char = self.controller.account.char
        service = self.controller.account.service

        if not pet.have_pet:
            logger.warning(f"[{self.controller.account.username}] AutoPet: Mất thông tin đệ tử, đang dừng...")
            self.stop()
            return

        logger.info(f"[{self.controller.account.username}] AutoPet: Kiểm tra thể lực đệ tử: {pet.c_stamina}/{pet.c_max_stamina}")
        
        if pet.c_stamina < STAMINA_THRESHOLD:
            logger.info(f"[{self.controller.account.username}] AutoPet: Thể lực đệ tử thấp ({pet.c_stamina}). Đang tìm đậu thần trong túi đồ...")
            
            found_bean = False
            bean_inventory_index = -1
            
            inventory = char.arr_item_bag
            if not inventory:
                logger.warning(f"[{self.controller.account.username}] AutoPet: Không thể tìm thấy đậu vì túi đồ trống.")
            else:
                for index, item in enumerate(inventory):
                    if item and item.item_id == BEAN_ITEM_ID:
                        found_bean = True
                        bean_inventory_index = index
                        logger.info(f"[{self.controller.account.username}] AutoPet: Đã tìm thấy đậu thần tại vị trí túi đồ: {index}")
                        break

            if found_bean:
                logger.info(f"[{self.controller.account.username}] AutoPet: Sử dụng đậu thần tại vị trí {bean_inventory_index} cho sư phụ...")
                await service.use_item(0, 1, bean_inventory_index, -1)
                await asyncio.sleep(1)
            else:
                logger.warning(f"[{self.controller.account.username}] AutoPet: Không tìm thấy đậu thần trong túi đồ.")

