"""
Configuration Loader - Load and manage configuration from JSON/YAML files
Supports environment variable overrides and hot-reload
"""
import json
import os
from typing import Any, Callable, Optional
from pathlib import Path


class ConfigLoader:
    """Singleton configuration loader with hot-reload support"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._config = {}
        self._config_path = None
        self._watchers = []
        self._initialized = True
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        return cls()
    
    def load(self, config_path: str) -> dict:
        """
        Load configuration from JSON file
        
        Args:
            config_path: Path to config file (JSON)
            
        Returns:
            Loaded configuration dictionary
        """
        self._config_path = config_path
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            
            # Apply environment variable overrides
            self._apply_env_overrides()
            
            return self._config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides (CLIENTNRO_* variables)"""
        prefix = "CLIENTNRO_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert CLIENTNRO_SERVER_HOST to server.host
                config_key = key[len(prefix):].lower().replace('_', '.')
                self.set(config_key, value)
    
    def reload(self) -> None:
        """Reload configuration from file"""
        if self._config_path:
            self.load(self._config_path)
            
            # Notify watchers
            for callback in self._watchers:
                try:
                    callback(self._config)
                except Exception as e:
                    print(f"Error in config watcher callback: {e}")
    
    def get(self, key: str, default=None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'server.host', 'ai.enabled')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'server.host')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_all(self) -> dict:
        """Get entire configuration dictionary"""
        return self._config.copy()
    
    def watch(self, callback: Callable[[dict], None]) -> None:
        """
        Register a callback to be called when config is reloaded
        
        Args:
            callback: Function to call with new config dict
        """
        self._watchers.append(callback)
    
    def save(self, config_path: Optional[str] = None) -> None:
        """
        Save current configuration to file
        
        Args:
            config_path: Path to save to (uses loaded path if None)
        """
        path = config_path or self._config_path
        if not path:
            raise ValueError("No config path specified")
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def merge(self, other_config: dict) -> None:
        """
        Merge another config dict into current config
        
        Args:
            other_config: Dictionary to merge
        """
        self._deep_merge(self._config, other_config)
    
    def _deep_merge(self, base: dict, update: dict) -> None:
        """Deep merge update dict into base dict"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value


# Convenience function for quick access
def get_config(key: str, default=None) -> Any:
    """
    Quick access to config value
    
    Args:
        key: Configuration key (dot notation)
        default: Default value if not found
        
    Returns:
        Configuration value
    """
    return ConfigLoader.get_instance().get(key, default)
