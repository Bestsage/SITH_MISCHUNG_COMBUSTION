
import os

file_path = r"c:\Users\samue\OneDrive\Documents\Rocket-Motor-Design-Plotter\core\app.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Range to delete: 1101 to 1250 (1-based)
start = 1101 - 1
end = 1250 - 1

# Safety check
print(f"Deleting lines {start+1} to {end+1}")
print(f"Start content: {lines[start].strip()}")
print(f"End content: {lines[end].strip()}")
# Check what's after
if len(lines) > end + 1:
    print(f"Next line: {lines[end+1].strip()}")

del lines[start:end+1]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Cleanup 2 complete.")
