
import tkinter as tk
import customtkinter as ctk
import os
import re
import io
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from tkinter import messagebox

from config import *
from utils import *

def init(app):
    """Initialise l'onglet Wiki."""
    # Nettoyer l'onglet existant si nécessaire
    for widget in app.tab_wiki.winfo_children():
        widget.destroy()

    # Barre de couleur en haut
    tk.Frame(app.tab_wiki, height=4, bg=TAB_ACCENT.get("wiki", ACCENT)).pack(fill=tk.X)
    
    # Frame principal qui contiendra tout
    main_container = ctk.CTkFrame(app.tab_wiki, fg_color="transparent")
    main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Titre
    title_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    title_frame.pack(fill=tk.X, padx=5, pady=(5,0))
    
    ctk.CTkLabel(
        title_frame,
        text="Wiki - Documentation complète et guide utilisateur.",
        font=(UI_FONT, 16, "bold"),
        text_color=app.accent
    ).pack(side=tk.LEFT)
    
    ctk.CTkLabel(title_frame, text="📖 Wiki & Documentation",
                 font=(UI_FONT, 16, "bold"), text_color="#9966ff").pack(side=tk.LEFT, padx=10)
    
    # Barre d'outils
    toolbar = ctk.CTkFrame(main_container, fg_color="transparent")
    toolbar.pack(fill=tk.X, padx=5, pady=5)
    
    # Variable pour la recherche
    app.wiki_search_var = tk.StringVar()
    ctk.CTkLabel(toolbar, text="Recherche:").pack(side=tk.LEFT, padx=(0, 5))
    search_entry = ctk.CTkEntry(toolbar, textvariable=app.wiki_search_var, width=200)
    search_entry.pack(side=tk.LEFT, padx=(0, 5))
    search_entry.bind("<Return>", lambda e: wiki_search(app))
    
    ctk.CTkButton(toolbar, text="Chercher", command=lambda: wiki_search(app)).pack(side=tk.LEFT, padx=5)
    ctk.CTkButton(toolbar, text="Suivant", command=lambda: wiki_search_next(app)).pack(side=tk.LEFT)
    
    # Widget Text Standard (pas de HTML)
    # Création d'un PanedWindow pour diviser l'espace
    # Note: CTk ne supporte pas nativement PanedWindow avec styling, on utilise frames côte à côte
    content_area = ctk.CTkFrame(main_container, fg_color="transparent")
    content_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Frame pour le sommaire (gauche) - Scrollable maintenant!
    app.toc_frame = ctk.CTkScrollableFrame(content_area, width=250, label_text="Sommaire")
    app.toc_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
    
    # Frame pour le contenu (droite)
    content_frame = ctk.CTkFrame(content_area, fg_color="transparent")
    content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    app.wiki_text = tk.Text(content_frame, bg=app.bg_surface, fg=app.text_primary,
                             font=(UI_FONT, 11), wrap=tk.WORD,
                             insertbackground=app.accent, padx=20, pady=15,
                             highlightthickness=0, bd=0,
                             relief=tk.FLAT,  # Style plat moderne
                             selectbackground=app.accent,
                             selectforeground=app.bg_main)
    app.wiki_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Scrollbar pour le texte principal
    scrollbar = ctk.CTkScrollbar(content_frame, command=app.wiki_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    app.wiki_text.config(yscrollcommand=scrollbar.set)
    
    # === CONFIGURATION DES STYLES TEXTE ===
    _configure_tags(app)
    
    # Variables d'état
    app.wiki_search_pos = "1.0"
    app.wiki_images = []
    
    # Charger contenu
    load_wiki_content(app)

def _configure_tags(app):
    """Configure les tags du widget Text."""
    wt = app.wiki_text
    bg_sf = app.bg_surface
    
    wt.tag_configure("h1", font=(UI_FONT, 20, "bold"), foreground="#ff79c6", spacing1=20, spacing3=15)
    wt.tag_configure("h2", font=(UI_FONT, 15, "bold"), foreground="#ffb86c", spacing1=18, spacing3=8)
    wt.tag_configure("h3", font=(UI_FONT, 13, "bold"), foreground="#8be9fd", spacing1=12, spacing3=5)
    wt.tag_configure("h4", font=(UI_FONT, 12, "bold"), foreground="#bd93f9", spacing1=8, spacing3=3)
    
    wt.tag_configure("bullet", font=(UI_FONT, 11), foreground=app.text_primary, lmargin1=30, lmargin2=50, spacing1=2)
    wt.tag_configure("numbered_list", font=(UI_FONT, 11), foreground=app.text_primary, lmargin1=30, lmargin2=50, spacing1=2)
    
    wt.tag_configure("code", font=(MONOSPACE_FONT, 10), background=bg_sf, foreground="#50fa7b", lmargin1=40, lmargin2=40, spacing1=1)
    wt.tag_configure("table_header", font=(MONOSPACE_FONT, 10, "bold"), foreground="#8be9fd", background=bg_sf)
    wt.tag_configure("table_row", font=(MONOSPACE_FONT, 10), foreground=app.text_primary, background=bg_sf)
    wt.tag_configure("formula", font=(MONOSPACE_FONT, 11, "bold"), foreground="#bd93f9", background=bg_sf, lmargin1=40, lmargin2=40, spacing1=3, spacing3=3)
    
    wt.tag_configure("important", foreground="#ff5555", font=(UI_FONT, 11, "bold"), background=bg_sf, lmargin1=20, lmargin2=40, spacing1=3, spacing3=3)
    wt.tag_configure("warning", foreground="#ffb347", font=(UI_FONT, 11, "bold"), background=bg_sf, lmargin1=20, lmargin2=40, spacing1=3, spacing3=3)
    wt.tag_configure("success", foreground="#50fa7b", font=(UI_FONT, 11, "bold"), lmargin1=20, lmargin2=40, spacing1=3, spacing3=3)
    wt.tag_configure("quote", font=(UI_FONT, 11, "italic"), foreground="#9fb4d3", lmargin1=50, lmargin2=50, spacing1=5, spacing3=5)
    wt.tag_configure("highlight", background="#3d3d00", foreground="#ffff00")
    wt.tag_configure("center", justify='center')
    wt.tag_configure("normal", font=(UI_FONT, 11), foreground=app.text_primary, spacing1=2)

def render_latex(app, formula, fontsize=12):
    """Renders LaTeX formula to a tk.PhotoImage using Matplotlib"""
    try:
        fig = Figure(figsize=(5, 0.8), dpi=100)
        fig.patch.set_facecolor(app.bg_surface)
        
        if not formula.startswith('$'):
            formula = f"${formula}$"
        
        fig.text(0.5, 0.5, formula, fontsize=fontsize, 
                 color=app.text_primary, 
                 ha='center', va='center')
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', facecolor=app.bg_surface, edgecolor='none', bbox_inches='tight', pad_inches=0.1)
        buf.seek(0)
        
        img = tk.PhotoImage(data=buf.getvalue())
        buf.close()
        return img
    except Exception as e:
        print(f"LaTeX Error: {e}")
        return None

def load_wiki_content(app):
    """Charge le contenu du wiki depuis un fichier externe"""
    wiki_files = [('wiki.md', 'markdown'), ('wiki.txt', 'text')]
    
    content = None
    wiki_format = 'text'
    
    # Chercher dans le dossier parent (root du projet)
    # app.py est dans core/, wiki.py est dans ui/tabs/ => remonter de 2 ou 3 niveaux selon l'appel
    # Le plus sûr est de baser sur os.getcwd() si lancé depuis root, ou relatif à ce fichier
    
    # Méthode robuste: chercher dans root projet
    # ui/tabs/wiki.py -> ui/tabs -> ui -> root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    # Fallback si structure différente
    if not os.path.exists(os.path.join(project_root, 'main.py')):
         # Essayer relative à cwd
         project_root = os.getcwd()

    for filename, format_type in wiki_files:
        wiki_file = os.path.join(project_root, filename)
        if os.path.exists(wiki_file):
            try:
                with open(wiki_file, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                wiki_format = format_type
                break
            except Exception as e:
                content = f"Erreur lors du chargement de {filename}: {str(e)}"
                break
    
    if content is None:
        content = "Erreur: Aucun fichier wiki trouvé (wiki.md ou wiki.txt).\n\nPlacez un fichier wiki.md dans le dossier racine."
        wiki_format = 'text'
    
    app.wiki_text.config(state=tk.NORMAL)
    app.wiki_text.delete(1.0, tk.END)
    
    # Vider sommaire
    for widget in app.toc_frame.winfo_children():
        widget.destroy()
    
    if wiki_format == 'markdown':
        _load_markdown_wiki(app, content)
    else:
        _load_text_wiki(app, content)
    
    app.wiki_text.config(state=tk.DISABLED)

def _load_markdown_wiki(app, content):
    """Parseur Markdown simple"""
    lines = content.split('\n')
    i = 0
    in_code_block = False
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        # Code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            i += 1
            continue
        
        if in_code_block:
            app.wiki_text.insert(tk.END, line + '\n', "code")
            i += 1
            continue
        
        # LaTeX
        if line.strip().startswith('$$') and line.strip().endswith('$$'):
            formula = line.strip()[2:-2].strip()
            if formula:
                img = render_latex(app, formula, fontsize=14)
                if img:
                    app.wiki_images.append(img)
                    app.wiki_text.insert(tk.END, '\n')
                    app.wiki_text.image_create(tk.END, image=img)
                    app.wiki_text.insert(tk.END, '\n\n')
                else:
                    app.wiki_text.insert(tk.END, line + '\n', "code")
            i += 1
            continue

        # Tables (simplifié)
        if line.strip().startswith('|'):
            # Collecter lignes
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            if len(table_lines) >= 2:
                _insert_formatted_table(app, table_lines)
            else:
                app.wiki_text.insert(tk.END, table_lines[0] + '\n', "normal")
            continue
        
        # Headers
        if line.startswith('#') and not in_code_block:
            level = len(line.split()[0])
            text = line.lstrip('#').strip()
            tag = f"h{min(level, 4)}"
            
            start_index = app.wiki_text.index("end-1c")
            app.wiki_text.insert(tk.END, text + '\n', tag)
            
            # Add to TOC
            indent = "  " * (level - 1)
            btn = ctk.CTkButton(app.toc_frame, text=f"{indent}{text}",
                                anchor="w", fg_color="transparent", height=24,
                                text_color=app.text_primary,
                                command=lambda pos=start_index: wiki_goto_section(app, pos))
            btn.pack(fill=tk.X, pady=1)
            
            i += 1
            continue
        
        # Lists
        if re.match(r'^\s*[\*\-\+]\s+', line):
            clean_line = re.sub(r'^\s*[\*\-\+]\s+', '• ', line)
            app.wiki_text.insert(tk.END, clean_line + '\n', "bullet")
            i += 1
            continue
        
        if re.match(r'^\s*\d+\.\s+', line):
            app.wiki_text.insert(tk.END, line + '\n', "numbered_list")
            i += 1
            continue
            
        # Quotes/Warnings
        if line.startswith('>'):
            content_text = line.lstrip('>').strip()
            tag = "quote"
            if "⚠️" in content_text or "Attention" in content_text: tag = "warning"
            elif "✅" in content_text: tag = "success"
            app.wiki_text.insert(tk.END, content_text + '\n', tag)
            i += 1
            continue
        
        # Text
        if line.strip():
            app.wiki_text.insert(tk.END, line + '\n', "normal")
        else:
            app.wiki_text.insert(tk.END, '\n', "normal")
            
        i += 1

def _insert_formatted_table(app, table_lines):
    rows = [l.strip('|').split('|') for l in table_lines]
    rows = [[c.strip() for c in r] for r in rows]
    
    if not rows: return

    # Calculate widths
    num_cols = max(len(r) for r in rows)
    col_widths = [0] * num_cols
    for row in rows:
        for idx, cell in enumerate(row):
            if idx < num_cols:
                if set(cell) <= {'-', ':', ' '}: continue
                col_widths[idx] = max(col_widths[idx], len(cell))
    
    def get_sep(char='─', mid='┼'):
        return mid.join([char * (w + 2) for w in col_widths])
    
    top = "┌" + get_sep('─', '┬') + "┐"
    mid = "├" + get_sep('─', '┼') + "┤"
    bot = "└" + get_sep('─', '┴') + "┘"
    
    app.wiki_text.insert(tk.END, top + "\n", "code")
    for idx, row in enumerate(rows):
        is_sep = all(set(c) <= {'-', ':', ' '} for c in row)
        if is_sep:
            app.wiki_text.insert(tk.END, mid + "\n", "code")
            continue
            
        formatted = []
        for i in range(num_cols):
            cell = row[i] if i < len(row) else ""
            formatted.append(f" {cell:<{col_widths[i]}} ")
        
        line = "│" + "│".join(formatted) + "│"
        tag = "table_header" if idx == 0 else "table_row"
        app.wiki_text.insert(tk.END, line + "\n", tag)
    
    app.wiki_text.insert(tk.END, bot + "\n", "code")

def _load_text_wiki(app, content):
    """Fallback text loader"""
    app.wiki_text.insert(tk.END, content)

def wiki_goto_section(app, pos):
    app.wiki_text.see(pos)
    app.wiki_text.tag_remove("highlight", "1.0", tk.END)
    app.wiki_text.tag_add("highlight", pos, f"{pos} lineend")

def wiki_search(app):
    term = app.wiki_search_var.get()
    if not term: return
    app.wiki_text.tag_remove("highlight", "1.0", tk.END)
    app.wiki_search_pos = "1.0"
    wiki_search_next(app)

def wiki_search_next(app):
    term = app.wiki_search_var.get()
    if not term: return
    
    pos = app.wiki_text.search(term, app.wiki_search_pos, nocase=True, stopindex=tk.END)
    if pos:
        end = f"{pos}+{len(term)}c"
        app.wiki_text.tag_add("highlight", pos, end)
        app.wiki_text.see(pos)
        app.wiki_search_pos = end
    else:
        app.wiki_search_pos = "1.0"
        messagebox.showinfo("Recherche", "Fin du document atteinte")
