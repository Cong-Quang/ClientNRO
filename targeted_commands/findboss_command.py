from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from logs.logger_config import TerminalColors
import asyncio

class FindbossCommand(TargetedCommand):
    """Lệnh tìm và liệt kê tất cả boss/chars trong map hiện tại"""
    
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        """
        Liệt kê tất cả characters (bao gồm bosses) trong map hiện tại.
        Yêu cầu cập nhật vị trí từ server trước khi hiển thị.
        """
        # Request cập nhật vị trí từ server (Cmd 18)
        await account.service.request_players()
        await asyncio.sleep(0.5)  # Đợi server response
        
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
        
        return True, "OK"
