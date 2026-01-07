"""Module chứa hàm hiển thị nhiệm vụ."""

from logs.logger_config import TerminalColors as C, print_header, print_separator


def display_task_info(account, compact=False, idx: int = None, print_output=True):
    """Hiển thị thông tin nhiệm vụ."""
    task = account.char.task
    
    if not task or not task.name:
        if compact:
            idx_str = f"[{idx}]" if idx is not None else ""
            line = f" {C.PURPLE}{idx_str:<3}{C.RESET} {C.DIM}│{C.RESET} {C.YELLOW}{account.username:<12}{C.RESET} {C.DIM}│{C.RESET} {C.GREY}Chưa có dữ liệu{C.RESET}"
            if print_output: print(line)
            return line
        else:
            msg = f"{C.YELLOW}[{account.username}] Chưa có thông tin nhiệm vụ.{C.RESET}"
            if print_output: print(msg)
            return msg

    task_id = task.task_id
    raw_task_id = getattr(account.char, 'ctask_id', -1)
    task_name = task.name.strip()
    
    sub_name = ""
    if task.sub_names and 0 <= task.index < len(task.sub_names):
        sub_name = task.sub_names[task.index].strip()
    else:
        sub_name = "..."

    current = task.count
    required = 0
    if task.counts and 0 <= task.index < len(task.counts):
        required = task.counts[task.index]
    
    prog_str = f"{current}/{required}"
    
    if compact:
        idx_str = f"[{idx}]" if idx is not None else ""
        name_short = task_name if len(task_name) < 28 else task_name[:26] + ".."
        step_short = sub_name if len(sub_name) < 23 else sub_name[:21] + ".."
        
        # Highlight desync
        if raw_task_id != -1 and raw_task_id != task_id:
            prog_full = f"{C.RED}(!){C.RESET} {prog_str}"
        else:
            prog_full = prog_str

        line = (
            f" {C.PURPLE}{idx_str:<3}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.YELLOW}{account.username:<12}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.CYAN}{str(task_id):<3}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.GREEN}{name_short:<28}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.BRIGHT_YELLOW}{step_short:<23}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.PURPLE}{prog_full}{C.RESET}"
        )
        if print_output: print(line)
        return line
    else:
        id_display = f"{task_id}"
        if raw_task_id != -1 and raw_task_id != task_id:
            id_display = f"{task_id} {C.RED}(Server: {raw_task_id} - Mismatch!){C.RESET}"
        
        lines = []
        lines.append("")
        print_header(f"[QUEST] Nhiem Vu - {account.username}", width=50, color=C.YELLOW)
        lines.append(f"  {C.GREEN}Tên NV  :{C.RESET} {task_name} {C.DIM}[ID:{id_display}]{C.RESET}")
        lines.append(f"  {C.GREEN}Bước    :{C.RESET} {sub_name} {C.DIM}(Index: {task.index}){C.RESET}")
        lines.append(f"  {C.GREEN}Tiến độ :{C.RESET} {C.PURPLE}{prog_str}{C.RESET}")
        
        output = "\n".join(lines)
        if print_output:
            for l in lines[1:]:
                print(l)
            print_separator(50, color=C.YELLOW)
        return output
