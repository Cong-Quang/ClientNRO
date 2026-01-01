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
    def __init__(self, username, password, version, host, port, proxy=None):
        self.username = username
        self.password = password
        self.version = version
        self.host = host
        self.port = port
        self.proxy = proxy
        self.is_logged_in = False
        self.tasks = []

        # Each account has its own instance of major components
        self.char = Char()
        self.pet = Pet()
        # The controller needs a reference to this account to access other components
        self.controller = Controller(self) 
        self.session = Session(self.controller, proxy=self.proxy)
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
            
            # Start connection monitor
            if Config.AUTO_RECONNECT:
                self.tasks.append(asyncio.create_task(self.monitor_connection()))
                
            return True
        else:
            logger.error(f"[{self.username}] Login failed. Disconnected.")
            return False

    async def monitor_connection(self):
        """Monitors the connection and reconnects if dropped."""
        logger.info(f"[{self.username}] Auto-reconnect monitoring started.")
        while True:
            await asyncio.sleep(5)
            # If we think we are logged in (or should be), but session is closed
            if self.is_logged_in and not self.session.connected:
                logger.warning(f"[{self.username}] Connection lost! Attempting to reconnect in 5 seconds...")
                self.is_logged_in = False 
                
                await asyncio.sleep(5)
                
                # Re-login logic
                # We need to recreate session components cleanly
                self.stop() # Cleanup old tasks/session
                
                # Re-init essential components if needed, or just call login
                # Account object reuses existing Char/Pet/Controller
                # But Session needs a fresh start usually.
                self.session = Session(self.controller)
                self.service = Service(self.session, self.char)
                # Controller needs to point to new stuff? 
                # Controller holds 'account' reference, account holds 'service/session'.
                # We just updated account.session/service, so controller.account.service should be fine.
                
                logger.info(f"[{self.username}] Reconnecting...")
                await self.login()
                
            elif not self.is_logged_in:
                 # If manually stopped or not logged in, stop monitoring
                 # But wait, if login failed, is_logged_in is False.
                 # If we want to persist, we should keep checking?
                 # For now, let's assume if is_logged_in becomes False via stop(), we break.
                 # But here we set is_logged_in=False above.
                 # So we need a flag 'should_be_online'.
                 pass
            
            # If the task is cancelled (by stop()), this loop breaks naturally (await sleep throws CancelledError)

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
