
import os

file_path = r"c:\Users\samue\OneDrive\Documents\Rocket-Motor-Design-Plotter\core\app.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Range to delete: 5492 to 5518 (1-based)
# But verify content first using start line content
start = 5492 - 1
end = 5518 - 1

print(f"Deleting duplicate export_dxf from {start+1} to {end+1}")
print(f"Start content: {lines[start].strip()}")
print(f"End content: {lines[end].strip()}")
print(f"Next line: {lines[end+1].strip()}")

del lines[start:end+1]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Cleanup 5 complete.")
