from commands.base_command import Command
from logs.logger_config import TerminalColors
from config import Config
from typing import Any
import asyncio

class LoginCommand(Command):
    def __init__(self, manager, proxy_list):
        self.manager = manager
        self.proxy_list = proxy_list
        self.C = TerminalColors

    async def execute(self, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        # login [target]
        target = None
        if len(parts) >= 2:
            target = parts[1]
        elif self.manager.command_target is not None:
                # Use current target
                if isinstance(self.manager.command_target, int):
                    target = str(self.manager.command_target)
                else:
                    target = self.manager.command_target
        else:
            # Mặc định là login default nếu không có tham số và không có target
            target = "default"
        
        # Logic xử lý danh sách acc cần login
        accounts_to_login = []
        
        if target == "all":
            accounts_to_login = list(self.manager.accounts)

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
                if 0 <= idx < len(self.manager.accounts):
                    accounts_to_login.append(self.manager.accounts[idx])

        elif target in self.manager.groups:
                # Login theo nhóm
                indices = self.manager.groups[target]
                for idx in indices:
                    if 0 <= idx < len(self.manager.accounts):
                        accounts_to_login.append(self.manager.accounts[idx])
                        
        elif ',' in target:
            try:
                indices = [int(i.strip()) for i in target.split(',')]
                for idx in indices:
                    if 0 <= idx < len(self.manager.accounts):
                        accounts_to_login.append(self.manager.accounts[idx])
            except ValueError:
                    print("Danh sách chỉ số không hợp lệ.")
                    return False
                    
        elif target.isdigit():
            idx = int(target)
            if 0 <= idx < len(self.manager.accounts):
                accounts_to_login.append(self.manager.accounts[idx])
            else:
                print("Chỉ số không hợp lệ.")
                return False
        else:
            print(f"Không tìm thấy nhóm hoặc chỉ số '{target}'.")
            return False

        # Thực hiện login
        if not accounts_to_login:
            print("Không có tài khoản nào được chọn để đăng nhập.")
            return False

        current_active_total = self.manager.get_active_account_count()
        limit = Config.MAX_ACCOUNTS
        available_slots_global = limit - current_active_total
        
        if available_slots_global <= 0:
            print(f"{self.C.RED}Đã đạt giới hạn {limit} tài khoản đang chạy.{self.C.RESET}")
            return False
        
        # --- PHÂN PHỐI PROXY ---
        # Tính toán usage hiện tại của tất cả các account ĐANG online
        local_ip_usage = 0
        proxy_usage = {p: 0 for p in self.proxy_list}
        
        for acc in self.manager.accounts:
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
                    print(f"[{self.C.YELLOW}{acc.username}{self.C.RESET}] {self.C.RED}Đã online. Bỏ qua.{self.C.RESET}")
                    continue
            
            if len(tasks) >= available_slots_global:
                print(f"{self.C.RED}Đã đạt giới hạn slot login toàn cục ({limit}). Dừng thêm.{self.C.RESET}")
                break
            
            # Logic gán proxy
            assigned_proxy = None

            if Config.USE_LOCAL_IP_FIRST:
                # Chế độ cũ: Ưu tiên IP máy
                if local_ip_usage < 5:
                    assigned_proxy = None
                    local_ip_usage += 1
                    print(f"[{self.C.YELLOW}{acc.username}{self.C.RESET}] {self.C.GREEN}Gán IP máy{self.C.RESET} (Slot {self.C.CYAN}{local_ip_usage}/5{self.C.RESET})")
                else:
                    # Tìm proxy còn slot
                    found_proxy = False
                    for p in self.proxy_list:
                        if proxy_usage[p] < 4:
                            assigned_proxy = p
                            proxy_usage[p] += 1
                            found_proxy = True
                            try:
                                display_p = p.split('@')[-1]
                            except:
                                display_p = p
                            print(f"[{self.C.YELLOW}{acc.username}{self.C.RESET}] {self.C.PURPLE}Gán Proxy{self.C.RESET} {self.C.GREY}...{display_p[-15:]}{self.C.RESET} (Slot {self.C.CYAN}{proxy_usage[p]}/4{self.C.RESET})")
                            break
                    if not found_proxy:
                        print(f"{self.C.RED}Hết tài nguyên mạng (IP máy & Proxy đều full 4 acc).{self.C.RESET}")
                        stop_login_sequence = True
            else:
                # Chế độ mới: Chỉ dùng proxy
                found_proxy = False
                if not self.proxy_list:
                    print(f"{self.C.RED}Không có proxy nào trong danh sách để gán.{self.C.RESET}")
                    stop_login_sequence = True
                else:
                    for p in self.proxy_list:
                        if proxy_usage[p] < 4:
                            assigned_proxy = p
                            proxy_usage[p] += 1
                            found_proxy = True
                            try:
                                display_p = p.split('@')[-1]
                            except:
                                display_p = p
                            print(f"[{self.C.YELLOW}{acc.username}{self.C.RESET}] {self.C.PURPLE}Gán Proxy (Bỏ qua IP Local){self.C.RESET} {self.C.GREY}...{display_p[-15:]}{self.C.RESET} (Slot {self.C.CYAN}{proxy_usage[p]}/4{self.C.RESET})")
                            break
                if not found_proxy and self.proxy_list:
                    print(f"{self.C.RED}Tất cả các proxy đều đã full (4 acc/proxy).{self.C.RESET}")
                    stop_login_sequence = True

            if stop_login_sequence:
                print(f"{self.C.RED}Dừng đăng nhập từ tài khoản: {acc.username}{self.C.RESET}")
                break # Thoát khỏi vòng lặp accounts_to_login

            # Cập nhật proxy cho account và login
            acc.proxy = assigned_proxy
            # Cần cập nhật lại session proxy vì session được tạo khi init Account
            if acc.session:
                acc.session.proxy = assigned_proxy

            print(f"Đang đăng nhập {self.C.YELLOW}{acc.username}{self.C.RESET}...")
            tasks.append(acc.login())
        
        if tasks:
            await asyncio.gather(*tasks)
            print(f"{self.C.GREEN}Đã hoàn tất quy trình đăng nhập cho {len(tasks)} tài khoản.{self.C.RESET}")
        else:
            if not stop_login_sequence:
                print(f"{self.C.YELLOW}Không có tác vụ đăng nhập nào được khởi tạo.{self.C.RESET}")

        return False