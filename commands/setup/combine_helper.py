"""
CombineHelper — class tái sử dụng cho mọi thao tác ép sao / combine tại NPC.

Cung cấp:
  - Mở giao diện combine
  - Check số lỗ (slot) đã ép / chưa ép
  - Thực hiện 1 lần combine (có verify)
  - Tổng kết trạng thái trang bị

Cách dùng:
  helper = CombineHelper(acc, log_func)
  await helper.open_combine()
  info = helper.check_item_slots(item_id=22)
  print(info)  # {"total": 10, "filled": 3, "empty": 7}
  done = await helper.do_combine(item_id=22, materials=[(16, 1)])
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import (
    MAP_DAO_KAME, NPC_BA_HAT_MIT, ITEM_UPGRADE_16,
)
from commands.setup.navigation_helpers import (
    teleport_to_npc, move_to_map, find_menu_option,
)
from commands.setup.inventory_helpers import count_item, refresh_inventory


# ── Option IDs trong NRO ──
# option_id 102: param = stars - 1 (ví dụ param=2 → 3 sao, param=6 → 7 sao)
# option_id 107: max stars (param = 10)
OPTION_STAR_LEVEL = 102
OPTION_MAX_STARS = 107


def detect_star_option(acc, item_id: int) -> int | None:
    """Tự động detect option_id cho sao pha lê."""
    # Check option 102 trước (đã confirm là star-related)
    for item in acc.char.arr_item_bag or []:
        if item is not None and item.item_id == item_id:
            for opt in (item.item_option or []):
                if opt.option_template_id == 102:
                    return 102
            break

    # Fallback
    CANDIDATE_IDS = [102, 107, 67, 72, 73, 74, 103, 106]
    all_options = {}
    for item in acc.char.arr_item_bag or []:
        if item is not None and item.item_id == item_id:
            for opt in (item.item_option or []):
                oid = opt.option_template_id
                if oid not in all_options:
                    all_options[oid] = []
                all_options[oid].append(opt.param)

    for oid in CANDIDATE_IDS:
        if oid in all_options:
            params = all_options[oid]
            if params and all(0 <= p <= 10 for p in params):
                return oid

    return None


class CombineHelper:
    """Helper cho thao tác ép sao / combine tại Bà Hạt Mít."""

    def __init__(self, acc, log_func):
        self.acc = acc
        self.log = log_func
        self.C = TerminalColors
        self.ctrl = acc.controller

    # ──────────────────────────────────────────
    # Check item slots
    # ──────────────────────────────────────────

    def check_item_slots(self, item_id: int, target_stars: int = 10) -> dict:
        """
        Kiểm tra chi tiết từng item trong balo theo ID.
        Returns: {
            "total": tổng_số_cái,
            "filled": đã_có_sao,
            "empty": chưa_có_sao,
            "max_stars": sao_cao_nhất,
            "target": sao_mục_tiêu,
            "items": [{"index": idx, "stars": sao, "info": "tên item"}, ...]
        }
        """
        items = []
        filled = 0
        max_stars = 0

        for idx, item in enumerate(self.acc.char.arr_item_bag or []):
            if item is not None and item.item_id == item_id:
                stars = self._get_item_stars(item)
                items.append({
                    "index": idx,
                    "stars": stars,
                    "info": item.info or f"Item {item_id}",
                    "options": [
                        {"id": o.option_template_id, "param": o.param}
                        for o in (item.item_option or [])
                    ],
                })
                if stars > 0:
                    filled += 1
                if stars > max_stars:
                    max_stars = stars

        return {
            "total": len(items),
            "filled": filled,
            "empty": len(items) - filled,
            "max_stars": max_stars,
            "target": target_stars,
            "items": items,
        }

    def get_item_stars(self, item_id: int) -> int:
        """Lấy số sao cao nhất của item trong balo."""
        max_stars = 0
        for item in self.acc.char.arr_item_bag or []:
            if item is not None and item.item_id == item_id:
                stars = self._get_item_stars(item)
                if stars > max_stars:
                    max_stars = stars
        return max_stars

    def get_item_star_at_index(self, bag_index: int) -> int:
        """Lấy số sao tại index cụ thể trong balo."""
        bag = self.acc.char.arr_item_bag or []
        if 0 <= bag_index < len(bag) and bag[bag_index] is not None:
            return self._get_item_stars(bag[bag_index])
        return 0

    def _get_item_stars(self, item) -> int:
        """Đọc số sao từ item object — option 102 param = stars - 1."""
        global OPTION_STAR_LEVEL
        if OPTION_STAR_LEVEL is not None:
            for opt in (item.item_option or []):
                if opt.option_template_id == OPTION_STAR_LEVEL:
                    return opt.param + 1  # param = stars - 1
        # Fallback
        for opt in (item.item_option or []):
            if opt.option_template_id == 107:
                return opt.param  # max stars
        return 0

    def dump_item_options(self, item_id: int):
        """Debug: in tất cả option_ids và params của items trong balo."""
        C = self.C
        self.log(f"{C.DIM}→ Dump options cho item {item_id}:{C.RESET}")
        for idx, item in enumerate(self.acc.char.arr_item_bag or []):
            if item is not None and item.item_id == item_id:
                opts_str = ", ".join([f"[{o.option_template_id}:{o.param}]" for o in (item.item_option or [])])
                self.log(f"{C.DIM}  idx={idx} info='{item.info}' opts={opts_str}{C.RESET}")

    def get_item_details(self, item_id: int) -> list[dict]:
        """
        Lấy chi tiết tất cả item theo ID trong balo.
        Returns: [{"index": idx, "qty": quantity, "stars": sao, "info": "tên", "options": [...]}]
        """
        results = []
        for idx, item in enumerate(self.acc.char.arr_item_bag or []):
            if item is not None and item.item_id == item_id:
                results.append({
                    "index": idx,
                    "qty": item.quantity,
                    "stars": self._get_item_stars(item),
                    "info": item.info or f"Item {item_id}",
                    "options": [
                        {"id": o.option_template_id, "param": o.param}
                        for o in (item.item_option or [])
                    ],
                })
        return results

    def is_fully_upgraded(self, item_id: int, target_stars: int = 10) -> bool:
        """Kiểm tra item đã đủ sao chưa (mọi item cùng loại đều đủ)."""
        for item in self.acc.char.arr_item_bag or []:
            if item is not None and item.item_id == item_id:
                if self._get_item_stars(item) < target_stars:
                    return False
        return True

    def count_item(self, item_id: int) -> int:
        """Đếm số lượng item trong balo."""
        return count_item(self.acc, item_id)

    # ──────────────────────────────────────────
    # Mở giao diện combine
    # ──────────────────────────────────────────

    async def open_combine(self) -> bool:
        """Mở menu NPC Bà Hạt Mít → Chức năng pha lê → Ép Sao Trang Bị."""
        C = self.C
        ctrl = self.ctrl

        if ctrl.tile_map.map_id != MAP_DAO_KAME:
            self.log(f"{C.DIM}→ Di chuyển tới Đảo Kame...{C.RESET}")
            if not await move_to_map(self.acc, MAP_DAO_KAME, self.log):
                self.log(f"{C.YELLOW}→ Không tới được Đảo Kame.{C.RESET}")
                return False

        if not await teleport_to_npc(self.acc, NPC_BA_HAT_MIT):
            self.log(f"{C.YELLOW}→ Không tìm thấy Bà Hạt Mít.{C.RESET}")
            return False
        await asyncio.sleep(0.3)

        ctrl.ui_menu_event.clear()
        await self.acc.service.open_menu_npc(NPC_BA_HAT_MIT)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.3)

        opts = ctrl.last_ui_options or []
        self.log(f"{C.DIM}→ Menu Bà Hạt Mít: {opts}{C.RESET}")
        if not opts:
            return False

        func_idx = find_menu_option(opts, "pha lê", "pha le", "chức năng", "chuc nang")
        if func_idx == -1:
            func_idx = 0
        self.log(f"{C.DIM}→ Chọn '{opts[func_idx]}'.{C.RESET}")

        ctrl.ui_menu_event.clear()
        await self.acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, func_idx)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.3)

        opts2 = ctrl.last_ui_options or []
        self.log(f"{C.DIM}→ Menu pha lê: {opts2}{C.RESET}")
        if not opts2:
            return False

        ep_idx = -1
        for i, opt in enumerate(opts2):
            ol = opt.lower().replace('\n', ' ')
            if "ép sao" in ol or "ep sao" in ol:
                ep_idx = i
                break
        if ep_idx == -1:
            for i, opt in enumerate(opts2):
                ol = opt.lower().replace('\n', ' ')
                if "trang bị" in ol and "pha lê" not in ol:
                    ep_idx = i
                    break
        if ep_idx == -1:
            self.log(f"{C.RED}→ Không tìm thấy 'Ép Sao Trang Bị': {opts2}{C.RESET}")
            return False

        self.log(f"{C.DIM}→ Chọn '{opts2[ep_idx]}'.{C.RESET}")
        ctrl.ui_menu_event.clear()
        ctrl.combine_event.clear()
        ctrl.combine_result = ""
        await self.acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, ep_idx)

        try:
            await asyncio.wait_for(ctrl.combine_event.wait(), timeout=3.0)
            self.log(f"{C.GREEN}→ Tab combine đã mở.{C.RESET}")
        except asyncio.TimeoutError:
            self.log(f"{C.YELLOW}→ Timeout chờ tab combine.{C.RESET}")

        await asyncio.sleep(0.5)
        return True

    # ──────────────────────────────────────────
    # Thực hiện combine
    # ──────────────────────────────────────────

    async def do_combine(self, main_item_id: int,
                         materials: list[tuple[int, int]],
                         max_times: int = 1) -> int:
        """
        Thực hiện combine lặp lại: main + materials → xác nhận → verify.
        Flow: send_combine → đợi menu → chọn option phù hợp → đợi kết quả.
        Returns: Số lần thành công
        """
        C = self.C
        ctrl = self.ctrl
        success = 0

        for round_idx in range(max_times):
            if not self.acc.is_logged_in:
                break

            await refresh_inventory(self.acc)

            item16_before = count_item(self.acc, ITEM_UPGRADE_16)

            # Tìm main item
            main_idx = -1
            for idx, item in enumerate(self.acc.char.arr_item_bag or []):
                if item is not None and item.item_id == main_item_id:
                    main_idx = idx
                    break
            if main_idx == -1:
                self.log(f"{C.YELLOW}  Hết item {main_item_id}.{C.RESET}")
                break

            # Tìm materials
            used = {main_idx}
            all_indices = [main_idx]
            all_ok = True
            for mat_id, mat_qty in materials:
                found = 0
                for idx, item in enumerate(self.acc.char.arr_item_bag or []):
                    if item is not None and item.item_id == mat_id and idx not in used:
                        if found < mat_qty:
                            all_indices.append(idx)
                            used.add(idx)
                            found += 1
                if found < mat_qty:
                    self.log(f"{C.YELLOW}  Thiếu: item {mat_id} (cần {mat_qty}, có {found}).{C.RESET}")
                    all_ok = False
            if not all_ok:
                break

            self.log(f"{C.DIM}  Lần {round_idx + 1}/{max_times}: indices={all_indices}{C.RESET}")

            # ── Gửi combine ──
            ctrl.combine_event.clear()
            ctrl.combine_result = ""
            ctrl.ui_menu_event.clear()
            await self.acc.service.send_combine_items(all_indices)

            # Đợi kết quả combine — thử cả 2 event
            result = None
            for wait in range(10):  # Tối đa đợi 10s
                await asyncio.sleep(0.5)
                if ctrl.combine_result in ("success", "fail"):
                    result = ctrl.combine_result
                    break
                # Có thể server gửi menu thay vì combine_event
                if ctrl.last_ui_options:
                    break

            opts = ctrl.last_ui_options or []

            # Nếu có menu — xử lý
            if opts:
                self.log(f"{C.DIM}  Menu confirm: {opts}{C.RESET}")

                # Chọn option phù hợp (không chọn "Đóng" nếu có option khác)
                confirm_idx = -1
                for i, opt in enumerate(opts):
                    ol = opt.lower().replace('\n', ' ')
                    if any(kw in ol for kw in ["nâng cấp", "nang cap", "cần", "can", "ngọc", "ngoc", "đồng ý", "dong y", "xác nhận"]):
                        confirm_idx = i
                        break
                if confirm_idx == -1 and len(opts) > 1:
                    # Nếu có nhiều option và không match gì, thử option cuối (thường là confirm)
                    confirm_idx = len(opts) - 1
                if confirm_idx == -1:
                    confirm_idx = 0

                self.log(f"{C.DIM}  Chọn: '{opts[confirm_idx]}' (index {confirm_idx}){C.RESET}")

                ctrl.combine_event.clear()
                ctrl.combine_result = ""
                await self.acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, confirm_idx)

                # Đợi kết quả sau khi confirm
                for wait in range(10):
                    await asyncio.sleep(0.5)
                    if ctrl.combine_result in ("success", "fail"):
                        result = ctrl.combine_result
                        break

            # ── Verify kết quả ──
            await refresh_inventory(self.acc)
            item16_after = count_item(self.acc, ITEM_UPGRADE_16)
            stars_before = self._get_star_count(main_item_id)
            stars_after = self._get_star_count_after_refresh(main_item_id)

            if result == "success":
                success += 1
                self.log(f"{C.GREEN}  ✓ Thành công (lần {round_idx + 1}), sao: {stars_before}→{stars_after}, 16: {item16_before}→{item16_after}.{C.RESET}")
            elif result == "fail":
                self.log(f"{C.YELLOW}  Thất bại (lần {round_idx + 1}).{C.RESET}")
            elif item16_after < item16_before:
                success += 1
                self.log(f"{C.GREEN}  ✓ Thành công (lần {round_idx + 1}), sao: {stars_before}→{stars_after}, 16: {item16_before}→{item16_after}.{C.RESET}")
            elif stars_after > stars_before:
                success += 1
                self.log(f"{C.GREEN}  ✓ Sao tăng (lần {round_idx + 1}), sao: {stars_before}→{stars_after}.{C.RESET}")
            else:
                self.log(f"{C.YELLOW}  Không xác nhận kết quả (sao: {stars_before}→{stars_after}, 16: {item16_before}→{item16_after}).{C.RESET}")

            await asyncio.sleep(0.5)

        return success

    def _get_star_count(self, item_id: int) -> int:
        """Lấy số sao hiện tại của item (option 102 param + 1)."""
        global OPTION_STAR_LEVEL
        for item in self.acc.char.arr_item_bag or []:
            if item is not None and item.item_id == item_id:
                if OPTION_STAR_LEVEL is not None:
                    for opt in (item.item_option or []):
                        if opt.option_template_id == OPTION_STAR_LEVEL:
                            return opt.param + 1
        return 0

    def _get_star_count_after_refresh(self, item_id: int) -> int:
        """Lấy số sao cao nhất của item (sau khi refresh)."""
        global OPTION_STAR_LEVEL
        max_s = 0
        for item in self.acc.char.arr_item_bag or []:
            if item is not None and item.item_id == item_id:
                if OPTION_STAR_LEVEL is not None:
                    for opt in (item.item_option or []):
                        if opt.option_template_id == OPTION_STAR_LEVEL:
                            if opt.param + 1 > max_s:
                                max_s = opt.param + 1
        return max_s

    # ──────────────────────────────────────────
    # Tổng kết
    # ──────────────────────────────────────────

    def print_status(self, item_ids: list[int], target_stars: int = 10):
        """In trạng thái chi tiết từng trang bị (kèm index trong balo)."""
        C = self.C
        self.log(f"{C.DIM}→ Trạng thái trang bị (option_id={OPTION_STAR_LEVEL}):{C.RESET}")
        for item_id in item_ids:
            self.dump_item_options(item_id)
            info = self.check_item_slots(item_id, target_stars)
            items = info["items"]
            max_s = info["max_stars"]
            ok = f"{C.GREEN}✓{C.RESET}" if info["filled"] == info["total"] and max_s >= target_stars else f"{C.YELLOW}✗{C.RESET}"
            self.log(f"{C.DIM}  {ok} Item {item_id}: {info['total']} cái, sao_max={max_s}/{target_stars}{C.RESET}")
            for it in items:
                s = it["stars"]
                sym = f"{C.GREEN}✓{C.RESET}" if s >= target_stars else f"{C.YELLOW}✗{C.RESET}"
                self.log(f"{C.DIM}      {sym} idx={it['index']:>3}  sao={s}/{target_stars}  {it['info'][:30]}{C.RESET}")
