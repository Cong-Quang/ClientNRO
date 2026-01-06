"""
AI Agent - Integration module between AI Core and Game Controller
Handles AI decision-making loop and action execution in real-time gameplay
"""

import asyncio
import random
from ai_core import InferenceEngine, StateBuilder, ActionDecoder, SharedMemory
from logs.logger_config import logger


class AIAgent:
    """
    AI Agent that controls a single game account using neural network decisions.
    Integrates with Controller to observe game state and execute actions.
    """
    
    def __init__(self, controller, service, account_id: str):
        """
        Initialize AI Agent for a controller.
        
        Args:
            controller: Game controller instance
            service: Network service for sending commands
            account_id: Unique identifier for this account
        """
        self.controller = controller
        self.service = service
        self.account_id = account_id
        
        # AI Components
        self.brain = InferenceEngine()
        self.state_builder = StateBuilder()
        self.action_decoder = ActionDecoder(controller, service, SharedMemory())
        self.shared_memory = SharedMemory()
        
        # Online Training (optional - disabled by default)
        self.online_trainer = None
        self.training_enabled = False
        self.epsilon = 0.5  # Exploration rate (0.0 = pure exploit, 1.0 = pure random)
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.9998  # Decay per step
        
        # State
        self.enabled = False
        self.task = None
        self.decision_interval = 0.01  # Seconds between decisions (Previously 0.5)
        
        logger.info(f"[AI Agent] Initialized for {account_id}")
    
    def load_weights(self, weights_path: str) -> bool:
        """Load AI model weights"""
        try:
            self.brain.load_weights(weights_path)
            logger.info(f"[AI Agent] Loaded weights from {weights_path}")
            return True
        except Exception as e:
            logger.error(f"[AI Agent] Error loading weights: {e}")
            return False

    def start(self):
        """Start AI decision-making loop"""
        if self.enabled:
            logger.warning(f"[AI Agent] Already running for {self.account_id}")
            return None
        
        self.enabled = True
        self.task = asyncio.create_task(self._decision_loop())
        logger.info(f"[AI Agent] Started for {self.account_id}")
        return self.task
    
    def stop(self):
        """Stop AI decision-making loop"""
        self.enabled = False
        if self.task:
            self.task.cancel()
            self.task = None
        logger.info(f"[AI Agent] Stopped for {self.account_id}")

    # ... (skipping unchanged methods) ...

    async def _decision_loop(self):
        """Main AI decision-making loop"""
        logger.info(f"[AI Agent] Decision loop started for {self.account_id}")
        
        try:
            while self.enabled:
                try:
                    # Check if in active group
                    if not self.shared_memory.is_bot_in_active_group(self.account_id):
                        await asyncio.sleep(self.decision_interval)
                        continue
                    
                    # Step 1: Build state from game
                    state = self.state_builder.build_state(self.controller)
                    
                    # Step 2: Get action mask (based on current game situation)
                    action_mask = self._build_action_mask()
                    
                    # Step 3: Decision Making (Epsilon-Greedy)
                    is_training = self.training_enabled or self.shared_memory.shared_trainer_enabled
                    
                    if is_training and random.random() < self.epsilon:
                        # Explore: Choose random valid action
                        valid_actions = [i for i, valid in enumerate(action_mask) if valid]
                    if is_training and random.random() < self.epsilon:
                        # Explore: Choose random valid action
                        valid_actions = [i for i, valid in enumerate(action_mask) if valid]
                        if valid_actions:
                            action_idx = random.choice(valid_actions)
                            confidence = 0.0
                            if logger.isEnabledFor(10):
                                logger.debug(f"[AI Agent] {self.account_id}: Exploring (eps={self.epsilon:.3f}) -> Action {action_idx}")
                        else:
                            action_idx = 0 # Fallback to Idle
                            confidence = 0.0
                        
                        # Decay epsilon
                        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
                        
                    else:
                        # Exploit: Neural network inference
                        action_idx, confidence = await self.brain.predict(state, action_mask)
                    
                    # Step 4: Execute action
                    context = self._build_context()
                    success = await self.action_decoder.execute_action(action_idx, context)
                    
                    # Step 5: Collect experience for online training (if enabled)
                    # Priority: Shared Trainer > Local Online Trainer
                    if SharedMemory().shared_trainer_enabled:
                         # Assume we import it or access via singleton
                         from ai_core.shared_training import SharedTrainer
                         shared = SharedTrainer()
                         # We need to calculate reward first (reuse Local Trainer logic or duplicate)
                         # To keep it reliable, let's use the local online_trainer to calc reward/state
                         # but push to shared if enabled.
                         if not self.online_trainer:
                             from ai_core.online_training import OnlineTrainer
                             self.online_trainer = OnlineTrainer(self, enable_training=False)
                         
                         # Collect step but push to shared
                         await self.online_trainer.collect_step_shared(state, action_idx, self.controller, shared)
                    
                    elif self.training_enabled and self.online_trainer:
                        await self.online_trainer.collect_step(state, action_idx, self.controller)
                    
                    # Log decision
                    if logger.isEnabledFor(10):  # DEBUG level
                        logger.debug(f"[AI Agent] {self.account_id}: Action {action_idx} (conf:{confidence:.2f}) -> {'OK' if success else 'FAIL'}")
                    
                    # Wait before next decision
                    await asyncio.sleep(self.decision_interval)
                
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.error(f"[AI Agent] Error in decision loop: {e}")
                    await asyncio.sleep(self.decision_interval)
        
        except asyncio.CancelledError:
            logger.info(f"[AI Agent] Decision loop cancelled for {self.account_id}")
        
        finally:
            self.enabled = False
            logger.info(f"[AI Agent] Decision loop ended for {self.account_id}")
    
    def _build_action_mask(self) -> list[bool]:
        """
        Build action mask based on current game state.
        Returns list of 32 bools indicating which actions are valid.
        """
        mask = [True] * 32  # All actions available by default
        
        char = self.controller.account.char
        
        # Disable actions if dead
        if char.is_die:
            # Only allow retreat/safe zone actions
            mask = [False] * 32
            mask[4] = True  # Retreat
            mask[7] = True  # Return to safe zone
            return mask
        
        # Disable HP potion if HP is full
        if char.c_hp >= char.c_hp_full * 0.9:
            mask[6] = False
        
        # Disable attack actions if no mobs nearby
        has_mobs = any(
            mob.status > 0 and not mob.is_mob_me
            for mob in self.controller.mobs.values()
        )
        if not has_mobs:
            mask[1] = False  # Attack nearest
            mask[2] = False  # Move to mob
            mask[3] = False  # Use skill
        
        # Disable multi-agent actions if no team
        team_leader = self.shared_memory.get_team_leader()
        if not team_leader:
            for i in range(8, 16):
                mask[i] = False
        
        # Disable goal-based actions if no goal
        goal = self.shared_memory.get_current_goal()
        if not goal:
            for i in range(24, 32):
                mask[i] = False
        
        return mask
    
    def _build_context(self) -> dict:
        """Build context dict for action execution"""
        context = {}
        
        # Add current goal if exists
        goal = self.shared_memory.get_current_goal()
        if goal:
            context.update(goal.get('data', {}))
        
        # Add team info
        context['team_leader'] = self.shared_memory.get_team_leader()
        context['account_id'] = self.account_id
        
        return context
    
    def enable_training(self, enabled: bool = True):
        """Enable/disable online training"""
        if enabled and not self.online_trainer:
            from ai_core.online_training import OnlineTrainer
            self.online_trainer = OnlineTrainer(self, enable_training=True)
        
        self.training_enabled = enabled
        logger.info(f"[AI Agent] Training {'enabled' if enabled else 'disabled'} for {self.account_id}")
    
    def save_model(self, path: str = None):
        """Save current model weights"""
        if path is None:
            import time
            path = f"ai_core/weights/{self.account_id}_{int(time.time())}.json"
        
        if self.online_trainer:
            self.online_trainer.save_checkpoint(path)
        else:
            self.brain.save_weights(path)
        
        logger.info(f"[AI Agent] Model saved: {path}")
        return path
    
    def get_status(self) -> dict:
        """Get AI agent status"""
        status = {
            "enabled": self.enabled,
            "account_id": self.account_id,
            "brain_loaded": self.brain.loaded,
            "decision_interval": self.decision_interval,
            "in_active_group": self.shared_memory.is_bot_in_active_group(self.account_id),
            "current_goal": self.shared_memory.get_current_goal(),
            "training_enabled": self.training_enabled
        }
        
        # Add training stats if available
        if self.training_enabled and self.online_trainer:
            status["training_stats"] = self.online_trainer.get_stats()
        
        return status

    def get_debug_status(self) -> dict:
        """Get detailed debug status for SharedMemory issues"""
        sm = self.shared_memory
        return {
            "account_id": self.account_id,
            "sm_id": id(sm),
            "sm_groups": sm.groups,
            "sm_active_groups": sm.active_groups,
            "is_in_active": sm.is_bot_in_active_group(self.account_id),
            "is_in_group_1": self.account_id in sm.groups.get(1, [])
        }
