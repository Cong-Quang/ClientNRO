from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Waypoint:
    min_x: int
    min_y: int
    max_x: int
    max_y: int
    is_enter: bool
    is_offline: bool
    name: str
    
    @property
    def center_x(self) -> int:
        return (self.min_x + self.max_x) // 2
    
    @property
    def center_y(self) -> int:
        return self.max_y

class TileMap:
    # Tile Types (from C# TileMap.cs)
    T_EMPTY = 0
    T_TOP = 2
    T_LEFT = 4
    T_RIGHT = 8
    T_TREE = 16
    T_WATERFALL = 32
    T_WATERFLOW = 64
    T_TOPFALL = 128
    T_OUTSIDE = 256
    T_DOWN1PIXEL = 512
    T_BRIDGE = 1024
    T_UNDERWATER = 2048
    T_SOLIDGROUND = 4096
    T_BOTTOM = 8192
    T_DIE = 16384
    T_HEBI = 32768
    T_BANG = 65536
    T_JUM8 = 131072
    T_NT0 = 262144
    T_NT1 = 524288
    T_CENTER = 1

    def __init__(self):
        self.map_id: int = 0
        self.planet_id: int = 0
        self.tile_id: int = 0
        self.bg_id: int = 0
        self.type_map: int = 0
        self.map_name: str = ""
        self.zone_id: int = 0
        self.waypoints: List[Waypoint] = []
        self.tmw: int = 0
        self.tmh: int = 0
        self.size: int = 24
        self.maps: List[int] = [] # Tile IDs
        self.types: List[int] = [] # Tile Types (Collision flags)

    def set_map_info(self, map_id, planet_id, tile_id, bg_id, type_map, map_name, zone_id):
        self.map_id = map_id
        self.planet_id = planet_id
        self.tile_id = tile_id
        self.bg_id = bg_id
        self.type_map = type_map
        self.map_name = map_name
        self.zone_id = zone_id

    def add_waypoint(self, wp: Waypoint):
        self.waypoints.append(wp)

    def is_tile_type_at(self, px: int, py: int, t: int) -> bool:
        """Check if tile at pixel (px, py) has type t."""
        try:
            # If we don't have map data, return False (assume clear)
            # Or safe default?
            if not self.types:
                return False
            
            # Simple bounds check
            if px < 0 or py < 0: return False
            
            idx = (py // self.size) * self.tmw + (px // self.size)
            if idx < 0 or idx >= len(self.types):
                return False
                
            return (self.types[idx] & t) == t
        except Exception:
            return False
