"""
Notification Handler - Xử lý các message thông báo và boss notifications
"""
from network.message import Message
from logs.logger_config import logger
from .base_handler import BaseHandler


class NotificationHandler(BaseHandler):
    """Handler xử lý server messages, chat, boss notifications."""
    
    def process_server_message(self, msg: Message):
        """Xử lý thông báo từ server (Cmd -25)."""
        try:
            reader = msg.reader()
            text = reader.read_utf()
            logger.info(f"SERVER MESSAGE: {text}")
            self.check_boss_notification(text, source="SERVER_MESSAGE")
        except Exception as e:
            logger.error(f"Error parsing SERVER_MESSAGE: {e}")

    def process_chat_server(self, msg: Message):
        """Xử lý chat thế giới từ server (Cmd 92)."""
        try:
            reader = msg.reader()
            text = reader.read_utf()
            self.check_boss_notification(text, source="CHAT_SERVER")
        except Exception as e:
            logger.error(f"Error parsing CHAT_THEGIOI_SERVER: {e}")

    def process_chat_map(self, msg: Message):
        """Xử lý chat trong map (Cmd 44)."""
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            text = reader.read_utf()
            self.check_boss_notification(text, source="CHAT_MAP")
        except Exception as e:
            logger.error(f"Error parsing CHAT_MAP: {e}")

    def process_server_alert(self, msg: Message):
        """Xử lý thông báo server (Cmd 94)."""
        try:
            reader = msg.reader()
            text = reader.read_utf()
            logger.info(f"SERVER ALERT: {text}")
            self.check_boss_notification(text, source="SERVER_ALERT")
        except Exception as e:
            logger.error(f"Error parsing SERVER_ALERT: {e}")

    def process_chat_vip(self, msg: Message):
        """Xử lý chat VIP (Cmd 93) - Kênh chính thông báo Boss."""
        try:
            reader = msg.reader()
            text = reader.read_utf()
            self.check_boss_notification(text, source="CHAT_VIP")
        except Exception as e:
            logger.error(f"Error parsing CHAT_VIP: {e}")

    def process_big_message(self, msg: Message):
        """Xử lý thông báo lớn (Cmd -70)."""
        try:
            reader = msg.reader()
            text = reader.read_utf()
            self.check_boss_notification(text, source="BIG_MESSAGE")
        except Exception as e:
            logger.error(f"Error parsing BIG_MESSAGE: {e}")

    def process_big_boss(self, msg: Message, type: int):
        """Xử lý thông tin Big Boss (Cmd 101, 102)."""
        try:
            logger.info(f"BIG_BOSS type {type} received. Len: {len(msg.get_data())}")
        except Exception as e:
            logger.error(f"Error parsing BIG_BOSS: {e}")

    def check_boss_notification(self, text: str, source: str = "UNKNOWN"):
        """
        Kiểm tra nội dung chat xem có phải thông báo boss xuất hiện không.
        """
        if "xuất hiện tại" in text:
            try:
                from logic.boss_manager import BossManager
                
                # Normalize text
                clean_text = text.replace("Boss ", "").replace("boss ", "").replace("BOSS ", "") 
                
                # Handle different phrases
                if " vừa xuất hiện tại " in clean_text:
                    splitter = " vừa xuất hiện tại "
                elif " đã xuất hiện tại " in clean_text:
                    splitter = " đã xuất hiện tại "
                else:
                    splitter = " xuất hiện tại "
                
                parts = clean_text.split(splitter)
                if len(parts) >= 2:
                    boss_name = parts[0].strip()
                    location_part = parts[1]
                    
                    # Tách khu vực nếu có
                    map_name = location_part.strip()
                    zone_id = -1
                    
                    if "khu vực" in location_part:
                        loc_parts = location_part.split(" khu vực ")
                        map_name = loc_parts[0].strip()
                        if len(loc_parts) > 1:
                            try:
                                zone_id = int(loc_parts[1].strip())
                            except:
                                pass

                    BossManager().add_boss(boss_name, map_name, zone_id)
                    logger.info(f"PHÁT HIỆN BOSS: {boss_name} tại {map_name} (Khu {zone_id})")
            
            except Exception as e:
                logger.error(f"Lỗi khi phân tích thông báo Boss: {e}")

        # Check death message
        if "vừa tiêu diệt được" in text:
            try:
                from logic.boss_manager import BossManager
                parts = text.split(" vừa tiêu diệt được ")
                if len(parts) >= 2:
                    remainder = parts[1]
                    boss_name = remainder.split(" mọi người")[0].strip()
                    
                    if BossManager().mark_boss_dead(boss_name):
                         logger.info(f"BOSS DIED: {boss_name}")
            except Exception as e:
                logger.error(f"Lỗi khi xử lý boss chết: {e}")
