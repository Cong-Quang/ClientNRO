"""
Plugin Hooks - Centralized hook system for triggering plugin events
"""
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from plugins.plugin_manager import PluginManager


class PluginHooks:
    """Centralized hook system for triggering plugin events"""
    
    def __init__(self, plugin_manager: 'PluginManager'):
        """
        Initialize plugin hooks
        
        Args:
            plugin_manager: Plugin manager instance
        """
        self.plugin_manager = plugin_manager
    
    def on_account_login(self, account) -> None:
        """
        Trigger when account logs in
        
        Args:
            account: Account that logged in
        """
        self.plugin_manager.trigger_hook('on_account_login', account)
    
    def on_account_logout(self, account) -> None:
        """
        Trigger when account logs out
        
        Args:
            account: Account that logged out
        """
        self.plugin_manager.trigger_hook('on_account_logout', account)
    
    def on_message_received(self, account, message) -> None:
        """
        Trigger when message is received from server
        
        Args:
            account: Account that received message
            message: Message object
        """
        self.plugin_manager.trigger_hook('on_message_received', account, message)
    
    def on_combat_start(self, account, target) -> None:
        """
        Trigger when combat starts
        
        Args:
            account: Account starting combat
            target: Combat target (mob or character)
        """
        self.plugin_manager.trigger_hook('on_combat_start', account, target)
    
    def on_mob_killed(self, account, mob) -> None:
        """
        Trigger when mob is killed
        
        Args:
            account: Account that killed mob
            mob: Mob that was killed
        """
        self.plugin_manager.trigger_hook('on_mob_killed', account, mob)
    
    def on_level_up(self, account, new_level: int) -> None:
        """
        Trigger when character levels up
        
        Args:
            account: Account that leveled up
            new_level: New level
        """
        self.plugin_manager.trigger_hook('on_level_up', account, new_level)
    
    def on_item_picked(self, account, item) -> None:
        """
        Trigger when item is picked up
        
        Args:
            account: Account that picked item
            item: Item that was picked
        """
        self.plugin_manager.trigger_hook('on_item_picked', account, item)
    
    def on_command_executed(self, command: str, args: list) -> None:
        """
        Trigger when command is executed
        
        Args:
            command: Command name
            args: Command arguments
        """
        self.plugin_manager.trigger_hook('on_command_executed', command, args)
