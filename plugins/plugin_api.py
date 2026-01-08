"""
Plugin API - Interface for plugins to interact with the system
"""
from typing import Any, Callable, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from core.account_manager import AccountManager
    from config.config_loader import ConfigLoader


class PluginAPI:
    """
    API interface provided to plugins for interacting with the system
    """
    
    def __init__(self, manager: 'AccountManager', config: 'ConfigLoader', logger: logging.Logger):
        """
        Initialize Plugin API
        
        Args:
            manager: Account manager instance
            config: Configuration loader instance
            logger: Logger instance
        """
        self.manager = manager
        self.config = config
        self.logger = logger
        self._custom_commands = {}
        self._event_subscribers = {}
    
    # Account Management
    
    def get_accounts(self) -> list:
        """
        Get list of all accounts
        
        Returns:
            List of Account objects
        """
        return self.manager.accounts
    
    def get_online_accounts(self) -> list:
        """
        Get list of online accounts
        
        Returns:
            List of online Account objects
        """
        return [acc for acc in self.manager.accounts if acc.is_logged_in]
    
    def get_account_by_username(self, username: str):
        """
        Get account by username
        
        Args:
            username: Account username
            
        Returns:
            Account object or None
        """
        for acc in self.manager.accounts:
            if acc.username == username:
                return acc
        return None
    
    # Configuration Access
    
    def get_config(self, key: str, default=None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key (dot notation)
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            key: Configuration key (dot notation)
            value: Value to set
        """
        self.config.set(key, value)
    
    # Logging
    
    def log_debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(message)
    
    def log_info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(message)
    
    # Command Registration
    
    def register_command(self, name: str, handler: Callable, description: str = "") -> bool:
        """
        Register a custom command
        
        Args:
            name: Command name
            handler: Function to handle command (receives args list)
            description: Command description
            
        Returns:
            True if registered successfully
        """
        if name in self._custom_commands:
            self.logger.warning(f"Command '{name}' already registered")
            return False
        
        self._custom_commands[name] = {
            'handler': handler,
            'description': description
        }
        self.logger.info(f"Registered custom command: {name}")
        return True
    
    def unregister_command(self, name: str) -> bool:
        """
        Unregister a custom command
        
        Args:
            name: Command name
            
        Returns:
            True if unregistered successfully
        """
        if name in self._custom_commands:
            del self._custom_commands[name]
            self.logger.info(f"Unregistered custom command: {name}")
            return True
        return False
    
    def get_custom_commands(self) -> dict:
        """Get all registered custom commands"""
        return self._custom_commands.copy()
    
    def execute_custom_command(self, name: str, args: list) -> Any:
        """
        Execute a custom command
        
        Args:
            name: Command name
            args: Command arguments
            
        Returns:
            Command result
        """
        if name not in self._custom_commands:
            return None
        
        try:
            handler = self._custom_commands[name]['handler']
            return handler(args)
        except Exception as e:
            self.logger.error(f"Error executing custom command '{name}': {e}")
            return None
    
    # Event System
    
    def subscribe_event(self, event_name: str, callback: Callable) -> None:
        """
        Subscribe to an event
        
        Args:
            event_name: Name of event to subscribe to
            callback: Function to call when event occurs
        """
        if event_name not in self._event_subscribers:
            self._event_subscribers[event_name] = []
        
        self._event_subscribers[event_name].append(callback)
        self.logger.debug(f"Subscribed to event: {event_name}")
    
    def unsubscribe_event(self, event_name: str, callback: Callable) -> None:
        """
        Unsubscribe from an event
        
        Args:
            event_name: Name of event
            callback: Callback function to remove
        """
        if event_name in self._event_subscribers:
            try:
                self._event_subscribers[event_name].remove(callback)
                self.logger.debug(f"Unsubscribed from event: {event_name}")
            except ValueError:
                pass
    
    def emit_event(self, event_name: str, *args, **kwargs) -> None:
        """
        Emit an event to all subscribers
        
        Args:
            event_name: Name of event
            *args: Event arguments
            **kwargs: Event keyword arguments
        """
        if event_name in self._event_subscribers:
            for callback in self._event_subscribers[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error in event callback for '{event_name}': {e}")
