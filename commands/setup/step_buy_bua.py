"""
Bước 7: Mua bùa tại Bà Hạt Mít (Vách Núi Moori).
Mua tất cả các loại bùa 1 tháng chưa có trong balo.
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import NPC_BA_HAT_MIT, MAP_VACH_NUI, BUA_ITEM_IDS
from commands.setup.navigation_helpers import (
    teleport_to_npc, move_to_map, find_npc,
    open_menu_npc, find_menu_option,
)
from commands.setup.inventory_helpers import count_item, refresh_inventory


async def buy_bua(acc, log_func) -> bool:
    """Mua bùa tại Bà Hạt Mít (Vách Núi Moori)."""
    C = TerminalColors
    ctrl = acc.controller

    # ── Di chuyển đến Vách Núi Moori ──
    log_func(f"{C.DIM}→ Di chuyển tới Vách Núi Moori (map {MAP_VACH_NUI})...{C.RESET}")
    if ctrl.tile_map.map_id != MAP_VACH_NUI:
        moved = await move_to_map(acc, MAP_VACH_NUI, log_func)
        if not moved:
            log_func(f"{C.RED}→ Không đến được Vách Núi (map hiện tại: {ctrl.tile_map.map_id}).{C.RESET}")
            return False

    log_func(f"{C.GREEN}→ Đã ở map {ctrl.tile_map.map_id}.{C.RESET}")
    await asyncio.sleep(0.01)

    # ── Đợi NPC load ──
    for attempt in range(5):
        npc_data = find_npc(acc, NPC_BA_HAT_MIT)
        if npc_data:
            break
        log_func(f"{C.DIM}  Đợi NPC load (lần {attempt + 1})...{C.RESET}")
        await asyncio.sleep(0.01)

    # ── Teleport đến Bà Hạt Mít ──
    if not await teleport_to_npc(acc, NPC_BA_HAT_MIT):
        log_func(f"{C.RED}→ Không tìm thấy Bà Hạt Mít (NPC {NPC_BA_HAT_MIT}) trên map {ctrl.tile_map.map_id}.{C.RESET}")
        # Liệt kê NPCs trên map để debug
        npcs = ctrl.npcs or {}
        if npcs:
            for nid, ndata in npcs.items():
                log_func(f"{C.DIM}  NPC: id={nid}, template={ndata.get('template_id')}, name={ndata.get('name', '?')}{C.RESET}")
        else:
            log_func(f"{C.YELLOW}  Không có NPC nào trên bản đồ.{C.RESET}")
        return False

    log_func(f"{C.GREEN}→ Đã tới Bà Hạt Mít.{C.RESET}")
    await asyncio.sleep(0.01)

    # ── Mở menu NPC ──
    opts = await open_menu_npc(acc, NPC_BA_HAT_MIT)
    log_func(f"{C.DIM}→ Menu Bà Hạt Mít: {opts}{C.RESET}")

    if not opts:
        log_func(f"{C.YELLOW}→ Menu rỗng, thử mở lại...{C.RESET}")
        ctrl.ui_menu_event.clear()
        await acc.service.open_menu_npc(NPC_BA_HAT_MIT)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.01)
        opts = ctrl.last_ui_options or []
        log_func(f"{C.DIM}→ Menu lần 2: {opts}{C.RESET}")

    if not opts:
        log_func(f"{C.RED}→ Không mở được menu.{C.RESET}")
        return False

    # ── Chọn "Cửa hàng bùa" ──
    shop_idx = find_menu_option(opts, "bùa", "bua", "cửa hàng")
    if shop_idx == -1:
        # Thử option 2 (thường là cửa hàng bùa)
        shop_idx = 1 if len(opts) > 1 else 0
        log_func(f"{C.YELLOW}→ Không tìm thấy 'Cửa hàng bùa', thử option {shop_idx}.{C.RESET}")

    log_func(f"{C.DIM}→ Chọn '{opts[shop_idx]}'{C.RESET}")
    opts2 = await open_menu_npc(acc, NPC_BA_HAT_MIT, timeout=3.0)
    # open_menu_npc đã mở menu rồi, cần dùng confirm trực tiếp
    ctrl.ui_menu_event.clear()
    await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, shop_idx)
    try:
        await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
    except asyncio.TimeoutError:
        pass
    await asyncio.sleep(0.01)

    opts2 = ctrl.last_ui_options or []
    log_func(f"{C.DIM}→ Menu bùa: {opts2}{C.RESET}")

    # ── Chọn "Bùa 1 tháng" ──
    month_idx = find_menu_option(opts2, "1 tháng", "1 thang", "tháng")
    if month_idx == -1:
        month_idx = 0 if opts2 else -1
        if month_idx >= 0:
            log_func(f"{C.YELLOW}→ Không tìm thấy 'Bùa 1 tháng', thử option 0.{C.RESET}")

    if month_idx == -1:
        log_func(f"{C.RED}→ Không có menu chọn thời hạn bùa.{C.RESET}")
        return False

    log_func(f"{C.DIM}→ Chọn '{opts2[month_idx]}'{C.RESET}")
    ctrl.ui_menu_event.clear()
    await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, month_idx)
    await asyncio.sleep(0.01)

    # ── Mua bùa ──
    await refresh_inventory(acc)
    existing = {item.item_id for item in (acc.char.arr_item_bag or []) if item is not None}

    bought = 0
    for item_id in BUA_ITEM_IDS:
        if item_id in existing:
            continue
        try:
            await acc.service.buy_item(0, item_id)
            bought += 1
            await asyncio.sleep(0.01)
        except Exception as e:
            log_func(f"{C.YELLOW}  Lỗi mua item {item_id}: {e}{C.RESET}")

    if bought > 0:
        log_func(f"{C.GREEN}→ Đã mua {bought} loại bùa.{C.RESET}")
    else:
        log_func(f"{C.YELLOW}→ Không mua thêm bùa (có thể đã có đủ).{C.RESET}")

    await refresh_inventory(acc)
    return True
