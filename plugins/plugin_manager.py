"""
Plugin Manager - Manage plugin lifecycle and coordination
"""
import logging
from typing import Dict, List, Optional, TYPE_CHECKING

from plugins.base_plugin import BasePlugin
from plugins.plugin_loader import PluginLoader
from plugins.plugin_api import PluginAPI

if TYPE_CHECKING:
    from core.account_manager import AccountManager
    from config.config_loader import ConfigLoader


class PluginManager:
    """Manages plugin lifecycle, registry, and hooks"""
    
    def __init__(self, config: 'ConfigLoader', manager: Optional['AccountManager'] = None, 
                 logger: Optional[logging.Logger] = None):
        """
        Initialize plugin manager
        
        Args:
            config: Configuration loader instance
            manager: Account manager instance (can be set later)
            logger: Logger instance
        """
        self.config = config
        self.manager = manager
        self.logger = logger or logging.getLogger(__name__)
        
        self.plugins: Dict[str, BasePlugin] = {}
        self.loader = PluginLoader(self.logger)
        self.api: Optional[PluginAPI] = None
    
    def set_manager(self, manager: 'AccountManager') -> None:
        """
        Set account manager (for late initialization)
        
        Args:
            manager: Account manager instance
        """
        self.manager = manager
        if self.manager:
            self.api = PluginAPI(self.manager, self.config, self.logger)
    
    def load_all_plugins(self) -> None:
        """Load all plugins from configured plugin directory"""
        plugin_dir = self.config.get('plugins.plugin_dir', 'plugins')
        
        if not self.api:
            if self.manager:
                self.api = PluginAPI(self.manager, self.config, self.logger)
            else:
                self.logger.warning("Cannot load plugins: AccountManager not set")
                return
        
        # Load plugins
        loaded_plugins = self.loader.load_all_plugins(plugin_dir)
        
        # Register and initialize plugins
        for plugin in loaded_plugins:
            self.register_plugin(plugin)
        
        # Auto-enable plugins
        auto_load = self.config.get('plugins.auto_load', True)
        if auto_load:
            for plugin_name in self.plugins.keys():
                self.enable_plugin(plugin_name)
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """
        Register a plugin
        
        Args:
            plugin: Plugin instance to register
            
        Returns:
            True if registered successfully
        """
        if plugin.name in self.plugins:
            self.logger.warning(f"Plugin '{plugin.name}' already registered")
            return False
        
        self.plugins[plugin.name] = plugin
        
        # Call on_load hook
        try:
            plugin.on_load(self.api)
            self.logger.info(f"Registered plugin: {plugin}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading plugin '{plugin.name}': {e}")
            del self.plugins[plugin.name]
            return False
    
    def enable_plugin(self, name: str) -> bool:
        """
        Enable a plugin
        
        Args:
            name: Plugin name
            
        Returns:
            True if enabled successfully
        """
        if name not in self.plugins:
            self.logger.error(f"Plugin '{name}' not found")
            return False
        
        plugin = self.plugins[name]
        
        if plugin.enabled:
            self.logger.warning(f"Plugin '{name}' already enabled")
            return False
        
        try:
            plugin.on_enable()
            self.logger.info(f"Enabled plugin: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error enabling plugin '{name}': {e}")
            return False
    
    def disable_plugin(self, name: str) -> bool:
        """
        Disable a plugin
        
        Args:
            name: Plugin name
            
        Returns:
            True if disabled successfully
        """
        if name not in self.plugins:
            self.logger.error(f"Plugin '{name}' not found")
            return False
        
        plugin = self.plugins[name]
        
        if not plugin.enabled:
            self.logger.warning(f"Plugin '{name}' already disabled")
            return False
        
        try:
            plugin.on_disable()
            self.logger.info(f"Disabled plugin: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error disabling plugin '{name}': {e}")
            return False
    
    def unload_plugin(self, name: str) -> bool:
        """
        Unload a plugin
        
        Args:
            name: Plugin name
            
        Returns:
            True if unloaded successfully
        """
        if name not in self.plugins:
            self.logger.error(f"Plugin '{name}' not found")
            return False
        
        plugin = self.plugins[name]
        
        # Disable first if enabled
        if plugin.enabled:
            self.disable_plugin(name)
        
        try:
            plugin.on_unload()
            del self.plugins[name]
            self.logger.info(f"Unloaded plugin: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error unloading plugin '{name}': {e}")
            return False
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        Get plugin by name
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance or None
        """
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """Get all registered plugins"""
        return self.plugins.copy()
    
    def get_enabled_plugins(self) -> List[BasePlugin]:
        """Get list of enabled plugins"""
        return [p for p in self.plugins.values() if p.enabled]
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> None:
        """
        Trigger a hook on all enabled plugins
        
        Args:
            hook_name: Name of hook method to call
            *args: Arguments to pass to hook
            **kwargs: Keyword arguments to pass to hook
        """
        for plugin in self.get_enabled_plugins():
            if hasattr(plugin, hook_name):
                try:
                    method = getattr(plugin, hook_name)
                    method(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error in plugin '{plugin.name}' hook '{hook_name}': {e}")
    
    def reload_plugin(self, name: str) -> bool:
        """
        Reload a plugin (unload and load again)
        
        Args:
            name: Plugin name
            
        Returns:
            True if reloaded successfully
        """
        if name not in self.plugins:
            self.logger.error(f"Plugin '{name}' not found")
            return False
        
        # Store plugin path/state before unloading
        plugin = self.plugins[name]
        file_path = getattr(plugin, 'file_path', None)
        was_enabled = plugin.enabled
        
        # Unload
        if not self.unload_plugin(name):
            return False
            
        if not file_path:
            self.logger.warning(f"Cannot reload plugin '{name}': file path not found. Only unloaded.")
            return True
            
        # Re-load from file
        try:
            new_plugin = self.loader.load_plugin(file_path)
            if new_plugin:
                # Register
                if self.register_plugin(new_plugin):
                    # Restore state
                    if was_enabled:
                        return self.enable_plugin(new_plugin.name)
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error reloading plugin '{name}': {e}")
            return False
    
    def list_plugins(self) -> str:
        """
        Get formatted list of all plugins
        
        Returns:
            Formatted string with plugin information
        """
        if not self.plugins:
            return "No plugins loaded"
        
        lines = ["Loaded Plugins:"]
        for name, plugin in self.plugins.items():
            status = "✓ Enabled" if plugin.enabled else "✗ Disabled"
            lines.append(f"  [{status}] {plugin.name} v{plugin.version} - {plugin.description}")
        
        return "\n".join(lines)
