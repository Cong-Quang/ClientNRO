"""
Configuration Management for ClientNRO

This package provides flexible configuration loading and validation.

Note: The main Config class is in ../config.py (root level)
This package contains the new config system components.
"""

# Import new config system components
# DO NOT import Config class here to avoid conflict with root config.py
from config_system.config_loader import ConfigLoader, get_config
from config_system.config_validator import ConfigValidator, validate_config

__all__ = [
    'ConfigLoader',
    'get_config',
    'ConfigValidator',
    'validate_config'
]
