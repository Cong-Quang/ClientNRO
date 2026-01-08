"""
Plugin Loader - Discover and load plugins from directory
"""
import os
import sys
import importlib.util
from pathlib import Path
from typing import List, Optional
import logging

from plugins.base_plugin import BasePlugin


class PluginLoader:
    """Discovers and loads plugins from the plugins directory"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize plugin loader
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def discover_plugins(self, plugin_dir: str) -> List[str]:
        """
        Discover all plugin files in directory
        
        Args:
            plugin_dir: Directory to search for plugins
            
        Returns:
            List of plugin file paths
        """
        if not os.path.exists(plugin_dir):
            self.logger.warning(f"Plugin directory not found: {plugin_dir}")
            return []
        
        plugin_files = []
        
        # Check if user_plugins subdirectory exists
        user_plugins_dir = os.path.join(plugin_dir, 'user_plugins')
        if os.path.exists(user_plugins_dir):
            # Scan user_plugins folder
            for root, dirs, files in os.walk(user_plugins_dir):
                # Skip __pycache__
                dirs[:] = [d for d in dirs if d != '__pycache__']
                
                for file in files:
                    # Look for Python files (but not __init__.py)
                    if file.endswith('.py') and file != '__init__.py':
                        plugin_path = os.path.join(root, file)
                        plugin_files.append(plugin_path)
        else:
            self.logger.warning(f"User plugins directory not found: {user_plugins_dir}")
        
        self.logger.info(f"Discovered {len(plugin_files)} plugin(s) in user_plugins/")
        return plugin_files
    
    def load_plugin(self, plugin_path: str) -> Optional[BasePlugin]:
        """
        Load a plugin from file path
        
        Args:
            plugin_path: Path to plugin file
            
        Returns:
            Plugin instance or None if failed
        """
        try:
            # Get module name from file path
            module_name = Path(plugin_path).stem
            
            # Load module from file
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec is None or spec.loader is None:
                self.logger.error(f"Failed to load spec for plugin: {plugin_path}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find plugin class (should inherit from BasePlugin)
            plugin_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and 
                    issubclass(item, BasePlugin) and 
                    item is not BasePlugin):
                    plugin_class = item
                    break
            
            if plugin_class is None:
                self.logger.error(f"No plugin class found in: {plugin_path}")
                return None
            
            # Instantiate plugin
            plugin = plugin_class()
            plugin.file_path = plugin_path
            
            # Validate plugin
            if not self.validate_plugin(plugin):
                self.logger.error(f"Plugin validation failed: {plugin_path}")
                return None
            
            self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
            return plugin
            
        except Exception as e:
            self.logger.error(f"Error loading plugin from {plugin_path}: {e}")
            return None
    
    def validate_plugin(self, plugin: BasePlugin) -> bool:
        """
        Validate that plugin meets requirements
        
        Args:
            plugin: Plugin instance to validate
            
        Returns:
            True if valid
        """
        # Check that it's a BasePlugin instance
        if not isinstance(plugin, BasePlugin):
            self.logger.error(f"Plugin must inherit from BasePlugin")
            return False
        
        # Check required attributes
        required_attrs = ['name', 'version', 'author', 'description']
        for attr in required_attrs:
            if not hasattr(plugin, attr):
                self.logger.error(f"Plugin missing required attribute: {attr}")
                return False
        
        # Check that name is not default
        if plugin.name == "BasePlugin":
            self.logger.error(f"Plugin must set a custom name")
            return False
        
        return True
    
    def load_all_plugins(self, plugin_dir: str) -> List[BasePlugin]:
        """
        Discover and load all plugins from directory
        
        Args:
            plugin_dir: Directory to load plugins from
            
        Returns:
            List of loaded plugin instances
        """
        plugin_files = self.discover_plugins(plugin_dir)
        plugins = []
        
        for plugin_path in plugin_files:
            plugin = self.load_plugin(plugin_path)
            if plugin:
                plugins.append(plugin)
        
        self.logger.info(f"Successfully loaded {len(plugins)} plugin(s)")
        return plugins
