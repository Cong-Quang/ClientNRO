import random
class Config:
    # --- Server ---
    HOST = "103.245.255.222"
    PORT = 12451

    # --- Version ---
    VERSION = f"2.{random.randint(1, 100)}.{random.randint(1, 100)}"

    # --- Account ---
    # List of accounts to run
    # You can add more accounts here
    MAX_ACCOUNTS = 1000 # Giới hạn số lượng tài khoản chạy cùng lúc
    AUTO_RECONNECT = True # Tự động đăng nhập lại khi mất kết nối
    DEFAULT_LOGIN = [0, 2, 3, 4, 5] # Danh sách ID mặc định muốn login khi gõ 'login' hoặc 'login all'

    ACCOUNTS = [
        # Example with proxy: "proxy": "http://user:pass@ip:port"
        # If proxy is None or missing, it will use the machine's IP.
        {"username": "poopooi01", "password": "02082003"},
        {"username": "poopooi03", "password": "02082003"},
        {"username": "poopooi04", "password": "02082003"},
        {"username": "poopooi05", "password": "02082003"},
        {"username": "poopooi06", "password": "02082003"},
        {"username": "poopooi07", "password": "02082003"},
        {"username": "poopooi08", "password": "02082003"},
        {"username": "poopooi09", "password": "02082003"},
        {"username": "poopooi10", "password": "02082003"},
    ]


    # From prompt: "Fukada:103.245.255.222:12451:0,0,0"
    # Assuming first part is server name, then IP, then Port.
