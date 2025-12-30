import sys
import os

# Cấu trúc lệnh gợi ý: { "lệnh_chính": ["sub1", "sub2", ...] }
COMMAND_TREE = {
    "group": ["list", "create", "delete", "add", "remove"],
    "pet": ["info", "follow", "protect", "attack", "home"],
    "logger": ["on", "off"],
    "autoplay": ["on", "off"],
    "autopet": ["on", "off"],
    "exit": [],
    "cls": [],
    "clear": [],
    "help": [],
    "list": [],
    "target": [],
    "show": [],
    "khu": []
}

def common_prefix(strings):
    """Tìm tiền tố chung dài nhất."""
    if not strings: return ""
    s1 = min(strings)
    s2 = max(strings)
    for i, c in enumerate(s1):
        if c != s2[i]: return s1[:i]
    return s1

def get_candidates(buffer_str):
    """
    Xác định danh sách gợi ý dựa trên bộ đệm hiện tại.
    Trả về: (list_candidates, prefix_current_word)
    """
    # Nếu buffer trống, gợi ý các lệnh chính
    if not buffer_str:
        return sorted(list(COMMAND_TREE.keys())), ""

    parts = buffer_str.split()
    
    # Trường hợp 1: Đang gõ lệnh chính (chưa có dấu cách hoặc chỉ có 1 từ chưa hoàn thiện)
    # VD: "gro" -> parts=["gro"], endswith space=False
    if len(parts) == 1 and not buffer_str.endswith(' '):
        prefix = parts[0]
        candidates = [cmd for cmd in COMMAND_TREE.keys() if cmd.startswith(prefix)]
        return sorted(candidates), prefix
    
    # Trường hợp 2: Đã gõ lệnh chính xong, đang gõ tham số
    # VD: "group " -> parts=["group"], endswith space=True
    # VD: "group cr" -> parts=["group", "cr"], endswith space=False
    
    cmd_base = parts[0]
    
    # Nếu lệnh chính không có trong danh sách, không gợi ý
    if cmd_base not in COMMAND_TREE:
        return [], ""
        
    sub_commands = COMMAND_TREE[cmd_base]
    if not sub_commands:
        return [], ""

    if buffer_str.endswith(' '):
        # Đang ở khoảng trắng sau lệnh chính -> gợi ý tất cả subcommands
        return sorted(sub_commands), ""
    else:
        # Đang gõ subcommand
        sub_prefix = parts[-1]
        candidates = [sub for sub in sub_commands if sub.startswith(sub_prefix)]
        return sorted(candidates), sub_prefix

def get_input_with_autocomplete(prompt, commands=None):
    # commands được giữ lại để tương thích nhưng logic chính dùng COMMAND_TREE
    sys.stdout.write(prompt)
    sys.stdout.flush()
    buffer = []
    
    if os.name == 'nt':
        import msvcrt
        while True:
            char = msvcrt.getwch()
            
            if char in ('\r', '\n'):
                sys.stdout.write('\n')
                sys.stdout.flush()
                return "".join(buffer)
            
            elif char == '\t':
                current_text = "".join(buffer)
                matches, prefix = get_candidates(current_text)
                
                if not matches:
                    continue
                
                if len(matches) == 1:
                    completion = matches[0]
                    # Phần cần thêm là phần còn thiếu của từ đang gõ
                    # completion là "create", prefix là "cr" -> to_add là "eate"
                    to_add = completion[len(prefix):]
                    buffer.extend(list(to_add))
                    sys.stdout.write(to_add)
                    
                    # Nếu là lệnh chính và có sub-command, tự động thêm dấu cách cho tiện
                    # Logic: Nếu prefix khớp với completion (đã gõ xong hoặc vừa gõ xong) 
                    # VÀ lệnh này nằm trong root COMMAND_TREE 
                    # VÀ nó có subcommands
                    full_word = prefix + to_add
                    if full_word in COMMAND_TREE and COMMAND_TREE[full_word] and not buffer[-1] == ' ':
                         buffer.append(' ')
                         sys.stdout.write(' ')

                    sys.stdout.flush()
                else:
                    common = common_prefix(matches)
                    if len(common) > len(prefix):
                        to_add = common[len(prefix):]
                        buffer.extend(list(to_add))
                        sys.stdout.write(to_add)
                        sys.stdout.flush()
                    else:
                        # Show list
                        sys.stdout.write('\n')
                        sys.stdout.write("  ".join(matches))
                        sys.stdout.write('\n')
                        sys.stdout.write(prompt + "".join(buffer))
                        sys.stdout.flush()

            elif char == '\x08': # Backspace
                if buffer:
                    buffer.pop()
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            
            elif char == '\x03': # Ctrl+C
                raise KeyboardInterrupt
            
            elif char == '\x00' or char == '\xe0':
                msvcrt.getwch()
            
            else:
                if char.isprintable():
                    buffer.append(char)
                    sys.stdout.write(char)
                    sys.stdout.flush()
    else:
        return input(prompt)