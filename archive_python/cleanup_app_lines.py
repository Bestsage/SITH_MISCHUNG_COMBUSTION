
import os

file_path = r"c:\Users\samue\OneDrive\Documents\Rocket-Motor-Design-Plotter\core\app.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Ranges to delete (1-based inclusive, so we convert to 0-based)
# Range 1: 1108 to 1219
# Range 2: 1229 to 1351

# We delete from bottom to top to preserve indices
# Delete Range 2 first
start2 = 1229 - 1
end2 = 1351 - 1
# Verify content (optional safety check)
print(f"Deleting lines {start2+1} to {end2+1}")
print(f"Start content: {lines[start2].strip()}")
print(f"End content: {lines[end2].strip()}")

del lines[start2:end2+1]

# Delete Range 1
start1 = 1108 - 1
end1 = 1219 - 1
print(f"Deleting lines {start1+1} to {end1+1}")
print(f"Start content: {lines[start1].strip()}")
print(f"End content: {lines[end1].strip()}")

del lines[start1:end1+1]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Cleanup complete.")
