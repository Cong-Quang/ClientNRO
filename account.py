import asyncio
import sys
from network.session import Session
from network.service import Service
from controller import Controller
from model.game_objects import Char, Pet
from config import Config
from logs.logger_config import logger, TerminalColors
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
        self.status = "Offline"
        self._should_auto_reconnect = False
        self.login_event = asyncio.Event()
        self.last_opennpc_compact = False

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
        writer.write_utf(f"client 1|{self.version}") # Platform | Version
        await self.session.send_message(msg_client)
        await asyncio.sleep(0.5)

        # 2. Send android pack (Cmd 126)
        logger.info(f"[{self.username}] Sending android pack (Cmd 126)...")
        msg_pack = Message(126)
        msg_pack.writer().write_utf("")
        await self.session.send_message(msg_pack)
        await asyncio.sleep(0.5)

        # 3. Send login credentials (Cmd -29, SubCmd 0)
        logger.info(f"[{self.username}] Sending login packet, waiting for confirmation...")
        self.login_event.clear() # Clear event before login attempt
        msg_login = Message(Cmd.NOT_LOGIN)
        writer = msg_login.writer()
        writer.write_byte(0)              # sub-command LOGIN
        writer.write_utf(self.username)
        writer.write_utf(self.password)
        writer.write_utf(self.version)
        writer.write_byte(1)              # Type (1 for isLogin2/Standard)
        await self.session.send_message(msg_login)
        
        try:
            await asyncio.wait_for(self.login_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            logger.error(f"[{self.username}] Login failed: No response from server (Timeout).")
            # Don't call self.stop() as it disables auto-reconnect.
            # Just clean up the current session attempt.
            if self.session:
                self.session.disconnect()
            self.stop_tasks()
            return False

        # If event was set, login is successful
        self.is_logged_in = True
        self.status = "Logged In"
        self._should_auto_reconnect = True
        logger.info(f"[{self.username}] Login successful! Account is running.")
        
        # Proactive notification to user
        sys.stdout.flush()
        sys.stderr.write(f"\r\033[K{TerminalColors.GREEN}[{self.username}] Đã đăng nhập thành công.{TerminalColors.RESET}\n")

        return True

    async def handle_disconnect(self):
        """Handles the disconnection event, triggering auto-reconnect if configured."""
        if not Config.AUTO_LOGIN or not self._should_auto_reconnect:
            # If auto-login is off, or this was a manual logout, just set status and exit
            self.status = "Offline"
            self.is_logged_in = False
            return

        logger.warning(f"[{self.username}] Connection lost! Starting auto-reconnect process...")
        self.status = "Reconnecting"
        self.is_logged_in = False

        while Config.AUTO_LOGIN and self._should_auto_reconnect:
            logger.info(f"[{self.username}] Attempting to reconnect in 0.5 seconds...")
            await asyncio.sleep(0.5)

            # Cleanup and re-initialize session components before trying to log in again
            self.stop_tasks() # Stop only tasks, not the whole account state
            self.session = Session(self.controller, proxy=self.proxy)
            self.service = Service(self.session, self.char)

            # Try to login again
            try:
                login_success = await self.login()
                if login_success:
                    logger.info(f"[{self.username}] Reconnect successful!")
                    # Proactive notification to user
                    sys.stdout.flush()
                    sys.stderr.write(f"\r\033[K{TerminalColors.GREEN}[{self.username}] Đã kết nối lại thành công.{TerminalColors.RESET}\n")
                    break # Exit the while loop on success
            except Exception as e:
                logger.error(f"[{self.username}] Error during reconnect attempt: {e}")
            
            # If login fails, the loop continues

    def stop_tasks(self):
        """Stops all running asyncio tasks for this account without a full logout."""
        for task in self.tasks:
            if not task.done():
                task.cancel()
        self.tasks = []

    def stop(self):
        """
        Stops all running tasks and disconnects the session for this account.
        This is considered a manual stop, so auto-reconnect is disabled.
        """
        logger.info(f"[{self.username}] Stopping account...")
        self._should_auto_reconnect = False # Disable auto-reconnect on manual stop
        self.stop_tasks()
        if self.session and self.session.connected:
            self.session.disconnect()
        self.is_logged_in = False
        self.status = "Offline"
