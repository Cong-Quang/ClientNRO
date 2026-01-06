"""
Action Decoder - Execute AI Decisions as Game Actions
Translates neural network output (0-31) into actual game commands
Supports: Basic actions, Multi-agent coordination, Boss hunting, Goal-based farming
"""

from typing import Optional, Dict, Any
import asyncio


class ActionDecoder:
    """
    Decodes AI action index into game commands.
    Action space: 32 actions organized by category.
    """
    
    # Action categories
    BASIC_ACTIONS = range(0, 8)
    MULTIAGENT_ACTIONS = range(8, 16)
    BOSS_HUNTING_ACTIONS = range(16, 24)
    GOAL_BASED_ACTIONS = range(24, 32)
    
    def __init__(self, controller, service, shared_memory):
        """
        Args:
            controller: Game controller instance
            service: Network service for sending commands
            shared_memory: SharedMemory instance for coordination
        """
        self.controller = controller
        self.service = service
        self.shared_memory = shared_memory
        self.char = controller.account.char
        
        print(f"[ActionDecoder] Initialized for account: {controller.account.username}")
    
    async def execute_action(self, action_index: int, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Execute the selected action.
        
        Args:
            action_index: Action to execute (0-31)
            context: Optional context data (item_ids, mob_id, etc.)
        
        Returns:
            bool: True if action executed successfully
        """
        if context is None:
            context = {}
        
        try:
            # Route to appropriate action category
            if action_index in self.BASIC_ACTIONS:
                return await self._execute_basic_action(action_index)
            elif action_index in self.MULTIAGENT_ACTIONS:
                return await self._execute_multiagent_action(action_index, context)
            elif action_index in self.BOSS_HUNTING_ACTIONS:
                return await self._execute_boss_hunting_action(action_index, context)
            elif action_index in self.GOAL_BASED_ACTIONS:
                return await self._execute_goal_based_action(action_index, context)
            else:
                print(f"[ActionDecoder] Invalid action index: {action_index}")
                return False
                
        except Exception as e:
            print(f"[ActionDecoder] Error executing action {action_index}: {e}")
            return False
    
    # ===== Basic Actions (0-7) =====
    
    async def _execute_basic_action(self, action_index: int) -> bool:
        """Execute basic game actions"""
        
        if action_index == 0:
            # Action 0: Idle
            return True
        
        elif action_index == 1:
            # Action 1: Attack nearest mob
            return await self._attack_nearest_mob()
        
        elif action_index == 2:
            # Action 2: Move to mob
            return await self._move_to_nearest_mob()
        
        elif action_index == 3:
            # Action 3: Use best skill
            return await self._use_best_skill()
        
        elif action_index == 4:
            # Action 4: Retreat (run away)
            return await self._retreat()
        
        elif action_index == 5:
            # Action 5: Pick up items
            return await self._pick_up_items()
        
        elif action_index == 6:
            # Action 6: Use HP potion
            return await self._use_hp_potion()
        
        elif action_index == 7:
            # Action 7: Return to safe zone
            return await self._return_to_safe_zone()
        
        return False
    
    # ===== Multi-Agent Actions (8-15) =====
    
    async def _execute_multiagent_action(self, action_index: int, context: Dict) -> bool:
        """Execute multi-agent coordination actions"""
        
        if action_index == 8:
            # Action 8: Broadcast target to team
            return await self._broadcast_target()
        
        elif action_index == 9:
            # Action 9: Follow team leader
            return await self._follow_leader()
        
        elif action_index == 10:
            # Action 10: Call for help
            return await self._call_for_help()
        
        elif action_index == 11:
            # Action 11: Form formation
            return await self._form_formation()
        
        # Actions 12-15: Reserved
        return True
    
    # ===== Boss Hunting Actions (16-23) =====
    
    async def _execute_boss_hunting_action(self, action_index: int, context: Dict) -> bool:
        """Execute boss hunting actions"""
        
        if action_index == 16:
            # Action 16: Search for boss
            return await self._search_for_boss(context)
        
        elif action_index == 17:
            # Action 17: Coordinate boss attack
            return await self._coordinate_boss_attack()
        
        elif action_index == 18:
            # Action 18: Tank boss (take damage for team)
            return await self._tank_boss()
        
        elif action_index == 19:
            # Action 19: Support teammates
            return await self._support_teammates()
        
        # Actions 20-23: Reserved
        return True
    
    # ===== Goal-Based Actions (24-31) =====
    
    async def _execute_goal_based_action(self, action_index: int, context: Dict) -> bool:
        """Execute goal-based actions with context"""
        
        if action_index == 24:
            # Action 24: Farm specific item (kill mobs for loot)
            return await self._farm_items(context)
        
        elif action_index == 25:
            # Action 25: Hunt specific mob
            return await self._hunt_specific_mob(context)
        
        elif action_index == 26:
            # Action 26: Gather resources
            return await self._gather_resources()
        
        elif action_index == 27:
            # Action 27: Complete quest objective
            return await self._complete_quest_objective(context)
        
        # Actions 28-31: Reserved
        return True
    
    # ===== Helper Methods =====
    
    async def _attack_nearest_mob(self) -> bool:
        """Attack the nearest alive mob"""
        try:
            nearest_mob = self._find_nearest_alive_mob()
            if nearest_mob:
                # Service.send_player_attack expects a list of mob_ids
                await self.service.send_player_attack(mob_ids=[nearest_mob.mob_id])
                return True
        except Exception as e:
            print(f"[ActionDecoder] Attack failed: {e}")
        return False
    
    async def _move_to_nearest_mob(self) -> bool:
        """Move towards nearest mob"""
        try:
            nearest_mob = self._find_nearest_alive_mob()
            if nearest_mob:
                # Update char position (Service sends char.cx/cy)
                self.char.cx = nearest_mob.x
                self.char.cy = nearest_mob.y
                await self.service.char_move()
                return True
        except:
            pass
        return False
    
    async def _use_best_skill(self) -> bool:
        """Use highest damage skill"""
        try:
            # Select best skill (simplified - use first available skill)
            if hasattr(self.char, 'skills') and self.char.skills:
                await self.service.select_skill(0)  # Use skill index 0
                return True
        except:
            pass
        return False
    
    async def _retreat(self) -> bool:
        """Run away from danger"""
        try:
            # Move in opposite direction of nearest mob
            nearest_mob = self._find_nearest_alive_mob()
            if nearest_mob:
                dx = self.char.cx - nearest_mob.x
                dy = self.char.cy - nearest_mob.y
                
                # Move further away
                retreat_x = self.char.cx + dx
                retreat_y = self.char.cy + dy
                
                # Update char position and send
                self.char.cx = retreat_x
                self.char.cy = retreat_y
                await self.service.char_move()
                return True
        except:
            pass
        return False
    
    async def _pick_up_items(self) -> bool:
        """Pick up nearby items"""
        # Implementation depends on item system
        return True
    
    async def _use_hp_potion(self) -> bool:
        """Use HP potion/item"""
        # Implementation depends on inventory system
        return True
    
    async def _return_to_safe_zone(self) -> bool:
        """Return to safe zone/spawn point"""
        # Implementation depends on map/waypoint system
        return True
    
    async def _broadcast_target(self) -> bool:
        """Share current target with team"""
        try:
            target_mob = self._find_nearest_alive_mob()
            if target_mob:
                self.shared_memory.broadcast_target(
                    self.controller.account.username,
                    {
                        "type": "mob",
                        "mob_id": target_mob.mob_id,
                        "x": target_mob.x,
                        "y": target_mob.y,
                        "hp": target_mob.hp
                    }
                )
                return True
        except:
            pass
        return False
    
    async def _follow_leader(self) -> bool:
        """Follow team leader"""
        leader_id = self.shared_memory.get_team_leader()
        if leader_id:
            # Implementation: get leader position and move there
            return True
        return False
    
    async def _call_for_help(self) -> bool:
        """Broadcast help request to team"""
        self.shared_memory.update_status(
            self.controller.account.username,
            {"status": "need_help", "hp": self.char.c_hp}
        )
        return True
    
    async def _form_formation(self) -> bool:
        """Organize team formation"""
        # Implementation: position bots in formation
        return True
    
    async def _search_for_boss(self, context: Dict) -> bool:
        """Search for boss on map"""
        boss_name = context.get('boss_name', '')
        # Implementation: scan map for boss
        return True
    
    async def _coordinate_boss_attack(self) -> bool:
        """Attack boss in coordination with team"""
        targets = self.shared_memory.get_shared_targets()
        for target in targets:
            if target.get('type') == 'boss':
                # Attack the boss
                return await self._attack_nearest_mob()
        return False
    
    async def _tank_boss(self) -> bool:
        """Tank boss (stay close, take damage)"""
        # Implementation: position in front, use defensive skills
        return True
    
    async def _support_teammates(self) -> bool:
        """Support team (healing, buffs)"""
        # Implementation: use support skills on teammates
        return True
    
    async def _farm_items(self, context: Dict) -> bool:
        """Farm items by killing specific mobs"""
        item_ids = context.get('item_ids', [])
        target_mob_id = context.get('target_mob_id')
        
        # Kill mob to get item drops
        if target_mob_id:
            # Find and attack mob with target_mob_id
            return await self._attack_nearest_mob()
        
        return False
    
    async def _hunt_specific_mob(self, context: Dict) -> bool:
        """Hunt specific mob type"""
        mob_id = context.get('mob_id')
        # Implementation: find and attack specific mob type
        return await self._attack_nearest_mob()
    
    async def _gather_resources(self) -> bool:
        """Gather resources from map"""
        return True
    
    async def _complete_quest_objective(self, context: Dict) -> bool:
        """Work on quest objective"""
        quest_id = context.get('quest_id')
        # Implementation: perform quest-specific actions
        return True
    
    def _find_nearest_alive_mob(self):
        """Find nearest alive mob (helper)"""
        import math
        
        nearest_mob = None
        min_distance = float('inf')
        
        try:
            for mob_id, mob in self.controller.mobs.items():
                # Aggressive Targeting:
                # Attack if Status > 0.
                # Skip ONLY if Dead (0).
                if mob.status <= 0 or mob.is_mob_me:
                    continue
                
                dx = mob.x - self.char.cx
                dy = mob.y - self.char.cy
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_mob = mob
        except Exception as e:
            print(f"[ActionDecoder] Error finding mob: {e}")
            pass
        
        if nearest_mob is None:
             # print("[ActionDecoder] No alive mob found!") # Uncomment for verbose debug
             pass
        
        return nearest_mob


# Example usage
if __name__ == "__main__":
    print("Testing ActionDecoder...")
    
    # Mock objects
    class MockChar:
        def __init__(self):
            self.cx = 500
            self.cy = 300
            self.c_hp = 5000
            self.skills = []
    
    class MockAccount:
        def __init__(self):
            self.char = MockChar()
            self.username = "test_account"
    
    class MockController:
        def __init__(self):
            self.account = MockAccount()
            self.mobs = {}
    
    class MockService:
        async def send_attack(self, mob_id, skill):
            print(f"  [Mock] Attacking mob {mob_id} with skill {skill}")
        
        async def char_move(self, x, y):
            print(f"  [Mock] Moving to ({x}, {y})")
        
        async def select_skill(self, index):
            print(f"  [Mock] Selected skill {index}")
    
    # Import SharedMemory
    from shared_memory import SharedMemory
    
    # Create instances
    controller = MockController()
    service = MockService()
    memory = SharedMemory()
    
    decoder = ActionDecoder(controller, service, memory)
    
    # Test actions
    async def test():
        print("\nTest 1: Action 0 (Idle)")
        await decoder.execute_action(0)
        
        print("\nTest 2: Action 8 (Broadcast target)")
        await decoder.execute_action(8)
        
        print("\nTest 3: Action 24 (Farm items) with context")
        await decoder.execute_action(24, {"item_ids": [1, 5, 10], "target_mob_id": 12})
    
    asyncio.run(test())
    print("\n[SUCCESS] ActionDecoder test complete!")
