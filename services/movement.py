import asyncio
import math
import logging
from model.game_objects import Char
from model.map_objects import Waypoint, TileMap
from network.service import Service

logger = logging.getLogger(__name__)

class MovementService:
    def __init__(self, controller):
        self.controller = controller
        self.is_moving = False
        self._move_task: asyncio.Task = None

    async def move_to(self, target_x: int, target_y: int):
        """
        Moves the character to target coordinates.
        Uses simple linear interpolation for now.
        """
        self.stop_moving()
        self.is_moving = True
        self._move_task = asyncio.create_task(self._move_loop(target_x, target_y))
        await self._move_task

    def stop_moving(self):
        if self._move_task and not self._move_task.done():
            self._move_task.cancel()
        self.is_moving = False

    async def _move_loop(self, tx: int, ty: int):
        char = self.controller.account.char
        speed = 10 # Pixels per tick (approx)
        
        try:
            while True:
                dx = tx - char.cx
                dy = ty - char.cy
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist <= speed:
                    char.cx = tx
                    char.cy = ty
                    await self.controller.account.service.char_move()
                    break
                
                # Normalize and scale
                vx = (dx / dist) * speed
                vy = (dy / dist) * speed
                
                char.cx += int(vx)
                char.cy += int(vy)
                
                # Determine direction
                if dx > 0: char.cdir = 1
                else: char.cdir = -1
                
                await self.controller.account.service.char_move()
                await asyncio.sleep(0.1) # 100ms per step
                
        except asyncio.CancelledError:
            logger.info("Movement cancelled.")
        except Exception as e:
            logger.error(f"Error in movement loop: {e}")
        finally:
            self.is_moving = False

    async def teleport_to(self, target_x: int, target_y: int):
        """
        Teleports the character to target coordinates immediately with 'wiggle' to ensure server sync.
        """
        self.stop_moving()
        char = self.controller.account.char
        
        # 1. Main Teleport
        char.cx = target_x
        char.cy = target_y
        await self.controller.account.service.char_move()
        
        # 2. Wiggle (Simulation of landing/adjusting)
        char.cy = target_y + 1
        await self.controller.account.service.char_move()
        
        char.cy = target_y
        await self.controller.account.service.char_move()
        
        # 3. Wait for server to register position
        await asyncio.sleep(0.3)

    async def enter_waypoint(self, waypoint_name: str = None, waypoint_index: int = None):
        """
        Move to a waypoint and attempt to enter it.
        """
        tile_map: TileMap = self.controller.tile_map
        target_wp: Waypoint = None

        if not tile_map.waypoints:
            logger.warning("No waypoints in current map.")
            return

        if waypoint_index is not None:
            if 0 <= waypoint_index < len(tile_map.waypoints):
                target_wp = tile_map.waypoints[waypoint_index]
        elif waypoint_name:
            for wp in tile_map.waypoints:
                # Use 'in' for a more robust match, as server names can have extra characters.
                if waypoint_name in wp.name:
                    target_wp = wp
                    break
        else:
            # Default to first available Enter/Offline waypoint
            for wp in tile_map.waypoints:
                if wp.is_enter or wp.is_offline:
                    target_wp = wp
                    break
        
        if not target_wp:
            logger.warning(f"Waypoint not found (Name: {waypoint_name}, Index: {waypoint_index})")
            return

        logger.info(f"Teleporting to Waypoint: {target_wp.name} at ({target_wp.center_x}, {target_wp.center_y})")
        
        # Teleport to waypoint
        await self.teleport_to(target_wp.center_x, target_wp.center_y)
        
        # Send change map request
        if target_wp.is_offline:
             logger.info("Sending Get Map Offline request...")
             await self.controller.account.service.get_map_offline()
        elif target_wp.is_enter:
             logger.info("Sending Request Change Map...")
             await self.controller.account.service.request_change_map()
        else:
            logger.info("Arrived at waypoint. Sending Change Map request just in case.")
            await self.controller.account.service.request_change_map()

    async def teleport_to_npc(self, npc_template_id: int) -> bool:
        """
        Finds an NPC by template ID and teleports to them.
        Returns True if successful, False otherwise.
        """
        # Search through values since npcs is keyed by index
        target_npc = None
        for npc in self.controller.npcs.values():
            if npc['template_id'] == npc_template_id:
                target_npc = npc
                break
        
        if target_npc:
            logger.info(f"Teleporting to NPC {npc_template_id} at ({target_npc['x']}, {target_npc['y']})")
            # Teleport slightly above the NPC (y-3) like C# source
            await self.teleport_to(target_npc['x'], target_npc['y'] - 3)
            return True
        else:
            # logger.warning(f"NPC {npc_template_id} not found on this map. Available NPCs: {list(self.controller.npcs.values())}")
            logger.warning(f"NPC {npc_template_id} not found on this map.")
            return False

