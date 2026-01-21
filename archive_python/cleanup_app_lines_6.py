
import os

file_path = r"c:\Users\samue\OneDrive\Documents\Rocket-Motor-Design-Plotter\core\app.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Range to delete: 5297 to 5353 (1-based)
# 5297:             # --- PLOTS ---
# 5353:             self.ax_temp.fill_between(X_mm, T_wall_hot_list, ...

start = 5297 - 1
end = 5353 - 1

print(f"Deleting legacy thermal plot block from {start+1} to {end+1}")
print(f"Start content: {lines[start].strip()}")
print(f"End content: {lines[end].strip()}")

del lines[start:end+1]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Cleanup 6 complete.")
