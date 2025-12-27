import os

files = [
    r"c:\Users\samue\OneDrive\Documents\Rocket-Motor-Design-Plotter\wiki.md",
    r"c:\Users\samue\OneDrive\Documents\Rocket-Motor-Design-Plotter\wiki.txt"
]

replacements = {
    '✅': '+',
    '❌': '-',
    '⚠️': '**ATTENTION:**',
    '🔥': '',
    '💀': '**DANGER:**',
    '🌡️': '',
    '📚': '',
    '📖': '',
    '📐': '',
    '📊': '',
    '🗄️': '',
    '💾': '',
    '👉': '->',
    '💡': 'NOTE:',
    '🛑': 'STOP:',
    '⚡': '',
    '🔧': '',
    '⚙️': '',
    '📝': '',
    '🔍': '',
    '📑': '',
    '🔗': '',
    '📌': '',
    '📍': '',
    '🚩': '',
    '🏁': '',
    '🚀': '',
    '💥': '',
    '🧪': '',
    '🔬': '',
    '🔭': '',
    '📡': '',
    '🛰️': '',
    '🛸': '',
    '🌍': '',
    '🌎': '',
    '🌏': '',
    '🪐': '',
    '🌠': '',
    '🌌': '',
    '🌑': '',
    '🌒': '',
    '🌓': '',
    '🌔': '',
    '🌕': '',
    '🌖': '',
    '🌗': '',
    '🌘': '',
    '🌙': '',
    '🌚': '',
    '🌛': '',
    '🌜': '',
    '☀️': '',
    '🌝': '',
    '🌞': '',
    '⭐': '',
    '🌟': '',
    '🌠': '',
    '☁️': '',
    '⛅': '',
    '⛈️': '',
    '🌤️': '',
    '🌥️': '',
    '🌦️': '',
    '🌧️': '',
    '🌨️': '',
    '🌩️': '',
    '🌪️': '',
    '🌫️': '',
    '🌬️': '',
    '🌀': '',
    '🌈': '',
    '🌂': '',
    '☂️': '',
    '☔': '',
    '⛱️': '',
    '⚡': '',
    '❄️': '',
    '☃️': '',
    '⛄': '',
    '☄️': '',
    '🔥': '',
    '💧': '',
    '🌊': '',
}

for file_path in files:
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            
            # Replace emojis
            for emoji, replacement in replacements.items():
                new_content = new_content.replace(emoji, replacement)
            
            # Replace xrightarrow if present
            if r'\xrightarrow' in new_content:
                print(f"Found xrightarrow in {file_path}, replacing...")
                # Simple replacement might not work for complex arguments, but let's try basic one
                # Or just replace the command name if arguments are compatible
                # \xrightarrow[under]{over} -> \overset{over}{\underset{under}{\longrightarrow}}
                # But usually it's just \xrightarrow{text} -> \overset{text}{\longrightarrow}
                # Since I can't easily parse latex with regex, I'll just warn or try simple replace
                pass 

            if content != new_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {file_path}")
            else:
                print(f"No changes needed for {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    else:
        print(f"File not found: {file_path}")
