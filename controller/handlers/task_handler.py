"""
Task Handler - Xử lý các message liên quan đến nhiệm vụ
"""
from network.message import Message
from logs.logger_config import logger
from .base_handler import BaseHandler


class TaskHandler(BaseHandler):
    """Handler xử lý task get, update, next."""
    
    def process_task_get(self, msg: Message):
        """Phân tích gói TASK_GET và lưu thông tin nhiệm vụ vào nhân vật."""
        try:
            reader = msg.reader()
            task_id = reader.read_short()
            index = reader.read_byte()
            task_name = reader.read_utf()
            task_detail = reader.read_utf()
            
            sub_names = []
            len_sub = reader.read_ubyte()
            
            # Đọc loop sub-tasks info
            for _ in range(len_sub):
                sub_names.append(reader.read_utf())
                reader.read_byte()  # npcId
                reader.read_short() # mapId
                reader.read_utf()   # desc
            
            # Đọc tiến độ hiện tại
            current_count = reader.read_short()
            
            # Đọc max count cho từng bước
            counts = []
            for _ in range(len_sub):
                counts.append(reader.read_short())

            # Update Char task
            char = self.account.char
            char.task.task_id = task_id
            char.task.index = index
            char.task.name = task_name
            char.task.detail = task_detail
            char.task.sub_names = sub_names
            char.task.counts = counts
            char.task.count = current_count
            
            logger.info(f"Nhiệm vụ (Cmd {msg.command}): [{task_id}] {task_name} - Bước {index} - Progress: {current_count}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích TASK_GET: {e}")

    def process_task_update(self, msg: Message):
        """Cập nhật tiến độ nhiệm vụ (TASK_UPDATE)."""
        try:
            reader = msg.reader()
            val = reader.read_short()
            
            char = self.account.char
            
            # Gói tin ngắn chỉ chứa tiến độ
            if reader.available() == 0:
                new_count = val
                if char.task.count != new_count:
                    char.task.count = new_count
                    logger.info(f"Cập nhật nhiệm vụ chính (Ngắn): Tiến độ -> {new_count}")
                return

            # Gói tin đầy đủ
            task_id = val
            index = reader.read_byte()
            count = reader.read_short()

            if char.task.task_id == task_id:
                if char.task.index != index or char.task.count != count:
                    char.task.index = index
                    char.task.count = count
                    logger.info(f"Cập nhật NV chính: [{task_id}] Bước {index} -> {count}")
            else:
                logger.info(f"Nhận được cập nhật cho task ID {task_id} (không phải NV chính), tiến độ -> {count}")

        except Exception as e:
            logger.error(f"Lỗi khi phân tích TASK_UPDATE: {e}")

    def process_task_next(self, msg: Message):
        """Xử lý chuyển bước nhiệm vụ (TASK_NEXT - 41)."""
        try:
            char = self.account.char
            
            data = msg.get_data()
            if data and len(data) > 0:
                reader = msg.reader()
                if reader.available() > 0:
                    next_index = reader.read_byte()
                    char.task.index = next_index
                    logger.info(f"Chuyển bước nhiệm vụ (Cmd 41): Index -> {next_index}")
                else:
                    char.task.index += 1
                    logger.info(f"Chuyển bước nhiệm vụ (Cmd 41): Index +1 -> {char.task.index} (Empty Reader)")
            else:
                char.task.index += 1
                logger.info(f"Chuyển bước nhiệm vụ (Cmd 41): Index +1 -> {char.task.index} (No Data)")
            
            char.task.count = 0
        except Exception as e:
            logger.error(f"Lỗi khi xử lý TASK_NEXT: {e}")
