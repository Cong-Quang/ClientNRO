import random
import os

# Try to import new config system
try:
    from config_system.config_loader import ConfigLoader
    _CONFIG_LOADER_AVAILABLE = True
except ImportError:
    _CONFIG_LOADER_AVAILABLE = False

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
    
    # ========== New Config System Integration ==========
    _loader = None
    _initialized = False
    
    @classmethod
    def init(cls):
        """Initialize config loader from JSON if available"""
        if cls._initialized:
            return
        
        cls._initialized = True
        
        if not _CONFIG_LOADER_AVAILABLE:
            return
        
        # Try to load from JSON config
        # Try to load from JSON config
        cls._loader = ConfigLoader.get_instance()
        
        # Priority: config/settings.json > config_system/default.json
        config_path = "config/settings.json"
        if not os.path.exists(config_path):
            config_path = "config_system/default.json"
            
        if os.path.exists(config_path):
            try:
                cls._loader.load(config_path)
                
                # Override class attributes with JSON values
                cls.HOST = cls._loader.get('server.host', cls.HOST)
                cls.PORT = cls._loader.get('server.port', cls.PORT)
                cls.MAX_ACCOUNTS = cls._loader.get('accounts.max_concurrent', cls.MAX_ACCOUNTS)
                cls.AUTO_LOGIN = cls._loader.get('accounts.auto_login', cls.AUTO_LOGIN)
                cls.DEFAULT_LOGIN = cls._loader.get('accounts.default_login', cls.DEFAULT_LOGIN)
                cls.LOGIN_BLACKLIST = cls._loader.get('accounts.login_blacklist', cls.LOGIN_BLACKLIST)
                cls.USE_LOCAL_IP_FIRST = cls._loader.get('proxy.use_local_ip_first', cls.USE_LOCAL_IP_FIRST)
                cls.DEFAULT_CHAR_GENDER = cls._loader.get('character.default_gender', cls.DEFAULT_CHAR_GENDER)
                cls.DEFAULT_CHAR_HAIR = cls._loader.get('character.default_hair', cls.DEFAULT_CHAR_HAIR)
                cls.AI_ENABLED = cls._loader.get('ai.enabled', cls.AI_ENABLED)
                cls.AI_WEIGHTS_PATH = cls._loader.get('ai.weights_path', cls.AI_WEIGHTS_PATH)
                cls.AI_STATE_DIM = cls._loader.get('ai.state_dim', cls.AI_STATE_DIM)
                cls.AI_ACTION_COUNT = cls._loader.get('ai.action_count', cls.AI_ACTION_COUNT)
                cls.AI_DECISION_INTERVAL = cls._loader.get('ai.decision_interval', cls.AI_DECISION_INTERVAL)
                
                print(f"✅ Loaded configuration from {config_path}")
            except Exception as e:
                print(f"⚠️ Error loading JSON config, using defaults: {e}")
        else:
            print(f"ℹ️ No configuration file found (checked {config_path}). Using hardcoded defaults.")
    
    @classmethod
    def get(cls, key: str, default=None):
        """
        Get config value from new system (with fallback to class attributes)
        
        Args:
            key: Configuration key (dot notation, e.g., 'server.host')
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        if cls._loader:
            return cls._loader.get(key, default)
        return default
    
    @classmethod
    def set(cls, key: str, value):
        """
        Set config value in new system
        
        Args:
            key: Configuration key (dot notation)
            value: Value to set
        """
        if cls._loader:
            cls._loader.set(key, value)

