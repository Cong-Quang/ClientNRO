import asyncio
import os
import shutil
from config import Config
from account import Account
from logs.logger_config import logger, set_logger_status, TerminalColors
from ui import display_help, display_pet_info, display_pet_help, display_character_status
from autocomplete import get_input_with_autocomplete, COMMAND_TREE
from combo import ComboEngine
import time

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
                    port=Config.PORT,
                    proxy=acc_data.get("proxy")
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

def load_proxies():
    """Đọc danh sách proxy từ file proxy.txt và chuyển đổi sang định dạng URL chuẩn."""
    proxies = []
    if os.path.exists("proxy.txt"):
        try:
            with open("proxy.txt", "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip()
                    if not p:
                        continue
                    
                    # Xử lý định dạng IP:PORT:USER:PASS
                    parts = p.split(':')
                    if len(parts) == 4:
                        ip, port, user, password = parts
                        # Chuyển đổi sang http://user:pass@ip:port
                        formatted_proxy = f"http://{user}:{password}@{ip}:{port}"
                        proxies.append(formatted_proxy)
                    else:
                        # Giữ nguyên nếu không phải định dạng trên (ví dụ đã là http://...)
                        proxies.append(p)
                        
            logger.info(f"Đã tải {len(proxies)} proxy từ file.")
        except Exception as e:
            logger.error(f"Lỗi khi đọc file proxy.txt: {e}")
    else:
        logger.warning("Không tìm thấy file proxy.txt. Chỉ sử dụng IP máy (Giới hạn 5 acc).")
    return proxies

async def command_loop(manager: AccountManager):
    """The main interactive command loop for managing multiple accounts."""
    C = TerminalColors
    # Tải danh sách proxy khi bắt đầu
    proxy_list = load_proxies()
    combo_engine = ComboEngine()
    combo_queue = []
    combo_running = False
    
    while True:
        # Update autocomplete with current groups
        current_group_names = list(manager.groups.keys())
        # Thêm 'default' vào danh sách gợi ý cho login
        login_suggestions = current_group_names + ["default"]
        COMMAND_TREE["login"] = login_suggestions
        COMMAND_TREE["logout"] = current_group_names
        COMMAND_TREE["target"] = current_group_names
        COMMAND_TREE["combo"] = ["list", "reload"] + combo_engine.list()

        target_str = f"{C.RED}None{C.RESET}"
        if manager.command_target is not None:
            if isinstance(manager.command_target, int):
                target_str = f"Acc {C.YELLOW}{manager.command_target}{C.RESET}"
            else:
                target_str = f"Group '{C.YELLOW}{manager.command_target}{C.RESET}'"
        
        prompt = f"[{target_str}]> "

        try:
            if combo_running:
                if not combo_queue:
                    combo_running = False
                    print("Combo hoàn tất.")
                    continue

                command = combo_queue.pop(0)
                print(f">>> {command}")
            else:
                command = await asyncio.to_thread(get_input_with_autocomplete, prompt)

            command = command.strip().lower()

            parts = command.split()
            if not command:
                continue

            cmd_base = parts[0]
            
            if parts[0] == "sleep":
                try:
                    await asyncio.sleep(float(parts[1]))
                except:
                    print("sleep <seconds>")
                continue


            if cmd_base == "exit":
                manager.stop_all()
                break
            
            elif cmd_base == "combo":
                if len(parts) == 1:
                    print("combo list | combo <name> | combo reload")
                    continue

                sub = parts[1]

                if sub == "list":
                    print("Danh sách combo:")
                    for c in combo_engine.list():
                        print(f"- {c}")
                    continue

                if sub == "reload":
                    combo_engine.load()
                    print("Đã reload combo.txt")
                    continue

                if not combo_engine.exists(sub):
                    print(f"Không có combo '{sub}'")
                    continue

                # Nạp combo vào queue
                combo_queue = combo_engine.get(sub).copy()
                combo_running = True
                print(f"Bắt đầu chạy combo '{sub}'")
                continue


            elif cmd_base in ("cls", "clear"):
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            elif cmd_base == "help":
                display_help()
                continue

            elif cmd_base == "autologin":
                if len(parts) > 1 and parts[1] in ["on", "off"]:
                    status = parts[1] == "on"
                    Config.AUTO_LOGIN = status
                    status_text = f"{C.GREEN}BẬT{C.RESET}" if status else f"{C.RED}TẮT{C.RESET}"
                    print(f"Đã {status_text} tính năng tự động đăng nhập lại.")
                else:
                    current_status = f"{C.GREEN}BẬT{C.RESET}" if Config.AUTO_LOGIN else f"{C.RED}TẮT{C.RESET}"
                    print(f"Tự động đăng nhập lại hiện đang {current_status}. Dùng: autoLogin <on|off>")
                continue
            
            elif cmd_base == "login":
                # login [target]
                target = None
                if len(parts) >= 2:
                    target = parts[1]
                elif manager.command_target is not None:
                     # Use current target
                     if isinstance(manager.command_target, int):
                         target = str(manager.command_target)
                     else:
                         target = manager.command_target
                else:
                    # Mặc định là login default nếu không có tham số và không có target
                    target = "default"
                
                # Logic xử lý danh sách acc cần login
                accounts_to_login = []
                
                if target == "all":
                    accounts_to_login = list(manager.accounts)

                    # Lọc theo blacklist nếu có (áp dụng chỉ cho 'login all')
                    if getattr(Config, 'LOGIN_BLACKLIST', None):
                        skipped = []
                        filtered = []
                        for i, acc in enumerate(accounts_to_login):
                            skip = False
                            for b in Config.LOGIN_BLACKLIST:
                                # Hỗ trợ cả username và index trong blacklist
                                if isinstance(b, int) and b == i:
                                    skip = True
                                    break
                                if isinstance(b, str) and b.lower() == acc.username.lower():
                                    skip = True
                                    break
                            if skip:
                                skipped.append(acc.username)
                            else:
                                filtered.append(acc)
                        accounts_to_login = filtered
                        if skipped:
                            print(f"Bỏ qua (theo blacklist): {', '.join(skipped)}")

                elif target == "default":
                    target_indices = Config.DEFAULT_LOGIN
                    for idx in target_indices:
                        if 0 <= idx < len(manager.accounts):
                            accounts_to_login.append(manager.accounts[idx])

                elif target in manager.groups:
                     # Login theo nhóm
                     indices = manager.groups[target]
                     for idx in indices:
                         if 0 <= idx < len(manager.accounts):
                             accounts_to_login.append(manager.accounts[idx])
                             
                elif ',' in target:
                    try:
                        indices = [int(i.strip()) for i in target.split(',')]
                        for idx in indices:
                            if 0 <= idx < len(manager.accounts):
                                accounts_to_login.append(manager.accounts[idx])
                    except ValueError:
                         print("Danh sách chỉ số không hợp lệ.")
                         continue
                         
                elif target.isdigit():
                    idx = int(target)
                    if 0 <= idx < len(manager.accounts):
                        accounts_to_login.append(manager.accounts[idx])
                    else:
                        print("Chỉ số không hợp lệ.")
                        continue
                else:
                    print(f"Không tìm thấy nhóm hoặc chỉ số '{target}'.")
                    continue

                # Thực hiện login
                if not accounts_to_login:
                    print("Không có tài khoản nào được chọn để đăng nhập.")
                    continue

                current_active_total = manager.get_active_account_count()
                limit = Config.MAX_ACCOUNTS
                available_slots_global = limit - current_active_total
                
                if available_slots_global <= 0:
                    print(f"{C.RED}Đã đạt giới hạn {limit} tài khoản đang chạy.{C.RESET}")
                    continue
                
                # --- PHÂN PHỐI PROXY ---
                # Tính toán usage hiện tại của tất cả các account ĐANG online
                local_ip_usage = 0
                proxy_usage = {p: 0 for p in proxy_list}
                
                for acc in manager.accounts:
                    if acc.is_logged_in:
                        if acc.proxy is None:
                            local_ip_usage += 1
                        elif acc.proxy in proxy_usage:
                            proxy_usage[acc.proxy] += 1
                
                tasks = []
                stop_login_sequence = False

                for acc in accounts_to_login:
                    if stop_login_sequence:
                        break

                    if acc.is_logged_in:
                         print(f"[{C.YELLOW}{acc.username}{C.RESET}] {C.RED}Đã online. Bỏ qua.{C.RESET}")
                         continue
                    
                    if len(tasks) >= available_slots_global:
                        print(f"{C.RED}Đã đạt giới hạn slot login toàn cục ({limit}). Dừng thêm.{C.RESET}")
                        break
                    
                    # Logic gán proxy
                    assigned_proxy = None
                    
                    # 1. Ưu tiên dùng IP máy (max 5)
                    if local_ip_usage < 5:
                        assigned_proxy = None
                        local_ip_usage += 1
                        print(f"[{C.YELLOW}{acc.username}{C.RESET}] {C.GREEN}Gán IP máy{C.RESET} (Slot {C.CYAN}{local_ip_usage}/5{C.RESET})")
                    else:
                        # 2. Tìm proxy còn slot (max 5)
                        found_proxy = False
                        for p in proxy_list:
                            if proxy_usage[p] < 5:
                                assigned_proxy = p
                                proxy_usage[p] += 1
                                found_proxy = True
                                try:
                                    display_p = p.split('@')[-1]
                                except:
                                    display_p = p
                                print(f"[{C.YELLOW}{acc.username}{C.RESET}] {C.PURPLE}Gán Proxy{C.RESET} {C.GREY}...{display_p[-15:]}{C.RESET} (Slot {C.CYAN}{proxy_usage[p]}/5{C.RESET})")
                                break
                        
                        if not found_proxy:
                            print(f"{C.RED}Hết tài nguyên mạng (IP máy & Proxy đều full 5 acc).{C.RESET}")
                            print(f"{C.RED}Dừng đăng nhập từ tài khoản: {acc.username}{C.RESET}")
                            stop_login_sequence = True
                            break # Thoát khỏi vòng lặp accounts_to_login
                    
                    # Cập nhật proxy cho account và login
                    acc.proxy = assigned_proxy
                    # Cần cập nhật lại session proxy vì session được tạo khi init Account
                    if acc.session:
                        acc.session.proxy = assigned_proxy

                    print(f"Đang đăng nhập {C.YELLOW}{acc.username}{C.RESET}...")
                    tasks.append(acc.login())
                
                if tasks:
                    await asyncio.gather(*tasks)
                    print(f"{C.GREEN}Đã hoàn tất quy trình đăng nhập cho {len(tasks)} tài khoản.{C.RESET}")
                else:
                    if not stop_login_sequence:
                        print(f"{C.YELLOW}Không có tác vụ đăng nhập nào được khởi tạo.{C.RESET}")

                continue

            elif cmd_base == "logout":
                # logout <index> hoặc logout all hoặc logout 1,2,3 hoặc logout <group>
                if len(parts) < 2:
                    print("Sử dụng: logout <index|list|all|group_name>")
                    continue
                
                target = parts[1]
                accounts_to_logout = []

                if target == "all":
                    accounts_to_logout = manager.accounts
                
                elif target in manager.groups:
                    indices = manager.groups[target]
                    for idx in indices:
                         if 0 <= idx < len(manager.accounts):
                             accounts_to_logout.append(manager.accounts[idx])
                
                elif ',' in target:
                    try:
                        indices = [int(i.strip()) for i in target.split(',')]
                        for idx in indices:
                            if 0 <= idx < len(manager.accounts):
                                accounts_to_logout.append(manager.accounts[idx])
                    except ValueError:
                         print("Danh sách chỉ số không hợp lệ.")
                         continue
                
                elif target.isdigit():
                    idx = int(target)
                    if 0 <= idx < len(manager.accounts):
                        accounts_to_logout.append(manager.accounts[idx])
                    else:
                         print("Chỉ số tài khoản không hợp lệ.")
                         continue
                else:
                    print(f"Không tìm thấy nhóm hoặc chỉ số '{target}'.")
                    continue
                
                # Thực hiện logout
                count = 0
                for acc in accounts_to_logout:
                    if acc.is_logged_in:
                        print(f"Đang đăng xuất {acc.username}...")
                        acc.stop()
                        count += 1
                
                if count > 0:
                    print(f"Đã đăng xuất {count} tài khoản.")
                else:
                    print("Không có tài khoản nào đang online trong danh sách chọn.")
                continue

            elif cmd_base == "proxy":
                if len(parts) > 1 and parts[1] == "list":
                    print(f"{C.CYAN}--- Danh sách Proxy ---{C.RESET}")
                    
                    # Tính toán usage
                    usage_map = {p: 0 for p in proxy_list}
                    local_usage = 0
                    
                    for acc in manager.accounts:
                        if acc.is_logged_in:
                            if acc.proxy:
                                if acc.proxy in usage_map:
                                    usage_map[acc.proxy] += 1
                            else:
                                local_usage += 1
                    
                    # Hiển thị Local IP
                    local_color = C.GREEN if local_usage > 0 else C.GREY
                    print(f"[Local] {local_color}{'IP Máy':<30} - Đang dùng: {local_usage}/5{C.RESET}")

                    # Hiển thị Proxy List
                    if not proxy_list:
                        print("  (Không có proxy nào được tải)")
                    
                    for i, p in enumerate(proxy_list):
                        count = usage_map.get(p, 0)
                        # Lấy phần IP:Port để hiển thị cho đẹp
                        try:
                            display_p = p.split('@')[-1]
                        except:
                            display_p = p
                        
                        if count > 0:
                            color = C.GREEN
                            status = f"Đang dùng: {count}/5"
                        else:
                            color = C.GREY
                            status = "Chưa dùng"
                        
                        print(f"[{i+1}]     {color}{display_p:<30} - {status}{C.RESET}")
                else:
                    print("Sử dụng: proxy list")
                continue

            elif cmd_base == "list":
                print(f"{C.CYAN}--- Danh sách tài khoản ---{C.RESET}")
                for i, acc in enumerate(manager.accounts):
                    status_text = acc.status
                    if acc.status == "Logged In":
                        status_color = C.GREEN
                    elif acc.status == "Reconnecting":
                        status_color = C.YELLOW
                    else:
                        status_color = C.RED
                    
                    status = f"{status_color}{status_text}{C.RESET}"

                    target_marker = ""
                    if isinstance(manager.command_target, int) and i == manager.command_target:
                        target_marker = f"{C.PURPLE}(*){C.RESET}"
                    
                    # Hiển thị thông tin proxy ngắn gọn
                    proxy_info = "Local"
                    if acc.proxy:
                        # Chỉ hiển thị IP cuối cho gọn
                        try:
                             # format http://user:pass@ip:port
                             ip_part = acc.proxy.split('@')[-1]
                             proxy_info = f"Proxy({ip_part})"
                        except:
                             proxy_info = "Proxy"

                    print(f"[{C.YELLOW}{i}{C.RESET}] {acc.username:<15} {status:<20} [{C.CYAN}{proxy_info}{C.RESET}] {target_marker}")
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

            # --- Pre-validation for Targetted Commands ---
            # Define commands that are valid to be sent to accounts.
            # If the command is not in this list, it's an unknown command for a single account.
            valid_target_commands = [
                "pet", "logger", "autoplay", "autopet", "blacklist", "gomap", 
                "findnpc", "teleport", "teleportnpc", "andau", "hit", "show", 
                "csgoc", "opennpc", "khu", "congcs"
            ]
            if cmd_base not in valid_target_commands:
                print(f"{C.RED}Lệnh không xác định: '{command}'. Gõ 'help'.{C.RESET}")
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
            
            # Xác định chế độ hiển thị gọn (compact) nếu gửi cho nhiều hơn 1 tài khoản
            is_compact = len(online_targets) > 1
            if is_compact and "pet info" in command:
                 # Gọn hơn: Username | Id | Tên Đệ | Trạng thái | HP | MP | SM | SĐ
                 print(f"{C.CYAN}{'Tài khoản':<15} {'ID':<4} {'Tên Đệ':<12} | {'TT':<6} | {'HP':>7} | {'MP':>7} | {'SM':>7} | {'SĐ':>7}{C.RESET}")
            elif is_compact and "csgoc" in command:
                # Header for base stats compact view
                print(f"{C.CYAN}{'Tài khoản':<19} | {'HP Gốc':>8} | {'MP Gốc':>7} | {'SĐ Gốc':>7} | {'Giáp Gốc':>7} | {'CM Gốc':>5} | {'Tiềm năng':>7}{C.RESET}")
            elif is_compact and command.strip() == "show":
                 # Header matching ui.py columns (right-aligned numbers)
                 print(f"{C.CYAN}{'Tài khoản':<19} | {'Bản đồ':<18} | {'ID':<3} | {'Khu':<3} | {'Tọa độ':<8} | {'HP':>8} | {'MP':>7} | {'SM':>7} | {'SĐ':>7} | {'Chức năng':<14}{C.RESET}")

            tasks = [handle_single_command(command, acc, compact_mode=is_compact, idx=i) for i, acc in enumerate(online_targets)]
            results = await asyncio.gather(*tasks)

            
            # Print per-account delivery status
            # Nếu là lệnh hiển thị thông tin (như pet info compact), ta không cần in trạng thái "Đã nhận" nữa vì nó sẽ làm rối
            # if not (is_compact and ("pet info" in command or command.strip() == "show" or "csgoc" in command)):
            #     for acc, (success, msg) in zip(online_targets, results):
            #         if success:
            #             print(f"[{C.YELLOW}{acc.username}{C.RESET}] {C.GREEN}Đã nhận{C.RESET}")
            #         else:
            #             print(f"[{C.YELLOW}{acc.username}{C.RESET}] {C.RED}Không nhận{C.RESET} - {msg}")


        except (EOFError, KeyboardInterrupt):
            logger.info("Đã nhận tín hiệu thoát, đang đóng tất cả kết nối...")
            manager.stop_all()
            break
        except Exception as e:
            logger.error(f"Lỗi trong vòng lặp lệnh chính: {e}")

async def handle_single_command(command: str, account: Account, compact_mode: bool = False, idx: int = None):
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
                    # This now needs the specific pet object and username (and optional idx for compact view)
                    display_pet_info(account.pet, account.username, compact=compact_mode, idx=idx)
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

        elif cmd_base == "blacklist":
                # Commands: blacklist list | add <name|id> | remove <name|id> | clear
                if len(parts) == 1:
                    print("Sử dụng: blacklist <list|add|remove|clear>")
                else:
                    sub = parts[1]
                    if sub == "list":
                        print(f"Blacklist: {Config.LOGIN_BLACKLIST}")
                    elif sub == "add" and len(parts) == 3:
                        val = parts[2]
                        try:
                            v = int(val)
                        except ValueError:
                            v = val
                        if v in Config.LOGIN_BLACKLIST:
                            print(f"Đã có trong blacklist: {v}")
                        else:
                            Config.LOGIN_BLACKLIST.append(v)
                            print(f"Đã thêm vào blacklist: {v}")
                    elif sub == "remove" and len(parts) == 3:
                        val = parts[2]
                        try:
                            v = int(val)
                        except ValueError:
                            v = val
                        if v in Config.LOGIN_BLACKLIST:
                            Config.LOGIN_BLACKLIST.remove(v)
                            print(f"Đã xóa khỏi blacklist: {v}")
                        else:
                            print(f"Không có trong blacklist: {v}")
                    elif sub == "clear":
                        Config.LOGIN_BLACKLIST.clear()
                        print("Đã xóa toàn bộ blacklist.")
                    else:
                        print("Sử dụng: blacklist <list|add|remove|clear>")

        elif cmd_base == "gomap":
            if len(parts) > 1:
                if parts[1] == "stop":
                    account.controller.xmap.finish()
                    print(f"[{C.YELLOW}{account.username}{C.RESET}] Đã dừng XMap.")
                elif parts[1] == "home":
                    print(f"[{C.YELLOW}{account.username}{C.RESET}] Đang về nhà...")
                    await account.controller.xmap.go_home()
                else:
                    try:
                        map_id = int(parts[1])
                        print(f"[{C.YELLOW}{account.username}{C.RESET}] Bắt đầu XMap tới {map_id}...")
                        await account.controller.xmap.start(map_id)
                    except ValueError:
                        print(f"[{C.YELLOW}{account.username}{C.RESET}] Map ID không hợp lệ: {parts[1]}")
            else:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: gomap <map_id> | gomap home | gomap stop")
        
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

        elif cmd_base == "andau":
            await account.controller.eat_pea()
        
        elif cmd_base == "hit":
            await account.controller.attack_nearest_mob()

        elif cmd_base == "show":
            # Gửi yêu cầu cập nhật thông tin mới nhất từ server trước khi hiển thị
            await account.service.request_me_info()
            # Chờ một chút để server phản hồi
            await asyncio.sleep(0.2) 
            
            if len(parts) > 1 and parts[1] == "csgoc":
                from ui import display_character_base_stats
                display_character_base_stats(account, compact=compact_mode, idx=idx)
            else:
                display_character_status(account, compact=compact_mode, idx=idx)
        
        elif cmd_base == "csgoc":
             # Alias ngắn gọn
             await account.service.request_me_info()
             await asyncio.sleep(0.2)
             from ui import display_character_base_stats
             display_character_base_stats(account, compact=compact_mode, idx=idx)

        elif cmd_base == "opennpc":
            # opennpc <npc_id> [index1] [index2] ...
            if len(parts) >= 2:
                try:
                    npc_id = int(parts[1])
                    menu_indices = [int(x) for x in parts[2:]]
                    
                    print(f"[{C.YELLOW}{account.username}{C.RESET}] Mở NPC {npc_id}...")
                    await account.service.open_menu_npc(npc_id)
                    
                    if menu_indices:
                        for menu_index in menu_indices:
                            #print(f"[{C.YELLOW}{account.username}{C.RESET}] -> Chọn menu {idx}...")
                            await asyncio.sleep(0.01) # Delay nhỏ giữa các lần chọn để server xử lý
                            await account.service.confirm_menu_npc(npc_id, menu_index)
                        print(f"[{C.YELLOW}{account.username}{C.RESET}] {C.GREEN}Done.{C.RESET}")
                            
                except ValueError:
                    print(f"[{C.YELLOW}{account.username}{C.RESET}] Tham số không hợp lệ. ID và Index phải là số.")
            else:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: opennpc <npc_id> [index1] [index2] ...")

        elif cmd_base == "khu":
            if len(parts) > 1 and parts[1].isdigit():
                zone_id = int(parts[1])
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Đang chuyển sang khu {C.CYAN}{zone_id}{C.RESET}...")
                # Gọi hàm gửi packet đổi khu (tên hàm có thể là request_change_zone hoặc change_zone tùy source của bạn)
                await account.service.request_change_zone(zone_id)
            else:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: khu <số khu>")    

        elif cmd_base == "congcs":
            # congcs <hp> <mp> <sd>
            if len(parts) == 4 and all(p.isdigit() for p in parts[1:]):
                t_hp = int(parts[1])
                t_mp = int(parts[2])
                t_sd = int(parts[3])
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Bắt đầu cộng chỉ số tới: HP={t_hp}, MP={t_mp}, SD={t_sd}")
                asyncio.create_task(account.controller.auto_upgrade_stats(t_hp, t_mp, t_sd))
            else:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: congcs <hp_goc> <mp_goc> <sd_goc>")
                
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