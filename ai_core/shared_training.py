"""
Shared Training Module - Enables multi-account distributed learning
Singleton pattern to aggregate experience from all bots into one central brain.
"""

import threading
import asyncio
import time
from typing import Optional, Dict

class SharedTrainer:
    """
    Singleton Trainer that collects experience from ALL agents.
    Manages a central AITrainer instance (PyTorch) and syncs weights to agents.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SharedTrainer, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Initialize training state
        self.trainer = None  # Lazy init to avoid PyTorch dependency if not used
        self.training_enabled = False
        self.agents = []  # List of registered agents
        self.latest_weights = None
        self.last_sync_time = 0
        self.sync_interval = 60  # Sync weights every 60 seconds
        
        self._initialized = True
        print("[SharedTrainer] Initialized - Centralized Learning Ready")

    def enable(self):
        """Enable shared training"""
        if self.training_enabled:
            return
            
        # Initialize PyTorch trainer only when enabled
        if self.trainer is None:
            try:
                from train.train_pytorch import AITrainer
                self.trainer = AITrainer(state_dim=20, action_dim=32, lr=0.001)
                print("[SharedTrainer] PyTorch Trainer Started")
            except ImportError:
                print("[SharedTrainer] Failed to import PyTorch trainer. Install dependencies!")
                return
        
        self.training_enabled = True
        
        # Start background worker
        loop = asyncio.get_event_loop()
        loop.create_task(self._shared_training_worker())
        print("[SharedTrainer] Shared Training ENABLED")

    def disable(self):
        """Disable shared training"""
        self.training_enabled = False
        print("[SharedTrainer] Shared Training DISABLED")

    def register_agent(self, agent):
        """Register an agent to contribute to shared training"""
        with self._lock:
            if agent not in self.agents:
                self.agents.append(agent)
                print(f"[SharedTrainer] Agent {agent.account_id} joined shared training")

    async def collect_step(self, state, action, reward, next_state, done):
        """Collect experience from any agent"""
        if not self.training_enabled or not self.trainer:
            return
            
        # Add to centralized replay buffer
        # AITrainer's deque is thread-safe for appends
        self.trainer.collect_experience(state, action, reward, next_state, done)

    async def _shared_training_worker(self):
        """Background worker loop"""
        print("[SharedTrainer] Worker started")
        while self.training_enabled:
            await asyncio.sleep(5)  # Train every 5 seconds check
            
            if not self.trainer:
                continue
                
            buffer_size = len(self.trainer.replay_buffer)
            if buffer_size >= 32:
                # Run training in thread pool to avoid blocking game loop
                loop = asyncio.get_event_loop()
                loss = await loop.run_in_executor(None, self._train_batch)
                
                if loss is not None:
                    # Periodically sync weights
                    current_time = time.time()
                    if current_time - self.last_sync_time > self.sync_interval:
                        await self._sync_weights_to_agents()
                        self.last_sync_time = current_time

    def _train_batch(self):
        """Run training batch (sync function)"""
        try:
            return self.trainer.train_episode(num_steps=10, batch_size=32)
        except Exception as e:
            print(f"[SharedTrainer] Training error: {e}")
            return None

    async def _sync_weights_to_agents(self):
        """Push updated weights to all agents"""
        if not self.agents or not self.trainer:
            return
            
        print("[SharedTrainer] Syncing weights to all agents...")
        try:
            # Export weights from PyTorch model
            weights_data = self.trainer.export_weights_to_dict()
            self.latest_weights = weights_data
            
            # Simply update agent brains (InferenceEngine)
            # This works because they are in the same process
            count = 0
            for agent in self.agents:
                if agent.brain and agent.enabled:
                    agent.brain.set_weights_from_dict(weights_data)
                    count += 1
            
            print(f"[SharedTrainer] Weights synced to {count} agents")
            
        except Exception as e:
            print(f"[SharedTrainer] Sync error: {e}")

    def get_stats(self):
        """Get shared training stats"""
        if not self.trainer:
            return {"enabled": False}
        
        stats = self.trainer.get_stats()
        stats["registered_agents"] = len(self.agents)
        return stats
