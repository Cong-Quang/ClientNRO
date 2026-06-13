from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from logs.logger_config import TerminalColors

class TansatCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) > 1:
            sub = parts[1].lower()
            if sub == "start":
                account.controller.toggle_autoplay(True)
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã {self.C.BRIGHT_GREEN}BẬT{self.C.RESET} tàn sát.")
            elif sub == "off":
                account.controller.toggle_autoplay(False)
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã {self.C.RED}TẮT{self.C.RESET} tàn sát.")
            elif sub == "clear":
                account.controller.auto_play.target_mobs.clear()
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã xóa danh sách mục tiêu tàn sát (Sẽ đánh tất cả).")
            elif sub == "list":
                current = account.controller.auto_play.target_mobs
                if current:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Danh sách ID quái tàn sát: {current}")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Danh sách tàn sát trống (Đánh tất cả).")
            elif sub.isdigit() or (sub.startswith("-") and sub[1:].isdigit()):
                # Add ID to list (supports negative IDs if needed, though template IDs are usually positive)
                mob_id = int(sub)
                account.controller.auto_play.target_mobs.add(mob_id)
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã thêm quái ID (Template ID) {mob_id} vào danh sách tàn sát.")
            else:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Lệnh tàn sát không hợp lệ: {sub}")
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: tansat <start|off|clear|list|id_quái>")
        return True, "OK"
