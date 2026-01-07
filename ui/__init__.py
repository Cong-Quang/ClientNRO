"""
UI Package - Tái cấu trúc từ ui.py

Package này chứa các module hiển thị thông tin game.
Re-export tất cả functions để đảm bảo backward compatibility.
"""

# Re-export all functions for backward compatibility
from ui.formatters import short_number
from ui.pet_status import get_pet_status_vietnamese, get_pet_status_short, get_pet_status_short_raw
from ui.table_utils import pad_colored, print_table_header, print_compact_divider
from ui.pet_display import display_pet_info, display_pet_help
from ui.character_display import (
    display_character_base_info,
    display_character_status,
    display_character_base_stats
)
from ui.task_display import display_task_info
from ui.help_display import display_help, display_macro_help
from ui.item_display import display_found_items
from ui.table_headers import (
    print_compact_header_show,
    print_compact_header_pet,
    print_compact_header_csgoc,
    print_compact_header_task,
    print_compact_header_autoquest,
    print_compact_footer
)
from ui.zone_display import display_zone_list, display_boss_list

# Re-export constants from logger_config
from logs.logger_config import TerminalColors, Box

__all__ = [
    # Formatters
    'short_number',
    # Pet status
    'get_pet_status_vietnamese',
    'get_pet_status_short',
    'get_pet_status_short_raw',
    # Table utilities
    'pad_colored',
    'print_table_header',
    'print_compact_divider',
    # Pet display
    'display_pet_info',
    'display_pet_help',
    # Character display
    'display_character_base_info',
    'display_character_status',
    'display_character_base_stats',
    # Task display
    'display_task_info',
    # Help display
    'display_help',
    'display_macro_help',
    # Item display
    'display_found_items',
    # Table headers
    'print_compact_header_show',
    'print_compact_header_pet',
    'print_compact_header_csgoc',
    'print_compact_header_task',
    'print_compact_header_autoquest',
    'print_compact_footer',
    # Zone display
    'display_zone_list',
    'display_boss_list',
    # Constants
    'TerminalColors',
    'Box',
]
