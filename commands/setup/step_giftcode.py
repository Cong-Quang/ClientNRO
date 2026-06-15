"""
Nhập giftcode tại NPC nhà hoặc Santa.
Bao gồm: gửi giftcode, đợi phản hồi server, kiểm tra item nhận được.
Có thể tái sử dụng cho bất kỳ NPC nào có chức năng giftcode.
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import NPC_SANTA, SANTA_MAPS, ITEM_1680
from commands.setup.navigation_helpers import (
    teleport_to_npc, open_menu_npc, open_input_form,
    find_menu_option, move_to_map,
)
from commands.setup.inventory_helpers import count_item, refresh_inventory


# ── Từ khóa nhận diện phản hồi giftcode ──
GIFTCODE_KEYWORDS = [
    "thành công", "chúc mừng", "nhận được", "tặng", "giftcode",
    "đã sử dụng", "da su dung", "hết hạn", "het han",
    "không tồn tại", "khong ton tai", "sai mã", "mã quà",
]


async def wait_giftcode_response(acc, ctrl, log_func, timeout: float = 5.0) -> tuple[str, str]:
    """
    Đợi phản hồi server sau khi gửi giftcode.
    Xử lý race condition: nếu message không liên quan → chờ message tiếp.
    Returns: (status, detail)其中 status: 'success'|'used'|'expired'|'invalid'|'unknown'
    """
    C = TerminalColors
    deadline = asyncio.get_event_loop().time() + timeout

    while True:
        remaining = deadline - asyncio.get_event_loop().time()
        if remaining <= 0:
            log_func(f"{C.YELLOW}→ Timeout chờ phản hồi giftcode từ server.{C.RESET}")
            return ("unknown", "timeout")

        try:
            await asyncio.wait_for(ctrl.server_message_event.wait(), timeout=remaining)
        except asyncio.TimeoutError:
            log_func(f"{C.YELLOW}→ Timeout chờ phản hồi giftcode từ server.{C.RESET}")
            return ("unknown", "timeout")

        text = ctrl.last_server_message.lower()
        detail = ctrl.last_server_message

        if not any(kw in text for kw in GIFTCODE_KEYWORDS):
            ctrl.server_message_event.clear()
            continue

        if "thành công" in text or "chúc mừng" in text:
            return ("success", detail)
        if ("nhận được" in text or "tặng" in text) and (
            "item" in text or "vật phẩm" in text or "ngọc" in text or "vàng" in text
        ):
            return ("success", detail)
        if any(kw in text for kw in ["đã sử dụng", "da su dung", "đã dùng", "da dung"]):
            return ("used", detail)
        if any(kw in text for kw in ["hết hạn", "het han", "hết hiệu lực", "qua hạn"]):
            return ("expired", detail)
        if any(kw in text for kw in ["không tồn tại", "khong ton tai", "không đúng",
                                      "sai", "không hợp lệ", "khong hop le"]):
            return ("invalid", detail)

        ctrl.server_message_event.clear()
        continue


async def check_giftcode_items(acc, log_func):
    """Kiểm tra item 1680 trong inventory sau khi nhận giftcode."""
    C = TerminalColors
    await refresh_inventory(acc)
    item_1680 = count_item(acc, ITEM_1680)
    if item_1680 > 0:
        log_func(f"{C.GREEN}→ Giftcode thành công: có item 1680 ({item_1680}) trong balo.{C.RESET}")
    else:
        log_func(f"{C.YELLOW}→ Giftcode đã nhập nhưng chưa thấy item 1680 trong balo.{C.RESET}")


async def submit_giftcode(acc, npc_id: int, code: str, log_func) -> bool:
    """
    Nhập giftcode tại NPC nhà (fallback tới Santa).
    Có thể tái sử dụng: truyền npc_id của bất kỳ NPC nào có chức năng giftcode.
    """
    C = TerminalColors
    ctrl = acc.controller

    # ── Thử tại NPC nhà ──
    if not await teleport_to_npc(acc, npc_id):
        log_func(f"{C.YELLOW}→ Không tìm thấy NPC nhà.{C.RESET}")
    else:
        opts = await open_menu_npc(acc, npc_id)
        gift_opt = find_menu_option(opts, "giftcode", "quà tặng", "mã")

        if gift_opt != -1:
            if await open_input_form(acc, npc_id, gift_opt):
                ctrl.server_message_event.clear()
                ctrl.last_server_message = ""
                await acc.service.send_client_input([code])

                status, detail = await wait_giftcode_response(acc, ctrl, log_func)
                if status == "success":
                    log_func(f"{C.GREEN}→ Giftcode '{code}' thành công!{C.RESET}")
                    await check_giftcode_items(acc, log_func)
                    return True
                elif status == "used":
                    log_func(f"{C.YELLOW}→ Giftcode '{code}' đã được sử dụng trước đó.{C.RESET}")
                    await check_giftcode_items(acc, log_func)
                    return True
                elif status == "expired":
                    log_func(f"{C.RED}→ Giftcode '{code}' đã hết hạn.{C.RESET}")
                    return False
                elif status == "invalid":
                    log_func(f"{C.RED}→ Giftcode '{code}' không tồn tại hoặc sai.{C.RESET}")
                    return False
                else:
                    log_func(f"{C.GREEN}→ Giftcode '{code}' đã gửi (phản hồi: {detail}).{C.RESET}")
                    return True
            else:
                log_func(f"{C.YELLOW}→ Timeout chờ form nhập giftcode.{C.RESET}")
        else:
            log_func(f"{C.YELLOW}→ NPC nhà không có tùy chọn Giftcode.{C.RESET}")

    # ── Fallback: tới Santa ──
    log_func(f"{C.DIM}→ Chuyển tới Santa để nhập giftcode...{C.RESET}")
    return await _submit_giftcode_santa(acc, code, log_func)


async def _submit_giftcode_santa(acc, code: str, log_func) -> bool:
    """Nhập giftcode tại Santa (fallback khi NPC nhà không có)."""
    C = TerminalColors
    ctrl = acc.controller
    santa_map = SANTA_MAPS.get(acc.char.gender, 5)

    if ctrl.tile_map.map_id != santa_map:
        await move_to_map(acc, santa_map, log_func)
    if ctrl.tile_map.map_id != santa_map:
        log_func(f"{C.RED}→ Không tới được map Santa {santa_map}.{C.RESET}")
        return False

    if not await teleport_to_npc(acc, NPC_SANTA):
        log_func(f"{C.YELLOW}→ Không tìm thấy Santa.{C.RESET}")
        return False

    opts = await open_menu_npc(acc, NPC_SANTA)
    gift_opt = find_menu_option(opts, "giftcode", "quà tặng", "mã")

    if gift_opt == -1:
        log_func(f"{C.RED}→ Không tìm thấy tùy chọn Giftcode tại Santa.{C.RESET}")
        return False

    if not await open_input_form(acc, NPC_SANTA, gift_opt):
        log_func(f"{C.YELLOW}→ Timeout chờ form giftcode tại Santa.{C.RESET}")
        return False

    ctrl.server_message_event.clear()
    ctrl.last_server_message = ""
    await acc.service.send_client_input([code])

    status, detail = await wait_giftcode_response(acc, ctrl, log_func)
    if status == "success":
        log_func(f"{C.GREEN}→ Giftcode '{code}' thành công tại Santa!{C.RESET}")
        await check_giftcode_items(acc, log_func)
        return True
    elif status == "used":
        log_func(f"{C.YELLOW}→ Giftcode '{code}' đã được sử dụng trước đó.{C.RESET}")
        await check_giftcode_items(acc, log_func)
        return True
    elif status == "expired":
        log_func(f"{C.RED}→ Giftcode '{code}' đã hết hạn tại Santa.{C.RESET}")
        return False
    elif status == "invalid":
        log_func(f"{C.RED}→ Giftcode '{code}' không tồn tại hoặc sai.{C.RESET}")
        return False
    else:
        log_func(f"{C.GREEN}→ Giftcode '{code}' đã gửi tại Santa (phản hồi: {detail}).{C.RESET}")
        return True
