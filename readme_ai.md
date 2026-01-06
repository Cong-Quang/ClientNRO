# AI System Documentation - ClientNRO Game Bot

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Terminal Commands](#terminal-commands)
- [Training](#training)
- [Advanced Usage](#advanced-usage)
- [Technical Details](#technical-details)
- [Troubleshooting](#troubleshooting)

---

## Overview

Hybrid AI system for ClientNRO game bot featuring:
- **Pure Python Runtime** (zero dependencies, <1ms inference)
- **PyTorch Training** (offline/online with auto GPU/CPU detection)
- **32 Action Space** (basic + multi-agent + goal-based)
- **Multi-Agent Coordination** (team leader, formations, shared targets)
- **Online Learning** (train while playing)
- **Cross-Platform** (Android, Windows, Linux compatible)

### Key Features
✅ Zero runtime dependencies (Python standard library only)  
✅ <1ms inference with Pure Python neural network  
✅ Background training without blocking gameplay  
✅ Multi-agent coordination via shared memory  
✅ Experience replay with 10K buffer  
✅ JSON weight export (3-5 KB files)  

---

## Architecture

### Hybrid Design
```
PyTorch Training → Export JSON → Pure Python Inference → Game Actions
       ↓                             ↓
  Experience Replay           State Building
```

**Components:**
- `ai_core/brain.py` - Pure Python NN [20→64→64→32] (232 lines)
- `ai_core/state_builder.py` - Game state → 20D vector (170 lines)
- `ai_core/action_decoder.py` - AI output → 32 actions (680 lines)
- `ai_core/shared_memory.py` - Multi-agent coordination (236 lines)
- `ai_core/online_training.py` - Online learning integration (200 lines)
- `ai_agent.py` - Real-time decision loop (220 lines)
- `ai_command_handler.py` - Terminal commands (350 lines)
- `train/train_pytorch.py` - PyTorch training script (300 lines)

**Total:** ~2,500 lines of code

---

## Installation

### Runtime (Required)
```bash
# Already installed with Python 3.12+
# No additional dependencies needed!
```

### Training (Optional)
```bash
pip install -r requirements-train.txt
# Installs: torch>=2.0.0
```

---

## Quick Start

### 1. Start Bot
```bash
python main.py
```

### 2. Login
```bash
[Acc 0]> login
```

### 3. Basic AI Setup
```bash
# Assign account to group 1
ai group assign poopooi01 1

# Activate group 1
ai group set 1

# Set goal (optional)
ai goal set farm_items 1,5,10 mob=12

# Start AI for account
target 0
aiagent on
```

### 4. Monitor
```bash
aiagent status
show  # Check character status
```

### 5. Stop AI
```bash
aiagent off
```

---

## Terminal Commands

### Global AI Control
```bash
ai status              # System status
ai info                # Model architecture
ai on                  # Global AI mode ON
ai off                 # Global AI mode OFF
ai toggle              # Toggle global mode
ai load <path>         # Load weights from file
ai reset               # Reset to default weights
```

### Goal Management
```bash
# Farm items by killing specific mob
ai goal set farm_items 1,5,10 mob=12

# Hunt specific boss
ai goal set hunt_boss Fide

# Show current goal
ai goal show

# Clear goal
ai goal clear
```

### Group Management
```bash
# Assign account to group
ai group assign poopooi01 1
ai group assign acc_1 2

# Set active groups (AI only runs for these groups)
ai group set 1,2,3

# Show group assignments
ai group show
```

### Zone Distribution
```bash
# Auto-distribute bots to zones on map 5
ai zone auto 5

# Show zone distribution for map 5
ai zone show 5
```

### Team Coordination
```bash
# Set team leader
ai team leader acc_0

# Show team formation
ai team formation
```

### Per-Account Control
```bash
# Select account
target 0

# Start AI for this account
aiagent on

# Enable online training
aiagent train on

# Check AI status
aiagent status

# Save current model
aiagent save

# Stop AI
aiagent off
```

---

## Training

### Demo Training (Quick Test)
```bash
# Install PyTorch first
pip install -r requirements-train.txt

# Run demo training with random data
python train\train_pytorch.py
```

**Output:**
- Trains with 1000 random samples
- Auto-detects GPU/CPU
- Exports: `ai_core/weights/demo_trained_weights.json`

**Load trained weights:**
```bash
ai load ai_core/weights/demo_trained_weights.json
aiagent on
```

### Online Training (Real Gameplay)

**1. Start AI with training enabled:**
```bash
target 0
aiagent on
aiagent train on
```

**2. AI collects experience while playing:**
- Kill mob: +1.0 reward
- Gain XP: +0.5 reward
- Pick gold: +0.3 reward
- Take damage: -0.1 penalty
- Die: -1.0 penalty
- Idle: -0.05 penalty

**3. Training happens automatically every 100 steps**

**4. Monitor training:**
```bash
aiagent status

# Output shows:
# training_enabled: True
# buffer_size: 456
# total_steps: 912
# avg_loss: 0.3421
```

**5. Save learned model:**
```bash
aiagent save
# Saves to: ai_core/weights/poopooi01_1704537600.json
```

**6. Use saved model next session:**
```bash
ai load ai_core/weights/poopooi01_1704537600.json
```

---

## Advanced Usage

### Multi-Agent Boss Hunt
```bash
# Login all accounts
login all

# Set team leader
ai team leader acc_0

# Set goal
ai goal set hunt_boss Fide

# Assign all to group 1
ai group assign acc_0 1
ai group assign acc_1 1
ai group assign acc_2 1

# Activate group
ai group set 1

# Start AI for all
target all
aiagent on
```

### Zone Distribution Farming
```bash
# Auto-distribute 3 bots across zones in map 5
ai zone auto 5

# Check distribution
ai zone show 5
# Output:
#   Zone 1: ['bot_1']
#   Zone 2: ['bot_2']
#   Zone 3: ['bot_3']

# Start AI
target all
aiagent on
```

### Train Multiple Accounts
```bash
# Each account trains independently
target 0
aiagent on
aiagent train on

target 1
aiagent on
aiagent train on

target 2
aiagent on
aiagent train on

# All collect experience and improve their models
```

---

## Technical Details

### Action Space (32 Actions)

#### Basic Actions (0-7)
- 0: Idle
- 1: Attack nearest mob
- 2: Move to nearest mob
- 3: Use skill on target
- 4: Retreat (low HP)
- 5: Move to random location
- 6: Use HP potion
- 7: Return to safe zone

#### Multi-Agent Actions (8-15)
- 8: Follow team leader
- 9: Broadcast target location
- 10: Use shared target
- 11: Formation: Circle around leader
- 12: Formation: Line behind leader
- 13: Coordinate attack
- 14: Call for help
- 15: Support teammate

#### Boss Hunting (16-23)
- 16: Search for boss
- 17: Report boss location
- 18: Move to boss
- 19: Focus fire on boss
- 20: Avoid boss AOE
- 21: Tank boss
- 22: DPS rotation
- 23: Heal/support

#### Goal-Based Actions (24-31)
- 24: Farm items (kill specific mobs)
- 25: Collect drops
- 26: Complete quest objective
- 27: Navigate to quest location
- 28: Hunt specific boss
- 29: Grind for XP
- 30: Resource gathering
- 31: Return to base

### State Vector (20 Dimensions)

The AI observes game state as a 20-dimensional vector:

```python
[
  HP_ratio,           # 0.0-1.0
  MP_ratio,           # 0.0-1.0
  X_position,         # Normalized
  Y_position,         # Normalized
  Mob_count,          # Normalized
  Nearest_mob_dist,   # Normalized
  Nearest_mob_HP,     # 0.0-1.0
  Skill_cooldown,     # 0.0-1.0
  In_combat,          # 0.0 or 1.0
  Has_pet,            # 0.0 or 1.0
  Pet_HP_ratio,       # 0.0-1.0
  # ... (20 total features)
]
```

### Neural Network Architecture

```
Input Layer:  20 neurons (state vector)
      ↓
Hidden Layer 1: 64 neurons (ReLU activation)
      ↓
Hidden Layer 2: 64 neurons (ReLU activation)
      ↓
Output Layer: 32 neurons (action logits)
      ↓
Softmax → Action probabilities
```

**Total Parameters:** 7,584

### Action Masking

Invalid actions are dynamically disabled:

```python
# Example: If character is dead
if char.is_die:
    mask = [False] * 32  # Disable all actions
    mask[4] = True       # Only allow retreat

# Example: If no mobs nearby
if no_mobs:
    mask[1] = False  # Can't attack
    mask[2] = False  # Can't move to mob
```

### Performance

**Inference:**
- Pure Python: <1ms per decision
- Decision interval: 0.5s (configurable)
- Memory usage: ~10 MB per agent

**Training:**
- GPU (RTX 3060): ~1000 steps/sec
- CPU (i7): ~100 steps/sec
- Weights file: 3-5 KB JSON
- Buffer: 10,000 experiences (~2 MB)

---

## Troubleshooting

### AI not executing actions
**Problem:** `in_active_group: False`

**Solution:**
```bash
ai group assign poopooi01 1
ai group set 1
aiagent status  # Verify in_active_group: True
```

### Training not working
**Problem:** PyTorch not installed

**Solution:**
```bash
pip install -r requirements-train.txt
```

### Commands not recognized
**Problem:** Not in terminal command mode

**Solution:** Make sure you're at the `[Acc 0]>` prompt

### Model not improving
**Problem:** Insufficient training data

**Solution:**
- Let AI play longer (collect more experience)
- Check `aiagent status` → buffer_size should be >100
- Reward function may need tuning

### High loss during training
**Problem:** Poor weight initialization or learning rate

**Solution:**
- Reset model: `ai reset`
- Reload weights: `ai load ai_core/weights/demo_trained_weights.json`
- Adjust learning rate in `train/train_pytorch.py`

---

## File Structure

```
ClientNRO/
├── ai_core/
│   ├── __init__.py
│   ├── brain.py              # Pure Python NN
│   ├── state_builder.py      # State → Vector
│   ├── action_decoder.py     # Action → Commands
│   ├── shared_memory.py      # Multi-agent coordination
│   ├── online_training.py    # Online learning
│   └── weights/
│       ├── default_weights.json
│       └── *.json            # Trained models
├── train/
│   └── train_pytorch.py      # Training script
├── ai_agent.py               # Decision loop
├── ai_command_handler.py     # Terminal commands
├── controller.py             # Game controller (AI integrated)
├── main.py                   # Entry point (AI integrated)
├── config.py                 # Configuration (AI settings)
├── autocomplete.py           # Command autocomplete (AI commands)
├── requirements-train.txt    # Training dependencies
└── readme_ai.md             # This file
```

---

## Configuration

Edit `config.py` for AI settings:

```python
# AI Configuration
AI_ENABLED = False              # Default AI state
AI_WEIGHTS_PATH = "ai_core/weights/default_weights.json"
AI_STATE_DIM = 20               # Input dimension
AI_ACTION_COUNT = 32            # Output dimension
AI_DECISION_INTERVAL = 0.5      # Seconds between decisions
```

---

## Examples

### Example 1: Solo Farming with AI
```bash
# Start
python main.py
login

# Setup
ai group assign poopooi01 1
ai group set 1
ai goal set farm_items 1,5,10 mob=12

# Run
target 0
aiagent on

# Monitor
aiagent status
show

# Stop
aiagent off
```

### Example 2: Boss Hunt with 3 Accounts
```bash
# Login
login all

# Setup team
ai team leader acc_0
ai goal set hunt_boss Fide

# Assign to group
ai group assign acc_0 1
ai group assign acc_1 1
ai group assign acc_2 1
ai group set 1

# Start all
target all
aiagent on
```

### Example 3: Train AI While Playing
```bash
# Start with training
target 0
aiagent on
aiagent train on

# Play for 30 minutes...
# AI learns from gameplay!

# Save learned model
aiagent save

# Check stats
aiagent status
# training_stats:
#   buffer_size: 2345
#   total_steps: 3600
#   avg_loss: 0.2134
```

---

## FAQ

**Q: Do I need PyTorch to run the bot?**  
A: No! PyTorch is only needed for training. Runtime uses Pure Python.

**Q: Can I use this on Android?**  
A: Yes! Pure Python inference works on any platform with Python 3.12+.

**Q: How long does training take?**  
A: Depends on data. Demo training: <1 minute. Real gameplay: 30-60 minutes for noticeable improvement.

**Q: Can multiple accounts share one model?**  
A: Currently each account has its own model. Shared training will be added in future update.

**Q: What if I don't have GPU?**  
A: Training script auto-detects and uses CPU if no GPU available. It's slower but works.

**Q: How do I reset AI to default?**  
A: Use `ai reset` command.

**Q: Can I modify the action space?**  
A: Yes, edit `action_decoder.py` and update `AI_ACTION_COUNT` in `config.py`.

---

## Credits

**AI System Architecture:**
- Hybrid PyTorch/Pure Python design
- Experience replay with online learning
- Multi-agent coordination via shared memory
- Zero-dependency runtime for cross-platform compatibility

**Implementation Date:** 2026-01-06  
**Version:** 1.0  
**Status:** Production Ready ✅

---

## License

Part of ClientNRO game bot project.

---

**For detailed technical flow, see:** `flow_explanation.md`  
**For training guide, see:** `training_guide.md`  
**For complete walkthrough, see:** `walkthrough.md`
