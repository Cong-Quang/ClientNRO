from targeted_commands.base_targeted_command import TargetedCommand
from logs.logger_config import logger, TerminalColors
from core.account import Account
import asyncio
from typing import Any

class ScanMapCommand(TargetedCommand):
    """
    Quét danh sách quái vật trong một khoảng Map ID và tự động lưu vào maps_config.json.
    Cú pháp: scanmap <start_id> <end_id> | stop
    """
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) == 2 and parts[1].lower() == "stop":
            await account.auto_scanmap.stop()
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Đã TẮT ScanMap{self.C.RESET}")
            return True, "OK"
            
        if len(parts) >= 2:
            try:
                start_id = int(parts[1])
                # Nếu chỉ truyền 1 tham số, start và end giống nhau
                end_id = start_id if len(parts) == 2 else int(parts[2])
                
                if not hasattr(account, 'auto_scanmap'):
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Lỗi: Tính năng ScanMap chưa được khởi tạo.")
                    return False, "Not initialized"
                    
                await account.auto_scanmap.start(start_id, end_id)
                if start_id == end_id:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.GREEN}Đã BẬT ScanMap cho Map {start_id}{self.C.RESET}")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.GREEN}Đã BẬT ScanMap từ {start_id} đến {end_id}{self.C.RESET}")
                return True, "OK"
            except ValueError:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Lỗi: ID map phải là số.")
                
        print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Cú pháp: scanmap <map_id> | scanmap <start_id> <end_id> | scanmap stop")
        return True, "OK"
