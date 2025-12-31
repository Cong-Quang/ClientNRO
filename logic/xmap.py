import time
import asyncio
import random
from typing import List, Dict, Optional
from logs.logger_config import logger
from network.service import Service

class NextMap:
    def __init__(self, map_id: int, npc_id: int = -1, select_name: str = "", select_name2: str = "", select_name3: str = "", 
                 walk: bool = False, x: int = -1, y: int = -1, item_id: int = -1, 
                 index_npc: int = -1, index_npc2: int = -1, index_npc3: int = -1):
        self.map_id = map_id
        self.npc_id = npc_id
        self.select_name = select_name
        self.select_name2 = select_name2
        self.select_name3 = select_name3
        self.walk = walk
        self.x = x
        self.y = y
        self.item_id = item_id
        self.index_npc = index_npc
        self.index_npc2 = index_npc2
        self.index_npc3 = index_npc3

class XMap:
    def __init__(self, controller):
        self.controller = controller
        self.link_maps: Dict[int, List[NextMap]] = {}
        self.is_xmapping = False
        self.target_map_id = -1
        self.path = []
        self.last_update = 0
        self.update_interval = 1.0 # 1 second delay between actions
        self.processing_map_change = False
        self.expected_next_map_id = -1
        self.last_action_time = 0
        
        self.dangerous_maps = set()
        self.zone_changed_in_map = False
        
        self.init_map_data()

    def init_map_data(self):
        # Map Groups for Directional Logic
        self.map_groups = [
            [42, 21, 0, 1, 2, 3, 4, 5, 6, 27, 28, 29, 30, 47, 42, 24, 53, 58, 59, 60, 61, 62, 55, 56, 54, 57], # Trai Dat
            [43, 22, 7, 8, 9, 11, 12, 13, 10, 31, 32, 33, 34, 43, 25], # Namek
            [44, 23, 14, 15, 16, 17, 18, 20, 19, 35, 36, 37, 38, 52, 44, 26, 84, 113, 127, 129], # Xayda
            [102, 92, 93, 94, 96, 97, 98, 99, 100, 103], # Tuong Lai
            [109, 108, 107, 110, 106, 105], # Cold
            [68, 69, 70, 71, 72, 64, 65, 63, 66, 67, 73, 74, 75, 76, 77, 81, 82, 83, 79, 80, 131, 132, 133], # Nappa
            [46, 45, 48, 50, 154, 155, 166], # Thap Leo
            [153, 156, 157, 158, 159], # Manh Vo
            [149, 147, 152, 151, 148], # Khi Gas
            [173, 174, 175] # Noel
        ]

        # DataXmap.cs Transcription
        self.add_link_maps(0, 21)
        self.add_link_maps(1, 47)
        self.add_link_maps(47, 111)
        self.add_link_maps(2, 24)
        self.add_link_maps(5, 29)
        self.add_link_maps(7, 22)
        self.add_link_maps(9, 25)
        self.add_link_maps(13, 33)
        self.add_link_maps(14, 23)
        self.add_link_maps(16, 26)
        self.add_link_maps(20, 37)
        self.add_link_maps(39, 21)
        self.add_link_maps(40, 22)
        self.add_link_maps(41, 23)
        self.add_link_maps(109, 105)
        self.add_link_maps(109, 106)
        self.add_link_maps(106, 107)
        self.add_link_maps(108, 105)
        self.add_link_maps(80, 105)
        self.add_link_maps(84, 104)
        self.add_link_maps(139, 140)

        self.add_link_maps(3, 27, 28, 29, 30)
        self.add_link_maps(11, 31, 32, 33, 34)
        self.add_link_maps(17, 35, 36, 37, 38)
        self.add_link_maps(109, 108, 107, 110, 106)
        self.add_link_maps(47, 46, 45, 48)
        self.add_link_maps(131, 132, 133)
        self.add_link_maps(160, 161, 162, 163)

        self.add_link_maps(42, 0, 1, 2, 3, 4, 5, 6)
        self.add_link_maps(43, 22, 7, 8, 9, 11, 12, 13, 10)
        self.add_link_maps(52, 44, 14, 15, 16, 17, 18, 20, 19)
        self.add_link_maps(53, 58, 59, 60, 61, 62, 55, 56, 54, 57)
        self.add_link_maps(68, 69, 70, 71, 72, 64, 65, 63, 66, 67, 73, 74, 75, 76, 77, 81, 82, 83, 79, 80)
        self.add_link_maps(102, 92, 93, 94, 96, 97, 98, 99, 100, 103)

        self.add_link_maps(153, 156, 157, 158, 159)
        self.add_link_maps(46, 45, 48, 50, 154, 155, 166)
        self.add_link_maps(149, 147, 152, 151, 148)
        self.add_link_maps(173, 174, 175)
        self.add_link_maps(7, 197)

        # NPC Links
        self.add_npc_link(19, 68, 12, "Đến Nappa", select_name3="Đồng ý")
        self.add_npc_link(68, 19, 12)
        self.add_npc_link(19, 109, 12, "Đến Cold")
        
        # Portal Group 24, 25, 26, 84
        self.add_portal_group(24, [25, 26, 84], 10, [0, 1, 2])
        self.add_portal_group(25, [24, 26, 84], 11, [0, 1, 2])
        self.add_portal_group(26, [24, 25, 84], 12, [0, 1, 2])
        self.add_portal_group(84, [24, 25, 26], 10, [0, 0, 0])

        self.add_npc_link(27, 102, 38, index_npc=1)
        self.add_npc_link(28, 102, 38, index_npc=1)
        self.add_npc_link(29, 102, 38, index_npc=1)
        self.add_npc_link(102, 27, 38, index_npc=1)

        self.add_npc_link(27, 53, 25, "Vào (miễn phí)", select_name2="Tham Gia", select_name3="OK")

        self.add_npc_link(52, 127, 44, "OK")
        self.add_npc_link(52, 129, 23, "Đại Hội Võ Thuật Lần thứ 23")
        self.add_npc_link(52, 113, 23, "Giải Siêu Hạng")
        self.add_npc_link(113, 52, 22, "Về Đại Hội Võ Thuật")
        self.add_npc_link(127, 52, 44, "Về Đại Hội Võ Thuật")
        self.add_npc_link(129, 52, 23, "Về Đại Hội Võ Thuật")

        self.add_npc_link(80, 131, 60, index_npc=0)
        self.add_npc_link(131, 80, 60, index_npc=1)

        self.add_npc_link(5, 153, 13, "Nói chuyện", "Về khu vực bang")
        self.add_npc_link(153, 5, 10, "Đảo Kame")
        self.add_npc_link(153, 156, 47, "OK")

        self.add_npc_link(45, 48, 19, index_npc=3)
        self.add_npc_link(48, 45, 20, index_npc=3, index_npc2=0)
        self.add_npc_link(48, 50, 20, index_npc=3, index_npc2=1)
        self.add_npc_link(50, 48, 44, index_npc=0)
        self.add_npc_link(50, 154, 44, index_npc=1)
        self.add_npc_link(154, 50, 55, index_npc=0)
        self.add_npc_link(154, 155, 44, index_npc=1)
        self.add_npc_link(155, 154, 44, index_npc=0)

        self.add_npc_link(155, 166, walk=True, x=1400, y=600)
        self.add_npc_link(46, 47, walk=True, x=80, y=700)
        self.add_npc_link(45, 46, walk=True, x=80, y=700)
        self.add_npc_link(46, 45, walk=True, x=380, y=90)

        self.add_npc_link(0, 149, 67, "OK", select_name2="Đồng ý")

        self.add_npc_link(24, 139, 63, index_npc=0)
        self.add_npc_link(139, 24, 63, index_npc=0)
        
        self.add_npc_link(126, 19, 53, "OK")
        self.add_npc_link(19, 126, 53, "OK")
        self.add_npc_link(52, 181, 44, "Bình hút năng lượng", "OK")
        self.add_npc_link(181, 52, 44, "Về nhà")

        # Item usage links
        self.add_npc_link(160, 161, item_id=992)
        self.add_npc_link(181, 52, item_id=1852)

    def add_link_maps(self, *args):
        """Creates a sequential chain of links: args[0]<->args[1]<->args[2]..."""
        maps = args
        for i in range(len(maps)):
            u = maps[i]
            if u not in self.link_maps:
                self.link_maps[u] = []
            
            if i > 0:
                v_prev = maps[i-1]
                self.link_maps[u].append(NextMap(v_prev))
            
            if i < len(maps) - 1:
                v_next = maps[i+1]
                self.link_maps[u].append(NextMap(v_next))

    def add_npc_link(self, current, next_map, npc_id=-1, select_name="", select_name2="", select_name3="", 
                     walk=False, x=-1, y=-1, item_id=-1, index_npc=-1, index_npc2=-1, index_npc3=-1):
        if current not in self.link_maps: self.link_maps[current] = []
        self.link_maps[current].append(NextMap(
            next_map, npc_id, select_name, select_name2, select_name3, walk, x, y, item_id, index_npc, index_npc2, index_npc3
        ))

    def add_portal_group(self, from_map, to_maps, npc_id, indices):
        for i, to_map in enumerate(to_maps):
            idx = indices[i] if i < len(indices) else -1
            self.add_npc_link(from_map, to_map, npc_id, index_npc=idx)

    def get_map_direction(self, current_id: int, next_id: int) -> str:
        """Determines if next map is Left, Right, or Center relative to current map."""
        for group in self.map_groups:
            if current_id in group and next_id in group:
                # Find indices. Note: duplicates exist (e.g. 42), find adjacent pair.
                indices_curr = [i for i, x in enumerate(group) if x == current_id]
                indices_next = [i for i, x in enumerate(group) if x == next_id]
                
                for ic in indices_curr:
                    for inext in indices_next:
                        if inext == ic + 1: return "Right" # Next in list -> Right
                        if inext == ic - 1: return "Left"  # Prev in list -> Left
        
        return "Center"

    async def start(self, map_id: int):
        self.is_xmapping = True
        self.target_map_id = map_id
        current_map = self.controller.tile_map.map_id
        
        # Reset dangerous maps state?
        # Requirement says "next time", so we probably shouldn't clear it immediately if we want persistence across retries.
        # But if we start a NEW xmap command, maybe we should?
        # Let's keep it persistent for the session life (until restart bot) or clear it?
        # For "lần sau tới đó", implying within the same logical session.
        # Let's Clear it for a fresh Start command to avoid stale data from long ago.
        self.dangerous_maps.clear()
        
        logger.info(f"XMap Started: {current_map} -> {map_id}")
        
        if current_map == map_id:
            self.finish()
            return

        self.path = self.find_path(current_map, map_id)
        if not self.path:
            logger.error(f"Cannot find path from {current_map} to {map_id}")
            self.finish()
        else:
            logger.info(f"Path found: {self.path}")
            asyncio.create_task(self.run_loop())

    async def run_loop(self):
        while self.is_xmapping:
            await self.update()
            await asyncio.sleep(self.update_interval)

    def finish(self):
        self.is_xmapping = False
        self.processing_map_change = False
        logger.info("XMap Finished.")

    def find_path(self, start, end):
        if start == end: return [start]
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            (vertex, path) = queue.pop(0)
            if vertex not in self.link_maps: continue
            
            for next_map_obj in self.link_maps[vertex]:
                neighbor = next_map_obj.map_id
                if neighbor not in visited:
                    if neighbor == end:
                        return path + [neighbor]
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    async def update(self):
        if not self.is_xmapping: return
        
        # Simple throttle
        if time.time() - self.last_update < self.update_interval:
            return
        self.last_update = time.time()

        current_map = self.controller.tile_map.map_id
        
        # Reset zone change flag if we moved to a new map
        if not self.path or current_map != self.path[0]:
             self.zone_changed_in_map = False

        # Handle Dangerous Map (Anti-Boss) logic
        if current_map in self.dangerous_maps and not self.zone_changed_in_map:
            current_zone = self.controller.map_info.get('zone', 0)
            next_zone = random.randint(0, 10)
            while next_zone == current_zone:
                next_zone = random.randint(0, 10)
            
            logger.warning(f"XMap: Entering dangerous map {current_map}. Switching to zone {next_zone} to avoid boss.")
            await self.controller.account.service.request_change_zone(next_zone)
            self.zone_changed_in_map = True
            return # Wait for zone change

        if current_map == self.target_map_id:
            self.finish()
            return
            
        # Check map change state
        if self.processing_map_change:
            if current_map == self.expected_next_map_id:
                 logger.info(f"Map changed to {current_map}. Continuing XMap.")
                 self.processing_map_change = False
                 self.last_action_time = 0
            elif time.time() - self.last_action_time > 5.0: # 5s timeout
                 logger.warning("Map change timeout. Retrying...")
                 self.processing_map_change = False
            else:
                 return # Wait for map change
        
        if not self.path:
             self.path = self.find_path(current_map, self.target_map_id)
             if not self.path:
                 self.finish()
                 return

        if self.path[0] != current_map:
            if current_map in self.path:
                idx = self.path.index(current_map)
                self.path = self.path[idx:]
            else:
                self.path = self.find_path(current_map, self.target_map_id)
                if not self.path:
                    self.finish()
                    return

        if len(self.path) < 2:
            return 

        next_map_id = self.path[1]
        
        connection = None
        if current_map in self.link_maps:
            for nm in self.link_maps[current_map]:
                if nm.map_id == next_map_id:
                    connection = nm
                    break
        
        if connection:
            await self.process_next_map(connection)
        else:
            logger.error(f"No connection found from {current_map} to {next_map_id}")
            self.finish()

    def handle_death(self):
        """Called when the character dies."""
        if self.is_xmapping:
            current_map = self.controller.tile_map.map_id
            logger.warning(f"XMap: Character died on map {current_map}. Marking as dangerous.")
            self.dangerous_maps.add(current_map)

    async def process_next_map(self, next_map: NextMap):
        current_map_id = self.controller.tile_map.map_id
        if current_map_id != self.path[0]:
             logger.warning(f"XMap: Off track! Current: {current_map_id}, Expected Start: {self.path[0]}")
             self.processing_map_change = False
             return

        action_performed = False
        if next_map.npc_id != -1:
            action_performed = await self.handle_npc_move(next_map)
        elif next_map.walk:
            await self.handle_walk_move(next_map)
            action_performed = True
        elif next_map.item_id != -1:
            await self.handle_item_move(next_map)
            action_performed = True # Assuming item use triggers something
        else:
            await self.handle_waypoint_move(next_map)
            action_performed = True

        if action_performed:
            # Wait for map change to complete
            start_wait = time.time()
            while self.controller.tile_map.map_id == current_map_id:
                if time.time() - start_wait > 5.0:
                    logger.warning("Map change timeout in process_next_map.")
                    break
                await asyncio.sleep(0.5)
            
            self.processing_map_change = True
            self.expected_next_map_id = next_map.map_id
            self.last_action_time = time.time()

    async def handle_waypoint_move(self, next_map: NextMap):
        waypoints = self.controller.tile_map.waypoints
        if not waypoints:
            logger.warning("No waypoints found on this map.")
            return

        current_map_id = self.controller.tile_map.map_id
        next_map_id = next_map.map_id
        
        direction = self.get_map_direction(current_map_id, next_map_id)
        
        # Sort waypoints by X position
        sorted_wps = sorted(waypoints, key=lambda w: w.center_x)
        
        target_wp = None
        
        # Override for Map 7 -> 197 (User Request: Waypoint #3)
        if current_map_id == 7 and next_map_id == 197:
            if len(waypoints) >= 3:
                target_wp = waypoints[2] # Index 2 = Waypoint 3

        # Override for Map 7 -> 43 (via Map 22)
        if current_map_id == 7 and next_map_id == 43:
             direction = self.get_map_direction(current_map_id, 22)

        if target_wp is None:
            # Base Maps (Home bases) often require entering a specific waypoint (Center)
            BASE_MAPS = {42, 43, 44}
            if next_map_id in BASE_MAPS:
                 # Try to find an 'enter' or 'offline' waypoint (usually center)
                 for wp in sorted_wps:
                     if wp.is_enter or wp.is_offline:
                         target_wp = wp
                         break
            
            # Directional Logic
            if target_wp is None:
                if direction == "Left":
                    target_wp = sorted_wps[0] # Left-most
                elif direction == "Right":
                    target_wp = sorted_wps[-1] # Right-most
                elif direction == "Center":
                    # Middle waypoint if available, otherwise fallback
                    if len(sorted_wps) > 1:
                        target_wp = sorted_wps[len(sorted_wps) // 2]
                    else:
                        target_wp = sorted_wps[0]
        
        # Ultimate fallback
        if target_wp is None and waypoints:
            target_wp = waypoints[0]

        logger.info(f"XMap: Moving {current_map_id}->{next_map_id} (Dir: {direction}). Selected WP: {target_wp.name} ({target_wp.min_x}-{target_wp.max_x})")
        await self.controller.movement.enter_waypoint(waypoint_index=waypoints.index(target_wp))

    async def handle_npc_move(self, next_map: NextMap) -> bool:
        # 1. Teleport to NPC first - Retry logic for async loading
        target_npc = None
        max_retries = 10
        for _ in range(max_retries):
            # We need to find the specific NPC instance ID, not just template ID for opening menu
            for npc in self.controller.npcs.values():
                if npc['template_id'] == next_map.npc_id:
                    target_npc = npc
                    break
            
            if target_npc:
                logger.info(f"Found NPC Template {next_map.npc_id} -> ID {target_npc['id']}")
                await self.controller.movement.teleport_to(target_npc['x'], target_npc['y'] - 3)
                break
            #await asyncio.sleep(0.1)
        else:
            return False # NPC not found
        
        # 2. Open Menu using the MAP ENTITY ID (target_npc['id'])
        # Empirical evidence: Cmd 33 requires Instance ID (e.g. 2), NOT Template ID (e.g. 11/12).
        await self.controller.account.service.open_menu_npc(target_npc['id'])
        
        # Wait for menu to open
        await asyncio.sleep(1.0)
        
        # 3. Select Options
        if next_map.index_npc != -1:
             # confirmMenu takes TEMPLATE ID.
             await self.controller.account.service.confirm_menu_npc(next_map.npc_id, next_map.index_npc)
             if next_map.index_npc2 != -1:
                 await asyncio.sleep(1.0)
                 await self.controller.account.service.confirm_menu_npc(next_map.npc_id, next_map.index_npc2)
        
        return True

    async def handle_walk_move(self, next_map: NextMap):
        char = self.controller.account.char
        char.cx = next_map.x
        char.cy = next_map.y
        await self.controller.account.service.char_move()

    async def handle_item_move(self, next_map: NextMap):
        pass