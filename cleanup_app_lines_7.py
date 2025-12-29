
import os

file_path = r"c:\Users\samue\OneDrive\Documents\Rocket-Motor-Design-Plotter\core\app.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Ranges to delete (Based on previous view_file lines)
# Lines ~3839 to 4300 contained all wiki logic
# Specifically:
# 3839 (after init_wiki_tab replacement) to 4300 covers:
# - config tags (now in module)
# - render_latex
# - load_wiki_content
# - _load_markdown_wiki
# - _insert_formatted_table
# - _load_text_wiki
# - open_wiki_at
# - wiki_search
# - wiki_search_next
# - wiki_goto_section
# - load_database (Wait, this is separate tab?)

# Let's inspect carefully. load_database starts around 4235.
# So we need to stop before load_database.

# I'll scan for start of load_database to find the cut point.

start_delete = -1
end_delete = -1

for i, line in enumerate(lines):
    if "def init_wiki_tab(self):" in line:
        start_delete = i + 3 # Skip the def lines I just replaced
    if "def load_database(self):" in line:
        end_delete = i - 1
        break

if start_delete > 0 and end_delete > start_delete:
    print(f"Deleting lines {start_delete+1} to {end_delete+1}")
    print(f"Start content: {lines[start_delete].strip()}")
    print(f"End content: {lines[end_delete].strip()}")
    # Verify it captures wiki stuff
    del lines[start_delete:end_delete+1]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Cleanup Wiki complete.")
else:
    print("Could not locate range automatically.")
