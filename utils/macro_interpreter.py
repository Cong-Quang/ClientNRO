import re
import math
import random
from logs.logger_config import logger

class MacroInterpreter:
    def __init__(self, name: str, lines: list[str], manager=None):
        self.name = name
        # Store lines removing comments and stripping whitespace
        self.lines = [line.split('#')[0].strip() for line in lines]
        self.pc = 0  # Program Counter
        self.variables = {}
        self.loop_stack = []  # Stores (start_pc, type, condition/params)
        self.finished = False
        self.manager = manager

    def is_running(self):
        return not self.finished

    def substitute_variables(self, text: str) -> str:
        """Replaces ${var} with variable values."""
        if not text:
            return text
        
        def replace(match):
            key = match.group(1)
            if self.manager:
                if key == "online_count":
                    return str(len([a for a in self.manager.accounts if a.is_logged_in]))
                if key == "total_count":
                    return str(len(self.manager.accounts))
                if key == "map_zone_count":
                    # Try to get zone count
                    zone_count = 20
                    for acc in [a for a in self.manager.accounts if a.is_logged_in]:
                        if hasattr(acc, 'controller') and acc.controller.zone_list:
                            zone_count = len(acc.controller.zone_list)
                            break
                    return str(zone_count)
                    
            return str(self.variables.get(key, ""))
        
        # Simple substitution ${var}
        return re.sub(r'\$\{([^}]+)\}', replace, text)

    def evaluate_expression(self, expr: str):
        """Evaluates a python-like expression with variables substituted."""
        # Safety: allows basic math and boolean ops. 
        # Be careful with security if this acts on untrusted input, 
        # but for a local bot tool this is acceptable for now.
        
        # Determine if we need to substitute variables in the expression?
        # Typically the expression engine should handle variables, but here 
        # we can do string substitution first or build a safe eval context.
        # String substitution first is easier.
        
        safe_expr = self.substitute_variables(expr)
        
        try:
            # We map some safe functions
            context = {
                "int": int,
                "float": float,
                "str": str,
                "len": len,
                "math": math,
                "random": random,
                "abs": abs,
                "round": round
            }
            
            # System variables
            if self.manager:
                online_accs = [a for a in self.manager.accounts if a.is_logged_in]
                context["online_count"] = len(online_accs)
                context["total_count"] = len(self.manager.accounts)
                
                # Try to get zone count from any online account that has zone info
                zone_count = 20 # Default fallback
                for acc in online_accs:
                    if hasattr(acc, 'controller') and acc.controller.zone_list:
                        zone_count = len(acc.controller.zone_list)
                        break
                context["map_zone_count"] = zone_count
            
            # Add variables to context so expressions can use 'a' instead of '${a}'
            context.update(self.variables)
            
            return eval(safe_expr, {"__builtins__": None}, context)
        except Exception as e:
            logger.error(f"Macro Eval Error '{expr}': {e}")
            return False

    def next_command(self) -> str | None:
        """Executes logic until a game command (yieldable) is found or end of script."""
        while self.pc < len(self.lines):
            line = self.lines[self.pc]
            self.pc += 1

            if not line:
                continue

            # Variable substitution for the command processing (except for var declaration keys)
            # But we process keywords first.
            
            parts = line.split()
            cmd = parts[0].lower()

            # --- Control Flow & Logic ---

            if cmd == "print":
                msg = line[5:].strip()
                print(f"[Macro {self.name}] {self.substitute_variables(msg)}")
                continue

            elif cmd in ("var", "set"):
                # var name value...
                if len(parts) >= 3:
                    var_name = parts[1]
                    # The value might be an expression
                    expr_str = " ".join(parts[2:])
                    # Try to evaluate as expression first, if fails treat as string?
                    # Or simpler: always evaluate.
                    # If user wants string, they should quote it? "string"
                    val = self.evaluate_expression(expr_str)
                    self.variables[var_name] = val
                    logger.debug(f"[Macro] Set {var_name} = {val}")
                else:
                    logger.error(f"[Macro] Invalid var syntax: {line}")
                continue

            elif cmd == "while":
                # while condition
                condition_str = " ".join(parts[1:])
                if self.evaluate_expression(condition_str):
                    self.loop_stack.append({
                        "type": "while",
                        "start_pc": self.pc - 1, # Point to the 'while' line
                        "condition": condition_str
                    })
                else:
                    # Skip to endwhile
                    self.skip_block("while", "endwhile")
                continue

            elif cmd == "endwhile":
                if not self.loop_stack or self.loop_stack[-1]["type"] != "while":
                    logger.error(f"[Macro] 'endwhile' without matching 'while' at line {self.pc}")
                    continue
                
                block = self.loop_stack[-1]
                # Re-evaluate condition
                if self.evaluate_expression(block["condition"]):
                    self.pc = block["start_pc"] + 1 # Jump back inside loop
                else:
                    self.loop_stack.pop() # Loop finished
                continue

            # TODO: Add 'if', 'for' if needed. For now 'while' covers most.

            # --- Game Commands ---
            # If not a logic command, it's a game command.
            # Substitute variables and return.
            final_cmd = self.substitute_variables(line)
            return final_cmd

        self.finished = True
        return None

    def skip_block(self, start_keyword, end_keyword):
        """Skips lines until matching end_keyword, handling nesting."""
        nesting = 1
        while self.pc < len(self.lines):
            line = self.lines[self.pc]
            self.pc += 1
            if not line: continue
            
            parts = line.split()
            cmd = parts[0].lower()
            
            if cmd == start_keyword:
                nesting += 1
            elif cmd == end_keyword:
                nesting -= 1
                if nesting == 0:
                    return
        
        logger.warning(f"[Macro] EOF reached while seeking {end_keyword}")
