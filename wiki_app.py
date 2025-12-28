from textual.app import App, ComposeResult
from textual.widgets import MarkdownViewer, Header, Footer
import os
import sys

class WikiApp(App):
    TITLE = "Rocket Motor Design - Wiki Viewer"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        
        # Load content here to pass it directly to the constructor
        base_dir = os.path.dirname(os.path.abspath(__file__))
        wiki_files = ["wiki.md", "wiki.txt"]
        content = "# Wiki Not Found\n\nCould not find 'wiki.md' or 'wiki.txt'."
        
        for filename in wiki_files:
            path = os.path.join(base_dir, filename)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8-sig") as f:
                        content = f.read()
                    break
                except Exception as e:
                    content = f"# Error reading wiki\n\n{e}"

        yield MarkdownViewer(content, show_table_of_contents=True)

if __name__ == "__main__":
    app = WikiApp()
    app.run()