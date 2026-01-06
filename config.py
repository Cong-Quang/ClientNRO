import random
class Config:
    
    # tạo account
    # DEFAULT_CHAR_GENDER: 0 (Trai Dat), 1 (Namek), 2 (Sayda)
    DEFAULT_CHAR_GENDER = 1
    # DEFAULT_CHAR_HAIR: ID toc
    DEFAULT_CHAR_HAIR = 4

    # HOST: địa chỉ server (IP hoặc domain)
    HOST = "103.245.255.222"
    
    # PORT: cổng server (int)
    PORT = 12451

     # VERSION: phiên bản công cụ (tự sinh, không cần sửa)
    VERSION = f"2.{random.randint(1, 100)}.{random.randint(1, 100)}"

    #MAX_ACCOUNTS: số tối đa tài khoản chạy đồng thời (int)
    MAX_ACCOUNTS = 1000

    # AUTO_LOGIN: True/False — tự động đăng nhập lại khi mất kết nối
    AUTO_LOGIN = False   

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
    # ACCOUNTS: list dict tài khoản; mỗi dict cần 'username' và 'password', có thể thêm 'proxy' (tuỳ chọn)
    ACCOUNTS = []
    try:
        with open("accounts.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        ACCOUNTS.append({"username": parts[0].strip(), "password": parts[1].strip()})
    except Exception as e:
        print(f"Error loading accounts: {e}")

    # From prompt: "Fukada:103.245.255.222:12451:0,0,0"
    # Assuming first part is server name, then IP, then Port.

    # ========== AI Configuration ==========
    # AI_ENABLED: Default AI state (True/False) - set to False for safety
    AI_ENABLED = False
    
    # AI_WEIGHTS_PATH: Path to neural network weights (JSON format)
    AI_WEIGHTS_PATH = "ai_core/weights/default_weights.json"
    
    # AI_STATE_DIM: Input state dimension for neural network
    AI_STATE_DIM = 20
    
    # AI_ACTION_COUNT: Number of possible actions (expanded action space)
    AI_ACTION_COUNT = 32
    
    # AI_DECISION_INTERVAL: Seconds between AI decisions (float)
    AI_DECISION_INTERVAL = 0.5

