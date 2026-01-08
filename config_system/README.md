# Configuration Guide

## Giới Thiệu

ClientNRO hỗ trợ 2 cách cấu hình:

1. **Legacy Mode**: Sử dụng file `config.py` (backward compatible)
2. **New Mode**: Sử dụng file JSON `config/settings.json` (recommended)

## Cấu Hình Mới (JSON)

### Tạo File Config

Tạo file `config/settings.json`:

```json
{
  "server": {
    "host": "103.245.255.222",
    "port": 12451,
    "version": "2.0.0"
  },
  "accounts": {
    "max_concurrent": 1000,
    "auto_login": false,
    "default_login": [0, 2, 3, 4, 5],
    "login_blacklist": [],
    "accounts_file": "accounts.txt"
  },
  "character": {
    "default_gender": 1,
    "default_hair": 4
  },
  "proxy": {
    "use_local_ip_first": false,
    "proxy_file": "proxy.txt"
  },
  "ai": {
    "enabled": false,
    "weights_path": "ai_core/weights/default_weights.json",
    "state_dim": 20,
    "action_count": 32,
    "decision_interval": 0.5
  },
  "plugins": {
    "enabled": true,
    "plugin_dir": "plugins",
    "auto_load": true,
    "enabled_plugins": []
  },
  "logging": {
    "level": "INFO",
    "file": "logs/client.log"
  }
}
```

### Các Tùy Chọn Cấu Hình

#### Server Settings

- **`server.host`** (string): Địa chỉ server (IP hoặc domain)
- **`server.port`** (int): Cổng server (1-65535)
- **`server.version`** (string): Phiên bản client

#### Account Settings

- **`accounts.max_concurrent`** (int): Số tài khoản tối đa chạy đồng thời
- **`accounts.auto_login`** (bool): Tự động đăng nhập lại khi mất kết nối
- **`accounts.default_login`** (array): Danh sách index tài khoản login mặc định
- **`accounts.login_blacklist`** (array): Danh sách tài khoản bỏ qua khi login all
- **`accounts.accounts_file`** (string): Đường dẫn file chứa danh sách tài khoản

#### Character Settings

- **`character.default_gender`** (int): Giới tính mặc định (0: Trái Đất, 1: Namek, 2: Xayda)
- **`character.default_hair`** (int): ID kiểu tóc mặc định

#### Proxy Settings

- **`proxy.use_local_ip_first`** (bool): Ưu tiên IP local trước khi dùng proxy
- **`proxy.proxy_file`** (string): Đường dẫn file chứa danh sách proxy

#### AI Settings

- **`ai.enabled`** (bool): Bật/tắt AI
- **`ai.weights_path`** (string): Đường dẫn file weights của neural network
- **`ai.state_dim`** (int): Số chiều state vector
- **`ai.action_count`** (int): Số lượng actions
- **`ai.decision_interval`** (float): Khoảng thời gian giữa các quyết định AI (giây)

#### Plugin Settings

- **`plugins.enabled`** (bool): Bật/tắt plugin system
- **`plugins.plugin_dir`** (string): Thư mục chứa plugins
- **`plugins.auto_load`** (bool): Tự động load plugins khi khởi động
- **`plugins.enabled_plugins`** (array): Danh sách plugins được enable

#### Logging Settings

- **`logging.level`** (string): Mức độ log (DEBUG, INFO, WARNING, ERROR)
- **`logging.file`** (string): Đường dẫn file log

## Environment Variables

Bạn có thể override config bằng environment variables với prefix `CLIENTNRO_`:

```bash
# Windows
set CLIENTNRO_SERVER_HOST=192.168.1.100
set CLIENTNRO_SERVER_PORT=12345
set CLIENTNRO_AI_ENABLED=true

# Linux/Mac
export CLIENTNRO_SERVER_HOST=192.168.1.100
export CLIENTNRO_SERVER_PORT=12345
export CLIENTNRO_AI_ENABLED=true
```

Format: `CLIENTNRO_<SECTION>_<KEY>` (uppercase, underscore separated)

Ví dụ:
- `server.host` → `CLIENTNRO_SERVER_HOST`
- `ai.enabled` → `CLIENTNRO_AI_ENABLED`
- `plugins.auto_load` → `CLIENTNRO_PLUGINS_AUTO_LOAD`

## Sử Dụng Trong Code

### Load Config

```python
from config import ConfigLoader

# Get singleton instance
config = ConfigLoader.get_instance()

# Load from file
config.load("config/settings.json")

# Get values
host = config.get('server.host')
port = config.get('server.port', 12451)  # with default
ai_enabled = config.get('ai.enabled', False)
```

### Set Config

```python
# Set value
config.set('server.host', '192.168.1.100')

# Save to file
config.save()  # Save to loaded file
config.save('config/custom.json')  # Save to specific file
```

### Watch for Changes (Hot-reload)

```python
def on_config_changed(new_config):
    print("Config changed!")
    # Reload your settings here

config.watch(on_config_changed)
```

## Multiple Environments

Bạn có thể tạo nhiều config files cho các môi trường khác nhau:

- `config/dev.json` - Development
- `config/prod.json` - Production
- `config/test.json` - Testing

Load config tương ứng:

```python
import os

env = os.getenv('ENV', 'dev')
config.load(f'config/{env}.json')
```

## Migration từ config.py

Nếu bạn đang dùng `config.py` cũ, không cần làm gì cả! Hệ thống sẽ tự động fallback về config.py nếu không tìm thấy `config/settings.json`.

Để migrate sang JSON:

1. Copy các giá trị từ `config.py`
2. Tạo file `config/settings.json` với format như trên
3. Restart application

## Validation

Config sẽ được validate tự động khi load. Nếu có lỗi, bạn sẽ thấy error message chi tiết:

```
Error: Field 'server.port' must be >= 1
Error: Field 'server.port' must be <= 65535
Error: Missing required field: server.host
```

## Best Practices

### 1. Không commit sensitive data

Thêm vào `.gitignore`:

```
config/settings.json
config/prod.json
```

### 2. Sử dụng default.json làm template

Copy `config/default.json` thành `config/settings.json` và chỉnh sửa.

### 3. Document custom settings

Nếu plugin của bạn thêm settings mới, document trong README:

```json
{
  "my_plugin": {
    "enabled": true,
    "interval": 60,
    "api_key": "your_api_key"
  }
}
```

### 4. Validate input

Luôn cung cấp default values:

```python
# Good
interval = config.get('my_plugin.interval', 60)

# Bad
interval = config.get('my_plugin.interval')  # Could be None
```

## Troubleshooting

### Config không load

- Kiểm tra file path đúng không
- Kiểm tra JSON syntax (dùng JSON validator)
- Kiểm tra permissions của file

### Environment variables không work

- Kiểm tra tên biến đúng format: `CLIENTNRO_SECTION_KEY`
- Kiểm tra biến đã được set chưa: `echo %CLIENTNRO_SERVER_HOST%` (Windows) hoặc `echo $CLIENTNRO_SERVER_HOST` (Linux)

### Validation errors

- Đọc error message kỹ
- Kiểm tra type và range của values
- Tham khảo `config/default.json` để xem format đúng

## Tài Liệu Tham Khảo

- `config/default.json` - Default configuration template
- `config/config_loader.py` - Configuration loader implementation
- `config/config_validator.py` - Validation logic
