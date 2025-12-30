import asyncio
import os # Import the os module
from network.session import Session
from network.message import Message
from network.service import Service
from config import Config
from controller import Controller
from cmd import Cmd
from logs.logger_config import logger, set_logger_status

from ui import display_pet_info, display_help, display_pet_help

# --- Cấu hình Logging ---
# Đặt True để xem log chi tiết (DEBUG), đặt False để xem log quan trọng (INFO)
VERBOSE_LOGGING = True 

# if VERBOSE_LOGGING:
#     logger.basicConfig(level=logger.DEBUG, format='[%(levelname)s] %(message)s')
# else:
#     logger.basicConfig(level=logger.INFO, format='[%(levelname)s] %(message)s')

# logger = logger.getLogger(__name__)

async def command_loop(session: Session, controller: Controller):
    """Vòng lặp chờ lệnh từ người dùng."""
    pet_status_map = {
        "follow": 0,
        "protect": 1,
        "attack": 2,
        "home": 3,
    }
    while session.connected:
        try:
            # Chạy input() trong một thread riêng để không block vòng lặp asyncio
            command = await asyncio.to_thread(input, "Nhập lệnh (help, pet, exit): ")
            command = command.strip().lower()

            if command.startswith("pet"):
                parts = command.split()
                if len(parts) == 1:
                    display_pet_help()
                else:
                    sub_cmd = parts[1]
                    if sub_cmd == "info":
                        # FIX: Lấy dữ liệu đệ tử mới nhất mỗi khi gọi lệnh
                        await Service.gI().pet_info()
                        await asyncio.sleep(0.5) # Đợi server phản hồi
                        display_pet_info()
                    elif sub_cmd in pet_status_map:
                        status_id = pet_status_map[sub_cmd]
                        await Service.gI().pet_status(status_id)
                    else:
                        logger.warning(f"Lệnh đệ tử không xác định: '{sub_cmd}'. Gõ 'pet' để xem trợ giúp.")

            elif command.startswith("logger"):
                parts = command.split()
                if len(parts) > 1:
                    sub_cmd = parts[1]
                    if sub_cmd == "on":
                        set_logger_status(True)
                        logger.info("Đã BẬT logger.")
                    elif sub_cmd == "off":
                        set_logger_status(False)
                        logger.info("Đã TẮT logger.")
                    else:
                        logger.warning(f"Lệnh logger không xác định: '{sub_cmd}'. Sử dụng 'on' hoặc 'off'.")
                else:
                    logger.warning("Vui lòng chỉ định 'on' hoặc 'off' cho logger.")
            
            elif command.startswith("autoplay"):
                parts = command.split()
                if len(parts) > 1:
                    sub_cmd = parts[1]
                    if sub_cmd == "on":
                        controller.toggle_autoplay(True)
                    elif sub_cmd == "off":
                        controller.toggle_autoplay(False)
                    else:
                        logger.warning(f"Lệnh autoplay không xác định: '{sub_cmd}'. Sử dụng 'on' hoặc 'off'.")
                else:
                    logger.warning("Vui lòng chỉ định 'on' hoặc 'off' cho autoplay.")

            elif command.startswith("autopet"):
                parts = command.split()
                if len(parts) > 1:
                    sub_cmd = parts[1]
                    if sub_cmd == "on":
                        controller.toggle_auto_pet(True)
                    elif sub_cmd == "off":
                        controller.toggle_auto_pet(False)
                    else:
                        logger.warning(f"Lệnh autopet không xác định: '{sub_cmd}'. Sử dụng 'on' hoặc 'off'.")
                else:
                    logger.warning("Vui lòng chỉ định 'on' hoặc 'off' cho autopet.")

            elif command == "clear": # New clear command
                os.system('cls') # For Windows
            
            elif command.startswith("khu"):
                parts = command.split()
                if len(parts) == 2:
                    try:
                        zone_id = int(parts[1])
                        await Service.gI().request_change_zone(zone_id)
                    except ValueError:
                        logger.warning("ID khu vực không hợp lệ. Vui lòng nhập một số nguyên.")
                else:
                    logger.warning("Cú pháp không đúng. Sử dụng: chuyenkhu [id khu]")

            elif command == "help":
                display_help()
            elif command == "exit":
                logger.info("Đang thoát...")
                session.disconnect()
                break
            elif command: # Người dùng nhập gì đó nhưng không phải lệnh hợp lệ
                logger.warning(f"Lệnh không xác định: '{command}'. Gõ 'help' để xem các lệnh có sẵn.")

        except (EOFError, KeyboardInterrupt):
            logger.info("Đã nhận tín hiệu thoát, đang đóng kết nối...")
            session.disconnect()
            break
        except Exception as e:
            logger.error(f"Lỗi trong vòng lặp lệnh: {e}")
            break

async def main():
    controller = Controller()
    session = Session(controller=controller)
    Service.setup(session) # Khởi tạo Service Singleton
    
    # Kết nối tới server
    await session.connect(Config.HOST, Config.PORT)

    # Đợi một chút để quá trình trao đổi key (nếu có) diễn ra
    await asyncio.sleep(1)

    if session.connected:
        logger.info("Gửi thông tin đăng nhập tới server...")
        
        # 1. Gửi setClientType (Cmd -29, SubCmd 2)
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
        writer.write_utf(f"Con Cặc|{Config.VERSION}") # Platform | Version
        await session.send_message(msg_client)
        await asyncio.sleep(0.5)

        # 2. Gửi gói tin android (Cmd 126)
        logger.info("Gửi gói tin android (Cmd 126)...")
        msg_pack = Message(126)
        msg_pack.writer().write_utf("")
        await session.send_message(msg_pack)
        await asyncio.sleep(0.5)

        # 3. Gửi gói tin đăng nhập (Cmd -29, SubCmd 0)
        logger.info("Gửi gói tin đăng nhập...")
        msg_login = Message(Cmd.NOT_LOGIN)
        writer = msg_login.writer()
        writer.write_byte(0)              # sub-command LOGIN
        writer.write_utf(Config.UerName)
        writer.write_utf(Config.PassWord)
        writer.write_utf(Config.VERSION)

        writer.write_byte(1)              # Type (1 for isLogin2/Standard)
        await session.send_message(msg_login)
        
        # Chạy vòng lặp lệnh và chờ kết nối
        logger.info("Đăng nhập thành công! Sẵn sàng nhận lệnh.")
        display_help()
        
        # Vòng lặp chính để giữ kết nối và nhận lệnh
        main_loop = asyncio.create_task(command_loop(session, controller))
        await main_loop
    else:
        logger.error("Không thể kết nối tới server.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Đang dừng...")