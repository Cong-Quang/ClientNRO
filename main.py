import asyncio
from network.session import Session
from network.message import Message
from network.service import Service
from config import Config
from controller import Controller
from cmd import Cmd
from logs.logger_config import logger 

# --- Cấu hình Logging ---
# Đặt True để xem log chi tiết (DEBUG), đặt False để xem log quan trọng (INFO)
VERBOSE_LOGGING = True 

# if VERBOSE_LOGGING:
#     logger.basicConfig(level=logger.DEBUG, format='[%(levelname)s] %(message)s')
# else:
#     logger.basicConfig(level=logger.INFO, format='[%(levelname)s] %(message)s')

# logger = logger.getLogger(__name__)

async def main():
    controller = Controller()
    session = Session(controller=controller)
    Service.setup(session) # Initialize Service Singleton
    
    await session.connect(Config.HOST, Config.PORT)

    # Wait for key exchange to likely happen
    await asyncio.sleep(1)

    if session.connected:
        logger.info("Gửi Thông tin đăng nhập tới server")
        
        # 1. Send setClientType (Cmd -29, SubCmd 2)
        # Service.cs: setClientType()
        msg_client = Message(Cmd.NOT_LOGIN)
        writer = msg_client.writer()
        writer.write_byte(2)              # Sub-command: CLIENT_INFO
        writer.write_byte(4)              # Main.typeClient (4 = PC usually)
        writer.write_byte(2)              # mGraphics.zoomLevel (try 2)
        writer.write_bool(False)          # Unknown bool
        writer.write_int(1024)            # Width
        writer.write_int(600)             # Height
        writer.write_bool(True)           # isQwerty
        writer.write_bool(True)           # isTouch
        writer.write_utf(f"Con Cặc|{Config.VERSION}") # Platform | Version
        
        await session.send_message(msg_client)
        
        await asyncio.sleep(0.5)

        logger.info("Gửi gói tin androi (Cmd 126)...")
        msg_pack = Message(126) # Cmd.ANDROID_PACK
        msg_pack.writer().write_utf("") # Empty pack name
        await session.send_message(msg_pack)

        await asyncio.sleep(0.5) # Short delay

        logger.info("Gửi gói tin đăng nhập")
        
        # 2. Send Login (Cmd -29, SubCmd 0)
        msg_login = Message(Cmd.NOT_LOGIN)
        writer = msg_login.writer()
        writer.write_byte(0)              # sub-command LOGIN
        writer.write_utf(Config.UerName)     # Username
        writer.write_utf(Config.PassWord)      # Password
        writer.write_utf(Config.VERSION)  # Version
        writer.write_byte(1)              # Type (1 for isLogin2/Standard)
        
        await session.send_message(msg_login)
        
        # Keep alive to receive response
        while session.connected:
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopping...")