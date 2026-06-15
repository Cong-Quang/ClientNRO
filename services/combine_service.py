"""
CombineService — Service tái sử dụng cho mọi thao tác ép sao / combine / đập đồ tại NPC.

Không phụ thuộc vào setup accounts, có thể dùng từ bất kỳ module nào
(targeted_commands, auto_boss, plugins, v.v.).

Cách dùng:
  svc = CombineService(acc, log_func)
  await svc.open_combine(npc_id=21, map_id=5)
  done = await svc.do_combine(main_item_id=1, materials=[(16, 1)], max_times=10)
  stars = svc.get_item_stars(1)
  info = svc.check_item_slots(1)
"""

import asyncio
from typing import Callable, Optional

from logs.logger_config import TerminalColors
from services.navigation import NavigationService, move_to_map, teleport_to_npc, find_menu_option
from services.inventory import InventoryService, refresh_inventory, count_item


# ── Option IDs trong NRO ──
# Server Java (EpSaoTrangBi.java): option 102 param = star count trực tiếp
# Server Java (PhaLeHoaTrangBi.java): option 107 = pha lê star
OPTION_STAR_EP = 102       # Ép sao: param = star count
OPTION_SLOT_MAX = 107      # Max slot / pha lê star


def detect_star_option(acc, item_id: int) -> Optional[int]:
    """Tự động detect option_id cho sao pha lê.
    Server dùng:
      - Option 102: ép sao (param = star count)
      - Option 107: pha lê hóa hoặc max slots
    """
    for item in acc.char.arr_item_bag or []:
        if item is not None and item.item_id == item_id:
            for opt in (item.item_option or []):
                if opt.option_template_id == 102:
                    return 102
            for opt in (item.item_option or []):
                if opt.option_template_id == 107:
                    return 107
            break
    return None


def is_item_upgraded(item) -> bool:
    """Kiểm tra item đã được ép/chế tạo chưa.
    - Item 12 (rada): phải có option 95 (HP steal) hoặc 96 (KI steal)
    - Items 1,7,22,28: phải có option 102 > 0 (ép sao)
    
    Dùng chung cho cả equip_master và equip_pet để tránh duplicate code.
    
    Args:
        item: Item object từ inventory (có item_id và item_option)
    Returns:
        True nếu item đã được ép (có option phù hợp)
    """
    if item is None or not item.item_option:
        return False
    opts = {o.option_template_id: o.param for o in item.item_option}
    # Item 12 (rada): kiểm tra option 95 (hút HP) hoặc 96 (hút KI)
    if item.item_id == 12:
        return 95 in opts or 96 in opts
    # Trang bị thường: kiểm tra option 102 (ép sao) > 0
    return opts.get(102, 0) > 0


def is_item_fully_upgraded(item) -> bool:
    """Kiểm tra item đã được ép FULL chưa (đầy đủ các sao/chỉ số cần thiết).
    - Item 12 (rada): phải đạt tối thiểu option 95 >= 40 (40% hút HP) và option 96 >= 10 (10% hút KI)
    - Các items khác (1,7,22,28): phải có option 102 >= 10 (10 sao = 30% sức đánh)
    """
    if item is None or not item.item_option:
        return False
    opts = {o.option_template_id: o.param for o in item.item_option}
    if item.item_id == 12:
        return opts.get(95, 0) >= 40 and opts.get(96, 0) >= 10
    return opts.get(102, 0) >= 10


class CombineService:
    """Dịch vụ combine / ép sao / đập đồ — tái sử dụng cho mọi module."""

    def __init__(self, acc, log_func: Optional[Callable] = None):
        """
        Args:
            acc: Account object
            log_func: Hàm log(msg) tùy chọn. Nếu None, dùng print mặc định.
        """
        self.acc = acc
        self.log = log_func or (lambda msg: None)
        self.C = TerminalColors
        self.ctrl = acc.controller
        self.nav = NavigationService(acc, log_func)
        self.inv = InventoryService(acc, log_func)

    # ═══════════════════════════════════════════════
    # UTILITY SHORTCUTS
    # ═══════════════════════════════════════════════

    def count_item(self, item_id: int) -> int:
        """Đếm item trong balo (delegate tới InventoryService)."""
        return self.inv.count_item(item_id)

    async def refresh_inventory(self):
        """Refresh inventory (delegate tới InventoryService)."""
        await self.inv.refresh()

    def find_menu_option(self, options: list[str], *keywords: str) -> int:
        """Tìm tùy chọn menu (delegate tới NavigationService)."""
        return NavigationService.find_menu_option(options, *keywords)

    # ═══════════════════════════════════════════════
    # ITEM HELPERS
    # ═══════════════════════════════════════════════

    def _get_item_stars(self, item) -> int:
        """Đọc số sao ép sao từ item object.
        Server Java (EpSaoTrangBi.java):
          - Option 102: param = ép sao star count (param=1 = 1 sao, param=9 = 9 sao)
          - Option 107: param = max slots (pha lê hóa), KHÔNG phải ép sao star
        Chỉ option 102 mới là ép sao star count.
        """
        for opt in (item.item_option or []):
            if opt.option_template_id == OPTION_STAR_EP:
                return opt.param  # param = star count trực tiếp
        # KHÔNG fallback về option 107 vì 107 là max slots, không phải ép sao star!
        return 0

    def _get_star_count(self, item_id: int) -> int:
        """Lấy số sao ép sao hiện tại của item (chỉ option 102)."""
        for item in self.acc.char.arr_item_bag or []:
            if item is not None and item.item_id == item_id:
                for opt in (item.item_option or []):
                    if opt.option_template_id == OPTION_STAR_EP:
                        return opt.param
        return 0

    def _get_star_count_max(self, item_id: int) -> int:
        """Lấy số sao ép sao cao nhất (chỉ option 102)."""
        max_s = 0
        for item in self.acc.char.arr_item_bag or []:
            if item is not None and item.item_id == item_id:
                for opt in (item.item_option or []):
                    if opt.option_template_id == OPTION_STAR_EP:
                        if opt.param > max_s:
                            max_s = opt.param
        return max_s

    def get_item_stars(self, item_id: int) -> int:
        """Lấy số sao cao nhất của item trong balo."""
        return self._get_star_count_max(item_id)

    def get_item_star_at_index(self, bag_index: int) -> int:
        """Lấy số sao tại index cụ thể trong balo."""
        bag = self.acc.char.arr_item_bag or []
        if 0 <= bag_index < len(bag) and bag[bag_index] is not None:
            return self._get_item_stars(bag[bag_index])
        return 0

    def count_item(self, item_id: int) -> int:
        """Đếm số lượng item trong balo."""
        return self.inv.count_item(item_id)

    def dump_item_options(self, item_id: int):
        """Debug: in tất cả option_ids và params của items trong balo."""
        C = self.C
        self.log(f"{C.DIM}→ Dump options cho item {item_id}:{C.RESET}")
        for idx, item in enumerate(self.acc.char.arr_item_bag or []):
            if item is not None and item.item_id == item_id:
                opts_str = ", ".join([f"[{o.option_template_id}:{o.param}]"
                                      for o in (item.item_option or [])])
                self.log(f"{C.DIM}  idx={idx} info='{item.info}' opts={opts_str}{C.RESET}")

    def get_item_details(self, item_id: int) -> list[dict]:
        """Lấy chi tiết tất cả item theo ID trong balo.
        Returns: [{"index": idx, "qty": quantity, "stars": sao,
                    "info": "tên", "options": [...]}]
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

    def get_slot_max(self, item) -> int:
        """Đọc số slot tối đa (option 107) của item — dùng để phân biệt ép sao vs pha lê hóa."""
        for opt in (item.item_option or []):
            if opt.option_template_id == OPTION_SLOT_MAX:
                return opt.param
        return 0

    # ═══════════════════════════════════════════════
    # SLOT CHECKERS
    # ═══════════════════════════════════════════════

    def check_item_slots(self, item_id: int, target_stars: int = 9) -> dict:
        """Kiểm tra chi tiết từng item trong balo theo ID.
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

    def is_fully_upgraded(self, item_id: int, target_stars: int = 9) -> bool:
        """Kiểm tra item đã đủ sao chưa (mọi item cùng loại đều đủ)."""
        for item in self.acc.char.arr_item_bag or []:
            if item is not None and item.item_id == item_id:
                if self._get_item_stars(item) < target_stars:
                    return False
        return True

    def print_status(self, item_ids: list[int], target_stars: int = 9):
        """In trạng thái chi tiết từng trang bị."""
        C = self.C
        self.log(f"{C.DIM}→ Trạng thái trang bị:{C.RESET}")
        for item_id in item_ids:
            self.dump_item_options(item_id)
            info = self.check_item_slots(item_id, target_stars)
            items = info["items"]
            max_s = info["max_stars"]
            ok = (f"{C.GREEN}✓{C.RESET}"
                  if info["filled"] == info["total"] and max_s >= target_stars
                  else f"{C.YELLOW}✗{C.RESET}")
            total = info['total']
            self.log(f"{C.DIM}  {ok} Item {item_id}: {total} cái, "
                     f"sao_max={max_s}/{target_stars}{C.RESET}")
            for it in items:
                s = it["stars"]
                sym = f"{C.GREEN}✓{C.RESET}" if s >= target_stars else f"{C.YELLOW}✗{C.RESET}"
                self.log(f"{C.DIM}      {sym} idx={it['index']:>3}  "
                         f"sao={s}/{target_stars}  {it['info'][:30]}{C.RESET}")

    # ═══════════════════════════════════════════════
    # OPEN COMBINE TAB
    # ═══════════════════════════════════════════════

    async def open_combine(self, npc_id: int = 21, map_id: int = 5,
                          menu_item_keywords: Optional[list[str]] = None,
                          submenu_keywords: Optional[list[str]] = None) -> bool:
        """Mở tab combine tại NPC.

        Args:
            npc_id: ID template của NPC (mặc định 21 = Bà Hạt Mít)
            map_id: ID map chứa NPC (mặc định 5 = Đảo Kame)
            menu_item_keywords: Từ khóa tìm menu chức năng chính
            submenu_keywords: Từ khóa tìm sub-menu combine

        Returns: True nếu mở tab combine thành công
        """
        C = self.C
        ctrl = self.ctrl
        menu_keywords = menu_item_keywords or ["pha lê", "pha le", "chức năng", "chuc nang"]
        sub_keywords = submenu_keywords or ["ép sao", "ep sao"]

        # Di chuyển tới map
        if ctrl.tile_map.map_id != map_id:
            self.log(f"{C.DIM}→ Di chuyển tới map {map_id}...{C.RESET}")
            if not await move_to_map(self.acc, map_id, self.log):
                self.log(f"{C.YELLOW}→ Không tới được map {map_id}.{C.RESET}")
                return False

        # Teleport tới NPC
        if not await teleport_to_npc(self.acc, npc_id):
            self.log(f"{C.YELLOW}→ Không tìm thấy NPC {npc_id}.{C.RESET}")
            return False
        await asyncio.sleep(0.05)

        # Mở menu NPC
        ctrl.ui_menu_event.clear()
        await self.acc.service.open_menu_npc(npc_id)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.05)

        opts = ctrl.last_ui_options or []
        self.log(f"{C.DIM}→ Menu NPC {npc_id}: {opts}{C.RESET}")
        if not opts:
            return False

        # Tìm menu chức năng chính
        func_idx = find_menu_option(opts, *menu_keywords)
        if func_idx == -1:
            func_idx = 0
        self.log(f"{C.DIM}→ Chọn '{opts[func_idx]}'.{C.RESET}")

        # Mở sub-menu
        ctrl.ui_menu_event.clear()
        await self.acc.service.confirm_menu_npc(npc_id, func_idx)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.05)

        opts2 = ctrl.last_ui_options or []
        self.log(f"{C.DIM}→ Sub-menu: {opts2}{C.RESET}")
        if not opts2:
            return False

        # Tìm option combine
        combine_idx = -1
        for i, opt in enumerate(opts2):
            ol = opt.lower().replace('\n', ' ')
            for kw in sub_keywords:
                if kw in ol:
                    combine_idx = i
                    break
            if combine_idx != -1:
                break

        if combine_idx == -1:
            # Fallback: tìm "trang bị" nhưng không phải "pha lê"
            for i, opt in enumerate(opts2):
                ol = opt.lower().replace('\n', ' ')
                if "trang bị" in ol and "pha lê" not in ol:
                    combine_idx = i
                    break

        if combine_idx == -1:
            self.log(f"{C.RED}→ Không tìm thấy option combine: {opts2}{C.RESET}")
            return False

        self.log(f"{C.DIM}→ Chọn '{opts2[combine_idx]}'.{C.RESET}")

        # Mở tab combine
        ctrl.ui_menu_event.clear()
        ctrl.combine_event.clear()
        ctrl.combine_result = ""
        await self.acc.service.confirm_menu_npc(npc_id, combine_idx)

        try:
            await asyncio.wait_for(ctrl.combine_event.wait(), timeout=2.0)
            self.log(f"{C.GREEN}→ Tab combine đã mở.{C.RESET}")
        except asyncio.TimeoutError:
            self.log(f"{C.YELLOW}→ Timeout chờ tab combine.{C.RESET}")

        await asyncio.sleep(0.05)
        return True

    # ═══════════════════════════════════════════════
    # OPEN ITEM UPGRADE (radar combine - 441/442)
    # ═══════════════════════════════════════════════

    async def open_item_upgrade(self, npc_id: int = 21, map_id: int = 5) -> bool:
        """Mở tab nâng cấp vật phẩm (dùng cho rada với item 441/442).
        Items 441/442 có ID > 20 nên không dùng được tab "Ép sao trang bị".
        Cần dùng tab khác — thử "Nâng cấp vật phẩm" hoặc "Pha lê hóa trang bị".

        Returns: True nếu mở tab thành công
        """
        C = self.C
        ctrl = self.ctrl

        # Di chuyển tới map
        if ctrl.tile_map.map_id != map_id:
            self.log(f"{C.DIM}→ Di chuyển tới map {map_id}...{C.RESET}")
            if not await move_to_map(self.acc, map_id, self.log):
                self.log(f"{C.YELLOW}→ Không tới được map {map_id}.{C.RESET}")
                return False

        # Teleport tới NPC
        if not await teleport_to_npc(self.acc, npc_id):
            self.log(f"{C.YELLOW}→ Không tìm thấy NPC {npc_id}.{C.RESET}")
            return False
        await asyncio.sleep(0.1)

        # Thử các đường dẫn menu khác nhau
        menu_paths = [
            # Path 1: "Chức năng pha lê" → "Pha lê hóa trang bị"
            {"main_kw": ["pha lê", "pha le", "chức năng", "chuc nang"],
             "sub_kw": ["pha lê hóa", "pha le hoa", "pha lê", "pha le"],
             "has_submenu": True},
            # Path 2: "Chức năng pha lê" → fallback (bất kỳ option nào không phải "ép sao")
            {"main_kw": ["pha lê", "pha le", "chức năng", "chuc nang"],
             "sub_kw": [],  # fallback: chọn option đầu tiên không phải "ép sao"
             "has_submenu": True, "fallback": True},
        ]

        for path_idx, path in enumerate(menu_paths):
            if not self.acc.is_logged_in:
                return False

            self.log(f"{C.DIM}→ Thử menu path {path_idx + 1}...{C.RESET}")

            # Mở menu NPC
            ctrl.ui_menu_event.clear()
            await self.acc.service.open_menu_npc(npc_id)
            try:
                await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.1)

            opts = ctrl.last_ui_options or []
            self.log(f"{C.DIM}  Menu NPC {npc_id}: {opts}{C.RESET}")
            if not opts:
                continue

            # Tìm main option
            main_idx = find_menu_option(opts, *path["main_kw"])
            if main_idx == -1:
                self.log(f"{C.DIM}  Không tìm thấy main option với keywords {path['main_kw']}.{C.RESET}")
                continue

            self.log(f"{C.DIM}  Chọn '{opts[main_idx]}'.{C.RESET}")

            if not path["has_submenu"]:
                # Direct option — confirm và mở tab combine
                ctrl.ui_menu_event.clear()
                ctrl.combine_event.clear()
                ctrl.combine_result = ""
                await self.acc.service.confirm_menu_npc(npc_id, main_idx)
                try:
                    await asyncio.wait_for(ctrl.combine_event.wait(), timeout=3.0)
                    self.log(f"{C.GREEN}→ Tab item upgrade đã mở (path {path_idx + 1}).{C.RESET}")
                    await asyncio.sleep(0.1)
                    return True
                except asyncio.TimeoutError:
                    self.log(f"{C.YELLOW}→ Timeout chờ tab combine.{C.RESET}")
                    continue
            else:
                # Mở sub-menu
                ctrl.ui_menu_event.clear()
                await self.acc.service.confirm_menu_npc(npc_id, main_idx)
                try:
                    await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
                except asyncio.TimeoutError:
                    pass
                await asyncio.sleep(0.1)

                opts2 = ctrl.last_ui_options or []
                self.log(f"{C.DIM}  Sub-menu: {opts2}{C.RESET}")
                if not opts2:
                    continue

                # Tìm sub option
                sub_idx = -1
                if path.get("fallback"):
                    # Fallback: chọn option đầu tiên KHÔNG phải "ép sao"
                    for i, opt in enumerate(opts2):
                        ol = opt.lower().replace('\n', ' ')
                        if "ép sao" not in ol and "ep sao" not in ol:
                            sub_idx = i
                            break
                    if sub_idx == -1:
                        sub_idx = 0
                else:
                    sub_kw = path.get("sub_kw", [])
                    sub_idx = find_menu_option(opts2, *sub_kw)
                    if sub_idx == -1:
                        sub_idx = 0

                self.log(f"{C.DIM}  Chọn '{opts2[sub_idx]}'.{C.RESET}")

                # Mở tab combine
                ctrl.ui_menu_event.clear()
                ctrl.combine_event.clear()
                ctrl.combine_result = ""
                await self.acc.service.confirm_menu_npc(npc_id, sub_idx)
                try:
                    await asyncio.wait_for(ctrl.combine_event.wait(), timeout=3.0)
                    self.log(f"{C.GREEN}→ Tab item upgrade đã mở (path {path_idx + 1}: {opts2[sub_idx]}).{C.RESET}")
                    await asyncio.sleep(0.1)
                    return True
                except asyncio.TimeoutError:
                    self.log(f"{C.YELLOW}→ Timeout chờ tab combine.{C.RESET}")
                    continue

        self.log(f"{C.RED}→ Không mở được tab item upgrade sau {len(menu_paths)} paths.{C.RESET}")
        return False

    # ═══════════════════════════════════════════════
    # DO COMBINE
    # ═══════════════════════════════════════════════

    async def do_combine(self, main_item_id: int,
                         materials: list[tuple[int, int]],
                         max_times: int = 1,
                         npc_id: int = 21,
                         bag_index: int = -1) -> int:
        """Thực hiện combine lặp lại: main + materials → xác nhận → verify.

        Flow:
          send_combine_items → đợi menu (ui_menu_event) → chọn option
          → đợi kết quả combine (combine_event) → verify

        Args:
            main_item_id: ID item chính (trang bị cần ép)
            materials: List (material_id, quantity)
            max_times: Số lần ép tối đa
            npc_id: NPC ID để confirm menu
            bag_index: Index cụ thể trong balo (nếu -1 thì tự tìm first item)

        Returns: Số lần thành công
        """
        C = self.C
        ctrl = self.ctrl
        success = 0

        for round_idx in range(max_times):
            if not self.acc.is_logged_in:
                break

            if round_idx == 0:
                await refresh_inventory(self.acc)

            # Track ALL materials before combine, not just Item 16
            mat_ids = [m[0] for m in materials]
            mat_before = {mid: count_item(self.acc, mid) for mid in mat_ids}

            # ── Tìm main item (theo index cụ thể hoặc first item) ──
            main_idx = bag_index
            if main_idx < 0:
                for idx, item in enumerate(self.acc.char.arr_item_bag or []):
                    if item is not None and item.item_id == main_item_id:
                        main_idx = idx
                        break
            else:
                # Kiểm tra index cụ thể còn tồn tại không
                bag = self.acc.char.arr_item_bag or []
                if main_idx >= len(bag) or bag[main_idx] is None or bag[main_idx].item_id != main_item_id:
                    self.log(f"{C.YELLOW}  Item {main_item_id} tại index {main_idx} không còn.{C.RESET}")
                    break
            if main_idx == -1:
                self.log(f"{C.YELLOW}  Hết item {main_item_id}.{C.RESET}")
                break

            # ── Tìm materials (không trùng index với main) ──
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
                    self.log(f"{C.YELLOW}  Thiếu: item {mat_id} "
                             f"(cần {mat_qty}, có {found}).{C.RESET}")
                    all_ok = False
            if not all_ok:
                break

            self.log(f"{C.DIM}  Lần {round_idx + 1}/{max_times}: "
                     f"indices={all_indices}{C.RESET}")

            # ── Clear state trước khi gửi ──
            ctrl.combine_event.clear()
            ctrl.combine_result = ""
            ctrl.ui_menu_event.clear()
            ctrl.last_ui_options = []
            ctrl.last_npc_template_id = 0

            # ── Gửi combine items ──
            await self.acc.service.send_combine_items(all_indices)

            # ── Server gửi menu confirm (OPEN_UI_CONFIRM cmd 32) ──
            result = None
            try:
                await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                pass

            opts = ctrl.last_ui_options or []

            if opts:
                self.log(f"{C.DIM}  Menu confirm: {opts}{C.RESET}")

                # Chọn option "nâng cấp", tránh "đóng"
                confirm_idx = -1
                close_idx = -1
                for i, opt in enumerate(opts):
                    ol = opt.lower().replace('\n', ' ')
                    if any(kw in ol for kw in ["đóng", "dong", "từ chối", "tu choi"]):
                        close_idx = i
                    elif any(kw in ol for kw in ["nâng cấp", "nang cap", "cần", "can",
                                                  "ngọc", "ngoc", "đồng ý", "dong y",
                                                  "xác nhận", "xac nhan", "cường hóa",
                                                  "cuong hoa"]):
                        confirm_idx = i
                        break

                if confirm_idx == -1:
                    for i, opt in enumerate(opts):
                        if i != close_idx:
                            confirm_idx = i
                            break
                if confirm_idx == -1:
                    confirm_idx = 0

                self.log(f"{C.DIM}  Chọn: '{opts[confirm_idx]}' (index {confirm_idx}){C.RESET}")

                # Gửi xác nhận
                ctrl.combine_event.clear()
                ctrl.combine_result = ""
                ctrl.ui_menu_event.clear()
                ctrl.last_ui_options = []
                await self.acc.service.confirm_menu_npc(npc_id, confirm_idx)

                # Đợi kết quả combine (timeout 5s để server kịp xử lý)
                try:
                    await asyncio.wait_for(ctrl.combine_event.wait(), timeout=5.0)
                    if ctrl.combine_result == "reopen":
                        result = "success"
                    else:
                        result = ctrl.combine_result
                except asyncio.TimeoutError:
                    pass
            else:
                if ctrl.combine_result in ("success", "fail"):
                    result = ctrl.combine_result

            # ── Verify ──
            await refresh_inventory(self.acc)
            mat_after = {mid: count_item(self.acc, mid) for mid in mat_ids}
            mat_consumed = any(mat_after[mid] < mat_before.get(mid, 0) for mid in mat_ids)
            stars_before = self._get_star_count(main_item_id) or 0
            stars_after = self._get_star_count_max(main_item_id) or 0

            if result == "success":
                success += 1
                self.log(f"{C.GREEN}  ✓ Thành công (lần {round_idx + 1}), "
                         f"sao: {stars_before}→{stars_after}{C.RESET}")
            elif result == "fail":
                self.log(f"{C.YELLOW}  ✗ Thất bại (lần {round_idx + 1}).{C.RESET}")
            elif mat_consumed:
                success += 1
                consumed = " ".join(f"{mid}:{mat_before.get(mid,0)}→{mat_after.get(mid,0)}" for mid in mat_ids if mat_after.get(mid,0) < mat_before.get(mid,0))
                self.log(f"{C.GREEN}  ✓ Thành công (lần {round_idx + 1}), "
                         f"mat bị consume ({consumed}).{C.RESET}")
            elif stars_after > stars_before:
                success += 1
                self.log(f"{C.GREEN}  ✓ Sao tăng (lần {round_idx + 1}), "
                         f"sao: {stars_before}→{stars_after}.{C.RESET}")
            else:
                self.log(f"{C.YELLOW}  ? Không xác định (sao: {stars_before}→{stars_after}).{C.RESET}")

            await asyncio.sleep(0.01)

        return success

    # ═══════════════════════════════════════════════
    # TIỆN ÍCH: find item indices
    # ═══════════════════════════════════════════════

    def find_item_indices(self, item_id: int, quantity: int = 1) -> list[int]:
        """Tìm indices của item trong balo."""
        indices = []
        for idx, item in enumerate(self.acc.char.arr_item_bag or []):
            if item is not None and item.item_id == item_id:
                indices.append(idx)
                if len(indices) >= quantity:
                    break
        return indices

    async def send_and_confirm(self, indices: list[int], npc_id: int = 21) -> str:
        """Gửi items lên combine và đợi kết quả.
        Returns: 'success' | 'fail' | 'timeout' | ''
        """
        ctrl = self.ctrl
        ctrl.combine_event.clear()
        ctrl.combine_result = ""
        ctrl.ui_menu_event.clear()
        ctrl.last_ui_options = []

        await self.acc.service.send_combine_items(indices)

        # Đợi menu confirm
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=4.0)
        except asyncio.TimeoutError:
            pass

        opts = ctrl.last_ui_options or []
        if not opts:
            return ctrl.combine_result if ctrl.combine_result in ("success", "fail") else ""

        # Chọn option đầu tiên không phải "Đóng"
        confirm_idx = 0
        for i, opt in enumerate(opts):
            ol = opt.lower().replace('\n', ' ')
            if "đóng" not in ol and "dong" not in ol:
                confirm_idx = i
                break

        ctrl.combine_event.clear()
        ctrl.combine_result = ""
        await self.acc.service.confirm_menu_npc(npc_id, confirm_idx)

        try:
            await asyncio.wait_for(ctrl.combine_event.wait(), timeout=5.0)
            if ctrl.combine_result == "reopen":
                return "success"
            return ctrl.combine_result
        except asyncio.TimeoutError:
            return "timeout"
