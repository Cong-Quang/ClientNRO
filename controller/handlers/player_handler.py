"""
Player Handler - Xử lý các message liên quan đến người chơi khác
"""
import asyncio
from network.message import Message
from network.reader import Reader
from logs.logger_config import logger
from .base_handler import BaseHandler


class PlayerHandler(BaseHandler):
    """Handler xử lý player add, move, die, list updates."""
    
    def process_player_add(self, msg: Message):
        """Đọc thông tin khi có player mới xuất hiện trên map và ghi log cơ bản."""
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            clan_id = reader.read_int()
            
            char_data = self.read_char_info(reader)
            char_data['id'] = player_id
            char_data['clan_id'] = clan_id
            
            # Lưu vào chars dict (cho boss detection)
            self.controller.chars[player_id] = char_data
            
            logger.info(f"Đã thêm người chơi (Cmd {msg.command}): ID={player_id}, Tên='{char_data.get('name')}', Vị trí=({char_data.get('x')},{char_data.get('y')})")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_ADD: {e}")

    def read_char_info(self, reader: Reader) -> dict:
        """Đọc thông tin cơ bản của một nhân vật từ `reader` và trả về dict chứa giá trị như level, tên, vị trí, hiệu ứng."""
        c = {}
        c['level'] = reader.read_byte()
        c['is_invisible'] = reader.read_bool()
        c['type_pk'] = reader.read_byte()
        c['class'] = reader.read_byte()
        c['gender'] = reader.read_byte()
        c['head'] = reader.read_short()
        c['name'] = reader.read_utf()
        c['hp'] = reader.read_int3() 
        c['max_hp'] = reader.read_int3() 
        c['body'] = reader.read_short()
        c['leg'] = reader.read_short()
        c['bag'] = reader.read_ubyte()
        reader.read_byte()
        c['x'] = reader.read_short()
        c['y'] = reader.read_short()
        c['eff_buff_hp'] = reader.read_short()
        c['eff_buff_mp'] = reader.read_short()
        
        num_eff = reader.read_byte()
        effects = []
        for _ in range(num_eff):
            eff_id = reader.read_byte()
            p1 = reader.read_int()
            p2 = reader.read_int()
            p3 = reader.read_short()
            effects.append({'id': eff_id, 'p1': p1, 'p2': p2, 'p3': p3})
        c['effects'] = effects
        
        return c

    def process_player_move(self, msg: Message):
        """Cập nhật vị trí khi server gửi thông tin di chuyển của một người chơi."""
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            x = reader.read_short()
            y = reader.read_short()
            logger.info(f"Người chơi di chuyển (Cmd {msg.command}): ID={player_id}, X={x}, Y={y}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_MOVE: {e}")

    def process_player_die(self, msg: Message):
        """Xử lý khi một người chơi chết; nếu là nhân vật local thì thực hiện bước revive/return flow."""
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            
            if player_id == self.account.char.char_id:
                logger.warning("Nhân vật của bạn đã chết (PLAYER_DIE).")
                
                was_auto_playing = self.controller.auto_play.interval
                was_auto_pet = self.controller.auto_pet.is_running
                current_map_id = self.controller.tile_map.map_id
                
                self.controller.xmap.handle_death()
                
                if was_auto_playing or was_auto_pet:
                    asyncio.create_task(self._handle_revive_and_return(current_map_id, was_auto_playing, was_auto_pet))
                else:
                    asyncio.create_task(self.account.service.return_town_from_dead())

            logger.info(f"Người chơi đã chết (Cmd {msg.command}): PlayerID={player_id}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_DIE: {e}")

    async def _handle_revive_and_return(self, target_map_id: int, resume_auto_play: bool, resume_auto_pet: bool):
        """Xử lý hồi sinh, đợi về nhà, quay lại map cũ (khu ngẫu nhiên) và tiếp tục auto."""
        logger.info(f"Đang thực hiện quy trình Hồi sinh -> Quay lại Map {target_map_id}...")
        
        await asyncio.sleep(1)
        await self.account.service.return_town_from_dead()

        timeout = 20
        start_wait = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_wait < timeout:
            if self.controller.tile_map.map_id != target_map_id and self.account.char.c_hp > 0:
                logger.info("Đã hồi sinh và về nhà thành công.")
                break
            await asyncio.sleep(1)
        
        if self.controller.tile_map.map_id == target_map_id:
            logger.warning("Không thể về nhà sau khi chết. Hủy quy trình quay lại.")
            return

        # Quay lại map mục tiêu và cố gắng khôi phục auto
        await asyncio.sleep(2)
        await self.controller.xmap.start(target_map_id, keep_dangerous=True)
        while self.controller.xmap.is_xmapping:
            await asyncio.sleep(1)
        if self.controller.tile_map.map_id == target_map_id:
            logger.info("Đã quay lại điểm cũ. Kích hoạt lại Auto...")
            if resume_auto_play:
                self.controller.toggle_autoplay(True)
            if resume_auto_pet:
                self.controller.toggle_auto_pet(True)
        else:
            logger.warning(f"Không thể quay lại map {target_map_id}.")

    def process_player_list_update(self, msg: Message):
        """Xử lý phản hồi REQUEST_PLAYERS (Cmd 18) - cập nhật vị trí và HP người chơi."""
        try:
            reader = msg.reader()
            num_players = reader.read_byte()
            logger.info(f"Processing player list update (Cmd 18): {num_players} players")
            
            for i in range(num_players):
                char_id = reader.read_int()
                cx = reader.read_short()
                cy = reader.read_short()
                hp_show = reader.read_long()
                
                # Cập nhật người chơi hiện có
                if char_id in self.controller.chars:
                    self.controller.chars[char_id]['x'] = cx
                    self.controller.chars[char_id]['y'] = cy
                    self.controller.chars[char_id]['hp'] = hp_show
                    logger.debug(f"Updated player {char_id} ({self.controller.chars[char_id].get('name')}): pos=({cx},{cy}), HP={hp_show}")
                else:
                    logger.warning(f"Player {char_id} in list but not in chars dict (pos={cx},{cy}, HP={hp_show})")
                    
        except Exception as e:
            logger.error(f"Lỗi khi phân tích REQUEST_PLAYERS response: {e}")
            import traceback
            traceback.print_exc()
