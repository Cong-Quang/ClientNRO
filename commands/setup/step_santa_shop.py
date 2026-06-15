"""
Bước 8: Mua item tại Santa shop.
Mua item hỗ trợ (517x100, 518x50) và item đặc biệt (402x20, 403x20).
Sau khi mua, dùng item 402 và 403 mỗi loại 6 lần.
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import (
    NPC_SANTA, SANTA_MAPS,
    SANTA_ITEM_HO_TRO, SANTA_ITEM_USE, SANTA_NO_BAG_ITEMS,
)
from commands.setup.navigation_helpers import teleport_to_npc, move_to_map
from commands.setup.inventory_helpers import count_item, refresh_inventory


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
            if not await teleport_to_npc(acc, NPC_SANTA):
                log_func(f"{C.YELLOW}  → Thử lần {attempt}/3 không tìm thấy Santa.{C.RESET}")
                await asyncio.sleep(0.2)
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
                if any(kw in ol for kw in tab_keywords):
                    shop_opt = i
                    break
            if shop_opt == -1:
                shop_opt = tab_default

            log_func(f"{C.DIM}  → Chọn option {shop_opt} ({opts[shop_opt] if shop_opt < len(opts) else 'default'})...{C.RESET}")
            ctrl.ui_menu_event.clear()
            await acc.service.confirm_menu_npc(NPC_SANTA, shop_opt)
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
                        await asyncio.sleep(0.01)
                    except Exception:
                        break
                if bought > 0:
                    log_func(f"{C.GREEN}→ Đã mua {bought} item {item_id}.{C.RESET}")

                if item_id not in SANTA_NO_BAG_ITEMS:
                    await refresh_inventory(acc)
                    final_count = count_item(acc, item_id)
                    if final_count < qty:
                        log_func(f"{C.YELLOW}  Còn thiếu {qty - final_count} item {item_id}.{C.RESET}")
                        all_ok = False

            if all_ok:
                return True
        return False

    # ── Mua items tại Cửa hàng Hỗ trợ ──
    log_func(f"{C.DIM}→ Mở Cửa hàng Hỗ trợ Santa (517, 518, 402, 403)...{C.RESET}")
    ok = await _open_and_buy(
        tab_keywords=["hỗ trợ", "hotro", "trợ"],
        tab_default=0,
        items=SANTA_ITEM_HO_TRO
    )
    if not ok:
        log_func(f"{C.YELLOW}→ Một số item Santa chưa mua đủ (có thể rương đầy hoặc thiếu vàng).{C.RESET}")

    # ── Dùng item 402 và 403 mỗi loại 6 lần ──
    log_func(f"{C.DIM}→ Dùng item 402 và 403 mỗi loại 6 lần cho đệ tử...{C.RESET}")
    await refresh_inventory(acc)
    
    # Kiểm tra đệ tử có tồn tại và đang hoạt động không
    have_pet = False
    if acc.pet and acc.pet.have_pet:
        have_pet = True
    else:
        try:
            acc.controller.pet_info_event.clear()
            await acc.service.pet_info()
            await asyncio.wait_for(acc.controller.pet_info_event.wait(), timeout=3.0)
            if acc.pet and acc.pet.have_pet:
                have_pet = True
        except Exception:
            pass
        
    if not have_pet:
        log_func(f"{C.YELLOW}  → Không tìm thấy đệ tử hoạt động, bỏ qua dùng sách kĩ năng đệ tử.{C.RESET}")
    else:
        for item_id, use_times in SANTA_ITEM_USE:
            if not acc.is_logged_in:
                break
            count = count_item(acc, item_id)
            if count == 0:
                log_func(f"{C.YELLOW}  → Không có item {item_id} trong balo.{C.RESET}")
                continue
            log_func(f"{C.DIM}  → Dùng {use_times} lần item {item_id} (có {count}) cho đệ tử...{C.RESET}")
            used = 0
            for _ in range(use_times):
                if not acc.is_logged_in:
                    break
                # Tìm index item trong balo
                idx = -1
                for j, it in enumerate(acc.char.arr_item_bag or []):
                    if it is not None and it.item_id == item_id:
                        idx = j
                        break
                if idx < 0:
                    log_func(f"{C.YELLOW}    Hết item {item_id} sau {used} lần.{C.RESET}")
                    break
                try:
                    # Dùng item cho đệ tử: get_item(type=6)
                    await acc.service.get_item(6, idx)
                    used += 1
                    await asyncio.sleep(0.1)
                except Exception as e:
                    log_func(f"{C.YELLOW}    Lỗi dùng item {item_id}: {e}{C.RESET}")
                    break
            if used > 0:
                log_func(f"{C.GREEN}    ✓ Đã dùng {used} lần item {item_id} cho đệ tử.{C.RESET}")

    return True
