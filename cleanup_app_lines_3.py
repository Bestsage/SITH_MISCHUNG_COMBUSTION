
import os

file_path = r"c:\Users\samue\OneDrive\Documents\Rocket-Motor-Design-Plotter\core\app.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Range to delete: 1101 to 1667 (1-based)
# But verify content first

start = 1101 - 1
# Locate the start of init_cad_tab just in case
for i, line in enumerate(lines):
    if "def init_cad_tab(self):" in line:
        start = i
        break

# Locate start of init_optimizer_tab as end marker
end = -1
for i, line in enumerate(lines):
    if "def init_optimizer_tab(self):" in line:
        end = i - 1 # Stop before this
        break

if end == -1:
    print("Could not find init_optimizer_tab")
    # Fallback to hardcoded line if confident? 
    # Or just warn
    exit(1)

print(f"Deleting CAD block from {start+1} to {end+1}")
print(f"Start content: {lines[start].strip()}")
print(f"End content: {lines[end].strip()}")
print(f"Next line: {lines[end+1].strip()}")

del lines[start:end+1]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Cleanup 3 complete.")
