"""
PyTorch Training Script for AI Agent
Online training: Trains while bot is playing
Auto GPU/CPU detection, Experience Replay, Export to JSON
"""

import torch
import torch.nn as nn
import torch.optim as optim
import json
import random
from collections import deque
from typing import List, Tuple
import os


class PolicyNetwork(nn.Module):
    """PyTorch MLP for policy learning [20 → 64 → 64 → 32]"""
    
    def __init__(self, state_dim=20, action_dim=32):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_dim)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)  # Logits (no softmax - use with CrossEntropyLoss)
        return x


class ExperienceReplay:
    """Experience replay buffer for training"""
    
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)
    
    def add(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        """Sample random batch from buffer"""
        batch = random.sample(self.buffer, min(batch_size, len(self.buffer)))
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            torch.FloatTensor(states),
            torch.LongTensor(actions),
            torch.FloatTensor(rewards),
            torch.FloatTensor(next_states),
            torch.FloatTensor(dones)
        )
    
    def __len__(self):
        return len(self.buffer)


class AITrainer:
    """AI Training Manager"""
    
    def __init__(self, state_dim=20, action_dim=32, lr=0.001):
        # Auto device detection
        if torch.cuda.is_available():
            self.device = torch.device('cuda')
            print(f"[Training] Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            self.device = torch.device('cpu')
            print(f"[Training] Using CPU")
        
        # Model
        self.model = PolicyNetwork(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.CrossEntropyLoss()
        
        # Experience replay
        self.replay_buffer = ExperienceReplay(capacity=10000)
        
        # Training stats
        self.total_steps = 0
        self.total_episodes = 0
        self.losses = []
        
        print(f"[Training] Model initialized: {sum(p.numel() for p in self.model.parameters())} parameters")
    
    def collect_experience(self, state, action, reward, next_state, done):
        """Add experience to replay buffer"""
        self.replay_buffer.add(state, action, reward, next_state, done)
        self.total_steps += 1
    
    def train_step(self, batch_size=32):
        """Single training step with mini-batch"""
        if len(self.replay_buffer) < batch_size:
            return None
        
        # Sample batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(batch_size)
        
        # Move to device
        states = states.to(self.device)
        actions = actions.to(self.device)
        rewards = rewards.to(self.device)
        next_states = next_states.to(self.device)
        dones = dones.to(self.device)
        
        # Forward pass
        logits = self.model(states)
        
        # Compute loss (supervised learning from action labels)
        loss = self.criterion(logits, actions)
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Track loss
        loss_val = loss.item()
        self.losses.append(loss_val)
        
        return loss_val
    
    def train_episode(self, num_steps=100, batch_size=32):
        """Train for multiple steps"""
        print(f"\n[Training] Episode {self.total_episodes + 1}")
        print(f"Buffer size: {len(self.replay_buffer)}")
        
        episode_losses = []
        for step in range(num_steps):
            loss = self.train_step(batch_size)
            if loss is not None:
                episode_losses.append(loss)
        
        self.total_episodes += 1
        
        if episode_losses:
            avg_loss = sum(episode_losses) / len(episode_losses)
            print(f"Average loss: {avg_loss:.4f}")
            return avg_loss
            avg_loss = sum(episode_losses) / len(episode_losses)
            print(f"Average loss: {avg_loss:.4f}")
            return avg_loss
        else:
            print("Not enough data to train yet")
            return None
            
    def export_weights_to_dict(self):
        """Export model weights to dictionary for in-memory sync"""
        self.model.eval()
        
        weights_data = {
            "architecture": [20, 64, 64, 32],
            "layers": []
        }
        
        # Extract weights from each layer
        with torch.no_grad():
            # Layer 1: fc1 (20 → 64)
            W1 = self.model.fc1.weight.cpu().numpy().tolist()  # (64, 20)
            b1 = self.model.fc1.bias.cpu().numpy().tolist()    # (64,)
            weights_data["layers"].append({"W": W1, "b": b1})
            
            # Layer 2: fc2 (64 → 64)
            W2 = self.model.fc2.weight.cpu().numpy().tolist()  # (64, 64)
            b2 = self.model.fc2.bias.cpu().numpy().tolist()    # (64,)
            weights_data["layers"].append({"W": W2, "b": b2})
            
            # Layer 3: fc3 (64 → 32)
            W3 = self.model.fc3.weight.cpu().numpy().tolist()  # (32, 64)
            b3 = self.model.fc3.bias.cpu().numpy().tolist()    # (32,)
            weights_data["layers"].append({"W": W3, "b": b3})
            
        return weights_data
    
    def export_weights(self, output_path):
        """Export model weights to JSON format for Pure Python inference"""
        self.model.eval()
        
        weights_data = {
            "architecture": [20, 64, 64, 32],
            "layers": []
        }
        
        # Extract weights from each layer
        with torch.no_grad():
            # Layer 1: fc1 (20 → 64)
            W1 = self.model.fc1.weight.cpu().numpy().tolist()  # (64, 20)
            b1 = self.model.fc1.bias.cpu().numpy().tolist()    # (64,)
            weights_data["layers"].append({"W": W1, "b": b1})
            
            # Layer 2: fc2 (64 → 64)
            W2 = self.model.fc2.weight.cpu().numpy().tolist()  # (64, 64)
            b2 = self.model.fc2.bias.cpu().numpy().tolist()    # (64,)
            weights_data["layers"].append({"W": W2, "b": b2})
            
            # Layer 3: fc3 (64 → 32)
            W3 = self.model.fc3.weight.cpu().numpy().tolist()  # (32, 64)
            b3 = self.model.fc3.bias.cpu().numpy().tolist()    # (32,)
            weights_data["layers"].append({"W": W3, "b": b3})
        
        # Save to JSON
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(weights_data, f, indent=2)
        
        print(f"[Training] Weights exported to: {output_path}")
        print(f"[Training] File size: {os.path.getsize(output_path) / 1024:.2f} KB")
    
    def load_weights(self, json_path):
        """Load weights from JSON"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        layers = data['layers']
        
        # Load into model
        with torch.no_grad():
            # Layer 1
            self.model.fc1.weight.copy_(torch.FloatTensor(layers[0]['W']))
            self.model.fc1.bias.copy_(torch.FloatTensor(layers[0]['b']))
            
            # Layer 2
            self.model.fc2.weight.copy_(torch.FloatTensor(layers[1]['W']))
            self.model.fc2.bias.copy_(torch.FloatTensor(layers[1]['b']))
            
            # Layer 3
            self.model.fc3.weight.copy_(torch.FloatTensor(layers[2]['W']))
            self.model.fc3.bias.copy_(torch.FloatTensor(layers[2]['b']))
        
        print(f"[Training] Weights loaded from: {json_path}")
    
    def get_stats(self):
        """Get training statistics"""
        return {
            "total_steps": self.total_steps,
            "total_episodes": self.total_episodes,
            "buffer_size": len(self.replay_buffer),
            "avg_loss_last_100": sum(self.losses[-100:]) / len(self.losses[-100:]) if self.losses else 0,
            "device": str(self.device)
        }


# Demo: Supervised learning from random data
def demo_training():
    """Demo training with random data"""
    print("="*70)
    print("PYTORCH TRAINING DEMO")
    print("="*70)
    
    # Initialize trainer
    trainer = AITrainer(state_dim=20, action_dim=32, lr=0.001)
    
    # Generate random training data
    print("\n[Demo] Generating random training data...")
    for i in range(1000):
        state = [random.random() for _ in range(20)]
        action = random.randint(0, 31)
        reward = random.random()
        next_state = [random.random() for _ in range(20)]
        done = random.random() > 0.9
        
        trainer.collect_experience(state, action, reward, next_state, done)
    
    print(f"[Demo] Generated {len(trainer.replay_buffer)} experiences")
    
    # Train for a few episodes
    print("\n[Demo] Training for 5 episodes...")
    for episode in range(5):
        trainer.train_episode(num_steps=50, batch_size=32)
    
    # Show stats
    print("\n[Demo] Training Statistics:")
    stats = trainer.get_stats()
    for key, val in stats.items():
        print(f"  {key}: {val}")
    
    # Export weights
    output_path = "ai_core/weights/demo_trained_weights.json"
    trainer.export_weights(output_path)
    
    print("\n[SUCCESS] Training demo complete!")
    print("="*70)
    print(f"\nTo use trained weights in bot:")
    print(f"  ai load {output_path}")
    print("="*70)


if __name__ == "__main__":
    demo_training()
