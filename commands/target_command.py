from commands.base_command import Command
from logs.logger_config import logger, TerminalColors
from typing import Any

class TargetCommand(Command):
    def __init__(self, manager):
        self.manager = manager
        self.C = TerminalColors

    async def execute(self, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) != 2:
            print("Sử dụng: target <index|group_name|all>")
            return False
        
        new_target = parts[1]
        if new_target.isdigit():
            new_target_idx = int(new_target)
            if 0 <= new_target_idx < len(self.manager.accounts):
                self.manager.command_target = new_target_idx
                print(f"Đã đặt mục tiêu là tài khoản [{self.C.YELLOW}{new_target_idx}{self.C.RESET}].")
            else:
                print("Chỉ số tài khoản không hợp lệ.")
        elif new_target in self.manager.groups:
            self.manager.command_target = new_target
            print(f"Đã đặt mục tiêu là nhóm '{self.C.YELLOW}{new_target}{self.C.RESET}'.")
        else:
            print(f"Không tìm thấy tài khoản hoặc nhóm với tên/chỉ số '{new_target}'.")
            
        return False
