"""
Target Utilities - Reusable focus functions for targeting system
Có thể dùng bởi AutoAttack, AI Core, AutoBoss, và các tools khác
"""
import math
from logs.logger_config import logger


def focus_nearest_mob(controller, max_distance: float = 100) -> bool:
    """
    Focus vào mob gần nhất trong khoảng cách max_distance
    
    Args:
        controller: Controller instance chứa account.char và mobs
        max_distance: Khoảng cách tối đa (pixels)
    
    Returns:
        True nếu tìm thấy và focus thành công, False nếu không
    """
    my_char = controller.account.char
    nearest_mob = None
    min_distance = float('inf')
    
    # Tìm mob gần nhất
    for mob_id, mob in controller.mobs.items():
        if mob.hp > -1:  # Mob chết có HP = -1, không phải 0 (theo auto_play.py)
            dist = math.sqrt((mob.x - my_char.cx)**2 + (mob.y - my_char.cy)**2)
            if dist <= max_distance and dist < min_distance:
                min_distance = dist
                nearest_mob = mob
    
    # Focus vào mob gần nhất
    if nearest_mob:
        my_char.mob_focus = nearest_mob
        logger.debug(f"Target Utils: Focused Mob {nearest_mob.mob_id} ({min_distance:.1f}px)")
        return True
    
    return False


def focus_nearest_char(controller, max_distance: float = 100) -> bool:
    """
    Focus vào char/boss gần nhất trong khoảng cách max_distance
    
    Args:
        controller: Controller instance chứa account.char và chars
        max_distance: Khoảng cách tối đa (pixels)
    
    Returns:
        True nếu tìm thấy và focus thành công, False nếu không
    """
    my_char = controller.account.char
    nearest_char = None
    min_distance = float('inf')
    
    # Tìm char gần nhất
    for char_id, char_data in controller.chars.items():
        if char_data.get('hp', 0) > -1:  # HP > -1 cho char
            char_x = char_data.get('x', 0)
            char_y = char_data.get('y', 0)
            dist = math.sqrt((char_x - my_char.cx)**2 + (char_y - my_char.cy)**2)
            if dist <= max_distance and dist < min_distance:
                min_distance = dist
                nearest_char = char_data
    
    # Focus vào char gần nhất
    if nearest_char:
        my_char.char_focus = nearest_char
        logger.debug(f"Target Utils: Focused Char {nearest_char.get('id')} ({min_distance:.1f}px)")
        return True
    
    return False


def focus_nearest_target(controller, prefer_boss: bool = False, max_distance: float = 100) -> bool:
    """
    Focus vào target gần nhất (mob hoặc char)
    
    Args:
        controller: Controller instance
        prefer_boss: Nếu True, ưu tiên char/boss hơn mob khi khoảng cách tương đương
        max_distance: Khoảng cách tối đa (pixels)
    
    Returns:
        True nếu tìm thấy và focus thành công, False nếu không
    """
    my_char = controller.account.char
    nearest_mob = None
    nearest_char = None
    min_mob_dist = float('inf')
    min_char_dist = float('inf')
    
    # Tìm mob gần nhất
    for mob_id, mob in controller.mobs.items():
        if mob.hp > -1:  # HP > -1 theo auto_play.py
            dist = math.sqrt((mob.x - my_char.cx)**2 + (mob.y - my_char.cy)**2)
            if dist <= max_distance and dist < min_mob_dist:
                min_mob_dist = dist
                nearest_mob = mob
    
    # Tìm char gần nhất
    for char_id, char_data in controller.chars.items():
        if char_data.get('hp', 0) > -1:  # HP > -1 cho char
            char_x = char_data.get('x', 0)
            char_y = char_data.get('y', 0)
            dist = math.sqrt((char_x - my_char.cx)**2 + (char_y - my_char.cy)**2)
            if dist <= max_distance and dist < min_char_dist:
                min_char_dist = dist
                nearest_char = char_data
    
    # Quyết định focus vào target nào
    if prefer_boss and nearest_char:
        # Ưu tiên boss: focus char nếu có
        my_char.char_focus = nearest_char
        logger.debug(f"Target Utils: Focused Char {nearest_char.get('id')} ({min_char_dist:.1f}px) [prefer_boss]")
        return True
    elif nearest_mob and nearest_char:
        # Có cả 2: chọn target gần hơn
        if min_mob_dist <= min_char_dist:
            my_char.mob_focus = nearest_mob
            logger.debug(f"Target Utils: Focused Mob {nearest_mob.mob_id} ({min_mob_dist:.1f}px)")
            return True
        else:
            my_char.char_focus = nearest_char
            logger.debug(f"Target Utils: Focused Char {nearest_char.get('id')} ({min_char_dist:.1f}px)")
            return True
    elif nearest_mob:
        # Chỉ có mob
        my_char.mob_focus = nearest_mob
        logger.debug(f"Target Utils: Focused Mob {nearest_mob.mob_id} ({min_mob_dist:.1f}px)")
        return True
    elif nearest_char:
        # Chỉ có char
        my_char.char_focus = nearest_char
        logger.debug(f"Target Utils: Focused Char {nearest_char.get('id')} ({min_char_dist:.1f}px)")
        return True
    
    return False


def focus_by_name(controller, name: str, target_type: str = "both", max_distance: float = 100) -> bool:
    """
    Focus vào target theo tên (fuzzy matching, case-insensitive)
    
    Args:
        controller: Controller instance
        name: Tên hoặc một phần tên cần tìm
        target_type: "mob", "char", hoặc "both"
        max_distance: Khoảng cách tối đa (pixels)
    
    Returns:
        True nếu tìm thấy và focus thành công, False nếu không
    """
    my_char = controller.account.char
    name_lower = name.lower()
    found_targets = []
    
    # Tìm mob theo tên
    if target_type in ["mob", "both"]:
        for mob_id, mob in controller.mobs.items():
            if mob.hp > -1:  # HP > -1 theo auto_play.py
                mob_name = mob.name.lower()
                if name_lower in mob_name:
                    dist = math.sqrt((mob.x - my_char.cx)**2 + (mob.y - my_char.cy)**2)
                    if dist <= max_distance:
                        found_targets.append(("mob", mob, dist, mob.name))
    
    # Tìm char theo tên
    if target_type in ["char", "both"]:
        for char_id, char_data in controller.chars.items():
            if char_data.get('hp', 0) > -1:  # HP > -1 cho char
                char_name = char_data.get('name', '').lower()
                if name_lower in char_name:
                    char_x = char_data.get('x', 0)
                    char_y = char_data.get('y', 0)
                    dist = math.sqrt((char_x - my_char.cx)**2 + (char_y - my_char.cy)**2)
                    if dist <= max_distance:
                        found_targets.append(("char", char_data, dist, char_data.get('name', 'Unknown')))
    
    if not found_targets:
        return False
    
    # Chọn target gần nhất trong danh sách match
    found_targets.sort(key=lambda x: x[2])  # Sort by distance
    target_kind, target_obj, target_dist, target_name = found_targets[0]
    
    if target_kind == "mob":
        my_char.mob_focus = target_obj
        logger.debug(f"Target Utils: Focused Mob '{target_name}' ID={target_obj.mob_id} ({target_dist:.1f}px)")
    else:  # char
        my_char.char_focus = target_obj
        logger.debug(f"Target Utils: Focused Char '{target_name}' ID={target_obj.get('id')} ({target_dist:.1f}px)")
    
    return True


def focus_by_id(controller, mob_id: int = None, char_id: int = None) -> bool:
    """
    Focus vào target theo ID cụ thể
    
    Args:
        controller: Controller instance
        mob_id: ID của mob cần focus (optional)
        char_id: ID của char cần focus (optional)
    
    Returns:
        True nếu tìm thấy và focus thành công, False nếu không
    """
    my_char = controller.account.char
    
    # Focus mob by ID
    if mob_id is not None:
        mob = controller.mobs.get(mob_id)
        if mob and mob.hp > -1:  # HP > -1 theo auto_play.py
            my_char.mob_focus = mob
            logger.debug(f"Target Utils: Focused Mob ID={mob_id}")
            return True
        else:
            logger.warning(f"Target Utils: Mob ID={mob_id} không tồn tại hoặc đã chết")
            return False
    
    # Focus char by ID
    if char_id is not None:
        char_data = controller.chars.get(char_id)
        if char_data and char_data.get('hp', 0) > -1:  # HP > -1 cho char
            my_char.char_focus = char_data
            logger.debug(f"Target Utils: Focused Char ID={char_id}")
            return True
        else:
            logger.warning(f"Target Utils: Char ID={char_id} không tồn tại hoặc đã chết")
            return False
    
    logger.warning("Target Utils: focus_by_id cần ít nhất mob_id hoặc char_id")
    return False


def clear_focus(controller):
    """
    Xóa tất cả focus hiện tại (mob_focus và char_focus)
    
    Args:
        controller: Controller instance
    """
    my_char = controller.account.char
    my_char.mob_focus = None
    my_char.char_focus = None
    logger.debug("Target Utils: Cleared all focus")


def get_focused_target(controller) -> tuple[str | None, any]:
    """
    Lấy target hiện tại đang focus
    
    Args:
        controller: Controller instance
    
    Returns:
        ("mob", mob_obj) nếu đang focus mob
        ("char", char_obj) nếu đang focus char
        (None, None) nếu không focus gì
    """
    my_char = controller.account.char
    
    if my_char.mob_focus is not None:
        return ("mob", my_char.mob_focus)
    elif my_char.char_focus is not None:
        return ("char", my_char.char_focus)
    else:
        return (None, None)
