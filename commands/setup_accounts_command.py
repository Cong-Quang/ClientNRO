"""
Setup Accounts Command - Tự động setup tài khoản mới hoàn chỉnh
Flow: Login → Tạo NV → Về nhà → NPC (ngọc + giftcode) → Farm đậu → Mua bùa
"""
import asyncio
from commands.base_command import Command
from logs.logger_config import TerminalColors
from config import Config
from typing import Any

NPC_GOHAN = 0
NPC_MOORI = 2
NPC_PARAGUS = 1
NPC_DAU_THAN = 4
NPC_BA_HAT_MIT = 21

HOME_MAPS = {0: 21, 1: 22, 2: 23}
HOME_NPC = {0: NPC_GOHAN, 1: NPC_MOORI, 2: NPC_PARAGUS}

TARGET_BEAN_ID = 595  # PEA_TEMP[9] trong MagicTree.java
BEAN_ITEM_IDS = [13, 60, 61, 62, 63, 64, 65, 352, 523, 595]

MAP_VACH_NUI = 43  # Vách núi Moori

GIFTCODES = ["tdstudio"]

# Item IDs bùa cần mua (bùa 1 tháng)
BUA_ITEM_IDS = [213, 214, 215, 216, 217, 218, 219, 522, 671, 672]


class SetupAccountsCommand(Command):
    def __init__(self, manager=None):
        self.C = TerminalColors
        self.manager = manager

    def _log(self, acc, msg: str):
        C = self.C
        prefix = f"[{C.YELLOW}{acc.username}{C.RESET}]"
        if msg.startswith("  "):
            msg = msg[2:]
        print(f"{prefix} {msg}")

    async def execute(self, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        C = self.C

        if not self.manager:
            print(f"{C.RED}Lỗi: Không tìm thấy AccountManager.{C.RESET}")
            return False

        if len(parts) < 3:
            print(f"{C.YELLOW}Cú pháp: setup_accounts <start_index> <end_index> [force]{C.RESET}")
            print(f"  Ví dụ: {C.CYAN}setup_accounts 0 9{C.RESET}")
            print(f"        {C.CYAN}setup_accounts 0 9 force{C.RESET}")
            return False

        try:
            start_idx = int(parts[1])
            end_idx = int(parts[2])
        except ValueError:
            print(f"{C.RED}Chỉ số không hợp lệ.{C.RESET}")
            return False

        if start_idx < 0 or end_idx >= len(self.manager.accounts) or start_idx > end_idx:
            print(f"{C.RED}Khoảng không hợp lệ (0-{len(self.manager.accounts) - 1}).{C.RESET}")
            return False

        force = False
        if len(parts) >= 4:
            if parts[3].lower() in ('force', 'again', 'reset', 'true', '1'):
                force = True

        accounts = self.manager.accounts[start_idx:end_idx + 1]
        print(f"{C.CYAN}=== SETUP {len(accounts)} TÀI KHOẢN ({start_idx}-{end_idx}) ĐỒNG THỜI (TỐI ĐA 5 ACC) ==={C.RESET}")
        if force:
            print(f"{C.RED}!!! CHẾ ĐỘ FORCE SETUP ĐƯỢC BẬT (Thiết lập lại) !!!{C.RESET}")
        print(f"{C.DIM}Login → NV → Nhà → NPC ngọc/giftcode → Farm đậu → Mua bùa{C.RESET}")
        print()

        sem = asyncio.Semaphore(5)

        async def setup_with_sem(acc, idx):
            async with sem:
                return await self._setup_one(acc, idx, end_idx, C, force=force)

        tasks = [setup_with_sem(acc, start_idx + i) for i, acc in enumerate(accounts)]
        results = await asyncio.gather(*tasks)

        success = sum(1 for r in results if r)
        fail = len(results) - success

        print()
        print(f"{C.CYAN}=== HOÀN TẤT ==={C.RESET}")
        print(f"  {C.GREEN}OK: {success}{C.RESET}  |  {C.RED}Fail: {fail}{C.RESET}")
        if accounts:
            self.manager.command_target = start_idx
            print(f"  Target: {C.YELLOW}{start_idx} ({accounts[0].username}){C.RESET}")
        return False

    # ================================================================
    # MAIN FLOW
    # ================================================================
    async def _ensure_logged_in(self, acc, C) -> bool:
        if acc.is_logged_in:
            return True
        self._log(acc, f"{C.YELLOW}→ Mất kết nối, đang đăng nhập lại...{C.RESET}")
        for attempt in range(3):
            try:
                if await acc.login():
                    if await self._wait_game_ready(acc, C):
                        self._log(acc, f"{C.GREEN}→ Đăng nhập lại thành công.{C.RESET}")
                        return True
            except Exception as e:
                self._log(acc, f"{C.RED}  Thử lại {attempt+1} lỗi: {e}{C.RESET}")
            await asyncio.sleep(3)
        return False

    async def _setup_one(self, acc, idx, end_idx, C, force=False) -> bool:
        C = self.C

        self._log(acc, f"{C.CYAN}=== Bắt đầu Setup (Acc {idx}/{end_idx}) ==={C.RESET}")

        # 1. Login (skip nếu đã online)
        self._log(acc, "[1/8] Login...")
        if not await self._ensure_logged_in(acc, C):
            self._log(acc, f"{C.RED}→ Login fail.{C.RESET}")
            return False

        # 2. Đợi game
        self._log(acc, "[2/8] Đợi game...")
        if acc.char.c_power > 0:
            self._log(acc, f"{C.GREEN}→ Đã có NV (SM={acc.char.c_power}).{C.RESET}")
        else:
            self._log(acc, f"{C.DIM}→ NV mới, chờ tạo...{C.RESET}")
            if not await self._wait_game_ready(acc, C):
                return False
            self._log(acc, f"{C.GREEN}→ Tạo NV OK (map {acc.controller.tile_map.map_id}).{C.RESET}")

        # 3. Về nhà
        if not await self._ensure_logged_in(acc, C): return False
        self._log(acc, "[3/8] Về nhà...")
        await self._go_home(acc, C)
        await asyncio.sleep(1)

        # 4. NPC: Nhận ngọc xanh
        if not await self._ensure_logged_in(acc, C): return False
        npc_id = HOME_NPC.get(acc.char.gender, NPC_MOORI)
        self._log(acc, f"[4/8] NPC nhận ngọc (template={npc_id})...")
        
        # Teleport đến NPC nhà trước khi tương tác
        if not await self._teleport_to_npc(acc, npc_id):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy NPC để nhận ngọc.{C.RESET}")
            return False
            
        # Mở menu để kiểm tra options một cách động
        ctrl = acc.controller
        ctrl.ui_menu_event.clear()
        await acc.service.open_menu_npc(npc_id)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.3)
        
        opts = ctrl.last_ui_options
        target_opt_idx = -1
        if opts:
            for i, opt in enumerate(opts):
                opt_lower = opt.lower()
                if "ngọc" in opt_lower or "xanh" in opt_lower:
                    target_opt_idx = i
                    break
        
        if target_opt_idx != -1:
            self._log(acc, f"{C.DIM}→ Tìm thấy tùy chọn nhận ngọc xanh ở vị trí {target_opt_idx} (options: {opts}){C.RESET}")
            await acc.service.confirm_menu_npc(npc_id, target_opt_idx)
            await asyncio.sleep(0.5)
        else:
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy tùy chọn nhận ngọc xanh trong {opts}, dùng mặc định option 2.{C.RESET}")
            await acc.service.confirm_menu_npc(npc_id, 2)
            await asyncio.sleep(0.5)

        # 5. Giftcode - check đã có item giftcode chưa
        if not await self._ensure_logged_in(acc, C): return False
        has_gift = self._has_giftcode_items(acc)
        self._log(acc, "[5/8] Giftcode...")
        if has_gift and not force:
            self._log(acc, f"{C.GREEN}→ Đã có item giftcode, bỏ qua.{C.RESET}")
        else:
            if force and has_gift:
                self._log(acc, f"{C.YELLOW}→ Force: Tiến hành nhập lại giftcode...{C.RESET}")
            for code in GIFTCODES:
                if not await self._ensure_logged_in(acc, C): return False
                await self._npc_giftcode(acc, npc_id, code, C)

        # 6. Farm đậu thần - check đủ chưa
        if not await self._ensure_logged_in(acc, C): return False
        bean_count = self._count_beans(acc)
        self._log(acc, f"[6/8] Farm đậu thần (hiện có: {bean_count})...")
        if bean_count >= 990 and not force:
            self._log(acc, f"{C.GREEN}→ Đủ đậu ({bean_count}>=990), bỏ qua.{C.RESET}")
        else:
            if force and bean_count >= 990:
                self._log(acc, f"{C.YELLOW}→ Force: Thiết lập lại/thu hoạch thêm đậu...{C.RESET}")
            await self._farm_magic_tree(acc, C, target_count=990)

        # 7. Mua bùa - check đã có chưa
        if not await self._ensure_logged_in(acc, C): return False
        has_bua = self._has_bua_items(acc)
        self._log(acc, "[7/8] Mua bùa...")
        if has_bua and not force:
            self._log(acc, f"{C.GREEN}→ Đã có bùa, bỏ qua.{C.RESET}")
        else:
            if force and has_bua:
                self._log(acc, f"{C.YELLOW}→ Force: Kiểm tra mua bùa còn thiếu...{C.RESET}")
            await self._buy_bua(acc, C)

        # 8. Tổng kết
        if not await self._ensure_logged_in(acc, C): return False
        bean_final = self._count_beans(acc)
        bua_count = self._count_bua_items(acc)
        self._log(acc, f"{C.GREEN}✓ Setup xong tài khoản này.{C.RESET}")
        self._log(acc, f"{C.DIM}  Đậu: {bean_final} | Bùa: {bua_count}/{len(BUA_ITEM_IDS)}{C.RESET}")
        return True

    # ================================================================
    # WAIT GAME
    # ================================================================
    async def _wait_game_ready(self, acc, C, timeout=30) -> bool:
        for sec in range(timeout):
            if not acc.is_logged_in:
                return False
            await asyncio.sleep(1)
            if acc.controller.tile_map.map_id > 0 and acc.char.c_power > 0:
                return True
            if sec == 8:
                try:
                    await acc.service.request_me_info()
                except Exception:
                    pass
            if sec == 15:
                try:
                    await acc.service.request_change_map()
                except Exception:
                    pass
        self._log(acc, f"{C.YELLOW}→ Timeout map={acc.controller.tile_map.map_id} power={acc.char.c_power}{C.RESET}")
        return acc.controller.tile_map.map_id > 0

    # ================================================================
    # GO HOME
    # ================================================================
    async def _go_home(self, acc, C):
        home_map = HOME_MAPS.get(acc.char.gender, 22)
        if acc.controller.tile_map.map_id == home_map:
            self._log(acc, f"{C.GREEN}→ Đã ở nhà (map {home_map}).{C.RESET}")
            return
        try:
            await acc.controller.xmap.start(home_map)
            for _ in range(45):
                if not acc.is_logged_in:
                    break
                await asyncio.sleep(1)
                if not acc.controller.xmap.is_xmapping:
                    break
                if acc.controller.tile_map.map_id == home_map:
                    acc.controller.xmap.stop()
                    break
            if acc.controller.tile_map.map_id == home_map:
                self._log(acc, f"{C.GREEN}→ Về nhà OK.{C.RESET}")
            else:
                self._log(acc, f"{C.YELLOW}→ Đang ở map {acc.controller.tile_map.map_id}.{C.RESET}")
        except Exception as e:
            self._log(acc, f"{C.RED}→ Lỗi xmap: {e}{C.RESET}")

    # ================================================================
    # NPC: CHỌN OPTION (mở menu → chọn option → server xử lý)
    # ================================================================
    async def _npc_select_option(self, acc, npc_id, option, C, desc=""):
        if not await self._teleport_to_npc(acc, npc_id):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy NPC.{C.RESET}")
            return
        ctrl = acc.controller
        ctrl.ui_menu_event.clear()
        await acc.service.open_menu_npc(npc_id)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.3)
        await acc.service.confirm_menu_npc(npc_id, option)
        await asyncio.sleep(0.5)
        self._log(acc, f"{C.GREEN}→ {desc or f'Đã chọn option {option}'}.{C.RESET}")

    # ================================================================
    # NPC: GIFTCODE (menu 0 → input form → send code)
    # ================================================================
    async def _npc_giftcode(self, acc, npc_id, code, C):
        ctrl = acc.controller
        
        # Thử mở NPC nhà trước
        if not await self._teleport_to_npc(acc, npc_id):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy NPC nhà.{C.RESET}")
            return False

        ctrl.ui_menu_event.clear()
        ctrl.input_form_received.clear()
        await acc.service.open_menu_npc(npc_id)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.3)

        opts = ctrl.last_ui_options
        giftcode_opt_idx = -1
        if opts:
            for i, opt in enumerate(opts):
                opt_lower = opt.lower()
                if "giftcode" in opt_lower or "quà tặng" in opt_lower or "mã" in opt_lower:
                    giftcode_opt_idx = i
                    break

        if giftcode_opt_idx != -1:
            self._log(acc, f"{C.GREEN}→ Tìm thấy Giftcode tại NPC nhà ở vị trí {giftcode_opt_idx}.{C.RESET}")
            await acc.service.confirm_menu_npc(npc_id, giftcode_opt_idx)
            try:
                await asyncio.wait_for(ctrl.input_form_received.wait(), timeout=3.0)
                await asyncio.sleep(0.3)
                await acc.service.send_client_input([code])
                await asyncio.sleep(1.0)
                self._log(acc, f"{C.GREEN}→ Đã gửi giftcode '{code}' tại NPC nhà.{C.RESET}")
                return True
            except asyncio.TimeoutError:
                self._log(acc, f"{C.YELLOW}→ Chờ form nhập giftcode tại NPC nhà quá giờ.{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ NPC nhà không có tùy chọn Giftcode (Options: {opts}). Di chuyển tới Santa (template=39)...{C.RESET}")
            
        # Fallback tới Santa (template 39)
        santa_map = {0: 5, 1: 13, 2: 20}.get(acc.char.gender, 5)
        if ctrl.tile_map.map_id != santa_map:
            self._log(acc, f"{C.DIM}→ Đang di chuyển tới map Santa {santa_map}...{C.RESET}")
            try:
                await ctrl.xmap.start(santa_map)
                for _ in range(45):
                    if not acc.is_logged_in:
                        break
                    await asyncio.sleep(1)
                    if not ctrl.xmap.is_xmapping:
                        break
                    if ctrl.tile_map.map_id == santa_map:
                        ctrl.xmap.stop()
                        break
            except Exception as e:
                self._log(acc, f"{C.RED}→ Lỗi xmap tới Santa: {e}{C.RESET}")
                
        if ctrl.tile_map.map_id != santa_map:
            self._log(acc, f"{C.RED}→ Không di chuyển được tới map Santa {santa_map}.{C.RESET}")
            return False

        # Tìm và teleport đến Santa
        if not await self._teleport_to_npc(acc, 39):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy Santa tại map {santa_map}.{C.RESET}")
            return False

        # Mở menu Santa
        ctrl.ui_menu_event.clear()
        ctrl.input_form_received.clear()
        await acc.service.open_menu_npc(39)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.3)

        santa_opts = ctrl.last_ui_options
        santa_opt_idx = -1
        if santa_opts:
            for i, opt in enumerate(santa_opts):
                opt_lower = opt.lower()
                if "giftcode" in opt_lower or "quà tặng" in opt_lower or "mã" in opt_lower:
                    santa_opt_idx = i
                    break

        if santa_opt_idx != -1:
            self._log(acc, f"{C.GREEN}→ Tìm thấy Giftcode tại Santa ở vị trí {santa_opt_idx}.{C.RESET}")
            await acc.service.confirm_menu_npc(39, santa_opt_idx)
            try:
                await asyncio.wait_for(ctrl.input_form_received.wait(), timeout=3.0)
                await asyncio.sleep(0.3)
                await acc.service.send_client_input([code])
                await asyncio.sleep(1.0)
                self._log(acc, f"{C.GREEN}→ Đã gửi giftcode '{code}' tại Santa.{C.RESET}")
                return True
            except asyncio.TimeoutError:
                self._log(acc, f"{C.YELLOW}→ Chờ form nhập giftcode tại Santa quá giờ.{C.RESET}")
        else:
            self._log(acc, f"{C.RED}→ Không tìm thấy tùy chọn Giftcode tại Santa (Options: {santa_opts}).{C.RESET}")
        return False

    # ================================================================
    # MAGIC TREE FARMING
    # ================================================================
    async def _farm_magic_tree(self, acc, C, target_count=990):
        ctrl = acc.controller
        
        # Đảm bảo phải về nhà trước khi farm đậu
        if not await self._ensure_logged_in(acc, C): return
        await self._go_home(acc, C)
        await asyncio.sleep(1)
        
        bean_count = self._count_beans(acc)
        self._log(acc, f"{C.DIM}→ Đậu: {bean_count}/{target_count}{C.RESET}")
        if bean_count >= target_count:
            self._log(acc, f"{C.GREEN}→ Đủ đậu.{C.RESET}")
            return

        prev_count = bean_count
        stuck = 0
        for r in range(300):
            if not acc.is_logged_in:
                self._log(acc, f"{C.RED}→ Mất kết nối, dừng farm đậu.{C.RESET}")
                break
            ctrl.magic_tree_menu.clear()
            ctrl.magic_tree_options = []
            await self._teleport_to_npc(acc, NPC_DAU_THAN)
            await asyncio.sleep(0.3)
            ctrl.ui_menu_event.clear()
            await acc.service.open_menu_npc(NPC_DAU_THAN)
            try:
                await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.5)

            opts = ctrl.magic_tree_options or ctrl.last_ui_options if hasattr(ctrl, 'last_ui_options') else []
            if not opts:
                await asyncio.sleep(2)
                continue

            lo = [o.lower().replace('\n', ' ') for o in opts]
            has_fast = any('kết hạt' in o for o in lo)
            has_harvest = any('thu' in o and 'hoạch' in o for o in lo)

            if has_fast:
                fi = next((i for i, o in enumerate(lo) if 'kết hạt' in o), None)
                if fi is not None:
                    self._log(acc, f"{C.DIM}[{r+1}] Kết hạt nhanh →{C.RESET}")
                    await acc.service.confirm_menu_npc(NPC_DAU_THAN, fi)
                    await asyncio.sleep(1.5)
            elif has_harvest:
                self._log(acc, f"{C.DIM}[{r+1}] Thu hoạch →{C.RESET}")
                await acc.service.confirm_menu_npc(NPC_DAU_THAN, 0)
                await asyncio.sleep(1.5)
            else:
                await acc.service.confirm_menu_npc(NPC_DAU_THAN, 0)
                await asyncio.sleep(1.5)

            bean_count = self._count_beans(acc)
            if r % 5 == 0 or bean_count >= target_count:
                self._log(acc, f"{C.DIM}  Đậu: {bean_count}/{target_count}{C.RESET}")
                bag_items = [f"ID={item.item_id} Qty={item.quantity}" for item in acc.char.arr_item_bag if item is not None]
                self._log(acc, f"{C.DIM}  Bag items: {', '.join(bag_items)}{C.RESET}")
            if bean_count >= target_count:
                break

            if bean_count == prev_count:
                stuck += 1
                if stuck >= 10:
                    await asyncio.sleep(3)
                    stuck = 0
            else:
                stuck = 0
            prev_count = bean_count

        bean_count = self._count_beans(acc)
        if bean_count >= target_count:
            self._log(acc, f"{C.GREEN}→ Đủ đậu: {bean_count}.{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ Đậu: {bean_count}/{target_count}.{C.RESET}")

    def _count_beans(self, acc):
        count = 0
        for item in acc.char.arr_item_bag:
            if item is not None and item.item_id in BEAN_ITEM_IDS:
                count += item.quantity
        return count

    def _count_item(self, acc, item_id):
        count = 0
        for item in acc.char.arr_item_bag:
            if item is not None and item.item_id == item_id:
                count += item.quantity
        return count

    def _has_giftcode_items(self, acc):
        """Kiểm tra đã có item giftcode chưa (thỏi vàng 457, ngọc 381-385)"""
        for item in acc.char.arr_item_bag:
            if item is not None and item.item_id in (457, 381, 382, 383, 384, 385, 386):
                return True
        return False

    def _has_bua_items(self, acc):
        """Kiểm tra đã có đủ 10 bùa 1 tháng chưa"""
        return self._count_bua_items(acc) >= len(BUA_ITEM_IDS)

    def _count_bua_items(self, acc):
        """Đếm số loại bùa đã có"""
        found = set()
        for item in acc.char.arr_item_bag:
            if item is not None and item.item_id in BUA_ITEM_IDS:
                found.add(item.item_id)
        return len(found)

    # ================================================================
    # MUA BÙA TẠI BÀ HẠT MÍT
    # ================================================================
    async def _buy_bua(self, acc, C):
        ctrl = acc.controller

        # Di chuyển đến vách núi Moori
        if acc.controller.tile_map.map_id != MAP_VACH_NUI:
            try:
                await acc.controller.xmap.start(MAP_VACH_NUI)
                for _ in range(45):
                    if not acc.is_logged_in:
                        break
                    await asyncio.sleep(1)
                    if not acc.controller.xmap.is_xmapping:
                        break
                    if acc.controller.tile_map.map_id == MAP_VACH_NUI:
                        acc.controller.xmap.stop()
                        break
                if acc.controller.tile_map.map_id != MAP_VACH_NUI:
                    self._log(acc, f"{C.YELLOW}→ Không đến được vách núi.{C.RESET}")
                    return
                self._log(acc, f"{C.GREEN}→ Đã đến vách núi.{C.RESET}")
            except Exception as e:
                self._log(acc, f"{C.RED}→ Lỗi xmap: {e}{C.RESET}")
                return
        else:
            self._log(acc, f"{C.GREEN}→ Đã ở vách núi.{C.RESET}")

        await asyncio.sleep(1)

        # Tìm và teleport đến Bà Hạt Mít
        npc_found = await self._teleport_to_npc(acc, NPC_BA_HAT_MIT)
        if not npc_found:
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy Bà Hạt Mít.{C.RESET}")
            return

        await asyncio.sleep(0.5)

        # Mở menu Bà Hạt Mít
        ctrl.ui_menu_event.clear()
        await acc.service.open_menu_npc(NPC_BA_HAT_MIT)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.3)

        # Chọn option 2: Cửa hàng bùa
        self._log(acc, f"{C.DIM}→ Mở cửa hàng bùa...{C.RESET}")
        ctrl.ui_menu_event.clear()
        await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, 2)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.3)

        # Chọn option 2: Bùa 1 tháng
        self._log(acc, f"{C.DIM}→ Chọn bùa 1 tháng...{C.RESET}")
        await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, 2)
        await asyncio.sleep(1)

        # Mua từng item bùa chưa có
        bought = 0
        existing_buas = {item.item_id for item in acc.char.arr_item_bag if item is not None}
        for item_id in BUA_ITEM_IDS:
            if item_id in existing_buas:
                continue
            try:
                await acc.service.buy_item(0, item_id)
                bought += 1
                await asyncio.sleep(0.3)
            except Exception:
                pass

        if bought > 0:
            self._log(acc, f"{C.GREEN}→ Đã mua {bought} loại bùa.{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ Không mua được bùa.{C.RESET}")

    # ================================================================
    # TELEPORT TO NPC
    # ================================================================
    async def _teleport_to_npc(self, acc, npc_id):
        npc_data = self._find_npc(acc, npc_id)
        if npc_data:
            x, y = npc_data.get('x', 100), npc_data.get('y', 100)
            await acc.controller.movement.teleport_to(x, y - 3)
            await asyncio.sleep(0.5)
            return True
        try:
            result = await acc.controller.movement.teleport_to_npc(npc_id, search_by_template=True)
            if result:
                await asyncio.sleep(0.5)
                return True
        except Exception:
            pass
        return False

    def _find_npc(self, acc, npc_id):
        npcs = acc.controller.npcs
        # Tìm theo template_id trước để tránh đụng độ với key id của map
        for _, npc_data in npcs.items():
            if npc_data.get('template_id') == npc_id:
                return npc_data
        if npc_id in npcs:
            return npcs[npc_id]
        return None
