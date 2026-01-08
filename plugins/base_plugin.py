"""
Base Plugin Class - All plugins must inherit from this class
"""
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from plugins.plugin_api import PluginAPI


class BasePlugin(ABC):
    """
    Base class for all plugins
    
    Plugins should inherit from this class and implement the lifecycle hooks.
    """
    
    def __init__(self):
        """Initialize plugin metadata"""
        self.name = "BasePlugin"
        self.version = "1.0.0"
        self.author = "Unknown"
        self.description = "Base plugin class"
        self.enabled = False
        self.api: Optional['PluginAPI'] = None
    
    def on_load(self, plugin_api: 'PluginAPI') -> None:
        """
        Called when plugin is loaded (before enable)
        
        Args:
            plugin_api: API interface for interacting with the system
        """
        self.api = plugin_api
        self.api.logger.info(f"Plugin '{self.name}' v{self.version} loaded")
    
    def on_enable(self) -> None:
        """
        Called when plugin is enabled
        Override this to register commands, hooks, etc.
        """
        self.enabled = True
        if self.api:
            self.api.logger.info(f"Plugin '{self.name}' enabled")
    
    def on_disable(self) -> None:
        """
        Called when plugin is disabled
        Override this to cleanup resources
        """
        self.enabled = False
        if self.api:
            self.api.logger.info(f"Plugin '{self.name}' disabled")
    
    def on_unload(self) -> None:
        """
        Called when plugin is unloaded (after disable)
        Override this for final cleanup
        """
        if self.api:
            self.api.logger.info(f"Plugin '{self.name}' unloaded")
        self.api = None
    
    # Event hooks - plugins can override these to respond to events
    
    def on_account_login(self, account) -> None:
        """Called when an account logs in"""
        pass
    
    def on_account_logout(self, account) -> None:
        """Called when an account logs out"""
        pass
    
    def on_message_received(self, account, message) -> None:
        """Called when a message is received from server"""
        pass
    
    def on_combat_start(self, account, target) -> None:
        """Called when combat starts"""
        pass
    
    def on_mob_killed(self, account, mob) -> None:
        """Called when a mob is killed"""
        pass
    
    def on_level_up(self, account, new_level: int) -> None:
        """Called when character levels up"""
        pass
    
    def on_item_picked(self, account, item) -> None:
        """Called when an item is picked up"""
        pass
    
    def on_command_executed(self, command: str, args: list) -> None:
        """Called when a command is executed"""
        pass
    
    def __str__(self) -> str:
        return f"{self.name} v{self.version} by {self.author}"
    
    def __repr__(self) -> str:
        return f"<Plugin: {self.name} v{self.version}>"
