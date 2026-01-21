from textual.app import App, ComposeResult
from textual.widgets import MarkdownViewer, Header, Footer, Static
from textual.binding import Binding
import os

class WikiApp(App):
    """Une visionneuse de documentation Markdown avancée avec Textual."""

    TITLE = "SITH MISCHUNG COMBUSTION - Wiki Avancé"
    SUB_TITLE = "Utilisez les flèches pour naviguer, Q pour quitter"

    BINDINGS = [
        Binding("q", "quit", "Quitter", show=True),
        Binding("t", "toggle_toc", "Sommaire", show=True),
    ]

    def compose(self) -> ComposeResult:
        """Compose l'interface utilisateur de l'application."""
        yield Header()
        yield self.load_content()
        yield Footer()

    def load_content(self) -> MarkdownViewer | Static:
        """Charge le contenu du fichier wiki.md ou wiki.txt."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        wiki_files = ["wiki.md", "wiki.txt"]

        for filename in wiki_files:
            path = os.path.join(base_dir, filename)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8-sig") as f:
                        content = f.read()
                    # Utiliser le MarkdownViewer avec le contenu chargé
                    return MarkdownViewer(
                        content, show_table_of_contents=True, id="viewer"
                    )
                except Exception as e:
                    # En cas d'erreur de lecture, afficher un message d'erreur
                    return Static(f"[bold red]Erreur de lecture du Wiki[/bold red]\n\n{e}")

        # Si aucun fichier n'est trouvé
        return Static("[bold red]Fichier Wiki non trouvé ![/bold red]\n\nImpossible de trouver 'wiki.md' ou 'wiki.txt'.")

    def action_toggle_toc(self) -> None:
        """Affiche ou masque le sommaire."""
        viewer = self.query_one(MarkdownViewer)
        viewer.show_table_of_contents = not viewer.show_table_of_contents

if __name__ == "__main__":
    app = WikiApp()
    app.run()