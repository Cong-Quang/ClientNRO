import asyncio
import os
from config import Config
from account import Account
from logs.logger_config import logger, set_logger_status, TerminalColors
from ui import display_help, display_pet_info, display_pet_help, display_character_status
from autocomplete import get_input_with_autocomplete

class AccountManager:
    def __init__(self):
        self.accounts = []
        self.groups = {"all": []} # Predefined 'all' group
        # The target for commands. Can be an int (index) or str (group name).
        self.command_target = None

    def load_accounts(self):
        """Loads account credentials from Config and creates Account objects."""
        for i, acc_data in enumerate(Config.ACCOUNTS):
            if acc_data.get("username") and acc_data.get("password"):
                acc = Account(
                    username=acc_data["username"],
                    password=acc_data["password"],
                    version=Config.VERSION,
                    host=Config.HOST,
                    port=Config.PORT
                )
                self.accounts.append(acc)
                self.groups["all"].append(i) # Add all account indices to 'all' group

        logger.info(f"Đã tải {len(self.accounts)} tài khoản từ config.")
        # Set initial target to the first account if available
        if self.accounts:
            self.command_target = 0

    async def start_all(self):
        """Starts the login process for all loaded accounts concurrently."""
        if not self.accounts:
            logger.warning("Không có tài khoản nào để bắt đầu.")
            return
        
        login_tasks = [acc.login() for acc in self.accounts]
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
                return [self.accounts[i] for i in group_indices if 0 <= i < len(self.accounts) and self.accounts[i].is_logged_in]
        
        return []

async def command_loop(manager: AccountManager):
    """The main interactive command loop for managing multiple accounts."""
    C = TerminalColors
    while True:
        target_str = f"{C.RED}None{C.RESET}"
        if manager.command_target is not None:
            if isinstance(manager.command_target, int):
                target_str = f"Acc {C.YELLOW}{manager.command_target}{C.RESET}"
            else:
                target_str = f"Group '{C.YELLOW}{manager.command_target}{C.RESET}'"
        
        prompt = f"[{target_str}]> "

        try:
            # command = await asyncio.to_thread(input, prompt)
            command = await asyncio.to_thread(get_input_with_autocomplete, prompt)
            command = command.strip().lower()
            parts = command.split()
            if not command:
                continue

            cmd_base = parts[0]

            if cmd_base == "exit":
                manager.stop_all()
                break
            
            elif cmd_base in ("cls", "clear"):
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            elif cmd_base == "help":
                display_help()
                continue

            elif cmd_base == "list":
                print(f"{C.CYAN}--- Danh sách tài khoản ---{C.RESET}")
                for i, acc in enumerate(manager.accounts):
                    status = f"{C.GREEN}Logged In{C.RESET}" if acc.is_logged_in else f"{C.RED}Offline{C.RESET}"
                    target_marker = ""
                    if isinstance(manager.command_target, int) and i == manager.command_target:
                        target_marker = f"{C.PURPLE}(*){C.RESET}"
                    print(f"[{C.YELLOW}{i}{C.RESET}] {acc.username:<20} {status} {target_marker}")
                continue
            
            # --- Group Management ---
            elif cmd_base == "group":
                if len(parts) < 2:
                    logger.warning("Lệnh group không hợp lệ. Dùng 'group list', 'group create <name> <ids>', 'group delete <name>', ...")
                    continue
                
                sub_cmd = parts[1]
                if sub_cmd == "list":
                    print(f"{C.CYAN}--- Danh sách nhóm ---{C.RESET}")
                    for name, indices in manager.groups.items():
                        members = ", ".join([manager.accounts[i].username for i in indices])
                        print(f"- {C.CYAN}{name}{C.RESET}: [{C.YELLOW}{', '.join(map(str, indices))}{C.RESET}] ({members})")

                elif sub_cmd == "create" and len(parts) >= 4:
                    name = parts[2]
                    if name == "all":
                        logger.error("Không thể tạo nhóm với tên 'all'.")
                        continue
                    try:
                        indices = [int(i) for i in parts[3].split(',')]
                        if all(0 <= i < len(manager.accounts) for i in indices):
                            manager.groups[name] = sorted(list(set(indices)))
                            logger.info(f"Đã tạo nhóm '{C.YELLOW}{name}{C.RESET}' với các thành viên: {manager.groups[name]}")
                        else:
                            logger.error("Một hoặc nhiều chỉ số không hợp lệ.")
                    except ValueError:
                        logger.error("Chỉ số thành viên không hợp lệ. Phải là các số được phân tách bằng dấu phẩy (VD: 1,2,3).")

                elif sub_cmd == "delete" and len(parts) == 3:
                    name = parts[2]
                    if name == "all":
                        logger.error("Không thể xóa nhóm 'all'.")
                    elif name in manager.groups:
                        del manager.groups[name]
                        logger.info(f"Đã xóa nhóm '{C.YELLOW}{name}{C.RESET}'.")
                    else:
                        logger.error(f"Không tìm thấy nhóm '{C.YELLOW}{name}{C.RESET}'.")
                
                elif sub_cmd == "add" and len(parts) >= 4:
                    name = parts[2]
                    if name == "all": logger.error("Không thể thêm thành viên vào nhóm 'all'."); continue
                    if name not in manager.groups: logger.error(f"Không tìm thấy nhóm '{C.YELLOW}{name}{C.RESET}'."); continue
                    try:
                        indices_to_add = {int(i) for i in parts[3].split(',')}
                        valid_indices = {i for i in indices_to_add if 0 <= i < len(manager.accounts)}
                        if len(valid_indices) != len(indices_to_add): logger.warning("Một vài chỉ số không hợp lệ đã bị bỏ qua.");
                        current_members = set(manager.groups[name])
                        current_members.update(valid_indices)
                        manager.groups[name] = sorted(list(current_members))
                        logger.info(f"Đã cập nhật nhóm '{C.YELLOW}{name}{C.RESET}': {manager.groups[name]}")
                    except ValueError: logger.error("Chỉ số không hợp lệ.");

                elif sub_cmd == "remove" and len(parts) >= 4:
                    name = parts[2]
                    if name == "all": logger.error("Không thể xóa thành viên khỏi nhóm 'all'."); continue
                    if name not in manager.groups: logger.error(f"Không tìm thấy nhóm '{C.YELLOW}{name}{C.RESET}'."); continue
                    try:
                        indices_to_remove = {int(i) for i in parts[3].split(',')}
                        current_members = set(manager.groups[name])
                        current_members.difference_update(indices_to_remove)
                        manager.groups[name] = sorted(list(current_members))
                        logger.info(f"Đã cập nhật nhóm '{C.YELLOW}{name}{C.RESET}': {manager.groups[name]}")
                    except ValueError: logger.error("Chỉ số không hợp lệ.");

                else:
                    logger.warning("Lệnh group không hợp lệ.")
                continue

            # --- Target Switching ---
            elif cmd_base == "target":
                if len(parts) != 2:
                    logger.warning("Sử dụng: target <index|group_name|all>"); continue
                
                new_target = parts[1]
                if new_target.isdigit():
                    new_target_idx = int(new_target)
                    if 0 <= new_target_idx < len(manager.accounts):
                        manager.command_target = new_target_idx
                        logger.info(f"Đã đặt mục tiêu là tài khoản [{C.YELLOW}{new_target_idx}{C.RESET}].")
                    else:
                        logger.error("Chỉ số tài khoản không hợp lệ.")
                elif new_target in manager.groups:
                    manager.command_target = new_target
                    logger.info(f"Đã đặt mục tiêu là nhóm '{C.YELLOW}{new_target}{C.RESET}'.")
                else:
                    logger.error(f"Không tìm thấy tài khoản hoặc nhóm với tên/chỉ số '{new_target}'.")
                continue

            # --- Command Execution ---
            target_accounts = manager.get_target_accounts()
            if not target_accounts:
                logger.error("Không có mục tiêu hợp lệ nào được chọn hoặc mục tiêu không online. Dùng 'target'.")
                continue
            
            logger.info(f"Đang gửi lệnh '{C.PURPLE}{command}{C.RESET}' đến {len(target_accounts)} tài khoản...")
            all_tasks = [handle_single_command(command, acc) for acc in target_accounts]
            await asyncio.gather(*all_tasks)

        except (EOFError, KeyboardInterrupt):
            logger.info("Đã nhận tín hiệu thoát, đang đóng tất cả kết nối...")
            manager.stop_all()
            break
        except Exception as e:
            logger.error(f"Lỗi trong vòng lặp lệnh chính: {e}")

async def handle_single_command(command: str, account: Account):
    """Processes a command for a single, specified account."""
    parts = command.strip().lower().split()
    cmd_base = parts[0]
    C = TerminalColors
    try:
        if cmd_base == "pet":
            if len(parts) == 1:
                display_pet_help()
            else:
                sub_cmd = parts[1]
                if sub_cmd == "info":
                    await account.service.pet_info()
                    await asyncio.sleep(0.5)
                    # This now needs the specific pet object
                    display_pet_info(account.pet)
                elif sub_cmd in {"follow", "protect", "attack", "home"}:
                    status_map = {"follow": 0, "protect": 1, "attack": 2, "home": 3}
                    await account.service.pet_status(status_map[sub_cmd])
                else:
                    logger.warning(f"[{C.YELLOW}{account.username}{C.RESET}] Lệnh đệ tử không xác định: '{sub_cmd}'.")

        elif cmd_base == "logger":
            if len(parts) > 1 and parts[1] in ["on", "off"]:
                status = parts[1] == "on"
                set_logger_status(status)
                logger.info(f"Đã {'BẬT' if status else 'TẮT'} logger.")
            else:
                logger.warning("Sử dụng: logger <on|off>")

        elif cmd_base == "autoplay":
            if len(parts) > 1 and parts[1] in ["on", "off"]:
                status = parts[1] == "on"
                account.controller.toggle_autoplay(status)
                logger.info(f"[{C.YELLOW}{account.username}{C.RESET}] Đã {'BẬT' if status else 'TẮT'} autoplay.")
            else:
                logger.warning(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: autoplay <on|off>")

        elif cmd_base == "autopet":
            if len(parts) > 1 and parts[1] in ["on", "off"]:
                status = parts[1] == "on"
                account.controller.toggle_auto_pet(status)
                logger.info(f"[{C.YELLOW}{account.username}{C.RESET}] Đã {'BẬT' if status else 'TẮT'} autopet.")
            else:
                logger.warning(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: autopet <on|off>")
        
        elif cmd_base == "show":
            display_character_status(account)

        elif cmd_base == "khu":
            if len(parts) == 2 and parts[1].isdigit():
                await account.service.request_change_zone(int(parts[1]))
            else:
                logger.warning(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: khu <id>")
        
        else:
            logger.warning(f"[{C.YELLOW}{account.username}{C.RESET}] Lệnh không xác định: '{command}'. Gõ 'help'.")

    except Exception as e:
        logger.error(f"Lỗi khi xử lý lệnh '{command}' cho {account.username}: {e}")


async def main():
    # Kích hoạt hỗ trợ màu ANSI trên Windows
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except (ImportError, AttributeError, OSError):
            logger.warning("Không thể kích hoạt hỗ trợ màu ANSI cho Windows.")

    # Check if accounts are configured
    if not Config.ACCOUNTS or not Config.ACCOUNTS[0].get("username") or "your_username" in Config.ACCOUNTS[0].get("username"):
        C = TerminalColors
        logger.error("="*60)
        logger.error(f"{C.BOLD_RED}CHƯA CẤU HÌNH TÀI KHOẢN!{C.RESET}")
        logger.error(f"Vui lòng mở file {C.YELLOW}'config.py'{C.RESET} và điền thông tin tài khoản.")
        logger.error("="*60)
        return

    manager = AccountManager()
    manager.load_accounts()
    await manager.start_all()

    if any(acc.is_logged_in for acc in manager.accounts):
        logger.info("Sẵn sàng nhận lệnh. Gõ 'help' để xem các lệnh có sẵn.")
        display_help()
        await command_loop(manager)
    else:
        logger.error("Không có tài khoản nào đăng nhập thành công. Thoát.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Đang dừng...")