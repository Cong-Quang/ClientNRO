"""
Character Handler - Xử lý các message liên quan đến thông tin nhân vật
"""
from network.message import Message
from logs.logger_config import logger
from .base_handler import BaseHandler


class CharacterHandler(BaseHandler):
    """Handler xử lý character stats, power, exp updates."""
    
    def process_me_load_point(self, msg: Message):
        """Đọc thông tin chỉ số nhân vật khi vào map hoặc load point và cập nhật thuộc tính `char`."""
        try:
            reader = msg.reader()
            char = self.account.char
            
            char.c_hp_goc = reader.read_int()
            char.c_mp_goc = reader.read_int()
            char.c_dam_goc = reader.read_int()
            char.c_hp_full = reader.read_int()
            char.c_mp_full = reader.read_int()
            char.c_hp = reader.read_int()
            char.c_mp = reader.read_int()
            
            char.cspeed = reader.read_byte()
            char.hp_from_1000 = reader.read_byte()
            char.mp_from_1000 = reader.read_byte()
            char.dam_from_1000 = reader.read_byte()
            
            char.c_dam_full = reader.read_int()
            char.c_def_full = reader.read_int()
            char.c_critical_full = reader.read_byte()
            char.c_tiem_nang = reader.read_long()

            if reader.available() >= 2:
                char.exp_for_one_add = reader.read_short()
            if reader.available() >= 2:
                char.c_def_goc = reader.read_short()
            if reader.available() >= 1:
                char.c_critical_goc = reader.read_byte()
            
            # Check for remaining data (Potential "Power Info Extra")
            if reader.available() > 0:
                remaining = reader.read_remaining()
                logger.info(f"Dữ liệu còn lại trong ME_LOAD_POINT (Power Info Extra?): {remaining.hex()}")

            if char.c_hp == 0:
                self.controller.xmap.handle_death()

            logger.info(f"Chỉ số nhân vật (Cmd {msg.command}): HP={char.c_hp}/{char.c_hp_full}, MP={char.c_mp}/{char.c_mp_full}, Tiềm năng={char.c_tiem_nang}, Sát thương={char.c_dam_full}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích ME_LOAD_POINT: {e}")

    def process_sub_command(self, msg: Message):
        """Xử lý SUB_COMMAND với nhiều trường hợp con (tải thông tin nhân vật, cập nhật HP/MP, tài sản, items)."""
        try:
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            char = self.account.char

            if sub_cmd == 0:
                # ME_LOAD_ALL - Load full character info
                char.char_id = reader.read_int()
                char.ctask_id = reader.read_byte()
                char.gender = reader.read_byte()
                char.head = reader.read_short()
                char.name = reader.read_utf()
                char.c_pk = reader.read_byte()
                char.c_type_pk = reader.read_byte()
                char.c_power = reader.read_long()
                
                char.eff5BuffHp = reader.read_short()
                char.eff5BuffMp = reader.read_short()
                
                nClass_id = reader.read_byte() 
                
                num_skills = reader.read_byte()
                for _ in range(num_skills):
                    reader.read_short()
                
                char.xu = reader.read_long()
                char.luong_khoa = reader.read_int()
                char.luong = reader.read_int()

                # Read body items
                try:
                    num_body_items = reader.read_byte()
                    for _ in range(num_body_items):
                        if reader.available() < 2: break
                        template_id = reader.read_short()
                        if template_id != -1:
                            if reader.available() < 4: break
                            reader.read_int() # quantity
                            if reader.available() < 1: break
                            reader.read_utf() # info
                            reader.read_utf() # content
                            if reader.available() < 1: break
                            num_options = reader.read_ubyte()
                            for _ in range(num_options):
                                if reader.available() < 3: break
                                reader.read_byte() # opt id
                                reader.read_short() # opt param
                except Exception as e:
                    logger.error(f"Lỗi khi phân tích Body Items: {e}")

                # Read bag items
                try:
                    if reader.available() < 1: return
                    num_bag_items = reader.read_byte()
                    for _ in range(num_bag_items):
                        if reader.available() < 2: break
                        template_id = reader.read_short()
                        if template_id != -1:
                            if reader.available() < 4: break
                            reader.read_int()
                            if reader.available() < 1: break
                            reader.read_utf()
                            reader.read_utf()
                            if reader.available() < 1: break
                            num_options = reader.read_ubyte()
                            for _ in range(num_options):
                                if reader.available() < 3: break
                                reader.read_byte()
                                reader.read_short()
                except Exception as e:
                    logger.error(f"Lỗi khi phân tích Bag Items: {e}")
                
                # Read box items
                try:
                    if reader.available() < 1: return
                    num_box_items = reader.read_byte()
                    for _ in range(num_box_items):
                        if reader.available() < 2: break
                        template_id = reader.read_short()
                        if template_id != -1:
                            if reader.available() < 4: break
                            reader.read_int()
                            if reader.available() < 1: break
                            reader.read_utf()
                            reader.read_utf()
                            if reader.available() < 1: break
                            num_options = reader.read_ubyte()
                            for _ in range(num_options):
                                if reader.available() < 3: break
                                reader.read_byte()
                                reader.read_short()
                except Exception as e:
                    logger.error(f"Lỗi khi phân tích Box Items: {e}")

                # Check for remaining data
                if reader.available() > 0:
                    remaining_data = reader.read_remaining()
                    logger.info(f"Dữ liệu còn lại trong ME_LOAD_ALL (Info khác?): {remaining_data.hex()}")

                logger.info(f"Đã xử lý đầy đủ ME_LOAD_ALL: Tên={char.name}, SM={char.c_power}, Vàng={char.xu}")
                
                # Signal that login is fully complete
                if not self.account.login_event.is_set():
                    self.account.login_event.set()

            elif sub_cmd == 4:
                char.xu = reader.read_long()
                char.luong = reader.read_int()
                char.c_hp = reader.read_int()
                char.c_mp = reader.read_int()
                char.luong_khoa = reader.read_int()
                logger.info(f"Cập nhật tài sản: Vàng={char.xu}, Ngọc={char.luong}, HP={char.c_hp}, MP={char.c_mp}")

            elif sub_cmd == 5:
                old_hp = char.c_hp
                char.c_hp = reader.read_int()
                logger.info(f"Cập nhật HP: {old_hp} -> {char.c_hp}")

            elif sub_cmd == 6:
                old_mp = char.c_mp
                char.c_mp = reader.read_int()
                logger.info(f"Cập nhật MP: {old_mp} -> {char.c_mp}")

            elif sub_cmd == 61:
                if reader.available() > 0:
                    remaining = reader.read_remaining()
                    logger.info(f"SUB_COMMAND (Lệnh {msg.command}) sub_cmd 61: Payload Hex: {remaining.hex()}")
                else:
                    logger.info(f"SUB_COMMAND (Lệnh {msg.command}) sub_cmd 61 (empty)")

            elif sub_cmd == 14:
                if reader.available() > 0:
                    remaining = reader.read_remaining()
                    logger.info(f"SUB_COMMAND (Lệnh {msg.command}) sub_cmd 14: Payload Hex: {remaining.hex()}")
                else:
                    logger.info(f"SUB_COMMAND (Lệnh {msg.command}) sub_cmd 14 (empty)")

            else:
                logger.info(f"SUB_COMMAND (Lệnh {msg.command}) lệnh phụ chưa xử lý: {sub_cmd}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích SUB_COMMAND: {e}")
            import traceback
            traceback.print_exc()

    def process_power_info(self, msg: Message):
        """Xử lý thông tin sức mạnh (POWER_INFO -115)."""
        try:
            reader = msg.reader()
            power = reader.read_long()
            self.account.char.c_power = power
            logger.info(f"Cập nhật Sức Mạnh (Cmd {msg.command}): {power}")
            
            if reader.available() > 0:
                pass
        except Exception as e:
            logger.error(f"Lỗi khi phân tích POWER_INFO: {e}")

    def process_player_up_exp(self, msg: Message):
        """Xử lý cập nhật EXP/Sức mạnh theo loại gói tin PLAYER_UP_EXP."""
        try:
            reader = msg.reader()
            exp_type = reader.read_byte()
            amount = reader.read_int()
            
            char = self.account.char
            if exp_type == 0:
                char.c_power += amount
            elif exp_type == 1:
                char.c_tiem_nang += amount
            elif exp_type == 2:
                char.c_power += amount
                char.c_tiem_nang += amount
            
            logger.info(f"Người chơi tăng EXP (Cmd {msg.command}): Loại={exp_type}, Số lượng={amount}. SM Hiện tại: {char.c_power}, TN: {char.c_tiem_nang}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_UP_EXP: {e}")
