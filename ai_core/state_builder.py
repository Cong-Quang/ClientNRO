"""
State Builder - Convert Game State to Neural Network Input Vector with Temporal Context
Pure Python - Zero Dependencies
Extracts and normalizes game data into 60-dimensional feature vector (3 frames × 20D)
"""

from typing import List, Tuple
from collections import deque
import math
import time


class StateBuilder:
    """
    Converts game state (from controller) into normalized feature vector with temporal context.
    Output: 60-dimensional float vector (3 frames × 20D base features)
    
    Temporal context helps AI recognize:
    - HP/MP trends (increasing/decreasing)
    - Mob movement patterns
    - Combat momentum
    """
    
    def __init__(self, state_dim: int = 20, history_frames: int = 3):
        self.base_state_dim = state_dim  # 20D per frame
        self.history_frames = history_frames  # 3 frames
        self.state_dim = state_dim * history_frames  # 60D total
        
        # State history buffer (stores last 3 frames)
        self.state_history = deque(maxlen=history_frames)
        
        # Combat tracking for new features
        self.damage_taken_history = deque(maxlen=20)  # (timestamp, damage)
        self.damage_dealt_history = deque(maxlen=20)  # (timestamp, damage)
        self.last_kill_time = 0.0
        self.last_hp = None  # Track HP changes
        
        # Normalization constants
        self.MAX_HP = 100000  # Max HP for normalization
        self.MAX_MP = 50000   # Max MP for normalization
        self.MAX_DISTANCE = 1000  # Max distance for normalization
        self.MAX_COORDS = 2000    # Max map coordinates
    
    def build_state(self, controller) -> List[float]:
        """
        Build temporal state vector from game controller.
        
        Returns 60D vector: [frame_t-2, frame_t-1, frame_t] (3 frames × 20D)
        
        Base features per frame (20 dims):
        0: HP ratio (c_hp / c_hp_full)
        1: MP ratio (c_mp / c_mp_full)
        2-3: Position (cx, cy) normalized
        4-5: Nearest mob distance (dx, dy) normalized
        6: Nearest mob HP ratio
        7: Mob count in range
        8-9: Skill cooldown status (2 skills)
        10: Is character dead (0/1)
        11: Pet status (has pet: 0/1)
        12-13: Distance to waypoint/target
        14-19: Reserved for future features
        
        Temporal context enables AI to detect:
        - HP trend: frame_t[0] > frame_t-1[0] = healing
        - Mob approaching: frame_t[4] < frame_t-1[4] = getting closer
        - Combat momentum: consecutive damage = aggressive combat
        """
        # Build current frame (20D)
        current_frame = self._build_single_frame(controller)
        
        # Add to history
        self.state_history.append(current_frame)
        
        # Build temporal state (60D)
        if len(self.state_history) < self.history_frames:
            # Pad with current frame if not enough history
            temporal_state = []
            for _ in range(self.history_frames - len(self.state_history)):
                temporal_state.extend(current_frame)
            for frame in self.state_history:
                temporal_state.extend(frame)
        else:
            # Concatenate all frames: [t-2, t-1, t]
            temporal_state = []
            for frame in self.state_history:
                temporal_state.extend(frame)
        
        return temporal_state
    
    def _build_single_frame(self, controller) -> List[float]:
        """Build single 20D state frame (internal helper)"""
        state = [0.0] * self.base_state_dim
        
        try:
            char = controller.account.char
            
            # Feature 0: HP ratio
            state[0] = self._normalize_ratio(char.c_hp, char.c_hp_full)
            
            # Feature 1: MP ratio
            state[1] = self._normalize_ratio(char.c_mp, char.c_mp_full)
            
            # Feature 2-3: Position normalized
            state[2] = self._normalize_coord(char.cx)
            state[3] = self._normalize_coord(char.cy)
            
            # Find nearest mob
            nearest_mob, mob_distance = self._find_nearest_mob(controller, char)
            
            if nearest_mob:
                # Feature 4-5: Distance to nearest mob (dx, dy)
                dx = nearest_mob.x - char.cx
                dy = nearest_mob.y - char.cy
                state[4] = self._normalize_distance(dx)
                state[5] = self._normalize_distance(dy)
                
                # Feature 6: Nearest mob HP ratio
                hp_val = max(1, nearest_mob.hp)
                state[6] = self._normalize_ratio(hp_val, nearest_mob.max_hp)
            else:
                state[4] = 0.0
                state[5] = 0.0
                state[6] = 0.0
            
            # Feature 7: Mob count in range (200px)
            state[7] = self._normalize_count(
                self._count_mobs_in_range(controller, char, 200)
            )
            
            # Feature 8-9: Skill cooldown
            state[8] = 1.0  # Skill 0 ready (placeholder)
            state[9] = 1.0  # Skill 1 ready (placeholder)
            
            # Feature 10: Is dead
            state[10] = 1.0 if char.is_die else 0.0
            
            # Feature 11: Has pet
            state[11] = 1.0 if char.have_pet else 0.0
            
            # Feature 12-13: Reserved for waypoint/target distance
            state[12] = 0.5
            state[13] = 0.5
            
            # Feature 14: Mob count in 100px (close range density)
            state[14] = self._normalize_count(
                self._count_mobs_in_range(controller, char, 100),
                max_count=10
            )
            
            # Feature 15: Mob count in 300px (far range density)
            state[15] = self._normalize_count(
                self._count_mobs_in_range(controller, char, 300),
                max_count=20
            )
            
            # Feature 16: Average mob HP in 200px range
            state[16] = self._get_average_mob_hp(controller, char, 200)
            
            # Feature 17: Recent damage taken (last 1 second)
            state[17] = self._get_recent_damage_taken()
            
            # Feature 18: Recent damage dealt (last 1 second)
            state[18] = self._get_recent_damage_dealt()
            
            # Feature 19: Time since last kill
            state[19] = self._get_time_since_kill()
            
        except Exception as e:
            print(f"[StateBuilder] Error building frame: {e}")
            state = [0.0] * self.base_state_dim
        
        return state
    
    def _find_nearest_mob(self, controller, char) -> Tuple:
        """Find nearest alive mob and distance"""
        nearest_mob = None
        min_distance = float('inf')
        
        try:
            for mob_id, mob in controller.mobs.items():
                # Visual-Only Targeting: 
                # Include if Status > 0 (even if HP=0).
                if mob.status <= 0 or mob.is_mob_me:
                    continue
                
                # Calculate distance
                dx = mob.x - char.cx
                dy = mob.y - char.cy
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_mob = mob
        except:
            pass
        
        return nearest_mob, min_distance
    
    def _count_mobs_in_range(self, controller, char, range_px: int) -> int:
        """Count alive mobs within range"""
        count = 0
        try:
            for mob_id, mob in controller.mobs.items():
                if mob.status <= 0 or mob.is_mob_me:
                    continue
                
                dx = mob.x - char.cx
                dy = mob.y - char.cy
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance <= range_px:
                    count += 1
        except:
            pass
        
        return count
    
    def _normalize_ratio(self, current: float, maximum: float) -> float:
        """Normalize ratio to [0, 1]"""
        if maximum <= 0:
            return 0.0
        return min(1.0, max(0.0, current / maximum))
    
    def _normalize_coord(self, coord: float) -> float:
        """Normalize coordinate to [0, 1]"""
        return min(1.0, max(0.0, coord / self.MAX_COORDS))
    
    def _normalize_distance(self, distance: float) -> float:
        """Normalize distance to [-1, 1]"""
        return max(-1.0, min(1.0, distance / self.MAX_DISTANCE))
    
    def _normalize_count(self, count: int, max_count: int = 20) -> float:
        """Normalize count to [0, 1]"""
        return min(1.0, count / max_count)
    
    def _get_average_mob_hp(self, controller, char, range_px: int) -> float:
        """Get average HP ratio of mobs in range"""
        try:
            mobs_in_range = []
            for mob_id, mob in controller.mobs.items():
                if mob.status <= 0 or mob.is_mob_me:
                    continue
                
                dx = mob.x - char.cx
                dy = mob.y - char.cy
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance <= range_px:
                    hp_ratio = self._normalize_ratio(max(1, mob.hp), mob.max_hp)
                    mobs_in_range.append(hp_ratio)
            
            if mobs_in_range:
                return sum(mobs_in_range) / len(mobs_in_range)
            return 0.0
        except:
            return 0.0
    
    def _get_recent_damage_taken(self) -> float:
        """Get damage taken in last 1 second, normalized"""
        try:
            current_time = time.time()
            recent_damage = sum(
                dmg for t, dmg in self.damage_taken_history 
                if current_time - t < 1.0
            )
            # Normalize by typical max HP (assume 100k max)
            return min(1.0, recent_damage / 10000)
        except:
            return 0.0
    
    def _get_recent_damage_dealt(self) -> float:
        """Get damage dealt in last 1 second, normalized"""
        try:
            current_time = time.time()
            recent_damage = sum(
                dmg for t, dmg in self.damage_dealt_history 
                if current_time - t < 1.0
            )
            # Normalize by typical damage output (10k per second is high)
            return min(1.0, recent_damage / 10000)
        except:
            return 0.0
    
    def _get_time_since_kill(self) -> float:
        """Get time since last kill, normalized to 30 seconds"""
        try:
            if self.last_kill_time == 0:
                return 1.0  # No kills yet
            current_time = time.time()
            time_since = current_time - self.last_kill_time
            return min(1.0, time_since / 30.0)
        except:
            return 1.0
    
    # Public methods for tracking combat events
    def record_damage_taken(self, amount: float):
        """Record damage taken for feature tracking"""
        self.damage_taken_history.append((time.time(), amount))
    
    def record_damage_dealt(self, amount: float):
        """Record damage dealt for feature tracking"""
        self.damage_dealt_history.append((time.time(), amount))
    
    def record_kill(self):
        """Record mob kill for feature tracking"""
        self.last_kill_time = time.time()


# Example usage
if __name__ == "__main__":
    print("Testing StateBuilder...")
    
    # Mock controller for testing
    class MockChar:
        def __init__(self):
            self.c_hp = 5000
            self.c_hp_full = 10000
            self.c_mp = 2000
            self.c_mp_full = 5000
            self.cx = 500
            self.cy = 300
            self.is_die = False
            self.have_pet = True
    
    class MockMob:
        def __init__(self, x, y, hp, max_hp):
            self.x = x
            self.y = y
            self.hp = hp
            self.max_hp = max_hp
            self.status = 5  # Alive
            self.is_mob_me = False
    
    class MockAccount:
        def __init__(self):
            self.char = MockChar()
    
    class MockController:
        def __init__(self):
            self.account = MockAccount()
            self.mobs = {
                1: MockMob(550, 320, 1000, 2000),
                2: MockMob(700, 400, 500, 1000),
                3: MockMob(1000, 500, 0, 1000),  # Dead
            }
    
    # Test
    builder = StateBuilder()
    controller = MockController()
    
    state = builder.build_state(controller)
    
    print(f"\nState vector (dim={len(state)}):")
    feature_names = [
        "HP ratio", "MP ratio", "Pos X", "Pos Y",
        "Mob dist X", "Mob dist Y", "Mob HP ratio", "Mob count",
        "Skill 0", "Skill 1", "Is dead", "Has pet",
        "Target dist X", "Target dist Y", "Reserved..."
    ]
    
    for i, (name, value) in enumerate(zip(feature_names, state[:14])):
        print(f"  [{i:2d}] {name:15s}: {value:.4f}")
    
    print(f"\n[SUCCESS] StateBuilder test complete!")
