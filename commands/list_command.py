from commands.base_command import Command
from ui import Box, TerminalColors

class ListCommand(Command):
    def __init__(self, manager):
        self.manager = manager
        self.C = TerminalColors
        self.B = Box

    async def execute(self, *args, **kwargs):
        print()
        print(f"{self.C.CYAN}{self.B.TL}{self.B.H * 70}{self.B.TR}{self.C.RESET}")
        print(f"{self.C.CYAN}{self.B.V}{self.C.RESET} {self.C.BOLD}{'#':<3} {'Tài khoản':<15} {'Trạng thái':<12} {'Kết nối':<25} {'':>5}{self.C.RESET} {self.C.CYAN}{self.B.V}{self.C.RESET}")
        print(f"{self.C.CYAN}{self.B.LT}{self.B.H * 70}{self.B.RT}{self.C.RESET}")
        
        for i, acc in enumerate(self.manager.accounts):
            # Status with symbol
            if acc.status == "Logged In":
                status_display = f"{self.C.BRIGHT_GREEN}[ON] Online{self.C.RESET}"
            elif acc.status == "Reconnecting":
                status_display = f"{self.C.BRIGHT_YELLOW}[..] Reconnect{self.C.RESET}"
            else:
                status_display = f"{self.C.RED}[--] Offline{self.C.RESET}"
            
            # Target marker
            target_marker = ""
            if isinstance(self.manager.command_target, int) and i == self.manager.command_target:
                target_marker = f"{self.C.PURPLE}[*]{self.C.RESET}"
            
            # Proxy info
            proxy_info = f"{self.C.DIM}Local IP{self.C.RESET}"
            if acc.proxy:
                try:
                    ip_part = acc.proxy.split('@')[-1]
                    if len(ip_part) > 20:
                        ip_part = "..." + ip_part[-17:]
                    proxy_info = f"{self.C.PURPLE}Proxy:{self.C.RESET}{self.C.DIM}{ip_part}{self.C.RESET}"
                except:
                    proxy_info = f"{self.C.PURPLE}Proxy{self.C.RESET}"

            print(f"{self.C.CYAN}{self.B.V}{self.C.RESET} {self.C.YELLOW}{i:<3}{self.C.RESET} {acc.username:<15} {status_display:<22} {proxy_info:<35} {target_marker} {self.C.CYAN}{self.B.V}{self.C.RESET}")
        
        print(f"{self.C.CYAN}{self.B.BL}{self.B.H * 70}{self.B.BR}{self.C.RESET}")
        print()
        return False
