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
            pet = Char.my_petz()
            if not pet.have_pet:
                logger.warning("AutoPet: Không có đệ tử để bắt đầu.")
                return

            self.is_running = True
            self.task = asyncio.create_task(self.loop())
            logger.info("Bắt đầu Auto-level Đệ tử.")

    def stop(self):
        """Stops the auto-pet leveling task."""
        if self.is_running:
            self.is_running = False
            if self.task:
                self.task.cancel()
            logger.info("Đã dừng Auto-level Đệ tử.")

    async def loop(self):
        """The main loop for checking pet status and taking action."""
        logger.info("Vòng lặp AutoPet đang chạy...")

        # Command the pet to attack initially
        await Service.gI().pet_status(2)
        logger.info("AutoPet: Đã ra lệnh cho đệ tử tấn công.")

        while self.is_running:
            try:
                await Service.gI().pet_info()
                await asyncio.sleep(0.5)

                await self.check_and_feed()
                await asyncio.sleep(CHECK_INTERVAL)
            except asyncio.CancelledError:
                logger.info("Vòng lặp AutoPet đã bị hủy.")
                break
            except Exception as e:
                logger.error(f"Lỗi trong vòng lặp AutoPet: {e}")
                await asyncio.sleep(CHECK_INTERVAL)

    async def check_and_feed(self):
        """Kiểm tra thể lực của đệ tử và cho ăn đậu nếu cần."""
        pet = Char.my_petz()
        if not pet.have_pet:
            logger.warning("AutoPet: Mất thông tin đệ tử, đang dừng...")
            self.stop()
            return

        logger.info(f"AutoPet: Kiểm tra thể lực đệ tử: {pet.c_stamina}/{pet.c_max_stamina}")
        
        if pet.c_stamina < STAMINA_THRESHOLD:
            logger.info(f"AutoPet: Thể lực đệ tử thấp ({pet.c_stamina}). Đang tìm đậu thần trong túi đồ...")
            
            # FIX: Lặp qua túi đồ để tìm đậu thần và sử dụng `index` của nó.
            # Đây là logic chính xác theo C# user cung cấp.
            found_bean = False
            bean_inventory_index = -1
            
            inventory = Char.my_charz().arr_item_bag
            if not inventory:
                logger.warning("AutoPet: Không thể tìm thấy đậu vì túi đồ trống. Cần cài đặt hàm process_bag_info trong controller.")
            else:
                # Lấy cả index và item
                for index, item in enumerate(inventory):
                    if item and item.item_id == BEAN_ITEM_ID:
                        found_bean = True
                        bean_inventory_index = index
                        logger.info(f"AutoPet: Đã tìm thấy đậu thần tại vị trí túi đồ: {index}")
                        break

            if found_bean:
                logger.info(f"AutoPet: Sử dụng đậu thần tại vị trí {bean_inventory_index} cho sư phụ (đệ tử sẽ được hưởng ké)...")
                # Gọi use_item với type = 0 (sử dụng), where = 1 (túi đồ)
                await Service.gI().use_item(0, 1, bean_inventory_index, -1)
                await asyncio.sleep(1)
            else:
                logger.warning("AutoPet: Không tìm thấy đậu thần trong túi đồ.")

