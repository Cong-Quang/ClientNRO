"""
Notification Plugin - Example showing event notifications
"""
from plugins.base_plugin import BasePlugin
from datetime import datetime


class NotificationPlugin(BasePlugin):
    """Plugin that sends notifications for important events"""
    
    def __init__(self):
        super().__init__()
        self.name = "NotificationPlugin"
        self.version = "1.0.0"
        self.author = "ClientNRO Team"
        self.description = "Sends notifications for important game events"
        
        # Statistics
        self.stats = {
            'logins': 0,
            'logouts': 0,
            'mobs_killed': 0,
            'level_ups': 0,
            'items_picked': 0
        }
    
    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        super().on_enable()
        self.api.log_info("🔔 Notification Plugin enabled")
        self.api.log_info("   Will notify on: login, logout, level up, mob kills, items")
    
    def on_disable(self) -> None:
        """Called when plugin is disabled"""
        self._print_statistics()
        super().on_disable()
    
    def on_account_login(self, account) -> None:
        """Notify when account logs in"""
        self.stats['logins'] += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.api.log_info("=" * 60)
        self.api.log_info(f"🔑 LOGIN NOTIFICATION [{timestamp}]")
        self.api.log_info(f"   Account: {account.username}")
        if account.char:
            self.api.log_info(f"   Character: {account.char.name} (Lv.{account.char.level})")
        self.api.log_info("=" * 60)
    
    def on_account_logout(self, account) -> None:
        """Notify when account logs out"""
        self.stats['logouts'] += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.api.log_info("=" * 60)
        self.api.log_info(f"🚪 LOGOUT NOTIFICATION [{timestamp}]")
        self.api.log_info(f"   Account: {account.username}")
        self.api.log_info("=" * 60)
    
    def on_mob_killed(self, account, mob) -> None:
        """Notify when mob is killed"""
        self.stats['mobs_killed'] += 1
        
        # Only notify for every 10th kill to avoid spam
        if self.stats['mobs_killed'] % 10 == 0:
            self.api.log_info(f"⚔️ {account.username} killed {self.stats['mobs_killed']} mobs!")
    
    def on_level_up(self, account, new_level: int) -> None:
        """Notify when character levels up"""
        self.stats['level_ups'] += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.api.log_info("=" * 60)
        self.api.log_info(f"⬆️ LEVEL UP NOTIFICATION [{timestamp}]")
        self.api.log_info(f"   🎉 {account.username} reached level {new_level}!")
        self.api.log_info("=" * 60)
        
        # TODO: In a real plugin, you could send this to Telegram, Discord, etc.
        # Example: self._send_telegram(f"{account.username} leveled up to {new_level}!")
    
    def on_item_picked(self, account, item) -> None:
        """Notify when item is picked"""
        self.stats['items_picked'] += 1
        
        # Only notify for rare/valuable items (example logic)
        # In real implementation, you'd check item rarity/value
        # For now, notify every 20 items
        if self.stats['items_picked'] % 20 == 0:
            self.api.log_info(f"💎 {account.username} picked up {self.stats['items_picked']} items!")
    
    def _print_statistics(self) -> None:
        """Print plugin statistics"""
        self.api.log_info("=" * 60)
        self.api.log_info("📊 NOTIFICATION PLUGIN STATISTICS")
        self.api.log_info(f"   Logins: {self.stats['logins']}")
        self.api.log_info(f"   Logouts: {self.stats['logouts']}")
        self.api.log_info(f"   Mobs Killed: {self.stats['mobs_killed']}")
        self.api.log_info(f"   Level Ups: {self.stats['level_ups']}")
        self.api.log_info(f"   Items Picked: {self.stats['items_picked']}")
        self.api.log_info("=" * 60)
    
    # Example: How to extend this for Telegram notifications
    # def _send_telegram(self, message: str) -> None:
    #     """Send notification to Telegram"""
    #     bot_token = self.api.get_config('telegram.bot_token')
    #     chat_id = self.api.get_config('telegram.chat_id')
    #     
    #     if bot_token and chat_id:
    #         # Use requests library to send message
    #         # import requests
    #         # url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    #         # requests.post(url, json={'chat_id': chat_id, 'text': message})
    #         pass
