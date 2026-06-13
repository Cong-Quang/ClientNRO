from targeted_commands.base_targeted_command import TargetedCommand
from logs.logger_config import logger, TerminalColors
from core.account import Account
import asyncio
from typing import Any

class AutoQuestCommand(TargetedCommand):
    """
    Bật/tắt chế độ tự động làm nhiệm vụ.
    Cú pháp: autoquest <on|off>
    """
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) > 1:
            action = parts[1].lower()
            if action == "on":
                await account.auto_main_quest.start()
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.GREEN}Đã BẬT Auto Quest{self.C.RESET}")
            elif action == "off":
                await account.auto_main_quest.stop()
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Đã TẮT Auto Quest{self.C.RESET}")
            elif action == "status":
                if hasattr(account, 'auto_main_quest'):
                    status_msg = account.auto_main_quest.get_status()
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.CYAN}{status_msg}{self.C.RESET}")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}AutoQuest chưa được khởi tạo.{self.C.RESET}")
            else:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Cú pháp: autoquest <on|off|status>")
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Cú pháp: autoquest <on|off|status>")
        return True, "OK"
