import asyncio
from logs.logger_config import logger 
from model.game_objects import Char
from network.service import Service

BEAN_ITEM_ID = 14  # Template ID for "đậu thần" (magic bean)
STAMINA_THRESHOLD = 100  # Use bean when stamina is below this value
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
                await self.check_and_feed()
                await asyncio.sleep(CHECK_INTERVAL)
            except asyncio.CancelledError:
                logger.info("Vòng lặp AutoPet đã bị hủy.")
                break
            except Exception as e:
                logger.error(f"Lỗi trong vòng lặp AutoPet: {e}")
                await asyncio.sleep(CHECK_INTERVAL)

    async def check_and_feed(self):
        """Checks pet's stamina and feeds it a bean if necessary."""
        pet = Char.my_petz()
        if not pet.have_pet:
            logger.warning("AutoPet: Mất thông tin đệ tử, đang dừng...")
            self.stop()
            return

        logger.info(f"AutoPet: Kiểm tra thể lực đệ tử: {pet.c_stamina}/{pet.c_max_stamina}")

        if pet.c_stamina < STAMINA_THRESHOLD:
            logger.info(f"AutoPet: Thể lực đệ tử thấp ({pet.c_stamina}), đang cho ăn đậu...")
            # Use item: type=0 (from bag), where=1 (to self), index=-1 (use template), template_id=BEAN_ITEM_ID
            await Service.gI().use_item(0, 1, -1, BEAN_ITEM_ID)
            # Wait a moment for the action to complete
            await asyncio.sleep(1)
