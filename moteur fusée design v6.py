import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, font as tkfont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np
import math
import json
import os
from datetime import datetime

#this code only works with python 3.10 and below, 3.11, 3.13, and 3.14 dont support rocketcea.

# Essayer d'importer RocketCEA
try:
    from rocketcea.cea_obj import CEA_Obj
    HAS_ROCKETCEA = True
except ImportError as e:
    print(f"⚠️ RocketCEA non disponible: {e}")
    HAS_ROCKETCEA = False
    CEA_Obj = None

# Essayer d'importer ezdxf, sinon on désactive l'export DXF
try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False

class RocketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SITH MISCHUNG COMBUSTION : LIGHT SIDE EDITION v6.2")
        self.root.geometry("1700x1080")
        self.root.state('zoomed')  # Maximize for large displays

        # Zoom options for UI (defined early for create_inputs)
        self.zoom_options = ["Auto", "1.0", "1.15", "1.25", "1.35", "1.5"]

        # --- THEME (OLED + Néon) ---
        self.bg_main = "#05060e"
        self.bg_panel = "#0b1020"
        self.bg_surface = "#0f172c"
        self.accent = "#00eaff"       # cyan néon
        self.accent_alt = "#ff5af1"   # magenta néon
        self.accent_alt2 = "#9dff6a"  # vert néon doux
        self.accent_alt3 = "#ffb347"  # orange chaud
        self.accent_alt4 = "#7b9bff"  # lavande
        self.text_primary = "#e8f1ff"
        self.text_muted = "#9fb4d3"
        self.grid_color = "#1f2a3d"

        self.tab_accent = {
            "summary": self.accent,
            "visu": self.accent_alt3,
            "thermal": self.accent_alt,
            "graphs": self.accent,
            "cea": self.accent_alt2,
            "database": self.accent_alt4,
            "solver": "#00ffaa",  # Vert/cyan pour le solveur
        }

        plt.rcParams.update({
            "figure.facecolor": self.bg_main,
            "axes.facecolor": self.bg_surface,
            "axes.edgecolor": self.accent,
            "axes.labelcolor": self.text_primary,
            "xtick.color": self.text_primary,
            "ytick.color": self.text_primary,
            "grid.color": self.grid_color,
            "text.color": self.text_primary,
            "axes.titlecolor": self.text_primary,
            "axes.prop_cycle": plt.cycler(color=[self.accent, self.accent_alt, self.accent_alt2, self.accent_alt3, "#7b9bff"]),
        })
        
        # --- VARIABLES ---
        self.inputs = {}
        self.results = {}
        self.geometry_profile = None  # Pour stocker X, Y du profil
        
        style = ttk.Style()
        style.theme_use('clam')
        self.root.configure(bg=self.bg_main)
        style.configure(".", background=self.bg_main, foreground=self.text_primary)
        style.configure("TFrame", background=self.bg_main)
        style.configure("TLabelFrame", background=self.bg_surface, foreground=self.accent, bordercolor=self.accent, borderwidth=1, relief="solid")
        style.configure("TLabelFrame.Label", background=self.bg_surface, foreground=self.accent)
        style.configure("TLabel", background=self.bg_main, foreground=self.text_primary)
        style.configure("TNotebook", background=self.bg_main, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.bg_surface, foreground=self.text_primary, padding=(12, 8))
        style.map("TNotebook.Tab", background=[("selected", self.accent)], foreground=[("selected", "#05060e")])
        style.configure("TButton", background=self.accent, foreground="#05060e", padding=(10, 6), borderwidth=0, focusthickness=3, focuscolor=self.accent_alt)
        style.map("TButton", background=[("active", self.accent_alt)], foreground=[("disabled", "#55607a")])
        style.configure("Primary.TButton", background=self.accent, foreground="#05060e", padding=(10, 6), borderwidth=0, focusthickness=3, focuscolor=self.accent_alt)
        style.map("Primary.TButton", background=[("active", self.accent_alt)], foreground=[("disabled", "#55607a")])
        style.configure("Secondary.TButton", background=self.accent_alt, foreground="#05060e", padding=(10, 6), borderwidth=0, focusthickness=3, focuscolor=self.accent)
        style.map("Secondary.TButton", background=[("active", self.accent)], foreground=[("disabled", "#55607a")])
        style.configure("Success.TButton", background=self.accent_alt2, foreground="#05060e", padding=(10, 6), borderwidth=0, focusthickness=3, focuscolor=self.accent_alt)
        style.map("Success.TButton", background=[("active", self.accent_alt3)], foreground=[("disabled", "#55607a")])
        style.configure("Warning.TButton", background=self.accent_alt3, foreground="#05060e", padding=(10, 6), borderwidth=0, focusthickness=3, focuscolor=self.accent_alt)
        style.map("Warning.TButton", background=[("active", self.accent_alt2)], foreground=[("disabled", "#55607a")])
        style.configure("TEntry", fieldbackground=self.bg_surface, foreground=self.text_primary, insertcolor=self.accent)
        style.configure("TCombobox", fieldbackground=self.bg_surface, background=self.bg_surface, foreground=self.text_primary, arrowcolor=self.accent)
        style.map("TCombobox", fieldbackground=[("readonly", self.bg_surface)], foreground=[("readonly", self.text_primary)])
        style.configure("TSpinbox", fieldbackground=self.bg_surface, background=self.bg_surface, foreground=self.text_primary, arrowcolor=self.accent, insertcolor=self.accent)
        style.map("TSpinbox", fieldbackground=[("!disabled", self.bg_surface)], foreground=[("!disabled", self.text_primary)])
        style.configure("TCheckbutton", background=self.bg_main, foreground=self.text_primary)
        style.configure("Treeview", background=self.bg_surface, fieldbackground=self.bg_surface, foreground=self.text_primary, bordercolor=self.bg_surface, rowheight=22)
        style.configure("Treeview.Heading", background=self.bg_main, foreground=self.accent, bordercolor=self.bg_surface)
        style.map("Treeview", background=[("selected", "#123042")], foreground=[("selected", self.text_primary)])
        style.configure("Vertical.TScrollbar", background=self.bg_main, troughcolor=self.bg_surface, arrowcolor=self.accent)
        style.configure("Horizontal.TProgressbar", background=self.accent, troughcolor=self.bg_surface, lightcolor=self.accent, darkcolor=self.accent)

        # --- LAYOUT PRINCIPAL ---
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panneau Gauche
        left_panel = ttk.LabelFrame(main_frame, text="Paramètres de Conception", width=380)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Panneau Droit
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tabs = ttk.Notebook(right_panel)
        self.tabs.pack(fill=tk.BOTH, expand=True)
        
        self.tab_summary = ttk.Frame(self.tabs)
        self.tab_visu = ttk.Frame(self.tabs)
        self.tab_thermal = ttk.Frame(self.tabs)
        self.tab_graphs = ttk.Frame(self.tabs)
        self.tab_cea = ttk.Frame(self.tabs)
        self.tab_database = ttk.Frame(self.tabs)
        self.tab_solver = ttk.Frame(self.tabs)
        self.tab_wiki = ttk.Frame(self.tabs)
        
        self.tabs.add(self.tab_summary, text="📊 Résumé")
        self.tabs.add(self.tab_visu, text="Visualisation 2D")
        self.tabs.add(self.tab_thermal, text="Analyse Thermique (Bartz)")
        self.tabs.add(self.tab_graphs, text="Analyses Paramétriques")
        self.tabs.add(self.tab_cea, text="Sortie NASA CEA (Raw)")
        self.tabs.add(self.tab_database, text="🔍 Base de Données")
        self.tabs.add(self.tab_solver, text="🧊 Solveur Coolant")
        self.tabs.add(self.tab_wiki, text="📖 Wiki")
        
        # Calculer le zoom AVANT d'initialiser les onglets (pour les polices)
        self.ui_scale = self.auto_scale_from_display()
        
        self.create_inputs(left_panel)
        self.init_summary_tab()
        self.init_visu_tab()
        self.init_thermal_tab()
        self.init_cea_tab()
        self.init_graphs_tab()
        self.init_database_tab()
        self.init_solver_tab()
        self.init_wiki_tab()

        # Apply UI scaling after layout is ready
        self.apply_ui_scale(self.ui_scale)

    def auto_scale_from_display(self):
        """Calcule un facteur de zoom en fonction de la résolution écran."""
        try:
            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()
            # Heuristique: 1080p -> 1.0, 1440p/2K -> 1.35, 4K -> 1.6
            if width >= 3800 or height >= 2100:
                return 1.6
            if width >= 2500 or height >= 1400:
                return 1.35
            return 1.0
        except Exception:
            return 1.0

    def scaled_font_size(self, base_size: int = 11) -> int:
        """Retourne une taille de police ajustée selon le zoom."""
        return max(10, int(base_size * getattr(self, 'ui_scale', 1.0)))

    def apply_ui_scale(self, scale: float):
        """Applique le zoom Tk et met à jour les polices."""
        self.ui_scale = scale
        
        try:
            self.root.tk.call('tk', 'scaling', scale)
        except tk.TclError:
            pass
        
        # Utiliser les tailles de base stockées, pas les tailles actuelles
        if not hasattr(self, '_base_font_sizes'):
            self._base_font_sizes = {}
            for fname in ("TkDefaultFont", "TkTextFont", "TkFixedFont", "TkMenuFont", "TkHeadingFont", "TkTooltipFont"):
                try:
                    f = tkfont.nametofont(fname)
                    self._base_font_sizes[fname] = abs(f.cget("size"))
                except tk.TclError:
                    self._base_font_sizes[fname] = 10
        
        for fname, base_size in self._base_font_sizes.items():
            try:
                f = tkfont.nametofont(fname)
                f.configure(size=max(8, int(base_size * scale)))
            except tk.TclError:
                continue
        
        # Mettre à jour les widgets Text personnalisés
        self.update_text_widget_fonts()

    def update_text_widget_fonts(self):
        """Met à jour les polices des widgets Text selon le zoom actuel."""
        fs = self.scaled_font_size(13)
        fs_title = self.scaled_font_size(16)
        
        # Widget Résumé
        if hasattr(self, 'txt_summary'):
            self.txt_summary.configure(font=("Consolas", fs))
            self.txt_summary.tag_configure("title", font=("Consolas", fs_title, "bold"))
            self.txt_summary.tag_configure("section", font=("Consolas", fs, "bold"))
        
        # Widget CEA
        if hasattr(self, 'txt_cea'):
            self.txt_cea.configure(font=("Consolas", fs))
            self.txt_cea.tag_configure("cea_header", font=("Consolas", fs, "bold"))
            self.txt_cea.tag_configure("cea_comment", font=("Consolas", fs, "italic"))
        
        # Widget Base de données
        if hasattr(self, 'db_details'):
            self.db_details.configure(font=("Consolas", fs))
            self.db_details.tag_configure("db_title", font=("Consolas", fs_title, "bold"))
            self.db_details.tag_configure("db_section", font=("Consolas", fs, "bold"))
        
        # Widget Solveur
        if hasattr(self, 'txt_solver'):
            self.txt_solver.configure(font=("Consolas", fs))
            self.txt_solver.tag_configure("title", font=("Consolas", fs_title, "bold"))
            self.txt_solver.tag_configure("section", font=("Consolas", fs, "bold"))

    def set_ui_scale_from_control(self):
        val = self.zoom_var.get()
        if val == "Auto":
            scale = self.auto_scale_from_display()
        else:
            try:
                scale = float(val)
            except ValueError:
                return
        self.apply_ui_scale(scale)

    def create_inputs(self, parent):
        # Zoom UI selector
        ttk.Label(parent, text="Zoom UI:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.zoom_var = tk.StringVar(value="Auto")
        zoom_combo = ttk.Combobox(parent, textvariable=self.zoom_var, values=self.zoom_options, state="readonly", width=8)
        zoom_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        zoom_combo.bind("<<ComboboxSelected>>", lambda e: self.set_ui_scale_from_control())

        self.param_defs = [
            ("Nom du Moteur", "name", "Moteur_Propane", str),
            ("Oxydant (CEA)", "ox", "O2", str),
            ("Carburant (CEA)", "fuel", "C3H8", str),
            ("Pression Chambre (bar)", "pc", 12.0, float),
            ("Ratio O/F (MR)", "mr", 2.8, float),
            ("Débit Massique (kg/s)", "mdot", 0.5, float),
            ("Contraction Ratio (Ac/At)", "cr", 3.5, float),
            ("Pression Sortie Design (bar)", "pe", 1.013, float),
            ("Angle Entrée Bell (°)", "tn", 25.0, float),
            ("Angle Sortie Bell (°)", "te", 8.0, float),
            ("L* (L-star) (m)", "lstar", 1.0, float),
            ("Pression Ambiante (bar)", "pamb", 1.013, float),
            # --- Paroi ---
            ("Temp. Paroi Max (K)", "twall", 800.0, float),
            ("Épaisseur Paroi (mm)", "wall_thickness", 2.0, float),  # Épaisseur en mm
            ("Conductivité Paroi (W/m-K)", "wall_k", 15.0, float),  # Acier inox ~15, Cuivre ~400, Inconel ~12
            # --- Refroidissement Régénératif ---
            ("Coolant (Auto=fuel)", "coolant_name", "Auto", str),  # Auto, H2O, C3H8, CH4, Custom...
            ("Débit Coolant (Auto=fuel)", "coolant_mdot", "Auto", str),  # Auto ou valeur en kg/s
            ("Coolant Pression (bar)", "coolant_pressure", 15.0, float),  # Pression circuit coolant
            ("Coolant T entrée (K)", "coolant_tin", 293.0, float),  # 20°C par défaut
            ("Coolant T sortie max (K)", "coolant_tout", 350.0, float),  # Avant vaporisation
            ("Marge Sécurité Coolant (%)", "coolant_margin", 20.0, float),  # 20% de marge
            # --- Coolant Custom (si Coolant = Custom) ---
            ("Custom Cp (J/kg-K)", "custom_cp", 2500.0, float),
            ("Custom T ébullition @1bar (K)", "custom_tboil", 350.0, float),
            ("Custom T critique (K)", "custom_tcrit", 500.0, float),
            ("Custom Hvap (kJ/kg)", "custom_hvap", 400.0, float),  # Enthalpie vaporisation
        ]
        
        row = 0
        row = 1  # start after zoom row
        for label, key, default, type_ in self.param_defs:
            lbl = ttk.Label(parent, text=label)
            lbl.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar(value=str(default))
            entry = ttk.Entry(parent, textvariable=var)
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            self.inputs[key] = (var, type_)
            row += 1
            
        ttk.Separator(parent, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1
        
        ttk.Button(parent, text="🔥 CALCULER TOUT (CEA + THERMIQUE)", command=self.run_simulation, style="Primary.TButton").grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
        row += 1
        
        # Boutons de sauvegarde/chargement
        ttk.Button(parent, text="💾 Sauvegarder Paramètres", command=self.save_design, style="Secondary.TButton").grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
        row += 1
        ttk.Button(parent, text="📂 Charger Paramètres", command=self.load_design, style="Success.TButton").grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
        row += 1
        
        # Bouton d'export DXF et graphes
        ttk.Button(parent, text="💾 EXPORTER DXF", command=self.export_dxf, style="Warning.TButton").grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
        row += 1
        ttk.Button(parent, text="📊 Exporter Graphes HD", command=self.export_graphs_hd, style="Primary.TButton").grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")

    def get_val(self, key):
        var, type_ = self.inputs[key]
        return type_(var.get())

    # --- TABS INIT ---
    def init_summary_tab(self):
        """Onglet Résumé - Affiche les résultats des calculs"""
        tk.Frame(self.tab_summary, height=4, bg=self.tab_accent.get("summary", self.accent)).pack(fill=tk.X)
        summary_frame = ttk.Frame(self.tab_summary)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        fs = self.scaled_font_size(13)
        fs_title = self.scaled_font_size(16)
        
        self.txt_summary = tk.Text(
            summary_frame,
            bg=self.bg_surface,
            fg=self.text_primary,
            insertbackground=self.accent,
            font=("Consolas", fs),
            highlightthickness=0,
            bd=0,
        )
        self.txt_summary.pack(fill=tk.BOTH, expand=True)
        
        # === TAGS DE COULEUR STYLE ÉDITEUR DE CODE ===
        # Titres / Sections (comme les mots-clés)
        self.txt_summary.tag_configure("title", foreground="#ff79c6", font=("Consolas", fs_title, "bold"))  # Rose/Magenta
        self.txt_summary.tag_configure("section", foreground="#ffb86c", font=("Consolas", fs, "bold"))  # Orange
        # Labels de paramètres (comme les variables)
        self.txt_summary.tag_configure("label", foreground="#8be9fd")  # Cyan
        # Valeurs numériques (comme les nombres)
        self.txt_summary.tag_configure("number", foreground="#bd93f9")  # Violet
        # Unités (comme les commentaires)
        self.txt_summary.tag_configure("unit", foreground="#6272a4")  # Gris-bleu
        # Valeurs de chaîne (comme les strings)
        self.txt_summary.tag_configure("string", foreground="#f1fa8c")  # Jaune
        # Succès / OK
        self.txt_summary.tag_configure("success", foreground="#50fa7b")  # Vert
        # Avertissement
        self.txt_summary.tag_configure("warning", foreground="#ffb347")  # Orange chaud
        # Erreur / Critique
        self.txt_summary.tag_configure("error", foreground="#ff5555")  # Rouge
        # Séparateurs
        self.txt_summary.tag_configure("separator", foreground="#44475a")  # Gris foncé
        # Symboles spéciaux
        self.txt_summary.tag_configure("symbol", foreground="#ff79c6")  # Rose
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(self.txt_summary, command=self.txt_summary.yview, style="Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_summary.config(yscrollcommand=scrollbar.set)

    def insert_colored_summary(self, summary: str, cooling_status: str, coolant_warning: str):
        """Insère le summary avec coloration syntaxique style éditeur de code."""
        import re
        
        lines = summary.split('\n')
        for line in lines:
            stripped = line.strip()
            
            # Lignes de séparateurs (═══)
            if '═══' in line or '---' in line:
                self.txt_summary.insert(tk.END, line + '\n', 'separator')
                continue
            
            # Titre principal (SITH MISCHUNG...)
            if 'SITH MISCHUNG' in line or 'LIGHT SIDE EDITION' in line:
                self.txt_summary.insert(tk.END, line + '\n', 'title')
                continue
            
            # Sections (--- XXX ---)
            if stripped.startswith('---') and stripped.endswith('---'):
                self.txt_summary.insert(tk.END, line + '\n', 'section')
                continue
            
            # Statuts de refroidissement
            if '✅' in line or 'OK' in line.upper() and 'Refroidissement' in line:
                self.txt_summary.insert(tk.END, line + '\n', 'success')
                continue
            if '⚠️' in line or '❌' in line:
                tag = 'error' if '❌' in line else 'warning'
                self.txt_summary.insert(tk.END, line + '\n', tag)
                continue
            
            # Lignes avec ":" (label : valeur)
            if ':' in line and not stripped.startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    label_part = parts[0] + ':'
                    value_part = parts[1]
                    
                    self.txt_summary.insert(tk.END, label_part, 'label')
                    
                    # Colorer les nombres dans la partie valeur
                    # Pattern pour trouver les nombres (y compris décimaux et négatifs)
                    tokens = re.split(r'(-?\d+\.?\d*)', value_part)
                    for token in tokens:
                        if re.match(r'^-?\d+\.?\d*$', token) and token not in ('', '-'):
                            self.txt_summary.insert(tk.END, token, 'number')
                        elif any(u in token for u in ['mm', 'MW', 'kW', 'K', 's', 'bar', 'kg', 'm/', 'J/', 'W/', 'kN', 'N', '°', '%']):
                            # Unités
                            self.txt_summary.insert(tk.END, token, 'unit')
                        elif any(c in token for c in ['∞', 'ε', 'Ø', 'Δ', '@']):
                            # Symboles spéciaux
                            self.txt_summary.insert(tk.END, token, 'symbol')
                        else:
                            # Texte normal ou strings
                            self.txt_summary.insert(tk.END, token, 'string')
                    
                    self.txt_summary.insert(tk.END, '\n')
                    continue
            
            # Ligne normale
            self.txt_summary.insert(tk.END, line + '\n')

    def insert_colored_cea(self, raw: str):
        """Insère la sortie CEA avec coloration syntaxique."""
        import re
        
        lines = raw.split('\n')
        for line in lines:
            stripped = line.strip()
            
            # Headers (lignes en majuscules ou avec ===)
            if stripped.startswith('*') or stripped.startswith('=') or '***' in line:
                self.txt_cea.insert(tk.END, line + '\n', 'cea_header')
                continue
            
            # Sections principales (THEORETICAL ROCKET, COMBUSTION, etc.)
            if stripped.isupper() and len(stripped) > 3 and not any(c.isdigit() for c in stripped):
                self.txt_cea.insert(tk.END, line + '\n', 'cea_section')
                continue
            
            # Lignes de données avec valeurs numériques
            if '=' in line or any(c.isdigit() for c in line):
                # Détecter les propriétés connues
                props = ['P,', 'T,', 'RHO,', 'H,', 'U,', 'G,', 'S,', 'M,', 'Cp,', 'GAMMAs', 'SON VEL', 
                         'MACH', 'VISC', 'CONDUCTIVITY', 'PRANDTL', 'Ae/At', 'CSTAR', 'CF', 'Ivac', 'Isp']
                is_prop_line = any(prop in line for prop in props)
                
                if is_prop_line:
                    # Coloriser label et valeur
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if re.match(r'^-?\d+\.?\d*[eE]?[+-]?\d*$', part):
                            self.txt_cea.insert(tk.END, part, 'cea_value')
                        elif part.upper() in ['BAR', 'ATM', 'K', 'KG/M**3', 'KJ/KG', 'M/SEC', 'SEC', 'POISE']:
                            self.txt_cea.insert(tk.END, part, 'cea_unit')
                        else:
                            self.txt_cea.insert(tk.END, part, 'cea_property')
                        if i < len(parts) - 1:
                            self.txt_cea.insert(tk.END, ' ')
                    self.txt_cea.insert(tk.END, '\n')
                    continue
                
                # Espèces chimiques (lignes avec formules)
                species_patterns = [r'\*[A-Z][a-z]?', r'CO2', r'H2O', r'OH', r'O2', r'H2', r'N2', r'CO', r'NO']
                if any(re.search(pat, line) for pat in species_patterns) and 'MOLE' not in line.upper():
                    # Coloriser les espèces
                    tokens = line.split()
                    for i, token in enumerate(tokens):
                        if re.match(r'^\*?[A-Z][A-Za-z0-9]*(\([A-Za-z]\))?$', token):
                            self.txt_cea.insert(tk.END, token, 'cea_species')
                        elif re.match(r'^-?\d+\.?\d*[eE]?[+-]?\d*$', token):
                            self.txt_cea.insert(tk.END, token, 'cea_value')
                        else:
                            self.txt_cea.insert(tk.END, token)
                        if i < len(tokens) - 1:
                            self.txt_cea.insert(tk.END, ' ')
                    self.txt_cea.insert(tk.END, '\n')
                    continue
            
            # Ligne normale
            self.txt_cea.insert(tk.END, line + '\n')

    def init_visu_tab(self):
        tk.Frame(self.tab_visu, height=4, bg=self.tab_accent.get("visu", self.accent_alt3)).pack(fill=tk.X)
        self.fig_visu, self.ax_visu = plt.subplots(figsize=(5, 5))
        self.fig_visu.patch.set_facecolor(self.bg_main)
        self.apply_dark_axes(self.ax_visu)
        self.canvas_visu = FigureCanvasTkAgg(self.fig_visu, master=self.tab_visu)
        self.canvas_visu.get_tk_widget().configure(bg=self.bg_main, highlightthickness=0)
        self.canvas_visu.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def init_cea_tab(self):
        tk.Frame(self.tab_cea, height=4, bg=self.tab_accent.get("cea", self.accent_alt2)).pack(fill=tk.X)
        fs = self.scaled_font_size(13)
        self.txt_cea = scrolledtext.ScrolledText(
            self.tab_cea,
            font=("Consolas", fs),
            state='disabled',
            bg=self.bg_surface,
            fg=self.text_primary,
            insertbackground=self.accent,
            highlightthickness=0,
            bd=0,
        )
        self.txt_cea.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tags de coloration CEA style éditeur de code
        self.txt_cea.tag_configure("cea_header", foreground="#ff79c6", font=("Consolas", fs, "bold"))
        self.txt_cea.tag_configure("cea_section", foreground="#ffb86c")
        self.txt_cea.tag_configure("cea_property", foreground="#8be9fd")
        self.txt_cea.tag_configure("cea_value", foreground="#bd93f9")
        self.txt_cea.tag_configure("cea_unit", foreground="#6272a4")
        self.txt_cea.tag_configure("cea_species", foreground="#50fa7b")
        self.txt_cea.tag_configure("cea_comment", foreground="#6272a4", font=("Consolas", fs, "italic"))
        
    def init_thermal_tab(self):
        tk.Frame(self.tab_thermal, height=4, bg=self.tab_accent.get("thermal", self.accent_alt)).pack(fill=tk.X)
        self.fig_thermal, (self.ax_flux, self.ax_temp) = plt.subplots(2, 1, figsize=(6, 6), sharex=True)
        self.fig_thermal.patch.set_facecolor(self.bg_main)
        self.fig_thermal.subplots_adjust(hspace=0.35, left=0.12, right=0.95, top=0.95, bottom=0.1)
        for ax in [self.ax_flux, self.ax_temp]:
            ax.set_facecolor(self.bg_surface)
        self.apply_dark_axes([self.ax_flux, self.ax_temp])
        self.canvas_thermal = FigureCanvasTkAgg(self.fig_thermal, master=self.tab_thermal)
        self.canvas_thermal.get_tk_widget().configure(bg=self.bg_main, highlightthickness=0)
        self.canvas_thermal.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def init_graphs_tab(self):
        tk.Frame(self.tab_graphs, height=4, bg=self.tab_accent.get("graphs", self.accent)).pack(fill=tk.X)
        ctrl_frame = ttk.LabelFrame(self.tab_graphs, text="Configuration Analyse Paramétrique", padding=10)
        ctrl_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Ligne 0 : Catégorie d'analyse
        row0 = ttk.Frame(ctrl_frame)
        row0.pack(fill=tk.X, pady=2)
        
        ttk.Label(row0, text="Catégorie:").pack(side=tk.LEFT)
        self.analysis_categories = [
            "🚀 Performances CEA",
            "🌡️ Thermique Paroi",
            "💧 Refroidissement",
            "📐 Géométrie"
        ]
        self.combo_category = ttk.Combobox(row0, values=self.analysis_categories, state="readonly", width=20)
        self.combo_category.current(0)
        self.combo_category.pack(side=tk.LEFT, padx=5)
        self.combo_category.bind("<<ComboboxSelected>>", self.update_analysis_options)
        
        # Ligne 1 : Mode et Résolution
        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="Mode:").pack(side=tk.LEFT)
        self.combo_mode = ttk.Combobox(row1, values=["2D (Courbe)", "3D (Surface)"], state="readonly", width=12)
        self.combo_mode.current(0)
        self.combo_mode.pack(side=tk.LEFT, padx=5)
        self.combo_mode.bind("<<ComboboxSelected>>", self.update_mode_display)
        
        ttk.Label(row1, text="Résolution:").pack(side=tk.LEFT, padx=(15, 0))
        self.spin_res = ttk.Spinbox(row1, from_=5, to=100, width=5, style="TSpinbox")
        self.spin_res.set(20)
        self.spin_res.pack(side=tk.LEFT, padx=5)
        
        # Ligne 2 : Axes
        row2 = ttk.Frame(ctrl_frame)
        row2.pack(fill=tk.X, pady=5)
        
        # Variables par catégorie
        self.input_vars_by_category = {
            "🚀 Performances CEA": ["Pression Chambre (bar)", "O/F Ratio", "Expansion Ratio (Eps)", "Contraction Ratio", "Pression Ambiante (bar)"],
            "🌡️ Thermique Paroi": ["Épaisseur Paroi (mm)", "Conductivité Paroi (W/m-K)", "Temp. Coolant (K)", "Profondeur Paroi (%)", "Pression Chambre (bar)", "O/F Ratio"],
            "💧 Refroidissement": ["Débit Coolant (kg/s)", "Temp. Entrée Coolant (K)", "Pression Coolant (bar)", "Épaisseur Paroi (mm)"],
            "📐 Géométrie": ["L* (m)", "Contraction Ratio", "Angle Entrée Bell (°)", "Angle Sortie Bell (°)", "Expansion Ratio"]
        }
        
        self.output_vars_by_category = {
            "🚀 Performances CEA": ["ISP Ambiante (s)", "ISP Vide (s)", "Température Chambre (K)", "Température Col (K)", "Température Sortie (K)", "C* (m/s)", "Cf Vide", "Cf Ambiante", "Gamma"],
            "🌡️ Thermique Paroi": ["T Paroi Gaz (K)", "T Paroi Milieu (K)", "T Paroi Coolant (K)", "Profil T dans Paroi (K)", "Flux Max (MW/m²)", "Flux Moyen (MW/m²)", "Puissance Thermique (kW)", "Marge Fusion (%)", "Delta T Paroi (K)"],
            "💧 Refroidissement": ["T Sortie Coolant (K)", "Delta T Coolant (K)", "Puissance Absorbée (kW)", "Marge Ébullition (%)"],
            "📐 Géométrie": ["Longueur Chambre (mm)", "Longueur Convergent (mm)", "Longueur Divergent (mm)", "Longueur Totale (mm)", "Diamètre Col (mm)", "Diamètre Sortie (mm)", "ISP Vide (s)", "ISP Ambiante (s)", "Efficacité Combustion (%)", "C* (m/s)", "Poussée Vide (N)"]
        }
        
        self.input_vars = self.input_vars_by_category["🚀 Performances CEA"]
        self.vars_out = self.output_vars_by_category["🚀 Performances CEA"]
        
        ttk.Label(row2, text="Axe X (Input):").pack(side=tk.LEFT)
        self.combo_x = ttk.Combobox(row2, values=self.input_vars, width=22, state="readonly")
        self.combo_x.current(1)
        self.combo_x.pack(side=tk.LEFT, padx=5)
        
        # Axe Y (caché par défaut, visible seulement en 3D)
        ttk.Label(row2, text="Axe Y (Input):").pack(side=tk.LEFT, padx=(10, 0))
        self.combo_y = ttk.Combobox(row2, values=self.input_vars, width=22, state="readonly")
        self.combo_y.current(0)
        self.combo_y.pack(side=tk.LEFT, padx=5)
        self.label_y = row2.winfo_children()[-2]  # Référence au label "Axe Y"
        
        # Masquer l'axe Y au démarrage (mode 2D par défaut)
        self.combo_y.pack_forget()
        self.label_y.pack_forget()
        
        ttk.Label(row2, text="Sortie (Z):").pack(side=tk.LEFT, padx=(10, 0))
        self.combo_z = ttk.Combobox(row2, values=self.vars_out, width=22, state="readonly")
        self.combo_z.current(0)
        self.combo_z.pack(side=tk.LEFT, padx=5)
        
        # Ligne 3 : Ranges X et Y
        self.f_range = ttk.Frame(ctrl_frame)
        self.f_range.pack(fill=tk.X, pady=2)
        
        ttk.Label(self.f_range, text="Min X:").pack(side=tk.LEFT)
        self.e_xmin = ttk.Entry(self.f_range, width=6)
        self.e_xmin.insert(0, "1.0")
        self.e_xmin.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(self.f_range, text="Max X:").pack(side=tk.LEFT)
        self.e_xmax = ttk.Entry(self.f_range, width=6)
        self.e_xmax.insert(0, "4.0")
        self.e_xmax.pack(side=tk.LEFT, padx=2)
        
        # Champs Min Y et Max Y (cachés par défaut en mode 2D)
        ttk.Label(self.f_range, text="Min Y:").pack(side=tk.LEFT, padx=(10, 0))
        self.e_ymin = ttk.Entry(self.f_range, width=6)
        self.e_ymin.insert(0, "1.5")
        self.e_ymin.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(self.f_range, text="Max Y:").pack(side=tk.LEFT)
        self.e_ymax = ttk.Entry(self.f_range, width=6)
        self.e_ymax.insert(0, "4.0")
        self.e_ymax.pack(side=tk.LEFT, padx=2)
        
        # Stocker les labels pour pouvoir les afficher/masquer
        self.label_ymin = self.f_range.winfo_children()[-4]
        self.label_ymax = self.f_range.winfo_children()[-2]
        
        # Masquer les champs Y au démarrage (mode 2D par défaut)
        self.label_ymin.pack_forget()
        self.e_ymin.pack_forget()
        self.label_ymax.pack_forget()
        self.e_ymax.pack_forget()
        
        ttk.Button(ctrl_frame, text="CALCULER & TRACER", command=self.plot_manager).pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Ligne 4 : Matériaux de référence (pour thermique)
        row4 = ttk.Frame(ctrl_frame)
        row4.pack(fill=tk.X, pady=2)
        
        ttk.Label(row4, text="Matériau Réf:").pack(side=tk.LEFT)
        self.materials_ref = {
            "Acier Inox 316L": {"k": 15, "t_melt": 1673, "color": "gray"},
            "Inconel 625": {"k": 10, "t_melt": 1623, "color": "orange"},
            "Inconel 718": {"k": 11.4, "t_melt": 1609, "color": "darkorange"},
            "Cuivre C10200": {"k": 391, "t_melt": 1356, "color": "brown"},
            "Cuivre-Chrome (CuCrZr)": {"k": 320, "t_melt": 1353, "color": "peru"},
            "Aluminium 6061": {"k": 167, "t_melt": 855, "color": "silver"},
            "Titane Ti-6Al-4V": {"k": 6.7, "t_melt": 1933, "color": "lightblue"},
            "Hastelloy X": {"k": 9.1, "t_melt": 1628, "color": "green"},
            "Niobium C103": {"k": 44, "t_melt": 2623, "color": "purple"},
            "Tungstène": {"k": 173, "t_melt": 3695, "color": "darkblue"},
        }
        self.combo_material = ttk.Combobox(row4, values=list(self.materials_ref.keys()), state="readonly", width=20)
        self.combo_material.current(0)
        self.combo_material.pack(side=tk.LEFT, padx=5)
        
        self.var_show_melt = tk.BooleanVar(value=True)
        ttk.Checkbutton(row4, text="Afficher T fusion", variable=self.var_show_melt).pack(side=tk.LEFT, padx=10)
        
        self.var_multi_materials = tk.BooleanVar(value=False)
        ttk.Checkbutton(row4, text="Comparer matériaux", variable=self.var_multi_materials).pack(side=tk.LEFT, padx=5)
        
        self.progress = ttk.Progressbar(self.tab_graphs, mode='indeterminate')
        self.progress.pack(side=tk.TOP, fill=tk.X, padx=10)
        
        self.fig_graph = plt.Figure(figsize=(5, 4), dpi=100)
        self.fig_graph.patch.set_facecolor(self.bg_main)
        self.canvas_graph = FigureCanvasTkAgg(self.fig_graph, master=self.tab_graphs)
        self.canvas_graph.get_tk_widget().configure(bg=self.bg_main, highlightthickness=0)
        self.canvas_graph.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def apply_dark_axes(self, axes):
        """Applique le thème sombre aux axes matplotlib."""
        if not isinstance(axes, (list, tuple)):
            axes = [axes]
        for ax in axes:
            ax.set_facecolor(self.bg_surface)
            ax.tick_params(colors=self.text_primary)
            if hasattr(ax, "xaxis"):
                ax.xaxis.label.set_color(self.text_primary)
            if hasattr(ax, "yaxis"):
                ax.yaxis.label.set_color(self.text_primary)
            if hasattr(ax, "zaxis"):
                ax.zaxis.label.set_color(self.text_primary)
                ax.zaxis.set_tick_params(colors=self.text_primary)
            if ax.get_title():
                ax.title.set_color(self.text_primary)
            for spine in getattr(ax, "spines", {}).values():
                spine.set_color(self.accent)
            ax.grid(True, color=self.grid_color, alpha=0.35)

    def get_category_color(self):
        palette = {
            "🚀 Performances CEA": self.accent,
            "🌡️ Thermique Paroi": self.accent_alt,
            "💧 Refroidissement": self.accent_alt2,
            "📐 Géométrie": self.accent_alt3,
        }
        return palette.get(self.combo_category.get(), self.accent)

    def init_database_tab(self):
        """Onglet Base de Données - Explorateur de propergols RocketCEA"""
        tk.Frame(self.tab_database, height=4, bg=self.tab_accent.get("database", self.accent_alt4)).pack(fill=tk.X)
        
        # Frame de contrôle en haut
        ctrl_frame = ttk.LabelFrame(self.tab_database, text="🔍 Recherche dans la Base de Données RocketCEA", padding=10)
        ctrl_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Ligne 1: Type et recherche
        row1 = ttk.Frame(ctrl_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="Type:").pack(side=tk.LEFT)
        self.db_type = ttk.Combobox(row1, values=["Tous", "Fuels (Carburants)", "Oxydants", "Coolants Communs"], 
                                     state="readonly", width=18)
        self.db_type.current(0)
        self.db_type.pack(side=tk.LEFT, padx=5)
        self.db_type.bind("<<ComboboxSelected>>", lambda e: self.search_database())
        
        ttk.Label(row1, text="Recherche:").pack(side=tk.LEFT, padx=(15, 0))
        self.db_search = ttk.Entry(row1, width=25)
        self.db_search.pack(side=tk.LEFT, padx=5)
        self.db_search.bind("<KeyRelease>", lambda e: self.search_database())
        
        ttk.Button(row1, text="🔄 Actualiser", command=self.search_database).pack(side=tk.LEFT, padx=10)
        ttk.Button(row1, text="📋 Copier Nom", command=self.copy_selected_name).pack(side=tk.LEFT, padx=5)
        
        # Frame pour la liste et les détails
        content_frame = ttk.Frame(self.tab_database)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Liste des propergols (gauche)
        list_frame = ttk.LabelFrame(content_frame, text="Propergols Disponibles", padding=5)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Treeview avec colonnes
        columns = ("name", "type", "t_ref", "formula")
        self.db_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        self.db_tree.heading("name", text="Nom CEA")
        self.db_tree.heading("type", text="Type")
        self.db_tree.heading("t_ref", text="T_ref (K)")
        self.db_tree.heading("formula", text="Formule/Info")
        
        self.db_tree.column("name", width=120)
        self.db_tree.column("type", width=80)
        self.db_tree.column("t_ref", width=80)
        self.db_tree.column("formula", width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.db_tree.yview)
        self.db_tree.configure(yscrollcommand=scrollbar.set)
        
        self.db_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.db_tree.bind("<<TreeviewSelect>>", self.on_propellant_select)
        
        # Détails du propergol sélectionné (droite)
        detail_frame = ttk.LabelFrame(content_frame, text="Détails du Propergol", padding=10)
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        fs = self.scaled_font_size(13)
        fs_title = self.scaled_font_size(16)
        
        self.db_details = scrolledtext.ScrolledText(
            detail_frame,
            font=("Consolas", fs),
            width=50,
            height=25,
            state='disabled',
            bg=self.bg_surface,
            fg=self.text_primary,
            insertbackground=self.accent,
            highlightthickness=0,
            bd=0,
        )
        self.db_details.pack(fill=tk.BOTH, expand=True)
        
        # Tags de couleur pour la base de données
        self.db_details.tag_configure("db_title", foreground="#ff79c6", font=("Consolas", fs_title, "bold"))
        self.db_details.tag_configure("db_section", foreground="#ffb86c", font=("Consolas", fs, "bold"))
        self.db_details.tag_configure("db_label", foreground="#8be9fd")
        self.db_details.tag_configure("db_number", foreground="#bd93f9")
        self.db_details.tag_configure("db_unit", foreground="#6272a4")
        self.db_details.tag_configure("db_string", foreground="#f1fa8c")
        self.db_details.tag_configure("db_success", foreground="#50fa7b")
        
        # Charger la base de données au démarrage
        self.root.after(100, self.load_database)

    def build_coolants_database(self):
        """Construit la base de données des coolants depuis RocketCEA + manuels"""
        
        # Propriétés thermophysiques connues (Cp liquide, T_crit, viscosité pour h)
        # Format: {nom_cea: {"Cp": J/kg-K, "T_crit": K, "rho": kg/m³, "mu": Pa.s, "k_liq": W/m-K}}
        fuel_props = {
            "RP1": {"Cp": 2000, "T_crit": 678, "rho": 810, "mu": 0.001, "k_liq": 0.12, "T_boil": 490},
            "RP_1": {"Cp": 2000, "T_crit": 678, "rho": 810, "mu": 0.001, "k_liq": 0.12, "T_boil": 490},
            "RP1_NASA": {"Cp": 2000, "T_crit": 678, "rho": 810, "mu": 0.001, "k_liq": 0.12, "T_boil": 490},
            "Kerosene": {"Cp": 2100, "T_crit": 658, "rho": 800, "mu": 0.001, "k_liq": 0.12, "T_boil": 480},
            "JetA": {"Cp": 2100, "T_crit": 670, "rho": 808, "mu": 0.001, "k_liq": 0.12, "T_boil": 478},
            "C3H8": {"Cp": 2500, "T_crit": 370, "rho": 493, "mu": 0.0001, "k_liq": 0.10, "T_boil": 231},
            "Propane": {"Cp": 2500, "T_crit": 370, "rho": 493, "mu": 0.0001, "k_liq": 0.10, "T_boil": 231},
            "CH4": {"Cp": 3500, "T_crit": 191, "rho": 422, "mu": 0.00012, "k_liq": 0.19, "T_boil": 112},
            "LCH4_NASA": {"Cp": 3500, "T_crit": 191, "rho": 422, "mu": 0.00012, "k_liq": 0.19, "T_boil": 112},
            "GCH4": {"Cp": 2200, "T_crit": 191, "rho": 100, "mu": 0.00001, "k_liq": 0.034, "T_boil": 112},
            "H2": {"Cp": 14300, "T_crit": 33, "rho": 71, "mu": 0.000013, "k_liq": 0.10, "T_boil": 20},
            "LH2": {"Cp": 14300, "T_crit": 33, "rho": 71, "mu": 0.000013, "k_liq": 0.10, "T_boil": 20},
            "LH2_NASA": {"Cp": 14300, "T_crit": 33, "rho": 71, "mu": 0.000013, "k_liq": 0.10, "T_boil": 20},
            "GH2": {"Cp": 14300, "T_crit": 33, "rho": 5, "mu": 0.000009, "k_liq": 0.18, "T_boil": 20},
            "GH2_160": {"Cp": 14300, "T_crit": 33, "rho": 10, "mu": 0.000009, "k_liq": 0.18, "T_boil": 20},
            "C2H5OH": {"Cp": 2440, "T_crit": 514, "rho": 789, "mu": 0.001, "k_liq": 0.17, "T_boil": 351},
            "Ethanol": {"Cp": 2440, "T_crit": 514, "rho": 789, "mu": 0.001, "k_liq": 0.17, "T_boil": 351},
            "CH3OH": {"Cp": 2500, "T_crit": 513, "rho": 792, "mu": 0.0006, "k_liq": 0.20, "T_boil": 338},
            "Methanol": {"Cp": 2500, "T_crit": 513, "rho": 792, "mu": 0.0006, "k_liq": 0.20, "T_boil": 338},
            "MMH": {"Cp": 2900, "T_crit": 585, "rho": 878, "mu": 0.0008, "k_liq": 0.22, "T_boil": 360},
            "N2H4": {"Cp": 3100, "T_crit": 653, "rho": 1004, "mu": 0.001, "k_liq": 0.50, "T_boil": 387},
            "UDMH": {"Cp": 2700, "T_crit": 523, "rho": 793, "mu": 0.0005, "k_liq": 0.21, "T_boil": 336},
            "NH3": {"Cp": 4700, "T_crit": 405, "rho": 682, "mu": 0.0002, "k_liq": 0.50, "T_boil": 240},
            "A50": {"Cp": 3000, "T_crit": 600, "rho": 900, "mu": 0.0008, "k_liq": 0.35, "T_boil": 370},
            "M20": {"Cp": 3050, "T_crit": 600, "rho": 950, "mu": 0.001, "k_liq": 0.40, "T_boil": 375},
            "MHF3": {"Cp": 2900, "T_crit": 585, "rho": 890, "mu": 0.0008, "k_liq": 0.22, "T_boil": 360},
            "TURPENTINE": {"Cp": 1800, "T_crit": 620, "rho": 870, "mu": 0.002, "k_liq": 0.13, "T_boil": 433},
            "Gasoline": {"Cp": 2000, "T_crit": 550, "rho": 750, "mu": 0.0004, "k_liq": 0.12, "T_boil": 373},
            "JP4": {"Cp": 2050, "T_crit": 650, "rho": 785, "mu": 0.001, "k_liq": 0.12, "T_boil": 473},
            "JP5": {"Cp": 2000, "T_crit": 675, "rho": 820, "mu": 0.001, "k_liq": 0.12, "T_boil": 523},
            "Butanol": {"Cp": 2400, "T_crit": 563, "rho": 810, "mu": 0.003, "k_liq": 0.15, "T_boil": 390},
            "IPA": {"Cp": 2600, "T_crit": 509, "rho": 786, "mu": 0.002, "k_liq": 0.14, "T_boil": 355},
            "Acetone": {"Cp": 2180, "T_crit": 508, "rho": 790, "mu": 0.0003, "k_liq": 0.16, "T_boil": 329},
            "DEE": {"Cp": 2200, "T_crit": 467, "rho": 713, "mu": 0.0002, "k_liq": 0.13, "T_boil": 308},
            "N2O": {"Cp": 880, "T_crit": 310, "rho": 1220, "mu": 0.00013, "k_liq": 0.12, "T_boil": 185},
            "C2H6": {"Cp": 2400, "T_crit": 305, "rho": 544, "mu": 0.00009, "k_liq": 0.11, "T_boil": 185},
            "C4H10": {"Cp": 2400, "T_crit": 425, "rho": 579, "mu": 0.0002, "k_liq": 0.11, "T_boil": 273},
            "C6H14": {"Cp": 2270, "T_crit": 507, "rho": 660, "mu": 0.0003, "k_liq": 0.12, "T_boil": 342},
        }
        
        ox_props = {
            "LOX": {"Cp": 1700, "T_crit": 155, "rho": 1141, "mu": 0.0002, "k_liq": 0.15, "T_boil": 90},
            "O2": {"Cp": 1700, "T_crit": 155, "rho": 1141, "mu": 0.0002, "k_liq": 0.15, "T_boil": 90},
            "LF2": {"Cp": 1550, "T_crit": 144, "rho": 1510, "mu": 0.0003, "k_liq": 0.16, "T_boil": 85},
            "F2": {"Cp": 1550, "T_crit": 144, "rho": 1510, "mu": 0.0003, "k_liq": 0.16, "T_boil": 85},
            "N2O4": {"Cp": 1580, "T_crit": 431, "rho": 1450, "mu": 0.0004, "k_liq": 0.12, "T_boil": 294},
            "HNO3": {"Cp": 1740, "T_crit": 520, "rho": 1510, "mu": 0.001, "k_liq": 0.35, "T_boil": 356},
            "IRFNA": {"Cp": 1700, "T_crit": 520, "rho": 1550, "mu": 0.001, "k_liq": 0.35, "T_boil": 359},
            "CLF3": {"Cp": 770, "T_crit": 424, "rho": 1770, "mu": 0.0004, "k_liq": 0.10, "T_boil": 285},
            "CLF5": {"Cp": 750, "T_crit": 416, "rho": 1900, "mu": 0.0004, "k_liq": 0.10, "T_boil": 260},
            "H2O2": {"Cp": 2600, "T_crit": 730, "rho": 1450, "mu": 0.001, "k_liq": 0.58, "T_boil": 423},
        }
        
        coolants = {}
        
        # Essayer de charger depuis RocketCEA, sinon utiliser les valeurs manuelles
        try:
            from rocketcea.blends import fuelCards, oxCards, getFuelRefTempDegK, getOxRefTempDegK
            use_cea = True
        except Exception:
            use_cea = False
            fuelCards = {}
            oxCards = {}
        
        # Ajouter les fuels
        for name, props in fuel_props.items():
            t_boil = props["T_boil"]
            if use_cea and name in fuelCards:
                try:
                    t_boil = getFuelRefTempDegK(name)
                except:
                    pass
            
            display_name = f"{name} (Fuel)"
            coolants[display_name] = {
                "Cp": props["Cp"],
                "T_boil": t_boil,
                "T_crit": props["T_crit"],
                "rho": props["rho"],
                "mu": props["mu"],
                "k_liq": props["k_liq"],
                "type": "fuel"
            }
        
        # Ajouter les oxydants
        for name, props in ox_props.items():
            t_boil = props["T_boil"]
            if use_cea and name in oxCards:
                try:
                    t_boil = getOxRefTempDegK(name)
                except:
                    pass
            
            display_name = f"{name} (Ox)"
            coolants[display_name] = {
                "Cp": props["Cp"],
                "T_boil": t_boil,
                "T_crit": props["T_crit"],
                "rho": props["rho"],
                "mu": props["mu"],
                "k_liq": props["k_liq"],
                "type": "ox"
            }
        
        # Coolants classiques non-propulseurs
        coolants["Eau (H2O)"] = {"Cp": 4186, "T_boil": 373, "T_crit": 647, "rho": 1000, "mu": 0.001, "k_liq": 0.60, "type": "coolant"}
        coolants["Glycol (EG)"] = {"Cp": 2400, "T_boil": 470, "T_crit": 645, "rho": 1110, "mu": 0.016, "k_liq": 0.25, "type": "coolant"}
        coolants["Dowtherm A"] = {"Cp": 1800, "T_boil": 530, "T_crit": 770, "rho": 1060, "mu": 0.002, "k_liq": 0.14, "type": "coolant"}
        coolants["Therminol 66"] = {"Cp": 1900, "T_boil": 632, "T_crit": 850, "rho": 1010, "mu": 0.002, "k_liq": 0.12, "type": "coolant"}
        coolants["LN2 (Azote liq.)"] = {"Cp": 2040, "T_boil": 77, "T_crit": 126, "rho": 808, "mu": 0.00016, "k_liq": 0.14, "type": "coolant"}
        
        return coolants

    def init_solver_tab(self):
        """Onglet Solveur Coolant - Trouve les paramètres pour éviter la fusion"""
        tk.Frame(self.tab_solver, height=4, bg=self.tab_accent.get("solver", "#00ffaa")).pack(fill=tk.X)
        
        # === PANNEAU DE CONFIGURATION ===
        config_frame = ttk.LabelFrame(self.tab_solver, text="⚙️ Configuration du Solveur", padding=10)
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Base de données des matériaux avec leurs propriétés
        self.materials_db = {
            "Cuivre (Cu)": {"k": 385, "T_melt": 1358, "T_max": 1100, "rho": 8960},
            "Cuivre-Chrome (CuCr)": {"k": 320, "T_melt": 1350, "T_max": 1050, "rho": 8900},
            "Cuivre-Zirconium (CuZr)": {"k": 340, "T_melt": 1356, "T_max": 1000, "rho": 8920},
            "AlSi10Mg (SLM)": {"k": 130, "T_melt": 870, "T_max": 573, "rho": 2670},
            "Inconel 718": {"k": 11.4, "T_melt": 1609, "T_max": 1200, "rho": 8190},
            "Inconel 625": {"k": 9.8, "T_melt": 1623, "T_max": 1250, "rho": 8440},
            "Acier Inox 316L": {"k": 16.3, "T_melt": 1673, "T_max": 1100, "rho": 8000},
            "Acier Inox 304": {"k": 16.2, "T_melt": 1723, "T_max": 1050, "rho": 7900},
            "Niobium (Nb)": {"k": 53.7, "T_melt": 2750, "T_max": 2200, "rho": 8570},
            "Molybdène (Mo)": {"k": 138, "T_melt": 2896, "T_max": 2400, "rho": 10280},
            "Tungstène (W)": {"k": 173, "T_melt": 3695, "T_max": 3000, "rho": 19300},
            "Titane Ti-6Al-4V": {"k": 6.7, "T_melt": 1933, "T_max": 700, "rho": 4430},
            "Aluminium 6061": {"k": 167, "T_melt": 855, "T_max": 500, "rho": 2700},
            "Graphite (C)": {"k": 120, "T_melt": 3900, "T_max": 3500, "rho": 2200},
            "Rhenium (Re)": {"k": 48, "T_melt": 3459, "T_max": 2800, "rho": 21020},
        }
        
        # Base de données des coolants - sera enrichie avec RocketCEA
        self.coolants_db = self.build_coolants_database()
        
        # Ligne 1: Matériau
        row1 = ttk.Frame(config_frame)
        row1.pack(fill=tk.X, pady=3)
        
        ttk.Label(row1, text="Matériau paroi:").pack(side=tk.LEFT)
        self.solver_material = ttk.Combobox(row1, values=list(self.materials_db.keys()), state="readonly", width=22)
        self.solver_material.current(0)
        self.solver_material.pack(side=tk.LEFT, padx=5)
        self.solver_material.bind("<<ComboboxSelected>>", lambda e: self.update_material_info())
        
        ttk.Label(row1, text="T fusion:").pack(side=tk.LEFT, padx=(15, 0))
        self.lbl_tmelt = ttk.Label(row1, text="1358 K", foreground=self.accent_alt)
        self.lbl_tmelt.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="T max service:").pack(side=tk.LEFT, padx=(15, 0))
        self.lbl_tmax = ttk.Label(row1, text="1100 K", foreground=self.accent_alt2)
        self.lbl_tmax.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="k:").pack(side=tk.LEFT, padx=(15, 0))
        self.lbl_k = ttk.Label(row1, text="385 W/m-K", foreground=self.accent)
        self.lbl_k.pack(side=tk.LEFT, padx=5)
        
        # Ligne 2: Épaisseur et coolant
        row2 = ttk.Frame(config_frame)
        row2.pack(fill=tk.X, pady=3)
        
        ttk.Label(row2, text="Épaisseur min (mm):").pack(side=tk.LEFT)
        self.solver_thickness = ttk.Entry(row2, width=8)
        self.solver_thickness.insert(0, "2.0")
        self.solver_thickness.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Coolant:").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_coolant = ttk.Entry(row2, width=15)
        self.solver_coolant.insert(0, "RP1")
        self.solver_coolant.pack(side=tk.LEFT, padx=5)
        ttk.Label(row2, text="(nom RocketCEA)", foreground=self.text_muted).pack(side=tk.LEFT)
        
        ttk.Label(row2, text="T entrée coolant (K):").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_tcool_in = ttk.Entry(row2, width=8)
        self.solver_tcool_in.insert(0, "300")
        self.solver_tcool_in.pack(side=tk.LEFT, padx=5)
        
        # Ligne 3: Pression coolant et marge
        row3 = ttk.Frame(config_frame)
        row3.pack(fill=tk.X, pady=3)
        
        ttk.Label(row3, text="Pression coolant (bar):").pack(side=tk.LEFT)
        self.solver_pcool = ttk.Entry(row3, width=8)
        self.solver_pcool.insert(0, "30")
        self.solver_pcool.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row3, text="Marge sécurité (%):").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_margin = ttk.Entry(row3, width=8)
        self.solver_margin.insert(0, "20")
        self.solver_margin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row3, text="Flux max estimé (MW/m²):").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_flux = ttk.Entry(row3, width=8)
        self.solver_flux.insert(0, "")
        self.solver_flux.pack(side=tk.LEFT, padx=5)
        ttk.Label(row3, text="(laisser vide = auto)", foreground=self.text_muted).pack(side=tk.LEFT)
        
        # Ligne 3b: Paramètres canaux de refroidissement
        row3b = ttk.Frame(config_frame)
        row3b.pack(fill=tk.X, pady=3)
        
        ttk.Label(row3b, text="Vitesse coolant (m/s):").pack(side=tk.LEFT)
        self.solver_vcool = ttk.Entry(row3b, width=8)
        self.solver_vcool.insert(0, "20")
        self.solver_vcool.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row3b, text="Diam. hydraulique (mm):").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_dh = ttk.Entry(row3b, width=8)
        self.solver_dh.insert(0, "3.0")
        self.solver_dh.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row3b, text="Surface refroidie (m²):").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_area = ttk.Entry(row3b, width=8)
        self.solver_area.insert(0, "0.01")
        self.solver_area.pack(side=tk.LEFT, padx=5)
        ttk.Label(row3b, text="(chambre + col)", foreground=self.text_muted).pack(side=tk.LEFT)
        
        # Ligne 4: Boutons
        row4 = ttk.Frame(config_frame)
        row4.pack(fill=tk.X, pady=8)
        
        ttk.Button(row4, text="🔍 Résoudre", command=self.solve_cooling, style="Success.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(row4, text="📊 Comparer Matériaux", command=self.compare_materials, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(row4, text="🧊 Comparer Coolants", command=self.compare_coolants, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(row4, text="🔥 Carte Thermique", command=self.plot_thermal_map, style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(row4, text="🔄 Utiliser données simulation", command=self.load_from_simulation, style="Warning.TButton").pack(side=tk.LEFT, padx=5)
        
        # === ZONE DE RÉSULTATS ===
        results_frame = ttk.LabelFrame(self.tab_solver, text="📋 Résultats du Solveur", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        fs = self.scaled_font_size(13)
        fs_title = self.scaled_font_size(16)
        
        self.txt_solver = tk.Text(
            results_frame,
            bg=self.bg_surface,
            fg=self.text_primary,
            insertbackground=self.accent,
            font=("Consolas", fs),
            highlightthickness=0,
            bd=0,
        )
        self.txt_solver.pack(fill=tk.BOTH, expand=True)
        
        # Tags de couleur
        self.txt_solver.tag_configure("title", foreground="#ff79c6", font=("Consolas", fs_title, "bold"))
        self.txt_solver.tag_configure("section", foreground="#ffb86c", font=("Consolas", fs, "bold"))
        self.txt_solver.tag_configure("label", foreground="#8be9fd")
        self.txt_solver.tag_configure("number", foreground="#bd93f9")
        self.txt_solver.tag_configure("unit", foreground="#6272a4")
        self.txt_solver.tag_configure("success", foreground="#50fa7b")
        self.txt_solver.tag_configure("warning", foreground="#ffb347")
        self.txt_solver.tag_configure("error", foreground="#ff5555")
        self.txt_solver.tag_configure("separator", foreground="#44475a")
        
        scrollbar = ttk.Scrollbar(self.txt_solver, command=self.txt_solver.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_solver.config(yscrollcommand=scrollbar.set)
        
        # Message initial
        self.txt_solver.insert(tk.END, "🧊 SOLVEUR DE REFROIDISSEMENT\n\n", "title")
        self.txt_solver.insert(tk.END, "Ce solveur calcule les paramètres nécessaires pour éviter la fusion du matériau.\n\n", "label")
        self.txt_solver.insert(tk.END, "1. Sélectionnez un matériau et une épaisseur minimum\n", "label")
        self.txt_solver.insert(tk.END, "2. Choisissez un coolant et ses conditions d'entrée\n", "label")
        self.txt_solver.insert(tk.END, "3. Cliquez sur 'Résoudre' pour trouver une solution\n\n", "label")
        self.txt_solver.insert(tk.END, "💡 Astuce: Lancez d'abord une simulation pour avoir le flux thermique réel.\n", "warning")

    def update_material_info(self):
        """Met à jour l'affichage des propriétés du matériau sélectionné"""
        mat_name = self.solver_material.get()
        if mat_name in self.materials_db:
            mat = self.materials_db[mat_name]
            self.lbl_tmelt.config(text=f"{mat['T_melt']} K")
            self.lbl_tmax.config(text=f"{mat['T_max']} K")
            self.lbl_k.config(text=f"{mat['k']} W/m-K")

    def load_from_simulation(self):
        """Charge les données depuis la dernière simulation"""
        if not self.results:
            messagebox.showwarning("Attention", "Lancez d'abord une simulation!")
            return
        
        loaded = []
        
        # Récupérer le flux max de la simulation
        if "q_max" in self.results:
            self.solver_flux.delete(0, tk.END)
            self.solver_flux.insert(0, f"{self.results['q_max']:.2f}")
            loaded.append(f"Flux max: {self.results['q_max']:.2f} MW/m²")
        
        # Récupérer l'épaisseur
        if "wall_thickness_mm" in self.results:
            self.solver_thickness.delete(0, tk.END)
            self.solver_thickness.insert(0, f"{self.results['wall_thickness_mm']:.1f}")
            loaded.append(f"Épaisseur: {self.results['wall_thickness_mm']:.1f} mm")
        
        # Utiliser la surface refroidie calculée par la simulation
        if "A_cooled" in self.results:
            A_total = self.results["A_cooled"]
            self.solver_area.delete(0, tk.END)
            self.solver_area.insert(0, f"{A_total:.4f}")
            loaded.append(f"Surface: {A_total*1e4:.1f} cm²")
        
        # Charger le coolant (le fuel utilisé dans la simulation)
        if "fuel" in self.results:
            fuel_name = self.results["fuel"]
            self.solver_coolant.delete(0, tk.END)
            self.solver_coolant.insert(0, fuel_name)
            loaded.append(f"Coolant: {fuel_name}")
            
            # Chercher la température d'ébullition
            coolant, coolant_name = self.find_coolant_properties(fuel_name)
            if coolant:
                self.solver_tcool_in.delete(0, tk.END)
                self.solver_tcool_in.insert(0, f"{coolant['T_boil']:.0f}")
                loaded.append(f"T entrée: {coolant['T_boil']:.0f} K")
        
        if loaded:
            messagebox.showinfo("Chargé", "Données de simulation chargées:\n" + "\n".join(loaded))
        else:
            messagebox.showwarning("Attention", "Aucune donnée thermique trouvée dans la simulation.")

    def find_coolant_properties(self, coolant_input):
        """Cherche un coolant dans la base de données par nom (exact ou partiel)"""
        coolant_input = coolant_input.strip().upper()
        
        if not coolant_input:
            return None, None
        
        # Recherche exacte d'abord
        for db_name, db_props in self.coolants_db.items():
            if coolant_input == db_name.upper():
                return db_props, db_name
        
        # Recherche partielle (le nom entré est contenu dans le nom de la base ou vice versa)
        for db_name, db_props in self.coolants_db.items():
            db_upper = db_name.upper()
            # Correspondance partielle
            if coolant_input in db_upper or db_upper in coolant_input:
                return db_props, db_name
            # Correspondance sans caractères spéciaux
            clean_input = ''.join(c for c in coolant_input if c.isalnum())
            clean_db = ''.join(c for c in db_upper if c.isalnum())
            if clean_input in clean_db or clean_db in clean_input:
                return db_props, db_name
        
        # Recherche par formule chimique courante
        aliases = {
            "METHANE": "CH4", "LNG": "CH4",
            "KEROSENE": "RP1", "RP-1": "RP1", "JET-A": "RP1",
            "HYDROGEN": "LH2", "H2": "LH2",
            "OXYGEN": "LOX", "O2": "LOX",
            "ETHANOL": "C2H5OH", "ALCOHOL": "C2H5OH",
            "METHANOL": "CH3OH",
            "PROPANE": "C3H8", "LPG": "C3H8",
            "HYDRAZINE": "N2H4",
            "NTO": "N2O4", "NITROGEN TETROXIDE": "N2O4",
            "NITROUS": "N2O", "NITROUS OXIDE": "N2O",
            "PEROXIDE": "H2O2", "HTP": "H2O2",
            "AMMONIA": "NH3",
            "WATER": "H2O", "EAU": "H2O",
            "GLYCOL": "EG", "ETHYLENE GLYCOL": "EG",
            "NITROGEN": "LN2", "AZOTE": "LN2",
        }
        
        if coolant_input in aliases:
            alias_name = aliases[coolant_input]
            for db_name, db_props in self.coolants_db.items():
                if alias_name.upper() in db_name.upper():
                    return db_props, db_name
        
        return None, None

    def solve_cooling(self):
        """Résout le problème de refroidissement avec modèle thermique complet"""
        self.txt_solver.delete(1.0, tk.END)
        
        try:
            # Récupérer les paramètres
            mat_name = self.solver_material.get()
            mat = self.materials_db[mat_name]
            
            # Chercher le coolant par son nom dans la base de données
            coolant_input = self.solver_coolant.get().strip()
            coolant, coolant_name = self.find_coolant_properties(coolant_input)
            
            if coolant is None:
                self.txt_solver.insert(tk.END, f"❌ Coolant '{coolant_input}' non trouvé dans la base de données!\n\n", "error")
                self.txt_solver.insert(tk.END, "Exemples de coolants valides:\n", "label")
                self.txt_solver.insert(tk.END, "• Fuels: RP1, CH4, LH2, C2H5OH, MMH, N2H4, C3H8\n", "success")
                self.txt_solver.insert(tk.END, "• Oxydants: LOX, N2O4, H2O2, N2O\n", "success")
                self.txt_solver.insert(tk.END, "• Autres: H2O, EG (Glycol), LN2\n", "success")
                return
            
            e_mm = float(self.solver_thickness.get())
            e_m = e_mm / 1000
            T_cool_in = float(self.solver_tcool_in.get())
            P_cool = float(self.solver_pcool.get())
            margin_pct = float(self.solver_margin.get()) / 100
            
            # Flux thermique
            flux_str = self.solver_flux.get().strip()
            if flux_str:
                q_max = float(flux_str) * 1e6  # MW/m² -> W/m²
            elif self.results and "q_max" in self.results:
                q_max = self.results["q_max"] * 1e6
            else:
                q_max = 15e6  # 15 MW/m² estimation
            
            q_max_mw = q_max / 1e6
            
            # Propriétés matériau
            T_melt = mat["T_melt"]
            T_max_service = mat["T_max"]
            k = mat["k"]
            
            # Propriétés coolant
            Cp = coolant["Cp"]
            rho = coolant["rho"]
            mu = coolant.get("mu", 0.001)  # Viscosité dynamique Pa.s
            k_liq = coolant.get("k_liq", 0.1)  # Conductivité thermique W/m-K
            
            # Température d'ébullition à la pression donnée
            # Clausius-Clapeyron simplifié: T_boil ∝ ln(P)
            T_boil_1bar = coolant["T_boil"]
            T_crit = coolant["T_crit"]
            # Approximation: augmentation de ~20-30K par décade de pression
            if P_cool > 1:
                T_boil = T_boil_1bar * (1 + 0.05 * math.log(P_cool))
            else:
                T_boil = T_boil_1bar
            T_boil = min(T_boil, T_crit * 0.99)  # Ne pas dépasser la T critique
            
            # === PARAMÈTRES CANAUX DE REFROIDISSEMENT ===
            try:
                v_cool = float(self.solver_vcool.get())
            except:
                v_cool = 20  # m/s par défaut
            
            try:
                D_h = float(self.solver_dh.get()) / 1000  # mm -> m
            except:
                D_h = 0.003  # 3mm par défaut
            
            try:
                A_cooled = float(self.solver_area.get())
            except:
                A_cooled = 0.01  # m² par défaut
            
            # === MODÈLE THERMIQUE COMPLET ===
            # Calcul du nombre de Reynolds et Prandtl
            Re = (rho * v_cool * D_h) / mu  # Reynolds
            Pr = (mu * Cp) / k_liq  # Prandtl
            
            # Corrélation de Dittus-Boelter (refroidissement)
            if Re > 10000:  # Turbulent
                Nu = 0.023 * (Re ** 0.8) * (Pr ** 0.4)
                h_cool = Nu * (k_liq / D_h)
                regime = "turbulent"
            elif Re > 2300:  # Transitoire
                # Interpolation Gnielinski
                f = (0.79 * math.log(Re) - 1.64) ** (-2)
                Nu = (f/8) * (Re - 1000) * Pr / (1 + 12.7 * (f/8)**0.5 * (Pr**(2/3) - 1))
                Nu = max(Nu, 4.36)
                h_cool = Nu * (k_liq / D_h)
                regime = "transitoire"
            else:  # Laminaire
                Nu = 4.36  # Flux constant
                h_cool = Nu * (k_liq / D_h)
                regime = "laminaire"
            
            # Limiter h à des valeurs réalistes (500 - 150000 W/m²-K)
            h_cool = max(500, min(150000, h_cool))
            
            # === CALCUL DES TEMPÉRATURES ===
            # T_wall_cold = T_coolant + q/h_cool (résistance convective côté froid)
            delta_T_convection = q_max / h_cool
            T_wall_cold = T_cool_in + delta_T_convection
            
            # ΔT à travers la paroi métallique (conduction)
            delta_T_wall = (q_max * e_m) / k
            
            # T_wall_hot = T_wall_cold + ΔT_paroi
            T_wall_hot = T_wall_cold + delta_T_wall
            
            # T max du coolant (à la sortie des canaux)
            T_cool_max = min(T_boil * (1 - margin_pct), T_crit * 0.85)
            
            # === VÉRIFICATIONS ===
            feasible = True
            issues = []
            
            # Check 1: T paroi hot vs T max service
            if T_wall_hot > T_max_service:
                issues.append(f"❌ T paroi hot ({T_wall_hot:.0f} K) > T max service ({T_max_service} K)")
                feasible = False
            
            # Check 2: T paroi hot vs T fusion
            if T_wall_hot > T_melt:
                issues.append(f"💀 T paroi hot ({T_wall_hot:.0f} K) > T FUSION ({T_melt} K) - DESTRUCTION!")
                feasible = False
            
            # Check 3: Coolant ne doit pas bouillir au contact de la paroi
            if T_wall_cold > T_boil:
                issues.append(f"⚠️ T paroi cold ({T_wall_cold:.0f} K) > T ébullition ({T_boil:.0f} K) - Ébullition!")
                if T_wall_cold > T_boil * 1.1:  # > 10% au-dessus = critique
                    feasible = False
            
            # Check 4: T entrée coolant vs T ébullition
            if T_cool_in >= T_boil * 0.9:
                issues.append(f"⚠️ T entrée coolant trop élevée vs T_ébullition")
            
            # Marge de sécurité
            margin_T = T_max_service - T_wall_hot
            if 0 < margin_T < 100 and feasible:
                issues.append(f"⚠️ Marge faible: seulement {margin_T:.0f} K sous T max service")
            
            # === CALCUL DU DÉBIT NÉCESSAIRE ===
            Q_total = q_max * A_cooled  # Puissance thermique totale
            delta_T_coolant = max(1, T_cool_max - T_cool_in)
            
            mdot_needed = Q_total / (Cp * delta_T_coolant)
            
            # Puissance thermique en kW
            Q_total_kW = Q_total / 1000
            
            # === ÉPAISSEUR OPTIMALE ===
            # On veut T_wall_hot = T_max_service avec marge 50K
            # T_wall_hot = T_cool_in + q/h_cool + q*e/k = T_max - 50
            # => e = (k/q) * (T_max - 50 - T_cool_in - q/h_cool)
            target_T_hot = T_max_service - 50
            delta_T_available = target_T_hot - T_cool_in - (q_max / h_cool)
            if delta_T_available > 0:
                e_optimal_m = (k * delta_T_available) / q_max
                e_optimal_mm = e_optimal_m * 1000
            else:
                e_optimal_mm = 0  # Impossible même avec e=0
            
            # Épaisseur max (avant fusion avec marge 100K)
            target_T_melt = T_melt - 100
            delta_T_melt = target_T_melt - T_cool_in - (q_max / h_cool)
            if delta_T_melt > 0:
                e_max_m = (k * delta_T_melt) / q_max
                e_max_mm = e_max_m * 1000
            else:
                e_max_mm = 0
            
            # === AFFICHAGE DES RÉSULTATS ===
            self.txt_solver.insert(tk.END, "═══════════════════════════════════════════\n", "separator")
            self.txt_solver.insert(tk.END, "  🧊 RÉSULTATS DU SOLVEUR COOLANT\n", "title")
            self.txt_solver.insert(tk.END, "═══════════════════════════════════════════\n\n", "separator")
            
            # Configuration
            self.txt_solver.insert(tk.END, "--- CONFIGURATION ---\n", "section")
            self.txt_solver.insert(tk.END, f"Matériau        : ", "label")
            self.txt_solver.insert(tk.END, f"{mat_name}\n", "number")
            self.txt_solver.insert(tk.END, f"Coolant         : ", "label")
            self.txt_solver.insert(tk.END, f"{coolant_name}\n", "number")
            self.txt_solver.insert(tk.END, f"Épaisseur       : ", "label")
            self.txt_solver.insert(tk.END, f"{e_mm:.1f}", "number")
            self.txt_solver.insert(tk.END, " mm\n", "unit")
            self.txt_solver.insert(tk.END, f"Flux max        : ", "label")
            self.txt_solver.insert(tk.END, f"{q_max_mw:.2f}", "number")
            self.txt_solver.insert(tk.END, " MW/m²\n", "unit")
            self.txt_solver.insert(tk.END, f"Surface refroidie: ", "label")
            self.txt_solver.insert(tk.END, f"{A_cooled*1e4:.1f}", "number")
            self.txt_solver.insert(tk.END, " cm²\n\n", "unit")
            
            # Propriétés coolant et transfert thermique
            self.txt_solver.insert(tk.END, "--- TRANSFERT THERMIQUE COOLANT ---\n", "section")
            self.txt_solver.insert(tk.END, f"Vitesse coolant : ", "label")
            self.txt_solver.insert(tk.END, f"{v_cool:.1f}", "number")
            self.txt_solver.insert(tk.END, " m/s\n", "unit")
            self.txt_solver.insert(tk.END, f"Diam. hydraul.  : ", "label")
            self.txt_solver.insert(tk.END, f"{D_h*1000:.1f}", "number")
            self.txt_solver.insert(tk.END, " mm\n", "unit")
            self.txt_solver.insert(tk.END, f"Reynolds        : ", "label")
            self.txt_solver.insert(tk.END, f"{Re:.0f}", "number")
            self.txt_solver.insert(tk.END, f" ({regime})\n", "unit")
            self.txt_solver.insert(tk.END, f"Prandtl         : ", "label")
            self.txt_solver.insert(tk.END, f"{Pr:.2f}", "number")
            self.txt_solver.insert(tk.END, "\n", "unit")
            self.txt_solver.insert(tk.END, f"Nusselt         : ", "label")
            self.txt_solver.insert(tk.END, f"{Nu:.1f}", "number")
            self.txt_solver.insert(tk.END, "\n", "unit")
            self.txt_solver.insert(tk.END, f"h_coolant       : ", "label")
            self.txt_solver.insert(tk.END, f"{h_cool:.0f}", "number")
            self.txt_solver.insert(tk.END, " W/m²-K\n", "unit")
            self.txt_solver.insert(tk.END, f"ΔT convection   : ", "label")
            self.txt_solver.insert(tk.END, f"{delta_T_convection:.0f}", "number")
            self.txt_solver.insert(tk.END, " K (q/h)\n\n", "unit")
            
            # Analyse thermique paroi
            self.txt_solver.insert(tk.END, "--- ANALYSE THERMIQUE PAROI ---\n", "section")
            self.txt_solver.insert(tk.END, f"T fusion mat.   : ", "label")
            self.txt_solver.insert(tk.END, f"{T_melt}", "number")
            self.txt_solver.insert(tk.END, " K\n", "unit")
            self.txt_solver.insert(tk.END, f"T max service   : ", "label")
            self.txt_solver.insert(tk.END, f"{T_max_service}", "number")
            self.txt_solver.insert(tk.END, " K\n", "unit")
            self.txt_solver.insert(tk.END, f"ΔT paroi        : ", "label")
            self.txt_solver.insert(tk.END, f"{delta_T_wall:.0f}", "number")
            self.txt_solver.insert(tk.END, " K (q*e/k)\n", "unit")
            self.txt_solver.insert(tk.END, f"T paroi cold    : ", "label")
            self.txt_solver.insert(tk.END, f"{T_wall_cold:.0f}", "number")
            self.txt_solver.insert(tk.END, f" K (T_cool + ΔT_conv)\n", "unit")
            self.txt_solver.insert(tk.END, f"T paroi hot     : ", "label")
            self.txt_solver.insert(tk.END, f"{T_wall_hot:.0f}", "number")
            self.txt_solver.insert(tk.END, " K (calculé)\n", "unit")
            self.txt_solver.insert(tk.END, f"Marge sécurité  : ", "label")
            if margin_T > 0:
                self.txt_solver.insert(tk.END, f"{margin_T:.0f}", "number")
            else:
                self.txt_solver.insert(tk.END, f"{margin_T:.0f}", "error")
            self.txt_solver.insert(tk.END, f" K sous T max\n\n", "unit")
            
            # Coolant
            self.txt_solver.insert(tk.END, "--- COOLANT ---\n", "section")
            self.txt_solver.insert(tk.END, f"T entrée        : ", "label")
            self.txt_solver.insert(tk.END, f"{T_cool_in:.0f}", "number")
            self.txt_solver.insert(tk.END, " K\n", "unit")
            self.txt_solver.insert(tk.END, f"T ébull. @{P_cool:.0f}bar : ", "label")
            self.txt_solver.insert(tk.END, f"{T_boil:.0f}", "number")
            self.txt_solver.insert(tk.END, " K\n", "unit")
            self.txt_solver.insert(tk.END, f"T critique      : ", "label")
            self.txt_solver.insert(tk.END, f"{T_crit:.0f}", "number")
            self.txt_solver.insert(tk.END, " K\n", "unit")
            self.txt_solver.insert(tk.END, f"T max sortie    : ", "label")
            self.txt_solver.insert(tk.END, f"{T_cool_max:.0f}", "number")
            self.txt_solver.insert(tk.END, f" K (avec marge {margin_pct*100:.0f}%)\n", "unit")
            self.txt_solver.insert(tk.END, f"Puiss. thermique: ", "label")
            self.txt_solver.insert(tk.END, f"{Q_total_kW:.1f}", "number")
            self.txt_solver.insert(tk.END, " kW\n", "unit")
            self.txt_solver.insert(tk.END, f"ΔT coolant max  : ", "label")
            self.txt_solver.insert(tk.END, f"{delta_T_coolant:.0f}", "number")
            self.txt_solver.insert(tk.END, " K\n", "unit")
            self.txt_solver.insert(tk.END, f"Débit estimé    : ", "label")
            if mdot_needed < float('inf'):
                self.txt_solver.insert(tk.END, f"{mdot_needed:.4f}", "number")
                self.txt_solver.insert(tk.END, " kg/s", "unit")
                self.txt_solver.insert(tk.END, f" ({mdot_needed*1000:.1f} g/s)\n\n", "unit")
            else:
                self.txt_solver.insert(tk.END, "IMPOSSIBLE\n\n", "error")
            
            # Recommandations
            self.txt_solver.insert(tk.END, "--- RECOMMANDATIONS ---\n", "section")
            self.txt_solver.insert(tk.END, f"Épaisseur optimale : ", "label")
            if e_optimal_mm > 0:
                self.txt_solver.insert(tk.END, f"{e_optimal_mm:.1f}", "number")
                self.txt_solver.insert(tk.END, " mm\n", "unit")
            else:
                self.txt_solver.insert(tk.END, "N/A (flux trop élevé)\n", "error")
            self.txt_solver.insert(tk.END, f"Épaisseur max      : ", "label")
            if e_max_mm > 0:
                self.txt_solver.insert(tk.END, f"{e_max_mm:.1f}", "number")
                self.txt_solver.insert(tk.END, " mm (avant fusion)\n\n", "unit")
            else:
                self.txt_solver.insert(tk.END, "N/A\n\n", "error")
            
            # === SECTION ABLATION / ÉPAISSEUR SACRIFICIELLE ===
            self.txt_solver.insert(tk.END, "--- 🔥 ANALYSE ABLATION ---\n", "section")
            
            # Calcul de l'épaisseur qui fond si e > e_max
            if e_max_mm > 0 and e_mm > e_max_mm:
                e_sacrificielle = e_mm - e_max_mm
                self.txt_solver.insert(tk.END, f"⚠️ Épaisseur actuelle ({e_mm:.1f}mm) > épaisseur max ({e_max_mm:.1f}mm)\n", "warning")
                self.txt_solver.insert(tk.END, f"🔥 ABLATION PRÉVUE  : ", "label")
                self.txt_solver.insert(tk.END, f"{e_sacrificielle:.2f}", "error")
                self.txt_solver.insert(tk.END, " mm vont fondre!\n", "error")
                
                # Masse perdue
                rho_mat = mat.get("rho", 8000)  # kg/m³
                masse_perdue = rho_mat * A_cooled * (e_sacrificielle / 1000)  # kg
                self.txt_solver.insert(tk.END, f"💀 Masse perdue     : ", "label")
                self.txt_solver.insert(tk.END, f"{masse_perdue*1000:.1f}", "error")
                self.txt_solver.insert(tk.END, " g\n", "unit")
                
                # Épaisseur finale après ablation
                e_finale = e_max_mm
                self.txt_solver.insert(tk.END, f"📐 Épaisseur finale : ", "label")
                self.txt_solver.insert(tk.END, f"{e_finale:.1f}", "number")
                self.txt_solver.insert(tk.END, " mm (après équilibre)\n", "unit")
                
                # Recalculer T_wall_hot finale
                e_finale_m = e_finale / 1000
                delta_T_wall_finale = (q_max * e_finale_m) / k
                T_wall_hot_finale = T_wall_cold + delta_T_wall_finale
                self.txt_solver.insert(tk.END, f"🌡️ T paroi finale   : ", "label")
                self.txt_solver.insert(tk.END, f"{T_wall_hot_finale:.0f}", "number")
                self.txt_solver.insert(tk.END, f" K (= T_melt - 100K)\n", "unit")
                
            elif e_max_mm > 0:
                marge_epaisseur = e_max_mm - e_mm
                self.txt_solver.insert(tk.END, f"✅ Pas d'ablation prévue\n", "success")
                self.txt_solver.insert(tk.END, f"Marge épaisseur : ", "label")
                self.txt_solver.insert(tk.END, f"+{marge_epaisseur:.1f}", "success")
                self.txt_solver.insert(tk.END, " mm avant fusion\n", "unit")
            else:
                self.txt_solver.insert(tk.END, f"💀 ABLATION TOTALE - Le flux est trop élevé!\n", "error")
                self.txt_solver.insert(tk.END, f"Même avec e=0, la paroi fondrait.\n", "error")
                self.txt_solver.insert(tk.END, f"Il faut améliorer le refroidissement (h_cool).\n", "warning")
            
            self.txt_solver.insert(tk.END, "\n", "unit")
            
            # Verdict
            self.txt_solver.insert(tk.END, "═══════════════════════════════════════════\n", "separator")
            if feasible and not issues:
                self.txt_solver.insert(tk.END, "✅ SOLUTION VIABLE\n", "success")
                self.txt_solver.insert(tk.END, f"Le {mat_name} avec {e_mm:.1f} mm peut supporter ce flux\n", "success")
                self.txt_solver.insert(tk.END, f"avec du {coolant_name} comme refroidissement.\n", "success")
            elif feasible and issues:
                self.txt_solver.insert(tk.END, "⚠️ SOLUTION POSSIBLE AVEC PRÉCAUTIONS\n", "warning")
                for issue in issues:
                    self.txt_solver.insert(tk.END, f"{issue}\n", "warning")
            else:
                self.txt_solver.insert(tk.END, "❌ SOLUTION NON VIABLE\n", "error")
                for issue in issues:
                    self.txt_solver.insert(tk.END, f"{issue}\n", "error")
                self.txt_solver.insert(tk.END, "\nSuggestions:\n", "label")
                
                # Suggestions spécifiques basées sur le problème
                if e_optimal_mm > 0 and e_mm > e_optimal_mm:
                    self.txt_solver.insert(tk.END, f"• Réduire l'épaisseur à {e_optimal_mm:.1f} mm (optimale)\n", "success")
                elif e_optimal_mm <= 0:
                    self.txt_solver.insert(tk.END, "• ⚠️ Flux trop élevé même avec e=0, augmenter h_cool!\n", "warning")
                    self.txt_solver.insert(tk.END, f"• Augmenter vitesse coolant (actuel: {v_cool:.0f} m/s)\n", "label")
                    self.txt_solver.insert(tk.END, f"• Réduire diamètre canaux (actuel: {D_h*1000:.1f} mm)\n", "label")
                
                if delta_T_convection > delta_T_wall:
                    self.txt_solver.insert(tk.END, "• Le ΔT convection domine → améliorer h_cool\n", "label")
                    # Calculer la vitesse nécessaire
                    h_needed = q_max / (T_max_service - T_cool_in - delta_T_wall - 50)
                    if h_needed > 0:
                        self.txt_solver.insert(tk.END, f"• h_cool nécessaire: {h_needed:.0f} W/m²-K\n", "number")
                
                self.txt_solver.insert(tk.END, "• Matériaux à haute conductivité: Cuivre, Molybdène\n", "label")
                
                # Trouver le meilleur coolant
                best_cp = max(self.coolants_db.items(), key=lambda x: x[1]["Cp"])
                self.txt_solver.insert(tk.END, f"• Meilleur Cp: {best_cp[0]} ({best_cp[1]['Cp']} J/kg-K)\n", "label")
            
            self.txt_solver.insert(tk.END, "═══════════════════════════════════════════\n", "separator")
            
        except Exception as e:
            self.txt_solver.insert(tk.END, f"❌ ERREUR: {str(e)}\n", "error")
            import traceback
            self.txt_solver.insert(tk.END, traceback.format_exc(), "error")

    def compare_materials(self):
        """Compare tous les matériaux pour le flux actuel"""
        self.txt_solver.delete(1.0, tk.END)
        
        try:
            flux_str = self.solver_flux.get().strip()
            if flux_str:
                q_max = float(flux_str) * 1e6
            elif self.results and "q_max" in self.results:
                q_max = self.results["q_max"] * 1e6
            else:
                q_max = 15e6
            
            e_mm = float(self.solver_thickness.get())
            e_m = e_mm / 1000
            T_cool_in = float(self.solver_tcool_in.get())
            
            self.txt_solver.insert(tk.END, "═══════════════════════════════════════════\n", "separator")
            self.txt_solver.insert(tk.END, "  📊 COMPARAISON DES MATÉRIAUX\n", "title")
            self.txt_solver.insert(tk.END, "═══════════════════════════════════════════\n\n", "separator")
            
            self.txt_solver.insert(tk.END, f"Flux: {q_max/1e6:.2f} MW/m² | Épaisseur: {e_mm:.1f} mm | T coolant: {T_cool_in:.0f} K\n\n", "label")
            
            self.txt_solver.insert(tk.END, f"{'Matériau':<25} {'k(W/mK)':<10} {'T_melt':<8} {'ΔT_paroi':<10} {'T_cold_req':<12} {'Statut'}\n", "section")
            self.txt_solver.insert(tk.END, "─" * 85 + "\n", "separator")
            
            results = []
            for name, mat in self.materials_db.items():
                delta_T = (q_max * e_m) / mat["k"]
                T_cold_needed = mat["T_max"] - delta_T
                
                if T_cold_needed >= T_cool_in + 50:
                    status = "✅ OK"
                    tag = "success"
                elif T_cold_needed >= T_cool_in:
                    status = "⚠️ Limite"
                    tag = "warning"
                else:
                    status = "❌ Non"
                    tag = "error"
                
                results.append((name, mat["k"], mat["T_melt"], delta_T, T_cold_needed, status, tag))
            
            # Trier par T_cold_needed décroissant (meilleur en premier)
            results.sort(key=lambda x: x[4], reverse=True)
            
            for name, k, T_melt, delta_T, T_cold, status, tag in results:
                line = f"{name:<25} {k:<10.1f} {T_melt:<8} {delta_T:<10.0f} {T_cold:<12.0f} "
                self.txt_solver.insert(tk.END, line, "label")
                self.txt_solver.insert(tk.END, f"{status}\n", tag)
            
        except Exception as e:
            self.txt_solver.insert(tk.END, f"❌ ERREUR: {str(e)}\n", "error")

    def compare_coolants(self):
        """Compare tous les coolants pour la configuration actuelle"""
        self.txt_solver.delete(1.0, tk.END)
        
        try:
            mat_name = self.solver_material.get()
            mat = self.materials_db[mat_name]
            
            flux_str = self.solver_flux.get().strip()
            if flux_str:
                q_max = float(flux_str) * 1e6
            elif self.results and "q_max" in self.results:
                q_max = self.results["q_max"] * 1e6
            else:
                q_max = 15e6
            
            e_mm = float(self.solver_thickness.get())
            e_m = e_mm / 1000
            T_cool_in = float(self.solver_tcool_in.get())
            P_cool = float(self.solver_pcool.get())
            
            delta_T_wall = (q_max * e_m) / mat["k"]
            T_wall_cold = mat["T_max"] - delta_T_wall
            
            self.txt_solver.insert(tk.END, "═══════════════════════════════════════════\n", "separator")
            self.txt_solver.insert(tk.END, "  🧊 COMPARAISON DES COOLANTS\n", "title")
            self.txt_solver.insert(tk.END, "═══════════════════════════════════════════\n\n", "separator")
            
            self.txt_solver.insert(tk.END, f"Matériau: {mat_name} | Flux: {q_max/1e6:.2f} MW/m²\n", "label")
            self.txt_solver.insert(tk.END, f"T paroi froide nécessaire: {T_wall_cold:.0f} K\n\n", "label")
            
            self.txt_solver.insert(tk.END, f"{'Coolant':<22} {'Cp(J/kgK)':<10} {'T_boil':<8} {'T_crit':<8} {'Marge':<10} {'Statut'}\n", "section")
            self.txt_solver.insert(tk.END, "─" * 75 + "\n", "separator")
            
            results = []
            for name, cool in self.coolants_db.items():
                T_boil = cool["T_boil"] + 20 * math.log10(max(1, P_cool))
                margin = T_boil - T_wall_cold
                
                if margin > 100:
                    status = "✅ Excellent"
                    tag = "success"
                elif margin > 50:
                    status = "✅ OK"
                    tag = "success"
                elif margin > 0:
                    status = "⚠️ Limite"
                    tag = "warning"
                else:
                    status = "❌ Ébullition"
                    tag = "error"
                
                results.append((name, cool["Cp"], T_boil, cool["T_crit"], margin, status, tag))
            
            # Trier par marge décroissante
            results.sort(key=lambda x: x[4], reverse=True)
            
            for name, cp, T_boil, T_crit, margin, status, tag in results:
                line = f"{name:<22} {cp:<10} {T_boil:<8.0f} {T_crit:<8} {margin:<10.0f} "
                self.txt_solver.insert(tk.END, line, "label")
                self.txt_solver.insert(tk.END, f"{status}\n", tag)
            
        except Exception as e:
            self.txt_solver.insert(tk.END, f"❌ ERREUR: {str(e)}\n", "error")
    
    def plot_thermal_map(self):
        """Affiche la carte thermique avec étude paramétrique en épaisseur"""
        if not self.results or "thermal_profile" not in self.results:
            messagebox.showwarning("Attention", "Lancez d'abord une simulation CEA pour avoir les données thermiques!")
            return
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.colors import LinearSegmentedColormap, Normalize
            from matplotlib.patches import Rectangle
            import matplotlib.patches as mpatches
            
            # Récupérer les données de base
            profile = self.results["thermal_profile"]
            X_mm = np.array(profile["X_mm"])
            Y_mm = np.array(profile["Y_mm"])
            Flux_MW = np.array(profile["Flux_MW"])  # MW/m²
            T_wall_cold = profile["T_wall_cold"]  # T côté coolant (K)
            hg_throat = profile["hg_throat"]  # Coefficient de transfert au col
            
            # Matériau sélectionné
            mat_name = self.solver_material.get()
            mat = self.materials_db[mat_name]
            T_melt = mat["T_melt"]
            T_max_service = mat["T_max"]
            k_mat = mat["k"]  # Conductivité thermique W/m-K
            
            # Plage d'épaisseurs à tester (0.5mm à 15mm)
            thicknesses = np.linspace(0.5, 15, 30)
            
            # Calculer T_wall_hot pour chaque épaisseur et chaque position
            # T_wall_hot = T_wall_cold + (q * e) / k
            # où q est le flux en W/m², e en m, k en W/m-K
            
            n_positions = len(X_mm)
            n_thicknesses = len(thicknesses)
            
            # Matrice de températures [position x épaisseur]
            T_matrix = np.zeros((n_positions, n_thicknesses))
            
            for j, e_mm in enumerate(thicknesses):
                e_m = e_mm / 1000  # Convertir en m
                for i in range(n_positions):
                    q_wm2 = Flux_MW[i] * 1e6  # MW/m² -> W/m²
                    delta_T = (q_wm2 * e_m) / k_mat
                    T_matrix[i, j] = T_wall_cold + delta_T
            
            # Trouver l'épaisseur critique (où ça fond) pour chaque position
            e_melt = np.zeros(n_positions)
            e_max_service = np.zeros(n_positions)
            
            for i in range(n_positions):
                # Épaisseur où T = T_melt
                q_wm2 = Flux_MW[i] * 1e6
                if q_wm2 > 0:
                    e_melt[i] = (T_melt - T_wall_cold) * k_mat / q_wm2 * 1000  # en mm
                    e_max_service[i] = (T_max_service - T_wall_cold) * k_mat / q_wm2 * 1000
                else:
                    e_melt[i] = 999
                    e_max_service[i] = 999
            
            # Créer la figure
            fig = plt.figure(figsize=(16, 12), facecolor=self.bg_main)
            
            # Layout: 2x2
            ax1 = fig.add_subplot(2, 2, 1)  # Carte thermique position x épaisseur
            ax2 = fig.add_subplot(2, 2, 2)  # Épaisseur critique vs position
            ax3 = fig.add_subplot(2, 2, 3)  # Profil moteur avec couleur
            ax4 = fig.add_subplot(2, 2, 4)  # Tableau récapitulatif
            
            for ax in [ax1, ax2, ax3, ax4]:
                ax.set_facecolor(self.bg_surface)
                ax.tick_params(colors=self.text_primary)
                for spine in ax.spines.values():
                    spine.set_color(self.grid_color)
            
            # === GRAPHE 1: Carte thermique (heatmap) ===
            # Colormap: bleu (froid) -> vert -> jaune -> orange -> rouge (chaud)
            colors_thermal = ['#0066ff', '#00cc66', '#ffff00', '#ff8800', '#ff0000', '#ff00ff']
            cmap = LinearSegmentedColormap.from_list('thermal', colors_thermal)
            
            # Normaliser par T_melt
            T_ratio = T_matrix / T_melt
            
            im = ax1.imshow(T_ratio.T, aspect='auto', origin='lower', cmap=cmap,
                           extent=[X_mm.min(), X_mm.max(), thicknesses.min(), thicknesses.max()],
                           vmin=0, vmax=1.3)
            
            # Lignes de contour
            cs1 = ax1.contour(X_mm, thicknesses, T_ratio.T, levels=[T_max_service/T_melt], 
                             colors=['orange'], linewidths=2, linestyles='--')
            cs2 = ax1.contour(X_mm, thicknesses, T_ratio.T, levels=[1.0], 
                             colors=['red'], linewidths=3)
            
            ax1.clabel(cs1, fmt=f'T_max ({T_max_service}K)', fontsize=9, colors='orange')
            ax1.clabel(cs2, fmt='FUSION', fontsize=10, colors='red')
            
            cbar = fig.colorbar(im, ax=ax1, label='T / T_fusion')
            cbar.ax.yaxis.label.set_color(self.text_primary)
            cbar.ax.tick_params(colors=self.text_primary)
            
            ax1.set_xlabel('Position axiale (mm)', color=self.text_primary)
            ax1.set_ylabel('Épaisseur paroi (mm)', color=self.text_primary)
            ax1.set_title(f'🔥 CARTE THERMIQUE - {mat_name}', color=self.text_primary, fontsize=12, fontweight='bold')
            ax1.axvline(0, color='cyan', linestyle=':', alpha=0.7, linewidth=1)
            ax1.text(0, thicknesses.max() * 0.95, 'COL', color='cyan', ha='center', fontsize=9)
            
            # === GRAPHE 2: Épaisseur critique vs position ===
            ax2.fill_between(X_mm, 0, e_max_service, color='green', alpha=0.3, label='Zone OK')
            ax2.fill_between(X_mm, e_max_service, e_melt, color='orange', alpha=0.3, label='Zone limite')
            ax2.fill_between(X_mm, e_melt, 20, color='red', alpha=0.3, label='Zone FUSION')
            
            ax2.plot(X_mm, e_melt, 'r-', linewidth=2, label=f'Épaisseur FUSION ({T_melt}K)')
            ax2.plot(X_mm, e_max_service, 'orange', linewidth=2, linestyle='--', label=f'Épaisseur T_max ({T_max_service}K)')
            
            # Marquer l'épaisseur actuelle
            e_current = float(self.solver_thickness.get())
            ax2.axhline(e_current, color='cyan', linewidth=2, linestyle='-', label=f'Épaisseur actuelle ({e_current:.1f}mm)')
            
            # Point critique (min)
            idx_min = np.argmin(e_melt)
            ax2.plot(X_mm[idx_min], e_melt[idx_min], 'ro', markersize=10)
            ax2.annotate(f'Min: {e_melt[idx_min]:.1f}mm\n(x={X_mm[idx_min]:.0f}mm)',
                        xy=(X_mm[idx_min], e_melt[idx_min]),
                        xytext=(X_mm[idx_min] + 10, e_melt[idx_min] + 2),
                        fontsize=10, color='red', fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color='red'))
            
            ax2.set_xlabel('Position axiale (mm)', color=self.text_primary)
            ax2.set_ylabel('Épaisseur paroi (mm)', color=self.text_primary)
            ax2.set_title('📏 ÉPAISSEUR CRITIQUE vs POSITION', color=self.text_primary, fontsize=12, fontweight='bold')
            ax2.set_ylim(0, min(20, max(e_melt) * 1.5))
            ax2.set_xlim(X_mm.min(), X_mm.max())
            ax2.legend(loc='upper right', fontsize=9, facecolor=self.bg_surface, labelcolor=self.text_primary)
            ax2.grid(True, alpha=0.2)
            ax2.axvline(0, color='cyan', linestyle=':', alpha=0.7)
            
            # === GRAPHE 3: Profil moteur avec couleur de flux ===
            # Normaliser le flux pour la couleur
            flux_norm = Flux_MW / max(Flux_MW)
            
            # Dessiner le profil comme une série de rectangles colorés
            # Exagérer l'épaisseur pour la visibilité (facteur 10)
            e_exag = e_current * 5  # Facteur d'exagération
            
            for i in range(len(X_mm) - 1):
                # Couleur basée sur le ratio T/T_melt pour l'épaisseur actuelle
                q_wm2 = Flux_MW[i] * 1e6
                T_hot = T_wall_cold + (q_wm2 * e_current/1000) / k_mat
                ratio = T_hot / T_melt
                
                # Couleur
                if ratio >= 1.0:
                    color = '#ff00ff'  # Magenta = fusion
                elif ratio >= T_max_service/T_melt:
                    color = '#ff4400'  # Rouge-orange = danger
                elif ratio >= 0.7:
                    color = '#ffaa00'  # Orange = attention
                elif ratio >= 0.5:
                    color = '#ffff00'  # Jaune
                else:
                    color = '#00cc66'  # Vert = OK
                
                # Rectangle pour la paroi (exagérée)
                width = X_mm[i+1] - X_mm[i]
                
                # Partie supérieure
                rect_top = Rectangle((X_mm[i], Y_mm[i]), width, e_exag, 
                                     facecolor=color, edgecolor='none', alpha=0.8)
                ax3.add_patch(rect_top)
                
                # Partie inférieure (miroir)
                rect_bot = Rectangle((X_mm[i], -Y_mm[i] - e_exag), width, e_exag,
                                     facecolor=color, edgecolor='none', alpha=0.8)
                ax3.add_patch(rect_bot)
            
            # Profil interne
            ax3.plot(X_mm, Y_mm, 'white', linewidth=1.5)
            ax3.plot(X_mm, -Y_mm, 'white', linewidth=1.5)
            
            # Profil externe
            ax3.plot(X_mm, Y_mm + e_exag, '--', color='#888888', linewidth=1)
            ax3.plot(X_mm, -Y_mm - e_exag, '--', color='#888888', linewidth=1)
            
            ax3.set_xlim(X_mm.min() - 5, X_mm.max() + 5)
            ax3.set_ylim(-Y_mm.max() - e_exag - 5, Y_mm.max() + e_exag + 10)
            ax3.set_xlabel('Position axiale (mm)', color=self.text_primary)
            ax3.set_ylabel('Rayon (mm) - épaisseur exagérée x5', color=self.text_primary)
            ax3.set_title(f'🚀 PROFIL THERMIQUE (e={e_current}mm)', color=self.text_primary, fontsize=12, fontweight='bold')
            ax3.set_aspect('equal')
            ax3.axvline(0, color='cyan', linestyle=':', alpha=0.5)
            ax3.text(0, Y_mm.max() + e_exag + 3, 'COL', color='cyan', ha='center', fontsize=9)
            
            # Légende couleurs
            legend_elements = [
                mpatches.Patch(facecolor='#00cc66', label='OK (<50% Tmelt)'),
                mpatches.Patch(facecolor='#ffff00', label='50-70% Tmelt'),
                mpatches.Patch(facecolor='#ffaa00', label='70-90% Tmelt'),
                mpatches.Patch(facecolor='#ff4400', label=f'>T_max ({T_max_service}K)'),
                mpatches.Patch(facecolor='#ff00ff', label='FUSION!'),
            ]
            ax3.legend(handles=legend_elements, loc='upper right', fontsize=8, 
                      facecolor=self.bg_surface, labelcolor=self.text_primary)
            
            # === GRAPHE 4: Tableau récapitulatif ===
            ax4.axis('off')
            
            # Calculs
            e_melt_min = min(e_melt)
            e_max_min = min(e_max_service)
            idx_critical = np.argmin(e_melt)
            x_critical = X_mm[idx_critical]
            flux_critical = Flux_MW[idx_critical]
            
            # Vérifier si l'épaisseur actuelle est OK
            T_hot_current = T_wall_cold + (flux_critical * 1e6 * e_current/1000) / k_mat
            
            # Texte du tableau
            table_text = f"""
    📊 RÉSUMÉ - {mat_name}
    {'='*50}
    
    🛠️  Matériau: {mat_name}
        • Conductivité k = {k_mat} W/m-K
        • T fusion = {T_melt} K
        • T max service = {T_max_service} K
    
    🔥  Flux thermique:
        • Max = {max(Flux_MW):.2f} MW/m²
        • Position critique = {x_critical:.1f} mm (x=0 = col)
    
    📏  ÉPAISSEURS CRITIQUES:
        • Épaisseur max avant FUSION = {e_melt_min:.2f} mm
        • Épaisseur max avant T_max = {e_max_min:.2f} mm
        • Épaisseur actuelle = {e_current:.1f} mm
    
    🎯  À LA POSITION CRITIQUE (x={x_critical:.0f}mm):
        • Flux = {flux_critical:.2f} MW/m²
        • T paroi hot = {T_hot_current:.0f} K
        • Marge avant fusion = {T_melt - T_hot_current:.0f} K
    """
            
            # Calculer l'ablation
            e_sacrificielle = max(0, e_current - e_melt_min)
            rho_mat = mat.get("rho", 8000)
            
            # Surface approximative de la zone critique (10% autour du col)
            idx_start = max(0, idx_critical - len(X_mm)//10)
            idx_end = min(len(X_mm)-1, idx_critical + len(X_mm)//10)
            A_critical = 0
            for i in range(idx_start, idx_end):
                r_avg = (Y_mm[i] + Y_mm[i+1]) / 2 / 1000  # m
                dL = abs(X_mm[i+1] - X_mm[i]) / 1000  # m
                A_critical += 2 * np.pi * r_avg * dL
            
            masse_perdue = rho_mat * A_critical * (e_sacrificielle / 1000) if e_sacrificielle > 0 else 0
            
            # Ajouter section ablation
            if e_sacrificielle > 0:
                ablation_text = f"""
    🔥  ANALYSE ABLATION:
        • Épaisseur sacrificielle = {e_sacrificielle:.2f} mm
        • Surface zone critique ≈ {A_critical*1e4:.1f} cm²
        • Masse qui fond ≈ {masse_perdue*1000:.1f} g
        • Épaisseur finale = {e_melt_min:.2f} mm
        
    ⚠️  Les premiers {e_sacrificielle:.1f} mm vont fondre
        jusqu'à atteindre l'équilibre thermique!
    """
                table_text += ablation_text
            else:
                table_text += f"""
    ✅  ABLATION: Aucune
        Marge = {e_melt_min - e_current:.1f} mm avant fusion
    """
            
            # Verdict
            if e_current > e_melt_min:
                verdict = f"\n    💀 ABLATION: {e_sacrificielle:.1f}mm vont fondre ({masse_perdue*1000:.0f}g perdus)"
                verdict_color = '#ff0000'
            elif e_current > e_max_min:
                verdict = f"\n    ⚠️ ATTENTION: L'épaisseur {e_current:.1f}mm > {e_max_min:.1f}mm (T_max)"
                verdict_color = '#ff8800'
            else:
                marge = e_max_min - e_current
                verdict = f"\n    ✅ OK: Marge de {marge:.1f}mm avant T_max service"
                verdict_color = '#00ff88'
            
            ax4.text(0.05, 0.95, table_text, transform=ax4.transAxes, fontsize=11,
                    verticalalignment='top', fontfamily='monospace', color=self.text_primary)
            ax4.text(0.05, 0.12, verdict, transform=ax4.transAxes, fontsize=13,
                    verticalalignment='top', fontfamily='monospace', color=verdict_color, fontweight='bold')
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            import traceback
            error_msg = f"Erreur: {str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("Erreur", error_msg)
    
    def init_wiki_tab(self):
        """Onglet Wiki - Documentation complète sur l'analyse thermique"""
        # Barre de couleur en haut
        tk.Frame(self.tab_wiki, height=4, bg="#9966ff").pack(fill=tk.X)
        
        # Frame principal
        main_frame = ttk.Frame(self.tab_wiki)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Titre
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="📖 WIKI - Analyse Thermique des Moteurs-Fusées", 
                 font=("Segoe UI", 16, "bold"), foreground=self.accent).pack(side=tk.LEFT)
        
        # Barre d'outils
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Variable pour la recherche
        self.wiki_search_var = tk.StringVar()
        ttk.Label(toolbar, text="🔍 Rechercher:").pack(side=tk.LEFT, padx=(0, 5))
        search_entry = ttk.Entry(toolbar, textvariable=self.wiki_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<Return>", lambda e: self.wiki_search())
        ttk.Button(toolbar, text="Chercher", command=self.wiki_search, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Suivant", command=self.wiki_search_next, style="Secondary.TButton").pack(side=tk.LEFT)
        
        # Sommaire à gauche
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Panneau sommaire
        toc_frame = ttk.LabelFrame(paned, text="📑 Sommaire", padding=5)
        paned.add(toc_frame, weight=1)
        
        # Liste du sommaire
        self.wiki_toc = tk.Listbox(toc_frame, bg=self.bg_surface, fg=self.text_primary,
                                   selectbackground=self.accent, selectforeground="#000000",
                                   font=("Consolas", 10), height=25, activestyle='none')
        self.wiki_toc.pack(fill=tk.BOTH, expand=True)
        self.wiki_toc.bind("<<ListboxSelect>>", self.wiki_goto_section)
        
        # Sections du sommaire
        toc_items = [
            "1. Introduction",
            "   1.1 Pourquoi refroidir ?",
            "   1.2 Stratégies de refroidissement",
            "   1.3 Schéma du transfert",
            "   1.4 Équations fondamentales",
            "   1.5 Ordres de grandeur",
            "2. Théorie du transfert thermique",
            "   2.1 Conduction thermique",
            "   2.2 Convection thermique", 
            "   2.3 Nombres adimensionnels",
            "3. Modèle de Bartz",
            "   3.1 Historique",
            "   3.2 Équation complète",
            "   3.3 Formule simplifiée",
            "   3.4 Propriétés gaz combustion",
            "   3.5 Valeurs typiques h_g",
            "   3.6 Limitations",
            "   3.7 Autres corrélations",
            "4. Températures de paroi",
            "   4.1 Système d'équations",
            "   4.2 Calcul T_wall_hot",
            "   4.3 Calcul T_wall_cold",
            "   4.4 Profil dans la paroi",
            "   4.5 Contraintes thermiques",
            "   4.6 Régime transitoire",
            "   4.7 Température adiabatique",
            "   4.8 Calcul itératif",
            "5. Corrélations coolant",
            "   5.1 Dittus-Boelter",
            "   5.2 Gnielinski",
            "   5.3 Régime laminaire",
            "   5.4 Régime transitoire",
            "   5.5 Ébullition sous-refroidie",
            "   5.6 Géométrie des canaux",
            "   5.7 Pertes de charge",
            "   5.8 Valeurs typiques h_c",
            "6. Épaisseur critique",
            "   6.1 Épaisseur de fusion",
            "   6.2 Épaisseur de service",
            "   6.3 Processus d'ablation",
            "   6.4 Épaisseur sacrificielle",
            "   6.5 Temps d'ablation",
            "   6.6 Ablation acceptable?",
            "   6.7 Dimensionnement",
            "   6.8 Carte thermique",
            "7. Propriétés matériaux",
            "   7.1 Tableau récapitulatif",
            "   7.2 Alliages de cuivre",
            "   7.3 Superalliages nickel",
            "   7.4 Alliages aluminium",
            "   7.5 Métaux réfractaires",
            "   7.6 Céramiques/composites",
            "   7.7 Critères de sélection",
            "   7.8 Exemples moteurs réels",
            "8. Propriétés coolants",
            "   8.1 Tableau récapitulatif",
            "   8.2 Hydrogène (LH2)",
            "   8.3 Oxygène (LOX)",
            "   8.4 Méthane (LCH4)",
            "   8.5 RP-1 / Kérosène",
            "   8.6 Éthanol",
            "   8.7 Hydrazines",
            "   8.8 Eau (H2O)",
            "   8.9 Ammoniac (NH3)",
            "   8.10 Sélection coolant",
            "   8.11 Propriétés vs T",
            "9. Exemples de calcul",
            "   9.1 Exemple LOX/RP-1",
            "   9.2 Exemple LOX/LH2",
            "   9.3 Exemple LOX/CH4",
            "   9.4 Dimensionnement canaux",
            "   9.5 Élévation T coolant",
            "   9.6 Analyse dimensionnelle",
            "   9.7 Tableau récapitulatif",
            "   9.8 Exercices",
            "10. Formules rapides",
            "   10.1 Équations fondamentales",
            "   10.2 Équation de Bartz",
            "   10.3 Nombres adimensionnels",
            "   10.4 Corrélations convection",
            "   10.5 Température paroi",
            "   10.6 Épaisseur paroi",
            "   10.7 Puissance thermique",
            "   10.8 Pertes de charge",
            "   10.9 Film cooling",
            "   10.10 Propriétés gaz",
            "   10.11 Tableau formules",
            "   10.12 Ordres de grandeur",
            "   10.13 Conversions",
            "   10.14 Constantes",
            "Références",
        ]
        for item in toc_items:
            self.wiki_toc.insert(tk.END, item)
        
        # Panneau contenu
        content_frame = ttk.LabelFrame(paned, text="📄 Contenu", padding=5)
        paned.add(content_frame, weight=4)
        
        # Zone de texte avec scrollbar
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.wiki_text = tk.Text(text_frame, bg=self.bg_surface, fg=self.text_primary,
                                 font=("Consolas", 11), wrap=tk.WORD,
                                 insertbackground=self.accent, padx=15, pady=10,
                                 highlightthickness=0, bd=0)
        
        scrollbar = ttk.Scrollbar(text_frame, command=self.wiki_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.wiki_text.config(yscrollcommand=scrollbar.set)
        self.wiki_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurer les tags de style
        self.wiki_text.tag_configure("h1", font=("Segoe UI", 18, "bold"), foreground="#ff79c6", spacing3=10)
        self.wiki_text.tag_configure("h2", font=("Segoe UI", 14, "bold"), foreground="#ffb86c", spacing1=15, spacing3=5)
        self.wiki_text.tag_configure("h3", font=("Segoe UI", 12, "bold"), foreground="#8be9fd", spacing1=10, spacing3=3)
        self.wiki_text.tag_configure("code", font=("Consolas", 10), background="#1a1a2e", foreground="#50fa7b")
        self.wiki_text.tag_configure("formula", font=("Consolas", 11), foreground="#bd93f9")
        self.wiki_text.tag_configure("important", foreground="#ff5555", font=("Consolas", 11, "bold"))
        self.wiki_text.tag_configure("table_header", font=("Consolas", 10, "bold"), foreground="#8be9fd")
        self.wiki_text.tag_configure("highlight", background="#3d3d00", foreground="#ffff00")
        self.wiki_text.tag_configure("normal", font=("Consolas", 11), foreground=self.text_primary)
        
        # Variable pour la recherche
        self.wiki_search_pos = "1.0"
        
        # Charger le contenu du wiki
        self.load_wiki_content()
    
    def load_wiki_content(self):
        """Charge le contenu du wiki dans la zone de texte"""
        self.wiki_text.config(state=tk.NORMAL)
        self.wiki_text.delete(1.0, tk.END)
        
        # Contenu du wiki (version ultra-détaillée)
        content = '''
🔥 ANALYSE THERMIQUE DES MOTEURS-FUSÉES - GUIDE COMPLET
═══════════════════════════════════════════════════════════════

Ce guide exhaustif couvre tous les aspects du refroidissement 
régénératif des moteurs-fusées à propergols liquides.


1. INTRODUCTION ET CONCEPTS FONDAMENTAUX
═══════════════════════════════════════════════════════════════

1.1 POURQUOI LE REFROIDISSEMENT EST-IL CRITIQUE ?
───────────────────────────────────────────────────────────────

Un moteur-fusée à propergols liquides génère des températures 
extrêmement élevées lors de la combustion:

  • Couple LOX/RP-1:    T_c ≈ 3500-3600 K
  • Couple LOX/LH2:     T_c ≈ 3200-3400 K  
  • Couple LOX/CH4:     T_c ≈ 3500-3600 K
  • Couple N2O4/UDMH:   T_c ≈ 3200-3400 K
  • Couple H2O2/RP-1:   T_c ≈ 2800-3000 K

⚠️  PROBLÈME CRITIQUE:
Ces températures dépassent largement le point de fusion de TOUS 
les métaux et alliages connus:

  • Cuivre fond à:      1358 K (1085°C)
  • Inconel fond à:     1609 K (1336°C)  
  • Tungstène fond à:   3695 K (3422°C)

Sans refroidissement, la paroi de la chambre fondrait en 
quelques MILLISECONDES à quelques SECONDES selon:
  - Le flux thermique local
  - L'épaisseur de la paroi
  - La conductivité thermique du matériau
  - La capacité thermique massique

EXEMPLE NUMÉRIQUE - Temps avant fusion sans refroidissement:
  Données: CuCr, e=3mm, ρ=8900 kg/m³, Cp=385 J/kg·K
  Flux entrant: q = 30 MW/m² (typique au col)
  
  Énergie pour chauffer 1m² de ΔT = 1000K:
  E = ρ × e × Cp × ΔT = 8900 × 0.003 × 385 × 1000 = 10.3 MJ
  
  Temps: t = E/q = 10.3×10⁶ / 30×10⁶ = 0.34 seconde!

💀 En moins d'une demi-seconde, la paroi atteint sa température 
   de fusion sans refroidissement actif!


1.2 LES DIFFÉRENTES STRATÉGIES DE REFROIDISSEMENT
───────────────────────────────────────────────────────────────

Il existe plusieurs méthodes pour gérer la charge thermique:

A) REFROIDISSEMENT RÉGÉNÉRATIF (traité dans ce guide)
   Le propergol (fuel ou oxydant) circule dans des canaux 
   autour de la chambre AVANT d'être injecté et brûlé.
   
   Avantages:
   ✅ Récupère l'énergie thermique (améliore Isp)
   ✅ Pas de perte de masse propulsive
   ✅ Permet fonctionnement continu longue durée
   ✅ Contrôle précis des températures
   
   Inconvénients:
   ❌ Complexité de fabrication (canaux, soudures)
   ❌ Risque de cokéfaction avec hydrocarbures
   ❌ Pertes de charge hydrauliques
   ❌ Coût élevé de fabrication

B) REFROIDISSEMENT PAR FILM (Film Cooling)
   Une couche de propergol liquide ou gazeux est injectée 
   le long de la paroi, créant une barrière protectrice.
   
   Avantages:
   ✅ Simple à implémenter
   ✅ Réduit le flux thermique effectif
   
   Inconvénients:
   ❌ Perte d'Isp (propergol non brûlé de façon optimale)
   ❌ Peut perturber la combustion
   ❌ Efficacité limitée dans le temps

C) REFROIDISSEMENT ABLATIF
   La paroi est faite d'un matériau qui s'érode progressivement,
   absorbant l'énergie par changement de phase.
   
   Avantages:
   ✅ Très simple (pas de circulation)
   ✅ Léger pour moteurs à courte durée
   ✅ Fiable (pas de pompes, pas de canaux)
   
   Inconvénients:
   ❌ Durée limitée
   ❌ Changement de géométrie pendant le tir
   ❌ Débris dans l'écoulement

D) REFROIDISSEMENT RADIATIF
   La paroi rayonne sa chaleur vers l'espace.
   Utilisé principalement pour les tuyères de moteurs 
   spatiaux à faible poussée.
   
   Avantages:
   ✅ Très simple, léger
   ✅ Pas de fluide de refroidissement
   
   Inconvénients:
   ❌ Limité aux faibles flux (< 5 MW/m²)
   ❌ Nécessite matériaux réfractaires (Nb, Mo, W)

E) TRANSPIRATION (Sweat Cooling)
   Le coolant suinte à travers un matériau poreux.
   
   Avantages:
   ✅ Très efficace thermiquement
   
   Inconvénients:
   ❌ Risque de bouchage des pores
   ❌ Difficulté de fabrication
   ❌ Rarement utilisé en pratique


1.3 SCHÉMA DU TRANSFERT THERMIQUE
───────────────────────────────────────────────────────────────

Vue en coupe de la paroi d'un moteur à refroidissement régénératif:

     GAZ DE COMBUSTION CHAUDS
     T_gaz ≈ 2800-3500 K (selon T_aw adiabatique)
     Vitesse: Mach 0.1-0.3 (chambre) à Mach 1+ (col)
            │
            │ CONVECTION FORCÉE (coefficient h_g)
            │ q₁ = h_g × (T_gaz - T_wall_hot)
            ↓
    ════════════════════════════════════════  
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║  ← Surface chaude
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║    T_wall_hot
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║
    ║░░░░░░ PAROI MÉTALLIQUE ░░░░░░░░░░░░║  ← Épaisseur e
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║    Conductivité k
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║
    ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║  ← Surface froide
    ════════════════════════════════════════    T_wall_cold
            │
            │ CONDUCTION (à travers la paroi)
            │ q₂ = (k/e) × (T_wall_hot - T_wall_cold)
            │
            ↓
    ╔══════════════════════════════════════╗
    ║        CANAL DE REFROIDISSEMENT      ║  ← Hauteur h_canal
    ║   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~→      ║    Largeur w_canal
    ║        Coolant en écoulement         ║    T_coolant
    ╚══════════════════════════════════════╝
            │
            │ CONVECTION FORCÉE (coefficient h_c)
            │ q₃ = h_c × (T_wall_cold - T_coolant)
            ↓
    ════════════════════════════════════════
    ║        PAROI EXTERNE (liner)         ║
    ════════════════════════════════════════

PRINCIPE DE CONSERVATION:
En régime permanent (steady-state), le flux est CONSTANT 
à travers toutes les couches:

  q₁ = q₂ = q₃ = q

  q = h_g×(T_gaz - T_wh) = (k/e)×(T_wh - T_wc) = h_c×(T_wc - T_cool)


1.4 ÉQUATIONS FONDAMENTALES DU TRANSFERT
───────────────────────────────────────────────────────────────

La résolution du problème thermique repose sur l'ANALOGIE 
ÉLECTRIQUE: le flux de chaleur est analogue au courant, 
la différence de température à la tension.

RÉSISTANCES THERMIQUES EN SÉRIE:

  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │  R_gaz  │────│ R_paroi │────│ R_cool  │
  │  1/h_g  │    │   e/k   │    │  1/h_c  │
  └─────────┘    └─────────┘    └─────────┘
       ↑              ↑              ↑
    T_gaz          T_wall         T_cool

Résistance totale:
  R_total = R_gaz + R_paroi + R_cool
  R_total = 1/h_g + e/k + 1/h_c   [m²·K/W]

Flux thermique:
  q = ΔT_total / R_total
  q = (T_gaz - T_coolant) / (1/h_g + e/k + 1/h_c)   [W/m²]

REMARQUE IMPORTANTE:
Cette formule suppose des coefficients h constants et une 
paroi plane. En réalité:
  - h_g varie avec la position (maximum au col)
  - La géométrie est cylindrique/conique
  - T_coolant augmente le long du canal
  - Les propriétés varient avec T


1.5 ORDRES DE GRANDEUR TYPIQUES
───────────────────────────────────────────────────────────────

Pour un moteur LOX/RP-1 de 100 kN:

PARAMÈTRES DE CONCEPTION:
  ┌────────────────────────┬──────────────────────────────┐
  │ Paramètre              │ Valeur typique               │
  ├────────────────────────┼──────────────────────────────┤
  │ Pression chambre       │ 30-100 bar                   │
  │ Température chambre    │ 3400-3600 K                  │
  │ Diamètre col           │ 50-150 mm                    │
  │ Diamètre chambre       │ 100-300 mm                   │
  │ Rapport de section     │ 15-40 (selon altitude)       │
  │ Épaisseur paroi        │ 1-5 mm                       │
  │ Nombre de canaux       │ 50-200                       │
  └────────────────────────┴──────────────────────────────┘

FLUX THERMIQUES:
  ┌────────────────────────┬──────────────────────────────┐
  │ Zone                   │ Flux q (MW/m²)               │
  ├────────────────────────┼──────────────────────────────┤
  │ Injecteur              │ 5 - 15                       │
  │ Chambre cylindrique    │ 5 - 15                       │
  │ Convergent             │ 10 - 30                      │
  │ Col (MAXIMUM!)         │ 20 - 80                      │
  │ Divergent (début)      │ 10 - 30                      │
  │ Divergent (sortie)     │ 1 - 5                        │
  └────────────────────────┴──────────────────────────────┘

COEFFICIENTS DE TRANSFERT:
  ┌────────────────────────┬──────────────────────────────┐
  │ Coefficient            │ Valeur (W/m²·K)              │
  ├────────────────────────┼──────────────────────────────┤
  │ h_g (chambre)          │ 2,000 - 10,000               │
  │ h_g (col)              │ 10,000 - 50,000              │
  │ h_c (RP-1)             │ 5,000 - 30,000               │
  │ h_c (LH2)              │ 20,000 - 150,000             │
  │ h_c (CH4)              │ 10,000 - 50,000              │
  └────────────────────────┴──────────────────────────────┘

TEMPÉRATURES DE PAROI:
  ┌────────────────────────┬──────────────────────────────┐
  │ Surface                │ Température (K)              │
  ├────────────────────────┼──────────────────────────────┤
  │ T_wall_hot (typique)   │ 600 - 1000                   │
  │ T_wall_hot (max admis) │ 800 - 1200 selon matériau    │
  │ T_wall_cold            │ 400 - 800                    │
  │ T_coolant entrée       │ 150 - 300                    │
  │ T_coolant sortie       │ 300 - 500                    │
  └────────────────────────┴──────────────────────────────┘


2. THÉORIE DÉTAILLÉE DU TRANSFERT THERMIQUE
═══════════════════════════════════════════════════════════════

Cette section développe les fondements physiques et 
mathématiques du transfert de chaleur dans les moteurs-fusées.


2.1 LA CONDUCTION THERMIQUE
───────────────────────────────────────────────────────────────

2.1.1 Loi de Fourier

La conduction est le transfert d'énergie thermique par 
agitation moléculaire et interaction électronique dans 
un milieu solide (ou fluide immobile).

ÉQUATION DE FOURIER (forme différentielle):
  
  q⃗ = -k × ∇T

Où:
  q⃗  = vecteur flux thermique [W/m²]
  k  = conductivité thermique [W/(m·K)]
  ∇T = gradient de température [K/m]

Le signe négatif indique que le flux va des zones chaudes 
vers les zones froides.

Pour une paroi plane 1D:

  q = -k × dT/dx = k × (T_hot - T_cold) / e

  q = k × ΔT / e   [W/m²]

RÉSISTANCE THERMIQUE DE CONDUCTION:

  R_cond = e / k   [m²·K/W]

  ΔT = q × R_cond

Plus k est élevé, plus la résistance est faible, plus le 
transfert est efficace.

2.1.2 Conductivité des matériaux pour moteurs-fusées

La conductivité k varie selon:
  - La composition du matériau
  - La température (généralement ↓ quand T ↑ pour métaux)
  - L'état cristallin
  - Les impuretés

TABLEAU DES CONDUCTIVITÉS DÉTAILLÉ:
  ┌──────────────────┬────────────────────────────────────────┐
  │ Matériau         │ k (W/m·K) à différentes températures   │
  ├──────────────────┼──────────┬──────────┬────────┬─────────┤
  │                  │  300 K   │  500 K   │ 800 K  │ 1000 K  │
  ├──────────────────┼──────────┼──────────┼────────┼─────────┤
  │ Cuivre pur       │   401    │   386    │  357   │   337   │
  │ CuCr (C18200)    │   324    │   315    │  298   │   285   │
  │ CuCrZr           │   315    │   305    │  288   │   275   │
  │ GRCop-84 (NASA)  │   298    │   285    │  265   │   250   │
  │ Inconel 718      │   11.4   │   14.7   │  19.2  │   22.1  │
  │ Inconel 625      │    9.8   │   12.8   │  17.3  │   20.5  │
  │ Inox 316L        │   16.3   │   18.9   │  22.5  │   25.2  │
  │ Inox 304         │   16.2   │   18.6   │  22.0  │   24.5  │
  │ Niobium          │   53.7   │   55.1   │  59.3  │   62.0  │
  │ C103 (Nb alloy)  │   44.2   │   46.5   │  51.2  │   54.5  │
  │ Molybdène        │   138    │   126    │  112   │   105   │
  │ TZM (Mo alloy)   │   120    │   115    │  105   │    98   │
  │ Tungstène        │   173    │   156    │  132   │   118   │
  │ Rhénium          │   47.9   │   44.5   │  40.2  │   38.0  │
  │ Tantale          │   57.5   │   56.0   │  57.5  │   59.0  │
  │ AlSi10Mg (SLM)   │   130    │   138    │  (fond)│  (fond) │
  │ Ti-6Al-4V        │    6.7   │    8.5   │  12.0  │   15.0  │
  │ Graphite (ISO)   │   120    │   100    │   80   │    70   │
  │ C/C composite    │   50-150 │   70-120 │  80-100│   85-95 │
  └──────────────────┴──────────┴──────────┴────────┴─────────┘

REMARQUES SUR LES ALLIAGES DE CUIVRE:

• CuCr (C18200 / "Chromium Copper"):
  - Contient ~1% Cr
  - Bonne conductivité + résistance mécanique
  - T_max service ≈ 1050 K (ramollissement)
  - Très utilisé: Merlin (SpaceX), RS-25 (NASA)

• CuCrZr (C18150):
  - Contient ~0.8% Cr + 0.08% Zr
  - Meilleure tenue à chaud que CuCr
  - T_max service ≈ 1100 K
  - Utilisé: RD-170 (Energomash)

• GRCop-84 (NASA Glenn):
  - Cu + 8% Cr + 4% Nb (nano-particules)
  - Développé spécifiquement pour moteurs-fusées
  - Excellente résistance au fluage à haute T
  - T_max service ≈ 1200 K
  - Utilisé: SLS RS-25 upgrades, Relativity Terran

2.1.3 Géométrie cylindrique

Pour une paroi cylindrique (chambre, tuyère):

  q_radial = (2π × k × L × ΔT) / ln(r_ext/r_int)

  Résistance: R_cyl = ln(r_ext/r_int) / (2π × k × L)

Pour des parois minces (e << r_moy), on peut approximer:
  R_cyl ≈ e / (k × A_moy)  où A_moy = 2π × r_moy × L


2.2 LA CONVECTION THERMIQUE
───────────────────────────────────────────────────────────────

2.2.1 Loi de Newton du refroidissement

La convection est le transfert d'énergie entre une surface 
solide et un fluide en mouvement.

ÉQUATION DE NEWTON:

  q = h × (T_surface - T_fluide)   [W/m²]

Où:
  h  = coefficient de transfert convectif [W/(m²·K)]
  T_surface = température de la paroi [K]
  T_fluide = température du fluide [K]

Le coefficient h dépend de nombreux facteurs:
  - Type d'écoulement (laminaire, turbulent)
  - Vitesse du fluide
  - Propriétés thermophysiques (ρ, μ, Cp, k_fluide)
  - Géométrie du canal
  - Rugosité de surface
  - Effets d'entrée

RÉSISTANCE THERMIQUE DE CONVECTION:

  R_conv = 1 / h   [m²·K/W]

2.2.2 Types de convection

CONVECTION NATURELLE:
  Le mouvement du fluide est dû à la différence de densité 
  causée par le gradient de température.
  h ≈ 5-25 W/m²·K (air)
  → Non pertinent pour les moteurs-fusées!

CONVECTION FORCÉE:
  Le mouvement du fluide est imposé par une pompe/turbine.
  h ≈ 50 - 200,000 W/m²·K selon le fluide et les conditions.
  → C'est le cas dans les moteurs-fusées.

ÉBULLITION:
  Changement de phase liquide → vapeur.
  h peut atteindre 100,000+ W/m²·K
  ⚠️ Éviter l'ébullition non contrôlée (DNB = crise d'ébullition)

2.2.3 Couche limite thermique

Près de la paroi, il existe une "couche limite thermique" où 
la température varie de T_surface à T_fluide.

CÔTÉ GAZ CHAUD:
  - Épaisseur couche limite: δ_th ≈ 0.1-1 mm
  - C'est là que se concentre la résistance thermique
  - La turbulence améliore le mélange → h_g plus élevé

CÔTÉ COOLANT:
  - Épaisseur couche limite: δ_th ≈ 0.01-0.5 mm
  - Canaux étroits → meilleur transfert
  - Turbulence très importante pour h_c élevé

LIEN AVEC h:
  h ≈ k_fluide / δ_th

Plus la couche limite est mince, plus h est élevé.


2.3 LES NOMBRES ADIMENSIONNELS
───────────────────────────────────────────────────────────────

Les corrélations de transfert thermique utilisent des 
groupements adimensionnels permettant de généraliser les 
résultats expérimentaux.

2.3.1 Nombre de Reynolds (Re)

DÉFINITION:
  Re = ρ × v × D_h / μ = v × D_h / ν

Où:
  ρ   = masse volumique [kg/m³]
  v   = vitesse moyenne [m/s]
  D_h = diamètre hydraulique [m]
  μ   = viscosité dynamique [Pa·s]
  ν   = viscosité cinématique [m²/s] = μ/ρ

SIGNIFICATION PHYSIQUE:
  Re = Forces d'inertie / Forces visqueuses

RÉGIMES D'ÉCOULEMENT:
  ┌────────────────────┬─────────────────────────────────────┐
  │ Re                 │ Régime                              │
  ├────────────────────┼─────────────────────────────────────┤
  │ Re < 2,300         │ LAMINAIRE                           │
  │                    │ Écoulement ordonné en couches       │
  │                    │ Profil de vitesse parabolique       │
  │                    │ Transfert thermique faible          │
  ├────────────────────┼─────────────────────────────────────┤
  │ 2,300 < Re < 10,000│ TRANSITOIRE                         │
  │                    │ Intermittence turbulente            │
  │                    │ Comportement imprévisible           │
  │                    │ À éviter si possible!               │
  ├────────────────────┼─────────────────────────────────────┤
  │ Re > 10,000        │ TURBULENT DÉVELOPPÉ                 │
  │                    │ Mélange chaotique efficace          │
  │                    │ Profil de vitesse aplati            │
  │                    │ Excellent transfert thermique!      │
  └────────────────────┴─────────────────────────────────────┘

DIAMÈTRE HYDRAULIQUE:
Pour un canal non-circulaire:
  D_h = 4 × A / P

Où:
  A = aire de la section [m²]
  P = périmètre mouillé [m]

Exemples:
  - Canal rectangulaire (w × h): D_h = 4×w×h / (2w+2h) = 2wh/(w+h)
  - Canal carré (a × a): D_h = a
  - Anneau (R_ext, R_int): D_h = 2×(R_ext - R_int)

VALEURS TYPIQUES DANS LES MOTEURS:
  ┌────────────────────┬──────────────────────────────────┐
  │ Fluide/Zone        │ Re typique                       │
  ├────────────────────┼──────────────────────────────────┤
  │ Gaz chambre        │ 10⁵ - 10⁷ (hautement turbulent)  │
  │ RP-1 dans canaux   │ 10⁴ - 10⁵                        │
  │ LH2 dans canaux    │ 10⁵ - 10⁶                        │
  │ CH4 dans canaux    │ 10⁴ - 10⁵                        │
  │ LOX dans canaux    │ 10⁴ - 10⁵                        │
  └────────────────────┴──────────────────────────────────┘

2.3.2 Nombre de Prandtl (Pr)

DÉFINITION:
  Pr = μ × Cp / k = ν / α

Où:
  μ  = viscosité dynamique [Pa·s]
  Cp = capacité thermique massique [J/(kg·K)]
  k  = conductivité thermique [W/(m·K)]
  ν  = viscosité cinématique [m²/s]
  α  = diffusivité thermique [m²/s]

SIGNIFICATION PHYSIQUE:
  Pr = Diffusivité de quantité de mouvement / Diffusivité thermique
  Pr = Épaisseur couche limite dynamique / Épaisseur couche limite thermique

INTERPRÉTATION:
  ┌────────────────────┬─────────────────────────────────────┐
  │ Pr                 │ Signification                       │
  ├────────────────────┼─────────────────────────────────────┤
  │ Pr << 1            │ MÉTAUX LIQUIDES                     │
  │ (0.001-0.03)       │ Diffusion thermique >> diffusion    │
  │                    │ de quantité de mouvement            │
  │                    │ Ex: Na, K, NaK, Hg, Li              │
  ├────────────────────┼─────────────────────────────────────┤
  │ Pr ≈ 0.7-1.0       │ GAZ                                 │
  │                    │ Couches limites comparables         │
  │                    │ Ex: Air, N2, O2, gaz de combustion  │
  ├────────────────────┼─────────────────────────────────────┤
  │ Pr > 1             │ LIQUIDES                            │
  │ (1-1000)           │ Diffusion momentum >> diffusion     │
  │                    │ thermique                           │
  │                    │ Ex: H2O (Pr≈6), RP-1 (Pr≈20-50)     │
  └────────────────────┴─────────────────────────────────────┘

VALEURS TYPIQUES:
  ┌────────────────────┬──────────────────────────────────┐
  │ Fluide             │ Pr (approximatif)                │
  ├────────────────────┼──────────────────────────────────┤
  │ Gaz de combustion  │ 0.7 - 0.9                        │
  │ Hydrogène liquide  │ 0.7 - 1.5                        │
  │ Méthane liquide    │ 2 - 5                            │
  │ LOX                │ 2 - 4                            │
  │ RP-1 / Kérosène    │ 10 - 100 (selon T)               │
  │ Éthanol            │ 10 - 50                          │
  │ Eau                │ 1 - 10 (selon T)                 │
  └────────────────────┴──────────────────────────────────┘

2.3.3 Nombre de Nusselt (Nu)

DÉFINITION:
  Nu = h × D_h / k_fluide

Où:
  h        = coefficient de convection [W/(m²·K)]
  D_h      = diamètre hydraulique [m]
  k_fluide = conductivité du fluide [W/(m·K)]

SIGNIFICATION PHYSIQUE:
  Nu = Transfert convectif réel / Transfert conductif pur

  Nu = 1 signifie que la convection n'améliore pas le 
       transfert par rapport à la conduction seule.
  Nu >> 1 signifie une amélioration significative.

UTILISATION:
Une fois Nu calculé via une corrélation, on obtient h:

  h = Nu × k_fluide / D_h

VALEURS TYPIQUES:
  - Écoulement laminaire: Nu ≈ 3.66-4.36
  - Écoulement turbulent: Nu ≈ 100-1000
  - Ébullition: Nu >> 1000

2.3.4 Autres nombres utiles

NOMBRE DE STANTON (St):
  St = h / (ρ × v × Cp) = Nu / (Re × Pr)
  
  Utilisé dans les analyses de couche limite.
  Représente le transfert thermique adimensionnel.

NOMBRE DE BIOT (Bi):
  Bi = h × L_c / k_solide
  
  Où L_c = caractéristique longueur du solide (e.g., épaisseur)
  
  Si Bi << 0.1: Température uniforme dans le solide
  Si Bi >> 0.1: Gradient de température significatif

NOMBRE DE FOURIER (Fo):
  Fo = α × t / L²
  
  Temps adimensionnel pour les problèmes transitoires.
  α = diffusivité thermique du solide.

NOMBRE DE MACH (Ma):
  Ma = v / a  (a = vitesse du son)
  
  Important côté gaz: effets de compressibilité.


3. MODÈLE DE BARTZ POUR h_g
═══════════════════════════════════════════════════════════════

L'équation de Bartz est la corrélation de référence pour 
calculer le coefficient de transfert convectif côté gaz 
chaud dans les moteurs-fusées.


3.1 HISTORIQUE ET DÉVELOPPEMENT
───────────────────────────────────────────────────────────────

David R. Bartz a développé cette corrélation en 1957 au 
Jet Propulsion Laboratory (JPL) de la NASA.

CONTEXTE:
  - Années 1950: développement de missiles balistiques
  - Besoin de prédire les températures de paroi
  - Corrélations existantes (Dittus-Boelter) inadaptées
  - Conditions extrêmes: T > 3000 K, P > 50 bar

APPROCHE DE BARTZ:
  1. Partir de la corrélation de Dittus-Boelter
  2. Adapter pour les propriétés variables (T très élevées)
  3. Introduire un facteur de correction σ
  4. Valider expérimentalement sur moteurs réels

PUBLICATION ORIGINALE:
  Bartz, D.R., "A Simple Equation for Rapid Estimation of 
  Rocket Nozzle Convective Heat Transfer Coefficients"
  Jet Propulsion, Vol. 27, No. 1, 1957, pp. 49-51


3.2 ÉQUATION COMPLÈTE DE BARTZ
───────────────────────────────────────────────────────────────

FORME GÉNÉRALE:

            0.026      ⎛  μ^0.2 × Cp  ⎞   ⎛ p_c ⎞^0.8
  h_g = ──────────── × ⎜ ───────────── ⎟ × ⎜ ──── ⎟     × (A_t/A)^0.9 × σ
         D_t^0.2       ⎝   Pr^0.6     ⎠   ⎝ c*   ⎠

DÉFINITION DES TERMES:

  h_g   = coefficient de transfert convectif [W/(m²·K)]
  D_t   = diamètre au col [m]
  μ     = viscosité dynamique des gaz [Pa·s]
  Cp    = capacité thermique massique à pression constante [J/(kg·K)]
  Pr    = nombre de Prandtl des gaz combustion [-]
  p_c   = pression de chambre [Pa]
  c*    = vitesse caractéristique [m/s]
  A_t   = aire au col [m²]
  A     = aire locale [m²]
  σ     = facteur de correction pour couche limite [-]

LE FACTEUR σ (sigma):

                          1
  σ = ─────────────────────────────────────────────────────────
        ⎛   T_wall_hot     ⎞^0.68   ⎛           T_wall_hot     ⎞^0.12
       ⎜0.5 × ─────────── + 0.5⎟    × ⎜1 + γ-1 × M² × (0.5 - ─────────)⎟
        ⎝      T_stag      ⎠         ⎝   2            T_stag   ⎠

Où:
  T_wall_hot = température de paroi côté gaz [K]
  T_stag = température de stagnation (≈ T_chambre) [K]
  γ = rapport des chaleurs spécifiques [-]
  M = nombre de Mach local [-]

SIMPLIFICATION COURANTE:
Pour les calculs préliminaires, on utilise souvent σ ≈ 1.0-1.2


3.3 FORMULE SIMPLIFIÉE (utilisée dans le code)
───────────────────────────────────────────────────────────────

Pour simplifier l'implémentation, on utilise:

ÉTAPE 1 - Calcul de h_g au col (référence):

            0.026      ⎛  μ^0.2 × Cp  ⎞   ⎛ P_c ⎞^0.8
  h_g_col = ────────── × ⎜ ────────────  ⎟ × ⎜ ──── ⎟
            D_t^0.2     ⎝   Pr^0.6    ⎠   ⎝ c*   ⎠

ÉTAPE 2 - h_g local par mise à l'échelle:

  h_g(x) = h_g_col × (D_t / D_local)^1.8

Cette relation vient du fait que:
  - h_g ∝ (débit massique par unité de surface)^0.8
  - À débit constant: G = ṁ/A ∝ 1/D²
  - Donc h_g ∝ (1/D²)^0.8 = D^(-1.6)
  - Avec correction pour le rapport de section: exposant ≈ 1.8

JUSTIFICATION DE L'EXPOSANT 1.8:
  - Origine: combinaison d'effets géométriques et d'écoulement
  - Au col: A minimum, G maximum, donc h_g maximum
  - Dans la chambre: A grand, h_g plus faible
  - Dans le divergent: A croissant, h_g décroissant rapidement


3.4 PROPRIÉTÉS DES GAZ DE COMBUSTION
───────────────────────────────────────────────────────────────

Les propriétés thermo-physiques des gaz de combustion sont 
calculées à une température de film:

  T_film = (T_wall_hot + T_adiabatique) / 2

PROPRIÉTÉS TYPIQUES (LOX/RP-1, T ≈ 2500 K):
  ┌────────────────────┬──────────────────────────────────┐
  │ Propriété          │ Valeur approximative             │
  ├────────────────────┼──────────────────────────────────┤
  │ μ (viscosité)      │ 7-9 × 10⁻⁵ Pa·s                  │
  │ Cp                 │ 2000-2500 J/(kg·K)               │
  │ k_gaz              │ 0.15-0.25 W/(m·K)                │
  │ Pr                 │ 0.75-0.85                        │
  │ γ (gamma)          │ 1.15-1.25                        │
  │ M (masse molaire)  │ 22-28 kg/kmol                    │
  └────────────────────┴──────────────────────────────────┘

VARIATION AVEC LE MÉLANGE O/F:
  ┌──────────────────┬───────────┬───────────┬───────────┐
  │ O/F (LOX/RP-1)   │    2.0    │    2.6    │    3.2    │
  ├──────────────────┼───────────┼───────────┼───────────┤
  │ T_chambre (K)    │   3350    │   3600    │   3500    │
  │ M (kg/kmol)      │   21.5    │   24.0    │   27.5    │
  │ γ                │   1.22    │   1.18    │   1.15    │
  │ c* (m/s)         │   1680    │   1750    │   1700    │
  └──────────────────┴───────────┴───────────┴───────────┘

EFFET SUR h_g:
  - O/F élevé: T_c plus élevé, mais M plus élevé
  - h_g varie peu avec O/F (effets compensatoires)


3.5 VALEURS TYPIQUES DE h_g
───────────────────────────────────────────────────────────────

  ┌─────────────────┬────────────────────┬──────────────────────┐
  │ Zone            │ h_g (W/m²·K)       │ Commentaires         │
  ├─────────────────┼────────────────────┼──────────────────────┤
  │ Injecteur       │ 3,000 - 10,000     │ Dépend du design     │
  │ Chambre (cyl.)  │ 2,000 - 8,000      │ Écoulement subsonique│
  │ Convergent      │ 5,000 - 20,000     │ Accélération du gaz  │
  │ Col (throat)    │ 10,000 - 50,000    │ MAXIMUM! Ma = 1      │
  │ Divergent début │ 8,000 - 25,000     │ Expansion commence   │
  │ Divergent mi    │ 3,000 - 10,000     │ Refroidissement gaz  │
  │ Divergent sortie│ 500 - 3,000        │ Gaz très dilatés     │
  └─────────────────┴────────────────────┴──────────────────────┘

FACTEURS INFLUENÇANT h_g:

  ┌────────────────────┬────────────────────────────────────────┐
  │ Facteur            │ Effet sur h_g                          │
  ├────────────────────┼────────────────────────────────────────┤
  │ Pression chambre ↑ │ h_g ↑ (∝ P^0.8)                        │
  │ Diamètre col ↓     │ h_g ↑ (∝ D^-0.2 pour référence)        │
  │ Position → col     │ h_g ↑ (maximum au col)                 │
  │ Position → sortie  │ h_g ↓ (minimum à la sortie)            │
  │ T_chambre ↑        │ h_g ↓ légèrement (via σ)               │
  │ T_paroi ↓          │ h_g ↑ légèrement (via σ)               │
  └────────────────────┴────────────────────────────────────────┘


3.6 LIMITATIONS DU MODÈLE DE BARTZ
───────────────────────────────────────────────────────────────

Le modèle de Bartz a des limitations importantes:

❌ NE PREND PAS EN COMPTE:
  - Rayonnement thermique (important si T > 3000 K)
  - Dissociation/recombinaison des gaz
  - Effets de couche limite réactive
  - Turbulence de combustion
  - Effets 3D près de l'injecteur
  - Rugosité de surface
  - Dépôts de suie (cokéfaction)

⚠️ PRÉCISION:
  - Généralement ±20-30% pour h_g
  - Peut être pire dans des conditions extrêmes
  - Sous-estime parfois h_g au col

✅ RECOMMANDATIONS:
  - Utiliser des marges de sécurité (facteur 1.2-1.5)
  - Valider par essais si possible
  - Utiliser CFD pour conception détaillée
  - Comparer avec d'autres corrélations (Rao, Cinjarew)


3.7 COMPARAISON AVEC AUTRES CORRÉLATIONS
───────────────────────────────────────────────────────────────

CORRÉLATION DE RAO (1960):
  Similaire à Bartz mais avec facteur σ modifié.
  Meilleure pour les gaz à haute température.

CORRÉLATION DE CINJAREW:
  Utilisée par l'industrie russe.
  Prend en compte plus de paramètres.

APPROCHE CFD MODERNE:
  - Résolution numérique des équations de Navier-Stokes
  - Modèles de turbulence (k-ε, k-ω SST)
  - Précision bien meilleure mais coût élevé
  - Utilisée pour la conception finale


4. CALCUL DES TEMPÉRATURES DE PAROI
═══════════════════════════════════════════════════════════════

Le calcul précis des températures de paroi est l'objectif 
principal de l'analyse thermique. C'est ce qui détermine 
si le moteur survivra ou non.


4.1 SYSTÈME D'ÉQUATIONS THERMIQUES
───────────────────────────────────────────────────────────────

En régime permanent, le flux thermique est constant à travers 
toutes les couches. Cela donne un système de 3 équations:

ÉQUATION 1 - Côté gaz chaud:
  q = h_g × (T_gaz - T_wall_hot)

ÉQUATION 2 - Conduction dans la paroi:
  q = (k/e) × (T_wall_hot - T_wall_cold)

ÉQUATION 3 - Côté coolant:
  q = h_c × (T_wall_cold - T_coolant)

COMBINAISON - Flux thermique total:

        T_gaz - T_coolant
  q = ─────────────────────────────
       1/h_g + e/k + 1/h_c

Cette équation est FONDAMENTALE. Elle permet de calculer q 
connaissant les températures des fluides et les résistances.


4.2 CALCUL DE T_WALL_HOT (température critique)
───────────────────────────────────────────────────────────────

C'est la température la plus importante car c'est elle qui 
détermine si le matériau va fondre ou se dégrader.

MÉTHODE 1 - À partir du flux:

  T_wall_hot = T_gaz - q/h_g

MÉTHODE 2 - À partir de T_wall_cold:

  T_wall_hot = T_wall_cold + q × e/k

MÉTHODE 3 - Formule directe (résolution du système):

           h_g×T_gaz + (k/e)×T_wall_cold
  T_wh = ────────────────────────────────
                h_g + k/e

Ou de façon équivalente:

           h_g×T_gaz + h_c×T_cool + (k/e)×(h_c×T_cool/(h_c+k/e))
  T_wh = ──────────────────────────────────────────────────────────
                            ...système couplé...

En pratique, on résout par itération ou formule analytique.

INFLUENCE DES PARAMÈTRES SUR T_wall_hot:
  ┌────────────────────┬────────────────────────────────────────┐
  │ Si on augmente...  │ Effet sur T_wall_hot                   │
  ├────────────────────┼────────────────────────────────────────┤
  │ h_g ↑              │ T_wall_hot ↑ (plus de flux entrant)    │
  │ h_c ↑              │ T_wall_hot ↓ (meilleure évacuation)    │
  │ k ↑                │ T_wall_hot ↓ (gradient réduit)         │
  │ e ↑                │ T_wall_hot ↑ (résistance accrue)       │
  │ T_gaz ↑            │ T_wall_hot ↑ (source plus chaude)      │
  │ T_coolant ↓        │ T_wall_hot ↓ (puits plus froid)        │
  └────────────────────┴────────────────────────────────────────┘


4.3 CALCUL DE T_WALL_COLD
───────────────────────────────────────────────────────────────

MÉTHODE 1 - À partir du flux:

  T_wall_cold = T_coolant + q/h_c

MÉTHODE 2 - À partir de T_wall_hot:

  T_wall_cold = T_wall_hot - q × e/k

IMPORTANCE DE T_WALL_COLD:
  - Détermine le ΔT dans la paroi
  - Influence le stress thermique (dilatation différentielle)
  - Affecte les propriétés du coolant (ébullition possible?)

⚠️ ATTENTION À L'ÉBULLITION:
Si T_wall_cold > T_ébullition du coolant (à la pression locale):
  → Formation de bulles
  → Risque de DNB (Departure from Nucleate Boiling)
  → Chute drastique de h_c → SURCHAUFFE → DESTRUCTION

TEMPÉRATURES D'ÉBULLITION (à pression atmosphérique):
  ┌────────────────────┬──────────────────────────────────┐
  │ Coolant            │ T_boil @ 1 bar (K)               │
  ├────────────────────┼──────────────────────────────────┤
  │ LH2                │ 20.3 K                           │
  │ LOX                │ 90.2 K                           │
  │ LN2                │ 77.4 K                           │
  │ CH4                │ 111.7 K                          │
  │ C2H6               │ 184.6 K                          │
  │ NH3                │ 239.8 K                          │
  │ C2H5OH             │ 351.4 K                          │
  │ H2O                │ 373.2 K                          │
  │ N2H4               │ 387.0 K                          │
  │ RP-1               │ 490-540 K (plage)                │
  └────────────────────┴──────────────────────────────────┘

À haute pression, T_boil augmente (selon courbe de saturation).


4.4 PROFIL DE TEMPÉRATURE DANS LA PAROI
───────────────────────────────────────────────────────────────

En régime permanent avec flux constant, le profil est LINÉAIRE:

                     q
  T(x) = T_wall_hot - ─── × x
                      k

Où:
  x = distance depuis la surface chaude (0 ≤ x ≤ e)
  T(0) = T_wall_hot
  T(e) = T_wall_cold

REPRÉSENTATION GRAPHIQUE:

  T (K)
    │
T_wh├─────●
    │      ╲
    │       ╲  Gradient = -q/k
    │        ╲
    │         ╲
T_wc├──────────●
    │          │
    └──────────┴────── x (m)
    0          e

GRADIENT DE TEMPÉRATURE:

  dT/dx = -q/k   [K/m]

Exemple numérique:
  q = 20 MW/m², k = 320 W/m·K (CuCr)
  dT/dx = -20×10⁶ / 320 = -62,500 K/m = -62.5 K/mm

Pour une épaisseur e = 2 mm:
  ΔT = 62.5 × 2 = 125 K


4.5 CONTRAINTES THERMIQUES (STRESS THERMIQUE)
───────────────────────────────────────────────────────────────

Le gradient de température crée des contraintes mécaniques 
dues à la dilatation différentielle.

CONTRAINTE THERMIQUE MAXIMALE:

              E × α × ΔT
  σ_th = ──────────────────
              2 × (1 - ν)

Où:
  E = module de Young [Pa]
  α = coefficient de dilatation thermique [1/K]
  ΔT = T_wall_hot - T_wall_cold [K]
  ν = coefficient de Poisson [-]

PROPRIÉTÉS THERMOMÉCANIQUES:
  ┌──────────────────┬────────┬────────────┬────────┐
  │ Matériau         │ E (GPa)│ α (10⁻⁶/K) │ ν      │
  ├──────────────────┼────────┼────────────┼────────┤
  │ Cuivre           │  117   │    17.0    │ 0.34   │
  │ CuCr             │  130   │    16.5    │ 0.34   │
  │ Inconel 718      │  200   │    13.0    │ 0.29   │
  │ Inox 316L        │  193   │    16.0    │ 0.27   │
  │ Niobium          │  105   │     7.3    │ 0.40   │
  │ Molybdène        │  329   │     5.0    │ 0.31   │
  │ Tungstène        │  411   │     4.5    │ 0.28   │
  └──────────────────┴────────┴────────────┴────────┘

EXEMPLE DE CALCUL:
  CuCr, ΔT = 150 K, E = 130 GPa, α = 16.5×10⁻⁶/K, ν = 0.34
  
  σ_th = 130×10⁹ × 16.5×10⁻⁶ × 150 / (2×(1-0.34))
  σ_th = 244 MPa

Cette contrainte s'ajoute aux contraintes de pression!


4.6 RÉGIME TRANSITOIRE (DÉMARRAGE/ARRÊT)
───────────────────────────────────────────────────────────────

Pendant les phases de démarrage et d'arrêt, le régime n'est 
pas permanent. Les équations deviennent:

ÉQUATION DE LA CHALEUR (1D):

  ∂T       k     ∂²T        ∂²T
  ── = ───────── × ─── = α × ───
  ∂t    ρ × Cp    ∂x²        ∂x²

Où α = k/(ρ×Cp) est la diffusivité thermique [m²/s].

TEMPS CARACTÉRISTIQUE:

  τ = e² / α

C'est le temps pour atteindre ~63% du régime permanent.

VALEURS TYPIQUES DE τ:
  ┌──────────────────┬────────────┬─────────────────────┐
  │ Matériau         │ α (mm²/s)  │ τ pour e=2mm (s)    │
  ├──────────────────┼────────────┼─────────────────────┤
  │ Cuivre           │   117      │     0.034           │
  │ CuCr             │   104      │     0.038           │
  │ Inconel 718      │    3.1     │     1.3             │
  │ Inox 316L        │    4.0     │     1.0             │
  │ Niobium          │   24.3     │     0.16            │
  │ Molybdène        │   53.7     │     0.074           │
  │ Tungstène        │   68.3     │     0.058           │
  └──────────────────┴────────────┴─────────────────────┘

IMPLICATIONS:
  - Cuivre: réponse très rapide (~35 ms)
  - Superalliages: réponse lente (~1 s)
  - Pendant le transitoire, T_wall_hot peut DÉPASSER la valeur 
    en régime permanent (overshoot)!

⚠️ RISQUE AU DÉMARRAGE:
Le coolant peut ne pas être à plein débit quand les gaz 
chauds arrivent → surchauffe critique possible!


4.7 TEMPÉRATURE ADIABATIQUE DE PAROI
───────────────────────────────────────────────────────────────

En réalité, on n'utilise pas directement T_chambre mais la 
température adiabatique de paroi T_aw.

DÉFINITION:
T_aw est la température qu'atteindrait une paroi parfaitement 
isolée (adiabatique) exposée à l'écoulement.

CALCUL:
                          γ - 1
  T_aw = T_statique × (1 + r × ───── × M²)
                            2

Où:
  r = facteur de récupération ≈ Pr^(1/3) pour turbulent
  γ = rapport des chaleurs spécifiques
  M = nombre de Mach local

VALEURS DE r:
  - Écoulement laminaire:  r ≈ Pr^(1/2) ≈ 0.85
  - Écoulement turbulent:  r ≈ Pr^(1/3) ≈ 0.89

EFFET:
  T_aw < T_stagnation (à cause des frottements visqueux)
  
Typiquement: T_aw ≈ 0.9 × T_stagnation au col


4.8 CALCUL ITÉRATIF COMPLET
───────────────────────────────────────────────────────────────

En pratique, le calcul est itératif car h_g et h_c dépendent 
des températures (via les propriétés des fluides).

ALGORITHME:
  1. Estimer T_wall_hot_init (e.g., 800 K)
  2. Calculer T_film_gaz = (T_aw + T_wall_hot)/2
  3. Calculer propriétés gaz à T_film_gaz
  4. Calculer h_g (Bartz)
  5. Estimer T_wall_cold
  6. Calculer T_film_cool = (T_wall_cold + T_cool)/2
  7. Calculer propriétés coolant à T_film_cool
  8. Calculer h_c (Dittus-Boelter ou Gnielinski)
  9. Calculer q = (T_aw - T_cool) / (1/h_g + e/k + 1/h_c)
  10. Calculer nouvelles T_wall_hot et T_wall_cold
  11. Si |T_new - T_old| > tolérance: retour à 2
  12. Sinon: CONVERGÉ!

CRITÈRE DE CONVERGENCE:
  |T_wall_hot_new - T_wall_hot_old| < 1 K

Typiquement convergence en 3-5 itérations.


5. CORRÉLATIONS CÔTÉ COOLANT - ANALYSE DÉTAILLÉE
═══════════════════════════════════════════════════════════════

Le calcul précis de h_c est crucial pour une conception fiable.
Cette section détaille les principales corrélations utilisées.


5.1 CORRÉLATION DE DITTUS-BOELTER
───────────────────────────────────────────────────────────────

C'est la corrélation la plus utilisée pour l'écoulement 
turbulent en convection forcée dans des tubes.

HISTORIQUE:
  Publiée en 1930 par F.W. Dittus et L.M.K. Boelter.
  Basée sur des expériences avec de l'eau et de l'huile.

ÉQUATION:
  Nu = 0.023 × Re^0.8 × Pr^n

Où:
  n = 0.4 si le fluide est CHAUFFÉ (T_paroi > T_fluide)
  n = 0.3 si le fluide est REFROIDI (T_paroi < T_fluide)

Dans le cas du refroidissement régénératif:
  Le coolant est chauffé → n = 0.4

DONC:
  Nu = 0.023 × Re^0.8 × Pr^0.4

CONDITIONS DE VALIDITÉ:
  ┌────────────────────────────────────────────────────────────┐
  │ • Re > 10,000 (écoulement pleinement turbulent)            │
  │ • 0.6 < Pr < 160                                           │
  │ • L/D > 10 (écoulement développé)                          │
  │ • Propriétés évaluées à T_bulk (température moyenne)       │
  │ • Flux de chaleur modéré                                   │
  │ • Parois lisses                                            │
  └────────────────────────────────────────────────────────────┘

CALCUL DE h_c:
              Nu × k_coolant
  h_c = ─────────────────────
               D_h

EXEMPLE DÉTAILLÉ:
  Données:
    Coolant: RP-1 à 350 K
    ρ = 780 kg/m³
    μ = 0.0008 Pa·s
    Cp = 2100 J/kg·K
    k = 0.12 W/m·K
    v = 25 m/s
    D_h = 3 mm = 0.003 m

  Calculs:
    Re = ρ×v×D_h/μ = 780×25×0.003/0.0008 = 73,125
    Pr = μ×Cp/k = 0.0008×2100/0.12 = 14.0
    Nu = 0.023 × 73125^0.8 × 14.0^0.4
    Nu = 0.023 × 8,547 × 2.92 = 573
    h_c = 573 × 0.12 / 0.003 = 22,920 W/m²·K

CORRECTIONS POUR CAS PARTICULIERS:

a) Correction pour L/D court (effets d'entrée):
   Nu_corrigé = Nu × (1 + (D/L)^0.7)
   
b) Correction pour T_paroi ≠ T_bulk:
   Nu_corrigé = Nu × (μ_bulk/μ_paroi)^0.14
   
c) Correction pour canaux non-circulaires:
   Utiliser D_h hydraulique, mais précision réduite.


5.2 CORRÉLATION DE GNIELINSKI
───────────────────────────────────────────────────────────────

Plus précise que Dittus-Boelter, surtout en régime transitoire.
Publiée par V. Gnielinski en 1976.

ÉQUATION PRINCIPALE:

        (f/8) × (Re - 1000) × Pr
  Nu = ─────────────────────────────────────────
        1 + 12.7 × (f/8)^0.5 × (Pr^(2/3) - 1)

Où f est le facteur de frottement de Darcy:

  f = (0.79 × ln(Re) - 1.64)^(-2)    [Équation de Petukhov]

Ou avec l'équation explicite de Colebrook-White simplifiée:

  f = 0.316 × Re^(-0.25)    [Équation de Blasius, Re < 10⁵]

CONDITIONS DE VALIDITÉ:
  ┌────────────────────────────────────────────────────────────┐
  │ • 2300 < Re < 5×10⁶                                        │
  │ • 0.5 < Pr < 2000                                          │
  │ • Plus précise que Dittus-Boelter                          │
  │ • Valide aussi en régime transitoire (Re > 2300)           │
  │ • Propriétés évaluées à T_bulk                             │
  └────────────────────────────────────────────────────────────┘

EXEMPLE DÉTAILLÉ:
  Reprenons l'exemple précédent (RP-1, Re = 73,125, Pr = 14.0)

  Calculs:
    f = (0.79×ln(73125) - 1.64)^(-2)
    f = (0.79×11.2 - 1.64)^(-2)
    f = (8.85 - 1.64)^(-2)
    f = 7.21^(-2) = 0.0192

    Numérateur = (0.0192/8) × (73125-1000) × 14.0
                = 0.0024 × 72125 × 14.0 = 2424

    Dénominateur = 1 + 12.7 × (0.0024)^0.5 × (14.0^0.667 - 1)
                 = 1 + 12.7 × 0.049 × (5.19 - 1)
                 = 1 + 12.7 × 0.049 × 4.19
                 = 1 + 2.61 = 3.61

    Nu = 2424 / 3.61 = 671

    h_c = 671 × 0.12 / 0.003 = 26,840 W/m²·K

COMPARAISON:
  Dittus-Boelter: h_c = 22,920 W/m²·K
  Gnielinski:     h_c = 26,840 W/m²·K (17% plus élevé)

Gnielinski est généralement plus précise (+/-10% vs +/-25%).


5.3 RÉGIME LAMINAIRE (Re < 2300)
───────────────────────────────────────────────────────────────

⚠️ À ÉVITER DANS LES MOTEURS-FUSÉES!
Le transfert thermique est très faible en laminaire.

CAS DU FLUX CONSTANT:
  Nu = 4.36 (tube circulaire)
  Nu = 3.66 (température de paroi constante)

POUR CANAUX RECTANGULAIRES:
  ┌────────────────┬───────────────────────────────────────────┐
  │ Rapport a/b    │ Nu (flux constant)                        │
  ├────────────────┼───────────────────────────────────────────┤
  │ 1.0 (carré)    │ 3.61                                      │
  │ 2.0            │ 4.12                                      │
  │ 4.0            │ 5.35                                      │
  │ 8.0            │ 6.49                                      │
  │ ∞ (plaques)    │ 8.24                                      │
  └────────────────┴───────────────────────────────────────────┘

CONSÉQUENCE:
En laminaire: h_c ≈ 100-500 W/m²·K seulement!
C'est 10 à 100 fois moins qu'en turbulent.

→ Toujours concevoir pour Re > 10,000 minimum.


5.4 RÉGIME TRANSITOIRE (2300 < Re < 10000)
───────────────────────────────────────────────────────────────

Zone difficile à prédire avec précision.

APPROCHE RECOMMANDÉE:
  Utiliser Gnielinski (valide dès Re > 2300).

ALTERNATIVE - Interpolation:
  Nu = Nu_lam + (Nu_turb - Nu_lam) × ((Re - 2300)/(10000 - 2300))

RECOMMANDATION:
  Éviter cette zone! Concevoir pour Re > 10,000.


5.5 ÉBULLITION SOUS-REFROIDIE (SUBCOOLED BOILING)
───────────────────────────────────────────────────────────────

Si T_paroi > T_saturation mais T_bulk < T_saturation:
  → Formation de bulles à la paroi
  → Les bulles se condensent dans le cœur du fluide
  → Transfert thermique AMÉLIORÉ!

CORRÉLATION DE CHEN (1966):
  h_total = h_convection + h_ébullition

  h_ébullition = S × h_nucleation

Où S est un facteur de suppression tenant compte de la 
turbulence qui inhibe la nucléation.

AVANTAGES:
  ✅ h peut augmenter de 2 à 5 fois
  ✅ Utilisé intentionnellement dans certains moteurs

RISQUES:
  ❌ Si T_bulk approche T_sat → ébullition en masse
  ❌ DNB (Departure from Nucleate Boiling) → destruction
  ❌ Instabilités hydrauliques possibles


5.6 EFFETS DE LA GÉOMÉTRIE DES CANAUX
───────────────────────────────────────────────────────────────

La géométrie des canaux influence fortement h_c.

TYPES DE CANAUX COURANTS:
  ┌────────────────────────────────────────────────────────────┐
  │                                                            │
  │  ┌──┐  ┌──┐  ┌──┐     Canaux rectangulaires               │
  │  │  │  │  │  │  │     (fraisage ou impression 3D)         │
  │  │  │  │  │  │  │                                          │
  │  └──┘  └──┘  └──┘                                          │
  │                                                            │
  │  ╭──╮  ╭──╮  ╭──╮     Canaux circulaires                  │
  │  │  │  │  │  │  │     (perçage ou tubes)                  │
  │  ╰──╯  ╰──╯  ╰──╯                                          │
  │                                                            │
  │  /\/\/\/\/\/\/\/\     Canaux hélicoïdaux                  │
  │  \/\/\/\/\/\/\/\/     (meilleur mélange)                  │
  │                                                            │
  └────────────────────────────────────────────────────────────┘

DIAMÈTRE HYDRAULIQUE:
  Canal rectangulaire:  D_h = 4×w×h / (2w + 2h) = 2wh/(w+h)
  Canal circulaire:     D_h = D
  Anneau:               D_h = D_ext - D_int

EFFET DU RAPPORT D'ASPECT (h/w):
  ┌────────────────┬───────────────────────────────────────────┐
  │ h/w            │ Effet                                     │
  ├────────────────┼───────────────────────────────────────────┤
  │ h/w ≈ 1        │ Optimal pour h_c                          │
  │ h/w > 3        │ Canaux étroits, h_c réduit aux coins      │
  │ h/w < 0.3      │ Canaux larges/plats, efficace             │
  └────────────────┴───────────────────────────────────────────┘

EFFET DU NOMBRE DE CANAUX:
  Plus de canaux → Plus petits D_h → Re plus bas MAIS D_h plus petit
  
  h_c ∝ Nu × k / D_h
  
  Si D_h ↓ de moitié:
    - Re ↓ de moitié
    - Nu ↓ d'environ 40% (∝ Re^0.8)
    - Mais D_h ↓ de 50%
    - Net: h_c ↑ d'environ 20%

OPTIMISATION:
  Compromis entre:
  - h_c élevé (petits canaux)
  - Pertes de charge acceptables (grands canaux)
  - Fabricabilité (dépend du procédé)


5.7 PERTES DE CHARGE DANS LES CANAUX
───────────────────────────────────────────────────────────────

Les pertes de charge sont liées au transfert thermique:
  Plus de turbulence → meilleur h_c MAIS plus de ΔP

ÉQUATION DE DARCY-WEISBACH:
            f × L × ρ × v²
  ΔP = ─────────────────────
             2 × D_h

Où:
  f = facteur de frottement (Darcy)
  L = longueur du canal [m]
  ρ = masse volumique [kg/m³]
  v = vitesse [m/s]
  D_h = diamètre hydraulique [m]

FACTEUR DE FROTTEMENT:
  Laminaire:    f = 64/Re
  Turbulent:    f ≈ 0.316 × Re^(-0.25)  (Blasius)
  Turbulent:    f = (0.79×ln(Re) - 1.64)^(-2)  (Petukhov)

ORDRES DE GRANDEUR:
  ┌────────────────────┬──────────────────────────────────┐
  │ Configuration      │ ΔP typique (bar)                 │
  ├────────────────────┼──────────────────────────────────┤
  │ RP-1 dans canaux   │ 10 - 50                          │
  │ LH2 dans canaux    │ 5 - 30                           │
  │ LOX dans canaux    │ 10 - 40                          │
  └────────────────────┴──────────────────────────────────┘

PUISSANCE DE POMPAGE:
  P_pompe = ΔP × Q = ΔP × A × v

Cette puissance est "perdue" et doit être fournie par la 
turbopompe → impact sur les performances globales.


5.8 VALEURS TYPIQUES DE h_c - TABLEAU COMPLET
───────────────────────────────────────────────────────────────

  ┌────────────────┬──────────────┬───────────┬───────────────┐
  │ Coolant        │ T (K)        │ v (m/s)   │ h_c (W/m²·K)  │
  ├────────────────┼──────────────┼───────────┼───────────────┤
  │ LH2            │ 25           │ 50        │ 50,000-150,000│
  │ LH2            │ 30           │ 100       │ 80,000-200,000│
  │ LOX            │ 100          │ 20        │ 15,000-40,000 │
  │ LOX            │ 100          │ 40        │ 25,000-60,000 │
  │ CH4            │ 150          │ 20        │ 10,000-30,000 │
  │ CH4            │ 150          │ 40        │ 18,000-50,000 │
  │ RP-1           │ 300          │ 15        │ 5,000-15,000  │
  │ RP-1           │ 350          │ 25        │ 10,000-25,000 │
  │ RP-1           │ 400          │ 30        │ 15,000-35,000 │
  │ C2H5OH         │ 300          │ 20        │ 8,000-20,000  │
  │ H2O            │ 350          │ 10        │ 15,000-40,000 │
  │ H2O            │ 350          │ 30        │ 30,000-80,000 │
  │ N2H4           │ 320          │ 15        │ 8,000-22,000  │
  └────────────────┴──────────────┴───────────┴───────────────┘

CLASSEMENT PAR CAPACITÉ DE REFROIDISSEMENT:
  1. LH2 (meilleur! Cp très élevé, k élevé, μ faible)
  2. H2O (excellent mais T_boil basse)
  3. LOX (bon mais corrosif, limites de T)
  4. CH4 (très bon, propre, compatible)
  5. C2H5OH (bon, simple)
  6. RP-1 (correct mais cokéfaction)
  7. N2H4 (toxique, éviter si possible)


6. ÉPAISSEUR CRITIQUE, SERVICE ET ABLATION
═══════════════════════════════════════════════════════════════

Cette section traite des critères d'épaisseur et du 
phénomène d'ablation pour les parois trop épaisses.


6.1 ÉPAISSEUR CRITIQUE DE FUSION (e_melt)
───────────────────────────────────────────────────────────────

L'épaisseur critique est l'épaisseur MAXIMALE pour laquelle 
T_wall_hot reste inférieure à T_melt (température de fusion).

DÉRIVATION:
  En régime permanent: T_wall_hot = T_wall_cold + q×e/k
  
  Pour éviter la fusion: T_wall_hot ≤ T_melt
  
  Donc: T_wall_cold + q×e/k ≤ T_melt
  
  Résolvant pour e:
  
         k × (T_melt - T_wall_cold)
  e ≤ ───────────────────────────────
                    q

FORMULE FINALE:
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │              k × (T_melt - T_wall_cold)                 │
  │   e_melt = ─────────────────────────────────            │
  │                        q                                │
  │                                                         │
  └─────────────────────────────────────────────────────────┘

INTERPRÉTATION:
  - Si e < e_melt: la paroi NE FOND PAS ✅
  - Si e = e_melt: T_wall_hot = T_melt exactement (limite)
  - Si e > e_melt: la surface FOND ❌

FACTEURS FAVORABLES (e_melt élevé = plus de marge):
  ✅ k élevé (bonne conductivité)
  ✅ T_melt élevé (matériau réfractaire)
  ✅ T_wall_cold bas (bon refroidissement)
  ✅ q faible (position loin du col)

EXEMPLE NUMÉRIQUE - CuCr:
  k = 320 W/m·K
  T_melt = 1350 K
  T_wall_cold = 600 K
  q = 25 MW/m² (au col)

  e_melt = 320 × (1350 - 600) / 25×10⁶
  e_melt = 320 × 750 / 25×10⁶
  e_melt = 240,000 / 25×10⁶
  e_melt = 0.0096 m = 9.6 mm

  → La paroi peut faire jusqu'à 9.6 mm avant de fondre.

EXEMPLE - COMPARAISON MATÉRIAUX:
  Même conditions: T_wc = 600 K, q = 25 MW/m²
  
  ┌──────────────────┬────────┬─────────┬──────────────────┐
  │ Matériau         │ k      │ T_melt  │ e_melt (mm)      │
  ├──────────────────┼────────┼─────────┼──────────────────┤
  │ Cuivre           │ 385    │ 1358 K  │ 11.7             │
  │ CuCr             │ 320    │ 1350 K  │ 9.6              │
  │ Inconel 718      │ 11.4   │ 1609 K  │ 0.46             │
  │ Inox 316L        │ 16.3   │ 1673 K  │ 0.70             │
  │ AlSi10Mg         │ 130    │ 870 K   │ 1.4              │
  │ Niobium          │ 53.7   │ 2750 K  │ 4.6              │
  │ Molybdène        │ 138    │ 2896 K  │ 12.7             │
  │ Tungstène        │ 173    │ 3695 K  │ 21.4             │
  └──────────────────┴────────┴─────────┴──────────────────┘

OBSERVATIONS:
  - Cuivre et alliages: e_melt ≈ 10 mm (excellent)
  - Superalliages: e_melt < 1 mm (faible conductivité!)
  - Réfractaires: e_melt élevé grâce à T_melt très haut


6.2 ÉPAISSEUR DE SERVICE (e_max)
───────────────────────────────────────────────────────────────

En pratique, on ne veut pas atteindre T_melt mais rester 
en dessous de T_max_service pour éviter:
  - Perte de propriétés mécaniques
  - Fluage (déformation lente sous charge)
  - Oxydation accélérée
  - Changements métallurgiques

FORMULE:

         k × (T_max_service - T_wall_cold)
  e_max = ───────────────────────────────────
                        q

TEMPÉRATURES MAX DE SERVICE:
  ┌──────────────────┬──────────────────────────────────────┐
  │ Matériau         │ T_max_service (K) et raison          │
  ├──────────────────┼──────────────────────────────────────┤
  │ Cuivre           │ 800-900 K (ramollissement)           │
  │ CuCr             │ 1000-1050 K (perte de dureté)        │
  │ CuCrZr           │ 1050-1100 K                          │
  │ GRCop-84         │ 1100-1200 K (excellent!)             │
  │ Inconel 718      │ 1100-1200 K (fluage)                 │
  │ Inconel 625      │ 1150-1250 K                          │
  │ Inox 316L        │ 1000-1100 K                          │
  │ AlSi10Mg         │ 500-573 K (très bas!)                │
  │ Niobium          │ 2000-2200 K (oxydation si pas vide)  │
  │ Molybdène        │ 2200-2400 K                          │
  │ Tungstène        │ 2800-3000 K                          │
  └──────────────────┴──────────────────────────────────────┘

MARGE DE SÉCURITÉ:
  Typiquement: T_design = T_max_service - 50 à 100 K

EXEMPLE - CuCr:
  k = 320 W/m·K
  T_max = 1050 K
  T_wall_cold = 600 K
  q = 25 MW/m²

  e_max = 320 × (1050 - 600) / 25×10⁶
  e_max = 320 × 450 / 25×10⁶
  e_max = 5.76 mm

  → Épaisseur max pour rester sous T_max = 5.76 mm


6.3 PROCESSUS D'ABLATION
───────────────────────────────────────────────────────────────

Que se passe-t-il si l'épaisseur initiale e₀ > e_melt?

RÉPONSE: La surface fond et s'érode jusqu'à atteindre e_melt.

MÉCANISME PHYSIQUE DÉTAILLÉ:

  INSTANT t = 0 (allumage):
  ┌────────────────────────────────────────────────────────────┐
  │  Gaz chauds arrivent                                       │
  │  T_wall_hot commence à monter rapidement                   │
  │  (régime transitoire)                                      │
  └────────────────────────────────────────────────────────────┘
           ↓
  INSTANT t = τ (temps caractéristique):
  ┌────────────────────────────────────────────────────────────┐
  │  T_wall_hot atteint le régime "quasi-permanent"            │
  │  Si e₀ > e_melt: T_wall_hot > T_melt                       │
  │  → La surface commence à FONDRE                            │
  └────────────────────────────────────────────────────────────┘
           ↓
  PHASE D'ABLATION:
  ┌────────────────────────────────────────────────────────────┐
  │  • Métal fondu à la surface                                │
  │  • Gouttelettes emportées par le flux gazeux               │
  │  • Épaisseur diminue progressivement                       │
  │  • T_wall_hot reste ≈ T_melt (latent heat)                 │
  └────────────────────────────────────────────────────────────┘
           ↓
  ÉQUILIBRE (t >> τ):
  ┌────────────────────────────────────────────────────────────┐
  │  e final = e_melt                                          │
  │  T_wall_hot = T_melt                                       │
  │  Plus de fusion, état stable                               │
  └────────────────────────────────────────────────────────────┘


6.4 ÉPAISSEUR SACRIFICIELLE ET MASSE PERDUE
───────────────────────────────────────────────────────────────

DÉFINITION:

  e_sacrificielle = e₀ - e_melt   (si e₀ > e_melt)
  e_sacrificielle = 0             (si e₀ ≤ e_melt)

C'est l'épaisseur qui va fondre et être emportée.

MASSE PERDUE PAR UNITÉ DE SURFACE:

  Δm/A = ρ_métal × e_sacrificielle   [kg/m²]

MASSE TOTALE PERDUE:

  Δm = ρ_métal × A_surface × e_sacrificielle   [kg]

EXEMPLE NUMÉRIQUE:
  Données:
    Matériau: CuCr
    ρ = 8900 kg/m³
    e₀ = 12 mm (épaisseur initiale)
    e_melt = 9.6 mm (calculé précédemment)
    A_surface = 0.05 m² (surface au col)

  Calculs:
    e_sacrificielle = 12 - 9.6 = 2.4 mm = 0.0024 m
    Δm = 8900 × 0.05 × 0.0024 = 1.07 kg

  → 1.07 kg de cuivre va fondre et être éjecté!


6.5 TEMPS D'ABLATION
───────────────────────────────────────────────────────────────

Combien de temps dure l'ablation?

BILAN ÉNERGÉTIQUE:
L'énergie pour fondre e_sac d'épaisseur sur 1 m² est:

  E_fusion = ρ × e_sac × (Cp × (T_melt - T₀) + L_fusion)

Où L_fusion est la chaleur latente de fusion.

CHALEUR LATENTE DE FUSION:
  ┌──────────────────┬──────────────────────────────────────┐
  │ Matériau         │ L_fusion (kJ/kg)                     │
  ├──────────────────┼──────────────────────────────────────┤
  │ Cuivre           │ 205                                  │
  │ Aluminium        │ 397                                  │
  │ Fer/Acier        │ 247                                  │
  │ Nickel           │ 298                                  │
  │ Niobium          │ 285                                  │
  │ Molybdène        │ 390                                  │
  │ Tungstène        │ 192                                  │
  └──────────────────┴──────────────────────────────────────┘

FLUX DISPONIBLE POUR LA FUSION:
Le flux "excédentaire" qui cause la fusion est:

  q_fusion = q_entrant - q_évacué_à_T_melt

TEMPS D'ABLATION (approximation):

  t_ablation ≈ ρ × e_sac × L_fusion / q_fusion

En pratique: quelques secondes à quelques dizaines de secondes.


6.6 QUAND L'ABLATION EST-ELLE ACCEPTABLE?
───────────────────────────────────────────────────────────────

L'ablation peut être:
  - ACCEPTÉE volontairement (moteurs ablatifs)
  - TOLÉRÉE accidentellement
  - CATASTROPHIQUE

CAS 1 - MOTEURS ABLATIFS (acceptable):
  ┌────────────────────────────────────────────────────────────┐
  │ • Conception prévue pour l'ablation                        │
  │ • Matériau sacrificiel (phénolique, silice)               │
  │ • Durée de fonctionnement limitée (quelques secondes)      │
  │ • Pas de refroidissement régénératif                       │
  │ • Simple, léger, fiable                                    │
  │ • Exemple: moteurs de missiles, boosters                   │
  └────────────────────────────────────────────────────────────┘

CAS 2 - ABLATION TOLÉRÉE:
  ┌────────────────────────────────────────────────────────────┐
  │ • Légère sur-épaisseur de sécurité                         │
  │ • Ablation minime (< 0.5 mm)                               │
  │ • Moteur reste fonctionnel après ablation                  │
  │ • Vérifié par calcul et tests                              │
  └────────────────────────────────────────────────────────────┘

CAS 3 - ABLATION CATASTROPHIQUE (à éviter!):
  ┌────────────────────────────────────────────────────────────┐
  │ ❌ Percement de la paroi → fuite de gaz chauds             │
  │ ❌ Contamination du coolant par métal fondu                │
  │ ❌ Modification de la géométrie → perte de performances    │
  │ ❌ Débris métalliques endommageant l'injecteur             │
  │ ❌ Explosion possible!                                      │
  └────────────────────────────────────────────────────────────┘


6.7 DIMENSIONNEMENT POUR ÉVITER L'ABLATION
───────────────────────────────────────────────────────────────

RÈGLE DE CONCEPTION:

  e_design < e_max < e_melt

Où:
  e_design = épaisseur choisie
  e_max = épaisseur pour T_wall_hot = T_max_service
  e_melt = épaisseur pour T_wall_hot = T_melt

MARGES RECOMMANDÉES:

  e_design = 0.7 à 0.8 × e_max

Cette marge couvre:
  - Incertitudes sur h_g (±20-30%)
  - Variations locales de flux
  - Transitoires (démarrage/arrêt)
  - Vieillissement du matériau

PROCÉDURE DE DIMENSIONNEMENT:
  1. Calculer q_max (au col)
  2. Choisir le matériau (k, T_melt, T_max)
  3. Calculer e_melt et e_max
  4. Choisir e_design avec marge
  5. Vérifier résistance mécanique (pression)
  6. Vérifier stress thermique
  7. Itérer si nécessaire


6.8 CARTE THERMIQUE ET VARIATION AXIALE
───────────────────────────────────────────────────────────────

Le flux q varie le long du moteur:
  - Maximum au COL
  - Décroissant vers la chambre et le divergent

CONSÉQUENCE:
  e_melt et e_max VARIENT aussi le long du moteur!

APPROCHE DE CONCEPTION:
  ┌────────────────────────────────────────────────────────────┐
  │ OPTION 1: Épaisseur constante                              │
  │  + Simple à fabriquer                                      │
  │  - Sur-dimensionné dans chambre et divergent               │
  │  - Sous-dimensionné potentiel au col                       │
  ├────────────────────────────────────────────────────────────┤
  │ OPTION 2: Épaisseur variable                               │
  │  + Optimisé thermiquement                                  │
  │  + Masse minimale                                          │
  │  - Fabrication plus complexe                               │
  │  - Usinage ou impression 3D                                │
  ├────────────────────────────────────────────────────────────┤
  │ OPTION 3: Matériau variable (hybride)                      │
  │  + Optimal pour chaque zone                                │
  │  + CuCr au col, Inconel dans divergent, etc.               │
  │  - Joints complexes                                        │
  │  - Dilatation différentielle                               │
  └────────────────────────────────────────────────────────────┘

PROFIL TYPIQUE D'UN MOTEUR MODERNE:
  - Chambre: e = 3-5 mm (CuCr ou GRCop)
  - Convergent/Col: e = 1.5-3 mm (minimum pour q max)
  - Divergent: e = 2-4 mm (CuCr) ou transition vers acier


7. PROPRIÉTÉS DES MATÉRIAUX POUR MOTEURS-FUSÉES
═══════════════════════════════════════════════════════════════

Cette section détaille les matériaux utilisés pour les parois 
de chambres de combustion et tuyères à refroidissement régénératif.


7.1 TABLEAU RÉCAPITULATIF DES PROPRIÉTÉS
───────────────────────────────────────────────────────────────

  ┌──────────────────┬───────┬─────────┬─────────┬─────────┐
  │ Matériau         │k W/m·K│T_melt K │T_max K  │ρ kg/m³  │
  ├──────────────────┼───────┼─────────┼─────────┼─────────┤
  │ Cuivre (Cu)      │  385  │  1358   │   900   │  8960   │
  │ CuCr (C18200)    │  320  │  1350   │  1050   │  8900   │
  │ CuCrZr (C18150)  │  315  │  1355   │  1100   │  8890   │
  │ GRCop-84 (NASA)  │  298  │  1350   │  1200   │  8870   │
  │ GRCop-42         │  310  │  1355   │  1150   │  8850   │
  │ AlSi10Mg (SLM)   │  130  │   870   │   573   │  2670   │
  │ Al 6061-T6       │  167  │   925   │   573   │  2700   │
  │ Inconel 718      │ 11.4  │  1609   │  1200   │  8190   │
  │ Inconel 625      │  9.8  │  1623   │  1250   │  8440   │
  │ Inconel X-750    │ 12.0  │  1620   │  1150   │  8280   │
  │ Haynes 230       │  8.9  │  1635   │  1350   │  8970   │
  │ Haynes 188       │ 10.4  │  1635   │  1320   │  8980   │
  │ Inox 316L        │ 16.3  │  1673   │  1100   │  8000   │
  │ Inox 304L        │ 16.2  │  1673   │  1050   │  7900   │
  │ Ti-6Al-4V        │  6.7  │  1933   │   700   │  4430   │
  │ Niobium (Nb)     │ 53.7  │  2750   │  2200   │  8570   │
  │ C103 (Nb alloy)  │ 44.2  │  2685   │  2000   │  8860   │
  │ Molybdène (Mo)   │  138  │  2896   │  2400   │ 10280   │
  │ TZM (Mo alloy)   │  120  │  2895   │  2500   │ 10220   │
  │ Tungstène (W)    │  173  │  3695   │  3000   │ 19300   │
  │ W-Re (W alloy)   │  100  │  3450   │  2800   │ 19700   │
  │ Rhénium (Re)     │ 47.9  │  3459   │  2800   │ 21020   │
  │ Tantale (Ta)     │ 57.5  │  3290   │  2600   │ 16650   │
  │ Graphite         │  120  │  3900*  │  3500   │  2200   │
  │ C/C Composite    │ 50-150│  3900*  │  3200   │  1800   │
  │ SiC (CVD)        │  120  │  3100*  │  2000   │  3210   │
  └──────────────────┴───────┴─────────┴─────────┴─────────┘
  * Sublime au lieu de fondre


7.2 ALLIAGES DE CUIVRE - LES CHAMPIONS DU REFROIDISSEMENT
───────────────────────────────────────────────────────────────

Les alliages de cuivre sont les matériaux de choix pour les 
zones à haut flux thermique (chambre, col) grâce à leur 
excellente conductivité thermique.

A) CUIVRE PUR (Cu - C10200, OFHC)

  Composition: Cu > 99.95%
  
  Propriétés:
    k = 385-401 W/m·K (le meilleur!)
    T_melt = 1358 K (1085°C)
    T_max = 800-900 K (ramollissement)
    σ_yield @ 20°C = 70 MPa (très faible)
    σ_yield @ 500°C = 35 MPa
  
  ✅ Avantages:
    - Conductivité maximale
    - Facile à usiner
    - Bon marché
  
  ❌ Inconvénients:
    - Très faible résistance mécanique
    - Ramollit rapidement à T > 500 K
    - Fluage important
  
  Utilisation:
    - Rarement seul pour moteurs haute pression
    - Parfois pour petits moteurs < 10 bar
    - Inserts ou revêtements

B) CUIVRE-CHROME (CuCr - C18200)

  Composition: Cu + 0.6-1.2% Cr
  
  Propriétés:
    k = 315-324 W/m·K
    T_melt = 1350 K
    T_max = 1000-1050 K
    σ_yield @ 20°C = 310-450 MPa (traité)
    σ_yield @ 500°C = 180 MPa
    E = 130 GPa
    α = 16.5 × 10⁻⁶ /K
  
  ✅ Avantages:
    - Excellent compromis k / résistance
    - Très bien maîtrisé industriellement
    - Soudable (TIG, EBW, FSW)
    - Disponible et économique
  
  ❌ Inconvénients:
    - Perd sa dureté si surchauffe > 800 K
    - Recristallisation possible
  
  Traitement thermique:
    - Mise en solution: 980°C, trempe eau
    - Vieillissement: 450-500°C, 2-4h
  
  Utilisation:
    - Merlin (SpaceX)
    - RS-25 SSME (NASA/Aerojet)
    - Vulcain (ESA)
    - RD-180, RD-191 (Energomash)
    - TRÈS COURANT!

C) CUIVRE-CHROME-ZIRCONIUM (CuCrZr - C18150)

  Composition: Cu + 0.5-1.5% Cr + 0.05-0.15% Zr
  
  Propriétés:
    k = 310-320 W/m·K
    T_melt = 1355 K
    T_max = 1050-1100 K
    σ_yield @ 20°C = 380-500 MPa
    σ_yield @ 600°C = 220 MPa
  
  ✅ Avantages:
    - Meilleure tenue à chaud que CuCr
    - Résistance au fluage améliorée
    - Zr stabilise les précipités de Cr
  
  ❌ Inconvénients:
    - Plus cher que CuCr
    - Traitement thermique critique
  
  Utilisation:
    - RD-170/171 (Energomash)
    - Moteurs russes haute performance
    - Réacteurs de fusion (ITER)

D) GRCop-84 (NASA Glenn Research Center)

  Composition: Cu + 8% Cr + 4% Nb (nano-dispersions)
  
  Propriétés:
    k = 285-300 W/m·K
    T_melt = 1350 K
    T_max = 1150-1200 K
    σ_yield @ 20°C = 250 MPa
    σ_yield @ 800°C = 150 MPa (EXCELLENT!)
    Résistance au fluage: 100× meilleure que CuCr
  
  ✅ Avantages:
    - Excellente résistance à haute T
    - Résistance au fluage exceptionnelle
    - Stable microstructuralement
    - Idéal pour impression 3D (SLM/DMLS)
  
  ❌ Inconvénients:
    - Développé par NASA, accès limité
    - Fabrication spécialisée
    - Plus cher
  
  Fabrication:
    - Atomisation plasma
    - Impression 3D (SLM avec laser 400W+)
    - HIP (Hot Isostatic Pressing)
  
  Utilisation:
    - RS-25 upgrades (SLS)
    - Relativity Space (Terran 1, Aeon)
    - Virgin Orbit (NewtonThree)
    - Aerojet Rocketdyne (RL10 upgrades)

E) GRCop-42 (variante)

  Composition: Cu + 4% Cr + 2% Nb
  
  Propriétés:
    k = 305-315 W/m·K (meilleur que GRCop-84)
    T_max = 1100-1150 K
    Compromis entre k et résistance haute T
  
  Utilisation:
    - Applications où k est prioritaire
    - Développement en cours


7.3 SUPERALLIAGES BASE NICKEL
───────────────────────────────────────────────────────────────

Les superalliages sont utilisés pour les zones moins sollicitées 
thermiquement mais nécessitant haute résistance mécanique.

A) INCONEL 718

  Composition: Ni-52%, Cr-19%, Fe-18%, Nb-5%, Mo-3%
  
  Propriétés:
    k = 11.4 W/m·K (faible!)
    T_melt = 1609 K
    T_max = 1100-1200 K
    σ_yield @ 20°C = 1035-1240 MPa (très élevé!)
    σ_yield @ 650°C = 1000 MPa
    E = 200 GPa
  
  ✅ Avantages:
    - Excellente résistance mécanique
    - Bonne résistance à l'oxydation
    - Soudable
    - Bien maîtrisé pour impression 3D
  
  ❌ Inconvénients:
    - Conductivité très faible (11× moins que CuCr)
    - Limite thermique malgré T_melt élevé
    - Usinage difficile
  
  Utilisation:
    - Structures de tuyères
    - Brides, collecteurs
    - Divergent (partie froide)
    - Chambres basse pression

B) INCONEL 625

  Composition: Ni-62%, Cr-22%, Mo-9%, Nb-3.5%
  
  Propriétés:
    k = 9.8 W/m·K
    T_melt = 1623 K
    T_max = 1200-1250 K
    σ_yield @ 20°C = 460-760 MPa
    Excellente résistance à la corrosion
  
  ✅ Avantages:
    - Meilleure résistance corrosion que 718
    - Soudable sans traitement post-soudure
    - Bon pour environnements agressifs
  
  Utilisation:
    - Divergent de tuyères
    - Environnements corrosifs
    - Propergols agressifs (N2O4, HNO3)

C) HAYNES 230

  Composition: Ni-57%, Cr-22%, W-14%, Mo-2%
  
  Propriétés:
    k = 8.9 W/m·K
    T_melt = 1635 K
    T_max = 1300-1350 K (excellent!)
    σ_yield @ 20°C = 390 MPa
    Résistance à l'oxydation exceptionnelle
  
  Utilisation:
    - Tuyères haute température
    - Applications spatiales réutilisables
    - Turbines, échangeurs

D) HAYNES 188

  Composition: Co-39%, Ni-22%, Cr-22%, W-14%
  
  Propriétés:
    k = 10.4 W/m·K
    T_max = 1300-1320 K
    Excellente résistance à l'oxydation
  
  Utilisation:
    - Tuyères pour moteurs réutilisables
    - Applications haute température longue durée


7.4 ALLIAGES D'ALUMINIUM
───────────────────────────────────────────────────────────────

Utilisés pour les petits moteurs ou prototypes grâce à leur 
légèreté et facilité d'usinage/impression 3D.

A) AlSi10Mg (impression 3D)

  Composition: Al + 10% Si + 0.3% Mg
  
  Propriétés:
    k = 120-140 W/m·K
    T_melt = 870 K (597°C) - TRÈS BAS!
    T_max = 473-573 K (200-300°C)
    ρ = 2670 kg/m³ (léger!)
    σ_yield @ 20°C = 230-280 MPa (SLM)
  
  ✅ Avantages:
    - Très léger (3× moins que CuCr)
    - Excellente imprimabilité 3D
    - Conductivité correcte
    - Économique
    - Prototypage rapide
  
  ❌ Inconvénients:
    - T_max TRÈS BASSE! (~300°C)
    - Fond facilement
    - Limité aux faibles flux
    - Résistance chute rapidement avec T
  
  ⚠️ ATTENTION:
    SEULEMENT pour moteurs faible pression/flux
    ou zones très bien refroidies!
  
  Utilisation:
    - Prototypes
    - Petits moteurs (< 5 kN)
    - Moteurs basse pression
    - Zones froides (divergent loin)

B) Al 6061-T6

  Composition: Al + 1% Mg + 0.6% Si + 0.3% Cu
  
  Propriétés:
    k = 167 W/m·K
    T_melt = 925 K
    T_max = 473-573 K
    σ_yield = 275 MPa
  
  Utilisation:
    - Structures, brides
    - Pas pour parois chaudes!


7.5 MÉTAUX RÉFRACTAIRES
───────────────────────────────────────────────────────────────

Pour les tuyères à rayonnement ou hautes températures extrêmes.
Utilisés principalement pour les divergents non refroidis.

A) NIOBIUM (Nb) et C103

  Nb pur:
    k = 53.7 W/m·K
    T_melt = 2750 K
    T_max = 2000-2200 K (sous vide!)
    ρ = 8570 kg/m³
  
  C103 (Nb-10Hf-1Ti):
    k = 44 W/m·K
    T_melt = 2685 K
    T_max = 1800-2000 K
    σ_yield @ 20°C = 310 MPa
    σ_yield @ 1200°C = 140 MPa
  
  ⚠️ OXYDATION:
    Nb s'oxyde catastrophiquement à T > 700 K dans l'air!
    → Utilisable uniquement dans le VIDE spatial
    → Ou avec revêtement siliciure (MoSi2, WSi2)
  
  Revêtements protecteurs:
    - R512E (Si-20Cr-20Fe)
    - R512A (Si-20Cr-5Ti-5Fe)
    - Durée: quelques heures à 1600 K
  
  Utilisation:
    - Divergents de moteurs spatiaux
    - Apollo LM Descent Engine
    - RL10 (extension de tuyère)
    - Moteurs d'apogée

B) MOLYBDÈNE (Mo) et TZM

  Mo pur:
    k = 138 W/m·K (excellent pour réfractaire!)
    T_melt = 2896 K
    T_max = 2200-2400 K
    ρ = 10280 kg/m³
  
  TZM (Mo-0.5Ti-0.08Zr):
    k = 115-125 W/m·K
    T_melt = 2895 K
    T_max = 2300-2500 K
    σ_yield @ 20°C = 700 MPa
    σ_yield @ 1000°C = 420 MPa
  
  ⚠️ OXYDATION:
    Forme MoO3 volatil à T > 800 K dans l'air
    → "Peste du molybdène"
    → Vide ou atmosphère inerte obligatoire
  
  Utilisation:
    - Inserts de col (vide spatial)
    - Tuyères haute température
    - Propulsion électrique (résistojets)

C) TUNGSTÈNE (W) et W-Re

  W pur:
    k = 173 W/m·K
    T_melt = 3695 K (le plus haut des métaux!)
    T_max = 2800-3000 K
    ρ = 19300 kg/m³ (très lourd!)
    σ_yield @ 20°C = 700-1000 MPa
  
  W-Re (W + 3-25% Re):
    k = 80-120 W/m·K
    T_melt = 3200-3450 K
    Meilleure ductilité que W pur
    σ_yield @ 1500°C = 300 MPa
  
  ⚠️ CARACTÉRISTIQUES:
    - Très fragile à température ambiante
    - DBTT (ductile-brittle) ≈ 400°C
    - Usinage très difficile (EDM)
    - Oxyde à T > 700 K dans l'air
  
  Utilisation:
    - Inserts de col (cas extrêmes)
    - Propulsion électrique (résistojets, arcjets)
    - Protection thermique

D) RHÉNIUM (Re)

  Propriétés:
    k = 47.9 W/m·K
    T_melt = 3459 K
    T_max = 2600-2800 K
    ρ = 21020 kg/m³ (2ème plus dense)
  
  ✅ Avantages:
    - Ductile à toutes températures
    - Pas de DBTT comme W
    - Excellente résistance au fluage
  
  ❌ Inconvénients:
    - EXTRÊMEMENT cher (~5000 $/kg)
    - Rare (production mondiale: 50 tonnes/an)
    - Lourd
  
  Utilisation:
    - Revêtement sur W ou Ir
    - Applications spatiales critiques
    - Très limité (coût prohibitif)


7.6 MATÉRIAUX CÉRAMIQUES ET COMPOSITES
───────────────────────────────────────────────────────────────

A) GRAPHITE

  Propriétés:
    k = 80-150 W/m·K (selon orientation)
    T_sublime = 3900 K (pas de fusion!)
    T_max = 3200-3500 K (vide)
    ρ = 1800-2200 kg/m³ (léger!)
  
  ⚠️ OXYDATION:
    Brûle à T > 700 K dans l'air!
    → Vide spatial uniquement
    → Ou revêtement SiC
  
  Utilisation:
    - Insertions de col (moteurs solides)
    - Tuyères de rentrée atmosphérique

B) COMPOSITE CARBONE-CARBONE (C/C)

  Propriétés:
    k = 50-150 W/m·K (selon orientation)
    T_max = 3000-3200 K
    ρ = 1600-1900 kg/m³
    σ_tension = 200-400 MPa
  
  ✅ Avantages:
    - Très léger
    - k augmente avec T (!!)
    - Résistance maintenue à haute T
  
  ❌ Inconvénients:
    - Oxydation catastrophique si air
    - Fabrication longue et coûteuse
    - Anisotrope
  
  Utilisation:
    - Navette spatiale (bords d'attaque)
    - Tuyères de moteurs solides
    - Freins d'avions (non-spatial)

C) CARBURE DE SILICIUM (SiC)

  Propriétés:
    k = 120 W/m·K
    T_décompose = 3100 K
    T_max = 1900-2000 K
    ρ = 3210 kg/m³
  
  ✅ Avantages:
    - Résistant à l'oxydation
    - Dur et résistant à l'érosion
  
  Utilisation:
    - Revêtements protecteurs
    - Échangeurs de chaleur


7.7 CRITÈRES DE SÉLECTION DES MATÉRIAUX
───────────────────────────────────────────────────────────────

POUR LA CHAMBRE ET LE COL (flux max):
  
  Priorité 1: k élevé (évacuer la chaleur)
  Priorité 2: T_max adéquat
  Priorité 3: Résistance mécanique
  
  → CHOIX: CuCr, CuCrZr, GRCop-84
  
POUR LE DIVERGENT (flux modéré):
  
  Option A: Refroidissement régénératif
    → CuCr ou transition vers Inconel
  
  Option B: Rayonnement (spatial)
    → Nb/C103, Mo/TZM, ou composites
  
POUR PROTOTYPES/TESTS:
  
  → AlSi10Mg (impression 3D, économique)
  → Durée de vie limitée acceptable

ARBRE DE DÉCISION:

  ┌─ Flux > 20 MW/m² ? ─────────────────────────────────────┐
  │                                                          │
  │ OUI                              NON                     │
  │  │                                │                      │
  │  ↓                                ↓                      │
  │ CuCr/CuCrZr/GRCop              Inconel ou                │
  │ (OBLIGATOIRE)                   matériau économique      │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
  
  ┌─ Réutilisable ? ────────────────────────────────────────┐
  │                                                          │
  │ OUI → GRCop-84 (résistance fluage)                       │
  │ NON → CuCr (économique)                                  │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
  
  ┌─ Impression 3D ? ───────────────────────────────────────┐
  │                                                          │
  │ OUI → GRCop-84 (optimal)                                 │
  │       Inconel 718 (structures)                           │
  │       AlSi10Mg (prototypes)                              │
  │                                                          │
  │ NON → CuCr forgé/usiné (économique)                      │
  │                                                          │
  └──────────────────────────────────────────────────────────┘


7.8 EXEMPLES DE MOTEURS RÉELS
───────────────────────────────────────────────────────────────

MERLIN 1D (SpaceX):
  - Chambre/col: CuCr (usiné)
  - Divergent: Nb-C103 (rayonnement)
  - Épaisseur: 1.5-3 mm
  - Pression: 97 bar

RS-25 / SSME (NASA/Aerojet):
  - Chambre: CuCr (fraisé + électroformé Ni)
  - Col: CuCr
  - Divergent: Inconel 718
  - Canaux: 430 canaux de refroidissement
  - Pression: 206 bar

RAPTOR (SpaceX):
  - Chambre/col: GRCop-84 ou variante (SLM)
  - Fabrication additive
  - Pression: 300+ bar

RD-170/180 (Energomash):
  - Chambre: CuCrZr (brasé)
  - Col: CuCrZr
  - Divergent: Inox + Nb
  - Canaux: tubes enroulés

BE-4 (Blue Origin):
  - Chambre: CuCr ou GRCop
  - Fabrication hybride (SLM + traditionnel)
  - Pression: 135 bar

VULCAIN 2 (ESA):
  - Chambre: CuCr (fraisé)
  - Divergent: Inconel + tubes
  - Pression: 115 bar


8. PROPRIÉTÉS DES COOLANTS - GUIDE COMPLET
═══════════════════════════════════════════════════════════════

Cette section détaille les propriétés thermophysiques des 
fluides utilisés pour le refroidissement régénératif.


8.1 TABLEAU RÉCAPITULATIF DES COOLANTS
───────────────────────────────────────────────────────────────

  ┌──────────────┬────────┬────────┬────────┬────────┬────────┐
  │ Coolant      │Cp J/kg·K│T_boil K│T_crit K│ρ kg/m³ │μ mPa·s │
  ├──────────────┼────────┼────────┼────────┼────────┼────────┤
  │ LH2          │ 14300  │  20.3  │  33.2  │   71   │  0.013 │
  │ LOX          │  1700  │  90.2  │  154.6 │  1141  │  0.19  │
  │ LN2          │  2040  │  77.4  │  126.2 │   808  │  0.16  │
  │ CH4 (LCH4)   │  3500  │  111.7 │  190.6 │   422  │  0.12  │
  │ C2H6 (éthane)│  2500  │  184.6 │  305.3 │   544  │  0.18  │
  │ C3H8 (propane│  2500  │  231.1 │  369.8 │   582  │  0.20  │
  │ RP-1         │  2000  │  490   │  678   │   810  │  1.2   │
  │ Jet-A        │  2100  │  450   │  650   │   800  │  1.5   │
  │ C2H5OH       │  2440  │  351.4 │  514.0 │   789  │  1.1   │
  │ CH3OH        │  2530  │  337.8 │  512.6 │   791  │  0.55  │
  │ N2H4         │  3100  │  387.0 │  653.0 │  1004  │  0.97  │
  │ MMH          │  2900  │  360.5 │  585.0 │   874  │  0.78  │
  │ UDMH         │  2750  │  336.0 │  523.0 │   791  │  0.51  │
  │ H2O          │  4186  │  373.2 │  647.1 │  1000  │  1.0   │
  │ H2O2 (90%)   │  2800  │  423.0 │  730   │  1390  │  1.2   │
  │ NH3          │  4700  │  239.8 │  405.4 │   682  │  0.26  │
  │ N2O          │  1900  │  184.7 │  309.6 │  1220  │  0.14  │
  └──────────────┴────────┴────────┴────────┴────────┴────────┘

Note: Propriétés au point d'ébullition @ 1 bar sauf indication.


8.2 HYDROGÈNE LIQUIDE (LH2) - LE MEILLEUR COOLANT
───────────────────────────────────────────────────────────────

L'hydrogène liquide est le MEILLEUR coolant pour plusieurs raisons:

PROPRIÉTÉS DÉTAILLÉES:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur                           │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 2.016 g/mol                      │
  │ Température ébullition │ 20.3 K (-253°C) @ 1 bar          │
  │ Température critique   │ 33.2 K                           │
  │ Pression critique      │ 13.0 bar                         │
  │ Densité liquide        │ 70.8 kg/m³ @ 20 K                │
  │ Densité gaz            │ 1.34 kg/m³ @ NBP                 │
  │ Cp liquide             │ 9,700-14,300 J/kg·K              │
  │ Cp gaz                 │ 14,300 J/kg·K                    │
  │ Conductivité (liq)     │ 0.10 W/m·K                       │
  │ Conductivité (gaz)     │ 0.017 W/m·K                      │
  │ Viscosité (liq)        │ 13 μPa·s (très faible!)          │
  │ Prandtl                │ 0.7-1.3                          │
  │ Chaleur latente        │ 448 kJ/kg                        │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES THERMIQUES:
  - Cp ÉNORME (14,300 J/kg·K) → absorbe beaucoup d'énergie
  - Viscosité très faible → Re élevé → h_c élevé
  - k/μ élevé → excellent transfert
  - h_c typique: 50,000-200,000 W/m²·K!

❌ INCONVÉNIENTS:
  - Très basse température → isolation critique
  - Densité très faible → gros réservoirs
  - Fuit facilement (petite molécule)
  - Fragilisation hydrogène des métaux
  - Coût de production/stockage

⚠️ PRÉCAUTIONS:
  - Matériaux compatibles: Al, Inox 304/316, Inconel
  - Éviter: aciers au carbone (fragilisation)
  - Joints: PTFE, Indium, soudures
  - Risque d'explosion si mélange avec O2!

MOTEURS UTILISANT LH2:
  - RS-25 / SSME (NASA)
  - RL10 (Aerojet Rocketdyne)
  - J-2, J-2X (Saturn V, SLS)
  - Vulcain (Ariane)
  - LE-7, LE-9 (Japon)
  - CE-20 (Inde)


8.3 OXYGÈNE LIQUIDE (LOX)
───────────────────────────────────────────────────────────────

Le LOX est parfois utilisé comme coolant (cycles oxydizer-rich).

PROPRIÉTÉS DÉTAILLÉES:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur                           │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 32.0 g/mol                       │
  │ Température ébullition │ 90.2 K (-183°C) @ 1 bar          │
  │ Température critique   │ 154.6 K                          │
  │ Pression critique      │ 50.4 bar                         │
  │ Densité liquide        │ 1141 kg/m³ @ 90 K                │
  │ Cp liquide             │ 1,700 J/kg·K                     │
  │ Conductivité (liq)     │ 0.15 W/m·K                       │
  │ Viscosité (liq)        │ 190 μPa·s                        │
  │ Prandtl                │ 2.2                              │
  │ Chaleur latente        │ 213 kJ/kg                        │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Disponible (c'est l'oxydant!)
  - Bonne densité → compact
  - Température modérée (90 K vs 20 K pour LH2)

❌ INCONVÉNIENTS:
  - Cp modéré seulement
  - TRÈS réactif → risques d'ignition
  - Incompatible avec hydrocarbures chauds
  - Corrosif à haute température

⚠️ ATTENTION EXTRÊME:
  - LOX + matière organique = EXPLOSION
  - Nettoyage LOX obligatoire (dégraissage)
  - Matériaux: Inox, Monel, Inconel
  - Éviter: Al (sauf alliages spéciaux), Ti

UTILISATION:
  - RD-170/180 (cycle oxidizer-rich)
  - Quelques moteurs à cycle ox-rich
  - Généralement le FUEL est préféré comme coolant


8.4 MÉTHANE LIQUIDE (LCH4)
───────────────────────────────────────────────────────────────

Le méthane gagne en popularité (Raptor, BE-4, etc.)

PROPRIÉTÉS DÉTAILLÉES:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur                           │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 16.04 g/mol                      │
  │ Température ébullition │ 111.7 K (-161°C) @ 1 bar         │
  │ Température critique   │ 190.6 K                          │
  │ Pression critique      │ 46.0 bar                         │
  │ Densité liquide        │ 422 kg/m³ @ 112 K                │
  │ Cp liquide             │ 3,500 J/kg·K                     │
  │ Conductivité (liq)     │ 0.19 W/m·K                       │
  │ Viscosité (liq)        │ 120 μPa·s                        │
  │ Prandtl                │ 2.2                              │
  │ Chaleur latente        │ 510 kJ/kg                        │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Cp élevé (meilleur que RP-1)
  - Température modérée (112 K)
  - PAS DE COKÉFACTION! (propre)
  - Compatible avec O2 (ISRU Mars)
  - Densité acceptable
  - Viscosité faible → bon Re

❌ INCONVÉNIENTS:
  - Moins dense que RP-1
  - Cryogénique (infrastructure)
  - Plage de T plus étroite que H2

AVANTAGE CLÉ - PAS DE COKE:
  Le méthane ne forme PAS de dépôts carbonés 
  contrairement au RP-1/kérosène. Les moteurs peuvent 
  être réutilisés sans nettoyage des canaux!

MOTEURS UTILISANT CH4:
  - Raptor (SpaceX) - full-flow staged combustion
  - BE-4 (Blue Origin) - oxygen-rich staged combustion
  - Prometheus (ESA)
  - Vulcan Centaur (ULA, via BE-4)


8.5 RP-1 / KÉROSÈNE
───────────────────────────────────────────────────────────────

Le RP-1 est le fuel hydrocarbure le plus utilisé historiquement.

PROPRIÉTÉS DÉTAILLÉES:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur (typique @ 300K)          │
  ├────────────────────────┼──────────────────────────────────┤
  │ Composition            │ C12H24 (moyenne)                 │
  │ Masse molaire          │ ~170 g/mol                       │
  │ Point éclair           │ 316 K (43°C)                     │
  │ Température ébullition │ 490-540 K (plage)                │
  │ Température critique   │ ~678 K                           │
  │ Densité @ 288 K        │ 799-815 kg/m³                    │
  │ Cp @ 300 K             │ 2,000 J/kg·K                     │
  │ Cp @ 400 K             │ 2,300 J/kg·K                     │
  │ Cp @ 500 K             │ 2,800 J/kg·K                     │
  │ Conductivité @ 300 K   │ 0.12 W/m·K                       │
  │ Conductivité @ 400 K   │ 0.10 W/m·K                       │
  │ Viscosité @ 300 K      │ 1.2 mPa·s                        │
  │ Viscosité @ 400 K      │ 0.4 mPa·s                        │
  │ Prandtl @ 300 K        │ 20                               │
  │ Prandtl @ 400 K        │ 9                                │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Stockable à température ambiante!
  - Haute densité → réservoirs compacts
  - Infrastructure existante (aviation)
  - Non toxique (relativement)
  - Économique

❌ INCONVÉNIENTS MAJEURS:

  ⚠️ COKÉFACTION (problème critique!):
  
  À T > 450-500 K, le RP-1 se décompose et dépose du 
  carbone (coke) sur les parois des canaux:
  
    - Réduit la section de passage
    - Réduit le transfert thermique
    - Peut boucher les canaux!
    - Limite la réutilisabilité
  
  TEMPÉRATURE LIMITE:
    T_paroi_froid < 480 K (idéal < 420 K)
  
  SOLUTIONS:
    - RP-2 (version purifiée, moins de soufre)
    - Additifs anti-coke
    - Vitesses élevées (moins de temps de résidence)
    - Canaux larges (plus faciles à nettoyer)

VARIATION DES PROPRIÉTÉS AVEC T:
  ┌────────────┬────────┬────────┬────────┬────────┐
  │ T (K)      │  300   │  350   │  400   │  450   │
  ├────────────┼────────┼────────┼────────┼────────┤
  │ ρ (kg/m³)  │  810   │  775   │  740   │  700   │
  │ Cp (J/kg·K)│  2000  │  2150  │  2300  │  2500  │
  │ k (W/m·K)  │  0.12  │  0.11  │  0.10  │  0.09  │
  │ μ (mPa·s)  │  1.2   │  0.65  │  0.40  │  0.28  │
  │ Pr         │  20    │  12.7  │  9.2   │  7.8   │
  └────────────┴────────┴────────┴────────┴────────┘

MOTEURS UTILISANT RP-1:
  - Merlin (SpaceX Falcon 9)
  - RD-180, RD-191 (Atlas V, Angara)
  - NK-33 (N1)
  - RS-27 (Delta II)
  - F-1 (Saturn V)
  - Rutherford (Rocket Lab) - électropompe


8.6 ÉTHANOL (C2H5OH)
───────────────────────────────────────────────────────────────

Utilisé historiquement et par certains nouveaux acteurs.

PROPRIÉTÉS DÉTAILLÉES:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur @ 300 K                   │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 46.07 g/mol                      │
  │ Température ébullition │ 351.4 K (78°C)                   │
  │ Température critique   │ 514 K                            │
  │ Pression critique      │ 63 bar                           │
  │ Densité                │ 789 kg/m³                        │
  │ Cp                     │ 2,440 J/kg·K                     │
  │ Conductivité           │ 0.17 W/m·K                       │
  │ Viscosité              │ 1.1 mPa·s                        │
  │ Prandtl                │ 16                               │
  │ Chaleur latente        │ 838 kJ/kg                        │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Stockable, non cryogénique
  - Non toxique, biodégradable
  - Bonne capacité de refroidissement
  - Peut contenir de l'eau (refroidissement film)
  - Production renouvelable possible

❌ INCONVÉNIENTS:
  - Point d'ébullition bas (78°C)
  - Risque d'ébullition dans les canaux
  - Isp inférieure au RP-1
  - Hygroscopique (absorbe l'eau)

UTILISATION HISTORIQUE:
  - V-2 (Allemagne WWII)
  - Redstone (USA)
  - Moteurs amateurs/universitaires

MOTEURS MODERNES:
  - MIRA (Espagne)
  - Copenhagen Suborbitals
  - Nombreux projets New Space


8.7 HYDRAZINE ET DÉRIVÉS (N2H4, MMH, UDMH)
───────────────────────────────────────────────────────────────

⚠️ TOXIQUES ET DANGEREUX - Usage spatial principalement

A) HYDRAZINE (N2H4)

  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur                           │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 32.05 g/mol                      │
  │ Température fusion     │ 274.7 K (1.5°C)                  │
  │ Température ébullition │ 387 K (114°C)                    │
  │ Densité                │ 1,004 kg/m³                      │
  │ Cp                     │ 3,100 J/kg·K                     │
  │ Conductivité           │ 0.35 W/m·K (élevé!)              │
  │ Viscosité              │ 0.97 mPa·s                       │
  └────────────────────────┴──────────────────────────────────┘

  ✅ Avantages: Stockable, hypergolique avec N2O4
  ❌ Inconvénients: TRÈS TOXIQUE, cancérigène

B) MMH (Monométhylhydrazine - CH3NHNH2)

  Densité: 874 kg/m³
  T_boil: 360.5 K
  Cp: 2,900 J/kg·K
  
  Moins toxique que N2H4, plus stable.
  Utilisé: Apollo LM, systèmes orbitaux.

C) UDMH (Diméthylhydrazine asymétrique)

  Densité: 791 kg/m³
  T_boil: 336 K
  Cp: 2,750 J/kg·K
  
  Plus stable au stockage.
  Utilisé: Proton (Russie), Longue Marche (Chine).

UTILISATION:
  - Systèmes orbitaux et interplanétaires
  - Moteurs vernier et RCS
  - En diminution (toxicité)


8.8 EAU (H2O)
───────────────────────────────────────────────────────────────

L'eau est un EXCELLENT coolant mais rarement utilisée seule.

PROPRIÉTÉS:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur @ 300 K                   │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 18.02 g/mol                      │
  │ Température ébullition │ 373.2 K (100°C)                  │
  │ Température critique   │ 647.1 K                          │
  │ Pression critique      │ 220.6 bar                        │
  │ Densité                │ 1,000 kg/m³                      │
  │ Cp                     │ 4,186 J/kg·K (très élevé!)       │
  │ Conductivité           │ 0.60 W/m·K (excellent!)          │
  │ Viscosité              │ 1.0 mPa·s                        │
  │ Prandtl                │ 7                                │
  │ Chaleur latente        │ 2,257 kJ/kg (énorme!)            │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Cp très élevé (4,186 J/kg·K)
  - Conductivité excellente (0.60 W/m·K)
  - Chaleur latente énorme (ébullition = super refroidissement)
  - Non toxique, disponible
  - Économique

❌ INCONVÉNIENTS:
  - Point d'ébullition bas (100°C @ 1 bar)
  - Gel à 0°C (problème spatial)
  - Corrosif si impuretés
  - Non utilisé comme propergol directement

UTILISATION:
  - Tests au sol (refroidissement auxiliaire)
  - Injection pour refroidissement film (mélange éthanol-eau)
  - Systèmes terrestres


8.9 AMMONIAC (NH3)
───────────────────────────────────────────────────────────────

Utilisé dans certaines applications spatiales.

PROPRIÉTÉS:
  ┌────────────────────────┬──────────────────────────────────┐
  │ Propriété              │ Valeur                           │
  ├────────────────────────┼──────────────────────────────────┤
  │ Masse molaire          │ 17.03 g/mol                      │
  │ Température ébullition │ 239.8 K (-33°C)                  │
  │ Température critique   │ 405.4 K                          │
  │ Densité liquide        │ 682 kg/m³                        │
  │ Cp                     │ 4,700 J/kg·K (très élevé!)       │
  │ Conductivité           │ 0.52 W/m·K                       │
  │ Viscosité              │ 0.26 mPa·s                       │
  │ Prandtl                │ 2.4                              │
  │ Chaleur latente        │ 1,370 kJ/kg                      │
  └────────────────────────┴──────────────────────────────────┘

✅ AVANTAGES:
  - Cp élevé (4,700 J/kg·K)
  - Bonne conductivité
  - Stockable sous pression modérée
  - Utilisable comme propergol (avec décomposition)

❌ INCONVÉNIENTS:
  - Toxique (irritant)
  - Odeur forte
  - Corrosif pour cuivre et laiton

UTILISATION:
  - Systèmes de contrôle thermique (boucles)
  - Propulsion électrique (résistojets)
  - ISS (système de refroidissement)


8.10 COMPARAISON ET SÉLECTION DU COOLANT
───────────────────────────────────────────────────────────────

CLASSEMENT PAR CAPACITÉ DE REFROIDISSEMENT:

  ┌────────────────┬────────────┬──────────────────────────────┐
  │ Rang │ Coolant │ Cp×k/μ     │ Commentaire                  │
  ├──────┼─────────┼────────────┼──────────────────────────────┤
  │  1   │ LH2     │ 110,000    │ Le meilleur, mais cryogénique│
  │  2   │ H2O     │ 2,500      │ Excellent mais T_boil basse  │
  │  3   │ NH3     │ 1,900      │ Très bon, stockable          │
  │  4   │ LCH4    │ 550        │ Bon compromis, propre        │
  │  5   │ LOX     │ 130        │ Correct, mais réactif        │
  │  6   │ C2H5OH  │ 75         │ Acceptable, non toxique      │
  │  7   │ RP-1    │ 20         │ Médiocre mais stockable      │
  └──────┴─────────┴────────────┴──────────────────────────────┘

ARBRE DE DÉCISION:

  ┌─ Cycle propulsif ? ─────────────────────────────────────────┐
  │                                                              │
  │ LOX/LH2  → Utiliser LH2 comme coolant (toujours)            │
  │ LOX/CH4  → Utiliser CH4 comme coolant                        │
  │ LOX/RP-1 → Utiliser RP-1 (attention cokéfaction)            │
  │ N2O4/MMH → Utiliser MMH (fuel côté refroidissement)         │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘

  ┌─ Fuel ou Ox pour refroidir ? ───────────────────────────────┐
  │                                                              │
  │ FUEL PRÉFÉRÉ (99% des cas):                                  │
  │  - Moins réactif que l'oxydant                               │
  │  - Généralement meilleur Cp                                  │
  │  - Pas de risque d'ignition avec matériaux                   │
  │                                                              │
  │ OX UTILISÉ (rare):                                           │
  │  - Cycles oxydizer-rich (RD-170)                             │
  │  - Nécessite matériaux spéciaux (Monel, Inconel)            │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘

DIMENSIONNEMENT DU DÉBIT COOLANT:

  Le débit de coolant doit absorber toute la chaleur:
  
  Q_total = ṁ_coolant × Cp × ΔT_coolant
  
  ṁ_coolant = Q_total / (Cp × ΔT_max_admissible)
  
  Typiquement: ΔT_coolant = 100-300 K selon le fluide

EXEMPLE:
  Q_total = 5 MW (intégrale du flux sur la surface)
  Coolant: RP-1, Cp = 2100 J/kg·K, ΔT = 150 K
  
  ṁ_coolant = 5×10⁶ / (2100 × 150) = 15.9 kg/s
  
  Si ratio O/F = 2.5, et ṁ_total = 50 kg/s:
  ṁ_fuel = 50/3.5 = 14.3 kg/s
  
  → ATTENTION: ṁ_coolant > ṁ_fuel disponible!
  → Il faut réduire Q ou augmenter h_c


8.11 PROPRIÉTÉS EN FONCTION DE LA TEMPÉRATURE
───────────────────────────────────────────────────────────────

Les propriétés des fluides varient significativement avec T.
Cela affecte les calculs de h_c.

MÉTHANE (LCH4):
  ┌──────────┬────────┬────────┬────────┬────────┬────────┐
  │ T (K)    │  115   │  130   │  150   │  170   │  190   │
  ├──────────┼────────┼────────┼────────┼────────┼────────┤
  │ ρ (kg/m³)│  420   │  400   │  370   │  330   │  260   │
  │ Cp J/kg·K│  3450  │  3600  │  3900  │  4500  │  6000  │
  │ k W/m·K  │  0.19  │  0.17  │  0.14  │  0.11  │  0.08  │
  │ μ (μPa·s)│  115   │  90    │  65    │  45    │  30    │
  └──────────┴────────┴────────┴────────┴────────┴────────┘

HYDROGÈNE (LH2):
  ┌──────────┬────────┬────────┬────────┬────────┐
  │ T (K)    │   20   │   25   │   30   │   33   │
  ├──────────┼────────┼────────┼────────┼────────┤
  │ ρ (kg/m³)│   71   │   65   │   50   │   31   │
  │ Cp J/kg·K│  9700  │ 12000  │ 19000  │   ∞    │
  │ k W/m·K  │  0.10  │  0.10  │  0.09  │  0.07  │
  │ μ (μPa·s)│   13   │   11   │    8   │    5   │
  └──────────┴────────┴────────┴────────┴────────┘

Note: À T_critique, Cp → ∞ (transition de phase)

CONSEIL:
  Toujours utiliser les propriétés à T_film:
  
  T_film = (T_wall_cold + T_bulk) / 2


9. EXEMPLES DE CALCUL COMPLETS
═══════════════════════════════════════════════════════════════

Cette section présente plusieurs exemples de calcul détaillés pour
illustrer l'application des équations thermiques aux moteurs-fusées.
Chaque exemple suit une méthodologie complète et vérifie les résultats.


9.1 EXEMPLE 1 : PETIT MOTEUR LOX/RP-1 (TYPE AMATEUR AVANCÉ)
───────────────────────────────────────────────────────────────

DONNÉES DU PROBLÈME:
  ┌─────────────────────────────────────────────────────────┐
  │ PARAMÈTRES DE CONCEPTION                                │
  ├─────────────────────────────────────────────────────────┤
  │ Propergols:        LOX / RP-1                           │
  │ Pression chambre:  25 bar (2.5 MPa)                     │
  │ Rapport O/F:       2.4                                  │
  │ Débit total:       0.8 kg/s                             │
  │ Diamètre col:      30 mm                                │
  │ Ratio expansion:   8:1                                  │
  │ T chambre:         3200 K (calculé CEA)                 │
  │ γ gaz:             1.21                                 │
  │ M gaz:             22.5 kg/kmol                         │
  │ μ gaz:             8.2×10⁻⁵ Pa·s                        │
  │ Cp gaz:            2100 J/kg·K                          │
  ├─────────────────────────────────────────────────────────┤
  │ SYSTÈME DE REFROIDISSEMENT                              │
  ├─────────────────────────────────────────────────────────┤
  │ Coolant:           RP-1                                 │
  │ T entrée coolant:  300 K                                │
  │ Pression coolant:  30 bar                               │
  │ Vitesse coolant:   20 m/s                               │
  │ Dh canal:          4 mm                                 │
  ├─────────────────────────────────────────────────────────┤
  │ PAROI                                                   │
  ├─────────────────────────────────────────────────────────┤
  │ Matériau:          CuCr1Zr                              │
  │ Conductivité:      320 W/m·K                            │
  │ T limite:          723 K (450°C)                        │
  │ T fusion:          1350 K                               │
  │ Épaisseur:         3 mm                                 │
  └─────────────────────────────────────────────────────────┘

ÉTAPE 1 - CALCUL DU COEFFICIENT h_g (ÉQUATION DE BARTZ)
─────────────────────────────────────────────────────────

Données nécessaires:
  • Dt = 0.030 m (diamètre col)
  • At = π × (0.030)² / 4 = 7.07×10⁻⁴ m²
  • Pc = 25×10⁵ Pa
  • c* = 1650 m/s (calculé ou table CEA)
  • Tc = 3200 K
  • M = 22.5 kg/kmol
  • γ = 1.21
  • μ = 8.2×10⁻⁵ Pa·s
  • Cp = 2100 J/kg·K
  • Pr = μ × Cp / k_gaz ≈ 0.72

Calcul du nombre de Prandtl:
  Pr = Cp × μ / k_gaz
  k_gaz ≈ Cp × μ / Pr = 2100 × 8.2×10⁻⁵ / 0.72 = 0.239 W/m·K

Facteur de correction σ (Bartz):
  T_wall estimée ≈ 900 K (première itération)
  T_aw = Tc × [1 + (γ-1)/2 × r × M²]
  Au col (M=1): T_aw ≈ 0.91 × Tc = 2912 K
  
  σ = [0.5 × (T_wall/Tc) × (1 + (γ-1)/2 × M²) + 0.5]^(-0.68)
  σ = [0.5 × (900/3200) × 1.105 + 0.5]^(-0.68)
  σ = [0.655]^(-0.68) = 1.38

Équation de Bartz au col:
  h_g = (0.026 / Dt^0.2) × (μ^0.2 × Cp / Pr^0.6) × (Pc/c*)^0.8 × (Dt/Rc)^0.1 × σ

  Avec Rc = 1.5 × Dt = 0.045 m (rayon de courbure standard):
  
  h_g = (0.026 / 0.030^0.2) × (8.2×10⁻⁵)^0.2 × 2100 / 0.72^0.6 
        × (25×10⁵ / 1650)^0.8 × (0.030/0.045)^0.1 × 1.38
  
  Calcul terme par terme:
    • 0.026 / 0.030^0.2 = 0.026 / 0.494 = 0.0527
    • (8.2×10⁻⁵)^0.2 = 0.0972
    • 0.72^0.6 = 0.823
    • (25×10⁵ / 1650)^0.8 = (1515)^0.8 = 405.7
    • (0.030/0.045)^0.1 = 0.667^0.1 = 0.960
    • σ = 1.38
  
  h_g = 0.0527 × 0.0972 × 2100 / 0.823 × 405.7 × 0.960 × 1.38
  
  h_g = 0.0527 × 247.5 × 405.7 × 0.960 × 1.38
  
  h_g ≈ 7,020 W/m²·K

  ⚠️ RÉSULTAT: h_g au col ≈ 7,000 W/m²·K


ÉTAPE 2 - CALCUL DU COEFFICIENT h_c (DITTUS-BOELTER)
─────────────────────────────────────────────────────

Propriétés du RP-1 à T_film ≈ 350 K (estimation):
  • ρ = 780 kg/m³
  • μ = 1.2×10⁻³ Pa·s
  • k = 0.11 W/m·K
  • Cp = 2100 J/kg·K
  • Pr = Cp × μ / k = 2100 × 1.2×10⁻³ / 0.11 = 22.9

Nombre de Reynolds:
  Re = ρ × v × Dh / μ
  Re = 780 × 20 × 0.004 / (1.2×10⁻³)
  Re = 52,000

  ✅ Re > 10,000 → Écoulement turbulent, Dittus-Boelter applicable

Nombre de Nusselt (Dittus-Boelter, chauffage):
  Nu = 0.023 × Re^0.8 × Pr^0.4
  Nu = 0.023 × (52,000)^0.8 × (22.9)^0.4
  Nu = 0.023 × 5,893 × 4.05
  Nu = 549

Coefficient de transfert:
  h_c = Nu × k / Dh
  h_c = 549 × 0.11 / 0.004
  h_c = 15,100 W/m²·K

  ⚠️ RÉSULTAT: h_c ≈ 15,100 W/m²·K


ÉTAPE 3 - CALCUL DU FLUX THERMIQUE ET TEMPÉRATURES
──────────────────────────────────────────────────

Résistance thermique totale:
  R_total = 1/h_g + e/k + 1/h_c
  
  R_gaz    = 1/7,000 = 1.43×10⁻⁴ m²·K/W
  R_paroi  = 0.003/320 = 9.38×10⁻⁶ m²·K/W
  R_cool   = 1/15,100 = 6.62×10⁻⁵ m²·K/W
  
  R_total = 1.43×10⁻⁴ + 9.38×10⁻⁶ + 6.62×10⁻⁵
  R_total = 2.19×10⁻⁴ m²·K/W

  Note: La résistance dominante est R_gaz (65% du total)

Flux thermique:
  ΔT = T_aw - T_coolant = 2912 - 300 = 2612 K
  
  q = ΔT / R_total
  q = 2612 / 2.19×10⁻⁴
  q = 11.93×10⁶ W/m²
  
  ⚠️ RÉSULTAT: q ≈ 12 MW/m²

Distribution des températures:
  T_wall_cold = T_coolant + q / h_c
  T_wall_cold = 300 + 11.93×10⁶ / 15,100
  T_wall_cold = 300 + 790 = 1090 K   ❌ TROP ÉLEVÉ!

  T_wall_hot = T_wall_cold + q × e / k
  T_wall_hot = 1090 + 11.93×10⁶ × 0.003 / 320
  T_wall_hot = 1090 + 112 = 1202 K


ÉTAPE 4 - ANALYSE ET ITÉRATION
─────────────────────────────

⚠️ PROBLÈME DÉTECTÉ:
  T_wall_cold = 1090 K >> T_limite (723 K)
  La conception actuelle NE FONCTIONNE PAS!

SOLUTIONS POSSIBLES:
  1. Augmenter la vitesse du coolant
  2. Augmenter le débit du coolant
  3. Réduire le diamètre hydraulique
  4. Ajouter du refroidissement par film
  5. Changer de coolant (LH2 beaucoup plus efficace)

ITÉRATION - Augmentation vitesse à 40 m/s:
  Re = 780 × 40 × 0.004 / (1.2×10⁻³) = 104,000
  Nu = 0.023 × (104,000)^0.8 × (22.9)^0.4 = 956
  h_c = 956 × 0.11 / 0.004 = 26,300 W/m²·K
  
  R_cool = 1/26,300 = 3.80×10⁻⁵ m²·K/W
  R_total = 1.43×10⁻⁴ + 9.38×10⁻⁶ + 3.80×10⁻⁵ = 1.90×10⁻⁴ m²·K/W
  
  q = 2612 / 1.90×10⁻⁴ = 13.7 MW/m²
  
  T_wall_cold = 300 + 13.7×10⁶ / 26,300 = 821 K   ❌ Encore trop!

ITÉRATION - Avec refroidissement par film (15% fuel):
  Efficacité film: η_film ≈ 0.60
  T_aw_effective = T_coolant + η_film × (T_aw - T_coolant)
  T_aw_effective = 300 + 0.60 × (2912 - 300) = 1867 K
  
  q = (1867 - 300) / 1.90×10⁻⁴ = 8.2 MW/m²
  
  T_wall_cold = 300 + 8.2×10⁶ / 26,300 = 612 K   ✅ OK!
  T_wall_hot = 612 + 8.2×10⁶ × 0.003 / 320 = 689 K   ✅ OK!

  ⚠️ SOLUTION: Vitesse 40 m/s + film cooling 15% → T_wall < T_limite


ÉTAPE 5 - CALCUL ÉPAISSEUR CRITIQUE
───────────────────────────────────

Avec la configuration finale (v=40 m/s, film 15%):

Épaisseur de fusion:
  e_melt = k × (T_fusion - T_wall_cold) / q
  e_melt = 320 × (1350 - 612) / 8.2×10⁶
  e_melt = 320 × 738 / 8.2×10⁶
  e_melt = 0.0288 m = 28.8 mm

Épaisseur limite opérationnelle:
  e_max = k × (T_limite - T_wall_cold) / q
  e_max = 320 × (723 - 612) / 8.2×10⁶
  e_max = 320 × 111 / 8.2×10⁶
  e_max = 0.00433 m = 4.33 mm

  ✅ Épaisseur 3 mm < e_max (4.33 mm) → Conception valide

Marge de sécurité sur épaisseur:
  Marge = (e_max - e_actuelle) / e_actuelle × 100
  Marge = (4.33 - 3) / 3 × 100 = 44%   ✅ Marge acceptable


ÉTAPE 6 - RÉCAPITULATIF CONCEPTION FINALE
─────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────┐
  │ RÉSUMÉ DE LA CONCEPTION VALIDÉE                         │
  ├─────────────────────────────────────────────────────────┤
  │ Vitesse coolant:      40 m/s                            │
  │ Film cooling:         15% du débit fuel                 │
  │ h_g:                  7,000 W/m²·K                      │
  │ h_c:                  26,300 W/m²·K                     │
  │ Flux thermique:       8.2 MW/m²                         │
  │ T_wall_hot:           689 K                             │
  │ T_wall_cold:          612 K                             │
  │ Marge vs T_limite:    34 K (5%)                         │
  │ Épaisseur:            3 mm (marge 44%)                  │
  └─────────────────────────────────────────────────────────┘


9.2 EXEMPLE 2 : MOTEUR LOX/LH2 HAUTE PERFORMANCE
───────────────────────────────────────────────────────────────

DONNÉES DU PROBLÈME:
  ┌─────────────────────────────────────────────────────────┐
  │ PARAMÈTRES DE CONCEPTION                                │
  ├─────────────────────────────────────────────────────────┤
  │ Propergols:        LOX / LH2                            │
  │ Pression chambre:  100 bar (10 MPa)                     │
  │ Rapport O/F:       6.0                                  │
  │ Débit total:       25 kg/s                              │
  │ Diamètre col:      80 mm                                │
  │ Ratio expansion:   40:1                                 │
  │ T chambre:         3550 K (calculé CEA)                 │
  │ γ gaz:             1.14                                 │
  │ M gaz:             13.5 kg/kmol                         │
  │ c*:                2350 m/s                             │
  ├─────────────────────────────────────────────────────────┤
  │ SYSTÈME DE REFROIDISSEMENT                              │
  ├─────────────────────────────────────────────────────────┤
  │ Coolant:           LH2 supercritique                    │
  │ T entrée coolant:  40 K                                 │
  │ Pression coolant:  150 bar                              │
  │ Débit H2:          3.57 kg/s (mdot_fuel)                │
  │ Dh canal:          2 mm                                 │
  │ Nombre canaux:     200                                  │
  ├─────────────────────────────────────────────────────────┤
  │ PAROI                                                   │
  ├─────────────────────────────────────────────────────────┤
  │ Matériau:          NARloy-Z (Cu-Ag-Zr)                  │
  │ Conductivité:      340 W/m·K                            │
  │ T limite:          810 K                                │
  │ T fusion:          1355 K                               │
  │ Épaisseur:         1.5 mm                               │
  └─────────────────────────────────────────────────────────┘

ÉTAPE 1 - CALCUL h_g (BARTZ)
────────────────────────────

  μ_gaz ≈ 7.5×10⁻⁵ Pa·s (à Tc)
  Cp_gaz = 3800 J/kg·K (H2O/H2 dominant)
  Pr = 0.68

  σ ≈ 1.42 (avec T_wall estimée 600 K)

  h_g = (0.026 / 0.080^0.2) × (7.5×10⁻⁵)^0.2 × 3800 / 0.68^0.6 
        × (100×10⁵ / 2350)^0.8 × σ
  
  Calcul:
    • 0.026 / 0.080^0.2 = 0.026 / 0.574 = 0.0453
    • (7.5×10⁻⁵)^0.2 = 0.0948
    • 0.68^0.6 = 0.796
    • (100×10⁵ / 2350)^0.8 = (4255)^0.8 = 846
  
  h_g = 0.0453 × 0.0948 × 3800 / 0.796 × 846 × 1.42
  
  h_g ≈ 24,600 W/m²·K

  Note: Plus élevé que LOX/RP-1 car Pc plus haute et Cp gaz plus élevé


ÉTAPE 2 - CALCUL h_c (LH2 SUPERCRITIQUE)
────────────────────────────────────────

L'hydrogène supercritique (P > 13 bar, T > 33 K) a des propriétés
exceptionnelles mais qui varient fortement avec la température.

Propriétés LH2 à 100 K, 150 bar:
  • ρ = 45 kg/m³
  • μ = 5.5×10⁻⁶ Pa·s
  • k = 0.12 W/m·K
  • Cp = 14,500 J/kg·K (pic pseudo-critique)
  • Pr = 0.67

Section canal (rectangulaire 2×4 mm):
  A_canal = 8 mm² = 8×10⁻⁶ m²
  Périmètre = 12 mm
  Dh = 4A/P = 4×8/12 = 2.67 mm

Débit par canal:
  mdot_canal = 3.57 / 200 = 0.0179 kg/s
  v = mdot / (ρ × A) = 0.0179 / (45 × 8×10⁻⁶) = 49.7 m/s

Nombre de Reynolds:
  Re = ρ × v × Dh / μ
  Re = 45 × 49.7 × 0.00267 / (5.5×10⁻⁶)
  Re = 1,086,000   (très turbulent!)

Corrélation Gnielinski (recommandée pour grandes variations Pr):
  f = (0.79 × ln(Re) - 1.64)^(-2)
  f = (0.79 × 13.9 - 1.64)^(-2) = (9.34)^(-2) = 0.0115
  
  Nu = (f/8) × (Re - 1000) × Pr / [1 + 12.7×(f/8)^0.5 × (Pr^(2/3) - 1)]
  Nu = (0.0115/8) × (1,085,000) × 0.67 / [1 + 12.7×(0.0379) × (-0.24)]
  Nu = 0.00144 × 727,000 / 0.884
  Nu = 1,183

Coefficient de transfert:
  h_c = Nu × k / Dh
  h_c = 1,183 × 0.12 / 0.00267
  h_c = 53,200 W/m²·K

  ⚠️ RÉSULTAT: h_c ≈ 53,000 W/m²·K (excellent!)


ÉTAPE 3 - FLUX ET TEMPÉRATURES
─────────────────────────────

Résistances thermiques:
  R_gaz    = 1/24,600 = 4.07×10⁻⁵ m²·K/W
  R_paroi  = 0.0015/340 = 4.41×10⁻⁶ m²·K/W
  R_cool   = 1/53,200 = 1.88×10⁻⁵ m²·K/W
  
  R_total = 6.39×10⁻⁵ m²·K/W

  Note: Distribution plus équilibrée grâce au h_c élevé

T_aw au col:
  r = Pr^0.33 = 0.68^0.33 = 0.88
  T_aw = Tc × [1 + r×(γ-1)/2] = 3550 × [1 + 0.88×0.07] = 3769 K
  
  (Pour LOX/LH2, T_aw ≈ 0.90 × Tc au col)

Flux thermique:
  ΔT = T_aw - T_bulk = 3769 - 100 = 3669 K
  
  q = 3669 / 6.39×10⁻⁵ = 57.4 MW/m²

  ⚠️ FLUX TRÈS ÉLEVÉ - typique des moteurs LOX/LH2

Températures paroi:
  T_wall_cold = 100 + 57.4×10⁶ / 53,200 = 1,179 K   ❌ PROBLÈME!
  
  La température dépasse la limite (810 K) et même approche la fusion!


ÉTAPE 4 - OPTIMISATION NÉCESSAIRE
─────────────────────────────────

Le flux de 57 MW/m² est trop intense. Solutions:

1. AUGMENTER LE NOMBRE DE CANAUX:
   N = 400 canaux → v = 99 m/s → Re = 2.17×10⁶
   Nu = 2,100 → h_c = 94,400 W/m²·K
   T_wall_cold = 100 + 57.4×10⁶ / 94,400 = 708 K   ✅ OK!

2. OU RÉDUIRE LE DIAMÈTRE HYDRAULIQUE:
   Dh = 1.5 mm → Re augmente → h_c augmente

3. OU AJOUTER FILM COOLING:
   Film H2 5% → efficacité 0.40
   T_aw_eff = 100 + 0.40×(3769-100) = 1568 K
   q = (1568-100) / 6.39×10⁻⁵ = 23.0 MW/m²
   T_wall_cold = 100 + 23.0×10⁶ / 53,200 = 533 K   ✅

CONCEPTION FINALE RETENUE: 400 canaux
  ┌─────────────────────────────────────────────────────────┐
  │ RÉSUMÉ LOX/LH2                                          │
  ├─────────────────────────────────────────────────────────┤
  │ h_g:                  24,600 W/m²·K                     │
  │ h_c:                  94,400 W/m²·K                     │
  │ Flux thermique:       50.2 MW/m² (avec 400 canaux)      │
  │ T_wall_cold:          632 K                             │
  │ T_wall_hot:           854 K                             │
  │ Marge vs T_limite:    -44 K ❌ (besoin film cooling)    │
  │                                                         │
  │ AVEC FILM COOLING 3%:                                   │
  │ Flux effectif:        32 MW/m²                          │
  │ T_wall_hot:           615 K   ✅                        │
  └─────────────────────────────────────────────────────────┘


9.3 EXEMPLE 3 : MOTEUR LOX/CH4 (NOUVELLE GÉNÉRATION)
───────────────────────────────────────────────────────────────

Le méthane est un compromis entre RP-1 et LH2, offrant de bonnes
propriétés de refroidissement sans les contraintes cryogéniques extrêmes.

DONNÉES:
  ┌─────────────────────────────────────────────────────────┐
  │ Propergols:        LOX / LCH4                           │
  │ Pression chambre:  80 bar                               │
  │ Rapport O/F:       3.6                                  │
  │ Diamètre col:      150 mm                               │
  │ T chambre:         3450 K                               │
  │ Coolant:           LCH4 supercritique (120 K, 100 bar)  │
  │ Matériau:          C-103 (Nb alloy, k=42 W/m·K)         │
  │ Épaisseur:         2 mm                                 │
  └─────────────────────────────────────────────────────────┘

CALCULS RAPIDES:

h_g (Bartz):
  h_g ≈ 18,500 W/m²·K (estimé avec corrélation)

h_c (CH4 supercritique à 150 K):
  Propriétés CH4: ρ=200 kg/m³, μ=30×10⁻⁶ Pa·s, k=0.15 W/m·K, Cp=4000 J/kg·K
  Avec v=30 m/s, Dh=3 mm:
  Re = 200 × 30 × 0.003 / 30×10⁻⁶ = 600,000
  Nu = 1,850 (Gnielinski)
  h_c = 1,850 × 0.15 / 0.003 = 92,500 W/m²·K

Flux et températures:
  R_total = 1/18,500 + 0.002/42 + 1/92,500 = 1.12×10⁻⁴ m²·K/W
  T_aw ≈ 0.92 × 3450 = 3174 K
  q = (3174 - 150) / 1.12×10⁻⁴ = 27.0 MW/m²
  
  T_wall_cold = 150 + 27.0×10⁶ / 92,500 = 442 K
  T_wall_hot = 442 + 27.0×10⁶ × 0.002 / 42 = 1,728 K   ❌

  ⚠️ Le niobium (T_fusion = 2750 K) supporte cette température, mais
     la durée de vie serait limitée. Une liner en cuivre serait préférable.

SOLUTION: Liner CuCrZr + coque Nb
  Liner 0.8 mm CuCrZr (k=320) + coque 2 mm Nb
  R_total = 1/18,500 + 0.0008/320 + 0.002/42 + 1/92,500 = 1.14×10⁻⁴
  T_wall_hot = 150 + 27×10⁶ × (1/92,500 + 0.0008/320) = 511 K   ✅


9.4 EXEMPLE 4 : DIMENSIONNEMENT CANAUX DE REFROIDISSEMENT
───────────────────────────────────────────────────────────────

Cet exemple montre comment dimensionner les canaux pour atteindre
un h_c cible avec un Δp acceptable.

OBJECTIF:
  Atteindre h_c = 50,000 W/m²·K avec RP-1
  Contrainte: Δp < 10 bar sur 200 mm de longueur

DONNÉES:
  • Coolant: RP-1 @ 350 K
  • ρ = 750 kg/m³, μ = 8×10⁻⁴ Pa·s, k = 0.10 W/m·K, Pr = 17
  • Débit disponible: 2 kg/s
  • Circonférence col: π × 0.050 = 0.157 m

MÉTHODE DE RÉSOLUTION:

1. Déterminer Nu nécessaire:
   h_c = Nu × k / Dh
   50,000 = Nu × 0.10 / Dh
   Nu × Dh = 5000   ... (Eq. 1)

2. Exprimer Nu en fonction de Re (Dittus-Boelter):
   Nu = 0.023 × Re^0.8 × 17^0.4 = 0.023 × Re^0.8 × 3.65
   Nu = 0.084 × Re^0.8   ... (Eq. 2)

3. Exprimer Re en fonction de Dh:
   Soit N canaux de largeur w et profondeur d
   Dh = 4×w×d / (2w + 2d)
   
   Pour w = 2×d: Dh = 4×2d² / 6d = 1.33d
   
   Débit par canal: mdot_c = 2/N
   Vitesse: v = mdot_c / (ρ × w × d) = 2 / (N × 750 × 2d²)
   
   Re = 750 × v × Dh / 8×10⁻⁴

4. Itération:
   Essai N = 80, d = 1.5 mm, w = 3 mm:
   Dh = 4×3×1.5 / 9 = 2 mm
   A_canal = 4.5 mm²
   v = 2 / (80 × 750 × 4.5×10⁻⁶) = 7.4 m/s
   Re = 750 × 7.4 × 0.002 / 8×10⁻⁴ = 13,900
   Nu = 0.084 × 13,900^0.8 = 213
   h_c = 213 × 0.10 / 0.002 = 10,650 W/m²·K   ❌ Trop bas!

   Essai N = 120, d = 1 mm, w = 2 mm:
   Dh = 4×2×1 / 6 = 1.33 mm
   A_canal = 2 mm²
   v = 2 / (120 × 750 × 2×10⁻⁶) = 11.1 m/s
   Re = 750 × 11.1 × 0.00133 / 8×10⁻⁴ = 13,850
   Nu = 0.084 × 13,850^0.8 = 212
   h_c = 212 × 0.10 / 0.00133 = 15,940 W/m²·K   ❌ Encore trop bas

   Essai N = 150, d = 0.8 mm, w = 1.6 mm (canaux fins):
   Dh = 4×1.6×0.8 / 4.8 = 1.07 mm
   v = 2 / (150 × 750 × 1.28×10⁻⁶) = 13.9 m/s
   Re = 750 × 13.9 × 0.00107 / 8×10⁻⁴ = 13,940
   h_c = 14,000 W/m²·K   ❌
   
   PROBLÈME: avec RP-1, difficile d'atteindre h_c > 30,000 W/m²·K
   sans pertes de charge excessives.

5. Vérification perte de charge:
   f = 0.316 / Re^0.25 = 0.316 / 13,940^0.25 = 0.029
   Δp = f × L/Dh × ρ × v² / 2
   Δp = 0.029 × 0.2/0.00107 × 750 × 13.9² / 2
   Δp = 5.42 × 72,560 = 3.93 bar   ✅ OK

CONCLUSION:
  h_c_max réaliste avec RP-1 ≈ 25,000 W/m²·K
  Pour h_c = 50,000 W/m²·K, utiliser LH2 ou LCH4


9.5 EXEMPLE 5 : CALCUL ÉLÉVATION TEMPÉRATURE COOLANT
───────────────────────────────────────────────────────────────

Vérifier que le coolant ne surchauffe pas en traversant les canaux.

DONNÉES:
  • Q_total = 850 kW (puissance thermique totale)
  • Coolant: RP-1
  • Débit: 2 kg/s
  • Cp = 2100 J/kg·K
  • T_entrée = 300 K
  • T_ébullition = 490 K à 30 bar

CALCUL:
  ΔT_coolant = Q_total / (mdot × Cp)
  ΔT_coolant = 850,000 / (2 × 2100)
  ΔT_coolant = 202 K
  
  T_sortie = 300 + 202 = 502 K   ⚠️ > T_ébullition!

PROBLÈME: Le RP-1 risque de bouillir et former des dépôts (coking)

SOLUTIONS:
  1. Augmenter le débit coolant (si possible)
  2. Augmenter la pression coolant pour élever T_ébullition
  3. Utiliser du refroidissement par film pour réduire Q_total
  4. Multi-pass cooling (entrée au col, zones froides vers chambre)

AVEC FILM COOLING 20%:
  Q_effectif = 0.65 × 850 = 552 kW (réduction typique avec film)
  ΔT_coolant = 552,000 / (2 × 2100) = 132 K
  T_sortie = 300 + 132 = 432 K   ✅ < T_ébullition


9.6 EXEMPLE 6 : ANALYSE DIMENSIONNELLE RAPIDE
───────────────────────────────────────────────────────────────

Méthode simplifiée pour estimation préliminaire.

RÈGLES EMPIRIQUES (moteurs conventionnels):

  ┌──────────────────────────────────────────────────────────┐
  │ ESTIMATIONS RAPIDES                                      │
  ├──────────────────────────────────────────────────────────┤
  │ h_g au col ≈ 5000 × (Pc/20)^0.8 × (30/Dt)^0.8 W/m²·K    │
  │   où Pc en bar, Dt en mm                                 │
  │                                                          │
  │ q_col ≈ 0.4 × h_g × Tc  (en W/m²)                       │
  │   approximation avec T_wall typique                      │
  │                                                          │
  │ Q_total ≈ q_col × 0.3 × A_totale                        │
  │   car flux moyen ≈ 30% du flux au col                    │
  │                                                          │
  │ ΔT_coolant ≈ Q_total / (mdot_fuel × Cp_fuel)            │
  └──────────────────────────────────────────────────────────┘

EXEMPLE RAPIDE:
  Pc = 50 bar, Dt = 60 mm, Tc = 3400 K, LOX/RP-1
  
  h_g ≈ 5000 × (50/20)^0.8 × (30/60)^0.8
  h_g ≈ 5000 × 2.0 × 0.57 = 5,700 W/m²·K
  
  q_col ≈ 0.4 × 5700 × 3400 = 7.8 MW/m²
  
  Cette estimation est généralement à ±30% de la valeur réelle.


9.7 TABLEAU RÉCAPITULATIF DES EXEMPLES
───────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │ COMPARAISON DES EXEMPLES DE CALCUL                                      │
  ├───────────┬──────────┬──────────┬──────────┬─────────┬─────────────────┤
  │ Exemple   │ Pc (bar) │ Dt (mm)  │ q (MW/m²)│ h_g     │ Solution        │
  ├───────────┼──────────┼──────────┼──────────┼─────────┼─────────────────┤
  │ LOX/RP-1  │ 25       │ 30       │ 8.2      │ 7,000   │ Film 15% + v↑   │
  │ LOX/LH2   │ 100      │ 80       │ 32       │ 24,600  │ 400 can + film  │
  │ LOX/CH4   │ 80       │ 150      │ 27       │ 18,500  │ Liner Cu + Nb   │
  └───────────┴──────────┴──────────┴──────────┴─────────┴─────────────────┘

TENDANCES OBSERVÉES:
  • q augmente avec Pc (quasi-linéairement)
  • h_g augmente quand Dt diminue
  • LOX/LH2 requiert le refroidissement le plus intense
  • Le film cooling est souvent nécessaire pour Pc > 50 bar


9.8 EXERCICES D'APPLICATION
───────────────────────────────────────────────────────────────

EXERCICE 1 - Calcul basique:
  Un moteur LOX/Ethanol a: Pc=15 bar, Dt=25 mm, Tc=3000 K
  Calculer h_g au col avec l'équation de Bartz.
  (Réponse: ≈ 4,800 W/m²·K)

EXERCICE 2 - Dimensionnement coolant:
  Avec q=5 MW/m² et h_c requis=20,000 W/m²·K
  Quelle élévation de température paroi côté froid?
  (Réponse: ΔT = q/h_c = 250 K)

EXERCICE 3 - Épaisseur critique:
  Paroi cuivre (k=360 W/m·K), T_limite=700 K, T_cold=400 K
  Flux q=15 MW/m². Quelle épaisseur maximale?
  (Réponse: e_max = k×ΔT/q = 7.2 mm)

EXERCICE 4 - Puissance thermique:
  Moteur 5 kN de poussée, Isp=280s, Tc=3200 K
  Estimer la puissance thermique à évacuer.
  (Réponse: Q ≈ 0.5-1 MW, selon géométrie et flux)


10. FORMULES RAPIDES (AIDE-MÉMOIRE COMPLET)
═══════════════════════════════════════════════════════════════

Cette section rassemble toutes les formules essentielles pour
la conception thermique des moteurs-fusées, organisées par thème.


10.1 ÉQUATIONS FONDAMENTALES DU TRANSFERT THERMIQUE
───────────────────────────────────────────────────────────────

FLUX THERMIQUE (LOI DE FOURIER):
  ┌─────────────────────────────────────────────────────────┐
  │ q = -k × (dT/dx)        [W/m²]                         │
  │                                                         │
  │ Pour une paroi plane:                                   │
  │ q = k × (T₁ - T₂) / e   [W/m²]                         │
  │                                                         │
  │ où: k = conductivité thermique [W/m·K]                  │
  │     e = épaisseur [m]                                   │
  │     T₁, T₂ = températures aux faces [K]                 │
  └─────────────────────────────────────────────────────────┘

CONVECTION (LOI DE NEWTON):
  ┌─────────────────────────────────────────────────────────┐
  │ q = h × (T_fluide - T_paroi)    [W/m²]                 │
  │                                                         │
  │ où: h = coefficient de convection [W/m²·K]              │
  │     T_fluide = température du fluide [K]                │
  │     T_paroi = température de la paroi [K]               │
  └─────────────────────────────────────────────────────────┘

RÉSISTANCES THERMIQUES EN SÉRIE:
  ┌─────────────────────────────────────────────────────────┐
  │ R_total = R_gaz + R_paroi + R_coolant                   │
  │                                                         │
  │ R_gaz = 1/h_g           [m²·K/W]                       │
  │ R_paroi = e/k           [m²·K/W]                       │
  │ R_coolant = 1/h_c       [m²·K/W]                       │
  │                                                         │
  │ Flux: q = ΔT_total / R_total                           │
  └─────────────────────────────────────────────────────────┘

COEFFICIENT GLOBAL DE TRANSFERT:
  ┌─────────────────────────────────────────────────────────┐
  │ U = 1 / R_total = 1 / (1/h_g + e/k + 1/h_c)            │
  │                                                         │
  │ q = U × (T_gaz - T_coolant)                            │
  └─────────────────────────────────────────────────────────┘


10.2 ÉQUATION DE BARTZ (CÔTÉ GAZ CHAUD)
───────────────────────────────────────────────────────────────

FORME COMPLÈTE:
  ┌─────────────────────────────────────────────────────────┐
  │                     0.026      μ^0.2 × Cp              │
  │ h_g = σ × ─────── × ────────── × (Pc/c*)^0.8 ×        │
  │                     Dt^0.2      Pr^0.6                  │
  │                                                         │
  │           × (Dt/R_c)^0.1 × (At/A)^0.9                  │
  └─────────────────────────────────────────────────────────┘

FACTEUR DE CORRECTION σ:
  ┌─────────────────────────────────────────────────────────┐
  │ σ = [½(Tw/Tc)(1 + (γ-1)/2 × M²) + ½]^(-0.68) ×        │
  │     × [1 + (γ-1)/2 × M²]^(-0.12)                       │
  │                                                         │
  │ Approximation au col (M=1):                             │
  │ σ ≈ [0.5 × Tw/Tc × (γ+1)/2 + 0.5]^(-0.68)             │
  └─────────────────────────────────────────────────────────┘

FORME SIMPLIFIÉE AU COL:
  ┌─────────────────────────────────────────────────────────┐
  │ h_g,throat = C × (Pc^0.8 / Dt^1.8) × σ                 │
  │                                                         │
  │ où C dépend des propriétés du gaz                       │
  │                                                         │
  │ Estimation rapide:                                      │
  │ h_g ≈ 5000 × (Pc/20)^0.8 × (30/Dt_mm)^1.8 [W/m²·K]    │
  └─────────────────────────────────────────────────────────┘

VARIATION LE LONG DE LA TUYÈRE:
  ┌─────────────────────────────────────────────────────────┐
  │ h_g(x) = h_g,throat × (Dt / D(x))^1.8                  │
  │                                                         │
  │ Au col:     h_g = h_g,throat (maximum)                  │
  │ Chambre:    h_g ≈ 0.3 × h_g,throat                     │
  │ Sortie:     h_g ≈ 0.05 × h_g,throat                    │
  └─────────────────────────────────────────────────────────┘


10.3 NOMBRES ADIMENSIONNELS
───────────────────────────────────────────────────────────────

NOMBRE DE REYNOLDS:
  ┌─────────────────────────────────────────────────────────┐
  │ Re = ρ × v × D_h / μ = v × D_h / ν                     │
  │                                                         │
  │ où: ρ = masse volumique [kg/m³]                         │
  │     v = vitesse [m/s]                                   │
  │     D_h = diamètre hydraulique [m]                      │
  │     μ = viscosité dynamique [Pa·s]                      │
  │     ν = viscosité cinématique [m²/s]                    │
  │                                                         │
  │ Régimes:                                                │
  │   Re < 2300      : Laminaire                            │
  │   2300 < Re < 10⁴: Transition                          │
  │   Re > 10⁴       : Turbulent                           │
  └─────────────────────────────────────────────────────────┘

NOMBRE DE PRANDTL:
  ┌─────────────────────────────────────────────────────────┐
  │ Pr = μ × Cp / k = ν / α                                │
  │                                                         │
  │ où: Cp = capacité thermique [J/kg·K]                    │
  │     k = conductivité thermique [W/m·K]                  │
  │     α = diffusivité thermique [m²/s]                    │
  │                                                         │
  │ Valeurs typiques:                                       │
  │   Gaz combustion : Pr ≈ 0.7-0.8                        │
  │   Eau           : Pr ≈ 7 (à 20°C)                      │
  │   RP-1          : Pr ≈ 15-25                           │
  │   LH2           : Pr ≈ 0.7-1.5                         │
  │   Huiles        : Pr ≈ 100-1000                        │
  └─────────────────────────────────────────────────────────┘

NOMBRE DE NUSSELT:
  ┌─────────────────────────────────────────────────────────┐
  │ Nu = h × D_h / k                                       │
  │                                                         │
  │ Interprétation: Nu = transfert convectif / conductif    │
  │                                                         │
  │ Pour obtenir h:                                         │
  │ h = Nu × k / D_h    [W/m²·K]                           │
  └─────────────────────────────────────────────────────────┘

DIAMÈTRE HYDRAULIQUE:
  ┌─────────────────────────────────────────────────────────┐
  │ D_h = 4 × A / P                                        │
  │                                                         │
  │ où: A = aire de la section [m²]                         │
  │     P = périmètre mouillé [m]                           │
  │                                                         │
  │ Cas particuliers:                                       │
  │   Tube circulaire:    D_h = D                          │
  │   Rectangle (a×b):    D_h = 2ab/(a+b)                  │
  │   Annulaire:          D_h = D_ext - D_int              │
  │   Carré (côté a):     D_h = a                          │
  └─────────────────────────────────────────────────────────┘


10.4 CORRÉLATIONS DE CONVECTION FORCÉE
───────────────────────────────────────────────────────────────

DITTUS-BOELTER (turbulent, fluides simples):
  ┌─────────────────────────────────────────────────────────┐
  │ Nu = 0.023 × Re^0.8 × Pr^n                             │
  │                                                         │
  │ n = 0.4  (chauffage du fluide)                         │
  │ n = 0.3  (refroidissement du fluide)                   │
  │                                                         │
  │ Validité: Re > 10,000                                   │
  │           0.6 < Pr < 160                                │
  │           L/D > 10                                      │
  └─────────────────────────────────────────────────────────┘

SIEDER-TATE (correction viscosité):
  ┌─────────────────────────────────────────────────────────┐
  │ Nu = 0.027 × Re^0.8 × Pr^(1/3) × (μ_bulk/μ_wall)^0.14 │
  │                                                         │
  │ Recommandé quand:                                       │
  │   T_wall >> T_bulk (grande variation de μ)             │
  └─────────────────────────────────────────────────────────┘

GNIELINSKI (transition + turbulent):
  ┌─────────────────────────────────────────────────────────┐
  │       (f/8) × (Re - 1000) × Pr                         │
  │ Nu = ─────────────────────────────────────             │
  │       1 + 12.7 × (f/8)^0.5 × (Pr^(2/3) - 1)            │
  │                                                         │
  │ avec f = (0.79 × ln(Re) - 1.64)^(-2)                   │
  │                                                         │
  │ Validité: 2300 < Re < 5×10⁶                            │
  │           0.5 < Pr < 2000                               │
  └─────────────────────────────────────────────────────────┘

PETUKHOV (haute précision, turbulent):
  ┌─────────────────────────────────────────────────────────┐
  │       (f/8) × Re × Pr                                  │
  │ Nu = ──────────────────────────────────────            │
  │       1.07 + 12.7 × (f/8)^0.5 × (Pr^(2/3) - 1)         │
  │                                                         │
  │ avec f = (0.790 × ln(Re) - 1.64)^(-2)                  │
  │                                                         │
  │ Précision: ±5% pour 10⁴ < Re < 5×10⁶                   │
  └─────────────────────────────────────────────────────────┘

LAMINAIRE (Re < 2300):
  ┌─────────────────────────────────────────────────────────┐
  │ Tube long, T_wall constante:                           │
  │   Nu = 3.66                                             │
  │                                                         │
  │ Tube long, flux constant:                              │
  │   Nu = 4.36                                             │
  │                                                         │
  │ Tube court (développement thermique):                  │
  │   Nu = 1.86 × (Re × Pr × D/L)^(1/3) × (μ_b/μ_w)^0.14  │
  └─────────────────────────────────────────────────────────┘


10.5 ÉQUATIONS DE TEMPÉRATURE DE PAROI
───────────────────────────────────────────────────────────────

PROFIL DE TEMPÉRATURE À TRAVERS LA PAROI:
  ┌─────────────────────────────────────────────────────────┐
  │ T_gaz ──────▶ T_wall_hot ──────▶ T_wall_cold ──────▶ T_coolant │
  │         h_g           k/e              h_c              │
  │                                                         │
  │ T_wall_hot = T_gaz - q/h_g                             │
  │                                                         │
  │ T_wall_cold = T_wall_hot - q×e/k                       │
  │              = T_coolant + q/h_c                        │
  │                                                         │
  │ Vérification: T_wall_hot = T_coolant + q×(1/h_c + e/k) │
  └─────────────────────────────────────────────────────────┘

TEMPÉRATURE ADIABATIQUE DE PAROI (T_aw):
  ┌─────────────────────────────────────────────────────────┐
  │ T_aw = T_statique × [1 + r × (γ-1)/2 × M²]             │
  │                                                         │
  │ Facteur de récupération r:                              │
  │   r = Pr^(1/2)  pour laminaire                         │
  │   r = Pr^(1/3)  pour turbulent                         │
  │                                                         │
  │ Au col (M=1):                                           │
  │   T_aw ≈ 0.90 × T_c  (gaz combustion typique)          │
  └─────────────────────────────────────────────────────────┘

TEMPÉRATURE CRITIQUE DE PAROI:
  ┌─────────────────────────────────────────────────────────┐
  │ Marge thermique:                                        │
  │   Marge = T_limite - T_wall_hot                        │
  │                                                         │
  │ Condition de sécurité:                                  │
  │   T_wall_hot < T_limite  (typiquement 20% de marge)    │
  │                                                         │
  │ Limite absolue:                                         │
  │   T_wall_hot << T_fusion  (facteur 1.5 minimum)        │
  └─────────────────────────────────────────────────────────┘


10.6 ÉPAISSEUR DE PAROI
───────────────────────────────────────────────────────────────

ÉPAISSEUR MAXIMALE (critère thermique):
  ┌─────────────────────────────────────────────────────────┐
  │ e_max = k × (T_limite - T_wall_cold) / q               │
  │                                                         │
  │ Si e > e_max: T_wall_hot > T_limite → Défaillance!     │
  └─────────────────────────────────────────────────────────┘

ÉPAISSEUR DE FUSION:
  ┌─────────────────────────────────────────────────────────┐
  │ e_melt = k × (T_fusion - T_wall_cold) / q              │
  │                                                         │
  │ Si e > e_melt: La paroi fond côté gaz!                 │
  └─────────────────────────────────────────────────────────┘

ÉPAISSEUR SACRIFICIELLE:
  ┌─────────────────────────────────────────────────────────┐
  │ e_sacrif = e_initial - e_melt                          │
  │                                                         │
  │ Épaisseur de matériau qui peut fondre sans             │
  │ compromettre l'intégrité structurelle.                 │
  │                                                         │
  │ Condition: e_sacrif > 0 et e_restante > e_min_struct   │
  └─────────────────────────────────────────────────────────┘

ÉPAISSEUR MINIMALE (critère mécanique):
  ┌─────────────────────────────────────────────────────────┐
  │ e_min = Pc × r / σ_admissible                          │
  │                                                         │
  │ où: Pc = pression chambre [Pa]                          │
  │     r = rayon local [m]                                 │
  │     σ_admissible = contrainte admissible à T [Pa]       │
  │                                                         │
  │ Note: σ_admissible diminue avec T!                     │
  └─────────────────────────────────────────────────────────┘


10.7 PUISSANCE ET ÉNERGIE THERMIQUE
───────────────────────────────────────────────────────────────

PUISSANCE THERMIQUE TOTALE:
  ┌─────────────────────────────────────────────────────────┐
  │ Q_total = ∫ q(x) × dA                                  │
  │                                                         │
  │ Approximation:                                          │
  │ Q_total ≈ q_moyen × A_totale                           │
  │                                                         │
  │ où: q_moyen ≈ 0.3 × q_col (valeur typique)             │
  └─────────────────────────────────────────────────────────┘

ÉLÉVATION DE TEMPÉRATURE DU COOLANT:
  ┌─────────────────────────────────────────────────────────┐
  │ ΔT_coolant = Q_total / (ṁ_coolant × Cp_coolant)        │
  │                                                         │
  │ T_sortie = T_entrée + ΔT_coolant                       │
  │                                                         │
  │ Condition: T_sortie < T_ébullition ou T_décomposition  │
  └─────────────────────────────────────────────────────────┘

FRACTION DE CHALEUR ABSORBÉE:
  ┌─────────────────────────────────────────────────────────┐
  │ η_thermique = Q_total / Q_combustion                   │
  │                                                         │
  │ Q_combustion = ṁ_propergols × ΔH_combustion            │
  │                                                         │
  │ Typiquement: η_thermique ≈ 1-5%                        │
  └─────────────────────────────────────────────────────────┘


10.8 PERTES DE CHARGE
───────────────────────────────────────────────────────────────

ÉQUATION DE DARCY-WEISBACH:
  ┌─────────────────────────────────────────────────────────┐
  │ Δp = f × (L/D_h) × (ρ × v²) / 2                        │
  │                                                         │
  │ où: f = facteur de friction                             │
  │     L = longueur du canal [m]                           │
  │     D_h = diamètre hydraulique [m]                      │
  └─────────────────────────────────────────────────────────┘

FACTEUR DE FRICTION:
  ┌─────────────────────────────────────────────────────────┐
  │ Laminaire (Re < 2300):                                  │
  │   f = 64 / Re                                           │
  │                                                         │
  │ Turbulent lisse (Blasius, Re < 10⁵):                   │
  │   f = 0.316 / Re^0.25                                  │
  │                                                         │
  │ Turbulent (Petukhov, Re > 3000):                       │
  │   f = (0.790 × ln(Re) - 1.64)^(-2)                     │
  │                                                         │
  │ Avec rugosité (Colebrook-White):                       │
  │   1/√f = -2×log₁₀(ε/3.7D + 2.51/(Re×√f))              │
  └─────────────────────────────────────────────────────────┘

PUISSANCE DE POMPAGE:
  ┌─────────────────────────────────────────────────────────┐
  │ P_pompe = Δp × Q_volumique / η_pompe                   │
  │         = Δp × ṁ / (ρ × η_pompe)                       │
  │                                                         │
  │ où: Q_volumique = débit volumique [m³/s]                │
  │     η_pompe = rendement de la pompe                     │
  └─────────────────────────────────────────────────────────┘


10.9 FILM COOLING
───────────────────────────────────────────────────────────────

EFFICACITÉ DU FILM:
  ┌─────────────────────────────────────────────────────────┐
  │ η_film = (T_aw - T_aw,film) / (T_aw - T_coolant)       │
  │                                                         │
  │ où: T_aw,film = température adiabatique avec film       │
  │     T_coolant = température du film injecté             │
  │                                                         │
  │ T_aw,effective = T_coolant + η_film × (T_aw - T_coolant)│
  └─────────────────────────────────────────────────────────┘

DÉBIT DE FILM:
  ┌─────────────────────────────────────────────────────────┐
  │ Règle empirique:                                        │
  │   ṁ_film = 2-5% du débit fuel pour protection locale   │
  │   ṁ_film = 10-20% pour protection chambre complète     │
  │                                                         │
  │ Efficacité typique:                                     │
  │   η_film ≈ 0.3 - 0.6 selon injection et géométrie      │
  └─────────────────────────────────────────────────────────┘

RÉDUCTION DE FLUX EFFECTIVE:
  ┌─────────────────────────────────────────────────────────┐
  │ q_avec_film = h_g × (T_aw,effective - T_wall_hot)      │
  │                                                         │
  │ Réduction typique: 30-60% du flux sans film            │
  └─────────────────────────────────────────────────────────┘


10.10 PROPRIÉTÉS DES GAZ DE COMBUSTION
───────────────────────────────────────────────────────────────

ESTIMATION DES PROPRIÉTÉS:
  ┌─────────────────────────────────────────────────────────┐
  │ Viscosité dynamique (loi de Sutherland):               │
  │   μ = μ₀ × (T/T₀)^1.5 × (T₀ + S)/(T + S)               │
  │                                                         │
  │ Pour gaz de combustion (approximation):                │
  │   μ ≈ 3×10⁻⁷ × T^0.7  [Pa·s]                          │
  │                                                         │
  │ Conductivité thermique:                                │
  │   k = Cp × μ / Pr                                      │
  │   k ≈ Cp × μ / 0.72  [W/m·K]                          │
  │                                                         │
  │ Cp (J/kg·K) typique:                                   │
  │   LOX/RP-1: 2000-2200                                  │
  │   LOX/LH2:  3500-4000                                  │
  │   LOX/CH4:  2400-2800                                  │
  └─────────────────────────────────────────────────────────┘


10.11 TABLEAU RÉCAPITULATIF DES FORMULES
───────────────────────────────────────────────────────────────

  ┌──────────────────────────────┬────────────────────────────────────────┐
  │ GRANDEUR                     │ FORMULE                                │
  ├──────────────────────────────┼────────────────────────────────────────┤
  │ Flux thermique               │ q = ΔT / R_total                       │
  │ Résistance totale            │ R = 1/h_g + e/k + 1/h_c                │
  │ Coefficient global           │ U = 1/R_total                          │
  │ T paroi chaude               │ T_hot = T_gaz - q/h_g                  │
  │ T paroi froide               │ T_cold = T_coolant + q/h_c             │
  │ Gradient dans paroi          │ ΔT_paroi = q × e / k                   │
  ├──────────────────────────────┼────────────────────────────────────────┤
  │ Reynolds                     │ Re = ρ·v·D_h / μ                       │
  │ Prandtl                      │ Pr = μ·Cp / k                          │
  │ Nusselt (Dittus-Boelter)     │ Nu = 0.023·Re^0.8·Pr^0.4               │
  │ h depuis Nu                  │ h = Nu·k / D_h                         │
  │ Diamètre hydraulique         │ D_h = 4·A / P                          │
  ├──────────────────────────────┼────────────────────────────────────────┤
  │ Épaisseur max thermique      │ e_max = k·(T_lim - T_cold) / q         │
  │ Épaisseur fusion             │ e_melt = k·(T_fus - T_cold) / q        │
  │ Épaisseur min mécanique      │ e_min = P·r / σ_adm                    │
  ├──────────────────────────────┼────────────────────────────────────────┤
  │ Puissance thermique          │ Q = ∫q·dA ≈ q_moy × A                  │
  │ ΔT coolant                   │ ΔT = Q / (ṁ·Cp)                        │
  │ Perte de charge              │ Δp = f·(L/D_h)·ρ·v²/2                  │
  └──────────────────────────────┴────────────────────────────────────────┘


10.12 ORDRES DE GRANDEUR TYPIQUES
───────────────────────────────────────────────────────────────

FLUX THERMIQUE AU COL:
  ┌─────────────────────────────────────────────────────────┐
  │ Moteur amateur (Pc < 10 bar):      1 - 5 MW/m²         │
  │ Petit moteur (Pc ~ 20-50 bar):     5 - 20 MW/m²        │
  │ Moteur orbital (Pc ~ 50-100 bar):  15 - 50 MW/m²       │
  │ Moteur haute Pc (> 150 bar):       30 - 80 MW/m²       │
  │ Record (SSME au col):              130 MW/m²           │
  └─────────────────────────────────────────────────────────┘

COEFFICIENTS DE TRANSFERT:
  ┌─────────────────────────────────────────────────────────┐
  │ h_g au col:                                             │
  │   Pc = 20 bar:     3,000 - 8,000 W/m²·K                │
  │   Pc = 50 bar:     8,000 - 20,000 W/m²·K               │
  │   Pc = 100 bar:    15,000 - 40,000 W/m²·K              │
  │   Pc = 200 bar:    30,000 - 80,000 W/m²·K              │
  │                                                         │
  │ h_c (coolant):                                          │
  │   RP-1:            5,000 - 30,000 W/m²·K               │
  │   LCH4:            20,000 - 80,000 W/m²·K              │
  │   LH2:             50,000 - 200,000 W/m²·K             │
  │   Eau:             5,000 - 50,000 W/m²·K               │
  └─────────────────────────────────────────────────────────┘

TEMPÉRATURES:
  ┌─────────────────────────────────────────────────────────┐
  │ T chambre:                                              │
  │   LOX/RP-1:        3200 - 3500 K                       │
  │   LOX/LH2:         3400 - 3600 K                       │
  │   LOX/CH4:         3300 - 3500 K                       │
  │   N2O4/UDMH:       3000 - 3200 K                       │
  │                                                         │
  │ T paroi hot typique:                                    │
  │   Cuivre allié:    500 - 800 K                         │
  │   Ni superalliage: 800 - 1100 K                        │
  │   Réfractaires:    1200 - 2000 K                       │
  └─────────────────────────────────────────────────────────┘

GÉOMÉTRIE:
  ┌─────────────────────────────────────────────────────────┐
  │ Épaisseur paroi:   0.5 - 10 mm                         │
  │ Largeur canal:     1 - 5 mm                            │
  │ Profondeur canal:  1 - 10 mm                           │
  │ Nombre canaux:     20 - 500                            │
  │ Vitesse coolant:   5 - 50 m/s                          │
  │ Δp canaux:         2 - 20 bar                          │
  └─────────────────────────────────────────────────────────┘


10.13 CONVERSIONS UTILES
───────────────────────────────────────────────────────────────

  ┌────────────────────────────────────────────────────────────────┐
  │ TEMPÉRATURE                                                     │
  │   K = °C + 273.15                                               │
  │   °C = (°F - 32) × 5/9                                         │
  │   K = (°F + 459.67) × 5/9                                      │
  ├────────────────────────────────────────────────────────────────┤
  │ PRESSION                                                        │
  │   1 bar = 100,000 Pa = 0.1 MPa                                 │
  │   1 bar = 14.504 psi                                           │
  │   1 atm = 101,325 Pa = 1.01325 bar                             │
  ├────────────────────────────────────────────────────────────────┤
  │ ÉNERGIE / PUISSANCE                                            │
  │   1 MW = 10⁶ W                                                 │
  │   1 kW = 1.341 hp                                              │
  │   1 BTU/s = 1055 W                                             │
  ├────────────────────────────────────────────────────────────────┤
  │ FLUX THERMIQUE                                                  │
  │   1 MW/m² = 10⁶ W/m²                                           │
  │   1 BTU/(h·ft²) = 3.155 W/m²                                   │
  ├────────────────────────────────────────────────────────────────┤
  │ COEFFICIENT DE TRANSFERT                                        │
  │   1 W/(m²·K) = 0.1761 BTU/(h·ft²·°F)                           │
  │   1 BTU/(h·ft²·°F) = 5.678 W/(m²·K)                            │
  ├────────────────────────────────────────────────────────────────┤
  │ CONDUCTIVITÉ THERMIQUE                                          │
  │   1 W/(m·K) = 0.5778 BTU/(h·ft·°F)                             │
  └────────────────────────────────────────────────────────────────┘


10.14 CONSTANTES PHYSIQUES
───────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────┐
  │ Constante des gaz parfaits:                             │
  │   R = 8.314 J/(mol·K)                                   │
  │                                                         │
  │ Constante de Stefan-Boltzmann:                         │
  │   σ = 5.67×10⁻⁸ W/(m²·K⁴)                              │
  │                                                         │
  │ Nombre d'Avogadro:                                     │
  │   N_A = 6.022×10²³ mol⁻¹                               │
  │                                                         │
  │ Accélération gravitationnelle:                         │
  │   g₀ = 9.80665 m/s²                                    │
  └─────────────────────────────────────────────────────────┘


RÉFÉRENCES BIBLIOGRAPHIQUES
═══════════════════════════════════════════════════════════════

OUVRAGES DE RÉFÉRENCE:
  ┌─────────────────────────────────────────────────────────┐
  │ • Sutton & Biblarz - "Rocket Propulsion Elements"       │
  │   (9th ed., 2016) - Référence principale               │
  │                                                         │
  │ • Humble, Henry & Larson - "Space Propulsion Analysis  │
  │   and Design" (1995) - Conception détaillée            │
  │                                                         │
  │ • Huzel & Huang - "Modern Engineering for Design of    │
  │   Liquid-Propellant Rocket Engines" (1992)             │
  │                                                         │
  │ • Hill & Peterson - "Mechanics and Thermodynamics      │
  │   of Propulsion" (1992)                                 │
  └─────────────────────────────────────────────────────────┘

PUBLICATIONS TECHNIQUES:
  ┌─────────────────────────────────────────────────────────┐
  │ • Bartz, D.R. (1957) - "A Simple Equation for Rapid    │
  │   Estimation of Rocket Nozzle Convective Heat Transfer │
  │   Coefficients" - Jet Propulsion, Vol. 27, No. 1       │
  │                                                         │
  │ • Dittus, F.W. & Boelter, L.M.K. (1930) - "Heat        │
  │   Transfer in Automobile Radiators of the Tubular Type"│
  │   University of California Publications, Vol. 2        │
  │                                                         │
  │ • Gnielinski, V. (1976) - "New Equations for Heat and  │
  │   Mass Transfer in Turbulent Pipe and Channel Flow"    │
  │   Int. Chem. Eng., Vol. 16, No. 2                      │
  │                                                         │
  │ • Sieder, E.N. & Tate, G.E. (1936) - "Heat Transfer    │
  │   and Pressure Drop of Liquids in Tubes"               │
  │   Industrial & Engineering Chemistry, Vol. 28          │
  └─────────────────────────────────────────────────────────┘

DOCUMENTS NASA:
  ┌─────────────────────────────────────────────────────────┐
  │ • NASA SP-125 - "Design of Liquid Propellant Rocket    │
  │   Engines" (Huzel & Huang, 1967)                       │
  │                                                         │
  │ • NASA SP-8014 - "Entry Thermal Protection" (1968)     │
  │                                                         │
  │ • NASA TM-X-52386 - "Regenerative Cooling of Rocket    │
  │   Engines" (1967)                                       │
  │                                                         │
  │ • NASA CR-134806 - "High Pressure LOX/Hydrogen         │
  │   Regenerative Cooling" (1975)                         │
  └─────────────────────────────────────────────────────────┘

LOGICIELS ET BASES DE DONNÉES:
  ┌─────────────────────────────────────────────────────────┐
  │ • CEA (Chemical Equilibrium with Applications)         │
  │   NASA Glenn Research Center                           │
  │   https://www.grc.nasa.gov/WWW/CEAWeb/                 │
  │                                                         │
  │ • NIST Chemistry WebBook                               │
  │   https://webbook.nist.gov/chemistry/                  │
  │                                                         │
  │ • RocketCEA (Python wrapper)                           │
  │   https://rocketcea.readthedocs.io/                    │
  └─────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════
Document généré par Rocket Motor Design Plotter v6 - Décembre 2025
'''
        
        # Insérer le contenu avec formatage
        lines = content.split('\n')
        for line in lines:
            if line.startswith('🔥') or line.startswith('═══'):
                self.wiki_text.insert(tk.END, line + '\n', "h1")
            elif line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')) and 'INTRODUCTION' in line or 'THÉORIE' in line or 'MODÈLE' in line or 'CALCUL' in line or 'CORRÉLATION' in line or 'ÉPAISSEUR' in line or 'PROPRIÉTÉS' in line or 'EXEMPLE' in line or 'FORMULES' in line or 'RÉFÉRENCES' in line:
                self.wiki_text.insert(tk.END, line + '\n', "h2")
            elif line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                self.wiki_text.insert(tk.END, line + '\n', "h2")
            elif line.strip().startswith(('2.1', '2.2', '2.3', '3.1', '3.2', '3.3', '4.1', '4.2', '5.1', '5.2', '5.3', '6.1', '6.2', '6.3')):
                self.wiki_text.insert(tk.END, line + '\n', "h3")
            elif line.strip().startswith('───'):
                self.wiki_text.insert(tk.END, line + '\n', "h2")
            elif '=' in line and ('q =' in line or 'Nu =' in line or 'Re =' in line or 'Pr =' in line or 'h_' in line or 'T_' in line or 'e_' in line):
                self.wiki_text.insert(tk.END, line + '\n', "formula")
            elif line.strip().startswith(('⚠️', '💀', '🔥', '✅', '❌')):
                self.wiki_text.insert(tk.END, line + '\n', "important")
            elif line.strip().startswith(('┌', '├', '└', '│')):
                self.wiki_text.insert(tk.END, line + '\n', "code")
            elif 'ÉTAPE' in line:
                self.wiki_text.insert(tk.END, line + '\n', "h3")
            else:
                self.wiki_text.insert(tk.END, line + '\n', "normal")
        
        self.wiki_text.config(state=tk.DISABLED)
    
    def wiki_search(self):
        """Recherche dans le wiki"""
        search_term = self.wiki_search_var.get()
        if not search_term:
            return
        
        # Supprimer les highlights précédents
        self.wiki_text.tag_remove("highlight", "1.0", tk.END)
        
        # Chercher depuis le début
        self.wiki_search_pos = "1.0"
        self.wiki_search_next()
    
    def wiki_search_next(self):
        """Trouve l'occurrence suivante"""
        search_term = self.wiki_search_var.get()
        if not search_term:
            return
        
        # Chercher
        pos = self.wiki_text.search(search_term, self.wiki_search_pos, nocase=True, stopindex=tk.END)
        
        if pos:
            # Calculer la fin
            end_pos = f"{pos}+{len(search_term)}c"
            
            # Highlight
            self.wiki_text.tag_add("highlight", pos, end_pos)
            
            # Scroll vers la position
            self.wiki_text.see(pos)
            
            # Préparer pour la prochaine recherche
            self.wiki_search_pos = end_pos
        else:
            # Revenir au début
            self.wiki_search_pos = "1.0"
            messagebox.showinfo("Recherche", f"Fin du document atteinte pour '{search_term}'")
    
    def wiki_goto_section(self, event):
        """Aller à une section du sommaire"""
        selection = self.wiki_toc.curselection()
        if not selection:
            return
        
        item = self.wiki_toc.get(selection[0])
        
        # Extraire le numéro de section
        section_map = {
            "1.": "1. INTRODUCTION",
            "1.1": "1.1 POURQUOI LE REFROIDISSEMENT",
            "1.2": "1.2 LES DIFFÉRENTES STRATÉGIES",
            "1.3": "1.3 SCHÉMA DU TRANSFERT",
            "1.4": "1.4 ÉQUATIONS FONDAMENTALES",
            "1.5": "1.5 ORDRES DE GRANDEUR",
            "2.": "2. THÉORIE DÉTAILLÉE",
            "2.1": "2.1 LA CONDUCTION THERMIQUE",
            "2.2": "2.2 LA CONVECTION THERMIQUE",
            "2.3": "2.3 LES NOMBRES ADIMENSIONNELS",
            "3.": "3. MODÈLE DE BARTZ",
            "3.1": "3.1 HISTORIQUE",
            "3.2": "3.2 ÉQUATION COMPLÈTE",
            "3.3": "3.3 FORMULE SIMPLIFIÉE",
            "3.4": "3.4 PROPRIÉTÉS DES GAZ",
            "3.5": "3.5 VALEURS TYPIQUES DE h_g",
            "3.6": "3.6 LIMITATIONS",
            "3.7": "3.7 COMPARAISON",
            "4.": "4. CALCUL DES TEMPÉRATURES",
            "4.1": "4.1 SYSTÈME D'ÉQUATIONS",
            "4.2": "4.2 CALCUL DE T_WALL_HOT",
            "4.3": "4.3 CALCUL DE T_WALL_COLD",
            "4.4": "4.4 PROFIL DE TEMPÉRATURE",
            "4.5": "4.5 CONTRAINTES THERMIQUES",
            "4.6": "4.6 RÉGIME TRANSITOIRE",
            "4.7": "4.7 TEMPÉRATURE ADIABATIQUE",
            "4.8": "4.8 CALCUL ITÉRATIF",
            "5.": "5. CORRÉLATIONS CÔTÉ COOLANT",
            "5.1": "5.1 CORRÉLATION DE DITTUS",
            "5.2": "5.2 CORRÉLATION DE GNIELINSKI",
            "5.3": "5.3 RÉGIME LAMINAIRE",
            "5.4": "5.4 RÉGIME TRANSITOIRE",
            "5.5": "5.5 ÉBULLITION SOUS-REFROIDIE",
            "5.6": "5.6 EFFETS DE LA GÉOMÉTRIE",
            "5.7": "5.7 PERTES DE CHARGE",
            "5.8": "5.8 VALEURS TYPIQUES DE h_c",
            "6.": "6. ÉPAISSEUR CRITIQUE",
            "6.1": "6.1 ÉPAISSEUR CRITIQUE DE FUSION",
            "6.2": "6.2 ÉPAISSEUR DE SERVICE",
            "6.3": "6.3 PROCESSUS D'ABLATION",
            "6.4": "6.4 ÉPAISSEUR SACRIFICIELLE",
            "6.5": "6.5 TEMPS D'ABLATION",
            "6.6": "6.6 QUAND L'ABLATION",
            "6.7": "6.7 DIMENSIONNEMENT",
            "6.8": "6.8 CARTE THERMIQUE",
            "7.": "7. PROPRIÉTÉS DES MATÉRIAUX",
            "7.1": "7.1 TABLEAU RÉCAPITULATIF",
            "7.2": "7.2 ALLIAGES DE CUIVRE",
            "7.3": "7.3 SUPERALLIAGES BASE NICKEL",
            "7.4": "7.4 ALLIAGES D'ALUMINIUM",
            "7.5": "7.5 MÉTAUX RÉFRACTAIRES",
            "7.6": "7.6 MATÉRIAUX CÉRAMIQUES",
            "7.7": "7.7 CRITÈRES DE SÉLECTION",
            "7.8": "7.8 EXEMPLES DE MOTEURS",
            "8.": "8. PROPRIÉTÉS DES COOLANTS",
            "8.1": "8.1 TABLEAU RÉCAPITULATIF",
            "8.2": "8.2 HYDROGÈNE LIQUIDE",
            "8.3": "8.3 OXYGÈNE LIQUIDE",
            "8.4": "8.4 MÉTHANE LIQUIDE",
            "8.5": "8.5 RP-1",
            "8.6": "8.6 ÉTHANOL",
            "8.7": "8.7 HYDRAZINE",
            "8.8": "8.8 EAU",
            "8.9": "8.9 AMMONIAC",
            "8.10": "8.10 COMPARAISON",
            "8.11": "8.11 PROPRIÉTÉS EN FONCTION",
            "9.": "9. EXEMPLES DE CALCUL",
            "9.1": "9.1 EXEMPLE 1",
            "9.2": "9.2 EXEMPLE 2",
            "9.3": "9.3 EXEMPLE 3",
            "9.4": "9.4 EXEMPLE 4",
            "9.5": "9.5 EXEMPLE 5",
            "9.6": "9.6 EXEMPLE 6",
            "9.7": "9.7 TABLEAU RÉCAPITULATIF",
            "9.8": "9.8 EXERCICES",
            "10.": "10. FORMULES RAPIDES",
            "10.1": "10.1 ÉQUATIONS FONDAMENTALES",
            "10.2": "10.2 ÉQUATION DE BARTZ",
            "10.3": "10.3 NOMBRES ADIMENSIONNELS",
            "10.4": "10.4 CORRÉLATIONS DE CONVECTION",
            "10.5": "10.5 ÉQUATIONS DE TEMPÉRATURE",
            "10.6": "10.6 ÉPAISSEUR DE PAROI",
            "10.7": "10.7 PUISSANCE ET ÉNERGIE",
            "10.8": "10.8 PERTES DE CHARGE",
            "10.9": "10.9 FILM COOLING",
            "10.10": "10.10 PROPRIÉTÉS DES GAZ",
            "10.11": "10.11 TABLEAU RÉCAPITULATIF",
            "10.12": "10.12 ORDRES DE GRANDEUR",
            "10.13": "10.13 CONVERSIONS",
            "10.14": "10.14 CONSTANTES",
            "Réf": "RÉFÉRENCES",
        }
        
        # Chercher le texte correspondant
        search_text = None
        for key, value in section_map.items():
            if item.strip().startswith(key):
                search_text = value
                break
        
        if search_text:
            pos = self.wiki_text.search(search_text, "1.0", nocase=True)
            if pos:
                self.wiki_text.see(pos)

    def load_database(self):
        """Charge tous les propergols depuis RocketCEA"""
        from rocketcea.blends import fuelCards, oxCards, getFuelRefTempDegK, getOxRefTempDegK, getFloatTokenFromCards
        
        self.propellant_db = []
        
        # Table des coolants communs (non dans RocketCEA)
        common_coolants = {
            "H2O": {"type": "Coolant", "t_ref": 373, "formula": "Eau - Cp=4186 J/kg-K"},
            "Water": {"type": "Coolant", "t_ref": 373, "formula": "Eau - Cp=4186 J/kg-K"},
            "EG": {"type": "Coolant", "t_ref": 470, "formula": "Ethylène Glycol - Cp=2400 J/kg-K"},
            "PG": {"type": "Coolant", "t_ref": 461, "formula": "Propylène Glycol - Cp=2500 J/kg-K"},
            "Dowtherm": {"type": "Coolant", "t_ref": 530, "formula": "Huile thermique - Cp=1800 J/kg-K"},
            "LN2": {"type": "Coolant", "t_ref": 77, "formula": "Azote Liquide - Cp=2040 J/kg-K"},
            "Therminol": {"type": "Coolant", "t_ref": 632, "formula": "Huile thermique - Cp=1900 J/kg-K"},
        }
        
        # Charger les fuels
        for name, cards in fuelCards.items():
            try:
                t_ref = getFuelRefTempDegK(name)
            except:
                t_ref = 298
            
            # Extraire la formule depuis les cards
            formula = ""
            if cards and len(cards) > 0:
                formula = cards[0].strip()[:50]
            
            self.propellant_db.append({
                "name": name,
                "type": "Fuel",
                "t_ref": t_ref,
                "formula": formula,
                "cards": cards
            })
        
        # Charger les oxydants
        for name, cards in oxCards.items():
            try:
                t_ref = getOxRefTempDegK(name)
            except:
                t_ref = 298
            
            formula = ""
            if cards and len(cards) > 0:
                formula = cards[0].strip()[:50]
            
            self.propellant_db.append({
                "name": name,
                "type": "Oxydant",
                "t_ref": t_ref,
                "formula": formula,
                "cards": cards
            })
        
        # Ajouter les coolants communs
        for name, info in common_coolants.items():
            self.propellant_db.append({
                "name": name,
                "type": info["type"],
                "t_ref": info["t_ref"],
                "formula": info["formula"],
                "cards": []
            })
        
        # Trier par nom
        self.propellant_db.sort(key=lambda x: x["name"].lower())
        
        # Afficher tout
        self.search_database()
    
    def search_database(self):
        """Filtre et affiche les propergols selon la recherche"""
        # Effacer la liste
        for item in self.db_tree.get_children():
            self.db_tree.delete(item)
        
        search_term = self.db_search.get().lower()
        type_filter = self.db_type.get()
        
        for prop in self.propellant_db:
            # Filtrer par type
            if type_filter == "Fuels (Carburants)" and prop["type"] != "Fuel":
                continue
            if type_filter == "Oxydants" and prop["type"] != "Oxydant":
                continue
            if type_filter == "Coolants Communs" and prop["type"] != "Coolant":
                continue
            
            # Filtrer par recherche
            if search_term:
                if search_term not in prop["name"].lower() and search_term not in prop["formula"].lower():
                    continue
            
            # Ajouter à la liste
            t_ref_str = f"{prop['t_ref']:.1f}" if prop['t_ref'] is not None else "N/A"
            self.db_tree.insert("", tk.END, values=(
                prop["name"],
                prop["type"],
                t_ref_str,
                prop["formula"][:40] if prop["formula"] else ""
            ))
    
    def on_propellant_select(self, event):
        """Affiche les détails du propergol sélectionné avec coloration syntaxique"""
        import re
        selection = self.db_tree.selection()
        if not selection:
            return
        
        item = self.db_tree.item(selection[0])
        name = item["values"][0]
        
        # Trouver le propergol dans la DB
        prop = None
        for p in self.propellant_db:
            if p["name"] == name:
                prop = p
                break
        
        if not prop:
            return
        
        self.db_details.config(state='normal')
        self.db_details.delete(1.0, tk.END)
        
        # Helper pour insérer avec couleurs
        def insert_separator(text):
            self.db_details.insert(tk.END, text + '\n', 'db_label')
        
        def insert_title(text):
            self.db_details.insert(tk.END, text + '\n', 'db_title')
        
        def insert_section(text):
            self.db_details.insert(tk.END, text + '\n', 'db_section')
        
        def insert_line(label, value, unit=""):
            self.db_details.insert(tk.END, f"{label}: ", 'db_label')
            # Coloriser les nombres dans la valeur
            str_val = str(value)
            tokens = re.split(r'(-?\d+\.?\d*)', str_val)
            for token in tokens:
                if re.match(r'^-?\d+\.?\d*$', token) and token:
                    self.db_details.insert(tk.END, token, 'db_number')
                else:
                    self.db_details.insert(tk.END, token, 'db_string')
            if unit:
                self.db_details.insert(tk.END, f" {unit}", 'db_unit')
            self.db_details.insert(tk.END, '\n')
        
        # Construire les détails
        t_ref = prop['t_ref'] if prop['t_ref'] is not None else 298
        
        insert_separator("═══════════════════════════════════════")
        insert_title(f"  PROPERGOL: {prop['name']}")
        insert_separator("═══════════════════════════════════════\n")
        
        insert_line("Type            ", prop['type'])
        insert_line("T référence     ", f"{t_ref:.2f}", f"K ({t_ref-273.15:.1f}°C)")
        self.db_details.insert(tk.END, '\n')
        
        # Ajouter les propriétés thermiques si disponibles
        if prop['type'] == 'Coolant':
            insert_section("--- PROPRIÉTÉS COOLANT ---")
            insert_line("Info", prop['formula'])
            self.db_details.insert(tk.END, '\n', '')
            self.db_details.insert(tk.END, "Utilisable directement comme coolant externe.\n", 'db_success')
            self.db_details.insert(tk.END, "Tapez ce nom dans le champ 'Coolant' du simulateur.\n", 'db_string')
        
        elif prop['type'] == 'Fuel':
            from rocketcea.blends import fuelCards, getFuelRefTempDegK, getFloatTokenFromCards
            
            insert_section("--- CARTE NASA CEA ---")
            if prop['cards']:
                for card in prop['cards']:
                    self.db_details.insert(tk.END, f"{card}\n", 'db_string')
            
            insert_section("\n--- PROPRIÉTÉS EXTRAITES ---")
            try:
                cards = fuelCards.get(prop['name'], [])
                rho = getFloatTokenFromCards(cards, 'rho')
                if rho:
                    insert_line("Densité (rho)   ", f"{rho:.4f}", f"g/cm³ ({rho*1000:.1f} kg/m³)")
                
                # Chercher h,cal (enthalpie)
                for card in cards:
                    if 'h,cal' in card:
                        match = re.search(r'h,cal=(-?\d+\.?\d*)', card)
                        if match:
                            h_cal = float(match.group(1))
                            insert_line("Enthalpie (h)   ", f"{h_cal:.1f}", "cal/mol")
            except Exception as e:
                self.db_details.insert(tk.END, f"Erreur extraction: {e}\n", 'db_label')
            
            # Ajouter les propriétés thermiques si dans nos tables
            cp_table = {
                "C3H8": 2500, "CH4": 3500, "LH2": 14300, "RP1": 2000, "RP_1": 2000,
                "C2H5OH": 2440, "CH3OH": 2500, "MMH": 2900, "N2H4": 3100, "UDMH": 2700, "NH3": 4700
            }
            hvap_table = {
                "C3H8": 426, "CH4": 510, "LH2": 446, "RP1": 290, "RP_1": 290,
                "C2H5OH": 841, "CH3OH": 1100, "MMH": 800, "N2H4": 1220, "UDMH": 540, "NH3": 1370
            }
            t_crit_table = {
                "C3H8": 370, "CH4": 191, "LH2": 33, "RP1": 678, "RP_1": 678,
                "C2H5OH": 514, "CH3OH": 513, "MMH": 585, "N2H4": 653, "UDMH": 523, "NH3": 405
            }
            
            if prop['name'] in cp_table:
                insert_section("\n--- PROPRIÉTÉS THERMIQUES (table interne) ---")
                insert_line("Cp liquide      ", cp_table[prop['name']], "J/kg-K")
            if prop['name'] in hvap_table:
                insert_line("Hvap            ", hvap_table[prop['name']], "kJ/kg")
            if prop['name'] in t_crit_table:
                insert_line("T critique      ", t_crit_table[prop['name']], "K")
            
            insert_section("\n--- UTILISATION ---")
            self.db_details.insert(tk.END, f"CEA Fuel    : Tapez '", 'db_label')
            self.db_details.insert(tk.END, prop['name'], 'db_success')
            self.db_details.insert(tk.END, "' dans Carburant (CEA)\n", 'db_label')
            self.db_details.insert(tk.END, f"Coolant     : Tapez '", 'db_label')
            self.db_details.insert(tk.END, prop['name'], 'db_success')
            self.db_details.insert(tk.END, "' dans Coolant (Auto=fuel)\n", 'db_label')
        
        elif prop['type'] == 'Oxydant':
            from rocketcea.blends import oxCards, getOxRefTempDegK, getFloatTokenFromCards
            
            insert_section("--- CARTE NASA CEA ---")
            if prop['cards']:
                for card in prop['cards']:
                    self.db_details.insert(tk.END, f"{card}\n", 'db_string')
            
            insert_section("\n--- PROPRIÉTÉS EXTRAITES ---")
            try:
                cards = oxCards.get(prop['name'], [])
                rho = getFloatTokenFromCards(cards, 'rho')
                if rho:
                    insert_line("Densité (rho)   ", f"{rho:.4f}", f"g/cm³ ({rho*1000:.1f} kg/m³)")
            except Exception as e:
                self.db_details.insert(tk.END, f"Erreur extraction: {e}\n", 'db_label')
            
            insert_section("\n--- UTILISATION ---")
            self.db_details.insert(tk.END, f"CEA Oxydant : Tapez '", 'db_label')
            self.db_details.insert(tk.END, prop['name'], 'db_success')
            self.db_details.insert(tk.END, "' dans Oxydant (CEA)\n", 'db_label')
            self.db_details.insert(tk.END, "Coolant     : Peut être utilisé comme coolant (LOX cooling)\n", 'db_string')
        
        self.db_details.config(state='disabled')
    
    def copy_selected_name(self):
        """Copie le nom du propergol sélectionné dans le presse-papier"""
        selection = self.db_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Sélectionnez d'abord un propergol dans la liste")
            return
        
        item = self.db_tree.item(selection[0])
        name = item["values"][0]
        
        self.root.clipboard_clear()
        self.root.clipboard_append(name)
        messagebox.showinfo("Copié!", f"'{name}' copié dans le presse-papier")

    # ==========================================================================
    # LOGIQUE DE GÉOMÉTRIE (RAO)
    # ==========================================================================
    def calculate_geometry_profile(self, r):
        """Génère les tableaux de coordonnées X (mm), Y (mm)"""
        L_cyl = r['lc']
        Rc = r['rc']
        Rt = r['rt']
        
        # Longueur du convergent
        L_conv = (Rc - Rt) * 1.5
        
        # Chambre cylindrique
        X_ch = np.linspace(-(L_cyl + L_conv), -L_conv, 20)
        Y_ch = np.full_like(X_ch, Rc)
        
        # Convergent (courbe cosinus pour lisser)
        X_conv = np.linspace(-L_conv, 0, 30)
        t = (X_conv - (-L_conv)) / L_conv
        Y_conv = Rt + (Rc - Rt) * (1 - np.sin(np.pi * t / 2))
        
        # Divergent (courbe de Bézier quadratique)
        P0 = (0, Rt)
        P2 = (r['lb'], r['re'])
        tn = math.tan(math.radians(r['tn']))
        te = math.tan(math.radians(r['te']))
        
        # Point de contrôle P1
        denom = tn - te
        if abs(denom) < 1e-9:
            denom = 1e-9
        x_int = (r['re'] - r['rt'] - te * r['lb']) / denom
        P1 = (x_int, tn * x_int + r['rt'])
        
        # Courbe de Bézier
        t_vals = np.linspace(0, 1, 50)
        X_bell = (1-t_vals)**2 * P0[0] + 2*(1-t_vals)*t_vals * P1[0] + t_vals**2 * P2[0]
        Y_bell = (1-t_vals)**2 * P0[1] + 2*(1-t_vals)*t_vals * P1[1] + t_vals**2 * P2[1]
        
        # Fusion des profils
        X = np.concatenate([X_ch, X_conv[1:], X_bell[1:]])
        Y = np.concatenate([Y_ch, Y_conv[1:], Y_bell[1:]])
        
        return X, Y

    # ==========================================================================
    # CEA VALUE HELPER (SÉCURISÉ)
    # ==========================================================================
    def get_cea_value_safe(self, ispObj, pc_psi, mr, pe_psi, eps_override, pamb_psi, var_name, debug=False):
        """Récupère une valeur CEA de manière sécurisée"""
        try:
            # Calcul de eps
            if eps_override > 0:
                eps = eps_override
            else:
                if pe_psi <= 0:
                    return 0
                try:
                    eps = ispObj.get_eps_at_PcOvPe(Pc=pc_psi, MR=mr, PcOvPe=pc_psi/pe_psi)
                except:
                    eps = 1.0
            
            if debug:
                print(f"DEBUG: pc_psi={pc_psi}, mr={mr}, eps={eps}")
            
            # Données de base
            data = ispObj.get_IvacCstrTc_ChmMwGam(Pc=pc_psi, MR=mr, eps=eps)
            # data = [IspVac, Cstar, Tc, MW, Gamma]
            
            if data[1] == 0:
                return 0
            
            # ISP Ambiante
            isp_amb = 0
            if pamb_psi > 0:
                try:
                    isp_amb_data = ispObj.estimate_Ambient_Isp(Pc=pc_psi, MR=mr, eps=eps, Pamb=pamb_psi)
                    isp_amb = isp_amb_data[0] if isp_amb_data else 0
                except:
                    isp_amb = data[0]  # Fallback sur ISP vide
            else:
                isp_amb = data[0]
            
            # Températures détaillées
            try:
                temps = ispObj.get_Temperatures(Pc=pc_psi, MR=mr, eps=eps, frozen=0, frozenAtThroat=0)
                # temps en Rankine -> Kelvin
                tc_k = temps[0] / 1.8
                tt_k = temps[1] / 1.8
                te_k = temps[2] / 1.8
            except:
                tc_k = data[2] / 1.8
                tt_k = tc_k * 0.9
                te_k = tc_k * 0.6
            
            # Mapping
            results_map = {
                "ISP Ambiante (s)": isp_amb,
                "ISP Vide (s)": data[0],
                "Température Chambre (K)": tc_k,
                "Température Col (K)": tt_k,
                "Température Sortie (K)": te_k,
                "C* (m/s)": data[1] * 0.3048,
                "Gamma": data[4],
                "MW": data[3]
            }
            
            return results_map.get(var_name, 0)
            
        except Exception as e:
            if debug:
                print(f"DEBUG ERROR: {e}")
            return 0

    # ==========================================================================
    # SIMULATION PRINCIPALE
    # ==========================================================================
    def run_simulation(self):
        try:
            # Inputs
            ox = self.get_val("ox")
            fuel = self.get_val("fuel")
            pc = self.get_val("pc")
            mr = self.get_val("mr")
            cr = self.get_val("cr")
            pe_des = self.get_val("pe")
            mdot = self.get_val("mdot")
            pamb = self.get_val("pamb")
            lstar = self.get_val("lstar")
            t_wall_limit = self.get_val("twall")  # T paroi côté coolant (limite max)
            wall_thickness_mm = self.get_val("wall_thickness")  # Épaisseur paroi en mm
            wall_k = self.get_val("wall_k")  # Conductivité thermique W/m-K
            wall_thickness_m = wall_thickness_mm / 1000.0  # Convertir en mètres
            
            # Validations
            if pc <= 0:
                raise ValueError("Pression chambre doit être > 0")
            if pe_des <= 0:
                raise ValueError("Pression sortie doit être > 0")
            if pc <= pe_des:
                raise ValueError("Pression chambre doit être > Pression sortie")
            if mr <= 0:
                raise ValueError("Ratio O/F doit être > 0")
            if mdot <= 0:
                raise ValueError("Débit massique doit être > 0")
            if cr <= 1:
                raise ValueError("Contraction Ratio doit être > 1")
            
            pc_psi = pc * 14.5038
            pe_psi = pe_des * 14.5038
            pamb_psi = pamb * 14.5038
            
            # Init CEA
            try:
                ispObj = CEA_Obj(oxName=ox, fuelName=fuel)
            except Exception as e:
                raise ValueError(f"Ergols inconnus: {ox}/{fuel}\n{e}")
            
            # Calcul de eps
            try:
                eps = ispObj.get_eps_at_PcOvPe(Pc=pc_psi, MR=mr, PcOvPe=pc_psi/pe_psi)
            except:
                eps = 2.0  # Fallback
            
            # Performances
            cstar_mps = self.get_cea_value_safe(ispObj, pc_psi, mr, pe_psi, eps, pamb_psi, "C* (m/s)", debug=True)
            if cstar_mps <= 1:
                raise ValueError("C* nul. Vérifiez les ergols ou la pression.")
            
            isp_amb = self.get_cea_value_safe(ispObj, pc_psi, mr, pe_psi, eps, pamb_psi, "ISP Ambiante (s)")
            isp_vac = self.get_cea_value_safe(ispObj, pc_psi, mr, pe_psi, eps, pamb_psi, "ISP Vide (s)")
            tc_k = self.get_cea_value_safe(ispObj, pc_psi, mr, pe_psi, eps, pamb_psi, "Température Chambre (K)")
            tt_k = self.get_cea_value_safe(ispObj, pc_psi, mr, pe_psi, eps, pamb_psi, "Température Col (K)")
            te_k = self.get_cea_value_safe(ispObj, pc_psi, mr, pe_psi, eps, pamb_psi, "Température Sortie (K)")
            
            # Géométrie
            at_m2 = (mdot * cstar_mps) / (pc * 1e5)
            rt_m = math.sqrt(at_m2 / math.pi)
            rt_mm = rt_m * 1000
            
            dt = 2 * rt_mm
            de = 2 * math.sqrt(at_m2 * eps / math.pi) * 1000
            dc = 2 * math.sqrt(at_m2 * cr / math.pi) * 1000
            
            # Longueur chambre
            vc = lstar * at_m2
            ac = at_m2 * cr
            lc_m = vc / ac
            lc_m = min(lc_m, 0.4)  # Limite max 400mm
            lc = lc_m * 1000
            
            re = de / 2
            rt = dt / 2
            lb = 0.8 * ((re - rt) / math.tan(math.radians(15)))
            
            self.results = {
                "dt": dt, "de": de, "dc": dc, "lc": lc, "lb": lb,
                "rt": rt, "re": re, "rc": dc / 2,
                "tn": self.get_val("tn"), "te": self.get_val("te"),
                "isp": isp_amb, "eps": eps,
                "tc_k": tc_k, "tt_k": tt_k, "te_k": te_k,
                "cstar_mps": cstar_mps
            }
            
            # --- ANALYSE THERMIQUE (BARTZ) ---
            # Propriétés de transport au col
            try:
                transp = ispObj.get_Throat_Transport(Pc=pc_psi, MR=mr, eps=eps)
                # transp = [Cp, Mu, K, Pr]
                Cp_imp = transp[0]
                Mu_poise = transp[1] / 1000.0
                Pr = transp[3]
            except:
                # Valeurs par défaut approximatives
                Cp_imp = 0.5
                Mu_poise = 0.001
                Pr = 0.7
            
            # Conversion SI
            Mu_si = Mu_poise * 0.1  # Pa.s
            Cp_si = Cp_imp * 4186.8  # J/kg-K
            
            # Stocker les propriétés transportées pour l'analyse paramétrique
            self.results["Mu"] = Mu_si
            self.results["Cp"] = Cp_si
            self.results["Pr"] = Pr
            
            # Profil géométrique
            X_mm, Y_mm = self.calculate_geometry_profile(self.results)
            Y_m = Y_mm / 1000.0
            self.geometry_profile = (X_mm, Y_mm)
            
            # Bartz - Calcul du coefficient de transfert thermique
            Dt_m = dt / 1000.0
            rt_m = Dt_m / 2
            pc_pa = pc * 1e5
            
            # hg au col (formule Bartz simplifiée)
            term1 = 0.026 / (Dt_m ** 0.2)
            term2 = (Mu_si ** 0.2 * Cp_si) / (Pr ** 0.6)
            term3 = (pc_pa / cstar_mps) ** 0.8
            hg_throat = term1 * term2 * term3  # W/m²-K
            
            # Boucle sur le profil
            Flux_list = []
            T_gas_list = []
            T_wall_hot_list = []  # Température paroi côté gaz chaud
            
            for i, r_local in enumerate(Y_m):
                d_local = 2 * r_local
                
                # hg local (scaling avec le diamètre)
                if d_local > 0:
                    hg_local = hg_throat * ((Dt_m / d_local) ** 1.8)
                else:
                    hg_local = hg_throat
                
                # Température gaz locale (interpolation)
                x_pos = X_mm[i]
                if x_pos <= -self.results['lc']:
                    # Chambre
                    t_gas = tc_k
                elif x_pos <= 0:
                    # Convergent: interpolation Tc -> Tt
                    ratio = (x_pos + self.results['lc']) / self.results['lc']
                    t_gas = tc_k - ratio * (tc_k - tt_k)
                else:
                    # Divergent: interpolation Tt -> Te
                    ratio = x_pos / self.results['lb'] if self.results['lb'] > 0 else 0
                    ratio = min(ratio, 1.0)
                    t_gas = tt_k - ratio * (tt_k - te_k)
                
                T_gas_list.append(t_gas)
                
                # === CALCUL THERMIQUE AVEC CONDUCTION DANS LA PAROI ===
                # Équilibre thermique: q = hg*(Tgas - Twall_hot) = k/e*(Twall_hot - Twall_cold)
                # On résout pour Twall_hot:
                # q = hg * (Tgas - Twall_hot)
                # q = (k/e) * (Twall_hot - Twall_cold)
                # => hg * Tgas - hg * Twall_hot = (k/e) * Twall_hot - (k/e) * Twall_cold
                # => hg * Tgas + (k/e) * Twall_cold = Twall_hot * (hg + k/e)
                # => Twall_hot = (hg * Tgas + (k/e) * Twall_cold) / (hg + k/e)
                
                if wall_k > 0 and wall_thickness_m > 0:
                    k_over_e = wall_k / wall_thickness_m  # Conductance de la paroi W/m²-K
                    t_wall_hot = (hg_local * t_gas + k_over_e * t_wall_limit) / (hg_local + k_over_e)
                else:
                    # Pas de résistance thermique -> T_wall_hot = T_wall_cold
                    t_wall_hot = t_wall_limit
                
                T_wall_hot_list.append(t_wall_hot)
                
                # Flux thermique basé sur T_wall_hot réel
                q = hg_local * (t_gas - t_wall_hot)
                Flux_list.append(q / 1e6)  # MW/m²
            
            # --- CALCULS STATISTIQUES ---
            q_max = max(Flux_list) if Flux_list else 0
            q_min = min(Flux_list) if Flux_list else 0
            q_mean = np.mean(Flux_list) if Flux_list else 0
            idx_max = Flux_list.index(q_max) if Flux_list else 0
            x_max = X_mm[idx_max]
            
            t_gas_max = max(T_gas_list) if T_gas_list else 0
            t_gas_mean = np.mean(T_gas_list) if T_gas_list else 0
            t_wall_hot_max = max(T_wall_hot_list) if T_wall_hot_list else 0
            t_wall_hot_mean = np.mean(T_wall_hot_list) if T_wall_hot_list else 0
            
            # --- CALCUL PUISSANCE THERMIQUE TOTALE ---
            # Intégration du flux sur la surface (approximation trapèze)
            # dA = 2 * pi * r * dL (surface latérale d'un cône)
            Q_total_W = 0
            for i in range(len(X_mm) - 1):
                r_avg = (Y_m[i] + Y_m[i+1]) / 2  # rayon moyen en m
                dL = abs(X_mm[i+1] - X_mm[i]) / 1000  # longueur en m
                dA = 2 * np.pi * r_avg * dL  # surface élémentaire
                q_avg = (Flux_list[i] + Flux_list[i+1]) / 2 * 1e6  # flux moyen en W/m²
                Q_total_W += q_avg * dA
            
            Q_total_kW = Q_total_W / 1000
            
            # Stocker les résultats thermiques pour l'accès depuis le solveur coolant
            self.results["Q_total_kW"] = Q_total_kW
            self.results["q_max"] = q_max  # MW/m²
            self.results["q_mean"] = q_mean  # MW/m²
            self.results["t_wall_hot_max"] = t_wall_hot_max
            self.results["wall_thickness_mm"] = wall_thickness_m * 1000
            self.results["fuel"] = fuel
            self.results["A_cooled"] = sum([2 * np.pi * (Y_m[i] + Y_m[i+1]) / 2 * abs(X_mm[i+1] - X_mm[i]) / 1000 for i in range(len(X_mm) - 1)])
            
            # Stocker les données du profil thermique pour le graphique du solveur
            self.results["thermal_profile"] = {
                "X_mm": list(X_mm),
                "Y_mm": list(Y_mm),
                "Flux_MW": Flux_list,
                "T_gas": T_gas_list,
                "T_wall_hot": T_wall_hot_list,
                "T_wall_cold": t_wall_limit,
                "hg_throat": hg_throat,
            }
            
            # --- PROPRIÉTÉS DU COOLANT (via RocketCEA ou Custom) ---
            # Option: utiliser le fuel, un autre propergol, ou un coolant custom
            coolant_choice = self.get_val("coolant_name").strip()
            coolant_mdot_str = self.get_val("coolant_mdot") if isinstance(self.get_val("coolant_mdot"), str) else str(self.get_val("coolant_mdot"))
            coolant_tin = self.get_val("coolant_tin")
            coolant_tout = self.get_val("coolant_tout")
            coolant_margin = self.get_val("coolant_margin") / 100.0  # En fraction
            
            # Déterminer quel coolant utiliser
            if coolant_choice.upper() == "AUTO" or coolant_choice == "":
                coolant_source = fuel  # Utiliser le fuel comme coolant
                use_fuel_as_coolant = True
            else:
                coolant_source = coolant_choice
                use_fuel_as_coolant = False
            
            # === TABLE DES COOLANTS COMMUNS (non-propergols) ===
            # Inclut l'eau, glycols, huiles thermiques, etc.
            common_coolants = {
                # Eau et solutions aqueuses
                "H2O": {"name": "Eau", "cp": 4186, "t_boil": 373, "t_crit": 647, "hvap": 2260, "M": 18},
                "WATER": {"name": "Eau", "cp": 4186, "t_boil": 373, "t_crit": 647, "hvap": 2260, "M": 18},
                "EAU": {"name": "Eau", "cp": 4186, "t_boil": 373, "t_crit": 647, "hvap": 2260, "M": 18},
                # Glycols
                "EG": {"name": "Ethylène Glycol", "cp": 2400, "t_boil": 470, "t_crit": 645, "hvap": 800, "M": 62},
                "ETHYLENE_GLYCOL": {"name": "Ethylène Glycol", "cp": 2400, "t_boil": 470, "t_crit": 645, "hvap": 800, "M": 62},
                "PG": {"name": "Propylène Glycol", "cp": 2500, "t_boil": 461, "t_crit": 626, "hvap": 750, "M": 76},
                # Huiles thermiques
                "DOWTHERM": {"name": "Dowtherm A", "cp": 1800, "t_boil": 530, "t_crit": 770, "hvap": 300, "M": 166},
                "THERMINOL": {"name": "Therminol 66", "cp": 1900, "t_boil": 632, "t_crit": 800, "hvap": 250, "M": 250},
                # Azote liquide
                "LN2": {"name": "Azote Liquide", "cp": 2040, "t_boil": 77, "t_crit": 126, "hvap": 199, "M": 28},
                "N2": {"name": "Azote Liquide", "cp": 2040, "t_boil": 77, "t_crit": 126, "hvap": 199, "M": 28},
                # Oxygène liquide (comme coolant)
                "LOX": {"name": "Oxygène Liquide", "cp": 1700, "t_boil": 90, "t_crit": 155, "hvap": 213, "M": 32},
                "O2": {"name": "Oxygène Liquide", "cp": 1700, "t_boil": 90, "t_crit": 155, "hvap": 213, "M": 32},
            }
            
            # Fonction pour récupérer les propriétés du carburant depuis RocketCEA
            def get_fuel_properties_from_cea(fuel_name):
                """Récupère T_ébullition et densité depuis RocketCEA blends"""
                from rocketcea.blends import fuelCards, getFuelRefTempDegK, getFloatTokenFromCards
                
                # Table des Cp liquides (J/kg-K) - CEA ne fournit pas le Cp liquide
                # Valeurs physiques standard à température proche du point d'ébullition
                cp_table = {
                    "C3H8": 2500, "Propane": 2500,
                    "CH4": 3500, "LCH4_NASA": 3500, "GCH4": 3500,
                    "C2H5OH": 2440, "Ethanol": 2440,
                    "CH3OH": 2500, "Methanol": 2500,
                    "RP1": 2000, "RP_1": 2000, "RP1_NASA": 2000, "Kerosene": 2000, "JetA": 2000,
                    "H2": 14300, "LH2": 14300, "LH2_NASA": 14300, "GH2": 14300, "GH2_160": 14300,
                    "MMH": 2900, "N2H4": 3100, "UDMH": 2700, "NH3": 4700,
                    "A50": 3000, "MHF3": 2900, "M20": 3050, "M20_NH3": 3050,
                }
                
                # Températures critiques (K)
                t_crit_table = {
                    "C3H8": 370, "Propane": 370,
                    "CH4": 191, "LCH4_NASA": 191, "GCH4": 191,
                    "C2H5OH": 514, "Ethanol": 514,
                    "CH3OH": 513, "Methanol": 513,
                    "RP1": 678, "RP_1": 678, "RP1_NASA": 678, "Kerosene": 678, "JetA": 678,
                    "H2": 33, "LH2": 33, "LH2_NASA": 33, "GH2": 33, "GH2_160": 33,
                    "MMH": 585, "N2H4": 653, "UDMH": 523, "NH3": 405,
                    "A50": 600, "MHF3": 585, "M20": 600, "M20_NH3": 600,
                }
                
                # Densités de secours (kg/m³) pour les carburants sans rho dans CEA
                rho_fallback = {
                    "LH2": 70.8, "LH2_NASA": 70.8, "H2": 70.8,
                    "C2H5OH": 789, "Ethanol": 789,
                    "CH3OH": 792, "Methanol": 792,
                    "GH2": 1.3, "GH2_160": 10,  # Gaz sous pression
                    "GCH4": 1.8,
                }
                
                # Mapping des noms alternatifs vers les noms CEA
                name_mapping = {
                    "RP-1": "RP1", "RP 1": "RP1", "KEROSENE": "Kerosene",
                    "METHANE": "CH4", "LCH4": "LCH4_NASA",
                    "HYDROGEN": "LH2", "HYDROGENE": "LH2",
                    "PROPANE": "C3H8", "ETHANOL": "C2H5OH", "METHANOL": "CH3OH",
                }
                
                # Normaliser le nom du fuel
                fuel_upper = fuel_name.upper().replace("-", "").replace(" ", "")
                
                # D'abord chercher dans le mapping
                cea_fuel_name = name_mapping.get(fuel_upper, None)
                
                # Puis chercher correspondance exacte dans fuelCards
                if cea_fuel_name is None:
                    for key in fuelCards.keys():
                        key_norm = key.upper().replace("-", "").replace("_", "")
                        if key_norm == fuel_upper or key.upper() == fuel_name.upper():
                            cea_fuel_name = key
                            break
                
                # Chercher correspondance partielle (moins prioritaire)
                if cea_fuel_name is None:
                    for key in fuelCards.keys():
                        key_norm = key.upper().replace("-", "").replace("_", "")
                        if fuel_upper in key_norm and len(fuel_upper) >= 3:
                            cea_fuel_name = key
                            break
                
                if cea_fuel_name is None:
                    return None, f"⚠ Carburant {fuel_name} non trouvé dans RocketCEA"
                
                # Récupérer Tref depuis RocketCEA (= T ébullition pour liquides)
                try:
                    t_boil = getFuelRefTempDegK(cea_fuel_name)
                except:
                    t_boil = 298  # Par défaut
                
                # Récupérer densité depuis RocketCEA
                try:
                    cards = fuelCards.get(cea_fuel_name, [])
                    rho = getFloatTokenFromCards(cards, 'rho')
                    if rho is None or rho == 0:
                        rho = rho_fallback.get(cea_fuel_name, 800) / 1000  # En g/cm³
                except:
                    rho = rho_fallback.get(cea_fuel_name, 800) / 1000
                
                # Cp depuis table (CEA ne fournit pas le Cp liquide)
                cp = cp_table.get(cea_fuel_name, 2500)
                
                # T critique depuis table
                t_crit = t_crit_table.get(cea_fuel_name, t_boil + 150)
                
                return {
                    "name": cea_fuel_name,
                    "cp": cp,
                    "t_boil": t_boil,
                    "t_crit": t_crit,
                    "rho": rho * 1000,  # Convertir g/cm³ en kg/m³
                }, None
            
            # Récupérer les propriétés du coolant
            coolant_warning = ""
            coolant_hvap = 400  # Par défaut
            coolant_M = 50  # Masse molaire par défaut
            
            if coolant_source.upper() == "CUSTOM":
                # Utiliser les valeurs custom définies par l'utilisateur
                fuel_props = {
                    "name": "Custom",
                    "cp": self.get_val("custom_cp"),
                    "t_boil": self.get_val("custom_tboil"),
                    "t_crit": self.get_val("custom_tcrit"),
                    "rho": 800,
                }
                coolant_hvap = self.get_val("custom_hvap")
                coolant_M = 50
                coolant_warning = "ℹ Coolant custom défini par l'utilisateur"
            
            elif coolant_source.upper() in common_coolants:
                # Utiliser la table des coolants communs
                cc = common_coolants[coolant_source.upper()]
                fuel_props = {
                    "name": cc["name"],
                    "cp": cc["cp"],
                    "t_boil": cc["t_boil"],
                    "t_crit": cc["t_crit"],
                    "rho": 1000,
                }
                coolant_hvap = cc["hvap"]
                coolant_M = cc["M"]
                coolant_warning = f"ℹ Coolant: {cc['name']}"
            
            else:
                # Récupérer depuis RocketCEA (propergols)
                fuel_props, cea_warning = get_fuel_properties_from_cea(coolant_source)
                
                if fuel_props is None:
                    fuel_props = {"cp": 2500, "name": coolant_source, "t_boil": 350, "t_crit": 500, "rho": 800}
                    coolant_warning = f"⚠ Propriétés de {coolant_source} estimées (non trouvé)"
                elif cea_warning:
                    coolant_warning = cea_warning
            
            coolant_cp = fuel_props["cp"]
            coolant_t_boil_1bar = fuel_props["t_boil"]  # T ébullition à 1 bar (donnée CEA)
            coolant_t_crit = fuel_props["t_crit"]
            coolant_name_display = fuel_props["name"]
            coolant_pressure = self.get_val("coolant_pressure")  # bar
            
            # === CORRECTION T_BOIL PAR PRESSION (Clausius-Clapeyron) ===
            # ln(P2/P1) = (Hvap/R) * (1/T1 - 1/T2)
            # => T2 = 1 / (1/T1 - R*ln(P2/P1)/Hvap)
            # Hvap en J/mol, R = 8.314 J/mol-K
            
            # Si pas déjà défini par common_coolants, utiliser les tables propergols
            if coolant_source.upper() not in common_coolants and coolant_source.upper() != "CUSTOM":
                # Enthalpies de vaporisation typiques (kJ/kg) pour les propergols
                hvap_table = {
                    "C3H8": 426, "Propane": 426,
                    "CH4": 510, "LCH4_NASA": 510,
                    "LH2": 446, "LH2_NASA": 446, "H2": 446,
                    "C2H5OH": 841, "Ethanol": 841,
                    "CH3OH": 1100, "Methanol": 1100,
                    "RP1": 290, "RP_1": 290, "Kerosene": 290,
                    "N2H4": 1220, "MMH": 800, "UDMH": 540,
                    "NH3": 1370,
                }
                # Masses molaires (g/mol)
                molar_mass_table = {
                    "C3H8": 44.1, "Propane": 44.1,
                    "CH4": 16.04, "LCH4_NASA": 16.04,
                    "LH2": 2.016, "LH2_NASA": 2.016, "H2": 2.016,
                    "C2H5OH": 46.07, "Ethanol": 46.07,
                    "CH3OH": 32.04, "Methanol": 32.04,
                    "RP1": 170, "RP_1": 170, "Kerosene": 170,
                    "N2H4": 32.05, "MMH": 46.07, "UDMH": 60.1,
                    "NH3": 17.03,
                }
                coolant_hvap = hvap_table.get(coolant_name_display, 400)
                coolant_M = molar_mass_table.get(coolant_name_display, 50)
            
            # Convertir Hvap en J/mol
            hvap_J_mol = coolant_hvap * coolant_M  # kJ/kg * g/mol = J/mol
            R = 8.314  # J/mol-K
            
            # Calculer T_boil à la pression du circuit
            P1 = 1.0  # bar (pression de référence)
            P2 = coolant_pressure  # bar
            T1 = coolant_t_boil_1bar  # K
            
            if P2 > 0 and T1 > 0 and hvap_J_mol > 0:
                try:
                    # Clausius-Clapeyron : T2 = 1 / (1/T1 - R*ln(P2/P1)/Hvap)
                    inv_T2 = (1/T1) - (R * math.log(P2/P1)) / hvap_J_mol
                    if inv_T2 > 0:
                        coolant_t_boil = 1 / inv_T2
                    else:
                        coolant_t_boil = coolant_t_crit  # Au-dessus du point critique
                except:
                    coolant_t_boil = coolant_t_boil_1bar
            else:
                coolant_t_boil = coolant_t_boil_1bar
            
            # Limiter à T_critique (au-delà, c'est un fluide supercritique)
            if coolant_t_boil >= coolant_t_crit:
                coolant_t_boil = coolant_t_crit - 10
                coolant_warning += f"\n⚠ Proche du point critique! T_boil limitée"
            
            # === VALIDATION DES TEMPÉRATURES ===
            # T_entrée doit être < T_ébullition (sinon le coolant est déjà gazeux!)
            if coolant_tin >= coolant_t_boil:
                coolant_warning += f"\n⚠ T entrée ({coolant_tin:.0f}K) >= T ébullition ({coolant_t_boil:.0f}K)!"
                coolant_warning += f"\n   → Réduire T entrée sous {coolant_t_boil - 10:.0f}K"
            
            # T_sortie doit être < T_ébullition (marge de sécurité)
            if coolant_tout > coolant_t_boil - 10:
                coolant_tout_orig = coolant_tout
                coolant_tout = coolant_t_boil - 20  # Marge de 20K avant ébullition
                coolant_warning += f"\n⚠ T sortie limitée: {coolant_tout_orig:.0f}K → {coolant_tout:.0f}K (avant ébullition)"
            
            # Calcul du ΔT (doit être positif : sortie > entrée)
            delta_T_coolant = coolant_tout - coolant_tin
            
            if delta_T_coolant <= 0:
                coolant_warning += f"\n❌ ΔT négatif! T_sortie ({coolant_tout:.0f}K) <= T_entrée ({coolant_tin:.0f}K)"
                coolant_warning += f"\n   → Augmenter T_sortie ou réduire T_entrée"
            
            # --- CALCUL DÉBIT COOLANT NÉCESSAIRE ---
            if delta_T_coolant > 0 and coolant_cp > 0:
                # Q = m_dot * Cp * dT  =>  m_dot = Q / (Cp * dT)
                mdot_coolant_needed = Q_total_W / (coolant_cp * delta_T_coolant)
                # Ajouter la marge de sécurité
                mdot_coolant_with_margin = mdot_coolant_needed * (1 + coolant_margin)
            else:
                mdot_coolant_needed = 0
                mdot_coolant_with_margin = 0
            
            # --- CALCUL DÉBIT DISPONIBLE ---
            # Débit fuel = Débit total / (1 + O/F)
            mdot_fuel_available = mdot / (1 + mr)
            mdot_ox_available = mdot - mdot_fuel_available
            
            # Déterminer le débit coolant disponible
            if coolant_mdot_str.strip().upper() == "AUTO":
                if use_fuel_as_coolant:
                    # Mode régénératif: le fuel passe dans les canaux
                    mdot_coolant_available = mdot_fuel_available
                    coolant_source_info = "(régen fuel)"
                else:
                    # Coolant externe avec débit non spécifié -> illimité
                    mdot_coolant_available = float('inf')
                    coolant_source_info = "(externe, débit illimité)"
            else:
                # Débit spécifié manuellement
                try:
                    mdot_coolant_available = float(coolant_mdot_str)
                    coolant_source_info = f"(spécifié: {mdot_coolant_available:.4f} kg/s)"
                except:
                    mdot_coolant_available = mdot_fuel_available
                    coolant_source_info = "(fallback fuel)"
            
            # --- VÉRIFICATION REFROIDISSEMENT ---
            if mdot_coolant_with_margin > 0:
                if mdot_coolant_available == float('inf'):
                    cooling_ratio = float('inf')
                else:
                    cooling_ratio = mdot_coolant_available / mdot_coolant_with_margin
            else:
                cooling_ratio = float('inf')
            
            cooling_ok = cooling_ratio >= 1.0
            
            if mdot_coolant_available == float('inf'):
                cooling_status = "✅ REFROIDISSEMENT OK (externe)"
                cooling_detail = f"Débit externe illimité"
                cooling_ratio_display = "∞"
            elif cooling_ok:
                cooling_status = "✅ REFROIDISSEMENT OK"
                cooling_excess = (cooling_ratio - 1) * 100
                cooling_detail = f"Excès de débit: +{cooling_excess:.1f}%"
                cooling_ratio_display = f"{cooling_ratio:.2f}x"
            else:
                cooling_status = "❌ REFROIDISSEMENT INSUFFISANT"
                cooling_deficit = (1 - cooling_ratio) * 100
                cooling_detail = f"Déficit de débit: -{cooling_deficit:.1f}%"
                cooling_ratio_display = f"{cooling_ratio:.2f}x"
            
            # Stocker pour le summary
            self.thermal_results = {
                "q_max": q_max, "q_min": q_min, "q_mean": q_mean,
                "x_max": x_max, "Q_total_kW": Q_total_kW,
                "mdot_coolant_needed": mdot_coolant_needed,
                "mdot_coolant_with_margin": mdot_coolant_with_margin,
                "mdot_fuel_available": mdot_fuel_available,
                "cooling_ok": cooling_ok, "cooling_ratio": cooling_ratio,
                "hg_throat": hg_throat, "coolant_cp": coolant_cp,
                "t_wall_hot_max": t_wall_hot_max, "t_wall_hot_mean": t_wall_hot_mean,
                "wall_thickness_mm": wall_thickness_mm, "wall_k": wall_k,
            }
            
            # Ajouter Q_total_kW à self.results aussi pour l'accés depuis les paramétrique
            self.results["Q_total_kW"] = Q_total_kW
            
            # --- PLOTS ---
            # Nettoyer complètement les axes
            for ax in [self.ax_flux, self.ax_temp]:
                ax.clear()
                ax.set_facecolor(self.bg_surface)
            self.apply_dark_axes([self.ax_flux, self.ax_temp])
            
            # Graphe Flux avec projections
            self.ax_flux.plot(X_mm, Flux_list, 'r-', linewidth=2, label='Flux thermique')
            self.ax_flux.set_ylabel("Flux (MW/m²)", color='r')
            self.ax_flux.set_title("Profil de Flux Thermique (Bartz)")
            self.ax_flux.grid(True, color=self.grid_color, alpha=0.35)
            
            # Ligne moyenne
            self.ax_flux.axhline(q_mean, color='green', linestyle='-.', linewidth=1.5, 
                                label=f'Moyenne: {q_mean:.2f} MW/m²')
            
            # Point max avec PROJECTIONS sur les axes
            self.ax_flux.plot(x_max, q_max, 'ro', markersize=10, zorder=5)
            
            # Projection verticale (vers l'axe X)
            self.ax_flux.plot([x_max, x_max], [0, q_max], 'r--', linewidth=1, alpha=0.7)
            # Projection horizontale (vers l'axe Y)
            xlim = self.ax_flux.get_xlim() if self.ax_flux.get_xlim()[0] != 0 else (min(X_mm), max(X_mm))
            self.ax_flux.plot([xlim[0], x_max], [q_max, q_max], 'r--', linewidth=1, alpha=0.7)
            
            # Annotations sur les axes
            self.ax_flux.annotate(f'{x_max:.1f} mm', (x_max, 0), 
                                 xytext=(0, -20), textcoords='offset points',
                                 ha='center', color='red', fontsize=9, fontweight='bold')
            self.ax_flux.annotate(f'{q_max:.2f}', (xlim[0], q_max),
                                 xytext=(-5, 0), textcoords='offset points',
                                 ha='right', va='center', color='red', fontsize=9, fontweight='bold')
            
            # Texte Max au point
            self.ax_flux.annotate(f'MAX', (x_max, q_max),
                                 xytext=(10, 10), textcoords='offset points',
                                 color='darkred', fontsize=10, fontweight='bold')
            
            self.ax_flux.legend(loc='upper right', fontsize=8, facecolor=self.bg_surface, edgecolor=self.accent)
            self.ax_flux.axhline(0, color=self.grid_color, linestyle='-', alpha=0.4)
            
            # Graphe Température avec projections
            self.ax_temp.plot(X_mm, T_gas_list, 'orange', linewidth=2, label="T gaz (adiabatique)")
            self.ax_temp.plot(X_mm, T_wall_hot_list, 'red', linewidth=2, label=f"T paroi hot ({t_wall_hot_max:.0f} K max)")
            self.ax_temp.axhline(t_wall_limit, color='blue', linestyle='--', linewidth=2, 
                                label=f"T paroi cold ({t_wall_limit:.0f} K)")
            
            # Moyenne température gaz
            self.ax_temp.axhline(t_gas_mean, color='darkorange', linestyle='-.', linewidth=1.5,
                                label=f'T moy gaz: {t_gas_mean:.0f} K')
            
            # Remplissage entre T_wall_hot et T_wall_cold pour visualiser le gradient
            self.ax_temp.fill_between(X_mm, T_wall_hot_list, [t_wall_limit]*len(X_mm),
                                     color='red', alpha=0.15, label=f"ΔT paroi (e={wall_thickness_mm:.1f}mm, k={wall_k:.0f})")
            
            # Point max température paroi hot
            idx_twall_max = T_wall_hot_list.index(t_wall_hot_max)
            x_twall_max = X_mm[idx_twall_max]
            self.ax_temp.plot(x_twall_max, t_wall_hot_max, 's', color='darkred', markersize=8)
            
            # Point max température avec projections
            idx_tmax = T_gas_list.index(t_gas_max)
            x_tmax = X_mm[idx_tmax]
            self.ax_temp.plot(x_tmax, t_gas_max, 'o', color='darkorange', markersize=8)
            self.ax_temp.plot([x_tmax, x_tmax], [t_wall_limit, t_gas_max], '--', color='darkorange', alpha=0.7)
            
            self.ax_temp.set_ylabel("Température (K)")
            self.ax_temp.set_xlabel("Position Axiale (mm)")
            self.ax_temp.legend(loc='upper right', fontsize=8, facecolor=self.bg_surface, edgecolor=self.accent)
            self.ax_temp.grid(True, color=self.grid_color, alpha=0.35)
            
            # Forcer le rafraîchissement complet de la figure
            self.fig_thermal.subplots_adjust(hspace=0.35, left=0.12, right=0.95, top=0.95, bottom=0.1)
            self.canvas_thermal.draw()
            
            # Géométrie 2D
            self.draw_engine(X_mm, Y_mm)
            
            # --- SUMMARY ---
            thrust_n = mdot * isp_amb * 9.81
            thrust_kn = thrust_n / 1000  # Convertir en kN
            
            summary = f"""═══════════════════════════════════
    SITH MISCHUNG COMBUSTION : LIGHT SIDE EDITION v6.2
═══════════════════════════════════

--- THERMIQUE (BARTZ) ---
Flux Max        : {q_max:.2f} MW/m² @ x={x_max:.1f}mm
Flux Moyen      : {q_mean:.2f} MW/m²
Flux Min        : {q_min:.2f} MW/m²
hg au Col       : {hg_throat:.0f} W/m²-K

Puissance Therm.: {Q_total_kW:.1f} kW

--- REFROIDISSEMENT RÉGÉNÉRATIF ---
Coolant         : {coolant_name_display} ({coolant_source})
Source          : {coolant_source_info}
Cp              : {coolant_cp:.0f} J/kg-K
Pression circuit: {coolant_pressure:.1f} bar
T ébull. @1bar  : {coolant_t_boil_1bar:.0f} K
T ébull. @{coolant_pressure:.0f}bar : {coolant_t_boil:.0f} K
T critique      : {coolant_t_crit:.0f} K
T entrée        : {coolant_tin:.0f} K
T sortie        : {coolant_tout:.0f} K
ΔT Coolant      : {delta_T_coolant:.0f} K

Débit nécessaire: {mdot_coolant_needed:.4f} kg/s
Avec marge {coolant_margin*100:.0f}% : {mdot_coolant_with_margin:.4f} kg/s
Débit dispo     : {mdot_coolant_available if mdot_coolant_available != float('inf') else '∞'} kg/s

{cooling_status}
{cooling_detail}
Ratio débit     : {cooling_ratio_display}
{coolant_warning}

--- PAROI & TEMPÉRATURES ---
Épaisseur paroi : {wall_thickness_mm:.1f} mm
Conductivité k  : {wall_k:.0f} W/m-K
T Gaz Chambre   : {tc_k:.0f} K
T Gaz Col       : {tt_k:.0f} K  
T Gaz Sortie    : {te_k:.0f} K
T Paroi Cold    : {t_wall_limit:.0f} K (côté coolant)
T Paroi Hot Max : {t_wall_hot_max:.0f} K (côté gaz)
ΔT Paroi Max    : {t_wall_hot_max - t_wall_limit:.0f} K

--- PERFORMANCES ---
ISP Sol ({pamb} bar): {isp_amb:.1f} s
ISP Vide        : {isp_vac:.1f} s
Poussée         : {thrust_kn:.3f} kN ({thrust_n:.0f} N)
C*              : {cstar_mps:.0f} m/s

--- GÉOMÉTRIE ---
Ø Col    : {dt:.2f} mm
Ø Sortie : {de:.2f} mm (ε={eps:.2f})
Ø Chambre: {dc:.2f} mm
L Chambre: {lc:.1f} mm
L Bell   : {lb:.1f} mm

--- DÉBITS ---
Débit Total     : {mdot:.4f} kg/s
Débit Fuel      : {mdot_fuel_available:.4f} kg/s
Débit Oxydant   : {mdot_ox_available:.4f} kg/s
"""
            self.txt_summary.delete(1.0, tk.END)
            self.insert_colored_summary(summary, cooling_status, coolant_warning)
            
            # Raw CEA output avec coloration
            try:
                raw = ispObj.get_full_cea_output(Pc=pc_psi, MR=mr, eps=eps, pc_units='bar', output='calories')
                self.txt_cea.config(state='normal')
                self.txt_cea.delete(1.0, tk.END)
                self.insert_colored_cea(raw)
                self.txt_cea.config(state='disabled')
            except:
                pass
            
            self.tabs.select(self.tab_summary)
            
        except Exception as e:
            messagebox.showerror("Erreur Prometheus", str(e))

    # ==========================================================================
    # DESSIN 2D
    # ==========================================================================
    def draw_engine(self, X, Y):
        self.ax_visu.clear()
        self.ax_visu.set_facecolor(self.bg_surface)
        self.apply_dark_axes(self.ax_visu)
        self.ax_visu.plot(X, Y, color=self.accent, linewidth=2)
        self.ax_visu.plot(X, -Y, color=self.accent, linewidth=2)
        self.ax_visu.fill_between(X, Y, -Y, color=self.accent, alpha=0.12)
        self.ax_visu.set_aspect('equal')
        self.ax_visu.set_title(f"Géométrie Moteur - {self.get_val('name')}")
        self.ax_visu.set_xlabel("Position axiale (mm)")
        self.ax_visu.set_ylabel("Rayon (mm)")
        self.ax_visu.grid(True, color=self.grid_color, alpha=0.35)
        self.ax_visu.axvline(0, color=self.accent_alt, linestyle='--', alpha=0.7, label='Col')
        self.ax_visu.legend(facecolor=self.bg_surface, edgecolor=self.accent)
        self.canvas_visu.draw()

    # ==========================================================================
    # EXPORT DXF
    # ==========================================================================
    def export_dxf(self):
        if not self.results or not self.geometry_profile:
            messagebox.showwarning("Attention", "Lancez d'abord une simulation!")
            return
        
        if not HAS_EZDXF:
            messagebox.showwarning("Attention", "Module ezdxf non installé.\nInstallez-le avec: pip install ezdxf")
            return
        
        f = filedialog.asksaveasfilename(defaultextension=".dxf", filetypes=[("DXF files", "*.dxf")])
        if f:
            try:
                doc = ezdxf.new()
                msp = doc.modelspace()
                
                X, Y = self.geometry_profile
                points_top = list(zip(X, Y))
                points_bottom = list(zip(X, -Y))
                
                msp.add_lwpolyline(points_top)
                msp.add_lwpolyline(points_bottom)
                
                doc.saveas(f)
                messagebox.showinfo("Succès", f"Fichier sauvegardé:\n{f}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{e}")

    def save_design(self):
        """Sauvegarder les paramètres de conception dans un fichier JSON"""
        f = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if not f:
            return
        
        try:
            # Récupérer tous les paramètres depuis les inputs
            design_data = {}
            for key, (var, type_) in self.inputs.items():
                design_data[key] = var.get()
            
            # Ajouter les résultats si disponibles
            design_data["_results"] = self.results
            design_data["_timestamp"] = datetime.now().isoformat()
            
            with open(f, 'w', encoding='utf-8') as fp:
                json.dump(design_data, fp, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Succès", f"Paramètres sauvegardés:\n{f}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{e}")

    def load_design(self):
        """Charger les paramètres de conception depuis un fichier JSON"""
        f = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not f:
            return
        
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                design_data = json.load(fp)
            
            # Charger les paramètres dans les inputs
            for key, (var, type_) in self.inputs.items():
                if key in design_data:
                    value = design_data[key]
                    try:
                        # Convertir en type approprié
                        var.set(type_(value))
                    except:
                        var.set(value)
            
            # Charger les résultats si disponibles
            if "_results" in design_data:
                self.results = design_data["_results"]
            
            messagebox.showinfo("Succès", f"Paramètres chargés:\n{f}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement:\n{e}")

    def export_graphs_hd(self):
        """Exporter les graphes actuels en haute résolution (PNG + PDF)"""
        if not hasattr(self, 'fig_graph') or not self.fig_graph.get_axes():
            messagebox.showwarning("Attention", "Aucun graphe à exporter. Lancez d'abord une analyse!")
            return
        
        # Demander le dossier de destination
        folder = filedialog.askdirectory(title="Sélectionner le dossier d'export")
        if not folder:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Récupérer le titre du graphe pour le nom de fichier
            title = self.fig_graph.get_axes()[0].get_title()
            # Nettoyer tous les caractères invalides pour un nom de fichier
            title = title.replace(" ", "_").replace(":", "").replace("?", "").replace("/", "_").replace("\\", "_").replace("(", "").replace(")", "").replace("[", "").replace("]", "")[:40] if title else "graph"
            
            # Créer un dossier avec timestamp pour les trois fichiers
            export_folder = os.path.join(folder, f"{title}_{timestamp}")
            os.makedirs(export_folder, exist_ok=True)
            
            # Export en PNG (haute résolution)
            png_file = os.path.join(export_folder, f"{title}.png")
            self.fig_graph.savefig(png_file, dpi=300, bbox_inches='tight', facecolor=self.bg_main)
            
            # Export en PDF (vecteur)
            pdf_file = os.path.join(export_folder, f"{title}.pdf")
            self.fig_graph.savefig(pdf_file, format='pdf', bbox_inches='tight', facecolor=self.bg_main)
            
            # Export en SVG (vecteur)
            svg_file = os.path.join(export_folder, f"{title}.svg")
            self.fig_graph.savefig(svg_file, format='svg', bbox_inches='tight', facecolor=self.bg_main)
            
            messagebox.showinfo("Succès", 
                f"Graphes exportés en haute résolution dans:\n"
                f"{export_folder}\n\n"
                f"Fichiers créés:\n"
                f"✓ {title}.png (300 DPI)\n"
                f"✓ {title}.pdf (Vecteur)\n"
                f"✓ {title}.svg (Vecteur)")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{e}")

    # ==========================================================================
    # ANALYSES PARAMÉTRIQUES
    # ==========================================================================
    
    def update_analysis_options(self, event=None):
        """Met à jour les options de X et Y selon la catégorie sélectionnée"""
        category = self.combo_category.get()
        
        # Mettre à jour les listes
        self.input_vars = self.input_vars_by_category.get(category, self.input_vars_by_category["🚀 Performances CEA"])
        self.vars_out = self.output_vars_by_category.get(category, self.output_vars_by_category["🚀 Performances CEA"])
        
        # Mettre à jour les combobox
        self.combo_x['values'] = self.input_vars
        self.combo_x.current(0)
        self.combo_y['values'] = self.input_vars
        self.combo_y.current(0)
        self.combo_z['values'] = self.vars_out
        self.combo_z.current(0)

    def update_mode_display(self, event=None):
        """Affiche/masque l'axe Y selon le mode sélectionné"""
        mode = self.combo_mode.get()
        category = self.combo_category.get()
        
        if "3D" in mode:
            # Afficher l'axe Y et les ranges en mode 3D
            self.label_y.pack(side=tk.LEFT, padx=(10, 0))
            self.combo_y.pack(side=tk.LEFT, padx=5)
            self.label_ymin.pack(side=tk.LEFT, padx=(10, 0))
            self.e_ymin.pack(side=tk.LEFT, padx=2)
            self.label_ymax.pack(side=tk.LEFT, padx=(0, 0))
            self.e_ymax.pack(side=tk.LEFT, padx=2)
        else:
            # Masquer l'axe Y et les ranges en mode 2D
            self.label_y.pack_forget()
            self.combo_y.pack_forget()
            self.label_ymin.pack_forget()
            self.e_ymin.pack_forget()
            self.label_ymax.pack_forget()
            self.e_ymax.pack_forget()
        self.combo_z.current(0)
        
        # Mettre à jour les valeurs par défaut des ranges selon la catégorie
        defaults = {
            "🚀 Performances CEA": ("1.0", "4.0"),
            "🌡️ Thermique Paroi": ("0.5", "5.0"),  # Épaisseur en mm
            "💧 Refroidissement": ("0.1", "1.0"),  # Débit en kg/s
            "📐 Géométrie": ("0.5", "2.0"),  # L* en m
        }
        xmin, xmax = defaults.get(category, ("1.0", "4.0"))
        self.e_xmin.delete(0, tk.END)
        self.e_xmin.insert(0, xmin)
        self.e_xmax.delete(0, tk.END)
        self.e_xmax.insert(0, xmax)

    def plot_manager(self):
        self.root.config(cursor="watch")
        self.progress.start()
        self.root.after(100, self.execute_plot)

    def execute_plot(self):
        try:
            category = self.combo_category.get()
            mode = self.combo_mode.get()
            
            if "🌡️ Thermique" in category:
                self.plot_thermal_parametric()
            elif "💧 Refroidissement" in category:
                self.plot_cooling_parametric()
            elif "📐 Géométrie" in category:
                self.plot_geometry_parametric()
            elif "2D" in mode:
                self.plot_2d()
            else:
                self.plot_3d()
        except Exception as e:
            messagebox.showerror("Erreur Graphe", str(e))
        finally:
            self.progress.stop()
            self.root.config(cursor="")

    def plot_2d(self):
        self.fig_graph.clear()
        ax = self.fig_graph.add_subplot(111)
        self.apply_dark_axes(ax)
        
        steps = int(self.spin_res.get())
        try:
            xmin = float(self.e_xmin.get())
            xmax = float(self.e_xmax.get())
        except:
            xmin, xmax = 1.0, 4.0
        
        ox = self.get_val("ox")
        fuel = self.get_val("fuel")
        
        try:
            ispObj = CEA_Obj(oxName=ox, fuelName=fuel)
        except:
            messagebox.showerror("Erreur", "Ergols invalides")
            return
        
        mode_x = self.combo_x.get()
        var_out = self.combo_z.get()
        
        # Valeurs par défaut
        pc_def = self.get_val("pc")
        mr_def = self.get_val("mr")
        pe_def = self.get_val("pe")
        pamb_def = self.get_val("pamb")
        
        X_vals = []
        Y_vals = []
        
        for i in range(steps + 1):
            val = xmin + (xmax - xmin) * (i / steps)
            
            # Mapping input
            pc = val if "Pression Chambre" in mode_x else pc_def
            mr = val if "O/F" in mode_x else mr_def
            eps_ov = val if "Expansion" in mode_x else 0
            pamb = val if "Ambiante" in mode_x else pamb_def
            
            pc_psi = pc * 14.5038
            pe_psi = pe_def * 14.5038
            pamb_psi = pamb * 14.5038
            
            result = self.get_cea_value_safe(ispObj, pc_psi, mr, pe_psi, eps_ov, pamb_psi, var_out)
            
            if result > 0:
                X_vals.append(val)
                Y_vals.append(result)
        
        if X_vals:
            ax.plot(X_vals, Y_vals, '-', linewidth=2, marker='o', markersize=3, color=self.get_category_color())
            ax.set_xlabel(mode_x)
            ax.set_ylabel(var_out)
            ax.set_title(f"{var_out} vs {mode_x}")
            ax.grid(True, color=self.grid_color, alpha=0.35)
            
            # Annotation du max
            y_max = max(Y_vals)
            x_max = X_vals[Y_vals.index(y_max)]
            ax.plot(x_max, y_max, 'ro', markersize=10)
            ax.annotate(f"Max: {y_max:.2f}", (x_max, y_max),
                       xytext=(10, 10), textcoords='offset points',
                       color='red', fontweight='bold')
        
        self.canvas_graph.draw()

    def plot_3d(self):
        self.fig_graph.clear()
        ax = self.fig_graph.add_subplot(111, projection='3d')
        self.apply_dark_axes(ax)
        
        steps = int(self.spin_res.get())
        if steps > 30:
            messagebox.showwarning("Attention", "Résolution > 30 en 3D peut être lent.")
        
        ox = self.get_val("ox")
        fuel = self.get_val("fuel")
        
        try:
            ispObj = CEA_Obj(oxName=ox, fuelName=fuel)
        except:
            return
        
        try:
            xmin = float(self.e_xmin.get())
            xmax = float(self.e_xmax.get())
            ymin = float(self.e_ymin.get())
            ymax = float(self.e_ymax.get())
        except:
            xmin, xmax = 1.0, 4.0
            ymin, ymax = 1.5, 4.0
        
        mode_x = self.combo_x.get()
        mode_y = self.combo_y.get()
        var_z = self.combo_z.get()
        
        # Créer les ranges pour X et Y
        X_range = np.linspace(xmin, xmax, steps)
        Y_range = np.linspace(ymin, ymax, steps)
        
        X, Y = np.meshgrid(X_range, Y_range)
        Z = np.zeros_like(X)
        
        pe_def = self.get_val("pe")
        pamb_def = self.get_val("pamb")
        
        # Mapping des paramètres vers les variables CEA
        param_map = {
            "Pression Chambre (bar)": ("pc", float),
            "O/F Ratio": ("mr", float),
            "Expansion Ratio (Eps)": ("eps", float),
            "Contraction Ratio": ("cr", float),
            "Pression Ambiante (bar)": ("pamb", float),
            "L* (m)": ("lstar", float),
        }
        
        for i in range(steps):
            for j in range(steps):
                vx = X[i, j]
                vy = Y[i, j]
                
                # Initialiser avec les valeurs par défaut
                pc = self.get_val("pc")
                mr = self.get_val("mr")
                eps_ov = 0
                
                # Appliquer les valeurs d'entrée selon les axes sélectionnés
                if "Pression Chambre" in mode_x:
                    pc = vx
                elif "O/F" in mode_x:
                    mr = vx
                elif "Expansion" in mode_x:
                    eps_ov = vx
                
                if "Pression Chambre" in mode_y:
                    pc = vy
                elif "O/F" in mode_y:
                    mr = vy
                elif "Expansion" in mode_y:
                    eps_ov = vy
                
                pc_psi = pc * 14.5038
                pe_psi = pe_def * 14.5038
                pamb_psi = pamb_def * 14.5038
                
                Z[i, j] = self.get_cea_value_safe(ispObj, pc_psi, mr, pe_psi, eps_ov, pamb_psi, var_z)
        
        surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=True)
        ax.set_xlabel(mode_x.split(" ")[0])
        ax.set_ylabel(mode_y.split(" ")[0])
        ax.set_zlabel(var_z.split(" ")[0])
        cb = self.fig_graph.colorbar(surf, shrink=0.5, aspect=5)
        cb.ax.yaxis.set_tick_params(color=self.text_primary)
        plt.setp(cb.ax.get_yticklabels(), color=self.text_primary)
        
        self.canvas_graph.draw()

    # ==========================================================================
    # ANALYSE THERMIQUE PARAMÉTRIQUE
    # ==========================================================================
    def plot_thermal_parametric(self):
        """Analyse paramétrique thermique - T paroi vs épaisseur, conductivité, etc."""
        self.fig_graph.clear()
        ax = self.fig_graph.add_subplot(111)
        self.apply_dark_axes(ax)
        
        steps = int(self.spin_res.get())
        try:
            xmin = float(self.e_xmin.get())
            xmax = float(self.e_xmax.get())
        except:
            xmin, xmax = 0.5, 5.0
        
        mode_x = self.combo_x.get()
        var_out = self.combo_z.get()
        
        # Récupérer les paramètres de base depuis les résultats ou les inputs
        if not hasattr(self, 'results') or not self.results:
            messagebox.showwarning("Attention", "Veuillez d'abord lancer un calcul CEA+Thermique pour avoir les données de base.")
            return
        
        # Paramètres de base
        pc = self.get_val("pc")
        mr = self.get_val("mr")
        wall_k_base = self.get_val("wall_k")
        wall_thickness_base = self.get_val("wall_thickness")
        t_wall_cold = self.get_val("twall")
        
        # Données CEA
        tc_k = self.results.get('tc_k', 3000)
        tt_k = self.results.get('tt_k', 2700)
        cstar_mps = self.results.get('cstar_mps', 1500)
        dt = self.results.get('dt', 20)
        Mu_si = self.results.get('Mu', 7e-5)
        Cp_si = self.results.get('Cp', 2000)
        Pr = self.results.get('Pr', 0.5)
        
        # Calcul hg au col
        Dt_m = dt / 1000.0
        pc_pa = pc * 1e5
        term1 = 0.026 / (Dt_m ** 0.2)
        term2 = (Mu_si ** 0.2 * Cp_si) / (Pr ** 0.6)
        term3 = (pc_pa / cstar_mps) ** 0.8
        hg_throat = term1 * term2 * term3
        
        X_vals = np.linspace(xmin, xmax, steps)
        
        # Comparer plusieurs matériaux ?
        if self.var_multi_materials.get():
            materials_to_plot = list(self.materials_ref.keys())[:6]  # Max 6 matériaux
        else:
            materials_to_plot = [self.combo_material.get()]
        
        t_melt_lines = []
        
        for mat_name in materials_to_plot:
            mat = self.materials_ref.get(mat_name, {"k": wall_k_base, "t_melt": 1673, "color": "blue"})
            Y_vals = []
            
            for val in X_vals:
                # Déterminer les paramètres selon l'axe X
                if "Épaisseur" in mode_x:
                    wall_thickness_m = val / 1000.0
                    wall_k = mat["k"]
                    depth_ratio = 0  # Côté gaz (surface)
                elif "Conductivité" in mode_x:
                    wall_k = val
                    wall_thickness_m = wall_thickness_base / 1000.0
                    depth_ratio = 0
                elif "Temp. Coolant" in mode_x:
                    t_wall_cold_local = val
                    wall_k = mat["k"]
                    wall_thickness_m = wall_thickness_base / 1000.0
                    depth_ratio = 0
                elif "Profondeur" in mode_x:
                    # val = % de profondeur (0% = côté gaz, 100% = côté coolant)
                    depth_ratio = val / 100.0
                    wall_thickness_m = wall_thickness_base / 1000.0
                    wall_k = mat["k"]
                else:
                    wall_thickness_m = wall_thickness_base / 1000.0
                    wall_k = mat["k"]
                    depth_ratio = 0
                
                t_wall_cold_use = val if "Temp. Coolant" in mode_x else t_wall_cold
                
                # Calcul de la température de paroi côté gaz chaud au col
                if wall_k > 0 and wall_thickness_m > 0:
                    k_over_e = wall_k / wall_thickness_m
                    t_wall_hot = (hg_throat * tc_k + k_over_e * t_wall_cold_use) / (hg_throat + k_over_e)
                else:
                    t_wall_hot = t_wall_cold_use
                
                # Température au milieu de la paroi (interpolation linéaire)
                t_wall_mid = (t_wall_hot + t_wall_cold_use) / 2
                
                # Température à une profondeur donnée (interpolation linéaire)
                # depth_ratio = 0 -> côté gaz (T_hot), depth_ratio = 1 -> côté coolant (T_cold)
                t_at_depth = t_wall_hot - depth_ratio * (t_wall_hot - t_wall_cold_use)
                
                # Delta T dans la paroi
                delta_t_wall = t_wall_hot - t_wall_cold_use
                
                # Flux thermique
                q = hg_throat * (tc_k - t_wall_hot)
                q_mw = q / 1e6
                
                # Marge fusion (basée sur la température à la profondeur analysée)
                t_check = t_at_depth if "Profondeur" in mode_x else t_wall_hot
                marge_fusion = ((mat["t_melt"] - t_check) / mat["t_melt"]) * 100
                
                # Sélectionner la sortie
                if "T Paroi Gaz" in var_out:
                    Y_vals.append(t_wall_hot)
                elif "T Paroi Milieu" in var_out:
                    Y_vals.append(t_wall_mid)
                elif "T Paroi Coolant" in var_out:
                    Y_vals.append(t_wall_cold_use)
                elif "Profil T" in var_out:
                    # Si on varie la profondeur, on trace T en fonction de la position
                    if "Profondeur" in mode_x:
                        Y_vals.append(t_at_depth)
                    else:
                        Y_vals.append(delta_t_wall)
                elif "Delta T Paroi" in var_out:
                    Y_vals.append(delta_t_wall)
                elif "Flux Max" in var_out:
                    Y_vals.append(q_mw)
                elif "Flux Moyen" in var_out:
                    Y_vals.append(q_mw * 0.7)  # Approximation
                elif "Puissance" in var_out:
                    # Estimation basée sur surface col
                    A_throat = np.pi * (Dt_m/2)**2
                    Q_kw = q * A_throat * 10 / 1000  # Factor 10 pour surface totale approx
                    Y_vals.append(Q_kw)
                elif "Marge Fusion" in var_out:
                    Y_vals.append(marge_fusion)
                else:
                    Y_vals.append(t_wall_hot)
            
            color = mat.get("color", "blue")
            ax.plot(X_vals, Y_vals, '-', linewidth=2, marker='o', markersize=3, 
                   label=mat_name, color=color)
            
            # Afficher la ligne de température de fusion pour ce matériau
            if self.var_show_melt.get() and ("T Paroi" in var_out or "Profil T" in var_out or "Delta T" in var_out):
                ax.axhline(y=mat["t_melt"], color=color, linestyle='--', alpha=0.5, 
                          label=f"T fusion {mat_name}: {mat['t_melt']}K")
        
        ax.set_xlabel(mode_x)
        ax.set_ylabel(var_out)
        ax.set_title(f"Analyse Thermique: {var_out} vs {mode_x}")
        ax.grid(True, color=self.grid_color, alpha=0.35)
        ax.legend(
            loc='best',
            fontsize=7,
            ncol=min(2, len(materials_to_plot)+1),
            framealpha=0.9,
            facecolor=self.bg_surface,
            edgecolor=self.accent,
        )
        
        # Zone de danger (rouge) si température
        if "T Paroi" in var_out:
            y_lim = ax.get_ylim()
            if self.var_multi_materials.get():
                # Trouver la T fusion min
                t_melt_min = min([self.materials_ref[m]["t_melt"] for m in materials_to_plot])
            else:
                mat = self.materials_ref.get(self.combo_material.get(), {"t_melt": 1673})
                t_melt_min = mat["t_melt"]
            if y_lim[1] > t_melt_min:
                ax.axhspan(t_melt_min, y_lim[1], alpha=0.12, color='red')
        
        self.canvas_graph.draw()

    def plot_cooling_parametric(self):
        """Analyse paramétrique du refroidissement"""
        self.fig_graph.clear()
        ax = self.fig_graph.add_subplot(111)
        self.apply_dark_axes(ax)
        
        steps = int(self.spin_res.get())
        try:
            xmin = float(self.e_xmin.get())
            xmax = float(self.e_xmax.get())
        except:
            xmin, xmax = 0.1, 1.0
        
        mode_x = self.combo_x.get()
        var_out = self.combo_z.get()
        
        if not hasattr(self, 'results') or not self.results:
            messagebox.showwarning("Attention", "Veuillez d'abord lancer un calcul CEA+Thermique.")
            return
        
        # Paramètres de base
        Q_total = self.results.get('Q_total_kW', 50)  # kW
        coolant_tin = self.get_val("coolant_tin")
        coolant_tout_max = self.get_val("coolant_tout")
        mdot_base = self.get_val("mdot")
        
        # Cp coolant (approximation propane/eau)
        fuel = self.get_val("fuel")
        if "H2O" in fuel or "Water" in fuel:
            Cp_coolant = 4186
            T_boil = 373
        elif "C3H8" in fuel or "Propane" in fuel:
            Cp_coolant = 2500
            T_boil = 231
        elif "CH4" in fuel or "Methane" in fuel:
            Cp_coolant = 2200
            T_boil = 112
        else:
            Cp_coolant = 2500
            T_boil = 350
        
        X_vals = np.linspace(xmin, xmax, steps)
        Y_vals = []
        
        for val in X_vals:
            if "Débit Coolant" in mode_x:
                mdot = val
            else:
                mdot = mdot_base
            
            if "Temp. Entrée" in mode_x:
                t_in = val
            else:
                t_in = coolant_tin
            
            # Delta T = Q / (mdot * Cp)
            if mdot > 0:
                delta_t = (Q_total * 1000) / (mdot * Cp_coolant)
                t_out = t_in + delta_t
            else:
                delta_t = 0
                t_out = t_in
            
            # Marge ébullition
            marge_ebull = ((T_boil - t_out) / T_boil) * 100 if t_out < T_boil else -((t_out - T_boil) / T_boil) * 100
            
            if "T Sortie" in var_out:
                Y_vals.append(t_out)
            elif "Delta T" in var_out:
                Y_vals.append(delta_t)
            elif "Puissance" in var_out:
                Y_vals.append(Q_total)
            elif "Marge" in var_out:
                Y_vals.append(marge_ebull)
            else:
                Y_vals.append(t_out)
        
        ax.plot(X_vals, Y_vals, '-', linewidth=2, marker='o', markersize=3, color=self.get_category_color())
        
        # Ligne d'ébullition si température
        if "T Sortie" in var_out:
            ax.axhline(y=T_boil, color='red', linestyle='--', label=f"T ébullition: {T_boil}K")
            ax.legend()
        
        ax.set_xlabel(mode_x)
        ax.set_ylabel(var_out)
        ax.set_title(f"Analyse Refroidissement: {var_out} vs {mode_x}")
        ax.grid(True, color=self.grid_color, alpha=0.35)
        
        self.canvas_graph.draw()

    def plot_geometry_parametric(self):
        """Analyse paramétrique géométrique"""
        self.fig_graph.clear()
        ax = self.fig_graph.add_subplot(111)
        self.apply_dark_axes(ax)
        
        steps = int(self.spin_res.get())
        try:
            xmin = float(self.e_xmin.get())
            xmax = float(self.e_xmax.get())
        except:
            xmin, xmax = 0.5, 2.0
        
        mode_x = self.combo_x.get()
        var_out = self.combo_z.get()
        
        # Récupérer paramètres de base
        pc = self.get_val("pc")
        mr = self.get_val("mr")
        mdot = self.get_val("mdot")
        cr = self.get_val("cr")
        lstar = self.get_val("lstar")
        tn = self.get_val("tn")
        te = self.get_val("te")
        pe = self.get_val("pe")
        
        ox = self.get_val("ox")
        fuel = self.get_val("fuel")
        
        try:
            ispObj = CEA_Obj(oxName=ox, fuelName=fuel)
        except:
            messagebox.showerror("Erreur", "Ergols invalides")
            return
        
        pc_psi = pc * 14.5038
        pe_psi = pe * 14.5038
        
        X_vals = np.linspace(xmin, xmax, steps)
        Y_vals = []
        
        # Pré-calcul de l'ISP optimal (avec L* optimal autour de 1.0-1.5m)
        lstar_optimal = 1.2  # L* optimal typique
        try:
            cstar_opt = ispObj.get_Cstar(Pc=pc_psi, MR=mr)
            if isinstance(cstar_opt, tuple):
                cstar_fps = cstar_opt[0]
            else:
                cstar_fps = cstar_opt
            cstar_opt_mps = cstar_fps * 0.3048
            
            # ISP optimal avec L* optimal
            eps_optimal = ispObj.get_eps_at_PcOvPe(Pc=pc_psi, MR=mr, PcOvPe=pc/pe, frozen=0, frozenAtThroat=0)
            isp_opt = ispObj.get_Isp(Pc=pc_psi, MR=mr, eps=eps_optimal)
            # Modèle d'efficacité : 98% au L* optimal, décline pour L* trop petit ou trop grand
        except:
            isp_opt = 300
            cstar_opt_mps = 1500
            eps_optimal = 1.0
        
        for val in X_vals:
            # Paramètres variables
            lstar_use = val if "L*" in mode_x else lstar
            cr_use = val if "Contraction" in mode_x else cr
            tn_use = val if "Angle Entrée" in mode_x else tn
            te_use = val if "Angle Sortie" in mode_x else te
            
            if "Expansion" in mode_x:
                eps_override = val
                eps = val
            else:
                eps_override = 0
                try:
                    eps = ispObj.get_eps_at_PcOvPe(Pc=pc_psi, MR=mr, PcOvPe=pc/pe, frozen=0, frozenAtThroat=0)
                except:
                    eps = 10.0  # Valeur par défaut
            
            # Calcul géométrie - get_Cstar retourne un float, pas un tuple
            try:
                cstar_result = ispObj.get_Cstar(Pc=pc_psi, MR=mr)
                if isinstance(cstar_result, tuple):
                    cstar_fps = cstar_result[0]
                else:
                    cstar_fps = cstar_result
                cstar_mps = cstar_fps * 0.3048
            except:
                cstar_mps = 1500  # Valeur par défaut
            
            # Calcul ISP et performances
            try:
                isp_vac = ispObj.get_Isp(Pc=pc_psi, MR=mr, eps=eps)
                pamb_psi = self.get_val("pamb") * 14.5038
                isp_amb = ispObj.estimate_Ambient_Isp(Pc=pc_psi, MR=mr, eps=eps, Pamb=pamb_psi)[0]
                cf_vac = ispObj.get_PambCf(Pc=pc_psi, MR=mr, eps=eps, Pamb=0)[1]
            except:
                isp_vac = 300
                isp_amb = 280
                cf_vac = 1.8
            
            At = (mdot * cstar_mps) / (pc * 1e5)
            dt = np.sqrt(4 * At / np.pi) * 1000
            Ac = At * cr_use
            dc = np.sqrt(4 * Ac / np.pi) * 1000
            de = dt * np.sqrt(eps)
            
            Vc = At * lstar_use
            lc = Vc / Ac * 1000
            
            l_conv = (dc - dt) / (2 * np.tan(np.radians(30))) if cr_use > 1 else 0
            l_div = (de - dt) / (2 * np.tan(np.radians((tn_use + te_use) / 2)))
            l_total = lc + l_conv + l_div
            
            # Efficacité de combustion en fonction du L* (modèle parabolique)
            # 100% d'efficacité au L* optimal, décline pour L* trop petit ou trop grand
            l_ratio = lstar_use / lstar_optimal
            combustion_eff = 100 * (1 - 0.02 * (l_ratio - 1)**2)  # Parabole centrée sur 1
            combustion_eff = max(combustion_eff, 50)  # Min 50%
            
            if "Longueur Chambre" in var_out:
                Y_vals.append(lc)
            elif "Longueur Convergent" in var_out:
                Y_vals.append(l_conv)
            elif "Longueur Divergent" in var_out:
                Y_vals.append(l_div)
            elif "Longueur Totale" in var_out:
                Y_vals.append(l_total)
            elif "Diamètre Col" in var_out:
                Y_vals.append(dt)
            elif "Diamètre Sortie" in var_out:
                Y_vals.append(de)
            elif "ISP Vide" in var_out:
                # ISP réelle avec perte de combustion
                isp_effective = isp_vac * (combustion_eff / 100)
                Y_vals.append(isp_effective)
            elif "ISP Ambiante" in var_out:
                # ISP réelle avec perte de combustion
                isp_amb_effective = isp_amb * (combustion_eff / 100)
                Y_vals.append(isp_amb_effective)
            elif "Efficacité Combustion" in var_out:
                Y_vals.append(combustion_eff)
            elif "C*" in var_out:
                Y_vals.append(cstar_mps)
            elif "Poussée" in var_out:
                # F = mdot * Isp * g0
                isp_effective = isp_vac * (combustion_eff / 100)
                thrust_N = mdot * isp_effective * 9.81
                Y_vals.append(thrust_N)
            else:
                Y_vals.append(l_total)
        
        ax.plot(X_vals, Y_vals, '-', linewidth=2, marker='s', markersize=4, color=self.get_category_color())
        ax.set_xlabel(mode_x)
        ax.set_ylabel(var_out)
        ax.set_title(f"Analyse Géométrie: {var_out} vs {mode_x}")
        ax.grid(True, color=self.grid_color, alpha=0.35)
        
        self.canvas_graph.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = RocketApp(root)
    root.mainloop()
