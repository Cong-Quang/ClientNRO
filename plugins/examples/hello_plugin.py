"""
Hello Plugin - Simple example plugin demonstrating basic functionality
"""
from plugins.base_plugin import BasePlugin


class HelloPlugin(BasePlugin):
    """Simple hello world plugin"""
    
    def __init__(self):
        super().__init__()
        self.name = "HelloPlugin"
        self.version = "1.0.0"
        self.author = "ClientNRO Team"
        self.description = "Simple hello world plugin example"
    
    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        super().on_enable()
        self.api.log_info("=" * 50)
        self.api.log_info("🎉 Hello from HelloPlugin!")
        self.api.log_info("This is a simple example plugin.")
        self.api.log_info("=" * 50)
    
    def on_disable(self) -> None:
        """Called when plugin is disabled"""
        self.api.log_info("👋 Goodbye from HelloPlugin!")
        super().on_disable()
    
    def on_account_login(self, account) -> None:
        """Called when an account logs in"""
        self.api.log_info(f"🔑 Account '{account.username}' logged in!")
    
    def on_account_logout(self, account) -> None:
        """Called when an account logs out"""
        self.api.log_info(f"🚪 Account '{account.username}' logged out!")
    
    def on_level_up(self, account, new_level: int) -> None:
        """Called when character levels up"""
        self.api.log_info(f"⬆️ {account.username} leveled up to level {new_level}!")
