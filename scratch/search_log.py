import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

log_path = r"C:\Users\quang\.gemini\antigravity-ide\brain\6ff49751-9782-4818-9506-b9e8f57d780e\.system_generated\tasks\task-860.log"
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print("Search results:")
found = False
count = 0
for line in lines:
    ll = line.lower()
    if "=== [10/14]" in ll:
        found = True
    if found:
        print(line.strip())
        count += 1
        if count >= 30:
            break
