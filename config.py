class Config:
    # --- Server ---
    HOST = "103.245.255.222"
    PORT = 12451

    # --- Version ---
    VERSION = "2.3.5"

    # --- Account ---
    # List of accounts to run
    # You can add more accounts here
    MAX_ACCOUNTS = 5 # Giới hạn số lượng tài khoản chạy cùng lúc
    AUTO_RECONNECT = True # Tự động đăng nhập lại khi mất kết nối
    DEFAULT_LOGIN = [3, 4, 5, 6, 7] # Danh sách ID mặc định muốn login khi gõ 'login' hoặc 'login all'

    ACCOUNTS = [
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
