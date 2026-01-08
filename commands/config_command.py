"""
Config Command - Quản lý cấu hình hot-reload
"""
from commands.base_command import Command
from config_system.config_loader import ConfigLoader

class ConfigCommand(Command):
    """
    Lệnh quản lý cấu hình:
    - config reload: Tải lại cấu hình từ file
    - config get <key>: Xem giá trị cấu hình
    - config set <key> <value>: Đặt giá trị cấu hình (Lưu ý: Chỉ int, bool, str)
    """
    def __init__(self, manager):
        self.manager = manager
        self.loader = ConfigLoader.get_instance()

    async def execute(self, parts):
        if len(parts) < 2:
            self._show_help()
            return

        subcmd = parts[1].lower()
        
        if subcmd == "reload":
            try:
                self.loader.reload()
                # Re-apply to global config wrapper
                from config import Config
                Config.init() # Re-read values
                print("✅ Đã tải lại cấu hình (Hot-reload success).")
                
                # Trigger hooks logic (optional)
                # PluginManager watches config, but manual trigger is good
                print("ℹ️ Lưu ý: Một số thay đổi cần restart plugin để áp dụng (ví dụ: auto_chat).")
                
            except Exception as e:
                print(f"❌ Lỗi khi tải lại cấu hình: {e}")
                
        elif subcmd == "get":
            if len(parts) < 3:
                print("Usage: config get <key> (e.g. server.host)")
                return
            key = parts[2]
            val = self.loader.get(key)
            print(f"🔧 {key} = {val} ({type(val).__name__})")
            
        elif subcmd == "set":
            if len(parts) < 4:
                print("Usage: config set <key> <value>")
                return
            key = parts[2]
            value_str = parts[3]
            
            # Simple type parser
            val = value_str
            if value_str.lower() == "true": val = True
            elif value_str.lower() == "false": val = False
            elif value_str.isdigit(): val = int(value_str)
            else:
                try:
                    val = float(value_str)
                except ValueError:
                    pass
            
            self.loader.set(key, val)
            print(f"✅ Đã đặt {key} = {val}")
            
        else:
            print(f"❌ Unknown subcommand: {subcmd}")
            self._show_help()

    def _show_help(self):
        print("="*60)
        print("⚙️ CONFIG COMMANDS")
        print("config reload       - Tải lại file cấu hình")
        print("config get <key>    - Xem giá trị (ví dụ: plugins.auto_load)")
        print("config set <key> <val> - Đặt giá trị (tạm thời, không lưu file)")
        print("="*60)
