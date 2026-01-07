"""
Combat Handler - Xử lý các message liên quan đến chiến đấu
"""
from network.message import Message
from logs.logger_config import logger
from .base_handler import BaseHandler


class CombatHandler(BaseHandler):
    """Handler xử lý mob HP, death, respawn, attacks."""
    
    def process_mob_hp(self, msg: Message):
        """Cập nhật HP của mob (MOB_HP), xử lý các dữ liệu bổ sung nếu có."""
        try:
            reader = msg.reader()
            mob_id = reader.read_ubyte() 
            current_hp = reader.read_int3() 
            damage = reader.read_int3() 
            
            if reader.available() > 0:
                try:
                    reader.read_bool()
                    reader.read_byte()
                except: pass

            mob = self.controller.mobs.get(mob_id)
            if mob:
                old_hp = mob.hp
                mob.hp = current_hp
                logger.info(f"Cập nhật quái vật: ID={mob_id} | HP: {old_hp} -> {current_hp}/{mob.max_hp} (ST: {damage})")
            else:
                logger.warning(f"Đã nhận MOB_HP cho MobID không xác định={mob_id}. HP={current_hp}")
                
        except Exception as e:
            logger.error(f"Lỗi khi phân tích MOB_HP: {e}")

    def process_npc_die(self, msg: Message):
        """Xử lý sự kiện mob chết (NPC_DIE) và cập nhật trạng thái trong `self.mobs`."""
        try:
            reader = msg.reader()
            mob_id = reader.read_ubyte()
            damage = reader.read_int3()
            
            mob = self.controller.mobs.get(mob_id)
            if mob:
                mob.hp = 0
                mob.status = 0
                logger.info(f"Quái vật đã CHẾT: ID={mob_id} (ST: {damage})")
                
                # Báo cho auto quest biết có quái chết
                self.controller.auto_quest.increment_kill_count(mob.template_id)

                if self.account.char.mob_focus == mob:
                    self.account.char.mob_focus = None
            else:
                logger.warning(f"Đã nhận NPC_DIE cho MobID không xác định={mob_id}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích NPC_DIE: {e}")

    def process_npc_live(self, msg: Message):
        """Xử lý NPC_LIVE: cập nhật HP và trạng thái khi quái vật hồi sinh."""
        try:
            reader = msg.reader()
            mob_id = reader.read_ubyte()
            if mob_id not in self.controller.mobs:
                logger.warning(f"NPC_LIVE: unknown mob id {mob_id}")
                return

            mob = self.controller.mobs[mob_id]
            
            mob.sys = reader.read_byte()
            mob.level_boss = reader.read_byte()
            mob.hp = reader.read_int()
            mob.status = 5
            mob.max_hp = mob.hp
            mob.x = mob.x_first
            mob.y = mob.y_first
            
            logger.info(f"Quái vật HỒI SINH: ID={mob_id} | HP={mob.hp} | Vị trí=({mob.x},{mob.y})")
            
        except Exception as e:
            logger.error(f"Lỗi khi phân tích NPC_LIVE: {e}")
            import traceback
            traceback.print_exc()

    def process_player_attack_npc(self, msg: Message):
        """Xử lý sự kiện người chơi tấn công NPC (PLAYER_ATTACK_NPC)."""
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            npc_id = reader.read_byte()
            logger.info(f"Người chơi tấn công NPC (Cmd {msg.command}): PlayerID={player_id}, NPC_ID={npc_id}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_ATTACK_NPC: {e}")
