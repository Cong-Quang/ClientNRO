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
            
            else:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Lệnh show con không xác định: {sub}")
        else:
            # Default show status
            display_character_status(account, compact=compact_mode, idx=idx)
        return True, "OK"
