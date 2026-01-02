import time
import os

class ComboEngine:
    def __init__(self, combo_file="combo.txt"):
        self.combo_file = combo_file
        self.combos = {}
        self.load()

    def load(self):
        self.combos.clear()
        if not os.path.exists(self.combo_file):
            return

        current = None
        with open(self.combo_file, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue

                if line.startswith("[") and line.endswith("]"):
                    current = line[1:-1].strip()
                    self.combos[current] = []
                    continue

                if current:
                    self.combos[current].append(line)

    def list(self):
        return list(self.combos.keys())

    def exists(self, name):
        return name in self.combos

    def get(self, name):
        return self.combos.get(name, [])
