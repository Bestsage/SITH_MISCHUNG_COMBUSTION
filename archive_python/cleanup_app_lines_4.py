
import os

file_path = r"c:\Users\samue\OneDrive\Documents\Rocket-Motor-Design-Plotter\core\app.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Range to delete: 900 to 1100 (1-based)
# 900: def on_heatmap_click(self, event):
# 1100: (empty line before init_optimizer_tab)

start = 900 - 1
end = 1100 - 1

print(f"Deleting block from {start+1} to {end+1}")
print(f"Start content: {lines[start].strip()}")
print(f"End content: {lines[end].strip()}")
print(f"Next line: {lines[end+1].strip()}")

del lines[start:end+1]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Cleanup 4 complete.")
