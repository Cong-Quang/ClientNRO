"""
Configuration Validator - Validate configuration schema and values
"""
from typing import Any, Tuple, List


class ConfigValidator:
    """Validates configuration against schema and rules"""
    
    # Define required fields and their types
    SCHEMA = {
        'server': {
            'required': True,
            'type': dict,
            'fields': {
                'host': {'required': True, 'type': str},
                'port': {'required': True, 'type': int, 'min': 1, 'max': 65535},
                'version': {'required': False, 'type': str}
            }
        },
        'accounts': {
            'required': True,
            'type': dict,
            'fields': {
                'max_concurrent': {'required': False, 'type': int, 'min': 1},
                'auto_login': {'required': False, 'type': bool},
                'default_login': {'required': False, 'type': list},
                'login_blacklist': {'required': False, 'type': list},
                'accounts_file': {'required': False, 'type': str}
            }
        },
        'character': {
            'required': False,
            'type': dict,
            'fields': {
                'default_gender': {'required': False, 'type': int, 'min': 0, 'max': 2},
                'default_hair': {'required': False, 'type': int, 'min': 0}
            }
        },
        'proxy': {
            'required': False,
            'type': dict,
            'fields': {
                'use_local_ip_first': {'required': False, 'type': bool},
                'proxy_file': {'required': False, 'type': str}
            }
        },
        'ai': {
            'required': False,
            'type': dict,
            'fields': {
                'enabled': {'required': False, 'type': bool},
                'weights_path': {'required': False, 'type': str},
                'state_dim': {'required': False, 'type': int, 'min': 1},
                'action_count': {'required': False, 'type': int, 'min': 1},
                'decision_interval': {'required': False, 'type': (int, float), 'min': 0.1}
            }
        },
        'plugins': {
            'required': False,
            'type': dict,
            'fields': {
                'enabled': {'required': False, 'type': bool},
                'plugin_dir': {'required': False, 'type': str},
                'auto_load': {'required': False, 'type': bool},
                'enabled_plugins': {'required': False, 'type': list}
            }
        },
        'logging': {
            'required': False,
            'type': dict,
            'fields': {
                'level': {'required': False, 'type': str, 'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR']},
                'file': {'required': False, 'type': str}
            }
        }
    }
    
    def validate(self, config: dict) -> Tuple[bool, List[str]]:
        """
        Validate entire configuration
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate top-level sections
        for section_name, section_schema in self.SCHEMA.items():
            if section_schema.get('required', False) and section_name not in config:
                errors.append(f"Missing required section: {section_name}")
                continue
            
            if section_name in config:
                section_errors = self._validate_section(
                    section_name, 
                    config[section_name], 
                    section_schema
                )
                errors.extend(section_errors)
        
        return len(errors) == 0, errors
    
    def _validate_section(self, section_name: str, section_data: Any, schema: dict) -> List[str]:
        """Validate a configuration section"""
        errors = []
        
        # Check type
        expected_type = schema.get('type')
        if expected_type and not isinstance(section_data, expected_type):
            errors.append(f"Section '{section_name}' must be of type {expected_type.__name__}")
            return errors
        
        # Validate fields if it's a dict
        if isinstance(section_data, dict) and 'fields' in schema:
            for field_name, field_schema in schema['fields'].items():
                field_path = f"{section_name}.{field_name}"
                
                # Check required
                if field_schema.get('required', False) and field_name not in section_data:
                    errors.append(f"Missing required field: {field_path}")
                    continue
                
                # Validate field if present
                if field_name in section_data:
                    field_errors = self._validate_field(
                        field_path,
                        section_data[field_name],
                        field_schema
                    )
                    errors.extend(field_errors)
        
        return errors
    
    def _validate_field(self, field_path: str, value: Any, schema: dict) -> List[str]:
        """Validate a single field"""
        errors = []
        
        # Check type
        expected_type = schema.get('type')
        if expected_type:
            # Handle multiple allowed types
            if isinstance(expected_type, tuple):
                if not isinstance(value, expected_type):
                    type_names = ' or '.join(t.__name__ for t in expected_type)
                    errors.append(f"Field '{field_path}' must be of type {type_names}")
            else:
                if not isinstance(value, expected_type):
                    errors.append(f"Field '{field_path}' must be of type {expected_type.__name__}")
        
        # Check min value (for numbers)
        if 'min' in schema and isinstance(value, (int, float)):
            if value < schema['min']:
                errors.append(f"Field '{field_path}' must be >= {schema['min']}")
        
        # Check max value (for numbers)
        if 'max' in schema and isinstance(value, (int, float)):
            if value > schema['max']:
                errors.append(f"Field '{field_path}' must be <= {schema['max']}")
        
        # Check choices
        if 'choices' in schema:
            if value not in schema['choices']:
                choices_str = ', '.join(str(c) for c in schema['choices'])
                errors.append(f"Field '{field_path}' must be one of: {choices_str}")
        
        return errors
    
    def validate_field(self, key: str, value: Any) -> Tuple[bool, str]:
        """
        Validate a single field by key path
        
        Args:
            key: Field key (e.g., 'server.port')
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        parts = key.split('.')
        if len(parts) < 2:
            return False, "Invalid key format"
        
        section_name = parts[0]
        field_name = parts[1]
        
        if section_name not in self.SCHEMA:
            return True, ""  # Unknown section, skip validation
        
        section_schema = self.SCHEMA[section_name]
        if 'fields' not in section_schema or field_name not in section_schema['fields']:
            return True, ""  # Unknown field, skip validation
        
        field_schema = section_schema['fields'][field_name]
        errors = self._validate_field(key, value, field_schema)
        
        if errors:
            return False, errors[0]
        return True, ""


def validate_config(config: dict) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    validator = ConfigValidator()
    return validator.validate(config)
