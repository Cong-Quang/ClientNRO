from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from config import Config

class BlacklistCommand(TargetedCommand):
    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) == 1:
            print("Sử dụng: blacklist <list|add|remove|clear>")
        else:
            sub = parts[1]
            if sub == "list":
                print(f"Blacklist: {Config.LOGIN_BLACKLIST}")
            elif sub == "add" and len(parts) == 3:
                val = parts[2]
                try:
                    v = int(val)
                except ValueError:
                    v = val
                if v in Config.LOGIN_BLACKLIST:
                    print(f"Đã có trong blacklist: {v}")
                else:
                    Config.LOGIN_BLACKLIST.append(v)
                    print(f"Đã thêm vào blacklist: {v}")
            elif sub == "remove" and len(parts) == 3:
                val = parts[2]
                try:
                    v = int(val)
                except ValueError:
                    v = val
                if v in Config.LOGIN_BLACKLIST:
                    Config.LOGIN_BLACKLIST.remove(v)
                    print(f"Đã xóa khỏi blacklist: {v}")
                else:
                    print(f"Không có trong blacklist: {v}")
            elif sub == "clear":
                Config.LOGIN_BLACKLIST.clear()
                print("Đã xóa toàn bộ blacklist.")
            else:
                print("Sử dụng: blacklist <list|add|remove|clear>")
        return True, "OK"
