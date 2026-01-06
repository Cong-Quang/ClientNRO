"""
AI Command Handler - Terminal commands for AI system
Handles: ai status, ai on/off, ai load/save, ai goal, ai group, ai zone, etc.
"""

from typing import Optional
from ai_core import InferenceEngine, StateBuilder, ActionDecoder, SharedMemory
from logs.logger_config import TerminalColors


class AICommandHandler:
    """Handles all AI-related terminal commands"""
    
    def __init__(self):
        self.C = TerminalColors
        self.brain = InferenceEngine()
        self.state_builder = StateBuilder()
        self.shared_memory = SharedMemory()
        self.ai_enabled = False  # Global AI on/off state
        
        # Per-account AI state
        self.account_ai_states = {}  # account_id -> {"enabled": bool, "decoder": ActionDecoder}
        
        print(f"[AI System] Initialized - Default mode: {self.C.RED}OFF{self.C.RESET}")
    
    def load_weights(self, weights_path: str) -> bool:
        """Load AI weights from file"""
        try:
            self.brain.load_weights(weights_path)
            return True
        except Exception as e:
            print(f"{self.C.RED}[AI] Error loading weights: {e}{self.C.RESET}")
            return False
   
    def register_account(self, account_id: str, controller, service):
        """Register an account for AI control"""
        if account_id not in self.account_ai_states:
            decoder = ActionDecoder(controller, service, self.shared_memory)
            self.account_ai_states[account_id] = {
                "enabled": False,
                "decoder": decoder,
                "controller": controller
            }
    
    async def handle_ai_command(self, parts: list[str], manager) -> bool:
        """
        Handle AI commands.
        Returns True if command was handled, False otherwise.
        """
        if not parts or parts[0] != "ai":
            return False
        
        if len(parts) == 1:
            self._show_ai_help()
            return True
        
        sub_cmd = parts[1]
        
        # AI Status & Info
        if sub_cmd == "status":
            self._show_status()
        elif sub_cmd == "info":
            self._show_info()
        
        # AI Control
        elif sub_cmd == "on":
            await self._ai_on(parts, manager)
        elif sub_cmd == "off":
            await self._ai_off(parts, manager)
        elif sub_cmd == "toggle":
            await self._ai_toggle(parts, manager)
        
        # Model Management
        elif sub_cmd == "load":
            self._load_weights(parts)
        elif sub_cmd == "reset":
            self._reset_weights()
        
        # Goal Management
        elif sub_cmd == "goal":
            self._handle_goal_commands(parts)
        
        # Group Management (AI-specific)
        elif sub_cmd == "group":
            self._handle_ai_group_commands(parts, manager)
        
        # Zone Distribution
        elif sub_cmd == "zone":
            self._handle_zone_commands(parts)
        
        # Team commands
        elif sub_cmd == "team":
            self._handle_team_commands(parts)
        
        elif sub_cmd == "trainer":
            self._handle_trainer_commands(parts)
        
        else:
            print(f"{self.C.RED}Unknown AI command: {sub_cmd}{self.C.RESET}")
            self._show_ai_help()
        
        return True

    def _handle_trainer_commands(self, parts: list[str]):
        """Handle shared trainer commands"""
        if len(parts) < 3:
            print(f"{self.C.RED}Usage: ai trainer shared <on|off>{self.C.RESET}")
            return
            
        if parts[2] == "shared":
            if len(parts) < 4:
                # Show status
                from ai_core.shared_training import SharedTrainer
                st = SharedTrainer()
                stats = st.get_stats()
                print(f"{self.C.CYAN}Shared Trainer Status:{self.C.RESET}")
                for k,v in stats.items():
                    print(f"  {k}: {v}")
                return

            mode = parts[3]
            from ai_core.shared_training import SharedTrainer
            st = SharedTrainer()
            
            if mode == "on":
                st.enable()
                self.shared_memory.shared_trainer_enabled = True
            elif mode == "off":
                st.disable()
                self.shared_memory.shared_trainer_enabled = False
            else:
                print("Invalid mode. Use on/off")
    
    def _show_ai_help(self):
        """Show AI command help"""
        C = self.C
        print(f"\n{C.CYAN}=== AI System Commands ==={C.RESET}")
        print(f"{C.YELLOW}Status & Info:{C.RESET}")
        print(f"  ai status              - Show AI system status")
        print(f"  ai info                - Show model architecture info")
        print(f"\n{C.YELLOW}Control:{C.RESET}")
        print(f"  ai on [account_id]     - Enable AI for account (default: current target)")
        print(f"  ai off [account_id]    - Disable AI for account")
        print(f"  ai toggle [account_id] - Toggle AI status")
        print(f"\n{C.YELLOW}Model:{C.RESET}")
        print(f"  ai load <path>         - Load weights from file")
        print(f"  ai reset               - Reset to default weights")
        print(f"\n{C.YELLOW}Goals:{C.RESET}")
        print(f"  ai goal set <type> <params>  - Set global goal")
        print(f"    Examples: ai goal set farm_items 1,5,10 mob=12")
        print(f"              ai goal set hunt_boss Fide")
        print(f"  ai goal show           - Show current goal")
        print(f"  ai goal clear          - Clear goal")
        print(f"\n{C.YELLOW}Groups:{C.RESET}")
        print(f"  ai group set <ids>     - Set active AI groups (e.g., 1,2,3)")
        print(f"  ai group show          - Show group assignments")
        print(f"  ai group assign <id> <gid> - Assign account to group")
        print(f"  ai group auto          - Auto assign all logged-in accounts to Group 1")
        print(f"\n{C.YELLOW}Zones:{C.RESET}")
        print(f"  ai zone auto <map_id>  - Auto distribute bots to zones")
        print(f"  ai zone show <map_id>  - Show zone distribution")
        print()
    
    def _show_status(self):
        """Show AI system status"""
        C = self.C
        status = f"{C.GREEN}ON{C.RESET}" if self.ai_enabled else f"{C.RED}OFF{C.RESET}"
        
        print(f"\n{C.CYAN}=== AI System Status ==={C.RESET}")
        print(f"Global AI: {status}")
        print(f"Brain loaded: {C.GREEN}Yes{C.RESET}" if self.brain.loaded else f"{C.RED}No{C.RESET}")
        print(f"Active accounts: {len([a for a in self.account_ai_states.values() if a['enabled']])}")
        
        # Show current goal
        goal = self.shared_memory.get_current_goal()
        if goal:
            print(f"Current goal: {C.YELLOW}{goal['type']}{C.RESET} - {goal['data']}")
        print()
    
    def _show_info(self):
        """Show AI model info"""
        C = self.C
        info = self.brain.get_model_info()
        
        print(f"\n{C.CYAN}=== AI Model Info ==={C.RESET}")
        print(f"Architecture: {info['architecture']}")
        print(f"Total parameters: {info['total_parameters']:,}")
        print(f"Engine: {info['inference_engine']}")
        print(f"Loaded: {info['loaded']}")
        print()
    
    async def _ai_on(self, parts: list[str], manager):
        """Enable AI for account(s)"""
        # TODO: Implement based on target system
        print(f"{self.C.GREEN}[AI] AI mode ON{self.C.RESET}")
        self.ai_enabled = True
    
    async def _ai_off(self, parts: list[str], manager):
        """Disable AI for account(s)"""
        print(f"{self.C.RED}[AI] AI mode OFF{self.C.RESET}")
        self.ai_enabled = False
    
    async def _ai_toggle(self, parts: list[str], manager):
        """Toggle AI status"""
        self.ai_enabled = not self.ai_enabled
        status = f"{self.C.GREEN}ON{self.C.RESET}" if self.ai_enabled else f"{self.C.RED}OFF{self.C.RESET}"
        print(f"[AI] Toggled to {status}")
    
    def _load_weights(self, parts: list[str]):
        """Load weights from file"""
        if len(parts) < 3:
            print(f"{self.C.RED}Usage: ai load <weights_path>{self.C.RESET}")
            return
        
        weights_path = parts[2]
        if self.load_weights(weights_path):
            print(f"{self.C.GREEN}[AI] Weights loaded successfully{self.C.RESET}")
        else:
            print(f"{self.C.RED}[AI] Failed to load weights{self.C.RESET}")
    
    def _reset_weights(self):
        """Reset to default weights"""
        if self.load_weights("ai_core/weights/default_weights.json"):
            print(f"{self.C.GREEN}[AI] Reset to default weights{self.C.RESET}")
    
    def _handle_goal_commands(self, parts: list[str]):
        """Handle goal management commands"""
        if len(parts) < 3:
            print(f"{self.C.RED}Usage: ai goal set/show/clear{self.C.RESET}")
            return
        
        goal_cmd = parts[2]
        C = self.C
        
        if goal_cmd == "show":
            goal = self.shared_memory.get_current_goal()
            if goal:
                print(f"{C.CYAN}Current Goal:{C.RESET}")
                print(f"  Type: {C.YELLOW}{goal['type']}{C.RESET}")
                print(f"  Data: {goal['data']}")
            else:
                print(f"{C.DIM}No goal set{C.RESET}")
        
        elif goal_cmd == "clear":
            self.shared_memory.clear_goal()
            print(f"{C.GREEN}[AI] Goal cleared{C.RESET}")
        
        elif goal_cmd == "set":
            if len(parts) < 5:
                print(f"{C.RED}Usage: ai goal set <type> <params>{C.RESET}")
                return
            
            goal_type = parts[3]
            params_str = " ".join(parts[4:])
            
            # Parse parameters
            goal_data = self._parse_goal_params(goal_type, params_str)
            
            self.shared_memory.set_global_goal(goal_type, goal_data)
            print(f"{C.GREEN}[AI] Goal set: {goal_type}{C.RESET}")
    
    def _parse_goal_params(self, goal_type: str, params_str: str) -> dict:
        """Parse goal parameters from string"""
        data = {}
        
        if goal_type == "farm_items":
            # Format: "1,5,10 mob=12"
            parts = params_str.split()
            if parts:
                data["item_ids"] = [int(x) for x in parts[0].split(',')]
            for part in parts[1:]:
                if '=' in part:
                    key, val = part.split('=')
                    data[key] = int(val) if val.isdigit() else val
        
        elif goal_type == "hunt_boss":
            data["boss_name"] = params_str
        
        else:
            data["raw_params"] = params_str
        
        return data
    
    def _handle_ai_group_commands(self, parts: list[str], manager=None):
        """Handle AI group commands"""
        if len(parts) < 3:
            print(f"{self.C.RED}Usage: ai group set/show/assign/auto{self.C.RESET}")
            return
        
        group_cmd = parts[2]
        C = self.C
        
        if group_cmd == "show":
            groups = self.shared_memory.groups
            active = self.shared_memory.active_groups
            
            print(f"{C.CYAN}AI Group Status:{C.RESET}")
            print(f"  Active groups: {C.YELLOW}{active}{C.RESET}")
            for gid, members in groups.items():
                marker = f"{C.GREEN}[ACTIVE]{C.RESET}" if gid in active else ""
                print(f"  Group {gid}: {members} {marker}")
        
        elif group_cmd == "set":
            if len(parts) < 4:
                print(f"{C.RED}Usage: ai group set <group_ids>{C.RESET}")
                return
            
            group_ids = [int(x) for x in parts[3].split(',')]
            self.shared_memory.set_active_groups(group_ids)
            print(f"{C.GREEN}[AI] Active groups set to: {group_ids}{C.RESET}")

        elif group_cmd == "assign":
            if len(parts) < 5:
                print(f"{C.RED}Usage: ai group assign <account_id> <group_id>{C.RESET}")
                return
            
            account_id = parts[3]
            try:
                group_id = int(parts[4])
                self.shared_memory.assign_to_group(account_id, group_id)
                print(f"{C.GREEN}[AI] Assigned {account_id} to group {group_id}{C.RESET}")
            except ValueError:
                print(f"{C.RED}Group ID must be a number{C.RESET}")

        elif group_cmd == "auto":
            # Auto assign all logged-in accounts to Group 1
            if not manager:
                print(f"{C.RED}[AI] Error: Manager not available for auto-assign{C.RESET}")
                return
                
            count = 0
            # Iterate through all accounts in manager
            for account in manager.accounts:
                if account.is_logged_in:
                    self.shared_memory.assign_to_group(account.username, 1)
                    count += 1
            
            print(f"{C.GREEN}[AI] Auto-assigned {count} logged-in accounts to Group 1{C.RESET}")
            
            # Also auto-set active group
            self.shared_memory.set_active_groups([1])
    
    def _handle_zone_commands(self, parts: list[str]):
        """Handle zone distribution commands"""
        if len(parts) < 3:
            print(f"{self.C.RED}Usage: ai zone auto/show <map_id>{self.C.RESET}")
            return
        
        zone_cmd = parts[2]
        C = self.C
        
        if zone_cmd == "show":
            if len(parts) < 4:
                print(f"{C.RED}Usage: ai zone show <map_id>{C.RESET}")
                return
            
            map_id = int(parts[3])
            distribution = self.shared_memory.get_zone_distribution(map_id)
            
            print(f"{C.CYAN}Zone Distribution (Map {map_id}):{C.RESET}")
            if distribution:
                for zone_id, bots in distribution.items():
                    print(f"  Zone {zone_id}: {bots}")
            else:
                print(f"{C.DIM}  No distribution set{C.RESET}")
        
        elif zone_cmd == "auto":
            if len(parts) < 4:
                print(f"{C.RED}Usage: ai zone auto <map_id>{C.RESET}")
                return
            
            map_id = int(parts[3])
            # TODO: Get bot IDs from manager
            bot_ids = ["bot_1", "bot_2", "bot_3"]  # Placeholder
            
            self.shared_memory.auto_distribute_zones(map_id, bot_ids, num_zones=3)
            print(f"{C.GREEN}[AI] Auto-distributed bots to zones{C.RESET}")
    
    def _handle_team_commands(self, parts: list[str]):
        """Handle team coordination commands"""
        if len(parts) < 3:
            print(f"{self.C.RED}Usage: ai team leader/formation{self.C.RESET}")
            return
        
        team_cmd = parts[2]
        C = self.C
        
        if team_cmd == "leader":
            if len(parts) < 4:
                leader = self.shared_memory.get_team_leader()
                print(f"Current leader: {leader if leader else C.DIM + 'None' + C.RESET}")
            else:
                leader_id = parts[3]
                self.shared_memory.set_team_leader(leader_id)
                print(f"{C.GREEN}[AI] Team leader set to: {leader_id}{C.RESET}")
        
        elif team_cmd == "formation":
            formation = self.shared_memory.get_team_formation()
            print(f"{C.CYAN}Team Formation:{C.RESET}")
            print(f"  Leader: {formation.get('leader', 'None')}")
            print(f"  Bots: {len(formation.get('bots', {}))}")
