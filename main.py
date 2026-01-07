import asyncio
import sys
import os
import shutil
from config import Config
from core.account import Account
from core.account_manager import AccountManager
from logs.logger_config import logger, TerminalColors, Box, print_header, print_separator
from ui import (
    display_help, display_pet_info, display_pet_help, display_character_status,
    display_character_base_stats, display_task_info, print_compact_header_show,
    print_compact_header_pet, print_compact_header_csgoc, print_compact_header_task,
    print_compact_header_autoquest, print_compact_footer, display_macro_help
)
from utils.autocomplete import get_input_with_autocomplete, COMMAND_TREE
from utils.macro_interpreter import MacroInterpreter
from handlers.ai_command_handler import AICommandHandler
from commands.command_loader import load_commands
from targeted_commands.targeted_command_loader import load_targeted_commands
import time

MOB_NAMES = {}

def load_mob_names():
    global MOB_NAMES
    try:
        with open("mob_data.txt", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    try:
                        mob_id = int(parts[0])
                        mob_name = parts[1].strip()
                        MOB_NAMES[mob_id] = mob_name
                    except ValueError:
                        continue
    except FileNotFoundError:
        logger.warning("File mob_data.txt not found.")
    except Exception as e:
        logger.error(f"Error loading mob_data.txt: {e}")

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
    
    # === Command Registry ===
    commands = load_commands(manager, proxy_list, None)
    targeted_commands = load_targeted_commands()
    
    current_macro: MacroInterpreter | None = None
    
    # Initialize AI Command Handler
    ai_handler = AICommandHandler()
    ai_handler.load_weights("ai_core/weights/default_weights.json")
    
    while True:
        # Update autocomplete with current groups
        current_group_names = list(manager.groups.keys())
        # Thêm 'default' vào danh sách gợi ý cho login
        login_suggestions = current_group_names + ["default"]
        COMMAND_TREE["login"] = login_suggestions
        COMMAND_TREE["logout"] = current_group_names
        COMMAND_TREE["target"] = current_group_names
        
        target_str = f"{C.RED}None{C.RESET}"
        if manager.command_target is not None:
            if isinstance(manager.command_target, int):
                target_str = f"Acc {C.YELLOW}{manager.command_target}{C.RESET}"
            else:
                target_str = f"Group '{C.YELLOW}{manager.command_target}{C.RESET}'"
        
        prompt = f"[{target_str}]> "

        try:
            if current_macro:
                if not current_macro.is_running():
                    current_macro = None
                    print(f"{C.GREEN}Macro hoàn tất.{C.RESET}")
                    continue

                command = current_macro.next_command()
                if command is None:
                    # Check again if finished after call
                    if not current_macro.is_running():
                        current_macro = None
                        print(f"{C.GREEN}Macro hoàn tất.{C.RESET}")
                    continue

                print(f"{C.CYAN}>>> [Macro] {command}{C.RESET}")
            else:
                command = await asyncio.to_thread(get_input_with_autocomplete, prompt)

            command = command.strip().lower()

            parts = command.split()
            if not command:
                continue

            cmd_base = parts[0]

            if cmd_base in commands:
                result = await commands[cmd_base].execute(parts=parts)
                if isinstance(result, bool) and result:
                    break
                if isinstance(result, MacroInterpreter):
                    current_macro = result
                continue

            # === AI Commands ===
            if await ai_handler.handle_ai_command(parts, manager):
                continue

            # --- Pre-validation for Targetted Commands ---
            if cmd_base in targeted_commands:
                # === Xử lý đặc biệt cho lệnh "show boss" ===
                # Lệnh này chỉ cần hiển thị 1 lần vì dữ liệu boss là chung cho tất cả tài khoản
                if command.strip() == "show boss":
                    from logic.boss_manager import BossManager
                    from ui import display_boss_list
                    bosses = BossManager().get_bosses()
                    display_boss_list(bosses)
                    continue
                
                # --- Command Execution ---
                target_accounts = manager.get_target_accounts()
                # Lọc chỉ gửi lệnh cho acc online, giữ lại index gốc để hiển thị đúng
                online_targets_with_idx = []
                for acc in target_accounts:
                    if acc.is_logged_in:
                        try:
                            real_idx = manager.accounts.index(acc)
                            online_targets_with_idx.append((real_idx, acc))
                        except ValueError:
                            pass

                if not online_targets_with_idx:
                    print("Không có mục tiêu nào đang online để thực hiện lệnh.")
                    continue
                
                # Build a readable recipient list
                recipients = []
                for idx, acc in online_targets_with_idx:
                    recipients.append(f"[{C.YELLOW}{acc.username}{C.RESET}]")
                print(f"Đang gửi lệnh '{C.PURPLE}{command}{C.RESET}' đến {len(online_targets_with_idx)} tài khoản: {', '.join(recipients)}")
                
                # Xác định chế độ hiển thị gọn (compact) nếu gửi cho nhiều hơn 1 tài khoản
                is_compact = len(online_targets_with_idx) > 1
                if is_compact and "pet info" in command:
                    print_compact_header_pet()
                elif is_compact and "csgoc" in command:
                    print_compact_header_csgoc()
                elif is_compact and command.strip() == "show":
                    print_compact_header_show()
                elif is_compact and command.strip() == "show nhiemvu":
                    print_compact_header_task()
                elif is_compact and "autobomong status" in command:
                    print_compact_header_autoquest()

                tasks = []
                for real_idx, acc in online_targets_with_idx:
                    tasks.append(targeted_commands[cmd_base].execute(account=acc, parts=parts, compact_mode=is_compact, idx=real_idx))
                results = await asyncio.gather(*tasks)

                # Nếu là lệnh show nhiemvu, in kết quả đã thu thập để tránh bị loạn dòng
                if "show nhiemvu" in command:
                    for success, msg in results:
                        if success and msg and msg != "OK":
                            print(msg)
                continue

            print(f"{C.RED}Lệnh không xác định: '{command}'. Gõ 'help'.{C.RESET}")


        except (EOFError, KeyboardInterrupt):
            logger.info("Đã nhận tín hiệu thoát, đang đóng tất cả kết nối...")
            manager.stop_all()
            break
        except Exception as e:
            logger.error(f"Lỗi trong vòng lặp lệnh chính: {e}")

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
    # Clean pycache first
    clean_pycache()
    load_mob_names()
    
    # Setup logger
    # logger is already imported and configured in logger_config
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Đang dừng...")
    finally:
        clean_pycache()