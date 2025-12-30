import logging
import asyncio
from network.message import Message
from cmd import Cmd
from network.reader import Reader
from model.map_objects import TileMap, Waypoint
from services.movement import MovementService
from logic.auto_play import AutoPlay

logger = logging.getLogger(__name__)

class Controller:
    def __init__(self):
        self.char_info = {} # Placeholder for character data
        self.map_info = {} # Placeholder for map data
        self.mobs = {} # Stores mob information
        self.tile_map = TileMap()
        self.movement = MovementService(self)
        self.auto_play = AutoPlay(self)

    def on_message(self, msg: Message):
        try:
            cmd = msg.command
            
            if cmd == Cmd.NOT_LOGIN: # -29
                self.message_not_login(msg)
            elif cmd == Cmd.NOT_MAP: # -28
                self.message_not_map(msg)
            elif cmd == Cmd.GET_SESSION_ID: # -27 (Handshake - already processed in Session)
                pass
            elif cmd == Cmd.ANDROID_PACK: # 126 (Sent by client, server response often minimal)
                logger.info(f"Received ANDROID_PACK response (Cmd {cmd}).")
            elif cmd == Cmd.SPEACIAL_SKILL: # 112
                # Example: Reads information about character's special skills
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
                # Resource. Not parsing in detail yet.
                logger.info(f"Received ITEM_BACKGROUND (Cmd {cmd}), Length: {len(msg.get_data())}")
            elif cmd == Cmd.BGITEM_VERSION: # -93
                # Resource. Not parsing in detail yet.
                logger.info(f"Received BGITEM_VERSION (Cmd {cmd}), Length: {len(msg.get_data())}")
            elif cmd == Cmd.TILE_SET: # -82
                # Resource. Not parsing in detail yet.
                logger.info(f"Received TILE_SET (Cmd {cmd}), Length: {len(msg.get_data())}")
            elif cmd == Cmd.MOB_ME_UPDATE: # -95
                 logger.info(f"Received MOB_ME_UPDATE (Cmd {cmd}).")
            elif cmd == Cmd.UPDATE_COOLDOWN: # -94
                 logger.info(f"Received UPDATE_COOLDOWN (Cmd {cmd}).")
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
            elif cmd == Cmd.SUB_COMMAND: # -30 (often subcommands inside)
                self.process_sub_command(msg)
            elif cmd == Cmd.CHANGE_FLAG: # -103
                self.process_change_flag(msg)
            elif cmd == Cmd.ME_BACK: # -15
                logger.info(f"Received ME_BACK (Cmd {cmd}).")
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
                logger.info(f"Received MAP_CLEAR (Cmd {cmd}).")
            else:
                logger.info(f"Received Unhandled Command: {cmd}, Payload Len: {len(msg.get_data())}, Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error handling message {msg.command}: {e}")
            import traceback
            traceback.print_exc()

    def message_not_login(self, msg: Message):
        try:
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            logger.info(f"NOT_LOGIN sub-command: {sub_cmd}")
            
            if sub_cmd == 2: # CLIENT_INFO / Server List Response
                server_list_str = reader.read_utf()
                logger.info(f"Received Server List/Link Info: {server_list_str}")
                
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
                        logger.info(f"Parsed Server List: {parsed_servers}")
                    else:
                        logger.warning(f"Failed to parse server list: {server_list_str}")

                    # Check for CanNapTien and AdminLink (as per C#)
                    if reader.available() > 0:
                        can_nap_tien_byte = reader.read_byte()
                        can_nap_tien = (can_nap_tien_byte == 1)
                        logger.info(f"Can Nap Tien: {can_nap_tien}")
                        
                        if reader.available() > 0:
                            admin_link_byte = reader.read_byte()
                            admin_link = admin_link_byte # C# used sbyte for this
                            logger.info(f"Admin Link: {admin_link}")

                except Exception as parse_e:
                    logger.warning(f"Error parsing full server list message: {parse_e}")


            elif sub_cmd == Cmd.LOGINFAIL: # -102
                reason = reader.read_utf()
                logger.error(f"Login Failed: {reason}")
                
            elif sub_cmd == Cmd.LOGIN_DE: # 122
                logger.info("Login DE received (Session/User info might be here).")
            
            elif sub_cmd == Cmd.LOGIN: # 0 (Usually implies success if receiving data?)
                logger.info("NOT_LOGIN sub-command 0 received. (Login/Character data expected).")
                # Need further analysis of C# Controller.messageNotLogin for sub 0
                
            else:
                logger.info(f"Received unhandled NOT_LOGIN sub-command: {sub_cmd}, Payload Hex: {msg.get_data().hex()}")
                
        except Exception as e:
            logger.error(f"Error parsing NOT_LOGIN: {e}")
            import traceback
            traceback.print_exc()

    def message_not_map(self, msg: Message):
        try:
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            logger.info(f"NOT_MAP sub-command: {sub_cmd}")

            if sub_cmd == 4: # UPDATE_VERSION / Login Success trigger?
                logger.info("Login Success! Server requesting version check.")
                
                vsData = reader.read_byte()
                vsMap = reader.read_byte()
                vsSkill = reader.read_byte()
                vsItem = reader.read_byte()
                logger.info(f"Server Versions - Data: {vsData}, Map: {vsMap}, Skill: {vsSkill}, Item: {vsItem}")
                
            else:
                logger.info(f"Received unhandled NOT_MAP sub-command: {sub_cmd}, Payload Hex: {msg.get_data().hex()}")

        except Exception as e:
            logger.error(f"Error parsing NOT_MAP: {e}")
            import traceback
            traceback.print_exc()

    def process_task_get(self, msg: Message):
        try:
            reader = msg.reader()
            task_id = reader.read_short()
            task_name = reader.read_utf()
            task_details = reader.read_utf()
            logger.info(f"Task Received (Cmd {msg.command}): ID={task_id}, Name='{task_name}', Details='{task_details}'")
        except Exception as e:
            logger.error(f"Error parsing TASK_GET: {e}")

    def process_game_info(self, msg: Message):
        try:
            reader = msg.reader()
            info_text = reader.read_utf()
            logger.info(f"Game Info (Cmd {msg.command}): '{info_text}'")
        except Exception as e:
            logger.error(f"Error parsing GAME_INFO: {e}")

    def process_map_info(self, msg: Message):
        try:
            reader = msg.reader()
            
            # Map Header (Matches Controller.cs case -24)
            map_id = reader.read_ubyte()
            planet_id = reader.read_byte()
            tile_id = reader.read_byte()
            bg_id = reader.read_byte()
            type_map = reader.read_byte()
            map_name = reader.read_utf()
            zone_id = reader.read_byte()
            
            logger.info(f"Map Info (Cmd {msg.command}): ID={map_id}, Name='{map_name}', Planet={planet_id}, Zone={zone_id}")
            self.map_info = {'id': map_id, 'name': map_name, 'planet': planet_id, 'zone': zone_id}
            
            # Update TileMap
            self.tile_map = TileMap() # Reset
            self.tile_map.set_map_info(map_id, planet_id, tile_id, bg_id, type_map, map_name, zone_id)

            # loadInfoMap (Matches Controller.cs loadInfoMap)
            cx = reader.read_short()
            cy = reader.read_short()
            
            # Update char pos
            from model.game_objects import Char, Mob
            Char.my_charz().cx = cx
            Char.my_charz().cy = cy
            Char.my_charz().map_id = map_id
            
            # Waypoints
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
                logger.debug(f"Parsed Waypoint: {name} (Ent:{is_enter}, Off:{is_offline})")
            
            # Mobs
            self.mobs = {} 
            num_mobs = reader.read_ubyte()
            logger.info(f"Mobs on map: {num_mobs}")
            
            for i in range(num_mobs):
                # Matches Mob constructor in Controller.cs
                is_disable = reader.read_bool()
                is_dont_move = reader.read_bool()
                is_fire = reader.read_bool()
                is_ice = reader.read_bool()
                is_wind = reader.read_bool()
                
                template_id = reader.read_ubyte()
                sys = reader.read_byte()
                hp = reader.read_int() # C# uses readInt() (4 bytes) here
                level = reader.read_byte()
                max_hp = reader.read_int() # C# uses readInt() (4 bytes) here
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
            
            logger.info(f"Parsed {len(self.mobs)} mobs.")
            
            # Start Auto Play (Attack)
            logger.info("MAP_INFO received. Starting AutoPlay...")
            self.auto_play.start()

        except Exception as e:
            logger.error(f"Error parsing MAP_INFO: {e}")
            import traceback
            traceback.print_exc()

    def process_npc_live(self, msg: Message):
        try:
            reader = msg.reader()
            mob_id = reader.read_ubyte()
            
            # Validation
            if mob_id not in self.mobs:
                logger.warning(f"NPC_LIVE: Unknown Mob ID {mob_id}")
                return

            mob = self.mobs[mob_id]
            
            # C# Logic:
            # mob.sys = msg.reader().readByte();
            # mob.levelBoss = msg.reader().readByte();
            # mob.hp = msg.reader().readInt();
            
            mob.sys = reader.read_byte()
            mob.level_boss = reader.read_byte()
            mob.hp = reader.read_int()
            
            # Reset
            mob.status = 5 # Alive
            mob.max_hp = mob.hp # Usually reset to max on respawn
            mob.x = mob.x_first
            mob.y = mob.y_first
            
            logger.info(f"Mob RESPAWN: ID={mob_id} | HP={mob.hp} | Pos=({mob.x},{mob.y})")
            
        except Exception as e:
            logger.error(f"Error parsing NPC_LIVE: {e}")
            import traceback
            traceback.print_exc()

    def process_me_load_point(self, msg: Message):
        try:
            reader = msg.reader()
            hp_goc = reader.read_int3()
            mp_goc = reader.read_int3()
            dam_goc = reader.read_int()
            hp_full = reader.read_int3()
            mp_full = reader.read_int3()
            hp = reader.read_int3()
            mp = reader.read_int3()
            
            speed = reader.read_byte()
            hp_from_1000 = reader.read_byte()
            mp_from_1000 = reader.read_byte()
            dam_from_1000 = reader.read_byte()
            
            dam_full = reader.read_int()
            def_full = reader.read_int()
            crit_full = reader.read_byte()
            potential = reader.read_long()
            
            logger.info(f"Character Stats (Cmd {msg.command}): HP={hp}/{hp_full}, MP={mp}/{mp_full}, Potential={potential}, Dam={dam_full}")
            self.char_info.update({
                'hp': hp, 'max_hp': hp_full, 
                'mp': mp, 'max_mp': mp_full, 
                'potential': potential, 'damage': dam_full
            })
        except Exception as e:
            logger.error(f"Error parsing ME_LOAD_POINT: {e}")

    def process_bag_info(self, msg: Message):
        try:
            reader = msg.reader()
            action = reader.read_byte()
            logger.info(f"Bag Info (Cmd {msg.command}): Action={action}, Payload Hex: {msg.get_data().hex()}")
            # This is complex, usually list of items etc.
        except Exception as e:
            logger.error(f"Error parsing BAG_INFO: {e}")
            
    def process_special_skill(self, msg: Message):
        try:
            reader = msg.reader()
            special_type = reader.read_byte()
            if special_type == 0:
                img_id = reader.read_short()
                info = reader.read_utf()
                logger.info(f"Special Skill (Cmd {msg.command}): Type={special_type}, ImgID={img_id}, Info='{info}'")
            elif special_type == 1:
                # More complex parsing for skill lists
                logger.info(f"Special Skill (Cmd {msg.command}): Type={special_type} (list), Payload Hex: {msg.get_data().hex()}")
            else:
                logger.info(f"Special Skill (Cmd {msg.command}): Unknown Type={special_type}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error parsing SPEACIAL_SKILL: {e}")

    def process_player_add(self, msg: Message):
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            clan_id = reader.read_int()
            
            # Use helper to read char info
            char_data = self.read_char_info(reader)
            char_data['id'] = player_id
            char_data['clan_id'] = clan_id
            
            logger.info(f"Player Added (Cmd {msg.command}): ID={player_id}, Name='{char_data.get('name')}', Pos=({char_data.get('x')},{char_data.get('y')})")
        except Exception as e:
            logger.error(f"Error parsing PLAYER_ADD: {e}")

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
        reader.read_byte() # unused/reserved
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
            logger.info(f"Player Move (Cmd {msg.command}): ID={player_id}, X={x}, Y={y}")
        except Exception as e:
            logger.error(f"Error parsing PLAYER_MOVE: {e}")

    def process_mob_hp(self, msg: Message):
        try:
            reader = msg.reader()
            mob_id = reader.read_ubyte() 
            current_hp = reader.read_int3() 
            damage = reader.read_int3() 
            
            # Optional extra data (crit, effect) - consuming to be safe
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
                     mob.status = 0 # Mark as dead if HP 0, though NPC_DIE usually confirms it
                
                logger.info(f"Mob Update: ID={mob_id} | HP: {old_hp} -> {current_hp}/{mob.max_hp} (Dmg: {damage})")
            else:
                logger.warning(f"Received MOB_HP for unknown MobID={mob_id}. HP={current_hp}")
                
        except Exception as e:
            logger.error(f"Error parsing MOB_HP: {e}")

    def process_npc_die(self, msg: Message):
        try:
            reader = msg.reader()
            mob_id = reader.read_ubyte()
            damage = reader.read_int3()
            # isCrit = reader.read_bool() # unused
            
            mob = self.mobs.get(mob_id)
            if mob:
                mob.hp = 0
                mob.status = 0 # Dead
                logger.info(f"Mob DIED: ID={mob_id} (Dmg: {damage})")
                
                # Clear focus if it was this mob
                from model.game_objects import Char
                if Char.my_charz().mob_focus == mob:
                    Char.my_charz().mob_focus = None
            else:
                logger.warning(f"Received NPC_DIE for unknown MobID={mob_id}")
        except Exception as e:
            logger.error(f"Error parsing NPC_DIE: {e}")

    def process_player_up_exp(self, msg: Message):
        try:
            reader = msg.reader()
            # C#: sbyte b73 = msg.reader().readByte();
            # C#: int num181 = msg.reader().readInt();
            exp_type = reader.read_byte()
            amount = reader.read_int()
            logger.info(f"Player EXP Up (Cmd {msg.command}): Type={exp_type}, Amount={amount}")
        except Exception as e:
            logger.error(f"Error parsing PLAYER_UP_EXP: {e}")

    def process_message_time(self, msg: Message):
        try:
            reader = msg.reader()
            time_id = reader.read_byte()
            message = reader.read_utf()
            duration = reader.read_short()
            logger.info(f"Message Time (Cmd {msg.command}): ID={time_id}, Msg='{message}', Duration={duration}s")
        except Exception as e:
            logger.error(f"Error parsing MESSAGE_TIME: {e}")

    def process_npc_chat(self, msg: Message):
        try:
            reader = msg.reader()
            npc_id = reader.read_short()
            message = reader.read_utf()
            logger.info(f"NPC Chat (Cmd {msg.command}): NPC_ID={npc_id}, Chat='{message}'")
        except Exception as e:
            logger.error(f"Error parsing NPC_CHAT: {e}")
            
    def process_sub_command(self, msg: Message):
        try:
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            logger.info(f"SUB_COMMAND (Cmd {msg.command}) sub-command: {sub_cmd}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error parsing SUB_COMMAND: {e}")

    def process_change_flag(self, msg: Message):
        try:
            reader = msg.reader()
            char_id = reader.read_int()
            flag_id = 0
            if reader.available() > 0:
                flag_id = reader.read_byte()
            logger.info(f"Change Flag (Cmd {msg.command}): CharID={char_id}, FlagID={flag_id}")
        except Exception as e:
            logger.error(f"Error parsing CHANGE_FLAG: {e}")

    def process_player_attack_npc(self, msg: Message):
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            # NPC ID is likely a short (2 bytes) based on log analysis (Payload 6 bytes: 4 + 2)
            npc_id = reader.read_byte() # Usually Mob ID is byte? Or Short?
            # Cmd 54 payload: write_byte(mobId) in Service.
            # But response might include player ID?
            # Let's peek payload.
            # logger.info(f"ATTACK_NPC Payload: {msg.get_data().hex()}")
            # Re-reading based on C# logic if available...
            # But for now, just log what we can.
            logger.info(f"Player Attack NPC (Cmd {msg.command}): PlayerID={player_id}, NPC_ID={npc_id}")
        except Exception as e:
            logger.error(f"Error parsing PLAYER_ATTACK_NPC: {e}")

    def process_player_die(self, msg: Message):
        try:
            reader = msg.reader()
            player_id = reader.read_int()
            logger.info(f"Player Died (Cmd {msg.command}): PlayerID={player_id}")
        except Exception as e:
            logger.error(f"Error parsing PLAYER_DIE: {e}")

    def process_max_stamina(self, msg: Message):
        try:
            reader = msg.reader()
            max_stamina = reader.read_short()
            logger.info(f"Max Stamina (Cmd {msg.command}): {max_stamina}")
        except Exception as e:
            logger.error(f"Error parsing MAXSTAMINA: {e}")

    def process_stamina(self, msg: Message):
        try:
            reader = msg.reader()
            stamina = reader.read_short()
            logger.info(f"Current Stamina (Cmd {msg.command}): {stamina}")
        except Exception as e:
            logger.error(f"Error parsing STAMINA: {e}")

    def process_update_active_point(self, msg: Message):
        try:
            reader = msg.reader()
            active_point = reader.read_int()
            logger.info(f"Update Active Point (Cmd {msg.command}): {active_point}")
        except Exception as e:
            logger.error(f"Error parsing UPDATE_ACTIVEPOINT: {e}")

    def process_map_offline(self, msg: Message):
        try:
            reader = msg.reader()
            map_id = reader.read_int()
            time_offline = 0
            if reader.available() > 0:
                time_offline = reader.read_int()
            logger.info(f"Map Offline (Cmd {msg.command}): MapID={map_id}, TimeOffline={time_offline}s")
        except Exception as e:
            logger.error(f"Error parsing MAP_OFFLINE: {e}")

    def process_pet_info(self, msg: Message):
        try:
            reader = msg.reader()
            pet_type = reader.read_byte() # Example field, needs C# source for full structure
            logger.info(f"Pet Info (Cmd {msg.command}): Type={pet_type}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error parsing PET_INFO: {e}")

    def process_thach_dau(self, msg: Message):
        try:
            reader = msg.reader()
            challenge_id = reader.read_int() # Example field
            logger.info(f"Thach Dau (Cmd {msg.command}): ChallengeID={challenge_id}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error parsing THACHDAU: {e}")

    def process_autoplay(self, msg: Message):
        try:
            reader = msg.reader()
            auto_mode = reader.read_byte() # Example field
            logger.info(f"Autoplay (Cmd {msg.command}): Mode={auto_mode}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error parsing AUTOPLAY: {e}")

    def process_mabu(self, msg: Message):
        try:
            reader = msg.reader()
            mabu_state = reader.read_byte() # Example field
            logger.info(f"Mabu (Cmd {msg.command}): State={mabu_state}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error parsing MABU: {e}")

    def process_the_luc(self, msg: Message):
        try:
            reader = msg.reader()
            the_luc_value = reader.read_short() # Example field
            logger.info(f"The Luc (Cmd {msg.command}): Value={the_luc_value}, Payload Hex: {msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error parsing THELUC: {e}")