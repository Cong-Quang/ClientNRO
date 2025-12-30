import logging
from network.writer import Writer
from network.message import Message
from network.session import Session
from model.game_objects import Char

logger = logging.getLogger(__name__)

class Service:
    _instance = None
    
    def __init__(self, session: Session):
        self.session = session

    @classmethod
    def gI(cls):
        return cls._instance

    @classmethod
    def setup(cls, session: Session):
        cls._instance = Service(session)

    async def char_move(self):
        # CMD: -7
        my_char = Char.my_charz()
        
        # Calculate delta
        num = my_char.cx - my_char.cxSend
        num2 = my_char.cy - my_char.cySend
        
        # If no change, return (unless forcing, but strict C# logic returns)
        if num == 0 and num2 == 0:
            return

        # Update sent state
        my_char.cxSend = my_char.cx
        my_char.cySend = my_char.cy
        
        msg = Message(-7)
        writer = msg.writer()
        
        # Type 1 (Fly) - assuming air/teleport context
        writer.write_byte(1) 
        
        # Always write X
        writer.write_short(my_char.cx)
        
        # Write Y ONLY if changed
        if num2 != 0:
            writer.write_short(my_char.cy)
            
        await self.session.send_message(msg)
        logger.warning(f"Sent move to ({my_char.cx}, {my_char.cy}) [Type=1, SendY={num2!=0}]")

    async def request_change_map(self):
        # CMD: -23 (MAP_CHANGE)
        msg = Message(-23)
        await self.session.send_message(msg)
        logger.info("Sent Request Change Map (Cmd -23)")

    async def get_map_offline(self):
        # CMD: -33 (MAP_OFFLINE)
        msg = Message(-33)
        await self.session.send_message(msg)
        logger.info("Sent Get Map Offline (Cmd -33)")

    async def send_player_attack(self, mob_ids: list[int], cdir: int = 1):
        # CMD: 54 (Attack Mob)
        # Structure based on Service.cs:
        # Loop mobs:
        #   if standard mob: write_byte(mob_id)
        #   if mob_me: write_byte(-1), write_int(mob_id) (Not supported yet)
        # write_byte(cdir)
        
        msg = Message(54)
        writer = msg.writer()
        
        for mob_id in mob_ids:
            writer.write_byte(mob_id)
            
        writer.write_byte(cdir)
        await self.session.send_message(msg)

    async def select_skill(self, skill_template_id: int):
        # CMD: 34 (SKILL_SELECT)
        msg = Message(34)
        writer = msg.writer()
        writer.write_short(skill_template_id)
        await self.session.send_message(msg)
        # logger.debug(f"Selected Skill Template: {skill_template_id}")
        
    async def request_change_zone(self, zone_id: int, index_ui: int = 0):
        """
        Gửi yêu cầu đổi khu vực (Zone)
        CMD: 21
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
