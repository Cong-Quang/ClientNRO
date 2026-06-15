"""
Tiện ích tìm NPC, teleport, tương tác menu và di chuyển map.
Có thể tái sử dụng từ bất kỳ module nào.
"""

import asyncio

from logs.logger_config import TerminalColors


# ── Constants ──
HOME_MAPS = {0: 21, 1: 22, 2: 23}  # Map nhà theo giới tính


# ── Tìm NPC ──

def find_npc(acc, npc_id: int):
    """Tìm NPC theo template_id trong bản đồ hiện tại."""
    npcs = acc.controller.npcs or {}
    for _, npc_data in npcs.items():
        if npc_data.get('template_id') == npc_id:
            return npc_data
    if npc_id in npcs:
        return npcs[npc_id]
    return None


def find_npc_by_name(acc, name: str):
    """Tìm NPC theo tên (không phân biệt hoa thường)."""
    name_lower = name.lower()
    npcs = acc.controller.npcs or {}
    for _, npc_data in npcs.items():
        if name_lower in npc_data.get('name', '').lower():
            return npc_data
    return None


# ── Teleport ──

async def teleport_to_npc(acc, npc_id: int, y_offset: int = -3) -> bool:
    """Teleport đến gần NPC. Thử tìm trong bản đồ trước, fallback movement service."""
    C = TerminalColors
    npc_data = find_npc(acc, npc_id)
    if npc_data:
        x, y = npc_data.get('x', 100), npc_data.get('y', 100)
        await acc.controller.movement.teleport_to(x, y + y_offset)
        await asyncio.sleep(0.3)
        return True
    try:
        result = await acc.controller.movement.teleport_to_npc(npc_id, search_by_template=True)
        if result:
            await asyncio.sleep(0.3)
            return True
    except Exception:
        pass
    return False


# ── Menu NPC ──

async def open_menu_npc(acc, npc_id: int, timeout: float = 3.0) -> list[str]:
    """Mở menu NPC, trả về danh sách tùy chọn (list[str])."""
    ctrl = acc.controller
    ctrl.ui_menu_event.clear()
    await acc.service.open_menu_npc(npc_id)
    try:
        await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        pass
    await asyncio.sleep(0.2)
    return ctrl.last_ui_options or []


async def confirm_menu_npc(acc, npc_id: int, option_idx: int,
                           wait_next: bool = False, timeout: float = 3.0) -> list[str]:
    """Xác nhận tùy chọn trong menu NPC. Nếu wait_next=True thì đợi menu tiếp theo."""
    ctrl = acc.controller
    if wait_next:
        ctrl.ui_menu_event.clear()
    await acc.service.confirm_menu_npc(npc_id, option_idx)
    if wait_next:
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.2)
        return ctrl.last_ui_options or []
    await asyncio.sleep(0.2)
    return []


async def open_input_form(acc, npc_id: int, option_idx: int, timeout: float = 3.0) -> bool:
    """Mở menu NPC → chọn option → đợi input form xuất hiện."""
    ctrl = acc.controller
    ctrl.ui_menu_event.clear()
    ctrl.input_form_received.clear()
    await acc.service.open_menu_npc(npc_id)
    try:
        await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        pass
    await asyncio.sleep(0.2)
    ctrl.ui_menu_event.clear()
    await acc.service.confirm_menu_npc(npc_id, option_idx)
    try:
        await asyncio.wait_for(ctrl.input_form_received.wait(), timeout=timeout)
        await asyncio.sleep(0.1)
        return True
    except asyncio.TimeoutError:
        return False


def find_menu_option(options: list[str], *keywords: str) -> int:
    """Tìm index tùy chọn trong menu chứa bất kỳ từ khóa nào. Trả về -1 nếu không."""
    for i, opt in enumerate(options):
        ol = opt.lower().replace('\n', ' ')
        for kw in keywords:
            if kw in ol:
                return i
    return -1


# ── Di chuyển map ──

async def go_home(acc, log_func) -> bool:
    """Di chuyển về nhà theo giới tính nhân vật."""
    C = TerminalColors
    home_map = HOME_MAPS.get(acc.char.gender, 22)
    if acc.controller.tile_map.map_id == home_map:
        log_func(f"{C.GREEN}→ Đã ở nhà (map {home_map}).{C.RESET}")
        return True
    try:
        await acc.controller.xmap.start(home_map)
        for _ in range(45):
            if not acc.is_logged_in:
                return False
            await asyncio.sleep(1)
            if not acc.controller.xmap.is_xmapping:
                break
            if acc.controller.tile_map.map_id == home_map:
                acc.controller.xmap.stop()
                break
        if acc.controller.tile_map.map_id == home_map:
            log_func(f"{C.GREEN}→ Về nhà OK.{C.RESET}")
            return True
        log_func(f"{C.YELLOW}→ Đang ở map {acc.controller.tile_map.map_id}.{C.RESET}")
        return False
    except Exception as e:
        log_func(f"{C.RED}→ Lỗi xmap: {e}{C.RESET}")
        return False


async def move_to_map(acc, target_map_id: int, log_func) -> bool:
    """Di chuyển đến map theo ID bằng xmap."""
    C = TerminalColors
    ctrl = acc.controller
    if ctrl.tile_map.map_id == target_map_id:
        log_func(f"{C.GREEN}→ Đã ở map {target_map_id}.{C.RESET}")
        return True
    try:
        log_func(f"{C.DIM}→ XMap tới map {target_map_id}...{C.RESET}")
        await ctrl.xmap.start(target_map_id)
        for i in range(45):
            if not acc.is_logged_in:
                return False
            await asyncio.sleep(1)
            if not ctrl.xmap.is_xmapping:
                break
            if ctrl.tile_map.map_id == target_map_id:
                ctrl.xmap.stop()
                break
            if i % 5 == 0 and i > 0:
                log_func(f"{C.DIM}  Đang di chuyển... (map {ctrl.tile_map.map_id}){C.RESET}")
        arrived = ctrl.tile_map.map_id == target_map_id
        if arrived:
            log_func(f"{C.GREEN}→ Đã đến map {target_map_id}.{C.RESET}")
        else:
            log_func(f"{C.YELLOW}→ Không đến được map {target_map_id} (đang ở {ctrl.tile_map.map_id}).{C.RESET}")
        return arrived
    except Exception as e:
        log_func(f"{C.RED}→ Lỗi xmap: {e}{C.RESET}")
        return False
