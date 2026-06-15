"""
Bước 14: Mặc đồ cho đệ tử.

Dùng get_item(type=6) để đưa trang bị đã ép cho đệ tử từ balo.
Trước khi đưa Item 12 (rada), kiểm tra và ép 441/442 nếu cần.
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import (
    ITEM_EQUIP, ITEM_12, ITEM_441, ITEM_442,
)
from commands.setup.inventory_helpers import count_item, refresh_inventory, use_item_for_pet
from services.combine_service import CombineService, is_item_upgraded, is_item_fully_upgraded


async def _upgrade_pet_rada(acc, log_func, C) -> bool:
    """Kiểm tra và ép 441/442 cho tất cả Item 12 (rada) trong balo trước khi đưa cho đệ tử."""
    await refresh_inventory(acc)

    svc = CombineService(acc, log_func)

    # Tìm tất cả Item 12 chưa được ép full (thiếu 95 hoặc 96)
    rada_list = []
    for idx, item in enumerate(acc.char.arr_item_bag or []):
        if item is not None and item.item_id == ITEM_12:
            if not is_item_fully_upgraded(item):
                opts = {o.option_template_id: o.param for o in (item.item_option or [])}
                need_442 = max(0, (10 - opts.get(96, 0)) // 5)
                need_441 = max(0, (40 - opts.get(95, 0)) // 5)
                rada_list.append((idx, need_442, need_441))

    if not rada_list:
        log_func(f"{C.GREEN}→ Tất cả rada trong balo đã được ép full.{C.RESET}")
        return True

    log_func(f"{C.DIM}→ Cần ép {len(rada_list)} rada (441/442) trước khi đưa cho đệ tử...{C.RESET}")

    for copy_idx, need_442, need_441 in rada_list:
        if not acc.is_logged_in:
            return False

        cur_442 = count_item(acc, ITEM_442)
        cur_441 = count_item(acc, ITEM_441)
        if cur_442 < need_442 or cur_441 < need_441:
            log_func(f"{C.YELLOW}  → Thiếu nguyên liệu ép rada idx {copy_idx} (cần 442:{need_442}, 441:{need_441}).{C.RESET}")
            continue

        log_func(f"{C.DIM}  === Ép rada idx {copy_idx} (cần 442:{need_442}, 441:{need_441}) ==={C.RESET}")

        # Mở tab combine
        if not await svc.open_combine():
            log_func(f"{C.RED}  → Không mở được combine tab, dừng ép rada.{C.RESET}")
            return False

        # Ép 442 (hút KI)
        for i in range(need_442):
            if not acc.is_logged_in:
                return False
            await refresh_inventory(acc)
            if count_item(acc, ITEM_442) < 1:
                log_func(f"{C.YELLOW}    Hết 442.{C.RESET}")
                break
            await svc.open_combine()
            done = await svc.do_combine(
                main_item_id=ITEM_12,
                materials=[(ITEM_442, 1)],
                max_times=1,
                bag_index=copy_idx,
            )
            if done > 0:
                log_func(f"{C.DIM}      ✓ 442 lần {i+1}/{need_442}.{C.RESET}")

        # Ép 441 (hút HP)
        for i in range(need_441):
            if not acc.is_logged_in:
                return False
            await refresh_inventory(acc)
            if count_item(acc, ITEM_441) < 1:
                log_func(f"{C.YELLOW}    Hết 441.{C.RESET}")
                break
            await svc.open_combine()
            done = await svc.do_combine(
                main_item_id=ITEM_12,
                materials=[(ITEM_441, 1)],
                max_times=1,
                bag_index=copy_idx,
            )
            if done > 0:
                log_func(f"{C.DIM}      ✓ 441 lần {i+1}/{need_441}.{C.RESET}")

    return True


async def equip_pet(acc, log_func, C=None) -> bool:
    """
    Mặc đồ cho đệ tử:
    1. Ép rada (Item 12) với 441/442 trước nếu cần
    2. Tìm bản sao đã ép của mỗi item và đưa cho đệ tử
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
                await asyncio.sleep(0.01)

    if not have_pet:
        log_func(f"{C.YELLOW}→ Không có đệ tử, bỏ qua step này.{C.RESET}")
        return True

    log_func(f"{C.DIM}→ Đệ tử: {acc.pet.name} (HP: {acc.pet.c_hp}/{acc.pet.c_hp_full}){C.RESET}")

    # ── Bước 1: Ép rada trước khi đưa cho đệ tử ──
    log_func(f"{C.DIM}→ Kiểm tra rada cần ép 441/442...{C.RESET}")
    await _upgrade_pet_rada(acc, log_func, C)

    # ── Bước 2: Đưa đồ cho đệ tử ──
    items_to_give = ITEM_EQUIP

    all_ok = True
    for item_id in items_to_give:
        if not acc.is_logged_in:
            return False

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

        # Tìm bản sao đã ép trong balo (ưu tiên bản ép full)
        found_idx = -1
        found_full = False
        for idx, item in enumerate(acc.char.arr_item_bag or []):
            if item is not None and item.item_id == item_id:
                if is_item_fully_upgraded(item):
                    found_idx = idx
                    found_full = True
                    break

        if not found_full:
            for idx, item in enumerate(acc.char.arr_item_bag or []):
                if item is not None and item.item_id == item_id and is_item_upgraded(item):
                    found_idx = idx
                    break

        if found_idx < 0:
            # Không còn item nào trong balo để đưa cho đệ tử
            # Kiểm tra nếu đệ tử đã mặc bản chưa ép (từ lần chạy trước)
            pet_has_any = False
            for item in body_items:
                if item is not None and item.item_id == item_id:
                    pet_has_any = True
                    break
            if pet_has_any:
                log_func(f"{C.DIM}  → Item {item_id}: Đệ tử đã có trên người (bản chưa ép).{C.RESET}")
                continue
            log_func(f"{C.YELLOW}  → Item {item_id}: không có trong balo, bỏ qua.{C.RESET}")
            continue

        # Đưa cho đệ tử: dùng use_item_for_pet
        log_func(f"{C.DIM}  → Đưa Item {item_id} (idx {found_idx}) cho đệ tử...{C.RESET}")
        ok = await use_item_for_pet(acc, found_idx, log_func)
        if ok:
            await asyncio.sleep(0.01)
            log_func(f"{C.GREEN}    ✓ Đã đưa Item {item_id} cho đệ tử.{C.RESET}")
        else:
            log_func(f"{C.RED}    ✗ Lỗi đưa Item {item_id} cho đệ tử.{C.RESET}")
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
