from commands.base_command import Command
from logs.logger_config import logger, TerminalColors
from typing import Any

class GroupCommand(Command):
    def __init__(self, manager):
        self.manager = manager
        self.C = TerminalColors

    async def execute(self, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) < 2:
            print("Lệnh group không hợp lệ. Dùng 'group list', 'group create <name> <ids>', 'group delete <name>', ...")
            return
        
        sub_cmd = parts[1]
        if sub_cmd == "list":
            self._list_groups()
        elif sub_cmd == "create" and len(parts) >= 4:
            self._create_group(parts[2], parts[3])
        elif sub_cmd == "delete" and len(parts) == 3:
            self._delete_group(parts[2])
        elif sub_cmd == "add" and len(parts) >= 4:
            self._add_to_group(parts[2], parts[3])
        elif sub_cmd == "remove" and len(parts) >= 4:
            self._remove_from_group(parts[2], parts[3])
        else:
            print("Lệnh group không hợp lệ.")
        
        return False

    def _list_groups(self):
        print(f"{self.C.CYAN}--- Danh sách nhóm ---{self.C.RESET}")
        for name, indices in self.manager.groups.items():
            members = ", ".join([self.manager.accounts[i].username for i in indices])
            print(f"- {self.C.CYAN}{name}{self.C.RESET}: [{self.C.YELLOW}{', '.join(map(str, indices))}{self.C.RESET}] ({members})")

    def _create_group(self, name: str, ids_str: str):
        if name == "all":
            print("Không thể tạo nhóm với tên 'all'.")
            return
        try:
            indices = [int(i) for i in ids_str.split(',')]
            if all(0 <= i < len(self.manager.accounts) for i in indices):
                self.manager.groups[name] = sorted(list(set(indices)))
                print(f"Đã tạo nhóm '{self.C.YELLOW}{name}{self.C.RESET}' với các thành viên: {self.manager.groups[name]}")
            else:
                print("Một hoặc nhiều chỉ số không hợp lệ.")
        except ValueError:
            print("Chỉ số thành viên không hợp lệ. Phải là các số được phân tách bằng dấu phẩy (VD: 1,2,3).")

    def _delete_group(self, name: str):
        if name == "all":
            print("Không thể xóa nhóm 'all'.")
        elif name in self.manager.groups:
            del self.manager.groups[name]
            print(f"Đã xóa nhóm '{self.C.YELLOW}{name}{self.C.RESET}'.")
        else:
            print(f"Không tìm thấy nhóm '{self.C.YELLOW}{name}{self.C.RESET}'.")

    def _add_to_group(self, name: str, ids_str: str):
        if name == "all":
            print("Không thể thêm thành viên vào nhóm 'all'.")
            return
        if name not in self.manager.groups:
            print(f"Không tìm thấy nhóm '{self.C.YELLOW}{name}{self.C.RESET}'.")
            return
        try:
            indices_to_add = {int(i) for i in ids_str.split(',')}
            valid_indices = {i for i in indices_to_add if 0 <= i < len(self.manager.accounts)}
            if len(valid_indices) != len(indices_to_add):
                print("Một vài chỉ số không hợp lệ đã bị bỏ qua.")
            current_members = set(self.manager.groups[name])
            current_members.update(valid_indices)
            self.manager.groups[name] = sorted(list(current_members))
            print(f"Đã cập nhật nhóm '{self.C.YELLOW}{name}{self.C.RESET}': {self.manager.groups[name]}")
        except ValueError:
            print("Chỉ số không hợp lệ.")

    def _remove_from_group(self, name: str, ids_str: str):
        if name == "all":
            print("Không thể xóa thành viên khỏi nhóm 'all'.")
            return
        if name not in self.manager.groups:
            print(f"Không tìm thấy nhóm '{self.C.YELLOW}{name}{self.C.RESET}'.")
            return
        try:
            indices_to_remove = {int(i) for i in ids_str.split(',')}
            current_members = set(self.manager.groups[name])
            current_members.difference_update(indices_to_remove)
            self.manager.groups[name] = sorted(list(current_members))
            print(f"Đã cập nhật nhóm '{self.C.YELLOW}{name}{self.C.RESET}': {self.manager.groups[name]}")
        except ValueError:
            print("Chỉ số không hợp lệ.")
