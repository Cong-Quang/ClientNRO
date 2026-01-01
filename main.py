import asyncio
import os
import shutil
from config import Config
from account import Account
from logs.logger_config import logger, set_logger_status, TerminalColors
from ui import display_help, display_pet_info, display_pet_help, display_character_status
from autocomplete import get_input_with_autocomplete

def clean_pycache():
    """Tìm và xóa tất cả thư mục __pycache__ trong thư mục hiện tại và thư mục con."""
    root_dir = os.getcwd()
    logger.info("Đang dọn dẹp các file rác (__pycache__)...")
    deleted_count = 0
    
    for root, dirs, files in os.walk(root_dir):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_path)
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Không thể xóa {pycache_path}: {e}")
    
    if deleted_count > 0:
        logger.info(f"Đã xóa {deleted_count} thư mục __pycache__.")
    else:
        logger.info("Không tìm thấy thư mục __pycache__ nào.")

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
            
            elif cmd_base == "login":
                # login <index> hoặc login all
                if len(parts) < 2:
                    print("Sử dụng: login <index|all>")
                    continue
                
                target = parts[1]
                if target == "all":
                    current_active = manager.get_active_account_count()
                    limit = Config.MAX_ACCOUNTS
                    available_slots = limit - current_active
                    
                    if available_slots <= 0:
                        print(f"{C.RED}Đã đạt giới hạn {limit} tài khoản đang chạy.{C.RESET}")
                        continue
                    
                    tasks = []
                    # 1. Ưu tiên login các acc trong DEFAULT_LOGIN trước
                    target_indices = Config.DEFAULT_LOGIN
                    # 2. Nếu vẫn còn trống chỗ, có thể lấy thêm các acc khác (tùy chọn)
                    # Ở đây ta chỉ lấy đúng các acc trong DEFAULT_LOGIN để đảm bảo tính tùy chỉnh của bạn
                    
                    for idx in target_indices:
                        if 0 <= idx < len(manager.accounts):
                            acc = manager.accounts[idx]
                            if not acc.is_logged_in and len(tasks) < available_slots:
                                print(f"Đang đăng nhập {acc.username}...")
                                tasks.append(acc.login())
                    
                    if tasks:
                        await asyncio.gather(*tasks)
                        print(f"Đã thực hiện đăng nhập {len(tasks)} tài khoản từ danh sách mặc định.")
                    else:
                        print("Tất cả tài khoản trong danh sách mặc định đã online hoặc đã đạt giới hạn.")

                elif ',' in target:
                    # Handle multiple indices: login 1,2,3
                    try:
                        indices = [int(i.strip()) for i in target.split(',')]
                        tasks = []
                        current_active = manager.get_active_account_count()
                        limit = Config.MAX_ACCOUNTS
                        
                        for idx in indices:
                            if 0 <= idx < len(manager.accounts):
                                acc = manager.accounts[idx]
                                if acc.is_logged_in:
                                    print(f"Tài khoản {acc.username} đã online. Bỏ qua.")
                                    continue
                                
                                if current_active >= limit:
                                    print(f"{C.RED}Đã đạt giới hạn {limit} tài khoản đang chạy. Bỏ qua {acc.username}.{C.RESET}")
                                    continue

                                print(f"Đang đăng nhập {acc.username}...")
                                tasks.append(acc.login())
                                current_active += 1
                            else:
                                print(f"Chỉ số {idx} không hợp lệ. Bỏ qua.")

                        if tasks:
                            await asyncio.gather(*tasks)
                            print(f"Đã thực hiện đăng nhập {len(tasks)} tài khoản.")
                    except ValueError:
                         print("Danh sách chỉ số không hợp lệ. Sử dụng định dạng: login 1,2,3")

                elif target.isdigit():
                    idx = int(target)
                    if 0 <= idx < len(manager.accounts):
                        acc = manager.accounts[idx]
                        if manager.get_active_account_count() >= Config.MAX_ACCOUNTS and not acc.is_logged_in:
                             print(f"{C.RED}Đã đạt giới hạn {Config.MAX_ACCOUNTS} tài khoản.{C.RESET}")
                        else:
                            if not acc.is_logged_in:
                                print(f"Đang đăng nhập {acc.username}...")
                                await acc.login()
                            else:
                                print(f"Tài khoản {acc.username} đã online.")
                    else:
                         print("Chỉ số tài khoản không hợp lệ.")
                continue

            elif cmd_base == "logout":
                # logout <index> hoặc logout all hoặc logout 1,2,3
                if len(parts) < 2:
                    print("Sử dụng: logout <index|list|all>")
                    continue
                
                target = parts[1]
                if target == "all":
                    count = 0
                    for acc in manager.accounts:
                        if acc.is_logged_in:
                            print(f"Đang đăng xuất {acc.username}...")
                            acc.stop()
                            count += 1
                    if count > 0:
                        print(f"Đã đăng xuất {count} tài khoản.")
                    else:
                        print("Không có tài khoản nào đang online.")

                elif ',' in target:
                    try:
                        indices = [int(i.strip()) for i in target.split(',')]
                        count = 0
                        for idx in indices:
                            if 0 <= idx < len(manager.accounts):
                                acc = manager.accounts[idx]
                                if acc.is_logged_in:
                                    print(f"Đang đăng xuất {acc.username}...")
                                    acc.stop()
                                    count += 1
                                else:
                                    print(f"Tài khoản {acc.username} đã offline. Bỏ qua.")
                            else:
                                print(f"Chỉ số {idx} không hợp lệ. Bỏ qua.")
                        if count > 0:
                            print(f"Đã đăng xuất {count} tài khoản.")
                    except ValueError:
                         print("Danh sách chỉ số không hợp lệ. Sử dụng định dạng: logout 1,2,3")

                elif target.isdigit():
                    idx = int(target)
                    if 0 <= idx < len(manager.accounts):
                        acc = manager.accounts[idx]
                        if acc.is_logged_in:
                            print(f"Đang đăng xuất {acc.username}...")
                            acc.stop()
                            print(f"Đã đăng xuất {acc.username}.")
                        else:
                            print(f"Tài khoản {acc.username} đã offline.")
                    else:
                         print("Chỉ số tài khoản không hợp lệ.")
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
                    print("Lệnh group không hợp lệ. Dùng 'group list', 'group create <name> <ids>', 'group delete <name>', ...")
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
                        print("Không thể tạo nhóm với tên 'all'.")
                        continue
                    try:
                        indices = [int(i) for i in parts[3].split(',')]
                        if all(0 <= i < len(manager.accounts) for i in indices):
                            manager.groups[name] = sorted(list(set(indices)))
                            print(f"Đã tạo nhóm '{C.YELLOW}{name}{C.RESET}' với các thành viên: {manager.groups[name]}")
                        else:
                            print("Một hoặc nhiều chỉ số không hợp lệ.")
                    except ValueError:
                        print("Chỉ số thành viên không hợp lệ. Phải là các số được phân tách bằng dấu phẩy (VD: 1,2,3).")

                elif sub_cmd == "delete" and len(parts) == 3:
                    name = parts[2]
                    if name == "all":
                        print("Không thể xóa nhóm 'all'.")
                    elif name in manager.groups:
                        del manager.groups[name]
                        print(f"Đã xóa nhóm '{C.YELLOW}{name}{C.RESET}'.")
                    else:
                        print(f"Không tìm thấy nhóm '{C.YELLOW}{name}{C.RESET}'.")
                
                elif sub_cmd == "add" and len(parts) >= 4:
                    name = parts[2]
                    if name == "all": print("Không thể thêm thành viên vào nhóm 'all'."); continue
                    if name not in manager.groups: print(f"Không tìm thấy nhóm '{C.YELLOW}{name}{C.RESET}'."); continue
                    try:
                        indices_to_add = {int(i) for i in parts[3].split(',')}
                        valid_indices = {i for i in indices_to_add if 0 <= i < len(manager.accounts)}
                        if len(valid_indices) != len(indices_to_add): print("Một vài chỉ số không hợp lệ đã bị bỏ qua.");
                        current_members = set(manager.groups[name])
                        current_members.update(valid_indices)
                        manager.groups[name] = sorted(list(current_members))
                        print(f"Đã cập nhật nhóm '{C.YELLOW}{name}{C.RESET}': {manager.groups[name]}")
                    except ValueError: print("Chỉ số không hợp lệ.");

                elif sub_cmd == "remove" and len(parts) >= 4:
                    name = parts[2]
                    if name == "all": print("Không thể xóa thành viên khỏi nhóm 'all'."); continue
                    if name not in manager.groups: print(f"Không tìm thấy nhóm '{C.YELLOW}{name}{C.RESET}'."); continue
                    try:
                        indices_to_remove = {int(i) for i in parts[3].split(',')}
                        current_members = set(manager.groups[name])
                        current_members.difference_update(indices_to_remove)
                        manager.groups[name] = sorted(list(current_members))
                        print(f"Đã cập nhật nhóm '{C.YELLOW}{name}{C.RESET}': {manager.groups[name]}")
                    except ValueError: print("Chỉ số không hợp lệ.");

                else:
                    print("Lệnh group không hợp lệ.")
                continue

            # --- Target Switching ---
            elif cmd_base == "target":
                if len(parts) != 2:
                    print("Sử dụng: target <index|group_name|all>"); continue
                
                new_target = parts[1]
                if new_target.isdigit():
                    new_target_idx = int(new_target)
                    if 0 <= new_target_idx < len(manager.accounts):
                        manager.command_target = new_target_idx
                        print(f"Đã đặt mục tiêu là tài khoản [{C.YELLOW}{new_target_idx}{C.RESET}].")
                    else:
                        print("Chỉ số tài khoản không hợp lệ.")
                elif new_target in manager.groups:
                    manager.command_target = new_target
                    print(f"Đã đặt mục tiêu là nhóm '{C.YELLOW}{new_target}{C.RESET}'.")
                else:
                    print(f"Không tìm thấy tài khoản hoặc nhóm với tên/chỉ số '{new_target}'.")
                continue

            # --- Command Execution ---
            target_accounts = manager.get_target_accounts()
            # Lọc chỉ gửi lệnh cho acc online, trừ lệnh 'login' (nhưng login đã xử lý riêng ở trên)
            online_targets = [acc for acc in target_accounts if acc.is_logged_in]
            
            if not online_targets:
                print("Không có mục tiêu nào đang online để thực hiện lệnh.")
                continue
            
            # Build a readable recipient list (index and username, show offline if any)
            recipients = []
            for i, acc in enumerate(online_targets):
                recipients.append(f"[{C.YELLOW}{acc.username}{C.RESET}]")
            print(f"Đang gửi lệnh '{C.PURPLE}{command}{C.RESET}' đến {len(online_targets)} tài khoản: {', '.join(recipients)}")
            
            tasks = [handle_single_command(command, acc) for acc in online_targets]
            results = await asyncio.gather(*tasks)
            # Print per-account delivery status
            for acc, (success, msg) in zip(online_targets, results):
                if success:
                    print(f"[{C.YELLOW}{acc.username}{C.RESET}] {C.GREEN}Đã nhận{C.RESET}")
                else:
                    print(f"[{C.YELLOW}{acc.username}{C.RESET}] {C.RED}Không nhận{C.RESET} - {msg}")


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
                    print(f"[{C.YELLOW}{account.username}{C.RESET}] Lệnh đệ tử không xác định: '{sub_cmd}'.")

        elif cmd_base == "logger":
            if len(parts) > 1 and parts[1] in ["on", "off"]:
                status = parts[1] == "on"
                set_logger_status(status)
                print(f"Đã {'BẬT' if status else 'TẮT'} logger.")
            else:
                print("Sử dụng: logger <on|off>")

        elif cmd_base == "autoplay":
            if len(parts) > 1 and parts[1] in ["on", "off"]:
                status = parts[1] == "on"
                account.controller.toggle_autoplay(status)
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Đã {'BẬT' if status else 'TẮT'} autoplay.")
            else:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: autoplay <on|off>")

        elif cmd_base == "autopet":
            if len(parts) > 1 and parts[1] in ["on", "off"]:
                status = parts[1] == "on"
                account.controller.toggle_auto_pet(status)
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Đã {'BẬT' if status else 'TẮT'} autopet.")
            else:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: autopet <on|off>")
        
        elif cmd_base == "show":
            display_character_status(account)

        elif cmd_base == "khu":
            if len(parts) == 2 and parts[1].isdigit():
                await account.service.request_change_zone(int(parts[1]))
            else:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: khu <id>")

        elif cmd_base == "gomap":
            # gomap <map_id>  : Bắt đầu XMap
            # gomap stop      : Dừng XMap hiện tại
            if len(parts) == 2 and parts[1].isdigit():
                map_id = int(parts[1])
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Bắt đầu XMap tới {map_id}...")
                await account.controller.xmap.start(map_id)
            elif len(parts) == 2 and parts[1] == "stop":
                account.controller.xmap.finish()
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Đã dừng XMap.")
            else:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: gomap <map_id> | gomap stop")
        
        elif cmd_base == "findnpc":
            npcs = account.controller.npcs
            if not npcs:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Không tìm thấy NPC nào trên bản đồ hiện tại.")
            else:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Các NPC trên bản đồ:")
                for npc_id, npc_data in npcs.items():
                    # thêm màu sắc cho npc id map
                    template_id = npc_data.get('template_id', 'N/A')
                    raw_name = npc_data.get('name')
                    if raw_name:
                        name = f"{raw_name} ({template_id})"
                    else:
                        name = f"NPC {template_id}"
                    x = npc_data.get('x', 'N/A')
                    y = npc_data.get('y', 'N/A')
                    print(f" - ID: {C.CYAN}{npc_id + 1}{C.RESET}, Tên: {C.GREEN}{name}{C.RESET}, Vị trí: ({x}, {y})")

        elif cmd_base == "teleport":
            if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
                x, y = int(parts[1]), int(parts[2])
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Dịch chuyển tới ({x}, {y})...")
                await account.controller.movement.teleport_to(x, y)
            else:
               print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: teleport <x> <y>")

        elif cmd_base == "teleportnpc":
            if len(parts) == 2 and parts[1].isdigit():
                npc_id = int(parts[1])
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Dịch chuyển tới NPC ID {npc_id}...")
                await account.controller.movement.teleport_to_npc(npc_id)
            else:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: teleportnpc <id>")

        
        else:
            print(f"[{C.YELLOW}{account.username}{C.RESET}] Lệnh không xác định: '{command}'. Gõ 'help'.")
        return True, "OK"
    except Exception as e:
        print(f"Lỗi khi xử lý lệnh '{command}' cho {account.username}: {e}")
        return False, str(e)


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
    # Không tự động login nữa
    # await manager.start_all()

    logger.info("Sẵn sàng nhận lệnh. Gõ 'login' để đăng nhập, gõ 'help' để xem trợ giúp.")
    display_help()
    await command_loop(manager)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Đang dừng...")
    finally:
        clean_pycache()