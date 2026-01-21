
file_path = r"c:\Users\samue\OneDrive\Documents\Rocket-Motor-Design-Plotter\core\app.py"
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Verify the lines match expectations before deleting
# Line 1333 (0-indexed 1332) should start with whitespace and "objective_function, bounds,"
# Line 1369 (0-indexed 1368) should start with "    def _evaluate_design"

start_idx = 1332  # Line 1333
end_idx = 1368    # Line 1369 (start of next function)

print(f"Line {start_idx+1}: {lines[start_idx]}")
print(f"Line {end_idx+1}: {lines[end_idx]}")

if "objective_function" in lines[start_idx] and "def _evaluate_design" in lines[end_idx]:
    print("Deleting garbage lines...")
    del lines[start_idx:end_idx]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Cleanup complete.")
else:
    print("Optimization worker cleanup failed: line mismatch.")
