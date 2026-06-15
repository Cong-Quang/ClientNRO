"""
Bước 8: Mua item tại Santa shop.
Mua item hỗ trợ (517x100, 518x50) và item đặc biệt (402x6, 403x6).
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import (
    NPC_SANTA, SANTA_MAPS,
    SANTA_ITEM_HO_TRO, SANTA_ITEM_DAC_BIET, SANTA_NO_BAG_ITEMS,
)
from commands.setup.navigation_helpers import teleport_to_npc, move_to_map
from commands.setup.inventory_helpers import count_item


async def santa_shop(acc, log_func) -> bool:
    """Mua item tại Santa shop (tab hỗ trợ + tab đặc biệt)."""
    C = TerminalColors
    ctrl = acc.controller
    santa_map = SANTA_MAPS.get(acc.char.gender, 5)

    # Di chuyển tới map Santa
    if ctrl.tile_map.map_id != santa_map:
        log_func(f"{C.DIM}→ Di chuyển tới map Santa ({santa_map})...{C.RESET}")
        moved = await move_to_map(acc, santa_map, log_func)
        if not moved:
            log_func(f"{C.YELLOW}→ Không đến được map Santa ({santa_map}).{C.RESET}")
            return False

    # Teleport tới Santa
    if not await teleport_to_npc(acc, NPC_SANTA):
        log_func(f"{C.YELLOW}→ Không tìm thấy Santa.{C.RESET}")
        return False
    await asyncio.sleep(0.2)

    async def _open_and_buy(tab_keywords, tab_default, items) -> bool:
        """Mở menu Santa → chọn tab → mua items."""
        for attempt in range(1, 4):
            if attempt > 1:
                await asyncio.sleep(0.5)
                if not await teleport_to_npc(acc, NPC_SANTA):
                    continue
                await asyncio.sleep(0.2)

            # Mở menu Santa
            ctrl.ui_menu_event.clear()
            await acc.service.open_menu_npc(NPC_SANTA)
            try:
                await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.1)

            opts = ctrl.last_ui_options or []
            shop_opt = -1
            for i, opt in enumerate(opts):
                ol = opt.lower()
                if "cửa hàng" in ol or "hỗ trợ" in ol or "hotro" in ol:
                    shop_opt = i
                    break
            if shop_opt == -1:
                shop_opt = 0

            ctrl.ui_menu_event.clear()
            await acc.service.confirm_menu_npc(NPC_SANTA, shop_opt)
            try:
                await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.1)

            # Chọn tab
            tab_opts = ctrl.last_ui_options or []
            tab_idx = -1
            for i, opt in enumerate(tab_opts):
                for kw in tab_keywords:
                    if kw in opt.lower():
                        tab_idx = i
                        break
                if tab_idx != -1:
                    break
            if tab_idx == -1:
                tab_idx = tab_default

            ctrl.ui_menu_event.clear()
            await acc.service.confirm_menu_npc(NPC_SANTA, tab_idx)
            try:
                await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.1)

            # Mua items
            all_ok = True
            for item_id, qty in items:
                current_count = count_item(acc, item_id)
                need = max(0, qty - current_count)
                if need <= 0:
                    log_func(f"{C.GREEN}→ Đã có đủ item {item_id} ({current_count}).{C.RESET}")
                    continue
                log_func(f"{C.DIM}→ Mua {need} item {item_id} (có {current_count}/{qty})...{C.RESET}")
                bought = 0
                for i in range(need):
                    if not acc.is_logged_in:
                        break
                    try:
                        await acc.service.buy_item(0, item_id)
                        bought += 1
                        if bought % 50 == 0:
                            log_func(f"{C.DIM}  Đã mua {bought}/{need} item {item_id}.{C.RESET}")
                        await asyncio.sleep(0.03)
                    except Exception:
                        break
                if bought > 0:
                    log_func(f"{C.GREEN}→ Đã mua {bought} item {item_id}.{C.RESET}")

                if item_id not in SANTA_NO_BAG_ITEMS:
                    try:
                        await acc.service.request_me_info()
                    except Exception:
                        pass
                    await asyncio.sleep(0.3)
                    final_count = count_item(acc, item_id)
                    if final_count < qty:
                        log_func(f"{C.YELLOW}  Còn thiếu {qty - final_count} item {item_id}.{C.RESET}")
                        all_ok = False

            if all_ok:
                return True
        return False

    # Tab hỗ trợ
    log_func(f"{C.DIM}→ Tab hỗ trợ: 517x100, 518x50...{C.RESET}")
    ok = await _open_and_buy(
        tab_keywords=["hỗ trợ", "hotro", "trợ"],
        tab_default=0,
        items=SANTA_ITEM_HO_TRO
    )
    if not ok:
        log_func(f"{C.RED}→ Mua tab hỗ trợ không đủ.{C.RESET}")

    # Tab đặc biệt
    log_func(f"{C.DIM}→ Tab đặc biệt: 402x6, 403x6...{C.RESET}")
    ok = await _open_and_buy(
        tab_keywords=["đặc biệt", "dac biet", "biệt", "special"],
        tab_default=1,
        items=SANTA_ITEM_DAC_BIET
    )
    if not ok:
        log_func(f"{C.RED}→ Mua tab đặc biệt không đủ.{C.RESET}")

    return True
