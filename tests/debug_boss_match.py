import time
from logic.boss_manager import BossManager

def debug_matching():
    bm = BossManager()
    bosses = bm.get_bosses()
    print("=== Current Bosses in BossManager ===")
    for b in bosses:
        print(f"Name: '{b['name']}', Status: '{b['status']}', Map: {b['map_id']}")
        
    target = "Số 4"
    target_lower = target.lower()
    print(f"\n=== Testing Match for '{target}' ===")
    
    found = False
    for b in bosses:
        b_name_lower = b['name'].lower()
        print(f"Checking '{target_lower}' in '{b_name_lower}'...", end=" ")
        
        if target_lower in b_name_lower:
            print("MATCH FOUND!")
            if b['status'] == 'Sống':
                print("  -> STATUS IS ALIVE! (Should work)")
                found = True
            else:
                print("  -> BUT STATUS IS DEAD/UNKNOWN.")
        else:
            print("NO MATCH.")

    if not found:
        print("\nCONCLUSION: Logic failed to find a living boss.")
    else:
        print("\nCONCLUSION: Logic works correcty.")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    debug_matching()
