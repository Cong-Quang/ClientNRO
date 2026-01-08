"""
Combo command to execute macros
"""
import os
from commands.base_command import Command
from utils.macro_interpreter import MacroInterpreter

class ComboCommand(Command):
    """
    Execute a combo/macro from a file.
    Usage: combo <macro_name>
    """
    def __init__(self, manager):
        self.manager = manager
        self.macro_dir = "macros"
        if not os.path.exists(self.macro_dir):
            os.makedirs(self.macro_dir)

    async def execute(self, parts):
        if len(parts) < 2:
            print("Usage: combo <macro_name>")
            print("Available macros:")
            self._list_macros()
            return None

        macro_name = parts[1]
        
        # Try different extensions
        file_path = None
        for ext in [".txt", ".macro", ""]:
            path = os.path.join(self.macro_dir, macro_name + ext)
            if os.path.exists(path):
                file_path = path
                break
        
        if not file_path:
            print(f"❌ Macro '{macro_name}' not found in {self.macro_dir}/")
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            print(f"▶️ Starting combo: {macro_name}")
            return MacroInterpreter(macro_name, lines, self.manager)
            
        except Exception as e:
            print(f"❌ Error loading macro: {e}")
            return None

    def _list_macros(self):
        if not os.path.exists(self.macro_dir):
            print("  (No macros directory)")
            return
            
        files = os.listdir(self.macro_dir)
        if not files:
            print("  (No macros found)")
            return
            
        for f in files:
            if f.endswith(".txt") or f.endswith(".macro"):
                print(f"  - {os.path.splitext(f)[0]}")
