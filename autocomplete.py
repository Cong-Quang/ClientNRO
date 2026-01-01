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
    "khu": [],
    "login": ["all"],
    "logout": ["all"],
    "gomap": ["stop"],
    "findnpc": [],
    "teleport": [],
    "teleportnpc": [],
    "andau": [],
    "hit": [],
    "proxy": ["list"]
}

COMMAND_HISTORY = []

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

    

    if os.name == 'nt':

        import msvcrt

        sys.stdout.write(prompt)

        sys.stdout.flush()

        buffer = []

        history_index = len(COMMAND_HISTORY)

        

        while True:

            char = msvcrt.getwch()

            

            if char in ('\r', '\n'):

                line = "".join(buffer)

                if line and (not COMMAND_HISTORY or line != COMMAND_HISTORY[-1]):

                    COMMAND_HISTORY.append(line)

                sys.stdout.write('\n')

                sys.stdout.flush()

                return line

            

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

                key = msvcrt.getwch()

                if key == 'H': # Up Arrow

                    if history_index > 0:

                        # Xóa dòng hiện tại

                        sys.stdout.write('\b \b' * len(buffer))

                        history_index -= 1

                        buffer = list(COMMAND_HISTORY[history_index])

                        sys.stdout.write("".join(buffer))

                        sys.stdout.flush()

                elif key == 'P': # Down Arrow

                    if history_index < len(COMMAND_HISTORY):

                        # Xóa dòng hiện tại

                        sys.stdout.write('\b \b' * len(buffer))

                        history_index += 1

                        if history_index == len(COMMAND_HISTORY):

                            buffer = []

                        else:

                            buffer = list(COMMAND_HISTORY[history_index])

                        sys.stdout.write("".join(buffer))

                        sys.stdout.flush()

            

            else:

                if char.isprintable():

                    buffer.append(char)

                    sys.stdout.write(char)

                    sys.stdout.flush()

    else:

        # Unix/Linux implementation

        try:

            import readline

            

            def completer(text, state):

                line = readline.get_line_buffer()

                matches, _ = get_candidates(line)

                

                # Filter matches to ensure they start with the current word 'text'

                # readline replaces the current word with the returned match.

                # get_candidates returns valid completions for the current slot.

                # If I type 'group cr', matches=['create']. 'text'='cr'. 

                # 'create'.startswith('cr') is True. Return 'create'.

                

                valid_matches = [m for m in matches if m.startswith(text)]

                

                if state < len(valid_matches):

                    match = valid_matches[state]

                    # Tự động thêm dấu cách nếu là lệnh trọn vẹn (tuỳ chọn, nhưng tiện)

                    # Nếu match là 1 lệnh chính có trong tree và có subcommands, thêm space

                    if match in COMMAND_TREE and COMMAND_TREE[match]:

                        match += " "

                    return match

                return None



            readline.set_completer(completer)

            readline.parse_and_bind("tab: complete")

            # Bind arrow keys for history is usually default in readline, but ensure it

            # readline.parse_and_bind('"\e[A": history-search-backward')

            # readline.parse_and_bind('"\e[B": history-search-forward')



        except ImportError:

            pass

            

        return input(prompt)
