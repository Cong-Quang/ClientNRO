"""
Custom Command Plugin - Example showing how to add custom commands
"""
from plugins.base_plugin import BasePlugin


class CustomCommandPlugin(BasePlugin):
    """Plugin that adds custom commands"""
    
    def __init__(self):
        super().__init__()
        self.name = "CustomCommandPlugin"
        self.version = "1.0.0"
        self.author = "ClientNRO Team"
        self.description = "Example plugin that adds custom commands"
        self.command_count = 0
    
    def on_enable(self) -> None:
        """Register custom commands when enabled"""
        super().on_enable()
        
        # Register custom commands
        self.api.register_command('hello', self.cmd_hello, "Say hello")
        self.api.register_command('status', self.cmd_status, "Show plugin status")
        self.api.register_command('count', self.cmd_count, "Show command count")
        
        self.api.log_info("✅ Custom commands registered: hello, status, count")
    
    def on_disable(self) -> None:
        """Unregister commands when disabled"""
        self.api.unregister_command('hello')
        self.api.unregister_command('status')
        self.api.unregister_command('count')
        
        self.api.log_info("❌ Custom commands unregistered")
        super().on_disable()
    
    def cmd_hello(self, args: list) -> str:
        """Custom 'hello' command"""
        self.command_count += 1
        
        if args:
            name = ' '.join(args)
            message = f"Hello, {name}! 👋"
        else:
            message = "Hello, World! 👋"
        
        self.api.log_info(message)
        return message
    
    def cmd_status(self, args: list) -> str:
        """Custom 'status' command - show account status"""
        online_accounts = self.api.get_online_accounts()
        total_accounts = len(self.api.get_accounts())
        
        status = f"📊 Status: {len(online_accounts)}/{total_accounts} accounts online"
        self.api.log_info(status)
        
        for acc in online_accounts:
            char_info = f"  - {acc.username}"
            if acc.char:
                char_info += f" (Lv.{acc.char.level}, HP: {acc.char.hp}/{acc.char.max_hp})"
            self.api.log_info(char_info)
        
        return status
    
    def cmd_count(self, args: list) -> str:
        """Custom 'count' command - show command execution count"""
        message = f"🔢 Commands executed: {self.command_count}"
        self.api.log_info(message)
        return message
    
    def on_command_executed(self, command: str, args: list) -> None:
        """Track all command executions"""
        # This hook is called for ALL commands, not just custom ones
        # You can use this to monitor or log command usage
        pass
