import asyncio
from config import Config
from core.account import Account

async def run_test():
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    Config.init()
    # Create the account
    acc = Account("poopooi01", "02082003", Config.VERSION, Config.HOST, Config.PORT)
    print("Testing login directly...")
    success = await acc.login()
    if success:
        print("Login SUCCESS!")
    else:
        print("Login FAILED!")
    
    # Wait a bit to catch any background messages
    await asyncio.sleep(2)
    acc.stop()

if __name__ == "__main__":
    asyncio.run(run_test())
