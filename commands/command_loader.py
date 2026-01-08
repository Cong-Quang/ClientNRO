import os
import importlib
from commands.base_command import Command

def load_commands(manager, proxy_list, combo_engine):
    commands = {}
    command_dir = "commands"
    for filename in os.listdir(command_dir):
        if filename.endswith("_command.py") and not filename.startswith("base_") and not filename.startswith("command_loader"):
            module_name = f"commands.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, Command) and attr is not Command:
                        command_name = filename[:-11]  # remove _command.py
                        
                        # Instantiate with the correct arguments
                        if command_name in ["list", "group", "target", "logout", "exit", "plugin"]:
                            commands[command_name] = attr(manager)
                        elif command_name in ["login", "proxy"]:
                            commands[command_name] = attr(manager, proxy_list)
                        elif command_name == "combo":
                            commands[command_name] = attr(manager)
                        elif command_name == "help":
                            commands[command_name] = attr()
                        elif command_name == "clear":
                             commands[command_name] = attr()
                        elif command_name == "sleep":
                             commands[command_name] = attr()
                        elif command_name == "autologin":
                             commands[command_name] = attr()
                        elif command_name == "wait":
                             commands[command_name] = attr()
                        elif command_name == "config":
                             commands[command_name] = attr(manager)
                        else:
                            commands[command_name] = attr()

            except Exception as e:
                print(f"Error loading command from {filename}: {e}")
    
    # Add aliases
    if "clear" in commands:
        commands["cls"] = commands["clear"]
        
    return commands
