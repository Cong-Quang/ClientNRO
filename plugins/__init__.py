"""
Plugin System for ClientNRO

This package provides a flexible plugin architecture for extending ClientNRO functionality.
"""

from plugins.base_plugin import BasePlugin
from plugins.plugin_loader import PluginLoader
from plugins.plugin_manager import PluginManager
from plugins.plugin_api import PluginAPI
from plugins.plugin_hooks import PluginHooks

__all__ = [
    'BasePlugin',
    'PluginLoader',
    'PluginManager',
    'PluginAPI',
    'PluginHooks'
]
