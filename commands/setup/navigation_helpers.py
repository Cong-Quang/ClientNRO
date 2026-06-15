"""
Backward-compatible wrapper — re-export từ services.navigation.

Code cũ vẫn import được:
  from commands.setup.navigation_helpers import teleport_to_npc, move_to_map

Code mới nên import trực tiếp từ services.navigation.
"""

from services.navigation import (  # noqa: F401
    HOME_MAPS, find_npc, find_npc_by_name, teleport_to_npc,
    open_menu_npc, confirm_menu_npc, open_input_form,
    find_menu_option, go_home, move_to_map, NavigationService,
)
