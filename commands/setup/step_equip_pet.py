"""
Bước 14: Mặc đồ cho đệ tử.

Dùng get_item(type=6) để đưa trang bị đã ép cho đệ tử từ balo.
Chỉ đưa items đã ép (có option 102 > 0 hoặc option 95/96 cho rada).
Tránh đưa nhầm đồ mặc định chưa ép.
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import ITEM_EQUIP
from commands.setup.inventory_helpers import count_item, refresh_inventory
from services.combine_service import is_item_upgraded, is_item_fully_upgraded


async def equip_pet(acc, log_func, C=None) -> bool:
    """
    Mặc đồ cho đệ tử: tìm bản sao đã ép của mỗi item và đưa cho đệ tử.
    Chỉ đưa items đã ép.
    """
    if C is None:
        C = TerminalColors

    await refresh_inventory(acc)

    # Kiểm tra đệ tử tồn tại
    have_pet = False
    if acc.pet and acc.pet.have_pet:
        have_pet = True
    else:
        for attempt in range(3):
            try:
                acc.controller.pet_info_event.clear()
                await acc.service.pet_info()
                await asyncio.wait_for(acc.controller.pet_info_event.wait(), timeout=3.0)
                if acc.pet and acc.pet.have_pet:
                    have_pet = True
                    break
            except Exception:
                pass
            if attempt < 2:
                await asyncio.sleep(0.2)

    if not have_pet:
        log_func(f"{C.YELLOW}→ Không có đệ tử, bỏ qua step này.{C.RESET}")
        return True

    log_func(f"{C.DIM}→ Đệ tử: {acc.pet.name} (HP: {acc.pet.c_hp}/{acc.pet.c_hp_full}){C.RESET}")

    items_to_give = ITEM_EQUIP

    all_ok = True
    for item_id in items_to_give:
        if not acc.is_logged_in:
            return False

        # Luôn refresh và re-find để đảm bảo index chính xác (tránh lỗi do server shift items khi đưa đồ cho đệ)
        await refresh_inventory(acc)

        # Kiểm tra xem đệ tử đã mặc bản FULL upgrade này chưa trên người
        already_equipped = False
        body_items = getattr(acc.pet, 'arr_item_body', None) or []
        for item in body_items:
            if item is not None and item.item_id == item_id and is_item_fully_upgraded(item):
                already_equipped = True
                break

        if already_equipped:
            log_func(f"{C.GREEN}  → Item {item_id}: Đệ tử đã mặc bản đã ép trên người.{C.RESET}")
            continue

        # Tìm bản sao đã ép trong balo
        found_idx = -1
        for idx, item in enumerate(acc.char.arr_item_bag or []):
            if item is not None and item.item_id == item_id and is_item_fully_upgraded(item):
                found_idx = idx
                break

        if found_idx < 0:
            log_func(f"{C.YELLOW}  → Item {item_id}: không tìm thấy bản ép full trong balo. Thử tìm bản ép thường...{C.RESET}")
            for idx, item in enumerate(acc.char.arr_item_bag or []):
                if item is not None and item.item_id == item_id and is_item_upgraded(item):
                    found_idx = idx
                    break
        # Fallback cuối: lấy bất kỳ bản nào (kể cả chưa ép)
        if found_idx < 0:
            log_func(f"{C.YELLOW}  → Item {item_id}: không tìm thấy bản đã ép. Lấy bản chưa ép làm fallback...{C.RESET}")
            for idx, item in enumerate(acc.char.arr_item_bag or []):
                if item is not None and item.item_id == item_id:
                    found_idx = idx
                    break
            if found_idx < 0:
                log_func(f"{C.YELLOW}  → Item {item_id}: không có trong balo, bỏ qua.{C.RESET}")
                continue

        # Đưa cho đệ tử: get_item(type=6, index)
        log_func(f"{C.DIM}  → Đưa Item {item_id} (idx {found_idx}) cho đệ tử...{C.RESET}")
        try:
            await acc.service.get_item(6, found_idx)
            await asyncio.sleep(0.3)
            log_func(f"{C.GREEN}    ✓ Đã đưa Item {item_id} cho đệ tử.{C.RESET}")
        except Exception as e:
            log_func(f"{C.RED}    ✗ Lỗi đưa Item {item_id}: {e}{C.RESET}")
            all_ok = False

    # Refresh pet info để verify
    await refresh_inventory(acc)
    try:
        acc.controller.pet_info_event.clear()
        await acc.service.pet_info()
        await asyncio.wait_for(acc.controller.pet_info_event.wait(), timeout=3.0)
    except Exception:
        pass

    # In items trên body đệ tử
    body_items = getattr(acc.pet, 'arr_item_body', None) or []
    if body_items:
        log_func(f"{C.DIM}→ Trang bị đệ tử hiện tại:{C.RESET}")
        for idx, item in enumerate(body_items):
            if item is not None:
                log_func(f"{C.DIM}  Body[{idx}]: Item {item.item_id} - {item.info or ''}{C.RESET}")

    if all_ok:
        log_func(f"{C.GREEN}→ Đã mặc đồ cho đệ tử.{C.RESET}")
    else:
        log_func(f"{C.YELLOW}→ Một số item không đưa được cho đệ tử.{C.RESET}")

    return True
