from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from logs.logger_config import TerminalColors
import asyncio

class UseitemCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) < 2:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Cú pháp: useitem <id> [số lượng]")
            return False, "Thiếu tham số"

        try:
            item_id = int(parts[1])
            quantity = 1
            if len(parts) >= 3:
                quantity = int(parts[2])
                
            char = account.char
            if getattr(char, 'arr_item_bag', None) is None:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Hành trang chưa tải!")
                return False, "Hành trang trống"

            # Tìm item trong hành trang
            found_index = -1
            for i, item in enumerate(char.arr_item_bag):
                if item and item.item_id == item_id:
                    found_index = i
                    break
                    
            if found_index == -1:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Không tìm thấy item ID {item_id} trong hành trang.")
                return False, "Không tìm thấy item"

            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Bắt đầu dùng item ID {item_id} số lượng {quantity} lần...")
            
            # Thực hiện vòng lặp dùng item
            for i in range(quantity):
                if not account.is_logged_in:
                    break
                    
                # Gửi bản tin dùng item tới server
                await account.service.use_item(0, 1, found_index, -1)
                
                # Chờ 0.1s giữa các lần dùng theo yêu cầu
                if i < quantity - 1:
                    await asyncio.sleep(0.1)

            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã gửi xong lệnh dùng {quantity} lần item ID {item_id} tại ô số {found_index}.")
            return True, "OK"
            
        except ValueError:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Tham số <id> hoặc [số lượng] phải là số.")
            return False, "Tham số không hợp lệ"
