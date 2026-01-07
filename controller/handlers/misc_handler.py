"""
Misc Handler - Xử lý các message còn lại
"""
import re
import asyncio
from network.message import Message
from logs.logger_config import logger
from .base_handler import BaseHandler


class MiscHandler(BaseHandler):
    """Handler xử lý các messages còn lại."""
    
    def process_game_info(self, msg: Message):
        """Đọc và ghi log chuỗi thông tin do server gửi (GAME_INFO)."""
        try:
            reader = msg.reader()
            info_text = reader.read_utf()
            logger.info(f"Thông tin trò chơi (Lệnh {msg.command}): '{info_text}'")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích cú pháp GAME_INFO: {e}")

    def process_special_skill(self, msg: Message):
        """Phân tích thông tin kỹ năng đặc biệt (các kiểu khác nhau theo `special_type`)."""
        try:
            reader = msg.reader()
            special_type = reader.read_byte()
            if special_type == 0:
                img_id = reader.read_short()
                info = reader.read_utf()
                logger.info(f"Kỹ năng đặc biệt (Cmd {msg.command}): Loại={special_type}, ImgID={img_id}, Thông tin='{info}'")
            elif special_type == 1:
                logger.info(f"Kỹ năng đặc biệt (Cmd {msg.command}): Loại={special_type} (danh sách), Payload Hex: {msg.get_data().hex()}")
            else:
                logger.info(f"Kỹ năng đặc biệt (Cmd {msg.command}): Loại không xác định={special_type}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích SPEACIAL_SKILL: {e}")

    def process_message_time(self, msg: Message):
        """Đọc thông báo thời gian (MESSAGE_TIME) và ghi log nội dung cùng thời hạn."""
        try:
            reader = msg.reader()
            time_id = reader.read_byte()
            message = reader.read_utf()
            duration = reader.read_short()
            logger.info(f"Thông báo thời gian (Cmd {msg.command}): ID={time_id}, Thông báo='{message}', Thời hạn={duration}s")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích MESSAGE_TIME: {e}")

    def process_change_flag(self, msg: Message):
        """Xử lý thay đổi cờ trạng thái của nhân vật (CHANGE_FLAG)."""
        try:
            reader = msg.reader()
            char_id = reader.read_int()
            flag_id = 0
            if reader.available() > 0:
                flag_id = reader.read_byte()
            logger.info(f"Thay đổi cờ (Lệnh {msg.command}): CharID={char_id}, FlagID={flag_id}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích CHANGE_FLAG: {e}")

    def process_max_stamina(self, msg: Message):
        """Cập nhật giá trị thể lực tối đa của người chơi (MAXSTAMINA)."""
        try:
            reader = msg.reader()
            max_stamina = reader.read_short()
            logger.info(f"Thể lực tối đa (Cmd {msg.command}): {max_stamina}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích MAXSTAMINA: {e}")

    def process_stamina(self, msg: Message):
        """Cập nhật thể lực hiện tại (STAMINA)."""
        try:
            reader = msg.reader()
            stamina = reader.read_short()
            logger.info(f"Thể lực hiện tại (Cmd {msg.command}): {stamina}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích STAMINA: {e}")

    def process_update_active_point(self, msg: Message):
        """Cập nhật điểm hoạt động/năng động của người chơi (UPDATE_ACTIVEPOINT)."""
        try:
            reader = msg.reader()
            active_point = reader.read_int()
            logger.info(f"Cập nhật điểm năng động (Cmd {msg.command}): {active_point}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích UPDATE_ACTIVEPOINT: {e}")

    def process_thach_dau(self, msg: Message):
        """Xử lý thông tin thách đấu (THACHDAU) từ server."""
        try:
            reader = msg.reader()
            challenge_id = reader.read_int()
            logger.info(f"Thách đấu (Cmd {msg.command}): ChallengeID={challenge_id}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích THACHDAU: {e}")

    def process_autoplay(self, msg: Message):
        """Nhận trạng thái hoặc cấu hình chế độ tự động từ server (AUTOPLAY)."""
        try:
            reader = msg.reader()
            auto_mode = reader.read_byte()
            logger.info(f"Tự động chơi (Cmd {msg.command}): Chế độ={auto_mode}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích AUTOPLAY: {e}")

    def process_mabu(self, msg: Message):
        """Xử lý gói tin liên quan đến Mabu và ghi lại trạng thái (MABU)."""
        try:
            reader = msg.reader()
            mabu_state = reader.read_byte()
            logger.info(f"Mabu (Cmd {msg.command}): Trạng thái={mabu_state}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích MABU: {e}")

    def process_the_luc(self, msg: Message):
        """Xử lý thông tin thể lực (THELUC) nhận từ server."""
        try:
            reader = msg.reader()
            the_luc_value = reader.read_short()
            logger.info(f"Thể lực (Cmd {msg.command}): Giá trị={the_luc_value}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích THELUC: {e}")

    def process_create_player(self, msg: Message):
        """Xử lý yêu cầu tạo nhân vật từ server (Cmd 2)."""
        try:
            logger.info("Server yêu cầu tạo nhân vật mới (Cmd 2).")
            
            clean_username = re.sub(r'[^a-zA-Z0-9]', '', self.account.username)
            suffix = clean_username[-3:] if len(clean_username) >= 3 else clean_username
            clean_name = f"hentaz{suffix}"

            from config import Config
            gender = Config.DEFAULT_CHAR_GENDER
            hair = Config.DEFAULT_CHAR_HAIR
            
            logger.info(f"Tự động tạo nhân vật: Name={clean_name}, Gender={gender}, Hair={hair}")
            asyncio.create_task(self.account.service.create_character(clean_name, gender, hair))
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý tạo nhân vật: {e}")
            import traceback
            traceback.print_exc()

    async def attack_nearest_mob(self):
        """Tấn công quái vật gần nhất một lần."""
        char = self.account.char
        mobs = self.controller.mobs
        if not mobs:
            logger.warning(f"[{self.account.username}] Không có quái vật nào trong khu vực.")
            return

        closest_mob = None
        min_dist = float('inf')

        for mob in mobs.values():
            if mob.status == 0 or mob.hp <= 0:
                continue
            
            dist = (char.cx - mob.x)**2 + (char.cy - mob.y)**2
            if dist < min_dist:
                min_dist = dist
                closest_mob = mob

        if closest_mob:
            logger.info(f"[{self.account.username}] Tấn công quái ID {closest_mob.mob_id} (Khoảng cách: {int(min_dist**0.5)})")
            cdir = 1 if closest_mob.x > char.cx else -1
            await self.account.service.send_player_attack([closest_mob.mob_id], cdir)
        else:
            logger.warning(f"[{self.account.username}] Không tìm thấy quái vật nào còn sống.")

    async def auto_upgrade_stats(self, target_hp: int, target_mp: int, target_sd: int):
        """Tự động cộng chỉ số tiềm năng cho đến khi đạt mục tiêu."""
        char = self.account.char
        logger.info(f"[{self.account.username}] Bắt đầu cộng chỉ số. Mục tiêu -> HP: {target_hp}, MP: {target_mp}, SD: {target_sd}")
        
        while True:
            acted = False
            
            if char.c_hp_goc <= target_hp - 2000:
                await self.account.service.up_potential(0, 100)
                acted = True
            elif char.c_hp_goc <= target_hp - 200:
                await self.account.service.up_potential(0, 10)
                acted = True
            elif char.c_hp_goc <= target_hp - 20:
                await self.account.service.up_potential(0, 1)
                acted = True
                
            if char.c_mp_goc <= target_mp - 2000:
                await self.account.service.up_potential(1, 100)
                acted = True
            elif char.c_mp_goc <= target_mp - 200:
                await self.account.service.up_potential(1, 10)
                acted = True
            elif char.c_mp_goc <= target_mp - 20:
                await self.account.service.up_potential(1, 1)
                acted = True

            if char.c_dam_goc <= target_sd - 100:
                await self.account.service.up_potential(2, 100)
                acted = True
            elif char.c_dam_goc <= target_sd - 10:
                await self.account.service.up_potential(2, 10)
                acted = True
            elif char.c_dam_goc <= target_sd - 1:
                await self.account.service.up_potential(2, 1)
                acted = True
            
            if not acted:
                logger.info(f"[{self.account.username}] Hoàn tất cộng chỉ số hoặc đã hết tiềm năng.")
                break
            
            await asyncio.sleep(0.05)
