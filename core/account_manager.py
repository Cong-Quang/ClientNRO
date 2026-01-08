import asyncio
from config import Config
from core.account import Account
from logs.logger_config import logger

class AccountManager:
    def __init__(self):
        self.accounts = []
        self.groups = {"all": []} # Predefined 'all' group
        # The target for commands. Can be an int (index) or str (group name).
        self.command_target = None
        # Plugin hooks (will be injected by main.py)
        self.plugin_hooks = None

    def load_accounts(self):
        """Loads account credentials from Config and creates Account objects."""
        for i, acc_data in enumerate(Config.ACCOUNTS):
            if acc_data.get("username") and acc_data.get("password"):
                acc = Account(
                    username=acc_data["username"],
                    password=acc_data["password"],
                    version=Config.VERSION,
                    host=Config.HOST,
                    port=Config.PORT,
                    proxy=acc_data.get("proxy")
                )
                acc.manager = self  # Set manager reference for plugin hooks
                self.accounts.append(acc)
                self.groups["all"].append(i) # Add all account indices to 'all' group

        logger.info(f"Đã tải {len(self.accounts)} tài khoản từ config.")
        # Set initial target to the first account if available
        if self.accounts:
            self.command_target = 0

    async def start_all(self):
        """Starts the login process for all loaded accounts concurrently (respecting limit)."""
        if not self.accounts:
            logger.warning("Không có tài khoản nào để bắt đầu.")
            return
        
        limit = Config.MAX_ACCOUNTS
        accounts_to_start = self.accounts[:limit]
        
        logger.info(f"Bắt đầu đăng nhập {len(accounts_to_start)} tài khoản (Giới hạn: {limit})...")
        
        login_tasks = [acc.login() for acc in accounts_to_start]
        await asyncio.gather(*login_tasks)
        
        # Set the first successfully logged-in account as the current target if none is set
        if self.command_target is None:
            for i, acc in enumerate(self.accounts):
                if acc.is_logged_in:
                    self.command_target = i
                    break

    def stop_all(self):
        """Stops all accounts."""
        logger.info("Đang dừng tất cả các tài khoản...")
        for acc in self.accounts:
            acc.stop()

    def get_active_account_count(self):
        return sum(1 for acc in self.accounts if acc.is_logged_in or (acc.session and acc.session.connected))

    def get_target_accounts(self) -> list[Account]:
        """Resolves the command_target to a list of account objects."""
        if self.command_target is None:
            return []
        
        if isinstance(self.command_target, int):
            if 0 <= self.command_target < len(self.accounts):
                return [self.accounts[self.command_target]]
            else:
                return []
        
        if isinstance(self.command_target, str):
            group_indices = self.groups.get(self.command_target)
            if group_indices is not None:
                # Trả về cả acc offline để có thể gửi lệnh login
                return [self.accounts[i] for i in group_indices if 0 <= i < len(self.accounts)]
        
        return []
