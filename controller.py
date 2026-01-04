from logs.logger_config import logger 
import asyncio
import struct
from network.message import Message
from cmd import Cmd
from network.reader import Reader
from model.map_objects import TileMap, Waypoint
from network.service import Service
from services.movement import MovementService
from logic.auto_play import AutoPlay
from logic.auto_pet import AutoPet
from logic.xmap import XMap

class Controller:
    """Quản lý xử lý tin nhắn và trạng thái game cho một tài khoản.

    Thuộc tính chính:
      - account: đối tượng tài khoản đang điều khiển
      - tile_map, mobs, npcs: trạng thái bản đồ và thực thể
      - movement, auto_play, auto_pet, xmap: các dịch vụ liên quan
    """
    def __init__(self, account):
        """Khởi tạo Controller cho `account`: thiết lập trạng thái và các dịch vụ liên quan."""
        self.account = account
        self.char_info = {}
        self.map_info = {}
        self.mobs = {}
        self.npcs = {}
        self.tile_map = TileMap()
        self.movement = MovementService(self)
        self.auto_play = AutoPlay(self)
        self.auto_pet = AutoPet(self)
        self.xmap = XMap(self)

    def toggle_autoplay(self, enabled: bool):
        """Bật hoặc tắt chế độ AutoPlay; khi bật, thêm task AutoPlay vào `account.tasks` nếu có."""
        if enabled:
            task = self.auto_play.start()
            if task:
                self.account.tasks.append(task)
        else:
            self.auto_play.stop()

    def toggle_auto_pet(self, enabled: bool):
        """Bật hoặc tắt chế độ AutoPet; khi bật, thêm task AutoPet vào `account.tasks` nếu có."""
        if enabled:
            task = self.auto_pet.start()
            if task:
                self.account.tasks.append(task)
        else:
            self.auto_pet.stop()

    def on_message(self, msg: Message):
        """Chuyển tiếp tin nhắn theo `msg.command` đến handler tương ứng.

        Không có chú thích inline: chỉ tên handler và log ngắn gọn để dễ đọc.
        """
        try:
            cmd = msg.command
            if cmd == Cmd.NOT_LOGIN:
                self.message_not_login(msg)
            elif cmd == Cmd.NOT_MAP:
                self.message_not_map(msg)
            elif cmd == Cmd.GET_SESSION_ID:
                pass
            elif cmd == Cmd.ANDROID_PACK:
                logger.info(f"Received ANDROID_PACK (Cmd {cmd}).")
            elif cmd == Cmd.SPEACIAL_SKILL:
                self.process_special_skill(msg)
            elif cmd == Cmd.ME_LOAD_POINT:
                self.process_me_load_point(msg)
            elif cmd == Cmd.TASK_GET:
                self.process_task_get(msg)
            elif cmd == Cmd.TASK_UPDATE:
                self.process_task_update(msg)
            elif cmd == Cmd.TASK_NEXT:
                self.process_task_next(msg)
            elif cmd == Cmd.GAME_INFO:
                self.process_game_info(msg)
            elif cmd == Cmd.MAP_INFO:
                self.process_map_info(msg)
            elif cmd == Cmd.BAG:
                self.process_bag_info(msg)
            elif cmd == Cmd.ITEM_BACKGROUND:
                logger.info(f"Received ITEM_BACKGROUND (Cmd {cmd}), len={len(msg.get_data())}")
            elif cmd == Cmd.BGITEM_VERSION:
                logger.info(f"Received BGITEM_VERSION (Cmd {cmd}), len={len(msg.get_data())}")
            elif cmd == Cmd.TILE_SET:
                logger.info(f"Received TILE_SET (Cmd {cmd}), len={len(msg.get_data())}")
            elif cmd == Cmd.MOB_ME_UPDATE:
                logger.info(f"Received MOB_ME_UPDATE (Cmd {cmd}).")
            elif cmd == Cmd.UPDATE_COOLDOWN:
                logger.info(f"Received UPDATE_COOLDOWN (Cmd {cmd}).")
            elif cmd == Cmd.PLAYER_ADD:
                self.process_player_add(msg)
            elif cmd == Cmd.PLAYER_MOVE:
                self.process_player_move(msg)
            elif cmd == Cmd.MOB_HP:
                self.process_mob_hp(msg)
            elif cmd == Cmd.PLAYER_UP_EXP:
                self.process_player_up_exp(msg)
            elif cmd == Cmd.MESSAGE_TIME:
                self.process_message_time(msg)
            elif cmd == Cmd.OPEN_UI_CONFIRM:
                self.process_open_ui_confirm(msg)
            elif cmd == Cmd.NPC_CHAT:
                self.process_npc_chat(msg)
            elif cmd == Cmd.NPC_ADD_REMOVE:
                self.process_npc_add_remove(msg)
            elif cmd == Cmd.SUB_COMMAND:
                self.process_sub_command(msg)
            elif cmd == Cmd.CHANGE_FLAG:
                self.process_change_flag(msg)
            elif cmd == Cmd.ME_BACK:
                logger.info(f"Received ME_BACK (Cmd {cmd}).")
            elif cmd == Cmd.PLAYER_ATTACK_NPC:
                self.process_player_attack_npc(msg)
            elif cmd == Cmd.PLAYER_DIE:
                self.process_player_die(msg)
            elif cmd == Cmd.NPC_DIE:
                self.process_npc_die(msg)
            elif cmd == Cmd.NPC_LIVE:
                self.process_npc_live(msg)
            elif cmd == Cmd.MAXSTAMINA:
                self.process_max_stamina(msg)
            elif cmd == Cmd.STAMINA:
                self.process_stamina(msg)
            elif cmd == Cmd.UPDATE_ACTIVEPOINT:
                self.process_update_active_point(msg)
            elif cmd == Cmd.MAP_OFFLINE:
                self.process_map_offline(msg)
            elif cmd == Cmd.PET_INFO:
                self.process_pet_info(msg)
            elif cmd == Cmd.POWER_INFO:
                self.process_power_info(msg)
            elif cmd == Cmd.THACHDAU:
                self.process_thach_dau(msg)
            elif cmd == Cmd.AUTOPLAY:
                self.process_autoplay(msg)
            elif cmd == Cmd.MABU:
                self.process_mabu(msg)
            elif cmd == Cmd.THELUC:
                self.process_the_luc(msg)
            elif cmd == Cmd.MAP_CLEAR:
                logger.info(f"Received MAP_CLEAR (Cmd {cmd}).")
            elif cmd == Cmd.UPDATE_DATA:
                self.process_update_data(msg)
            elif cmd == Cmd.UPDATE_MAP:
                self.process_update_map(msg)
            else:
                logger.info(f"Unhandled command: {cmd}, len={len(msg.get_data())}, hex={msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error handling message {msg.command}: {e}")
            import traceback
            traceback.print_exc()
    def message_not_login(self, msg: Message):
        """Xử lý các sub-command của NOT_LOGIN (ví dụ server list, login fail...)."""
        try:
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            logger.info(f"NOT_LOGIN subcmd: {sub_cmd}")

            if sub_cmd == 2:
                server_list_str = reader.read_utf()
                logger.info(f"Server list received: {server_list_str}")
                try:
                    servers = server_list_str.split(',')
                    parsed_servers = []
                    for s in servers:
                        parts = s.split(':')
                        if len(parts) >= 3:
                            parsed_servers.append({'name': parts[0], 'ip': parts[1], 'port': int(parts[2])})
                    if parsed_servers:
                        logger.info(f"Parsed servers: {parsed_servers}")
                    else:
                        logger.warning(f"Failed to parse server list: {server_list_str}")

                    if reader.available() > 0:
                        can_nap_tien = (reader.read_byte() == 1)
                        logger.info(f"Admin enabled: {can_nap_tien}")
                        if reader.available() > 0:
                            admin_link = reader.read_byte()
                            logger.info(f"Admin link flag: {admin_link}")
                except Exception as parse_e:
                    logger.warning(f"Error parsing server list: {parse_e}")

            elif sub_cmd == Cmd.LOGINFAIL:
                reason = reader.read_utf()
                logger.error(f"Login failed: {reason}")
            elif sub_cmd == Cmd.LOGIN_DE:
                logger.info("Login DE confirmed.")
            elif sub_cmd == Cmd.LOGIN:
                logger.info("Received NOT_LOGIN subcmd 0.")
            else:
                logger.info(f"Unhandled NOT_LOGIN subcmd: {sub_cmd}, payload={msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error parsing NOT_LOGIN: {e}")
            import traceback
            traceback.print_exc()

    def message_not_map(self, msg: Message):
        """Xử lý NOT_MAP sub-commands (ví dụ: UPDATE_VERSION)."""
        try:
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            logger.info(f"NOT_MAP subcmd: {sub_cmd}")

            if sub_cmd == 4:
                vsData = reader.read_byte()
                vsMap = reader.read_byte()
                vsSkill = reader.read_byte()
                vsItem = reader.read_byte()
                logger.info(f"Server versions: data={vsData}, map={vsMap}, skill={vsSkill}, item={vsItem}")
                asyncio.create_task(self.account.service.client_ok())
                
            else:
                logger.info(f"Unhandled NOT_MAP subcmd: {sub_cmd}, payload={msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error parsing NOT_MAP: {e}")
            import traceback
            traceback.print_exc()

    def process_task_get(self, msg: Message):
        """Phân tích gói TASK_GET và lưu thông tin nhiệm vụ vào nhân vật."""
        try:
            reader = msg.reader()
            task_id = reader.read_short()
            index = reader.read_byte()
            task_name = reader.read_utf()
            task_detail = reader.read_utf()
            
            # Cấu trúc task:
            # - byte len
            # - loop len:
            #   + utf subName
            #   + byte npcId
            #   + short mapId
            #   + utf desc
            # - short count (current)
            # - loop len:
            #   + short maxCount
            
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
            char.task.counts = counts # Mảng chứa max count của từng bước
            char.task.count = current_count # Giá trị đã làm được
            
            logger.info(f"Nhiệm vụ (Cmd {msg.command}): [{task_id}] {task_name} - Bước {index} - Progress: {current_count}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích TASK_GET: {e}")

    def process_task_update(self, msg: Message):
        """Cập nhật tiến độ nhiệm vụ (TASK_UPDATE)."""
        try:
            reader = msg.reader()
            val = reader.read_short()
            
            char = self.account.char
            
            # Check for short packet (Optimized packet: Only 2 bytes sent)
            # LOGIC FIX: The short packet contains the CURRENT COUNT, not the Task ID.
            if reader.available() == 0:
                char.task.count = val
                logger.info(f"Cập nhật nhiệm vụ (Ngắn): Tiến độ -> {val}")
                return

            # Normal packet: task_id, index, count
            task_id = val
            if reader.available() < 3:
                 logger.warning(f"TASK_UPDATE: Dữ liệu không đủ ({reader.available()} bytes).")
                 return

            index = reader.read_byte()
            count = reader.read_short()
            
            # Verify if it matches current task
            if char.task.task_id == task_id and char.task.index == index:
                char.task.count = count
                logger.info(f"Cập nhật nhiệm vụ (Cmd {msg.command}): [{task_id}] Bước {index} -> {count}")
            else:
                # If ID matches but index diff, maybe task changed step?
                if char.task.task_id == task_id:
                     char.task.index = index
                     char.task.count = count
                     logger.info(f"Cập nhật nhiệm vụ (Cmd {msg.command}): [{task_id}] Bước {index} -> {count}")
                else:
                     logger.warning(f"TASK_UPDATE bị bỏ qua: ID {task_id}, Idx {index} != CurID {char.task.task_id}")

        except Exception as e:
            logger.error(f"Lỗi khi phân tích TASK_UPDATE: {e}")

    def process_task_next(self, msg: Message):
        """Xử lý chuyển bước nhiệm vụ (TASK_NEXT - 41)."""
        try:
            # Cmd 41 thường rỗng (len=0) nghĩa là next step.
            char = self.account.char
            
            # Check if there is data
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
                # Empty packet = Increment index
                char.task.index += 1
                logger.info(f"Chuyển bước nhiệm vụ (Cmd 41): Index +1 -> {char.task.index} (No Data)")
            
            char.task.count = 0
        except Exception as e:
            logger.error(f"Lỗi khi xử lý TASK_NEXT: {e}")

    def process_game_info(self, msg: Message):
        """Đọc và ghi log chuỗi thông tin do server gửi (GAME_INFO)."""
        try:
            reader = msg.reader()
            info_text = reader.read_utf()
            logger.info(f"Thông tin trò chơi (Lệnh {msg.command}): '{info_text}'")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích cú pháp GAME_INFO: {e}")

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

            self.map_info = {'id': map_id, 'name': map_name, 'planet': planet_id, 'zone': zone_id}
            self.tile_map.set_map_info(map_id, planet_id, tile_id, bg_id, type_map, map_name, zone_id)

            self.account.char.cx = reader.read_short()
            self.account.char.cy = reader.read_short()
            self.account.char.map_id = map_id

            self.tile_map.waypoints = []
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
                self.tile_map.add_waypoint(wp)

            self.mobs = {}
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
                # Ghi chú: Tên mob không được server gửi trực tiếp trong gói MAP_INFO này.
                # Thuộc tính `name` trong class Mob sẽ không được điền.
                mob = Mob(mob_id=i, template_id=t_id, x=mx, y=my, hp=hp, max_hp=max_hp)
                mob.x_first, mob.y_first = mx, my
                mob.status = status
                self.mobs[i] = mob

            num_extra = reader.read_byte()
            for _ in range(num_extra):
                if reader.available() > 0:
                    reader.read_byte()

            self.npcs = {}
            if reader.available() > 0:
                num_npcs = reader.read_byte()
                for i in range(num_npcs):
                    status = reader.read_byte()
                    nx = reader.read_short()
                    ny = reader.read_short()
                    t_id = reader.read_byte()
                    avatar = reader.read_short()
                    self.npcs[i] = {'id': i, 'status': status, 'x': nx, 'y': ny, 'template_id': t_id, 'avatar': avatar}
                    logger.info(f"Loaded NPC: id={i}, template={t_id} at ({nx},{ny})")

            # Signal that the login is complete as we are now in a map
            if not self.account.login_event.is_set():
                self.account.login_event.set()

            asyncio.create_task(self.account.service.pet_info())

        except Exception as e:
            logger.error(f"Error parsing MAP_INFO: {e}")
            import traceback
            traceback.print_exc()

    def process_npc_live(self, msg: Message):
        """Xử lý NPC_LIVE: cập nhật HP và trạng thái khi quái vật hồi sinh."""
        try:
            reader = msg.reader()
            mob_id = reader.read_ubyte()
            if mob_id not in self.mobs:
                logger.warning(f"NPC_LIVE: unknown mob id {mob_id}")
                return

            mob = self.mobs[mob_id]
            
            mob.sys = reader.read_byte()
            mob.level_boss = reader.read_byte()
            mob.hp = reader.read_int()
            # Ghi chú: Tên mob không được server gửi trực tiếp trong gói NPC_LIVE này.
            # Thuộc tính `name` trong class Mob sẽ không được điền ngay cả khi hồi sinh.
            mob.status = 5
            mob.max_hp = mob.hp
            mob.x = mob.x_first
            mob.y = mob.y_first
            
            logger.info(f"Quái vật HỒI SINH: ID={mob_id} | HP={mob.hp} | Vị trí=({mob.x},{mob.y})")
            
        except Exception as e:
            logger.error(f"Lỗi khi phân tích NPC_LIVE: {e}")
            import traceback
            traceback.print_exc()

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
                self.xmap.handle_death()

            logger.info(f"Chỉ số nhân vật (Cmd {msg.command}): HP={char.c_hp}/{char.c_hp_full}, MP={char.c_mp}/{char.c_mp_full}, Tiềm năng={char.c_tiem_nang}, Sát thương={char.c_dam_full}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích ME_LOAD_POINT: {e}")

    def process_npc_add_remove(self, msg: Message):
        """Xử lý lệnh thêm/bớt NPC (hiện chỉ đọc template id và không hành động thêm)."""
        try:
            reader = msg.reader()
            npc_template_id = reader.read_byte()
            pass
        except Exception as e:
            logger.error(f"Lỗi khi phân tích NPC_ADD_REMOVE: {e}")

    def process_sub_command(self, msg: Message):
        """Xử lý SUB_COMMAND với nhiều trường hợp con (tải thông tin nhân vật, cập nhật HP/MP, tài sản, items)."""
        try:
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            char = self.account.char

            if sub_cmd == 0:
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


                try:
                    num_body_items = reader.read_byte()
                    for _ in range(num_body_items):
                        if reader.available() < 2: break
                        template_id = reader.read_short()
                        if template_id != -1:
                            if reader.available() < 4: break
                            reader.read_int() # quantity
                            if reader.available() < 1: break
                            # Skip reading strings for now to avoid complexity
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

                # Check for remaining data (Potential "Other Info")
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

            elif sub_cmd == 61: # Unhandled sub-command
                if reader.available() > 0:
                    remaining = reader.read_remaining()
                    logger.info(f"SUB_COMMAND (Lệnh {msg.command}) sub_cmd 61: Payload Hex: {remaining.hex()}")
                else:
                    logger.info(f"SUB_COMMAND (Lệnh {msg.command}) sub_cmd 61 (empty)")

            elif sub_cmd == 14: # Unhandled sub-command (frequent)
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
    def process_bag_info(self, msg: Message):
        """Cập nhật dữ liệu túi đồ (BAG): xử lý danh sách ô, cập nhật số lượng hoặc thay đổi ô trong túi."""
        try:
            reader = msg.reader()
            action = reader.read_byte()
            logger.info(f"Thông tin túi đồ (Cmd {msg.command}): Hành động={action}")

            if action == 0:
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

            elif action == 2:
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

    def process_player_add(self, msg: Message):
        """Đọc thông tin khi có player mới xuất hiện trên map và ghi log cơ bản."""
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            clan_id = reader.read_int()
            

            char_data = self.read_char_info(reader)
            char_data['id'] = player_id
            char_data['clan_id'] = clan_id
            
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

            mob = self.mobs.get(mob_id)
            if mob:
                old_hp = mob.hp
                mob.hp = current_hp
                if mob.hp <= 0:
                     mob.status = 0
                
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
            
            mob = self.mobs.get(mob_id)
            if mob:
                mob.hp = 0
                mob.status = 0
                logger.info(f"Quái vật đã CHẾT: ID={mob_id} (ST: {damage})")
                

                if self.account.char.mob_focus == mob:
                    self.account.char.mob_focus = None
            else:
                logger.warning(f"Đã nhận NPC_DIE cho MobID không xác định={mob_id}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích NPC_DIE: {e}")

    def process_player_up_exp(self, msg: Message):
        """Xử lý cập nhật EXP/Sức mạnh theo loại gói tin PLAYER_UP_EXP."""
        try:
            reader = msg.reader()
            exp_type = reader.read_byte()
            amount = reader.read_int()
            
            char = self.account.char
            if exp_type == 0: # 0 is cPower
                char.c_power += amount
            elif exp_type == 1: # 1 is cTiemNang
                char.c_tiem_nang += amount
            elif exp_type == 2: # 2 is both
                char.c_power += amount
                char.c_tiem_nang += amount
            
            logger.info(f"Người chơi tăng EXP (Cmd {msg.command}): Loại={exp_type}, Số lượng={amount}. SM Hiện tại: {char.c_power}, TN: {char.c_tiem_nang}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_UP_EXP: {e}")

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

    def process_open_ui_confirm(self, msg: Message):
        """Xử lý menu NPC (OPEN_UI_CONFIRM): đọc template id, nội dung menu và các lựa chọn."""
        try:
            reader = msg.reader()
            npc_template_id = reader.read_short()
            menu_chat = reader.read_utf()
            num_options = reader.read_byte()
            options = []
            for _ in range(num_options):
                options.append(reader.read_utf())
            
            logger.info(f"NPC Menu (Template ID {npc_template_id}): '{menu_chat}'")
            for i, opt in enumerate(options):
                logger.info(f"  [{i}] {opt}")
            
            # Pass Bo Mong NPC messages to the auto module
            if npc_template_id == 17:
                self.auto_bo_mong.handle_npc_message(menu_chat, options)
                
        except Exception as e:
            logger.error(f"Lỗi khi phân tích OPEN_UI_CONFIRM: {e}")

    def process_quest_info(self, msg: Message):
        """Xử lý thông tin nhiệm vụ (phỏng đoán từ Cmd 93)."""
        try:
            reader = msg.reader()
            # Cấu trúc của gói tin này chưa rõ, giả định nó chứa một chuỗi UTF
            # có chứa chi tiết nhiệm vụ mà AutoBoMong đang chờ.
            quest_text = reader.read_utf()
            logger.info(f"Thông tin nhiệm vụ (Cmd {msg.command}): '{quest_text}'")
            
            # Chuyển thông tin này đến AutoBoMong để xử lý
            self.auto_bo_mong.handle_npc_message(quest_text, [])
            
        except Exception as e:
            logger.error(f"Lỗi khi phân tích process_quest_info (Cmd {msg.command}): {e}")

    def process_npc_chat(self, msg: Message):
        """Ghi log nội dung chat của NPC (NPC_CHAT)."""
        try:
            reader = msg.reader()
            npc_id = reader.read_short()
            message = reader.read_utf()
            logger.info(f"NPC Chat (Cmd {msg.command}): NPC_ID={npc_id}, Nội dung='{message}'")

            # Check if this NPC is Bo Mong and pass the message
            # We need to check against the template_id stored in self.npcs
            bo_mong_template_id = 17
            npc_data = self.npcs.get(npc_id)
            if npc_data and npc_data.get('template_id') == bo_mong_template_id:
                self.auto_bo_mong.handle_npc_message(message, [])

        except Exception as e:
            logger.error(f"Lỗi khi phân tích NPC_CHAT: {e}")
            


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

    def process_player_attack_npc(self, msg: Message):
        """Xử lý sự kiện người chơi tấn công NPC (PLAYER_ATTACK_NPC)."""
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            npc_id = reader.read_byte()
            logger.info(f"Người chơi tấn công NPC (Cmd {msg.command}): PlayerID={player_id}, NPC_ID={npc_id}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích PLAYER_ATTACK_NPC: {e}")

    def process_player_die(self, msg: Message):
        """Xử lý khi một người chơi chết; nếu là nhân vật local thì thực hiện bước revive/return flow."""
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            
            if player_id == self.account.char.char_id:
                logger.warning("Nhân vật của bạn đã chết (PLAYER_DIE).")
                
                was_auto_playing = self.auto_play.interval
                was_auto_pet = self.auto_pet.is_running
                current_map_id = self.tile_map.map_id
                
                self.xmap.handle_death()
                
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
            if self.tile_map.map_id != target_map_id and self.account.char.c_hp > 0:
                logger.info("Đã hồi sinh và về nhà thành công.")
                break
            await asyncio.sleep(1)
        timeout = 20
        start_wait = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_wait < timeout:
            if self.tile_map.map_id != target_map_id and self.account.char.c_hp > 0:
                logger.info("Đã hồi sinh và về nhà thành công.")
                break
            await asyncio.sleep(1)
        
        if self.tile_map.map_id == target_map_id:
            logger.warning("Không thể về nhà sau khi chết. Hủy quy trình quay lại.")
            return

        # Quay lại map mục tiêu và cố gắng khôi phục auto
        await asyncio.sleep(2)
        await self.xmap.start(target_map_id, keep_dangerous=True)
        while self.xmap.is_xmapping:
            await asyncio.sleep(1)
        if self.tile_map.map_id == target_map_id:
            logger.info("Đã quay lại điểm cũ. Kích hoạt lại Auto...")
            if resume_auto_play:
                self.toggle_autoplay(True)
            if resume_auto_pet:
                self.toggle_auto_pet(True)
        else:
            logger.warning(f"Không thể quay lại map {target_map_id}.")

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
    def process_pet_info(self, msg: Message):
        """Đọc thông tin đệ tử (PET_INFO) và cập nhật đối tượng pet trong account."""
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
        """Xử lý thông tin thách đấu (THACHDAU) từ server."""
        try:
            reader = msg.reader()
            challenge_id = reader.read_int()
            logger.info(f"Thách đấu (Cmd {msg.command}): ChallengeID={challenge_id}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích THACHDAU: {e}")

    def process_power_info(self, msg: Message):
        """Xử lý thông tin sức mạnh (POWER_INFO -115)."""
        try:
            reader = msg.reader()
            power = reader.read_long()
            self.account.char.c_power = power
            logger.info(f"Cập nhật Sức Mạnh (Cmd {msg.command}): {power}")
            
            # Nếu còn dữ liệu, có thể là các info khác
            if reader.available() > 0:
                 # Ví dụ: vàng,ngọc...
                 pass
        except Exception as e:
            logger.error(f"Lỗi khi phân tích POWER_INFO: {e}")

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

    def process_update_data(self, msg: Message):
        """Xử lý gói tin UPDATE_DATA (-87)."""
        try:
            reader = msg.reader()
            vc_data = reader.read_byte()
            logger.info(f"UPDATE_DATA: vcData={vc_data}")
            
            def read_byte_array(r):
                length = r.read_int()
                return r.read_bytes(length)

            # Đọc các chunk dữ liệu (Dart, Arrow, Effect, Image, Part, Skill)
            # Trong C#, createData chỉ đọc đến NR_skill
            read_byte_array(reader) # dart
            read_byte_array(reader) # arrow
            read_byte_array(reader) # effect
            read_byte_array(reader) # image
            read_byte_array(reader) # part
            read_byte_array(reader) # skill
            
            # Không đọc map_data ở đây nữa vì nó nằm trong gói UPDATE_MAP (6)
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý UPDATE_DATA: {e}")

    def process_update_map(self, msg: Message):
        """Xử lý gói tin UPDATE_MAP (6) để cập nhật MobTemplate."""
        try:
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
        """Xử lý gói tin liên quan đến Mabu và ghi lại trạng thái (MABU)."""
        try:
            reader = msg.reader()
            mabu_state = reader.read_byte()
            logger.info(f"Mabu (Cmd {msg.command}): Trạng thái={mabu_state}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích MABU: {e}")

    async def eat_pea(self):
        """Tìm và ăn đậu trong hành trang khi HP/MP thấp."""
        PEAN_IDS = [595]
        char = self.account.char
        pet = self.account.pet
        needs_eat = False
        reasons = []

        # Nếu HP < 80% thì cần dùng đậu
        if char.c_hp_full > 0 and (char.c_hp / char.c_hp_full) < 0.8:
            needs_eat = True
            reasons.append(f"HP thấp ({int(char.c_hp/char.c_hp_full*100)}%)")
            
        # Nếu MP < 80% thì cần dùng đậu
        if char.c_mp_full > 0 and (char.c_mp / char.c_mp_full) < 0.8:
            needs_eat = True
            reasons.append(f"MP thấp ({int(char.c_mp/char.c_mp_full*100)}%)")


        
        if not needs_eat:
            logger.info(f"[{self.account.username}] Không cần ăn đậu (HP/MP > 80%, Thể lực > 20%).")
            return

        logger.info(f"[{self.account.username}] Quyết định ăn đậu. Lý do: {', '.join(reasons)}")

        found_index = -1
        

        if char.arr_item_bag:
            for i, item in enumerate(char.arr_item_bag):
                if item and item.item_id in PEAN_IDS:
                    found_index = i
                    break
        
        if found_index != -1:
            logger.info(f"[{self.account.username}] Sử dụng đậu thần tại vị trí {found_index}...")
            # Gọi service.use_item(0, 1, found_index, -1)
            await self.account.service.use_item(0, 1, found_index, -1)
        else:
            logger.warning(f"[{self.account.username}] Cần ăn đậu nhưng không tìm thấy trong hành trang.")

    def find_item_in_bag(self, item_id: int):
        """Tìm item trong hành trang và trả về danh sách kết quả."""
        results = []
        char = self.account.char
        if not char.arr_item_bag:
            return results
            
        for i, item in enumerate(char.arr_item_bag):
            if item and item.item_id == item_id:
                results.append(item)
        return results

    async def use_item_by_id(self, item_id: int, action_type: int):
        """
        Tìm và thực hiện hành động với item theo ID (sử dụng hoặc bán).
        Mô phỏng lại logic C#: Duyệt qua bag, nếu gặp ID thì thực hiện action.
        :param item_id: ID template của item.
        :param action_type: 0 = Sử dụng, 1 = Bán.
        """
        char = self.account.char
        if not char.arr_item_bag:
            logger.warning(f"[{self.account.username}] Hành trang chưa tải hoặc rỗng.")
            return

        found = False
        count_action = 0
        for i, item in enumerate(char.arr_item_bag):
            if item and item.item_id == item_id:
                found = True
                try:
                    if action_type == 0:
                        # Use: type=0 (bag), where=1 (me), index=i, template=-1
                        await self.account.service.use_item(0, 1, i, -1)
                        count_action += 1
                        # Delay một chút để tránh spam quá nhanh nếu có nhiều item
                        await asyncio.sleep(0.1)
                    elif action_type == 1:
                        # Sale: action=1, type=1, index=i
                        await self.account.service.sale_item(1, 1, i)
                        count_action += 1
                        await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"[{self.account.username}] Lỗi khi xử lý item {item_id} tại index {i}: {e}")
        
        if not found:
            logger.warning(f"[{self.account.username}] Không tìm thấy item ID {item_id} trong hành trang.")
        else:
            action_str = "Sử dụng" if action_type == 0 else "Bán"
            logger.info(f"[{self.account.username}] Đã gửi yêu cầu {action_str} {count_action} item ID {item_id}.")

    async def attack_nearest_mob(self):
        """Tấn công quái vật gần nhất một lần."""
        char = self.account.char
        mobs = self.mobs
        if not mobs:
            logger.warning(f"[{self.account.username}] Không có quái vật nào trong khu vực.")
            return

        closest_mob = None
        min_dist = float('inf')

        # Tìm quái gần nhất
        for mob in mobs.values():
            if mob.status == 0 or mob.hp <= 0:
                continue
            
            dist = (char.cx - mob.x)**2 + (char.cy - mob.y)**2
            if dist < min_dist:
                min_dist = dist
                closest_mob = mob

        if closest_mob:
            logger.info(f"[{self.account.username}] Tấn công quái ID {closest_mob.mob_id} (Khoảng cách: {int(min_dist**0.5)})")
            # Gửi lệnh tấn công
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
            
            # Kiểm tra HP gốc
            if char.c_hp_goc <= target_hp - 2000:
                await self.account.service.up_potential(0, 100)
                acted = True
            elif char.c_hp_goc <= target_hp - 200:
                await self.account.service.up_potential(0, 10)
                acted = True
            elif char.c_hp_goc <= target_hp - 20:
                await self.account.service.up_potential(0, 1)
                acted = True
                
            # Kiểm tra MP gốc
            if char.c_mp_goc <= target_mp - 2000:
                await self.account.service.up_potential(1, 100)
                acted = True
            elif char.c_mp_goc <= target_mp - 200:
                await self.account.service.up_potential(1, 10)
                acted = True
            elif char.c_mp_goc <= target_mp - 20:
                await self.account.service.up_potential(1, 1)
                acted = True

            # Kiểm tra Sức đánh gốc
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
            
            # Ngủ 1 chút để server kịp xử lý và tránh spam quá nhanh
            await asyncio.sleep(0.05)

    def process_the_luc(self, msg: Message):
        """Xử lý thông tin thể lực (THELUC) nhận từ server."""
        try:
            reader = msg.reader()
            the_luc_value = reader.read_short()
            logger.info(f"Thể lực (Cmd {msg.command}): Giá trị={the_luc_value}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Lỗi khi phân tích THELUC: {e}")