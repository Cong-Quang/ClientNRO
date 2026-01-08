from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from logs.logger_config import TerminalColors

class AutoitemCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        
        if len(parts) < 2:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng:")
            print(f"  autoitem on <item_id>  - Bật auto-item với ID item")
            print(f"  autoitem off           - Tắt auto-item")
            print(f"  autoitem status        - Xem trạng thái")
            return True, "OK"
        
        subcommand = parts[1].lower()
        
        if subcommand == "on":
            if len(parts) < 3:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Lỗi: Cần chỉ định item ID{self.C.RESET}")
                print(f"  Sử dụng: autoitem on <item_id>")
                return False, "Missing item_id"
            
            try:
                item_id = int(parts[2])
                
                # Check if item exists in bag
                found = False
                for item in account.char.arr_item_bag:
                    if item and item.item_id == item_id:
                        found = True
                        break
                
                if not found:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Cảnh báo: Không tìm thấy item ID {item_id} trong túi đồ{self.C.RESET}")
                    print(f"  Vẫn sẽ bật Auto-Item. Hãy đảm bảo item có trong túi.")
                
                account.controller.toggle_auto_item(True, item_id)
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.GREEN}Đã BẬT Auto-Item với item ID: {item_id}{self.C.RESET}")
                print(f"  Item sẽ được sử dụng mỗi 30 phút")
                
            except ValueError:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Lỗi: Item ID phải là số nguyên{self.C.RESET}")
                return False, "Invalid item_id"
        
        elif subcommand == "off":
            account.controller.toggle_auto_item(False, None)
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Đã TẮT Auto-Item{self.C.RESET}")
        
        elif subcommand == "status":
            status = account.controller.auto_item.get_status()
            
            if status["running"]:
                next_use_minutes = status["next_use_seconds"] // 60
                next_use_seconds = status["next_use_seconds"] % 60
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Auto-Item Status:")
                print(f"  Trạng thái: {self.C.GREEN}ĐANG CHẠY{self.C.RESET}")
                print(f"  Item ID: {self.C.CYAN}{status['item_id']}{self.C.RESET}")
                print(f"  Sử dụng tiếp theo sau: {self.C.CYAN}{next_use_minutes}m {next_use_seconds}s{self.C.RESET}")
            else:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Auto-Item Status:")
                print(f"  Trạng thái: {self.C.RED}ĐANG TẮT{self.C.RESET}")
        
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Lệnh không hợp lệ: {subcommand}{self.C.RESET}")
            print(f"  Sử dụng: autoitem <on|off|status>")
            return False, "Invalid subcommand"
        
        return True, "OK"
