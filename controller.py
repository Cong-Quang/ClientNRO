from logs.logger_config import logger 
import asyncio
from network.message import Message
from cmd import Cmd
from network.reader import Reader
from model.map_objects import TileMap, Waypoint
from network.service import Service
from services.movement import MovementService
from logic.auto_play import AutoPlay
from logic.auto_pet import AutoPet

# logger = logging.getLogger(__name__)

class Controller:
    def __init__(self, account):
        self.account = account
        self.char_info = {} # Nơi lưu trữ dữ liệu nhân vật
        self.map_info = {} # Nơi lưu trữ dữ liệu bản đồ
        self.mobs = {} # Lưu trữ thông tin quái vật
        self.tile_map = TileMap()
        self.movement = MovementService(self)
        self.auto_play = AutoPlay(self)
        self.auto_pet = AutoPet(self)

    def toggle_autoplay(self, enabled: bool):
        if enabled:
            task = self.auto_play.start()
            if task:
                self.account.tasks.append(task)
        else:
            self.auto_play.stop()

    def toggle_auto_pet(self, enabled: bool):
        if enabled:
            task = self.auto_pet.start()
            if task:
                self.account.tasks.append(task)
        else:
            self.auto_pet.stop()

    def on_message(self, msg: Message):
        try:
            cmd = msg.command
            if cmd == Cmd.NOT_LOGIN: # -29
                self.message_not_login(msg)
            elif cmd == Cmd.NOT_MAP: # -28
                self.message_not_map(msg)
            elif cmd == Cmd.GET_SESSION_ID: # -27 (Bắt tay - đã được xử lý trong Session)
                pass
            elif cmd == Cmd.ANDROID_PACK: # 126 (Gửi bởi client, phản hồi của server thường rất ít)
                logger.info(f"Đã nhận được phản hồi ANDROID_PACK (Cmd {cmd}).")
            elif cmd == Cmd.SPEACIAL_SKILL: # 112
                # Ví dụ: Đọc thông tin về các kỹ năng đặc biệt của nhân vật
                self.process_special_skill(msg)
            elif cmd == Cmd.ME_LOAD_POINT: # -42
                self.process_me_load_point(msg)
            elif cmd == Cmd.TASK_GET: # 40
                self.process_task_get(msg)
            elif cmd == Cmd.GAME_INFO: # 50
                self.process_game_info(msg)
            elif cmd == Cmd.MAP_INFO: # -24
                self.process_map_info(msg)
            elif cmd == Cmd.BAG: # -36
                self.process_bag_info(msg)
            elif cmd == Cmd.ITEM_BACKGROUND: # -31
                # Tài nguyên. Hiện chưa phân tích chi tiết.
                logger.info(f"Đã nhận ITEM_BACKGROUND (Cmd {cmd}), Độ dài: {len(msg.get_data())}")
            elif cmd == Cmd.BGITEM_VERSION: # -93
                # Tài nguyên. Hiện chưa phân tích chi tiết.
                logger.info(f"Đã nhận BGITEM_VERSION (Cmd {cmd}), Độ dài: {len(msg.get_data())}")
            elif cmd == Cmd.TILE_SET: # -82
                # Tài nguyên. Hiện chưa phân tích chi tiết.
                logger.info(f"Đã nhận TILE_SET (Cmd {cmd}), Độ dài: {len(msg.get_data())}")
            elif cmd == Cmd.MOB_ME_UPDATE: # -95
                 logger.info(f"Đã nhận MOB_ME_UPDATE (Cmd {cmd}).")
            elif cmd == Cmd.UPDATE_COOLDOWN: # -94
                 logger.info(f"Đã nhận UPDATE_COOLDOWN (Cmd {cmd}).")
            elif cmd == Cmd.PLAYER_ADD: # -5
                self.process_player_add(msg)
            elif cmd == Cmd.PLAYER_MOVE: # -7
                self.process_player_move(msg)
            elif cmd == Cmd.MOB_HP: # -9
                self.process_mob_hp(msg)
            elif cmd == Cmd.PLAYER_UP_EXP: # -3
                self.process_player_up_exp(msg)
            elif cmd == Cmd.MESSAGE_TIME: # 65
                self.process_message_time(msg)
            elif cmd == Cmd.NPC_CHAT: # 124
                self.process_npc_chat(msg)
            elif cmd == Cmd.SUB_COMMAND: # -30 (thường chứa các lệnh phụ bên trong)
                self.process_sub_command(msg)
            elif cmd == Cmd.CHANGE_FLAG: # -103
                self.process_change_flag(msg)
            elif cmd == Cmd.ME_BACK: # -15
                logger.info(f"Đã nhận ME_BACK (Cmd {cmd}).")
            elif cmd == Cmd.PLAYER_ATTACK_NPC: # 54
                self.process_player_attack_npc(msg)
            elif cmd == Cmd.PLAYER_DIE: # -8
                self.process_player_die(msg)
            elif cmd == Cmd.NPC_DIE: # -12
                self.process_npc_die(msg)
            elif cmd == Cmd.NPC_LIVE: # -13
                self.process_npc_live(msg)
            elif cmd == Cmd.MAXSTAMINA: # -69
                self.process_max_stamina(msg)
            elif cmd == Cmd.STAMINA: # -68
                self.process_stamina(msg)
            elif cmd == Cmd.UPDATE_ACTIVEPOINT: # -97
                self.process_update_active_point(msg)
            elif cmd == Cmd.MAP_OFFLINE: # -33
                self.process_map_offline(msg)
            elif cmd == Cmd.PET_INFO: # -107
                self.process_pet_info(msg)
            elif cmd == Cmd.THACHDAU: # -118
                self.process_thach_dau(msg)
            elif cmd == Cmd.AUTOPLAY: # -116
                self.process_autoplay(msg)
            elif cmd == Cmd.MABU: # -117
                self.process_mabu(msg)
            elif cmd == Cmd.THELUC: # -119
                self.process_the_luc(msg)
            elif cmd == Cmd.MAP_CLEAR: # -22
                logger.info(f"Đã nhận MAP_CLEAR (Cmd {cmd}).")
            
            else:
                logger.info(f"Đã nhận lệnh chưa được xử lý: {cmd}, Payload Len: {len(msg.get_data())}, Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi xử lý tin nhắn {msg.command}: {e}")
            import traceback
            traceback.print_exc()

    def message_not_login(self, msg: Message):
        try:
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            logger.info(f"Lệnh phụ NOT_LOGIN: {sub_cmd}")
            
            if sub_cmd == 2: # CLIENT_INFO / Phản hồi danh sách máy chủ
                server_list_str = reader.read_utf()
                logger.info(f"Đã nhận được danh sách máy chủ/thông tin liên kết: {server_list_str}")
                
                try:
                    servers = server_list_str.split(',')
                    parsed_servers = []
                    for s in servers:
                        parts = s.split(':')
                        if len(parts) >= 3:
                            server_name = parts[0]
                            server_ip = parts[1]
                            server_port = int(parts[2])
                            parsed_servers.append({'name': server_name, 'ip': server_ip, 'port': server_port})
                    if parsed_servers:
                        logger.info(f"Danh sách máy chủ đã phân tích: {parsed_servers}")
                    else:
                        logger.warning(f"Không thể phân tích danh sách máy chủ: {server_list_str}")

                    # Kiểm tra CanNapTien và AdminLink (theo C#)
                    if reader.available() > 0:
                        can_nap_tien_byte = reader.read_byte()
                        can_nap_tien = (can_nap_tien_byte == 1)
                        logger.info(f"Admin: {can_nap_tien}")
                        
                        if reader.available() > 0:
                            admin_link_byte = reader.read_byte()
                            admin_link = admin_link_byte # C# dùng sbyte cho trường này
                            logger.info(f"Admin Link: {admin_link}")

                except Exception as parse_e:
                    logger.warning(f"Lỗi khi phân tích thông báo danh sách máy chủ đầy đủ: {parse_e}")


            elif sub_cmd == Cmd.LOGINFAIL: # -102
                reason = reader.read_utf()
                logger.error(f"Đăng nhập thất bại: {reason}")
                
            elif sub_cmd == Cmd.LOGIN_DE: # 122
                logger.info("Đăng nhập DE đã được xác nhận (Thông tin phiên/người dùng có thể nằm ở đây).")
            
            elif sub_cmd == Cmd.LOGIN: # 0 (Thường ám chỉ thành công nếu nhận được dữ liệu?)
                logger.info("Đã nhận lệnh phụ NOT_LOGIN 0. (Dữ liệu đăng nhập/nhân vật đang chờ xử lý).")
                # Cần phân tích thêm C# Controller.messageNotLogin cho sub 0
                
            else:
                logger.info(f"Đã nhận được lệnh phụ NOT_LOGIN chưa được xử lý: {sub_cmd}, Payload Hex: {msg.get_data().hex()}")
                
        except Exception as e:
            logger.error(f"Lỗi khi phân tích cú pháp NOT_LOGIN: {e}")
            import traceback
            traceback.print_exc()

    def message_not_map(self, msg: Message):
        try:
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            logger.info(f"Lệnh phụ NOT_MAP: {sub_cmd}")

            if sub_cmd == 4: # UPDATE_VERSION / Kích hoạt đăng nhập thành công?
                logger.info("Đăng nhập thành công! Máy chủ đang yêu cầu kiểm tra phiên bản.")
                
                vsData = reader.read_byte()
                vsMap = reader.read_byte()
                vsSkill = reader.read_byte()
                vsItem = reader.read_byte()
                logger.info(f"Phiên bản máy chủ - Dữ liệu: {vsData}, Bản đồ: {vsMap}, Kỹ năng: {vsSkill}, Vật phẩm: {vsItem}")
                
            else:
                logger.info(f"Đã nhận được lệnh phụ NOT_MAP chưa được xử lý: {sub_cmd}, Payload Hex: {msg.get_data().hex()}")

        except Exception as e:
            logger.error(f"Lỗi khi phân tích cú pháp NOT_MAP: {e}")
            import traceback
            traceback.print_exc()

    def process_task_get(self, msg: Message):
        try:
            reader = msg.reader()
            task_id = reader.read_short()
            task_name = reader.read_utf()
            task_details = reader.read_utf()
            logger.info(f"Nhiệm vụ đã nhận (Lệnh {msg.command}): ID={task_id}, Tên='{task_name}', Chi tiết='{task_details}'")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích cú pháp TASK_GET: {e}")

    def process_game_info(self, msg: Message):
        try:
            reader = msg.reader()
            info_text = reader.read_utf()
            logger.info(f"Thông tin trò chơi (Lệnh {msg.command}): '{info_text}'")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích cú pháp GAME_INFO: {e}")

    def process_map_info(self, msg: Message):
        try:
            reader = msg.reader()
            
            # Map Header (Khớp với Controller.cs case -24)
            map_id = reader.read_ubyte()
            planet_id = reader.read_byte()
            tile_id = reader.read_byte()
            bg_id = reader.read_byte()
            type_map = reader.read_byte()
            map_name = reader.read_utf()
            zone_id = reader.read_byte()
            
            logger.info(f"Thông tin bản đồ (Lệnh {msg.command}): ID={map_id}, Tên='{map_name}', Hành tinh={planet_id}, Khu vực={zone_id}")
            self.map_info = {'id': map_id, 'name': map_name, 'planet': planet_id, 'zone': zone_id}
            
            # Cập nhật TileMap
            self.tile_map = TileMap() # Đặt lại
            self.tile_map.set_map_info(map_id, planet_id, tile_id, bg_id, type_map, map_name, zone_id)

            # loadInfoMap (Khớp với loadInfoMap trong Controller.cs)
            cx = reader.read_short()
            cy = reader.read_short()
            
            # Cập nhật vị trí nhân vật
            from model.game_objects import Char, Mob
            char = self.account.char
            char.cx = cx
            char.cy = cy
            char.map_id = map_id
            
            # Waypoints (Điểm chuyển bản đồ)
            num_waypoints = reader.read_byte()
            logger.debug(f"Waypoints: {num_waypoints}")
            for _ in range(num_waypoints):
                min_x = reader.read_short()
                min_y = reader.read_short()
                max_x = reader.read_short()
                max_y = reader.read_short()
                is_enter = reader.read_bool()
                is_offline = reader.read_bool()
                name = reader.read_utf()
                
                wp = Waypoint(min_x, min_y, max_x, max_y, is_enter, is_offline, name)
                self.tile_map.add_waypoint(wp)
                logger.debug(f"Đã phân tích Waypoint: {name} (Vào:{is_enter}, Off:{is_offline})")
            
            # Quái vật (Mobs)
            self.mobs = {} 
            num_mobs = reader.read_ubyte()
            logger.info(f"Quái vật trên bản đồ: {num_mobs}")
            
            for i in range(num_mobs):
                # Khớp với Mob constructor trong Controller.cs
                is_disable = reader.read_bool()
                is_dont_move = reader.read_bool()
                is_fire = reader.read_bool()
                is_ice = reader.read_bool()
                is_wind = reader.read_bool()
                
                template_id = reader.read_ubyte()
                sys = reader.read_byte()
                hp = reader.read_int() # C# dùng readInt() (4 bytes) ở đây
                level = reader.read_byte()
                max_hp = reader.read_int() # C# dùng readInt() (4 bytes) ở đây
                x = reader.read_short()
                y = reader.read_short()
                status = reader.read_byte()
                level_boss = reader.read_byte()
                is_boss = reader.read_bool()
                
                mob = Mob()
                mob.mob_id = i 
                mob.template_id = template_id
                mob.x = x
                mob.y = y
                mob.x_first = x
                mob.y_first = y
                mob.hp = hp
                mob.max_hp = max_hp
                mob.status = status
                mob.is_disable = is_disable
                
                self.mobs[i] = mob
            
            logger.info(f"Đã phân tích {len(self.mobs)} quái vật.")
            
            # Yêu cầu thông tin đệ tử sau khi vào map
            asyncio.create_task(self.account.service.pet_info())

        except Exception as e:
            logger.error(f"Lỗi khi phân tích MAP_INFO: {e}")
            import traceback
            traceback.print_exc()

    def process_npc_live(self, msg: Message):
        try:
            reader = msg.reader()
            mob_id = reader.read_ubyte()
            
            # Kiểm tra tính hợp lệ
            if mob_id not in self.mobs:
                logger.warning(f"NPC_LIVE: ID Quái vật không xác định {mob_id}")
                return

            mob = self.mobs[mob_id]
            
            # Logic C#:
            # mob.sys = msg.reader().readByte();
            # mob.levelBoss = msg.reader().readByte();
            # mob.hp = msg.reader().readInt();
            
            mob.sys = reader.read_byte()
            mob.level_boss = reader.read_byte()
            mob.hp = reader.read_int()
            
            # Đặt lại trạng thái
            mob.status = 5 # Còn sống
            mob.max_hp = mob.hp # Thường đặt lại mức tối đa khi hồi sinh
            mob.x = mob.x_first
            mob.y = mob.y_first
            
            logger.info(f"Quái vật HỒI SINH: ID={mob_id} | HP={mob.hp} | Vị trí=({mob.x},{mob.y})")
            
        except Exception as e:
            logger.error(f"Lỗi khi phân tích NPC_LIVE: {e}")
            import traceback
            traceback.print_exc()

    def process_me_load_point(self, msg: Message):
        try:
            reader = msg.reader()
            char = self.account.char
            
            # Trong source code này, readInt3Byte thực chất gọi readInt (4 bytes)
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
            
            logger.info(f"Chỉ số nhân vật (Cmd {msg.command}): HP={char.c_hp}/{char.c_hp_full}, MP={char.c_mp}/{char.c_mp_full}, Tiềm năng={char.c_tiem_nang}, Sát thương={char.c_dam_full}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích ME_LOAD_POINT: {e}")

    def process_sub_command(self, msg: Message):
        try:
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            char = self.account.char

            if sub_cmd == 0: # ME_LOAD_ALL
                char.char_id = reader.read_int()
                char.ctask_id = reader.read_byte()
                char.gender = reader.read_byte()
                char.head = reader.read_short()
                char.name = reader.read_utf()
                char.c_pk = reader.read_byte()
                char.c_type_pk = reader.read_byte()
                char.c_power = reader.read_long()
                logger.info(f"ME_LOAD_ALL: ID={char.char_id}, Tên={char.name}, Sức mạnh={char.c_power}")
            
            elif sub_cmd == 4: # ME_LOAD_INFO
                char.xu = reader.read_long()
                char.luong = reader.read_int()
                char.c_hp = reader.read_int()
                char.c_mp = reader.read_int()
                char.luong_khoa = reader.read_int()
                logger.info(f"Cập nhật tài sản: Vàng={char.xu}, Ngọc={char.luong}, HP={char.c_hp}, MP={char.c_mp}")

            elif sub_cmd == 5: # ME_LOAD_HP
                old_hp = char.c_hp
                char.c_hp = reader.read_int()
                logger.info(f"Cập nhật HP: {old_hp} -> {char.c_hp}")

            elif sub_cmd == 6: # ME_LOAD_MP
                old_mp = char.c_mp
                char.c_mp = reader.read_int()
                logger.info(f"Cập nhật MP: {old_mp} -> {char.c_mp}")

            else:
                logger.info(f"SUB_COMMAND (Lệnh {msg.command}) lệnh phụ: {sub_cmd}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích SUB_COMMAND: {e}")

    def process_bag_info(self, msg: Message):
        try:
            reader = msg.reader()
            action = reader.read_byte()
            logger.info(f"Thông tin túi đồ (Cmd {msg.command}): Hành động={action}")

            if action == 0:  # Full inventory update
                from model.game_objects import Char, Item, ItemOption
                my_char = self.account.char

                if reader.available() < 1: return
                bag_size = reader.read_ubyte()
                my_char.arr_item_bag = [None] * bag_size
                logger.info(f"Đang xử lý {bag_size} ô trong túi đồ.")

                for i in range(bag_size):
                    if reader.available() < 2: break 
                    template_id = reader.read_short()
                    if template_id == -1:
                        continue

                    item = Item()
                    item.item_id = template_id
                    
                    if reader.available() < 4: break
                    item.quantity = reader.read_int()

                    if reader.available() < 2: break
                    item.info = reader.read_utf()
                    
                    if reader.available() < len(item.info.encode('utf-8')) + 1: break

                    if reader.available() < 2: break
                    item.content = reader.read_utf()
                    
                    if reader.available() < len(item.content.encode('utf-8')) + 1: break
                    
                    item.index_ui = i
                    
                    if reader.available() < 1: break
                    num_options = reader.read_ubyte()
                    if num_options > 0:
                        item.item_option = []
                        for _ in range(num_options):
                            if reader.available() < 3: break
                            option_id = reader.read_ubyte()
                            param = reader.read_ushort()
                            if option_id != 255:
                                item.item_option.append(ItemOption(option_id, param))
                    
                    my_char.arr_item_bag[i] = item
                
                logger.info(f"Đã cập nhật thành công túi đồ với {sum(1 for i in my_char.arr_item_bag if i is not None)} vật phẩm.")

            elif action == 2: # Single item quantity update
                if reader.available() < 5: return
                index = reader.read_byte()
                quantity = reader.read_int()
                logger.info(f"Cập nhật số lượng vật phẩm tại vị trí {index} thành {quantity}.")
                my_char = self.account.char
                if index < len(my_char.arr_item_bag) and my_char.arr_item_bag[index] is not None:
                    my_char.arr_item_bag[index].quantity = quantity
                    if quantity == 0:
                        my_char.arr_item_bag[index] = None
                else:
                    logger.warning(f"Nhận được cập nhật số lượng cho vật phẩm không hợp lệ tại vị trí {index}.")

        except Exception as e:
            logger.error(f"Lỗi khi phân tích BAG_INFO (Cmd -36): {e}")
            import traceback
            traceback.print_exc()
            
    def process_special_skill(self, msg: Message):
        try:
            reader = msg.reader()
            special_type = reader.read_byte()
            if special_type == 0:
                img_id = reader.read_short()
                info = reader.read_utf()
                logger.info(f"Kỹ năng đặc biệt (Cmd {msg.command}): Loại={special_type}, ImgID={img_id}, Thông tin='{info}'")
            elif special_type == 1:
                # Phân tích phức tạp hơn cho danh sách kỹ năng
                logger.info(f"Kỹ năng đặc biệt (Cmd {msg.command}): Loại={special_type} (danh sách), Payload Hex: {msg.get_data().hex()}")
            else:
                logger.info(f"Kỹ năng đặc biệt (Cmd {msg.command}): Loại không xác định={special_type}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích SPEACIAL_SKILL: {e}")

    def process_player_add(self, msg: Message):
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            clan_id = reader.read_int()
            
            # Sử dụng hàm hỗ trợ để đọc thông tin nhân vật
            char_data = self.read_char_info(reader)
            char_data['id'] = player_id
            char_data['clan_id'] = clan_id
            
            logger.info(f"Đã thêm người chơi (Cmd {msg.command}): ID={player_id}, Tên='{char_data.get('name')}', Vị trí=({char_data.get('x')},{char_data.get('y')})")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_ADD: {e}")

    def read_char_info(self, reader: Reader) -> dict:
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
        reader.read_byte() # không sử dụng/dự phòng
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
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            x = reader.read_short()
            y = reader.read_short()
            logger.info(f"Người chơi di chuyển (Cmd {msg.command}): ID={player_id}, X={x}, Y={y}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_MOVE: {e}")

    def process_mob_hp(self, msg: Message):
        try:
            reader = msg.reader()
            mob_id = reader.read_ubyte() 
            current_hp = reader.read_int3() 
            damage = reader.read_int3() 
            
            # Dữ liệu bổ sung tùy chọn (chí mạng, hiệu ứng) - đọc để đảm bảo an toàn
            if reader.available() > 0:
                try:
                    reader.read_bool() # isCrit
                    reader.read_byte() # effectId
                except: pass

            mob = self.mobs.get(mob_id)
            if mob:
                old_hp = mob.hp
                mob.hp = current_hp
                if mob.hp <= 0:
                     mob.status = 0 # Đánh dấu là đã chết nếu HP bằng 0, mặc dù NPC_DIE thường sẽ xác nhận điều này
                
                logger.info(f"Cập nhật quái vật: ID={mob_id} | HP: {old_hp} -> {current_hp}/{mob.max_hp} (ST: {damage})")
            else:
                logger.warning(f"Đã nhận MOB_HP cho MobID không xác định={mob_id}. HP={current_hp}")
                
        except Exception as e:
            logger.error(f"Lỗi khi phân tích MOB_HP: {e}")

    def process_npc_die(self, msg: Message):
        try:
            reader = msg.reader()
            mob_id = reader.read_ubyte()
            damage = reader.read_int3()
            # isCrit = reader.read_bool() # không sử dụng
            
            mob = self.mobs.get(mob_id)
            if mob:
                mob.hp = 0
                mob.status = 0 # Đã chết
                logger.info(f"Quái vật đã CHẾT: ID={mob_id} (ST: {damage})")
                
                # Xóa tiêu điểm nếu đó là quái vật này
                if self.account.char.mob_focus == mob:
                    self.account.char.mob_focus = None
            else:
                logger.warning(f"Đã nhận NPC_DIE cho MobID không xác định={mob_id}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích NPC_DIE: {e}")

    def process_player_up_exp(self, msg: Message):
        try:
            reader = msg.reader()
            # C#: sbyte b73 = msg.reader().readByte();
            # C#: int num181 = msg.reader().readInt();
            exp_type = reader.read_byte()
            amount = reader.read_int()
            logger.info(f"Người chơi tăng EXP (Cmd {msg.command}): Loại={exp_type}, Số lượng={amount}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_UP_EXP: {e}")

    def process_message_time(self, msg: Message):
        try:
            reader = msg.reader()
            time_id = reader.read_byte()
            message = reader.read_utf()
            duration = reader.read_short()
            logger.info(f"Thông báo thời gian (Cmd {msg.command}): ID={time_id}, Thông báo='{message}', Thời hạn={duration}s")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích MESSAGE_TIME: {e}")

    def process_npc_chat(self, msg: Message):
        try:
            reader = msg.reader()
            npc_id = reader.read_short()
            message = reader.read_utf()
            logger.info(f"NPC Chat (Cmd {msg.command}): NPC_ID={npc_id}, Nội dung='{message}'")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích NPC_CHAT: {e}")
            
    def process_sub_command(self, msg: Message):
        try:
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            logger.info(f"SUB_COMMAND (Lệnh {msg.command}) lệnh phụ: {sub_cmd}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích SUB_COMMAND: {e}")

    def process_change_flag(self, msg: Message):
        try:
            reader = msg.reader()
            char_id = reader.read_int()
            flag_id = 0
            if reader.available() > 0:
                flag_id = reader.read_byte()
            logger.info(f"Thay đổi cờ (Lệnh {msg.command}): CharID={char_id}, FlagID={flag_id}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích CHANGE_FLAG: {e}")

    def process_player_attack_npc(self, msg: Message):
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            # NPC ID có khả năng là kiểu short (2 byte) dựa trên phân tích log (Payload 6 byte: 4 + 2)
            npc_id = reader.read_byte() # Thường Mob ID là byte? Hay Short?
            # Cmd 54 payload: write_byte(mobId) trong Service.
            # Nhưng phản hồi có thể bao gồm ID người chơi?
            # Hãy kiểm tra payload.
            # logger.info(f"ATTACK_NPC Payload: {msg.get_data().hex()}")
            # Đọc lại dựa trên logic C# nếu có...
            # Nhưng hiện tại, chỉ ghi log những gì có thể.
            logger.info(f"Người chơi tấn công NPC (Cmd {msg.command}): PlayerID={player_id}, NPC_ID={npc_id}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_ATTACK_NPC: {e}")

    def process_player_die(self, msg: Message):
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            logger.info(f"Người chơi đã chết (Cmd {msg.command}): PlayerID={player_id}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_DIE: {e}")

    def process_max_stamina(self, msg: Message):
        try:
            reader = msg.reader()
            max_stamina = reader.read_short()
            logger.info(f"Thể lực tối đa (Cmd {msg.command}): {max_stamina}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích MAXSTAMINA: {e}")

    def process_stamina(self, msg: Message):
        try:
            reader = msg.reader()
            stamina = reader.read_short()
            logger.info(f"Thể lực hiện tại (Cmd {msg.command}): {stamina}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích STAMINA: {e}")

    def process_update_active_point(self, msg: Message):
        try:
            reader = msg.reader()
            active_point = reader.read_int()
            logger.info(f"Cập nhật điểm năng động (Cmd {msg.command}): {active_point}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích UPDATE_ACTIVEPOINT: {e}")

    def process_map_offline(self, msg: Message):
        try:
            reader = msg.reader()
            map_id = reader.read_int()
            time_offline = 0
            if reader.available() > 0:
                time_offline = reader.read_int()
            logger.info(f"Bản đồ ngoại tuyến (Cmd {msg.command}): MapID={map_id}, Thời gian ngoại tuyến={time_offline}s")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích MAP_OFFLINE: {e}")
    def process_pet_info(self, msg: Message):
        try:
            reader = msg.reader()
            from model.game_objects import Char, Item, ItemOption, Skill
            
            b_pet = reader.read_byte()
            if b_pet == 0:
                self.account.char.have_pet = False
                self.account.pet.have_pet = False
                logger.info("Nhân vật không có đệ tử.")
            if b_pet == 1:
                self.account.char.have_pet = True
                self.account.pet.have_pet = True
                logger.info("Nhân vật có đệ tử.")
            
            if b_pet != 2:
                return

            pet = self.account.pet
            pet.have_pet = True
            pet.head = reader.read_short()
            pet.set_default_part()
            
            num_body = reader.read_ubyte()
            pet.arr_item_body = [None] * num_body
            for i in range(num_body):
                template_id = reader.read_short()
                if template_id == -1:
                    continue
                
                item = Item()
                item.item_id = template_id
                item.quantity = reader.read_int()
                item.info = reader.read_utf()
                item.content = reader.read_utf()
                
                num_options = reader.read_ubyte()
                if num_options != 0:
                    item.item_option = []
                    for _ in range(num_options):
                        opt_id = reader.read_ubyte()
                        opt_param = reader.read_ushort()
                        if opt_id != 255:
                             item.item_option.append(ItemOption(opt_id, opt_param))
                
                pet.arr_item_body[i] = item
            
            pet.c_hp = reader.read_int()
            pet.c_hp_full = reader.read_int()
            pet.c_mp = reader.read_int()
            pet.c_mp_full = reader.read_int()
            pet.c_dam_full = reader.read_int()
            pet.name = reader.read_utf()
            pet.curr_str_level = reader.read_utf()
            pet.c_power = reader.read_long()
            pet.c_tiem_nang = reader.read_long()
            pet.pet_status = reader.read_byte()
            pet.c_stamina = reader.read_short()
            pet.c_max_stamina = reader.read_short()
            pet.c_critical_full = reader.read_byte()
            pet.c_def_full = reader.read_short()
            
            num_skills = reader.read_byte()
            pet.arr_pet_skill = [None] * num_skills
            for i in range(num_skills):
                skill_id = reader.read_short()
                if skill_id != -1:
                    s = Skill()
                    s.skill_id = skill_id
                    pet.arr_pet_skill[i] = s
                else:
                    s = Skill()
                    s.more_info = reader.read_utf()
                    pet.arr_pet_skill[i] = s
            
            logger.info(f"Đã cập nhật thông tin Đệ tử: {pet.name} | HP: {pet.c_hp}/{pet.c_hp_full} | Sức mạnh: {pet.c_power}")

        except Exception as e:
            logger.error(f"Lỗi khi phân tích PET_INFO: {e}")
            import traceback
            traceback.print_exc()

    def process_thach_dau(self, msg: Message):
        try:
            reader = msg.reader()
            challenge_id = reader.read_int() # Trường ví dụ
            logger.info(f"Thách đấu (Cmd {msg.command}): ChallengeID={challenge_id}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích THACHDAU: {e}")

    def process_autoplay(self, msg: Message):
        try:
            reader = msg.reader()
            auto_mode = reader.read_byte() # Trường ví dụ
            logger.info(f"Tự động chơi (Cmd {msg.command}): Chế độ={auto_mode}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích AUTOPLAY: {e}")

    def process_mabu(self, msg: Message):
        try:
            reader = msg.reader()
            mabu_state = reader.read_byte() # Trường ví dụ
            logger.info(f"Mabu (Cmd {msg.command}): Trạng thái={mabu_state}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích MABU: {e}")

    def process_the_luc(self, msg: Message):
        try:
            reader = msg.reader()
            the_luc_value = reader.read_short() # Trường ví dụ
            logger.info(f"Thể lực (Cmd {msg.command}): Giá trị={the_luc_value}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích THELUC: {e}")