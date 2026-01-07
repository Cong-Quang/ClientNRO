import os
import importlib
from targeted_commands.base_targeted_command import TargetedCommand

def load_targeted_commands():
    commands = {}
    command_dir = "targeted_commands"
    for filename in os.listdir(command_dir):
        if filename.endswith("_command.py") and not filename.startswith("base_"):
            module_name = f"targeted_commands.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, TargetedCommand) and attr is not TargetedCommand:
                        command_name = filename[:-11]
                        commands[command_name] = attr()
            except Exception as e:
                print(f"Error loading targeted command from {filename}: {e}")
    return commands
