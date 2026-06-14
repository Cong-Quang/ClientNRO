import asyncio
import json
import math
import time
from logs.logger_config import logger

REPORT_NPC_MAP = {
    "cui": (12, 19),
    "quy_lao": (0, 21),
    "quy lão": (0, 21),
    "truong_lao": (1, 22),
    "truong lao": (1, 22),
    "vua vegeta": (2, 23),
    "ong gohan": (16, 21),
    "ong moori": (16, 21),
}

BOSS_CONFIG = {
    "kuku": ([68, 69, 70, 71, 72], 12),
    "mập đầu đinh": ([63, 64, 65, 66, 67], 12),
    "map dau dinh": ([63, 64, 65, 66, 67], 12),
    "rambo": ([73, 74, 75, 76, 77], 12),
    "fide": ([110, 111, 112], 12),
    "so 4": ([110, 111, 112], 12),
    "so 3": ([110, 111, 112], 12),
    "so 2": ([110, 111, 112], 12),
    "so 1": ([110, 111, 112], 12),
}


class AutoMainQuest:
    def __init__(self, account):
        self.account = account
        self.is_running = False
        self.task = None
        self.config_data = self._load_config()
        self.blacklist_mobs = {}
        self._boss_map_id = None
        self._boss_step_index = -1
        self._boss_skip = False

    def _load_config(self):
        try:
            with open('maps_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"maps": []}

    # ── NPC Report ──────────────────────────────────────────────

    def _find_report_npc(self, step_name):
        step_lower = step_name.lower()
        report_kw = ["báo cáo", "báo tin", "gặp", "nói chuyện", "hỏi", "report", "talk to"]
        is_report = any(kw in step_lower for kw in report_kw)
        if not is_report:
            for npc_name, (tid, mid) in REPORT_NPC_MAP.items():
                if npc_name in step_lower:
                    return (tid, mid)
            return None
        for npc_name, (tid, mid) in REPORT_NPC_MAP.items():
            if npc_name in step_lower:
                return (tid, mid)
        if "cui" in step_lower or "vegeta" in step_lower:
            return (12, 19)
        return None

    async def _handle_report_npc(self, npc_tid, target_map, step_name):
        username = self.account.username
        char = self.account.char
        self.current_status_msg = f"Báo cáo NPC (Map {target_map})"

        if char.map_id != target_map:
            print(f"[{username}] [AutoQuest] Di chuyển tới Map {target_map} để báo cáo NPC...")
            if not self.account.controller.xmap.is_xmapping:
                await self.account.controller.xmap.start(target_map)
            await asyncio.sleep(2)
            return

        npc_data = None
        for _, info in self.account.controller.npcs.items():
            if info.get('template_id') == npc_tid:
                npc_data = info
                break
        if not npc_data:
            ok = await self.account.controller.movement.teleport_to_npc(npc_tid, search_by_template=True)
            if not ok:
                await asyncio.sleep(2)
                return
        else:
            await self.account.controller.movement.teleport_to(npc_data['x'], npc_data['y'] - 3)
        await asyncio.sleep(0.5)

        cur_idx = char.task.index
        self.account.controller.ui_menu_event.clear()
        await self.account.service.open_menu_npc(npc_tid)
        try:
            await asyncio.wait_for(self.account.controller.ui_menu_event.wait(), timeout=5.0)
            opts = self.account.controller.last_ui_options
            if opts:
                await self.account.service.confirm_menu_npc(npc_tid, 0)
                await asyncio.sleep(1)
        except asyncio.TimeoutError:
            if char.task.index > cur_idx:
                print(f"[{username}] [AutoQuest] Task đã hoàn thành silent.")
        await asyncio.sleep(1)

    # ── Boss Detection ──────────────────────────────────────────

    def _find_boss_in_step(self, step_name):
        step_lower = step_name.lower()
        for boss_name, (spawn_maps, cui_tid) in BOSS_CONFIG.items():
            if boss_name in step_lower:
                return (boss_name, spawn_maps, cui_tid)
        return None

    # ── Boss Task Handler ───────────────────────────────────────

    async def _handle_boss_task(self, boss_name, spawn_maps, cui_tid, step_name):
        username = self.account.username
        char = self.account.char
        task = char.task
        self._boss_step_index = task.index

        if char.c_hp_full < 150000:
            print(f"[{username}] [AutoQuest] ⛔ HP max ({char.c_hp_full:,}) < 150k. Bỏ qua {boss_name}.")
            self.current_status_msg = f"HP {char.c_hp_full:,} < 150k - Bỏ qua"
            self._boss_skip = True
            return
        if char.c_dam_full < 10000:
            print(f"[{username}] [AutoQuest] ⛔ Dame ({char.c_dam_full:,}) < 10k. Bỏ qua {boss_name}.")
            self.current_status_msg = f"Dame {char.c_dam_full:,} < 10k - Bỏ qua"
            self._boss_skip = True
            return
        self._boss_skip = False

        # Đã ở map boss → fight trực tiếp
        if char.map_id in spawn_maps:
            self._boss_map_id = char.map_id
            await self._boss_fight_loop(boss_name, spawn_maps)
            return

        # Chết → hồi sinh và quay map boss cũ
        if char.c_hp == 0:
            print(f"[{username}] [AutoQuest] Chết! Hồi sinh...")
            await self.account.service.return_town_from_dead()
            await asyncio.sleep(3)
            if self._boss_map_id and self._boss_map_id in spawn_maps:
                if not self.account.controller.xmap.is_xmapping:
                    await self.account.controller.xmap.start(self._boss_map_id)
                while self.account.controller.xmap.is_xmapping:
                    await asyncio.sleep(1)
            return

        # Chưa ở map 19 → di chuyển tới 19
        if char.map_id != 19:
            print(f"[{username}] [AutoQuest] Di chuyển tới Map 19 (Cui)...")
            if not self.account.controller.xmap.is_xmapping:
                await self.account.controller.xmap.start(19)
            await asyncio.sleep(2)
            return

        # Đã ở Map 19 → dùng Cui tele
        cui_npc = None
        for _, info in self.account.controller.npcs.items():
            if info.get('template_id') == 12:
                cui_npc = info
                break
        if not cui_npc:
            await asyncio.sleep(1)
            return

        await self.account.controller.movement.teleport_to(cui_npc['x'], cui_npc['y'] - 3)
        await asyncio.sleep(0.5)

        print(f"[{username}] [AutoQuest] Cui → tele tới {boss_name}...")
        self.account.controller.ui_menu_event.clear()
        await self.account.service.open_menu_npc(12)
        try:
            await asyncio.wait_for(self.account.controller.ui_menu_event.wait(), timeout=5.0)
            opts = self.account.controller.last_ui_options
            target_idx = 0
            for i, opt in enumerate(opts):
                if boss_name.lower() in opt.lower():
                    target_idx = i
                    break
            await self.account.service.confirm_menu_npc(12, target_idx)
            await asyncio.sleep(2)
        except asyncio.TimeoutError:
            pass

        await asyncio.sleep(1)
        self._boss_map_id = char.map_id
        self._boss_step_index = task.index
        await self._boss_fight_loop(boss_name, spawn_maps)

    # ── Boss Fight Loop ─────────────────────────────────────────

    async def _boss_fight_loop(self, boss_name, spawn_maps):
        username = self.account.username
        char = self.account.char
        task = char.task
        atk_count = 0
        death_count = 0
        last_pl_time = 0
        last_hp = 0
        same_hp_count = 0
        MAX_DEATHS = 3
        MAX_ATTACKS = 500

        print(f"[{username}] [AutoQuest] ⚔️ Fight {boss_name} | HP_MAX:{char.c_hp_full} | Dame:{char.c_dam_full}")

        while self.is_running:
            # Task chuyển bước → boss đã chết
            if task.index != self._boss_step_index:
                print(f"[{username}] [AutoQuest] ✅ Task đã chuyển! {boss_name} đã chết!")
                self.current_status_msg = f"Hoàn thành: {boss_name}"
                return

            # Chết
            if char.c_hp == 0:
                death_count += 1
                if death_count >= MAX_DEATHS:
                    print(f"[{username}] [AutoQuest] ⛔ Chết {MAX_DEATHS} lần. Dừng {boss_name}.")
                    self.current_status_msg = f"Chết {MAX_DEATHS} lần - Dừng"
                    return
                self.current_status_msg = f"Chết lần {death_count} - Hồi sinh..."
                await self.account.service.return_town_from_dead()
                await asyncio.sleep(3)
                if self._boss_map_id and self._boss_map_id in spawn_maps:
                    if not self.account.controller.xmap.is_xmapping:
                        await self.account.controller.xmap.start(self._boss_map_id)
                    while self.account.controller.xmap.is_xmapping:
                        await asyncio.sleep(1)
                await asyncio.sleep(1)
                atk_count = 0
                continue

            # Request player list mỗi 2s để update HP boss
            now = time.time()
            if now - last_pl_time > 2:
                await self.account.service.request_players()
                last_pl_time = now

            # Tìm boss
            target_boss = None
            target_cid = None
            for cid, cdata in self.account.controller.chars.items():
                if boss_name.lower() in cdata.get('name', '').lower():
                    target_boss = cdata
                    target_cid = cid
                    break

            if not target_boss:
                atk_count += 1
                if atk_count > MAX_ATTACKS:
                    print(f"[{username}] [AutoQuest] ⚠️ Không tìm thấy {boss_name} sau {atk_count} đòn. Reset.")
                    self._boss_map_id = None
                    return
                self.current_status_msg = f"Đang tìm {boss_name}..."
                await asyncio.sleep(0.5)
                continue

            boss_hp = target_boss.get('hp', 0)
            boss_x = target_boss.get('x', 0)
            boss_y = target_boss.get('y', 0)

            # Boss HP=0 → đã chết
            if boss_hp <= 0:
                print(f"[{username}] [AutoQuest] {boss_name} HP=0! Chờ task update...")
                self.current_status_msg = f"{boss_name} HP=0"
                await asyncio.sleep(3)
                if task.index == self._boss_step_index:
                    self._boss_map_id = None
                return

            # HP không đổi quá lâu → boss đã chạy
            if boss_hp == last_hp:
                same_hp_count += 1
                if same_hp_count > 50:
                    print(f"[{username}] [AutoQuest] ⚠️ HP không đổi ({boss_hp}) {same_hp_count} đòn. Reset.")
                    self._boss_map_id = None
                    return
            else:
                same_hp_count = 0
                last_hp = boss_hp

            # Teleport cực gần boss
            dist = math.sqrt((boss_x - char.cx)**2 + (boss_y - char.cy)**2)
            if dist > 5:
                char.cx = boss_x
                char.cy = boss_y
                char.cxSend = char.cx
                char.cySend = char.cy
                await self.account.service.char_move()
                await asyncio.sleep(0.1)

            # Face boss
            char.cdir = 1 if char.cx <= boss_x else -1

            # Attack
            skill = self.account.controller.auto_play.find_best_skill()
            if skill:
                await self.account.service.select_skill(skill.template.id)
            await self.account.service.attack_player(target_cid)
            atk_count += 1

            if atk_count % 10 == 0:
                print(f"[{username}] [AutoQuest] ⚔️ {boss_name} HP:{boss_hp} deaths:{death_count} #{atk_count}")
            self.current_status_msg = f"{boss_name} HP:{boss_hp} #{atk_count}"

            await asyncio.sleep(0.1)

    # ── Mob Kill ────────────────────────────────────────────────

    def _find_map_by_mob_name(self, step_name):
        step_lower = step_name.lower()
        matches = []
        for map_info in self.config_data.get("maps", []):
            for mob in map_info.get("mobs", []):
                if mob["mob_name"].lower() in step_lower:
                    matches.append({
                        "map_id": map_info["map_id"],
                        "mob_id": mob["mob_id"],
                        "count": mob.get("count", 1),
                    })
        if matches:
            matches.sort(key=lambda x: x["count"], reverse=True)
            return matches[0]["map_id"], matches[0]["mob_id"]
        return None, None

    def _get_nearest_valid_mob(self, target_mob_id):
        mobs = self.account.controller.mobs
        char = self.account.char
        best = None
        best_dist = float('inf')
        now = time.time()
        for mid, mob in mobs.items():
            if mob.template_id != target_mob_id or mob.hp <= 0 or mob.status <= 1:
                continue
            if mid in self.blacklist_mobs and now < self.blacklist_mobs[mid]:
                continue
            d = math.hypot(mob.x - char.cx, mob.y - char.cy)
            if d < best_dist:
                best_dist = d
                best = mob
        return best

    # ── Start / Stop ────────────────────────────────────────────

    async def start(self):
        if self.is_running:
            return
        self.config_data = self._load_config()
        self.is_running = True
        self._boss_map_id = None
        self._boss_step_index = -1
        self._boss_skip = False
        self.current_status_msg = "Khởi động..."
        print(f"[{self.account.username}] [AutoQuest] Bật tự động làm nhiệm vụ chính.")
        self.task = asyncio.create_task(self._quest_loop())

    async def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        self.current_status_msg = "Đã tắt"
        print(f"[{self.account.username}] [AutoQuest] Tắt tự động làm nhiệm vụ chính.")
        if self.task and not self.task.done():
            self.task.cancel()

    def get_status(self):
        if not self.is_running:
            return "Đang tắt"
        return getattr(self, 'current_status_msg', "Không rõ")

    # ── Main Loop ───────────────────────────────────────────────

    async def _quest_loop(self):
        while self.is_running:
            try:
                if not self.account.is_logged_in or not self.account.char.task:
                    await asyncio.sleep(1)
                    continue

                task = self.account.char.task
                if task.index >= len(task.sub_names):
                    await asyncio.sleep(5)
                    continue

                step_name = task.sub_names[task.index]

                # 1. NPC Report
                npc_result = self._find_report_npc(step_name)
                if npc_result:
                    await self._handle_report_npc(npc_result[0], npc_result[1], step_name)
                    await asyncio.sleep(0.5)
                    continue

                # 2. Boss Hunt
                boss_result = self._find_boss_in_step(step_name)
                if boss_result:
                    if self._boss_step_index >= 0 and task.index > self._boss_step_index:
                        self._boss_step_index = -1
                        self._boss_skip = False
                    if not self._boss_skip:
                        await self._handle_boss_task(boss_result[0], boss_result[1], boss_result[2], step_name)
                    else:
                        self.current_status_msg = f"Bỏ qua boss (stats不够)"
                        await asyncio.sleep(5)
                    await asyncio.sleep(0.3)
                    continue

                # 3. Mob Kill
                target_map, target_mob = self._find_map_by_mob_name(step_name)
                if target_map is not None:
                    if self.account.char.map_id != target_map:
                        self.current_status_msg = f"Di chuyển Map {target_map}"
                        if not self.account.controller.xmap.is_xmapping:
                            await self.account.controller.xmap.start(target_map)
                        await asyncio.sleep(2)
                        continue

                    mob = self._get_nearest_valid_mob(target_mob)
                    if mob:
                        self.account.char.cx = mob.x
                        self.account.char.cy = mob.y
                        await self.account.service.char_move()
                        await asyncio.sleep(0.05)

                        atk_time = time.time()
                        last_hp = mob.hp
                        while self.is_running and mob.hp > 0 and mob.status > 1:
                            await self.account.service.send_player_attack(mob_ids=[mob.mob_id])
                            if time.time() - atk_time > 5:
                                if mob.hp == last_hp:
                                    self.blacklist_mobs[mob.template_id] = time.time() + 30
                                    break
                                last_hp = mob.hp
                                atk_time = time.time()
                            await asyncio.sleep(0.3)
                            if self.account.char.task.index > task.index:
                                break
                    else:
                        self.current_status_msg = f"Chờ quái hồi sinh..."
                        await asyncio.sleep(1)
                else:
                    if getattr(self, '_last_missing', None) != step_name:
                        print(f"[{self.account.username}] [AutoQuest] Thiếu data map: '{step_name}'")
                        self._last_missing = step_name
                    await asyncio.sleep(10)

                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[{self.account.username}] [AutoQuest] Lỗi: {e}")
                await asyncio.sleep(2)
