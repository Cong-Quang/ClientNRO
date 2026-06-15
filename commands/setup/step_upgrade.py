"""
Bước 11 & 12: Ép sao trang bị tại Bà Hạt Mít (Đảo Kame).

Step 11: Ép Item 16 (x11 lần, mỗi lần 1x Item 16 + 2x Item 1)
Step 12: Ép trang bị (items 1, 7, 22, 28, 12)
  - Set 1: mỗi trang bị ép với Item 16 (x9, server MAX_STAR=9, mỗi sao +3% sức đánh)
    🔴 KHÔNG ép Item 16 cho Item 12 (rada) — rada chỉ ép 442+441
  - Set 2: TẤT CẢ copy của Item 12 (rada): 2x442 (10% hút ki) + 8x441 (40% hút HP)

Dùng services.combine_service thay vì setup-specific CombineHelper.
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import (
    ITEM_UPGRADE_16, ITEM_UPGRADE_16_CRYSTAL,
    ITEM_12, ITEM_442, ITEM_441,
    ITEM_EQUIP, UPGRADE_TIMES_PER_PIECE,
)
from commands.setup.inventory_helpers import count_item, refresh_inventory
from services.combine_service import CombineService


# ── HELPERS ──

async def _upgrade_one_by_one(svc, acc, log_func, C, item_id, copy_idx, target_stars, mat_id, mat_qty=1, max_total=9) -> int:
    """Ép từng cái một, kiểm tra sao sau mỗi lần, retry nếu cần.
    
    Args:
        svc: CombineService instance
        item_id: ID của trang bị cần ép
        copy_idx: index trong balo
        target_stars: số sao mục tiêu
        mat_id: ID nguyên liệu
        mat_qty: số lượng nguyên liệu mỗi lần ép (mặc định 1)
        max_total: số lần ép tối đa
        
    Returns: số sao đã ép thành công
    """
    done_total = 0
    attempt = 0
    max_attempts = max_total * 2  # cho phép retry

    while attempt < max_attempts:
        if not acc.is_logged_in:
            log_func(f"{C.YELLOW}  Mất kết nối, dừng ép.{C.RESET}")
            break

        if attempt > 0:
            await refresh_inventory(acc)

        # Đọc sao hiện tại
        current = svc.get_item_star_at_index(copy_idx)
        if current >= target_stars:
            log_func(f"{C.GREEN}  ✓ idx {copy_idx} đã đạt {current}/{target_stars} sao.{C.RESET}")
            break

        # Kiểm tra nguyên liệu
        mat_count = count_item(acc, mat_id)
        if mat_count < mat_qty:
            log_func(f"{C.YELLOW}  Hết item {mat_id} (còn {mat_count}).{C.RESET}")
            break

        need = target_stars - current
        to_do = min(need, mat_count // mat_qty, max_total - done_total)
        if to_do <= 0:
            break

        if not await svc.open_combine():
            log_func(f"{C.RED}  Không mở được combine.{C.RESET}")
            attempt += 1
            await asyncio.sleep(0.2)
            continue

        mat_count_before = count_item(acc, mat_id)
        stars_before = current

        done = await svc.do_combine(
            main_item_id=item_id,
            materials=[(mat_id, mat_qty)],
            max_times=to_do,
            bag_index=copy_idx,
        )

        stars_after = svc.get_item_star_at_index(copy_idx)

        if done > 0 or stars_after > stars_before:
            gained = stars_after - stars_before
            done_total += max(gained, 1)
            log_func(f"{C.DIM}    ✓ +{gained} sao (tổng {stars_after}/{target_stars}){C.RESET}")
            attempt = 0  # reset attempt counter on success
            await asyncio.sleep(0.05)
        else:
            mat_count_after = count_item(acc, mat_id)
            if mat_count_after < mat_count_before:
                # Nguyên liệu vẫn bị consume dù không detect được sao
                done_total += 1
                log_func(f"{C.DIM}    ? Nguyên liệu consumed, coi như thành công.{C.RESET}")
                attempt = 0
                await asyncio.sleep(0.05)
            else:
                attempt += 1
                log_func(f"{C.YELLOW}    ✗ Lần {attempt} không thành công, retry...{C.RESET}")
                await asyncio.sleep(0.2)

    return done_total


# ── STEP 11: Ép Item 16 ──

async def upgrade_item_16(acc, log_func, C=None) -> bool:
    """
    Ép sao Item 1 (trang bị) bằng Item 16 (đá pha lê).
    Server EpSaoTrangBi.java yêu cầu đúng 2 items: 1 trangBi + 1 daPhaLe.
    Mỗi lần combine: 1x Item 1 (equipment) + 1x Item 16 (crystal).
    """
    if C is None:
        C = TerminalColors

    svc = CombineService(acc, log_func)

    # Kiểm tra Item 1 đã đủ sao chưa (server MAX_STAR=9)
    equip_id = ITEM_UPGRADE_16_CRYSTAL  # Item 1 = equipment
    target = UPGRADE_TIMES_PER_PIECE     # Server MAX_STAR = 9

    if svc.is_fully_upgraded(equip_id, target):
        stars = svc.get_item_stars(equip_id)
        log_func(f"{C.GREEN}→ Item 1 đã đủ {stars} sao, bỏ qua.{C.RESET}")
        return True

    if not await svc.open_combine():
        return False

    await refresh_inventory(acc)

    equip_count = svc.count_item(equip_id)
    crystal_count = svc.count_item(ITEM_UPGRADE_16)
    current_stars = svc.get_item_stars(equip_id)

    log_func(f"{C.DIM}→ Item 1 (equip): {equip_count} (sao: {current_stars}/{target}), "
             f"Item 16 (crystal): {crystal_count}.{C.RESET}")

    if equip_count == 0:
        log_func(f"{C.YELLOW}→ Không có Item 1 để ép.{C.RESET}")
        return True

    need = target - current_stars
    if need <= 0:
        log_func(f"{C.GREEN}→ Item 1 đã đủ sao.{C.RESET}")
        return True

    # Tìm index của Item 1
    copy_idx = -1
    for idx, item in enumerate(acc.char.arr_item_bag or []):
        if item is not None and item.item_id == equip_id:
            copy_idx = idx
            break
    if copy_idx < 0:
        log_func(f"{C.YELLOW}→ Không tìm thấy Item 1 trong balo.{C.RESET}")
        return False

    max_up = min(need, crystal_count)
    if max_up <= 0:
        log_func(f"{C.YELLOW}→ Không đủ Item 16 (cần {need}, có {crystal_count}).{C.RESET}")
        return False

    log_func(f"{C.DIM}→ Ép Item 1 x{max_up} lần (cần thêm {need} sao)...{C.RESET}")

    done = await _upgrade_one_by_one(
        svc, acc, log_func, C,
        item_id=equip_id,
        copy_idx=copy_idx,
        target_stars=target,
        mat_id=ITEM_UPGRADE_16,
        mat_qty=1,
        max_total=max_up,
    )

    if done > 0:
        log_func(f"{C.GREEN}→ Item 1: xong {done}/{max_up} lần.{C.RESET}")
        return True
    log_func(f"{C.RED}→ Không ép được Item 1.{C.RESET}")
    return False


# ── Helper ép rada: 1 combine với 1 material ──

async def _rada_combine_one(svc, acc, log_func, C, copy_idx, mat_id, mat_label, use_item_upgrade=True) -> bool:
    """Ép 1 lần cho rada với material 442 hoặc 441.
    Đảm bảo tab combine luôn mở trước khi gửi lệnh.

    Args:
        use_item_upgrade: True=dùng open_item_upgrade(), False=dùng open_combine()
    """
    for attempt in range(5):
        if not acc.is_logged_in:
            return False

        await refresh_inventory(acc)

        # Kiểm tra material
        if count_item(acc, mat_id) < 1:
            log_func(f"{C.YELLOW}    Hết {mat_label} (item {mat_id}).{C.RESET}")
            return False

        mat_before = count_item(acc, mat_id)
        stars_before = svc.get_item_star_at_index(copy_idx)

        # Luôn mở lại tab combine trước mỗi lần do_combine vì server close tab sau combine
        if use_item_upgrade:
            tab_ok = await svc.open_item_upgrade()
        else:
            tab_ok = await svc.open_combine()
            
        if not tab_ok:
            log_func(f"{C.YELLOW}      Không mở được tab ở lần thử {attempt+1}/5, retry...{C.RESET}")
            await asyncio.sleep(0.1)
            continue

        done = await svc.do_combine(
            main_item_id=ITEM_12,
            materials=[(mat_id, 1)],
            max_times=1,
            bag_index=copy_idx,
        )

        await refresh_inventory(acc)
        stars_after = svc.get_item_star_at_index(copy_idx)
        mat_after = count_item(acc, mat_id)

        if done > 0 or stars_after > stars_before or mat_after < mat_before:
            return True
        else:
            log_func(f"{C.YELLOW}      retry {attempt+1}/5 cho {mat_label}...{C.RESET}")
            await asyncio.sleep(0.1)

    log_func(f"{C.RED}    ✗ {mat_label} thất bại sau 5 lần.{C.RESET}")
    return False


# ── STEP 12: Ép trang bị ──

async def upgrade_other_items(acc, log_func, C=None) -> bool:
    """
    Ép trang bị (items 1, 7, 22, 28, 12):
    - Set 1 (Item 16 sức đánh): items 1,7,22,28 — ALL copies
      🔴 BỎ QUA Item 12 (rada) — rada chỉ ép 442+441 (hút ki + hút HP)
    - Set 2 (442 hút ki + 441 hút HP): TẤT CẢ copy của Item 12
    - Quan trọng: Mở combine 1 lần duy nhất, reuse cho tất cả các copy
    """
    if C is None:
        C = TerminalColors

    svc = CombineService(acc, log_func)
    overall_ok = True

    # ── Set 1: Ép Item 16 (sức đánh) lên từng bản sao ──
    # Items 1,7,22,28: ép ALL copies
    # 🔴 Item 12 (rada) BỊ LOẠI khỏi vòng lặp — rada chỉ ép 442+441
    for item_id in ITEM_EQUIP:
        if item_id == ITEM_12:
            continue
        if not acc.is_logged_in:
            return False

        # Tìm tất cả bản sao
        all_copies = []
        for idx, item in enumerate(acc.char.arr_item_bag or []):
            if item is not None and item.item_id == item_id:
                stars = svc.get_item_star_at_index(idx)
                all_copies.append((idx, stars))

        if not all_copies:
            log_func(f"{C.DIM}→ Item {item_id}: không có trong balo.{C.RESET}")
            continue

        copies_to_upgrade = all_copies

        need_any = any(stars < UPGRADE_TIMES_PER_PIECE for _, stars in copies_to_upgrade)
        if not need_any:
            log_func(f"{C.GREEN}→ Item {item_id}: tất cả đã đủ sao, bỏ qua.{C.RESET}")
            continue

        item16_count = svc.count_item(ITEM_UPGRADE_16)
        if item16_count < 1:
            log_func(f"{C.YELLOW}→ Item {item_id}: hết Item 16.{C.RESET}")
            continue

        log_func(f"{C.DIM}→ Item {item_id}: {len(copies_to_upgrade)} bản sao cần ép "
                 f"({', '.join(f'idx {idx}={s}⭐' for idx, s in copies_to_upgrade)})."
                 f" Item 16: {item16_count}.{C.RESET}")

        for copy_idx, current_stars in copies_to_upgrade:
            if not acc.is_logged_in:
                return False

            if current_stars >= UPGRADE_TIMES_PER_PIECE:
                continue

            need = UPGRADE_TIMES_PER_PIECE - current_stars
            item16_now = svc.count_item(ITEM_UPGRADE_16)
            if item16_now < 1:
                log_func(f"{C.YELLOW}  → Hết Item 16 cho idx {copy_idx}.{C.RESET}")
                break

            max_up = min(need, item16_now)
            if max_up <= 0:
                continue

            log_func(f"{C.DIM}  → Ép idx {copy_idx} (sao: {current_stars}→{UPGRADE_TIMES_PER_PIECE}/{UPGRADE_TIMES_PER_PIECE}), "
                     f"x{max_up} lần (ép từng cái một)...{C.RESET}")

            done = await _upgrade_one_by_one(
                svc, acc, log_func, C,
                item_id=item_id,
                copy_idx=copy_idx,
                target_stars=UPGRADE_TIMES_PER_PIECE,
                mat_id=ITEM_UPGRADE_16,
                mat_qty=1,
                max_total=max_up,
            )

            if done > 0:
                log_func(f"{C.GREEN}    ✓ idx {copy_idx}: xong {done} lần.{C.RESET}")
            else:
                overall_ok = False
                log_func(f"{C.YELLOW}    ✗ idx {copy_idx}: không ép được.{C.RESET}")

    # ── Set 2: Item 12 đặc biệt (442 hút ki + 441 hút HP) ──
    # Mỗi copy rada: 2x442 + 8x441
    # QUAN TRỌNG: Mở combine TAB MỚI cho mỗi copy (server có thể close tab sau combine)
    if not acc.is_logged_in:
        return False

    await refresh_inventory(acc)

    total_442 = svc.count_item(ITEM_442)
    total_441 = svc.count_item(ITEM_441)
    log_func(f"{C.DIM}→ Set 2 (rada 442+441): Có {total_442}x442, {total_441}x441 trong balo.{C.RESET}")

    # Ép rada theo vòng lặp: tìm từng copy, ép, refresh, lặp
    copy_round = 0
    while True:
        if not acc.is_logged_in:
            break

        await refresh_inventory(acc)

        # Tìm 1 bản sao Item 12 cần upgrade (hút ki < 10% hoặc hút HP < 40%)
        copy_idx = -1
        need_442_qty = 0
        need_441_qty = 0
        for idx, item in enumerate(acc.char.arr_item_bag or []):
            if item is not None and item.item_id == ITEM_12:
                opts = {o.option_template_id: o.param for o in (item.item_option or [])}
                p_ki = opts.get(96, 0)
                p_hp = opts.get(95, 0)
                if p_ki < 10 or p_hp < 40:
                    copy_idx = idx
                    need_442_qty = max(0, (10 - p_ki) // 5)
                    need_441_qty = max(0, (40 - p_hp) // 5)
                    break

        if copy_idx < 0:
            log_func(f"{C.GREEN}→ Tất cả rada trong balo đã được ép xong (hoặc không còn rada chưa ép).{C.RESET}")
            break

        # Kiểm tra nguyên liệu
        cur_442 = svc.count_item(ITEM_442)
        cur_441 = svc.count_item(ITEM_441)
        if cur_442 < need_442_qty or cur_441 < need_441_qty:
            log_func(f"{C.YELLOW}  → Thiếu nguyên liệu cho rada idx {copy_idx} (cần 442:{need_442_qty}, 441:{need_441_qty}; có 442:{cur_442}, 441:{cur_441}).{C.RESET}")
            break

        copy_round += 1
        log_func(f"{C.DIM}  === Rada copy #{copy_round}: idx {copy_idx} (cần thêm 442:{need_442_qty}, 441:{need_441_qty}) ==={C.RESET}")

        # Mở tab combine "Ép sao trang bị" (sử dụng open_combine thay vì open_item_upgrade)
        use_item_upgrade_tab = False
        tab_opened = await svc.open_combine()

        if not tab_opened:
            log_func(f"{C.RED}  → Không mở được combine tab, dừng ép rada.{C.RESET}")
            overall_ok = False
            break

        # Ép 442 (hút ki)
        combine_failed = False
        for i in range(need_442_qty):
            if not acc.is_logged_in:
                break
            await refresh_inventory(acc)
            if svc.count_item(ITEM_442) < 1:
                log_func(f"{C.YELLOW}    Hết 442 ở lần {i+1}/{need_442_qty}.{C.RESET}")
                break
            ok = await _rada_combine_one(svc, acc, log_func, C, copy_idx, ITEM_442, "442", use_item_upgrade=use_item_upgrade_tab)
            if ok:
                log_func(f"{C.DIM}      ✓ 442 lần {i+1}/{need_442_qty}.{C.RESET}")
            else:
                log_func(f"{C.YELLOW}      ✗ 442 lần {i+1}/{need_442_qty}.{C.RESET}")
                combine_failed = True
                break

        if combine_failed:
            overall_ok = False
            break

        # Ép 441 (hút HP)
        for i in range(need_441_qty):
            if not acc.is_logged_in:
                break
            await refresh_inventory(acc)
            if svc.count_item(ITEM_441) < 1:
                log_func(f"{C.YELLOW}    Hết 441 ở lần {i+1}/{need_441_qty}.{C.RESET}")
                break
            ok = await _rada_combine_one(svc, acc, log_func, C, copy_idx, ITEM_441, "441", use_item_upgrade=use_item_upgrade_tab)
            if ok:
                log_func(f"{C.DIM}      ✓ 441 lần {i+1}/{need_441_qty}.{C.RESET}")
            else:
                log_func(f"{C.YELLOW}      ✗ 441 lần {i+1}/{need_441_qty}.{C.RESET}")
                combine_failed = True
                break

        if combine_failed:
            overall_ok = False
            break

        log_func(f"{C.DIM}  → Rada copy #{copy_round} (idx {copy_idx}): kết thúc.{C.RESET}")

    # ── Verify options của Item 12 sau khi ép ──
    await refresh_inventory(acc)
    log_func(f"{C.CYAN}→ Verify options Item 12 (rada):{C.RESET}")
    svc.dump_item_options(ITEM_12)
    for idx, item in enumerate(acc.char.arr_item_bag or []):
        if item is not None and item.item_id == ITEM_12:
            star = svc.get_item_star_at_index(idx)
            opts = {o.option_template_id: o.param
                    for o in (item.item_option or [])}
            has_ki_steal = 96 in opts
            has_hp_steal = 95 in opts
            log_func(f"{C.DIM}  [idx {idx}] sao={star} "
                     f"hutHP={has_hp_steal}({opts.get(95,0)}) "
                     f"hutKi={has_ki_steal}({opts.get(96,0)}){C.RESET}")

    # ── Tổng kết ──
    svc.print_status(ITEM_EQUIP, UPGRADE_TIMES_PER_PIECE)

    if overall_ok:
        log_func(f"{C.GREEN}→ Hoàn thành ép trang bị.{C.RESET}")
    else:
        log_func(f"{C.YELLOW}→ Một số item không ép được.{C.RESET}")
    return overall_ok
