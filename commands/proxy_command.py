from commands.base_command import Command
from logs.logger_config import TerminalColors
from ui import Box
from typing import Any

class ProxyCommand(Command):
    def __init__(self, manager, proxy_list):
        self.manager = manager
        self.proxy_list = proxy_list
        self.C = TerminalColors
        self.B = Box

    async def execute(self, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) > 1 and parts[1] == "list":
            self._list_proxies()
        else:
            print(f"{self.C.YELLOW}Sử dụng: proxy list{self.C.RESET}")
        return False

    def _list_proxies(self):
        print()
        print(f"{self.C.PURPLE}{self.B.TL}{self.B.H * 55}{self.B.TR}{self.C.RESET}")
        print(f"{self.C.PURPLE}{self.B.V}{self.C.RESET} {self.C.BOLD}{'#':<6} {'Địa chỉ':<30} {'Sử dụng':>10}{self.C.RESET} {self.C.PURPLE}{self.B.V}{self.C.RESET}")
        print(f"{self.C.PURPLE}{self.B.LT}{self.B.H * 55}{self.B.RT}{self.C.RESET}")
        
        # Calculate usage
        usage_map = {p: 0 for p in self.proxy_list}
        local_usage = 0
        
        for acc in self.manager.accounts:
            if acc.is_logged_in:
                if acc.proxy:
                    if acc.proxy in usage_map:
                        usage_map[acc.proxy] += 1
                else:
                    local_usage += 1
        
        # Local IP row
        usage_bar = f"{'#' * local_usage}{'-' * (5 - local_usage)}"
        local_col = self.C.BRIGHT_GREEN if local_usage > 0 else self.C.DIM
        print(f"{self.C.PURPLE}{self.B.V}{self.C.RESET} {self.C.CYAN}Local{self.C.RESET}  {local_col}{'IP Máy':<30}{self.C.RESET} {local_col}{usage_bar} {local_usage}/5{self.C.RESET} {self.C.PURPLE}{self.B.V}{self.C.RESET}")

        # Proxy list
        if not self.proxy_list:
            print(f"{self.C.PURPLE}{self.B.V}{self.C.RESET} {self.C.DIM}(Không có proxy nào được tải){self.C.RESET}")
        
        for i, p in enumerate(self.proxy_list):
            count = usage_map.get(p, 0)
            try:
                display_p = p.split('@')[-1]
            except:
                display_p = p
            if len(display_p) > 28:
                display_p = "..." + display_p[-25:]
            
            usage_bar = f"{'#' * count}{'-' * (4 - count)}"
            col = self.C.BRIGHT_GREEN if count > 0 else self.C.DIM
            print(f"{self.C.PURPLE}{self.B.V}{self.C.RESET} {self.C.YELLOW}[{i+1:>2}]{self.C.RESET}   {col}{display_p:<30}{self.C.RESET} {col}{usage_bar} {count}/4{self.C.RESET} {self.C.PURPLE}{self.B.V}{self.C.RESET}")
        
        print(f"{self.C.PURPLE}{self.B.BL}{self.B.H * 55}{self.B.BR}{self.C.RESET}")
        print()
