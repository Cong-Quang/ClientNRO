from logs.logger_config import logger 
from network.writer import Writer
from network.message import Message
from network.session import Session
from model.game_objects import Char
from cmd import Cmd

# logger = logging.getLogger(__name__)

class Service:
    def __init__(self, session: Session, char_data: Char):
        self.session = session
        self.char_data = char_data

    async def pet_info(self):
        """Yêu cầu thông tin đệ tử (Cmd -107)"""
        try:
            msg = Message(Cmd.PET_INFO)
            await self.session.send_message(msg)
            logger.info("Đã gửi yêu cầu thông tin đệ tử (PET_INFO)")
        except Exception as e:
            logger.error(f"Lỗi khi gửi yêu cầu pet_info: {e}")

    async def pet_status(self, status: int):
        """Thay đổi trạng thái đệ tử (Cmd -108)
        0: Đi theo, 1: Bảo vệ, 2: Tấn công, 3: Về nhà, 4: Hợp thể, 5: Hợp thể vĩnh viễn
        """
        try:
            msg = Message(Cmd.PET_STATUS)
            msg.writer().write_byte(status)
            await self.session.send_message(msg)
            logger.info(f"Đã gửi yêu cầu thay đổi trạng thái đệ tử: {status}")
        except Exception as e:
            logger.error(f"Lỗi khi gửi yêu cầu pet_status: {e}")

    async def char_move(self):
        # Mã lệnh (CMD): -7
        my_char = self.char_data
        
        # Tính toán độ chênh lệch (delta)
        num = my_char.cx - my_char.cxSend
        num2 = my_char.cy - my_char.cySend
        
        # Nếu không có thay đổi thì thoát (theo logic nghiêm ngặt của C#)
        if num == 0 and num2 == 0:
            return

        # Cập nhật trạng thái tọa độ đã gửi
        my_char.cxSend = my_char.cx
        my_char.cySend = my_char.cy
        
        msg = Message(-7)
        writer = msg.writer()
        
        # Loại 1 (Bay) - giả định trong ngữ cảnh bay hoặc dịch chuyển
        writer.write_byte(1) 
        
        # Luôn luôn ghi tọa độ X
        writer.write_short(my_char.cx)
        
        # CHỈ ghi tọa độ Y nếu có sự thay đổi
        if num2 != 0:
            writer.write_short(my_char.cy)
            
        await self.session.send_message(msg)
        logger.warning(f"Dịch chuyển tới ({my_char.cx}, {my_char.cy}) [Loại=1, Send Y={num2!=0}]")

    async def request_change_map(self):
        # Mã lệnh (CMD): -23 (ĐỔI_BẢN_ĐỒ)
        msg = Message(-23)
        await self.session.send_message(msg)
        logger.info("Gửi yêu cầu đổi bản đồ (Cmd -23)")

    async def get_map_offline(self):
        # Mã lệnh (CMD): -33 (BẢN_ĐỒ_NGOẠI_TUYẾN)
        msg = Message(-33)
        await self.session.send_message(msg)
        logger.info("Gửi yêu cầu tải bản đồ ngoại tuyến (Cmd -33)")

    async def send_player_attack(self, mob_ids: list[int], cdir: int = 1):
        # Mã lệnh (CMD): 54 (TẤN_CÔNG)
        msg = Message(54)
        writer = msg.writer()
        
        for mob_id in mob_ids:
            writer.write_byte(mob_id)
            
        writer.write_byte(cdir)
        await self.session.send_message(msg)

    async def select_skill(self, skill_template_id: int):
        # Mã lệnh (CMD): 34 (CHỌN_KỸ_NĂNG)
        msg = Message(34)
        writer = msg.writer()
        writer.write_short(skill_template_id)
        await self.session.send_message(msg)
        # logger.debug(f"Đã chọn mẫu kỹ năng: {skill_template_id}")
        
    async def request_change_zone(self, zone_id: int, index_ui: int = 0):
        """
        Gửi yêu cầu đổi khu vực (Zone)
        Mã lệnh (CMD): 21
        """
        msg = Message(21)
        writer = msg.writer()
        try:
            # Ghi mã khu vực vào gói tin
            writer.write_byte(zone_id)
            
            # Gửi gói tin đi
            await self.session.send_message(msg)
            logger.info(f"Đã gửi yêu cầu đổi sang Khu vực: {zone_id}")
            
        except Exception as e:
            logger.error(f"Lỗi khi gửi yêu cầu đổi khu vực: {e}")

    async def use_item(self, type: int, where: int, index: int, template_id: int):
        """
        Sử dụng một vật phẩm. (Cmd -43)
        :param type: 0: sử dụng từ túi đồ, 1: đeo vào, ...
        :param where: 1: sử dụng cho bản thân, ...
        :param index: vị trí trong túi đồ (-1 nếu dùng template_id)
        :param template_id: ID mẫu của vật phẩm
        """
        if self.char_data.statusMe == 14: # Nếu đang trong trạng thái không thể hành động
            return
            
        logger.info(f"Sử dụng vật phẩm: type={type} where={where} index={index} template_id={template_id}")
        try:
            msg = Message(Cmd.USE_ITEM)
            writer = msg.writer()
            writer.write_byte(type)
            writer.write_byte(where)
            writer.write_byte(index)
            if index == -1:
                writer.write_short(template_id)
            await self.session.send_message(msg)
        except Exception as e:
            logger.error(f"Lỗi khi gửi yêu cầu sử dụng vật phẩm: {e}")

    async def get_item(self, type: int, index: int):
        """
        Lấy hoặc sử dụng một vật phẩm trên đối tượng khác (VD: đệ tử). (Cmd -40)
        :param type: 6: Dùng vật phẩm trong túi đồ cho đệ tử (BAG_PET)
        :param index: Vị trí của vật phẩm trong túi đồ
        """
        logger.info(f"Yêu cầu vật phẩm: type={type} index={index}")
        try:
            msg = Message(Cmd.GET_ITEM)
            writer = msg.writer()
            writer.write_byte(type)
            writer.write_byte(index)
            await self.session.send_message(msg)
        except Exception as e:
            logger.error(f"Lỗi khi gửi yêu cầu get_item: {e}")

    