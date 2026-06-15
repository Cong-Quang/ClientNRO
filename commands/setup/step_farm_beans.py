"""
Bước 6: Farm đậu thần tại cây đậu trong nhà.
Mục tiêu: >= 1000 đậu thần.
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import NPC_DAU_THAN, TARGET_BEAN_QTY
from commands.setup.navigation_helpers import go_home, teleport_to_npc
from commands.setup.inventory_helpers import count_beans


async def farm_magic_tree(acc, log_func, target_count: int = TARGET_BEAN_QTY) -> bool:
    """
    Farm đậu thần tại cây đậu trong nhà.
    Flow: Về nhà → Teleport NPC đậu thần → Kết hạt nhanh / Thu hoạch lặp lại.
    """
    C = TerminalColors
    ctrl = acc.controller

    # Về nhà trước
    await go_home(acc, log_func)
    await asyncio.sleep(0.01)
    await teleport_to_npc(acc, NPC_DAU_THAN)
    await asyncio.sleep(0.01)

    bean_count = count_beans(acc)
    log_func(f"{C.DIM}→ Đậu: {bean_count}/{target_count}{C.RESET}")

    if bean_count >= target_count:
        log_func(f"{C.GREEN}→ Đủ đậu.{C.RESET}")
        return True

    prev_count = bean_count
    stuck = 0

    for r in range(300):
        if not acc.is_logged_in:
            log_func(f"{C.RED}→ Mất kết nối, dừng farm đậu.{C.RESET}")
            return False

        ctrl.magic_tree_menu.clear()
        ctrl.magic_tree_options = []
        ctrl.ui_menu_event.clear()
        await acc.service.open_menu_npc(NPC_DAU_THAN)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=0.8)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.01)

        opts = ctrl.magic_tree_options or ctrl.last_ui_options or []
        if not opts:
            await asyncio.sleep(0.01)
            continue

        lo = [o.lower().replace('\n', ' ') for o in opts]
        has_fast = any('kết hạt' in o for o in lo)
        has_harvest = any('thu' in o and 'hoạch' in o for o in lo)

        if has_fast:
            fi = next((i for i, o in enumerate(lo) if 'kết hạt' in o), None)
            if fi is not None:
                if r % 10 == 0:
                    log_func(f"{C.DIM}[{r+1}] Kết hạt nhanh →{C.RESET}")
                await acc.service.confirm_menu_npc(NPC_DAU_THAN, fi)
                await asyncio.sleep(0.01)
        elif has_harvest:
            if r % 10 == 0:
                log_func(f"{C.DIM}[{r+1}] Thu hoạch →{C.RESET}")
            await acc.service.confirm_menu_npc(NPC_DAU_THAN, 0)
            await asyncio.sleep(0.01)
        else:
            await acc.service.confirm_menu_npc(NPC_DAU_THAN, 0)
            await asyncio.sleep(0.01)

        bean_count = count_beans(acc)
        if r % 5 == 0 or bean_count >= target_count:
            log_func(f"{C.DIM}  Đậu: {bean_count}/{target_count}{C.RESET}")
        if bean_count >= target_count:
            log_func(f"{C.GREEN}→ Đủ đậu: {bean_count}.{C.RESET}")
            return True

        if bean_count == prev_count:
            stuck += 1
            if stuck >= 10:
                log_func(f"{C.YELLOW}→ Bị kẹt không tăng đậu.{C.RESET}")
                break
        else:
            stuck = 0
        prev_count = bean_count

    bean_count = count_beans(acc)
    if bean_count >= target_count:
        log_func(f"{C.GREEN}→ Đủ đậu: {bean_count}.{C.RESET}")
        return True

    log_func(f"{C.YELLOW}→ Đậu: {bean_count}/{target_count}.{C.RESET}")
    return False
