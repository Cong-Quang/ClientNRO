from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from logs.logger_config import TerminalColors
from ui import display_character_status, display_character_base_stats, display_task_info, Box, display_boss_list
import asyncio
from logic.boss_manager import BossManager

class ShowCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        compact_mode = kwargs.get('compact_mode', False)
        idx = kwargs.get('idx')

        if len(parts) > 1:
            sub = parts[1].lower()
            if sub == "csgoc":
                    await account.service.request_me_info()
                    await asyncio.sleep(0.2)
                    from ui import display_character_base_stats
                    display_character_base_stats(account, compact=compact_mode, idx=idx)
            
            elif sub == "nhiemvu":
                    await account.service.request_task_info()
                    await asyncio.sleep(0.5)
                    from ui import display_task_info
                    return True, display_task_info(account, compact=compact_mode, idx=idx, print_output=False)
            
            elif sub == "boss":
                bosses = BossManager().get_bosses()
                display_boss_list(bosses)
            
            elif sub == "findboss":
                # Request cập nhật vị trí từ server trước
                await account.service.request_players()
                await asyncio.sleep(0.5)
                
                # Hiển thị danh sách boss/chars trong map hiện tại
                chars = account.controller.chars
                
                if not chars:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Không có character/boss nào trong map.")
                    return
                
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.CYAN}--- Danh sách Boss/Chars trong Map ---{self.C.RESET}")
                print(f"{self.C.PURPLE}{'ID':<8} | {'Tên':<25} | {'HP':<18} | {'Level':<5} | {'Vị trí (X,Y)':<15}{self.C.RESET}")
                print("-" * 90)
                
                for char_id, char_data in chars.items():
                    char_name = char_data.get('name', 'Unknown')
                    hp = char_data.get('hp', 0)
                    max_hp = char_data.get('max_hp', 0)
                    level = char_data.get('level', '?')
                    x = char_data.get('x', 0)
                    y = char_data.get('y', 0)
                    
                    hp_text = f"{hp}/{max_hp}"
                    pos_text = f"({x}, {y})"
                    
                    # Highlight if HP is low (potential boss fight)
                    if hp < max_hp:
                        char_name_colored = f"{self.C.RED}{char_name}{self.C.RESET}"
                    else:
                        char_name_colored = f"{self.C.GREEN}{char_name}{self.C.RESET}"
                    
                    print(f"{char_id:<8} | {char_name_colored:<34} | {hp_text:<18} | {level:<5} | {pos_text:<15}")
                
                print(f"\n{self.C.CYAN}Tổng số: {len(chars)} character(s){self.C.RESET}")

            elif sub == "mobs":
                mobs = account.controller.mobs
                if not mobs:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Không có quái nào trong map.")
                else:
                    B = Box
                    print()
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.CYAN}=== Danh sách Quái trong Map ==={self.C.RESET}")
                    print(f"{self.C.PURPLE}{B.TL}{B.H * 75}{B.TR}{self.C.RESET}")
                    print(f"{self.C.PURPLE}{B.V}{self.C.RESET} {self.C.BOLD}{'ID (Type/Mob)':<15} {'Tên quái':<20} {'HP':<20} {'Trạng thái':<15}{self.C.RESET} {self.C.PURPLE}{B.V}{self.C.RESET}")
                    print(f"{self.C.PURPLE}{B.LT}{B.H * 75}{B.RT}{self.C.RESET}")
                    
                    for mob_id, mob_data in mobs.items():
                        name = mob_data.name if getattr(mob_data, 'name', None) else f"Quái {mob_data.template_id}"
                        hp = getattr(mob_data, 'hp', 0)
                        max_hp = getattr(mob_data, 'max_hp', 0)
                        status = getattr(mob_data, 'status', 0)
                        template_id = getattr(mob_data, 'template_id', 0)
                        
                        id_display = f"{template_id}/{mob_id}"
                        hp_display = f"{hp:,}/{max_hp:,}" if max_hp > 0 else str(hp)
                        status_str = "Sống" if status > 1 else ("Chết" if status <= 1 else str(status))
                        
                        print(f"{self.C.PURPLE}{B.V}{self.C.RESET} {self.C.CYAN}{id_display:<15}{self.C.RESET} {self.C.GREEN}{name:<20}{self.C.RESET} {self.C.RED}{hp_display:<20}{self.C.RESET} {self.C.YELLOW}{status_str:<15}{self.C.RESET} {self.C.PURPLE}{B.V}{self.C.RESET}")
                    
                    print(f"{self.C.PURPLE}{B.BL}{B.H * 75}{B.BR}{self.C.RESET}")
                    print(f"Tổng số quái: {self.C.BRIGHT_GREEN}{len(mobs)}{self.C.RESET}")
                    print()

            elif sub == "finfomap":
                # Hiển thị danh sách tất cả người chơi trong map hiện tại
                chars = account.controller.chars
                if not chars:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Không có người chơi nào khác trong map hiện tại.")
                else:
                    # Lọc chỉ lấy người chơi thật (loại bỏ boss/entity lạ)
                    # Boss thường có ID âm, tên lạ, hoặc HP/level bất thường
                    real_players = {}
                    for player_id, player_data in chars.items():
                        name = player_data.get('name', '').strip()
                        level = player_data.get('level', 0)
                        hp = player_data.get('hp', 0)
                        max_hp = player_data.get('max_hp', 0)
                        
                        # Filter: Bỏ qua nếu:
                        # - ID âm (thường là boss)
                        # - Tên rỗng hoặc chỉ có ký tự đặc biệt
                        # - Level = 1 và HP quá cao (boss giả dạng)
                        # - HP hoặc max_hp = 0 (dữ liệu lỗi)
                        if player_id < 0:
                            continue
                        if not name or len(name) < 2 or name == "$":
                            continue
                        if level == 1 and max_hp > 100000:  # Boss thường có HP cực cao ở level 1
                            continue
                        if hp == 0 and max_hp == 0:
                            continue
                            
                        real_players[player_id] = player_data
                    
                    if not real_players:
                        print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Không có người chơi nào khác trong map hiện tại.")
                        print(f"{self.C.DIM}(Có {len(chars)} entity khác - có thể là boss/NPC){self.C.RESET}")
                    else:
                        B = Box
                        print()
                        print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.CYAN}=== Danh sách người chơi trong Map ==={self.C.RESET}")
                        print(f"{self.C.PURPLE}{B.TL}{B.H * 100}{B.TR}{self.C.RESET}")
                        print(f"{self.C.PURPLE}{B.V}{self.C.RESET} {self.C.BOLD}{'ID':<10} {'Tên':<20} {'Lv':<5} {'HP':<25} {'Vị trí':<15} {'Clan ID':<10}{self.C.RESET} {self.C.PURPLE}{B.V}{self.C.RESET}")
                        print(f"{self.C.PURPLE}{B.LT}{B.H * 100}{B.RT}{self.C.RESET}")
                        
                        for player_id, player_data in real_players.items():
                            name = player_data.get('name', 'N/A')
                            level = player_data.get('level', 0)
                            hp = player_data.get('hp', 0)
                            max_hp = player_data.get('max_hp', 0)
                            x = player_data.get('x', 0)
                            y = player_data.get('y', 0)
                            clan_id = player_data.get('clan_id', -1)
                            
                            hp_display = f"{hp:,}/{max_hp:,}"  # Format với dấu phẩy
                            pos_display = f"({x}, {y})"
                            clan_display = str(clan_id) if clan_id != -1 else "None"
                            
                            print(f"{self.C.PURPLE}{B.V}{self.C.RESET} {self.C.CYAN}{player_id:<10}{self.C.RESET} {self.C.GREEN}{name:<20}{self.C.RESET} {self.C.YELLOW}{level:<5}{self.C.RESET} {hp_display:<25} {pos_display:<15} {clan_display:<10} {self.C.PURPLE}{B.V}{self.C.RESET}")
                        
                        print(f"{self.C.PURPLE}{B.BL}{B.H * 100}{B.BR}{self.C.RESET}")
                        print(f"Tổng số người chơi: {self.C.BRIGHT_GREEN}{len(real_players)}{self.C.RESET}")
                        if len(chars) > len(real_players):
                            print(f"{self.C.DIM}(+ {len(chars) - len(real_players)} entity khác - có thể là boss/NPC){self.C.RESET}")
                        print()
            
            elif sub == "balo":
                char = account.char
                B = Box
                print()
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.CYAN}=== Hành Trang & Rương ==={self.C.RESET}")
                
                # Hàm helper in danh sách item
                def print_items(items_list, title):
                    print(f"{self.C.PURPLE}{B.TL}{B.H * 85}{B.TR}{self.C.RESET}")
                    print(f"{self.C.PURPLE}{B.V}{self.C.RESET} {self.C.BOLD}{title:<84}{self.C.RESET}{self.C.PURPLE}{B.V}{self.C.RESET}")
                    print(f"{self.C.PURPLE}{B.V}{self.C.RESET} {self.C.BOLD}{'Ô':<5} {'ID':<8} {'Tên Item':<25} {'Số lượng':<12} {'Thông tin (Info)':<31}{self.C.RESET} {self.C.PURPLE}{B.V}{self.C.RESET}")
                    print(f"{self.C.PURPLE}{B.LT}{B.H * 85}{B.RT}{self.C.RESET}")
                    
                    count = 0
                    if items_list:
                        from model.game_objects import ITEM_TEMPLATES
                        for i, item in enumerate(items_list):
                            if item is not None:
                                count += 1
                                item_name = ITEM_TEMPLATES.get(item.item_id, "")
                                if len(item_name) > 23:
                                    item_name = item_name[:20] + "..."
                                info_str = getattr(item, 'info', '').replace('\n', ' | ')
                                if len(info_str) > 30:
                                    info_str = info_str[:27] + "..."
                                qty_str = f"{item.quantity:,}"
                                print(f"{self.C.PURPLE}{B.V}{self.C.RESET} {self.C.CYAN}{i:<5}{self.C.RESET} {self.C.YELLOW}{item.item_id:<8}{self.C.RESET} {self.C.BRIGHT_GREEN}{item_name:<25}{self.C.RESET} {self.C.GREEN}{qty_str:<12}{self.C.RESET} {info_str:<31} {self.C.PURPLE}{B.V}{self.C.RESET}")
                    
                    if count == 0:
                        print(f"{self.C.PURPLE}{B.V}{self.C.RESET} {self.C.DIM}{'Trống':<84}{self.C.RESET}{self.C.PURPLE}{B.V}{self.C.RESET}")
                        
                    print(f"{self.C.PURPLE}{B.BL}{B.H * 85}{B.BR}{self.C.RESET}")

                print_items(char.arr_item_bag, f"Hành Trang (Bag) - {len([i for i in getattr(char, 'arr_item_bag', []) if i])} món")
                print()
                print_items(getattr(char, 'arr_item_box', []), f"Rương Đồ (Box) - {len([i for i in getattr(char, 'arr_item_box', []) if i])} món")
                print()

            else:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Lệnh show con không xác định: {sub}")
        else:
            # Default show status
            display_character_status(account, compact=compact_mode, idx=idx)
        return True, "OK"
