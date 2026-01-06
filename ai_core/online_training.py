"""
Online Training Integration - AI learns while playing the game
Tích hợp trainer vào AI Agent để học trong khi chơi
"""

import asyncio
from typing import Optional
from train.train_pytorch import AITrainer


class OnlineTrainer:
    """
    Online training manager - Trains AI while bot is playing
    Collects experience from real gameplay and trains in background
    """
    
    def __init__(self, ai_agent, enable_training=True):
        """
        Args:
            ai_agent: AIAgent instance
            enable_training: Enable background training
        """
        self.ai_agent = ai_agent
        self.trainer = AITrainer(state_dim=20, action_dim=32, lr=0.001)
        self.enable_training = enable_training
        
        # Training state
        self.last_state = None
        self.last_action = None
        self.training_task = None
        self.steps_since_train = 0
        self.train_interval = 100  # Train every 100 steps
        
        print(f"[Online Training] Initialized - Training: {'ON' if enable_training else 'OFF'}")
    
    def calculate_reward(self, old_state_dict, new_state_dict) -> float:
        """
        Calculate reward based on state transition
        
        Reward structure:
        - Kill mob: +1.0
        - Take damage: -0.1
        - Die: -1.0
        - Gain XP: +0.5
        - Pick item: +0.3
        - Idle too long: -0.1
        """
        reward = 0.0
        
        try:
            old_char = old_state_dict['char']
            new_char = new_state_dict['char']
            
            # Death penalty
            if not old_char.is_die and new_char.is_die:
                reward -= 1.0
                return reward
            
            # HP change
            hp_diff = new_char.c_hp - old_char.c_hp
            if hp_diff < 0:
                reward -= 0.1  # Took damage
            
            # XP gain (tiềm năng)
            xp_gain = new_char.c_tiem_nang - old_char.c_tiem_nang
            if xp_gain > 0:
                reward += 0.5
            
            # Gold gain
            gold_gain = new_char.xu - old_char.xu
            if gold_gain > 0:
                reward += 0.3
            
            # Mob kills (check if mobs HP decreased)
            old_mobs = old_state_dict.get('mobs', {})
            new_mobs = new_state_dict.get('mobs', {})
            
            for mob_id, old_mob in old_mobs.items():
                if mob_id in new_mobs:
                    new_mob = new_mobs[mob_id]
                    # Mob died
                    if old_mob.hp > 0 and new_mob.hp == 0:
                        reward += 1.0
                    # Damaged mob
                    elif new_mob.hp < old_mob.hp:
                        reward += 0.2
            
            # Movement penalty if idle
            if old_char.cx == new_char.cx and old_char.cy == new_char.cy:
                reward -= 0.05
            
        except Exception as e:
            print(f"[Online Training] Error calculating reward: {e}")
            reward = 0.0
        
        return reward
    
    async def collect_step(self, state, action, controller):
        """
        Collect single experience step from gameplay
        Called after each AI decision
        """
        if not self.enable_training:
            return
        
        try:
            # First step - just store state
            if self.last_state is None:
                self.last_state = state
                self.last_action = action
                self.last_state_dict = {
                    'char': controller.account.char,
                    'mobs': controller.mobs.copy()
                }
                return
            
            # Calculate reward
            current_state_dict = {
                'char': controller.account.char,
                'mobs': controller.mobs.copy()
            }
            
            reward = self.calculate_reward(self.last_state_dict, current_state_dict)
            
            # Check if episode done (died)
            done = controller.account.char.is_die
            
            # Add to replay buffer
            self.trainer.collect_experience(
                self.last_state,
                self.last_action,
                reward,
                state,
                done
            )
            
            # Update for next step
            self.last_state = state
            self.last_action = action
            self.last_state_dict = current_state_dict
            
            self.steps_since_train += 1
            
            # Periodic training
            if self.steps_since_train >= self.train_interval:
                await self._background_train()
                self.steps_since_train = 0
        
            # Periodic training
            if self.steps_since_train >= self.train_interval:
                await self._background_train()
                self.steps_since_train = 0
        
        except Exception as e:
            print(f"[Online Training] Error collecting step: {e}")

    async def collect_step_shared(self, state, action, controller, shared_trainer):
        """Collect step and push to SharedTrainer"""
        try:
            # Similar logic to collect_step but pushes to shared_trainer
            if self.last_state is None:
                self.last_state = state
                self.last_action = action
                self.last_state_dict = {
                    'char': controller.account.char,
                    'mobs': controller.mobs.copy()
                }
                # Register agent if needed
                shared_trainer.register_agent(self.ai_agent)
                return
            
            # Calculate reward
            current_state_dict = {
                'char': controller.account.char,
                'mobs': controller.mobs.copy()
            }
            
            reward = self.calculate_reward(self.last_state_dict, current_state_dict)
            done = controller.account.char.is_die
            
            # Push to SHARED trainer
            await shared_trainer.collect_step(
                self.last_state,
                self.last_action,
                reward,
                state,
                done
            )
            
            # Update state
            self.last_state = state
            self.last_action = action
            self.last_state_dict = current_state_dict
            
        except Exception as e:
            print(f"[Shared] Error collecting step: {e}")
    
    async def _background_train(self):
        """Train in background without blocking gameplay"""
        if len(self.trainer.replay_buffer) < 32:
            return
        
        # Train asynchronously
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self._train_batch
        )
    
    def _train_batch(self):
        """Single training batch (runs in thread pool)"""
        try:
            loss = self.trainer.train_step(batch_size=32)
            if loss is not None:
                print(f"[Online Training] Trained - Loss: {loss:.4f} | Buffer: {len(self.trainer.replay_buffer)}")
        except Exception as e:
            print(f"[Online Training] Training error: {e}")
    
    def save_checkpoint(self, path: str):
        """Save current model weights"""
        self.trainer.export_weights(path)
        print(f"[Online Training] Checkpoint saved: {path}")
    
    def auto_save_loop(self, interval_minutes=10):
        """Auto-save model periodically"""
        async def _auto_save():
            while self.enable_training:
                await asyncio.sleep(interval_minutes * 60)
                timestamp = asyncio.get_event_loop().time()
                self.save_checkpoint(f"ai_core/weights/autosave_{int(timestamp)}.json")
        
        return asyncio.create_task(_auto_save())
    
    def get_stats(self):
        """Get training statistics"""
        return {
            "training_enabled": self.enable_training,
            "buffer_size": len(self.trainer.replay_buffer),
            "total_steps": self.trainer.total_steps,
            "total_episodes": self.trainer.total_episodes,
            "avg_loss": self.trainer.get_stats()['avg_loss_last_100']
        }


# Example usage in AI Agent
"""
# In ai_agent.py - integrate online training

class AIAgent:
    def __init__(self, controller, service, account_id):
        # ... existing code ...
        
        # Add online trainer (optional)
        self.online_trainer = OnlineTrainer(self, enable_training=False)
    
    async def _decision_loop(self):
        while self.enabled:
            # ... existing code ...
            
            # Step 1: Build state
            state = self.state_builder.build_state(self.controller)
            
            # Step 2: Predict action
            action_idx, confidence = await self.brain.predict(state, action_mask)
            
            # Step 3: Execute action
            success = await self.action_decoder.execute_action(action_idx, context)
            
            # NEW: Step 4: Collect experience for training
            if self.online_trainer.enable_training:
                await self.online_trainer.collect_step(state, action_idx, self.controller)
            
            await asyncio.sleep(self.decision_interval)
"""
