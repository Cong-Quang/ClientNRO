import asyncio
import time
from logs.logger_config import logger

USE_INTERVAL = 1800  # 30 minutes in seconds (30 * 60)

class AutoItem:
    def __init__(self, controller):
        self.controller = controller
        self.is_running = False
        self.task: asyncio.Task = None
        self.item_id = None  # Template ID of the item to use
        self.last_use_time = 0  # Timestamp of last item usage

    def start(self, item_id: int):
        """Starts the auto-item task with specified item ID."""
        if not self.is_running:
            self.item_id = item_id
            self.is_running = True
            self.last_use_time = 0  # Reset timer to use immediately
            self.task = asyncio.create_task(self.loop())
            logger.info(f"[{self.controller.account.username}] Bắt đầu Auto-Item với item ID: {item_id}")
            return self.task
        else:
            logger.warning(f"[{self.controller.account.username}] Auto-Item đã đang chạy.")
            return None

    def stop(self):
        """Stops the auto-item task."""
        if self.is_running:
            self.is_running = False
            if self.task:
                self.task.cancel()
            logger.info(f"[{self.controller.account.username}] Đã dừng Auto-Item.")
            self.item_id = None
            self.last_use_time = 0

    def get_status(self):
        """Returns current status information."""
        if self.is_running:
            current_time = time.time()
            time_since_last_use = current_time - self.last_use_time
            time_until_next_use = max(0, USE_INTERVAL - time_since_last_use)
            return {
                "running": True,
                "item_id": self.item_id,
                "next_use_seconds": int(time_until_next_use)
            }
        else:
            return {"running": False}

    async def loop(self):
        """The main loop for auto-using items every 30 minutes."""
        logger.info(f"[{self.controller.account.username}] Vòng lặp Auto-Item đang chạy...")
        
        while self.is_running:
            try:
                current_time = time.time()
                time_elapsed = current_time - self.last_use_time
                
                # Check if it's time to use the item
                if time_elapsed >= USE_INTERVAL:
                    await self.use_item()
                    self.last_use_time = current_time
                    logger.info(f"[{self.controller.account.username}] Auto-Item: Đã sử dụng item. Sẽ sử dụng lại sau {USE_INTERVAL//60} phút.")
                
                # Sleep for a short interval before checking again
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except asyncio.CancelledError:
                logger.info(f"[{self.controller.account.username}] Vòng lặp Auto-Item đã bị hủy.")
                break
            except Exception as e:
                logger.error(f"[{self.controller.account.username}] Lỗi trong vòng lặp Auto-Item: {e}")
                await asyncio.sleep(10)

    async def use_item(self):
        """Find and use the specified item from inventory."""
        char = self.controller.account.char
        service = self.controller.account.service
        
        if not self.item_id:
            logger.warning(f"[{self.controller.account.username}] Auto-Item: Không có item ID được chỉ định.")
            return
        
        # Search for the item in inventory
        inventory = char.arr_item_bag
        if not inventory:
            logger.warning(f"[{self.controller.account.username}] Auto-Item: Túi đồ trống hoặc chưa được tải.")
            return
        
        found_item = False
        item_index = -1
        
        for index, item in enumerate(inventory):
            if item and item.item_id == self.item_id:
                found_item = True
                item_index = index
                logger.info(f"[{self.controller.account.username}] Auto-Item: Tìm thấy item ID {self.item_id} tại vị trí {index}")
                break
        
        if found_item:
            # Use the item (action type 0 = use, type 1 = use on master/self)
            # Using type 1 (use on self) as it's more common for consumables
            logger.info(f"[{self.controller.account.username}] Auto-Item: Đang sử dụng item tại vị trí {item_index}...")
            await service.use_item(0, 1, item_index, -1)
            await asyncio.sleep(0.5)
        else:
            logger.warning(f"[{self.controller.account.username}] Auto-Item: Không tìm thấy item ID {self.item_id} trong túi đồ.")
