
import tkinter as tk
import customtkinter as ctk
import re
from config import MONOSPACE_FONT, BG_PANEL, BG_SURFACE, BG_MAIN, TEXT_PRIMARY, ACCENT, TAB_ACCENT

def init(app):
    """Onglet Résumé - Affiche les résultats des calculs"""
    # Barre d'accent en haut
    accent_bar = ctk.CTkFrame(app.tab_summary, height=4, fg_color=TAB_ACCENT.get("summary", ACCENT))
    accent_bar.pack(fill=tk.X)
    
    summary_frame = ctk.CTkFrame(app.tab_summary, fg_color=BG_PANEL, corner_radius=10)
    summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    fs = app.scaled_font_size(13)
    fs_title = app.scaled_font_size(16)
    
    # Utiliser tk.Text pour garder les tags de couleur (encapsulé dans CTkFrame)
    text_container = ctk.CTkFrame(summary_frame, fg_color=BG_SURFACE, corner_radius=8)
    text_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    app.txt_summary = tk.Text(
        text_container,
        bg=BG_SURFACE,
        fg=TEXT_PRIMARY,
        insertbackground=ACCENT,
        font=(MONOSPACE_FONT, fs),
        highlightthickness=0,
        bd=0,
        wrap=tk.WORD,
        padx=15,
        pady=10,
        relief=tk.FLAT,  # Style plat moderne
        selectbackground=ACCENT,  # Couleur de sélection
        selectforeground=BG_MAIN,  # Texte sélectionné
    )
    app.txt_summary.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    # === TAGS DE COULEUR STYLE ÉDITEUR DE CODE ===
    app.txt_summary.tag_configure("title", foreground="#ff79c6", font=("Consolas", fs_title, "bold"))
    app.txt_summary.tag_configure("section", foreground="#ffb86c", font=("Consolas", fs, "bold"))
    app.txt_summary.tag_configure("label", foreground="#8be9fd")
    app.txt_summary.tag_configure("number", foreground="#bd93f9")
    app.txt_summary.tag_configure("unit", foreground="#6272a4")
    app.txt_summary.tag_configure("string", foreground="#f1fa8c")
    app.txt_summary.tag_configure("success", foreground="#50fa7b")
    app.txt_summary.tag_configure("warning", foreground="#ffb347")
    app.txt_summary.tag_configure("error", foreground="#ff5555")
    app.txt_summary.tag_configure("separator", foreground="#44475a")
    app.txt_summary.tag_configure("symbol", foreground="#ff79c6")
    
    # Scrollbar moderne
    scrollbar = ctk.CTkScrollbar(text_container, command=app.txt_summary.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)
    app.txt_summary.config(yscrollcommand=scrollbar.set)

def update(app):
    """Rafraîchit l'onglet Résumé."""
    if hasattr(app, 'last_summary_data'):
        insert_colored_summary(app, *app.last_summary_data)

def insert_colored_summary(app, summary: str, cooling_status: str, coolant_warning: str):
    """Insère le summary avec coloration syntaxique style éditeur de code."""
    # Reset
    app.txt_summary.delete("1.0", tk.END)
    
    lines = summary.split('\n')
    for line in lines:
        stripped = line.strip()
        
        # Lignes de séparateurs (═══)
        if '═══' in line or '---' in line:
            app.txt_summary.insert(tk.END, line + '\n', 'separator')
            continue
        
        # Titre principal (SITH MISCHUNG...)
        if 'SITH MISCHUNG' in line or 'LIGHT SIDE EDITION' in line:
            app.txt_summary.insert(tk.END, line + '\n', 'title')
            continue
        
        # Sections (--- XXX ---)
        if stripped.startswith('---') and stripped.endswith('---'):
            app.txt_summary.insert(tk.END, line + '\n', 'section')
            continue
        
        # Statuts de refroidissement
        if '✅' in line or 'OK' in line.upper() and 'Refroidissement' in line:
            app.txt_summary.insert(tk.END, line + '\n', 'success')
            continue
        if '⚠️' in line or '❌' in line:
            tag = 'error' if '❌' in line else 'warning'
            app.txt_summary.insert(tk.END, line + '\n', tag)
            continue
        
        # Lignes avec ":" (label : valeur)
        if ':' in line and not stripped.startswith('#'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                label_part = parts[0] + ':'
                value_part = parts[1]
                
                app.txt_summary.insert(tk.END, label_part, 'label')
                
                # Colorer les nombres dans la partie valeur
                # Pattern pour trouver les nombres (y compris décimaux et négatifs)
                tokens = re.split(r'(-?\d+\.?\d*)', value_part)
                for token in tokens:
                    if re.match(r'^-?\d+\.?\d*$', token) and token not in ('', '-'):
                        app.txt_summary.insert(tk.END, token, 'number')
                    elif any(u in token for u in ['mm', 'MW', 'kW', 'K', 's', 'bar', 'kg', 'm/', 'J/', 'W/', 'kN', 'N', '°', '%']):
                        # Unités
                        app.txt_summary.insert(tk.END, token, 'unit')
                    elif any(c in token for c in ['∞', 'ε', 'Ø', 'Δ', '@']):
                        # Symboles spéciaux
                        app.txt_summary.insert(tk.END, token, 'symbol')
                    else:
                        # Texte normal ou strings
                        app.txt_summary.insert(tk.END, token, 'string')
                
                app.txt_summary.insert(tk.END, '\n')
                continue
        
        # Ligne normale
        app.txt_summary.insert(tk.END, line + '\n')
