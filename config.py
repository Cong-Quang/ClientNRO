import random
class Config:
    # HOST: địa chỉ server (IP hoặc domain)
    HOST = "103.245.255.222"
    
    # PORT: cổng server (int)
    PORT = 12451

     # VERSION: phiên bản công cụ (tự sinh, không cần sửa)
    VERSION = f"2.{random.randint(1, 100)}.{random.randint(1, 100)}"

    #MAX_ACCOUNTS: số tối đa tài khoản chạy đồng thời (int)
    MAX_ACCOUNTS = 1000

    # AUTO_LOGIN: True/False — tự động đăng nhập lại khi mất kết nối
    AUTO_LOGIN = True   

    # DEFAULT_LOGIN: list các index (int) trong ACCOUNTS được login khi 'login' không có tham số / 'login default'
    DEFAULT_LOGIN = [0, 2, 3, 4, 5]  

    # LOGIN_BLACKLIST: list username (str) hoặc index (int) sẽ bị bỏ qua khi dùng 'login all'
    # Ví dụ mẫu: bỏ qua username 'poopooi07' và tài khoản index 9
    #LOGIN_BLACKLIST: list = ["poopooi07", 9]
    LOGIN_BLACKLIST: list = []

    # USE_LOCAL_IP_FIRST: True/False — True để ưu tiên gán 5 IP local cho 1 tài khoản trước khi dùng proxy.
    # False để bỏ qua IP local và gán trực tiếp 5 tài khoản cho 1 proxy.
    USE_LOCAL_IP_FIRST = False     
    
    # ACCOUNTS: list dict tài khoản; mỗi dict cần 'username' và 'password', có thể thêm 'proxy' (tuỳ chọn)
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
        {"username": "ordinary215", "password": "123456789"},
    ]


    # From prompt: "Fukada:103.245.255.222:12451:0,0,0"
    # Assuming first part is server name, then IP, then Port.
