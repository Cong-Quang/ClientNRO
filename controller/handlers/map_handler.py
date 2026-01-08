"""
Map Handler - Xử lý các message liên quan đến bản đồ
"""
import asyncio
from network.message import Message
from logs.logger_config import logger
from model.map_objects import Waypoint
from .base_handler import BaseHandler
import ui


class MapHandler(BaseHandler):
    """Handler xử lý map info, zones, updates."""
    
    def process_map_info(self, msg: Message):
        """Đọc MAP_INFO và cập nhật: bản đồ, tọa độ nhân vật, waypoints, mobs và NPCs."""
        try:
            reader = msg.reader()
            from model.game_objects import Mob

            map_id = reader.read_ubyte()
            planet_id = reader.read_byte()
            tile_id = reader.read_byte()
            bg_id = reader.read_byte()
            type_map = reader.read_byte()
            map_name = reader.read_utf()
            zone_id = reader.read_byte()

            logger.info(f"Enter map: {map_name} (id={map_id}, zone={zone_id})")

            self.controller.map_info = {'id': map_id, 'name': map_name, 'planet': planet_id, 'zone': zone_id}
            self.controller.tile_map.set_map_info(map_id, planet_id, tile_id, bg_id, type_map, map_name, zone_id)
            
            # Clear chars list when entering new map/zone
            self.controller.chars.clear()

            self.account.char.cx = reader.read_short()
            self.account.char.cy = reader.read_short()
            self.account.char.map_id = map_id

            self.controller.tile_map.waypoints = []
            num_waypoints = reader.read_byte()
            for _ in range(num_waypoints):
                min_x = reader.read_short()
                min_y = reader.read_short()
                max_x = reader.read_short()
                max_y = reader.read_short()
                is_enter = reader.read_bool()
                is_offline = reader.read_bool()
                name = reader.read_utf()
                wp = Waypoint(min_x, min_y, max_x, max_y, is_enter, is_offline, name)
                self.controller.tile_map.add_waypoint(wp)

            self.controller.mobs = {}
            num_mobs = reader.read_ubyte()
            for i in range(num_mobs):
                for _ in range(5):
                    reader.read_bool()
                t_id = reader.read_byte()
                sys = reader.read_byte()
                hp = reader.read_int()
                level = reader.read_byte()
                max_hp = reader.read_int()
                mx = reader.read_short()
                my = reader.read_short()
                status = reader.read_byte()
                level_boss = reader.read_byte()
                is_boss = reader.read_bool()
                mob = Mob(mob_id=i, template_id=t_id, x=mx, y=my, hp=hp, max_hp=max_hp)
                mob.x_first, mob.y_first = mx, my
                mob.status = status
                self.controller.mobs[i] = mob

            num_extra = reader.read_byte()
            for _ in range(num_extra):
                if reader.available() > 0:
                    reader.read_byte()

            self.controller.npcs = {}
            if reader.available() > 0:
                num_npcs = reader.read_byte()
                for i in range(num_npcs):
                    status = reader.read_byte()
                    nx = reader.read_short()
                    ny = reader.read_short()
                    t_id = reader.read_byte()
                    avatar = reader.read_short()
                    self.controller.npcs[i] = {'id': i, 'status': status, 'x': nx, 'y': ny, 'template_id': t_id, 'avatar': avatar}
                    logger.info(f"Loaded NPC: id={i}, template={t_id} at ({nx},{ny})")

            # Signal that the login is complete as we are now in a map
            if not self.account.login_event.is_set():
                self.account.login_event.set()

            asyncio.create_task(self.account.service.pet_info())
            asyncio.create_task(self.account.service.finish_load_map())

        except Exception as e:
            logger.error(f"Error parsing MAP_INFO: {e}")
            import traceback
            traceback.print_exc()

    def process_zone_list(self, msg: Message):
        """Xử lý gói tin danh sách khu vực (Cmd 29)."""
        try:
            reader = msg.reader()
            zones_data = []
            
            n_zones = reader.read_byte()
            for _ in range(n_zones):
                zone_id = reader.read_byte()
                pts = reader.read_byte()
                num_players = reader.read_byte()
                max_players = reader.read_byte()
                rank_flag = reader.read_byte()
                
                z_info = {
                    'zone_id': zone_id,
                    'pts': pts,
                    'num_players': num_players,
                    'max_players': max_players,
                    'rank_flag': rank_flag
                }
                
                if rank_flag == 1:
                    z_info['rankName1'] = reader.read_utf()
                    z_info['rank1'] = reader.read_int()
                    z_info['rankName2'] = reader.read_utf()
                    z_info['rank2'] = reader.read_int()
                    
                zones_data.append(z_info)
            
            # Lưu zone_list cho auto_boss sử dụng
            self.controller.zone_list = zones_data
                
            current_zone = self.controller.map_info.get('zone', -1)
            map_id = self.controller.map_info.get('id', -1)
            ui.display_zone_list(zones_data, self.controller.map_info.get('name', 'Unknown'), self.account.username, current_zone, map_id)
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý danh sách khu vực: {e}")

    def process_map_offline(self, msg: Message):
        """Xử lý thông báo bản đồ chuyển sang chế độ offline (MAP_OFFLINE)."""
        try:
            reader = msg.reader()
            map_id = reader.read_int()
            time_offline = 0
            if reader.available() > 0:
                time_offline = reader.read_int()
            logger.info(f"Bản đồ ngoại tuyến (Cmd {msg.command}): MapID={map_id}, Thời gian ngoại tuyến={time_offline}s")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích MAP_OFFLINE: {e}")

    def process_update_data(self, msg: Message):
        """Xử lý gói tin UPDATE_DATA (-87)."""
        try:
            reader = msg.reader()
            vc_data = reader.read_byte()
            logger.info(f"UPDATE_DATA: vcData={vc_data}")
            
            def read_byte_array(r):
                length = r.read_int()
                return r.read_bytes(length)

            # Đọc các chunk dữ liệu
            read_byte_array(reader) # dart
            read_byte_array(reader) # arrow
            read_byte_array(reader) # effect
            read_byte_array(reader) # image
            read_byte_array(reader) # part
            read_byte_array(reader) # skill
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý UPDATE_DATA: {e}")

    def process_update_map(self, msg: Message):
        """Xử lý gói tin UPDATE_MAP (6) để cập nhật MobTemplate."""
        try:
            import struct
            reader = msg.reader()
            vc_map = reader.read_byte()
            logger.info(f"UPDATE_MAP: vcMap={vc_map}")
            
            # Map Names
            num_maps = reader.read_ubyte()
            for _ in range(num_maps):
                reader.read_utf()
                
            # Npc Templates
            num_npcs = reader.read_ubyte()
            for _ in range(num_npcs):
                reader.read_utf() # name
                reader.read_short() # head
                reader.read_short() # body
                reader.read_short() # leg
                num_menu = reader.read_ubyte()
                for _ in range(num_menu):
                    num_str = reader.read_ubyte()
                    for _ in range(num_str):
                        reader.read_utf()
            
            # Mob Templates
            from model.game_objects import MOB_TEMPLATES, MobTemplate
            try:
                num_mobs = reader.read_ubyte()
                count = 0
                for i in range(num_mobs):
                    t = MobTemplate()
                    t.mob_template_id = i
                    t.type = reader.read_byte()
                    t.name = reader.read_utf()
                    t.hp = reader.read_int()
                    t.range_move = reader.read_byte()
                    t.speed = reader.read_byte()
                    t.dart_type = reader.read_byte()
                    
                    MOB_TEMPLATES[i] = t
                    count += 1
                logger.info(f"Đã cập nhật {count} Mob Templates từ gói UPDATE_MAP.")
            except struct.error:
                 logger.warning(f"UPDATE_MAP: Dữ liệu Mob không đầy đủ (có thể do bản đồ cache hoặc gói tin ngắn). Đã đọc {count} mobs. Size={len(msg.get_data())}")
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý UPDATE_MAP: {e}")
            try:
                logger.error(f"Packet data (hex): {msg.get_data().hex()}")
            except:
                pass
            import traceback
            traceback.print_exc()
