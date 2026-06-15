"""
CombineHelper — Wrapper tương thích ngược cho setup accounts.

Tái export từ services.combine_service để giữ backward compatibility.
Các module mới nên import trực tiếp từ services.combine_service.
"""

from services.combine_service import (
    CombineService as CombineHelper,
    detect_star_option,
    OPTION_STAR_EP,
    OPTION_SLOT_MAX,
)

# Re-export các hằng số cho tương thích
OPTION_STAR_LEVEL = OPTION_STAR_EP
OPTION_MAX_STARS = OPTION_SLOT_MAX
