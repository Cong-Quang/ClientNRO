from commands.base_command import Command
from logs.logger_config import TerminalColors
from typing import Any

class LogoutCommand(Command):
    def __init__(self, manager):
        self.manager = manager
        self.C = TerminalColors

    async def execute(self, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        # logout [target]
        target = None
        if len(parts) >= 2:
            target = parts[1]
        elif self.manager.command_target is not None:
                if isinstance(self.manager.command_target, int):
                    target = str(self.manager.command_target)
                else:
                    target = self.manager.command_target
        
        if not target:
            print("Sử dụng: logout <index|list|all|group_name>")
            return False
        
        accounts_to_logout = []

        if target == "all":
            accounts_to_logout = self.manager.accounts
        
        elif target in self.manager.groups:
            indices = self.manager.groups[target]
            for idx in indices:
                    if 0 <= idx < len(self.manager.accounts):
                        accounts_to_logout.append(self.manager.accounts[idx])
        
        elif ',' in target:
            try:
                indices = [int(i.strip()) for i in target.split(',')]
                for idx in indices:
                    if 0 <= idx < len(self.manager.accounts):
                        accounts_to_logout.append(self.manager.accounts[idx])
            except ValueError:
                    print("Danh sách chỉ số không hợp lệ.")
                    return False
        
        elif target.isdigit():
            idx = int(target)
            if 0 <= idx < len(self.manager.accounts):
                accounts_to_logout.append(self.manager.accounts[idx])
            else:
                    print("Chỉ số tài khoản không hợp lệ.")
                    return False
        else:
            print(f"Không tìm thấy nhóm hoặc chỉ số '{target}'.")
            return False
        
        # Thực hiện logout
        count = 0
        for acc in accounts_to_logout:
            if acc.is_logged_in:
                print(f"Đang đăng xuất {acc.username}...")
                acc.stop()
                count += 1
        
        if count > 0:
            print(f"Đã đăng xuất {count} tài khoản.")
        else:
            print("Không có tài khoản nào đang online trong danh sách chọn.")
        return False
