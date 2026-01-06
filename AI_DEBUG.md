# AI Agent Debug Guide - Vì sao không có action?

## Phân tích weights file

**File:** `poopooi01_1767695586.json`

✅ **Weights hợp lệ:**
- Architecture: [20, 64, 64, 32] ✓
- Có 3 layers với weights thực (not random)
- File size: 251 KB (đã train)

➡️ **Kết luận:** Model đã được train, không phải vấn đề về weights.

---

## Nguyên nhân chính: `in_active_group: False`

### Vấn đề
Khi bạn chạy `aiagent status`, có thể thấy:
```
in_active_group: False
```

**Điều này có nghĩa:**
- AI Agent đang chạy (enabled: True)
- Nhưng account KHÔNG ở trong active group
- → AI **skip tất cả actions** mỗi 0.5s!

### Tại sao?
Xem code trong `ai_agent.py`:

```python
async def _decision_loop(self):
    while self.enabled:
        # CHECKPOINT 1: Check active group
        if not self.shared_memory.is_bot_in_active_group(self.account_id):
            await asyncio.sleep(0.5)
            continue  # ← Skip action execution!
        
        # Các bước sau không bao giờ chạy...
        state = self.state_builder.build_state(...)
        action = await self.brain.predict(...)
        # ...
```

**Flow khi `in_active_group: False`:**
```
Check group → False → Sleep 0.5s → Loop back
     ↓
No state building
No prediction  
No action execution
```

---

## Solution: Assign vào group

### Bước 1: Assign account vào group
```bash
ai group assign poopooi01 1
```

**Output:**
```
[SharedMemory] Assigned poopooi01 to group 1
```

### Bước 2: Set active groups
```bash
ai group set 1
```

**Output:**  
```
[SharedMemory] Active groups: [1]
[AI] Active groups set to: [1]
```

### Bước 3: Verify
```bash
aiagent status
```

**Kỳ vọng output:**
```
enabled: True
in_active_group: True  ← PHẢI LÀ TRUE!
```

---

## Các nguyên nhân khác (ít phổ biến)

### 2. Action Mask disable tất cả
```python
# Nếu character chết
if char.is_die:
    mask = [False] * 32  # All actions disabled
```

**Check:** Xem character còn sống không?

### 3. Random weights predict Idle (Action 0)
Random weights có thể luôn predict action 0 (Idle).

**Check:** Load trained weights:
```bash
ai load ai_core/weights/poopooi01_1767695586.json
```

### 4. Decision interval quá dài
Default: 0.5s. Có thể bạn nghĩ "không có action" vì chờ quá lâu.

**Check:** Trong `config.py`:
```python
AI_DECISION_INTERVAL = 0.5  # Try 0.2 for faster actions
```

---

## Debug Checklist

Chạy từng bước để debug:

### Step 1: Check AI status
```bash
target 0
aiagent status
```

**Kiểm tra:**
- [ ] `enabled: True`
- [ ] `in_active_group: True` ← QUAN TRỌNG NHẤT!
- [ ] `brain_loaded: True`

### Step 2: Check group assignment
```bash
ai group show
```

**Kỳ vọng:**
```
AI Group Status:
  Active groups: [1]
  
Group Assignments:
  Group 1: ['poopooi01']
```

### Step 3: Check character status
```bash
show
```

**Kiểm tra:**
- HP > 0 (not dead)
- Có mobs nearby

### Step 4: Test với goal
```bash
ai goal set farm_items 1,5,10 mob=12
aiagent status
```

**Kiểm tra:**
- `current_goal` có hiển thị không?

### Step 5: Monitor logs
Watch terminal output khi AI chạy. Nếu `in_active_group: True`, bạn sẽ thấy:
- State building messages
- Action execution attempts
- Training logs (if enabled)

---

## Quick Fix (All-in-one)

Nếu bạn muốn fix nhanh, chạy tất cả cùng lúc:

```bash
# Stop AI
aiagent off

# Setup groups
ai group assign poopooi01 1
ai group set 1

# Set goal (optional)
ai goal set farm_items 1,5,10 mob=12

# Load trained weights
ai load ai_core/weights/poopooi01_1767695586.json

# Verify
aiagent status

# Start AI
aiagent on

# Monitor
show
```

**Expected behavior sau khi fix:**
- AI sẽ execute action mỗi 0.5s
- Terminal hiển thị action logs (nếu DEBUG on)
- Character di chuyển/attack

---

## How to verify AI is working

### Method 1: Watch character
- Character sẽ di chuyển/attack mobs
- HP/MP thay đổi
- Position thay đổi

### Method 2: Check training stats
```bash
aiagent status
```

**Nếu training enabled, sẽ thấy:**
```
training_stats:
  buffer_size: 45  ← Tăng dần
  total_steps: 90  ← Tăng dần
```

### Method 3: Enable debug logging
Trong `brain.py`, có dòng:
```python
if logger.isEnabledFor(10):  # DEBUG level
    logger.debug(f"[AI Agent] Action {action_idx} ...")
```

Set logger to DEBUG để thấy chi tiết.

---

## Summary

**90% trường hợp:**
```bash
# Nguyên nhân
in_active_group: False

# Fix
ai group assign poopooi01 1
ai group set 1
```

**10% trường hợp khác:**
- Character chết (HP = 0)
- Random weights → action 0
- Bugs trong code

**Verify:**
```bash
aiagent status
# Phải thấy: in_active_group: True
```

---

*Debug guide created: 2026-01-06*
