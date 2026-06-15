"""
GiftcodeService — Service tái sử dụng cho thao tác nhập giftcode tại NPC.

Không phụ thuộc vào setup accounts, có thể dùng từ bất kỳ module nào.

Cách dùng:
  svc = GiftcodeService(acc, log_func)
  status, detail = await svc.submit_giftcode("tdstudio")
  # status: 'success' | 'used' | 'expired' | 'invalid' | 'unknown'
"""

import asyncio
from typing import Callable, Optional

from logs.logger_config import TerminalColors
from services.navigation import NavigationService
from services.inventory import InventoryService


# ── Từ khóa nhận diện phản hồi giftcode ──
GIFTCODE_KEYWORDS = [
    "thành công", "chúc mừng", "nhận được", "tặng", "giftcode",
    "đã sử dụng", "da su dung", "hết hạn", "het han",
    "không tồn tại", "khong ton tai", "sai mã", "mã quà",
]

# ── Constants (import từ shared constants) ──
from commands.setup.constants import SANTA_MAPS, NPC_SANTA, ITEM_1680


class GiftcodeService:
    """Dịch vụ nhập giftcode — tái sử dụng cho mọi module."""

    def __init__(self, acc, log_func: Optional[Callable] = None):
        """
        Args:
            acc: Account object
            log_func: Hàm log(msg) tùy chọn
        """
        self.acc = acc
        self.log = log_func or (lambda msg: None)
        self.C = TerminalColors
        self.ctrl = acc.controller
        self.nav = NavigationService(acc, log_func)
        self.inv = InventoryService(acc, log_func)

    # ═══════════════════════════════════════════════
    # EVENT GUARD
    # ═══════════════════════════════════════════════

    def _ensure_server_event(self):
        """Đảm bảo server_message_event tồn tại và là asyncio.Event().
        Controller có thể bị re-init (ví dụ khi reconnect), làm mất event cũ.
        """
        ctrl = self.ctrl
        if ctrl.server_message_event is None or not isinstance(ctrl.server_message_event, asyncio.Event):
            ctrl.server_message_event = asyncio.Event()
        return ctrl.server_message_event

    # ═══════════════════════════════════════════════
    # WAIT FOR GIFTCODE RESPONSE
    # ═══════════════════════════════════════════════

    async def wait_response(self, timeout: float = 5.0) -> tuple[str, str]:
        """Đợi phản hồi server sau khi gửi giftcode.
        Xử lý race condition: nếu message không liên quan → chờ message tiếp.

        Returns:
            (status, detail) với status: 'success'|'used'|'expired'|'invalid'|'unknown'
        """
        C = self.C
        ctrl = self.ctrl
        deadline = asyncio.get_event_loop().time() + timeout

        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                self.log(f"{C.YELLOW}→ Timeout chờ phản hồi giftcode.{C.RESET}")
                return ("unknown", "timeout")

            try:
                evt = self._ensure_server_event()
                await asyncio.wait_for(evt.wait(), timeout=remaining)
            except asyncio.TimeoutError:
                self.log(f"{C.YELLOW}→ Timeout chờ phản hồi giftcode.{C.RESET}")
                return ("unknown", "timeout")

            text = ctrl.last_server_message.lower()
            detail = ctrl.last_server_message

            if not any(kw in text for kw in GIFTCODE_KEYWORDS):
                self._ensure_server_event().clear()
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

            self._ensure_server_event().clear()
            continue

    # ═══════════════════════════════════════════════
    # CHECK ITEM 1680
    # ═══════════════════════════════════════════════

    async def check_reward_items(self):
        """Kiểm tra item 1680 trong inventory sau khi nhận giftcode."""
        C = self.C
        await self.inv.refresh()
        count = self.inv.count_item(ITEM_1680)
        if count > 0:
            self.log(f"{C.GREEN}→ Giftcode thành công: có item 1680 ({count}).{C.RESET}")
        else:
            self.log(f"{C.YELLOW}→ Giftcode đã nhập nhưng chưa thấy item 1680.{C.RESET}")

    # ═══════════════════════════════════════════════
    # SUBMIT GIFTCODE
    # ═══════════════════════════════════════════════

    async def submit_giftcode(self, code: str, npc_id: Optional[int] = None,
                              santa_map: Optional[int] = None) -> str:
        """Nhập giftcode tại NPC (tự động fallback tới Santa).

        Args:
            code: Mã giftcode (ví dụ "tdstudio")
            npc_id: ID NPC nhà (nếu None, chỉ thử Santa)
            santa_map: Map Santa theo giới tính (nếu None, tự động)

        Returns:
            status: 'success' | 'used' | 'expired' | 'invalid' | 'unknown'
        """
        # ── Thử tại NPC nhà ──
        if npc_id is not None:
            status = await self._submit_at_npc(code, npc_id)
            if status in ("success", "used"):
                return status
        else:
            self.log(f"{self.C.DIM}→ Không có NPC nhà, chuyển thẳng tới Santa...{self.C.RESET}")

        # ── Fallback: Santa ──
        return await self._submit_at_santa(code, santa_map)

    async def _submit_at_npc(self, code: str, npc_id: int) -> str:
        """Nhập giftcode tại NPC cụ thể."""
        C = self.C
        ctrl = self.ctrl

        if not await self.nav.teleport_to_npc(npc_id):
            self.log(f"{C.YELLOW}→ Không tìm thấy NPC {npc_id}.{C.RESET}")
            return "unknown"

        opts = await self.nav.open_menu(npc_id)
        gift_opt = self.nav.find_menu_option(opts, "giftcode", "quà tặng", "mã")

        if gift_opt == -1:
            self.log(f"{C.YELLOW}→ NPC {npc_id} không có tùy chọn Giftcode.{C.RESET}")
            return "unknown"

        if not await self.nav.open_input_form(npc_id, gift_opt):
            self.log(f"{C.YELLOW}→ Timeout chờ form giftcode.{C.RESET}")
            return "unknown"

        self._ensure_server_event().clear()
        ctrl.last_server_message = ""
        await self.acc.service.send_client_input([code])

        status, detail = await self.wait_response()
        await self._log_giftcode_result(code, status, detail)
        if status == "success" or status == "used":
            await self.check_reward_items()
        return status

    async def _submit_at_santa(self, code: str, santa_map: Optional[int] = None) -> str:
        """Nhập giftcode tại Santa."""
        C = self.C
        ctrl = self.ctrl

        if santa_map is None:
            santa_map = SANTA_MAPS.get(self.acc.char.gender, 5)

        if ctrl.tile_map.map_id != santa_map:
            await self.nav.move_to_map(santa_map)
        if ctrl.tile_map.map_id != santa_map:
            self.log(f"{C.RED}→ Không tới được map Santa {santa_map}.{C.RESET}")
            return "unknown"

        if not await self.nav.teleport_to_npc(NPC_SANTA):
            self.log(f"{C.YELLOW}→ Không tìm thấy Santa.{C.RESET}")
            return "unknown"

        opts = await self.nav.open_menu(NPC_SANTA)
        gift_opt = self.nav.find_menu_option(opts, "giftcode", "quà tặng", "mã")

        if gift_opt == -1:
            self.log(f"{C.RED}→ Santa không có tùy chọn Giftcode.{C.RESET}")
            return "unknown"

        if not await self.nav.open_input_form(NPC_SANTA, gift_opt):
            self.log(f"{C.YELLOW}→ Timeout chờ form giftcode tại Santa.{C.RESET}")
            return "unknown"

        self._ensure_server_event().clear()
        ctrl.last_server_message = ""
        await self.acc.service.send_client_input([code])

        status, detail = await self.wait_response()
        await self._log_giftcode_result(f"{code} (Santa)", status, detail)
        if status == "success" or status == "used":
            await self.check_reward_items()
        return status

    def _log_giftcode_result(self, code: str, status: str, detail: str):
        """Ghi log kết quả giftcode."""
        C = self.C
        if status == "success":
            self.log(f"{C.GREEN}→ Giftcode '{code}' thành công!{C.RESET}")
        elif status == "used":
            self.log(f"{C.YELLOW}→ Giftcode '{code}' đã dùng trước đó.{C.RESET}")
        elif status == "expired":
            self.log(f"{C.RED}→ Giftcode '{code}' đã hết hạn.{C.RESET}")
        elif status == "invalid":
            self.log(f"{C.RED}→ Giftcode '{code}' không tồn tại.{C.RESET}")
        else:
            self.log(f"{C.GREEN}→ Giftcode '{code}' đã gửi ({detail}).{C.RESET}")
