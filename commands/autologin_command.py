from commands.base_command import Command
from config import Config
from logs.logger_config import TerminalColors

class AutoLoginCommand(Command):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, *args, **kwargs) -> bool:
        parts = kwargs.get('parts', [])
        
        if len(parts) > 1 and parts[1] in ["on", "off"]:
            status = parts[1] == "on"
            Config.AUTO_LOGIN = status
            status_text = f"{self.C.GREEN}BẬT{self.C.RESET}" if status else f"{self.C.RED}TẮT{self.C.RESET}"
            print(f"Đã {status_text} tính năng tự động đăng nhập lại.")
        else:
            current_status = f"{self.C.GREEN}BẬT{self.C.RESET}" if Config.AUTO_LOGIN else f"{self.C.RED}TẮT{self.C.RESET}"
            print(f"Tự động đăng nhập lại hiện đang {current_status}. Dùng: autologin <on|off>")
            
        return False
