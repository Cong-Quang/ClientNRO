import asyncio
import sys, io, os
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from config import Config
from core.account_manager import AccountManager
from services.inventory import InventoryService

async def main():
    Config.init()
    manager = AccountManager()
    manager.load_accounts()
    acc = manager.accounts[5]
    print(f"Logging in as {acc.username}...")
    if await acc.login():
        print("Logged in! Waiting for game state to load...")
        await asyncio.sleep(2)
        inv = InventoryService(acc, print)
        await inv.refresh()
        print("\n--- INVENTORY BAG ---")
        for idx, item in enumerate(acc.char.arr_item_bag or []):
            if item is not None:
                opts = ", ".join([f"[{o.option_template_id}:{o.param}]" for o in (item.item_option or [])])
                print(f"Index {idx}: ID {item.item_id} | Qty {item.quantity} | Name: {item.info} | Opts: {opts}")
        print("\n--- EQUIPMENT MASTER ---")
        for idx, item in enumerate(acc.char.arr_item_body or []):
            if item is not None:
                opts = ", ".join([f"[{o.option_template_id}:{o.param}]" for o in (item.item_option or [])])
                print(f"Body {idx}: ID {item.item_id} | Name: {item.info} | Opts: {opts}")
        print("\n--- EQUIPMENT PET ---")
        if acc.pet and acc.pet.have_pet:
            # Request pet info first to load it
            acc.controller.pet_info_event.clear()
            await acc.service.pet_info()
            try:
                await asyncio.wait_for(acc.controller.pet_info_event.wait(), timeout=3.0)
            except Exception:
                pass
            for idx, item in enumerate(acc.pet.arr_item_body or []):
                if item is not None:
                    opts = ", ".join([f"[{o.option_template_id}:{o.param}]" for o in (item.item_option or [])])
                    print(f"PetBody {idx}: ID {item.item_id} | Name: {item.info} | Opts: {opts}")
        acc.session.disconnect()
    else:
        print("Login failed")

if __name__ == "__main__":
    asyncio.run(main())
