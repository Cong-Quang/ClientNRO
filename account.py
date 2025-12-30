# account.py
import asyncio
from network.session import Session
from network.service import Service
from controller import Controller
from model.game_objects import Char, Pet
from config import Config
from logs.logger_config import logger
from cmd import Cmd
from network.message import Message

class Account:
    """
    Encapsulates all objects and data for a single game account session.
    """
    def __init__(self, username, password, version, host, port):
        self.username = username
        self.password = password
        self.version = version
        self.host = host
        self.port = port
        self.is_logged_in = False
        self.tasks = []

        # Each account has its own instance of major components
        self.char = Char()
        self.pet = Pet()
        # The controller needs a reference to this account to access other components
        self.controller = Controller(self) 
        self.session = Session(self.controller)
        # The service is now a regular object, instantiated per account
        self.service = Service(self.session, self.char)


    async def login(self):
        """
        Connects and performs the login sequence for this account.
        """
        listen_task = await self.session.connect(self.host, self.port)
        if listen_task:
            self.tasks.append(listen_task)
        
        await asyncio.sleep(1)

        if not self.session.connected:
            logger.error(f"[{self.username}] Connection failed. Cannot proceed with login.")
            return False

        logger.info(f"[{self.username}] Sending login information to the server...")

        # 1. Send setClientType (Cmd -29, SubCmd 2)
        msg_client = Message(Cmd.NOT_LOGIN)
        writer = msg_client.writer()
        writer.write_byte(2)              # Sub-command: CLIENT_INFO
        writer.write_byte(4)              # Main.typeClient (4 = PC)
        writer.write_byte(2)              # mGraphics.zoomLevel
        writer.write_bool(False)          # Unknown bool
        writer.write_int(1024)            # Width
        writer.write_int(600)             # Height
        writer.write_bool(True)           # isQwerty
        writer.write_bool(True)           # isTouch
        writer.write_utf(f"Con Cặc|{self.version}") # Platform | Version
        await self.session.send_message(msg_client)
        await asyncio.sleep(0.5)

        # 2. Send android pack (Cmd 126)
        logger.info(f"[{self.username}] Sending android pack (Cmd 126)...")
        msg_pack = Message(126)
        msg_pack.writer().write_utf("")
        await self.session.send_message(msg_pack)
        await asyncio.sleep(0.5)

        # 3. Send login credentials (Cmd -29, SubCmd 0)
        logger.info(f"[{self.username}] Sending login packet...")
        msg_login = Message(Cmd.NOT_LOGIN)
        writer = msg_login.writer()
        writer.write_byte(0)              # sub-command LOGIN
        writer.write_utf(self.username)
        writer.write_utf(self.password)
        writer.write_utf(self.version)
        writer.write_byte(1)              # Type (1 for isLogin2/Standard)
        await self.session.send_message(msg_login)
        
        # A short wait to see if the login is successful
        await asyncio.sleep(2) 
        
        if self.session.connected:
            self.is_logged_in = True
            logger.info(f"[{self.username}] Login successful! Account is running.")
            return True
        else:
            logger.error(f"[{self.username}] Login failed. Disconnected.")
            return False

    def stop(self):
        """
        Stops all running tasks and disconnects the session for this account.
        """
        logger.info(f"[{self.username}] Stopping account...")
        for task in self.tasks:
            if not task.done():
                task.cancel()
        if self.session and self.session.connected:
            self.session.disconnect()
        self.is_logged_in = False
