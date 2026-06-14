"""
Live test script for setup_accounts_command.
Runs the actual bot login and setup flow WITHOUT interactive CLI.
Usage: python tests/live_test_setup.py <start_idx> <end_idx> [force|reset]
Example: python tests/live_test_setup.py 5 10 reset
"""
import asyncio
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from core.account_manager import AccountManager
from logs.logger_config import TerminalColors, logger
from commands.setup_accounts_command import SetupAccountsCommand

C = TerminalColors

async def run_test(start_idx, end_idx, force=False, reset=False):
    print(f"{C.CYAN}========================================{C.RESET}")
    print(f"{C.CYAN}LIVE TEST: setup_accounts {start_idx} {end_idx}{C.RESET}")
    print(f"{C.CYAN}========================================{C.RESET}")

    # Initialize config
    Config.init()

    # Create account manager
    manager = AccountManager()
    manager.load_accounts()

    accounts = manager.accounts[start_idx:end_idx + 1]
    print(f"\n{C.YELLOW}Accounts to test: {[a.username for a in accounts]}{C.RESET}")
    print(f"Total: {len(accounts)} accounts\n")

    # Create setup command
    setup_cmd = SetupAccountsCommand(manager)

    # If reset, do reset first via execute
    if reset:
        print(f"\n{C.CYAN}=== RESET STATE ==={C.RESET}")
        await setup_cmd.execute(parts=["setup_accounts", str(start_idx), str(end_idx), "reset"])
        print(f"{C.GREEN}→ Đã reset trạng thái.{C.RESET}")
        # Wait a bit after reset
        await asyncio.sleep(1)

    # Login all accounts in parallel (max 5 at a time)
    print(f"\n{C.CYAN}=== LOGIN ACCOUNTS ==={C.RESET}")
    sem = asyncio.Semaphore(5)

    async def login_with_sem(acc):
        async with sem:
            print(f"{C.DIM}[{acc.username}] Đang đăng nhập...{C.RESET}")
            success = await acc.login()
            if success:
                print(f"{C.GREEN}[{acc.username}] ✓ Đăng nhập thành công.{C.RESET}")
            else:
                print(f"{C.RED}[{acc.username}] ✗ Đăng nhập thất bại.{C.RESET}")
            return success

    login_tasks = [login_with_sem(acc) for acc in accounts]
    login_results = await asyncio.gather(*login_tasks)

    online_count = sum(1 for r in login_results if r)
    print(f"\n{C.CYAN}Online: {online_count}/{len(accounts)}{C.RESET}")

    if online_count == 0:
        print(f"{C.RED}Không có account nào online. Dừng test.{C.RESET}")
        return

    # Chờ game ready
    print(f"\n{C.CYAN}=== WAIT GAME READY (30s) ==={C.RESET}")
    for i in range(30):
        ready_count = 0
        for acc in accounts:
            if acc.is_logged_in and acc.controller.tile_map.map_id > 0 and acc.char.c_power > 0:
                ready_count += 1
        if ready_count == online_count:
            print(f"{C.GREEN}Tất cả accounts đã sẵn sàng sau {i+1}s.{C.RESET}")
            break
        await asyncio.sleep(1)
        if i % 5 == 0:
            print(f"{C.DIM}  Đợi game ready... ({i+1}s, {ready_count}/{online_count} ready){C.RESET}")

    # Refresh inventory for all accounts
    print(f"\n{C.CYAN}=== REFRESH INVENTORY ==={C.RESET}")
    for acc in accounts:
        if acc.is_logged_in:
            try:
                await acc.service.request_me_info()
            except Exception:
                pass
    await asyncio.sleep(1)

    # Show initial state
    print(f"\n{C.CYAN}=== INITIAL STATE ==={C.RESET}")
    for acc in accounts:
        if acc.is_logged_in:
            gold = getattr(acc.char, 'xu', 0)
            gems = getattr(acc.char, 'ngoc', 0)
            power = acc.char.c_power
            bag_count = sum(1 for it in (acc.char.arr_item_bag or []) if it is not None)
            print(f"  {C.YELLOW}{acc.username}{C.RESET}: SM={power}, Vàng={gold}, Ngọc={gems}, Bag={bag_count} items")

    # RUN SETUP
    print(f"\n{C.CYAN}=== RUN SETUP ==={C.RESET}")
    print(f"  accounts {start_idx}-{end_idx}, force={force}, reset={reset}")
    print()

    # Reset done earlier, now run actual setup
    parts = ["setup_accounts", str(start_idx), str(end_idx)]
    if force:
        parts.append("force")
    # Don't pass reset here - already handled above

    start_time = time.time()
    result = await setup_cmd.execute(parts=parts)
    elapsed = time.time() - start_time

    # Final state
    print(f"\n{C.CYAN}=== FINAL STATE ==={C.RESET}")
    for acc in accounts:
        if acc.is_logged_in:
            try:
                await acc.service.request_me_info()
                await asyncio.sleep(0.2)
            except Exception:
                pass
            gold = getattr(acc.char, 'xu', 0)
            gems = getattr(acc.char, 'ngoc', 0)
            power = acc.char.c_power
            bag_count = sum(1 for it in (acc.char.arr_item_bag or []) if it is not None)
            bean_count = setup_cmd._count_beans(acc)
            bua_count = setup_cmd._count_bua_items(acc)
            item16 = setup_cmd._count_item(acc, 16)
            item12 = setup_cmd._count_item(acc, 12)
            print(f"  {C.YELLOW}{acc.username}{C.RESET}: SM={power}, Vàng={gold}, Ngọc={gems}")
            print(f"    Bag: {bag_count} items, Đậu: {bean_count}, Bùa: {bua_count}, Item16: {item16}, Item12: {item12}")

    print(f"\n{C.CYAN}========================================{C.RESET}")
    print(f"{C.CYAN}TEST COMPLETED in {elapsed:.1f}s{C.RESET}")
    if isinstance(result, bool):
        print(f"{C.GREEN if result else C.RED}Result: {result}{C.RESET}")
    else:
        print(f"{C.GREEN}Setup command executed.{C.RESET}")
    print(f"{C.CYAN}========================================{C.RESET}")

    # Write test report
    report_path = "logs/setup_test_report.md"
    os.makedirs("logs", exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Setup Test Report\n\n")
        f.write(f"- **Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Accounts:** {start_idx}-{end_idx} ({', '.join(a.username for a in accounts)})\n")
        f.write(f"- **Force:** {force}\n")
        f.write(f"- **Reset:** {reset}\n")
        f.write(f"- **Duration:** {elapsed:.1f}s\n")
        f.write(f"- **Result:** {'Success' if isinstance(result, bool) and result else 'Completed'}\n\n")
        f.write("## Per-Account Summary\n\n")
        for acc in accounts:
            if acc.is_logged_in:
                gold = getattr(acc.char, 'xu', 0)
                gems = getattr(acc.char, 'ngoc', 0)
                power = acc.char.c_power
                step_state = setup_cmd.state_mgr.get(acc.username)
                completed_steps = [s for s, v in step_state.steps.items() if v.get('completed')]
                f.write(f"### {acc.username}\n")
                f.write(f"- SM: {power}, Gold: {gold}, Gems: {gems}\n")
                f.write(f"- Completed steps: {', '.join(completed_steps) if completed_steps else 'None'}\n")
                f.write(f"- Errors: {[v.get('error') for v in step_state.steps.values() if v.get('error')]}\n\n")

    print(f"\n{C.GREEN}Report saved to: {report_path}{C.RESET}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tests/live_test_setup.py <start_idx> <end_idx> [force|reset]")
        print("Example: python tests/live_test_setup.py 5 10 reset")
        sys.exit(1)

    start_idx = int(sys.argv[1])
    end_idx = int(sys.argv[2])
    force = "force" in sys.argv
    reset = "reset" in sys.argv

    asyncio.run(run_test(start_idx, end_idx, force, reset))
