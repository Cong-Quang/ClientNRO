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
        char = Char.my_charz()
        speed = 10 # Pixels per tick (approx)
        
        try:
            while True:
                dx = tx - char.cx
                dy = ty - char.cy
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist <= speed:
                    char.cx = tx
                    char.cy = ty
                    await Service.gI().char_move()
                    break
                
                # Normalize and scale
                vx = (dx / dist) * speed
                vy = (dy / dist) * speed
                
                char.cx += int(vx)
                char.cy += int(vy)
                
                # Determine direction
                if dx > 0: char.cdir = 1
                else: char.cdir = -1
                
                await Service.gI().char_move()
                await asyncio.sleep(0.1) # 100ms per step
                
        except asyncio.CancelledError:
            logger.info("Movement cancelled.")
        except Exception as e:
            logger.error(f"Error in movement loop: {e}")
        finally:
            self.is_moving = False

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
                if wp.name == waypoint_name:
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

        logger.info(f"Moving to Waypoint: {target_wp.name} at ({target_wp.center_x}, {target_wp.center_y})")
        
        # Move to waypoint
        await self.move_to(target_wp.center_x, target_wp.center_y)
        
        # Send change map request
        if target_wp.is_offline:
             logger.info("Sending Get Map Offline request...")
             await Service.gI().get_map_offline()
        elif target_wp.is_enter:
             logger.info("Sending Request Change Map...")
             await Service.gI().request_change_map()
        else:
            # Waypoint might be just a transition (like Left/Right map edge)
            # In NRO, stepping on the edge often triggers map change automatically via server check,
            # or client sends requestChangeMap when inside the zone.
            logger.info("Arrived at waypoint. Sending Change Map request just in case.")
            await Service.gI().request_change_map()

