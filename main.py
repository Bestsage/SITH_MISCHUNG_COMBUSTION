
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, font as tkfont
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np
import math
import json
import os
import io
import re
from datetime import datetime

# Configuration CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Fonction pour obtenir la meilleure police monospace disponible
def get_monospace_font():
    """Retourne une police monospace appropriée selon le système."""
    import platform
    import tkinter as tk
    
    # Test des polices dans l'ordre de préférence
    test_fonts = ["Consolas", "Monaco", "Menlo", "Courier New", "Liberation Mono", "DejaVu Sans Mono", "Courier"]
    
    # Créer une fenêtre temporaire pour tester les polices (non affichée)
    test_root = tk.Tk()
    test_root.withdraw()
    
    for font_name in test_fonts:
        try:
            test_font = tk.font.Font(family=font_name, size=10)
            # Vérifier si la police existe en testant ses métriques
            if test_font.actual()['family'] == font_name:
                test_root.destroy()
                return font_name
        except:
            continue
    
    test_root.destroy()
    # Fallback: utiliser la police monospace par défaut du système
    return "Courier" if platform.system() != "Linux" else "Liberation Mono"

# Police monospace système pour les widgets Text
MONOSPACE_FONT = get_monospace_font()

# Fonction pour obtenir la meilleure police UI (sans serif) disponible
def get_ui_font():
    """Retourne une police UI appropriée selon le système."""
    import platform
    import tkinter as tk
    
    # Test des polices dans l'ordre de préférence
    test_fonts = ["Segoe UI", "Roboto", "Ubuntu", "Cantarell", "DejaVu Sans", "Liberation Sans", "Arial", "Helvetica", "Sans"]
    
    # Créer une fenêtre temporaire pour tester les polices (non affichée)
    test_root = tk.Tk()
    test_root.withdraw()
    
    for font_name in test_fonts:
        try:
            test_font = tk.font.Font(family=font_name, size=10)
            # Vérifier si la police existe
            if test_font.actual()['family'] == font_name:
                test_root.destroy()
                return font_name
        except:
            continue
    
    test_root.destroy()
    # Fallback: utiliser la police sans serif par défaut
    return "Sans"

# Police UI système
UI_FONT = get_ui_font()

# Fonction pour détecter le scaling du bureau sur Linux
def get_linux_desktop_scale():
    """Détecte le facteur de scaling du bureau Linux (GNOME/KDE).
    
    Réf: https://github.com/TomSchimansky/CustomTkinter/issues/2597
    Le bug connu est que CustomTkinter ne détecte pas correctement le desktop scaling
    sur Linux, ce qui rend les widgets écrasés.
    """
    import platform
    import subprocess
    import os
    
    if platform.system() != "Linux":
        return 1.0
    
    scale = 1.0
    detection_method = "none"
    
    # Méthode 1: Détection via DPI réel vs logique (la plus fiable)
    # Cette méthode fonctionne même avec le fractional scaling de GNOME
    try:
        import tkinter as tk
        root_temp = tk.Tk()
        root_temp.withdraw()
        
        # Obtenir les dimensions réelles et logiques
        root_temp.update_idletasks()
        # Mesurer 1 pouce réel
        real_dpi = root_temp.winfo_fpixels('1i')
        # Mesurer 1 pouce logique (ce que le système pense)
        logical_dpi = root_temp.winfo_pixels('1i')
        root_temp.destroy()
        
        if real_dpi > 0 and logical_dpi > 0:
            # Le ratio donne le scaling réel
            detected_scale = real_dpi / logical_dpi
            if detected_scale > 0.5 and detected_scale < 5.0:  # Plage raisonnable
                # Arrondir à des valeurs communes pour éviter les variations mineures
                common_scales = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
                detected_scale = min(common_scales, key=lambda x: abs(x - detected_scale))
                scale = detected_scale
                detection_method = "DPI"
    except Exception as e:
        pass
    
    # Méthode 2: Variables d'environnement (Wayland/X11)
    if scale == 1.0:
        try:
            # GDK_SCALE pour GTK/Wayland
            gdk_scale = os.environ.get("GDK_SCALE", "")
            if gdk_scale:
                try:
                    scale = float(gdk_scale)
                    detection_method = "GDK_SCALE"
                except:
                    pass
            
            # QT_SCALE_FACTOR (pour KDE/Qt apps)
            if scale == 1.0:
                qt_scale = os.environ.get("QT_SCALE_FACTOR", "")
                if qt_scale:
                    try:
                        scale = float(qt_scale)
                        detection_method = "QT_SCALE_FACTOR"
                    except:
                        pass
        except:
            pass
    
    # Méthode 3: GNOME avec gsettings (scaling entier, ancienne méthode)
    if scale == 1.0:
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "scaling-factor"],
                capture_output=True, text=True, timeout=1, stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                scale_str = result.stdout.strip()
                if scale_str and scale_str.startswith("uint32"):
                    # Format: uint32 2 pour 200%
                    parts = scale_str.split()
                    if len(parts) >= 2:
                        scale_int = int(parts[1])
                        if scale_int > 0:
                            scale = float(scale_int)
                            detection_method = "gsettings"
        except:
            pass
    
    # Méthode 4: Détection via xrandr (X11)
    if scale == 1.0:
        try:
            result = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True, text=True, timeout=1, stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ' connected' in line and 'mm' in line:
                        # Essayer d'extraire le DPI depuis les dimensions
                        # Format: 1920x1080+0+0 (512mm x 288mm)
                        import re
                        match = re.search(r'\((\d+)mm.*?(\d+)mm\)', line)
                        if match:
                            width_mm = float(match.group(1))
                            height_mm = float(match.group(2))
                            # Extraire la résolution
                            res_match = re.search(r'(\d+)x(\d+)', line)
                            if res_match:
                                width_px = float(res_match.group(1))
                                height_px = float(res_match.group(2))
                                # Calculer le DPI
                                width_dpi = width_px / (width_mm / 25.4)
                                height_dpi = height_px / (height_mm / 25.4)
                                avg_dpi = (width_dpi + height_dpi) / 2
                                detected_scale = avg_dpi / 96.0
                                if 0.5 < detected_scale < 5.0:
                                    common_scales = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
                                    detected_scale = min(common_scales, key=lambda x: abs(x - detected_scale))
                                    scale = detected_scale
                                    detection_method = "xrandr"
                                    break
        except:
            pass
    
    # S'assurer que le scale est dans une plage valide
    scale = max(1.0, min(5.0, scale))
    
    return scale, detection_method

# Configuration spécifique pour Linux pour améliorer le rendu
try:
    import platform
    import os
    if platform.system() == "Linux":
        # Vérifier si l'utilisateur a défini manuellement le scaling
        manual_scale = os.environ.get("CUSTOMTKINTER_SCALE", None)
        if manual_scale:
            try:
                desktop_scale = float(manual_scale)
                method = "manuel (variable CUSTOMTKINTER_SCALE)"
            except:
                desktop_scale, method = get_linux_desktop_scale()
        else:
            # Détecter le scaling du bureau automatiquement
            desktop_scale, method = get_linux_desktop_scale()
        
        # Appliquer le scaling à CustomTkinter
        # Le widget scaling doit correspondre au scaling du bureau pour éviter l'écrasement
        # Référence: https://github.com/TomSchimansky/CustomTkinter/issues/2597
        ctk.set_widget_scaling(desktop_scale)
        ctk.set_window_scaling(desktop_scale)
        
        print(f"📝 Police monospace utilisée: {MONOSPACE_FONT}")
        print(f"📝 Police UI utilisée: {UI_FONT}")
        print(f"🖥️  Scaling du bureau détecté: {desktop_scale:.2f}x (méthode: {method})")
        if desktop_scale != 1.0:
            print(f"✅ Scaling CustomTkinter configuré pour corriger le bug d'affichage Linux")
        if manual_scale is None and desktop_scale == 1.0:
            print(f"💡 Astuce: Si les widgets semblent écrasés, définissez CUSTOMTKINTER_SCALE=2.0 (exemple)")
            print(f"   Exemple: CUSTOMTKINTER_SCALE=2.0 python3.10 main.py")
    else:
        # Pour Windows/Mac, utiliser les valeurs par défaut
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
except Exception as e:
    print(f"⚠️  Erreur lors de la configuration du scaling: {e}")
    # Valeurs par défaut en cas d'erreur
    try:
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
    except:
        pass 

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

# Essayer d'importer numpy-stl pour l'export 3D
try:
    from stl import mesh as stl_mesh
    HAS_NUMPY_STL = True
except ImportError:
    HAS_NUMPY_STL = False

# Essayer d'importer cadquery pour l'export STEP
try:
    import cadquery as cq
    HAS_CADQUERY = True
except ImportError:
    HAS_CADQUERY = False

class MultiRowTabview(ctk.CTkFrame):
    """
    A custom TabView that arranges tab buttons in multiple rows.
    Supports detaching tabs into separate windows via Right-Click.
    """
    def __init__(self, master, 
                 fg_color=None, 
                 btn_fg_color=None,
                 btn_hover_color=None,
                 btn_selected_color=None,
                 btn_text_color=None,
                 btn_selected_text_color=None,
                 command_right_click=None,
                 **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.main_fg_color = fg_color
        self.btn_fg_color = btn_fg_color
        self.btn_hover_color = btn_hover_color
        self.btn_selected_color = btn_selected_color
        self.btn_text_color = btn_text_color
        self.btn_selected_text_color = btn_selected_text_color
        self.command_right_click = command_right_click
        
        # Frame for buttons (Top)
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(side="top", fill="x", pady=(0, 5))
        
        # Rows for buttons
        self.row1 = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        self.row1.pack(side="top", fill="x", pady=(0, 2))
        self.row2 = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        self.row2.pack(side="top", fill="x")
        
        # Content frame (Bottom)
        self.content_frame = ctk.CTkFrame(self, fg_color=self.main_fg_color, corner_radius=10)
        self.content_frame.pack(side="bottom", fill="both", expand=True)
        
        self.tabs = {}     # name -> frame
        self.buttons = {}  # name -> button
        self.popped_windows = set() # Set of names of popped out tabs
        self.current_tab = None

    def add(self, name):
        # Create the tab content frame
        frame = ctk.CTkFrame(self.content_frame, fg_color=self.main_fg_color, corner_radius=0)
        self.tabs[name] = frame
        
        # Decide which row to put the button in (Split 6 / rest)
        if len(self.buttons) < 6:
            parent = self.row1
        else:
            parent = self.row2
            
        # Create the button
        btn = ctk.CTkButton(parent, text=name,
                            fg_color=self.btn_fg_color,
                            hover_color=self.btn_hover_color,
                            text_color=self.btn_text_color,
                            corner_radius=6,
                            height=28,
                            width=80, # Allow expanding
                            command=lambda: self.set(name))
        
        btn.pack(side="left", fill="x", expand=True, padx=2)
        
        # Bind Right Click if callback provided
        if self.command_right_click:
            btn.bind("<Button-3>", lambda event, n=name: self.command_right_click(n))
        
        self.buttons[name] = btn
        return frame

    def set(self, name):
        if name not in self.tabs:
            return
        
        # Hide all tabs
        for f in self.tabs.values():
            f.pack_forget()
            
        # Reset all buttons color
        for n, b in self.buttons.items():
            is_popped = n in self.popped_windows
            if n == name:
                b.configure(fg_color=self.btn_selected_color)
                if self.btn_selected_text_color:
                    b.configure(text_color=self.btn_selected_text_color)
            else:
                b.configure(fg_color=self.btn_fg_color if not is_popped else "gray20")
                b.configure(text_color=self.btn_text_color if not is_popped else "gray60")
                
        # Show selected tab (only if not popped out)
        if name not in self.popped_windows:
            self.tabs[name].pack(fill="both", expand=True, padx=5, pady=5)
            
        self.current_tab = name
        
    def pop_out(self, name):
        """Marque l'onglet comme détaché (visuel uniquement)."""
        self.popped_windows.add(name)
        self.buttons[name].configure(text=f"❐ {name}")
        # Masquer le contenu si c'était l'onglet actif
        if self.current_tab == name:
            self.tabs[name].pack_forget()
        self.set(self.current_tab) # Rafraîchir les couleurs

    def dock_in(self, name):
        """Marque l'onglet comme rattaché (visuel uniquement)."""
        if name in self.popped_windows:
            self.popped_windows.remove(name)
            self.buttons[name].configure(text=name)
            # Réafficher si c'est l'onglet actif
            if self.current_tab == name:
                self.tabs[name].pack(fill="both", expand=True, padx=5, pady=5)
            self.set(self.current_tab) # Rafraîchir les couleurs
        
    def get(self):
        return self.current_tab

class RocketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SITH MISCHUNG COMBUSTION : DARK SIDE EDITION v6.3")
        self.root.geometry("1700x1080")
        
        # Maximiser la fenêtre dès le début (comportement d'origine)
        try:
            self.root.state('zoomed')
        except:
            pass

        # Zoom options for UI (defined early for create_inputs)
        self.zoom_options = ["Auto", "1.0", "1.15", "1.25", "1.35", "1.5"]

        # --- THEME (OLED + Néon) ---
        self.bg_main = "#000000"
        self.bg_panel = "#07080A"
        self.bg_surface = "#080a0c"
        self.accent = "#00d9ff"       # cyan néon
        self.accent_alt = "#ff5af1"   # magenta néon
        self.accent_alt2 = "#9dff6a"  # vert néon doux
        self.accent_alt3 = "#ffb347"  # orange chaud
        self.accent_alt4 = "#7b9bff"  # lavande
        self.text_primary = "#e8f1ff"
        self.text_muted = "#8b949e"
        self.grid_color = "#15191d"
        self.border_color = "#30363d"

        self.tab_accent = {
            "summary": self.accent,
            "visu": self.accent_alt3,
            "thermal": self.accent_alt,
            "graphs": self.accent,
            "cea": self.accent_alt2,
            "database": self.accent_alt4,
            "solver": "#00ffaa",
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
        self.geometry_profile = None
        
        # --- BASE DE DONNÉES MATÉRIAUX UNIFIÉE ---
        self.materials_db = {
            "Cuivre (Cu-OFHC)": {"k": 390, "T_melt": 1356, "T_max": 800, "rho": 8940, "E": 115, "nu": 0.34, "alpha": 17.0, "sigma_y": 60, "sigma_uts": 220, "color": "#b87333"},
            "Cuivre-Chrome (CuCr)": {"k": 320, "T_melt": 1350, "T_max": 1050, "rho": 8900, "E": 118, "nu": 0.33, "alpha": 17.0, "sigma_y": 350, "sigma_uts": 420, "color": "#cd7f32"},
            "Cuivre-Zirconium (CuZr)": {"k": 340, "T_melt": 1356, "T_max": 900, "rho": 8920, "E": 120, "nu": 0.33, "alpha": 17.0, "sigma_y": 280, "sigma_uts": 380, "color": "#d2691e"},
            "GlidCop AL-15": {"k": 365, "T_melt": 1356, "T_max": 1200, "rho": 8900, "E": 130, "nu": 0.33, "alpha": 16.6, "sigma_y": 380, "sigma_uts": 450, "color": "#cc5500"},
            "CuCrNb (GRCop-42)": {"k": 320, "T_melt": 1330, "T_max": 1100, "rho": 8790, "E": 115, "nu": 0.33, "alpha": 17.5, "sigma_y": 260, "sigma_uts": 430, "color": "#ff7f50"},
            "AlSi10Mg (SLM)": {"k": 110, "T_melt": 843, "T_max": 570, "rho": 2670, "E": 70, "nu": 0.33, "alpha": 21.0, "sigma_y": 240, "sigma_uts": 350, "color": "#a9a9a9"},
            "Aluminium 7075-T6": {"k": 130, "T_melt": 750, "T_max": 400, "rho": 2810, "E": 71, "nu": 0.33, "alpha": 23.6, "sigma_y": 503, "sigma_uts": 572, "color": "#c0c0c0"},
            "Aluminium 6061-T6": {"k": 167, "T_melt": 855, "T_max": 450, "rho": 2700, "E": 69, "nu": 0.33, "alpha": 23.6, "sigma_y": 276, "sigma_uts": 310, "color": "#d3d3d3"},
            "Inconel 718": {"k": 11.4, "T_melt": 1533, "T_max": 1200, "rho": 8190, "E": 200, "nu": 0.29, "alpha": 13.0, "sigma_y": 1030, "sigma_uts": 1240, "color": "#8b4513"},
            "Inconel 625": {"k": 9.8, "T_melt": 1563, "T_max": 1250, "rho": 8440, "E": 207, "nu": 0.28, "alpha": 12.8, "sigma_y": 460, "sigma_uts": 880, "color": "#a0522d"},
            "Monel 400": {"k": 21.8, "T_melt": 1570, "T_max": 1000, "rho": 8800, "E": 179, "nu": 0.32, "alpha": 13.9, "sigma_y": 240, "sigma_uts": 550, "color": "#808000"},
            "Hastelloy X": {"k": 9.1, "T_melt": 1530, "T_max": 1300, "rho": 8220, "E": 205, "nu": 0.30, "alpha": 14.0, "sigma_y": 360, "sigma_uts": 750, "color": "#556b2f"},
            "Acier Inox 316L": {"k": 16.3, "T_melt": 1673, "T_max": 1100, "rho": 8000, "E": 193, "nu": 0.30, "alpha": 16.0, "sigma_y": 290, "sigma_uts": 580, "color": "#708090"},
            "Acier Inox 304L": {"k": 16.2, "T_melt": 1673, "T_max": 1050, "rho": 7900, "E": 193, "nu": 0.29, "alpha": 17.2, "sigma_y": 215, "sigma_uts": 505, "color": "#778899"},
            "Acier Inox 17-4PH": {"k": 17.9, "T_melt": 1677, "T_max": 600, "rho": 7750, "E": 196, "nu": 0.27, "alpha": 10.8, "sigma_y": 1100, "sigma_uts": 1250, "color": "#696969"},
            "Titane Ti-6Al-4V": {"k": 6.7, "T_melt": 1933, "T_max": 750, "rho": 4430, "E": 114, "nu": 0.34, "alpha": 8.6, "sigma_y": 880, "sigma_uts": 950, "color": "#4682b4"},
            "Niobium C-103": {"k": 42, "T_melt": 2623, "T_max": 2200, "rho": 8860, "E": 90, "nu": 0.40, "alpha": 7.3, "sigma_y": 250, "sigma_uts": 380, "color": "#9370db"},
            "Molybdène (TZM)": {"k": 126, "T_melt": 2896, "T_max": 2400, "rho": 10220, "E": 320, "nu": 0.31, "alpha": 5.3, "sigma_y": 560, "sigma_uts": 700, "color": "#4b0082"},
            "Tungstène": {"k": 173, "T_melt": 3695, "T_max": 3200, "rho": 19250, "E": 411, "nu": 0.28, "alpha": 4.5, "sigma_y": 550, "sigma_uts": 980, "color": "#000080"},
            "Tantalum": {"k": 57, "T_melt": 3290, "T_max": 2800, "rho": 16690, "E": 186, "nu": 0.34, "alpha": 6.3, "sigma_y": 170, "sigma_uts": 250, "color": "#483d8b"},
            "Rhenium": {"k": 48, "T_melt": 3459, "T_max": 3000, "rho": 21020, "E": 463, "nu": 0.26, "alpha": 6.2, "sigma_y": 290, "sigma_uts": 490, "color": "#800000"},
            "Graphite": {"k": 120, "T_melt": 3900, "T_max": 3500, "rho": 1800, "E": 11, "nu": 0.20, "alpha": 4.0, "sigma_y": 30, "sigma_uts": 45, "color": "#000000"},
            "Carbon-Phenolic": {"k": 1.5, "T_melt": 2500, "T_max": 3000, "rho": 1450, "E": 15, "nu": 0.30, "alpha": 5.0, "sigma_y": 50, "sigma_uts": 80, "color": "#2f4f4f"},
        }

        # --- LAYOUT PRINCIPAL CUSTOMTKINTER ---
        main_frame = ctk.CTkFrame(self.root, fg_color=self.bg_main)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- SYSTÈME SIDEBAR (Gauche) ---
        # 1. Barre de contrôle fine (toujours visible)
        self.sidebar_ctrl = ctk.CTkFrame(main_frame, width=32, fg_color=self.bg_panel, corner_radius=0)
        self.sidebar_ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0), pady=0)

        # Bouton Toggle
        self.btn_toggle = ctk.CTkButton(
            self.sidebar_ctrl, text="◀", width=32, height=32,
            fg_color="transparent", text_color=self.accent,
            font=ctk.CTkFont(size=14, weight="bold"),
            hover_color=self.bg_surface,
            command=self.toggle_sidebar
        )
        self.btn_toggle.pack(side=tk.TOP, pady=5, padx=0)

        # 2. Panneau Gauche (Contenu Scrollable & Masquable)
        self.left_panel = ctk.CTkScrollableFrame(
            main_frame, 
            width=400,
            fg_color=self.bg_panel,
            border_color=self.border_color,
            border_width=1,
            corner_radius=10,
            label_text="⚙️ Paramètres",
            label_fg_color=self.accent,
            label_text_color=self.bg_main
        )
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 10), pady=0)
        
        # Alias pour compatibilité avec le reste du code
        left_panel = self.left_panel
        
        # Panneau Droit
        right_panel = ctk.CTkFrame(main_frame, fg_color=self.bg_main)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # MultiRowTabview personnalisé
        self.tabs = MultiRowTabview(
            right_panel,
            fg_color=self.bg_panel,
            btn_fg_color=self.bg_surface,
            btn_selected_color=self.accent,
            btn_hover_color=self.grid_color,
            btn_text_color=self.text_primary,
            btn_selected_text_color=self.bg_main,
            command_right_click=self.handle_tab_detach,
            corner_radius=10
        )
        self.tabs.pack(fill=tk.BOTH, expand=True)
        
        # Créer les onglets
        self.tab_summary = self.tabs.add("📊 Résumé")
        self.tab_cad = self.tabs.add("👁️ Visu & CAD")
        self.tab_thermal = self.tabs.add("🌡️ Thermique")
        self.tab_heatmap = self.tabs.add("🔥 Carte 2D")
        self.tab_optimizer = self.tabs.add("⚙️ Optimiseur")
        self.tab_stress = self.tabs.add("🛡️ Contraintes")
        self.tab_graphs = self.tabs.add("📈 Analyses")
        self.tab_cea = self.tabs.add("🔬 NASA CEA")
        self.tab_database = self.tabs.add("🔍 Matériaux")
        self.tab_solver = self.tabs.add("🧊 Coolant")
        self.tab_wiki = self.tabs.add("📖 Wiki")
        
        # Calculer le zoom AVANT d'initialiser les onglets
        self.ui_scale = self.auto_scale_from_display()
        
        self.create_inputs(left_panel)
        self.init_summary_tab()
        self.init_thermal_tab()
        self.init_heatmap_tab()
        self.init_cad_tab()
        self.init_optimizer_tab()
        self.init_stress_tab()
        self.init_cea_tab()
        self.init_graphs_tab()
        self.init_database_tab()
        self.init_solver_tab()
        self.init_wiki_tab()

        # Configurer le style TTK pour les Treeviews (fonds sombres)
        self.setup_ttk_style()

        # Apply UI scaling after layout is ready
        self.apply_ui_scale(self.ui_scale)

        # MAPPING DES ONGLETS POUR LE DÉTACHEMENT
        # Format: "Nom": {"var": "nom_variable_frame", "init": "nom_methode_init", "update": "nom_methode_update_ou_None"}
        self.tab_map = {
            "📊 Résumé": {"var": "tab_summary", "init": "init_summary_tab", "update": "refresh_summary_tab"},
            "👁️ Visu & CAD": {"var": "tab_cad", "init": "init_cad_tab", "update": "update_cad_preview"},
            "🌡️ Thermique": {"var": "tab_thermal", "init": "init_thermal_tab", "update": "refresh_thermal_tab"},
            "🔥 Carte 2D": {"var": "tab_heatmap", "init": "init_heatmap_tab", "update": "update_heatmap"},
            "⚙️ Optimiseur": {"var": "tab_optimizer", "init": "init_optimizer_tab", "update": "refresh_optimizer_tab"},
            "🛡️ Contraintes": {"var": "tab_stress", "init": "init_stress_tab", "update": "calculate_stresses"},
            "📈 Analyses": {"var": "tab_graphs", "init": "init_graphs_tab", "update": "plot_manager"},
            "🔬 NASA CEA": {"var": "tab_cea", "init": "init_cea_tab", "update": None},
            "🔍 Matériaux": {"var": "tab_database", "init": "init_database_tab", "update": "search_database"},
            "🧊 Coolant": {"var": "tab_solver", "init": "init_solver_tab", "update": None},
            "📖 Wiki": {"var": "tab_wiki", "init": "init_wiki_tab", "update": None},
        }

        # Sélectionner le premier onglet par défaut
        self.tabs.set("📊 Résumé")
        
        # Gérer la fermeture propre de l'application
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ttk_style(self):
        """Configure le thème des widgets standards TTK (Treeview, etc.) pour correspondre au mode sombre."""
        style = ttk.Style()
        style.theme_use('clam') # 'clam' permet plus de personnalisation que 'vista' ou 'xpnative'
        
        # Configuration Treeview (Tableaux)
        style.configure("Treeview",
                        background=self.bg_surface,
                        fieldbackground=self.bg_surface,
                        foreground=self.text_primary,
                        borderwidth=0,
                        font=(UI_FONT, self.scaled_font_size(10)))
        
        style.map("Treeview",
                  background=[('selected', self.accent)],
                  foreground=[('selected', self.bg_main)])
        
        # En-têtes Treeview
        style.configure("Treeview.Heading",
                        background=self.bg_panel,
                        foreground=self.accent,
                        relief="flat",
                        font=(UI_FONT, self.scaled_font_size(11), "bold"))
        
        style.map("Treeview.Heading",
                  background=[('active', self.bg_surface)])
        
        # Ascenseurs (Scrollbars)
        style.configure("Vertical.TScrollbar",
                        background=self.bg_panel,
                        troughcolor=self.bg_main,
                        bordercolor=self.border_color,
                        arrowcolor=self.accent)

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
            self.txt_summary.configure(font=(MONOSPACE_FONT, fs))
            self.txt_summary.tag_configure("title", font=(MONOSPACE_FONT, fs_title, "bold"))
            self.txt_summary.tag_configure("section", font=(MONOSPACE_FONT, fs, "bold"))
        
        # Widget CEA
        if hasattr(self, 'txt_cea'):
            self.txt_cea.configure(font=(MONOSPACE_FONT, fs))
            self.txt_cea.tag_configure("cea_header", font=(MONOSPACE_FONT, fs, "bold"))
            self.txt_cea.tag_configure("cea_comment", font=(MONOSPACE_FONT, fs, "italic"))
        
        # Widget Base de données
        if hasattr(self, 'db_details'):
            self.db_details.configure(font=(MONOSPACE_FONT, fs))
            self.db_details.tag_configure("db_title", font=(MONOSPACE_FONT, fs_title, "bold"))
            self.db_details.tag_configure("db_section", font=(MONOSPACE_FONT, fs, "bold"))
        
        # Widget Solveur
        if hasattr(self, 'txt_solver'):
            self.txt_solver.configure(font=(MONOSPACE_FONT, fs))
            self.txt_solver.tag_configure("title", font=(MONOSPACE_FONT, fs_title, "bold"))
            self.txt_solver.tag_configure("section", font=(MONOSPACE_FONT, fs, "bold"))

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

    def handle_tab_detach(self, tab_name):
        """Gère le détachement complet d'un onglet dans une nouvelle fenêtre."""
        if tab_name not in self.tab_map:
            messagebox.showinfo("Info", f"Le détachement n'est pas configuré pour '{tab_name}'.")
            return

        info = self.tab_map[tab_name]
        var_name = info["var"]
        init_method_name = info["init"]
        update_method_name = info["update"]

        # Récupérer le frame original (qui est actuellement self.tab_...)
        original_frame = self.tabs.tabs[tab_name]
        
        # S'assurer que l'onglet n'est pas déjà détaché (vérification basique)
        if getattr(self, var_name) != original_frame:
            # Déjà détaché, on pourrait ramener au premier plan la fenêtre existante
            # Mais ici on suppose que MultiRowTabview gère l'état visuel
            return

        # 1. Vider le frame original (sans le détruire lui-même)
        for child in original_frame.winfo_children():
            child.destroy()

        # 2. Créer la nouvelle fenêtre
        win = ctk.CTkToplevel(self.root)
        win.title(f"{tab_name} - Détaché")
        win.geometry("1000x800")
        
        # Frame conteneur dans la fenêtre pour simuler l'environnement de l'onglet
        container = ctk.CTkFrame(win, fg_color=self.bg_panel)
        container.pack(fill=tk.BOTH, expand=True)

        # 3. Détourner la variable d'instance (ex: self.tab_thermal) vers le nouveau conteneur
        setattr(self, var_name, container)

        # 4. Reconstruire l'interface de l'onglet dans la nouvelle fenêtre
        if hasattr(self, init_method_name):
            getattr(self, init_method_name)()
        
        # 5. Restaurer l'état / les données
        if update_method_name and hasattr(self, update_method_name):
            try:
                getattr(self, update_method_name)()
            except Exception as e:
                print(f"Erreur lors de la mise à jour de l'onglet détaché: {e}")

        # 6. Gérer la fermeture de la fenêtre pour "Rentrer" l'onglet
        def on_close():
            win.destroy()
            
            # Restaurer la variable d'instance vers le frame original
            setattr(self, var_name, original_frame)
            
            # Reconstruire l'interface dans l'onglet original
            if hasattr(self, init_method_name):
                getattr(self, init_method_name)()
            
            # Restaurer les données
            if update_method_name and hasattr(self, update_method_name):
                try:
                    getattr(self, update_method_name)()
                except:
                    pass
            
            # Notifier le TabView que l'onglet est revenu
            self.tabs.dock_in(tab_name)

        win.protocol("WM_DELETE_WINDOW", on_close)
        
        # Notifier le TabView que l'onglet est sorti (visuel bouton)
        self.tabs.pop_out(tab_name)

    # --- Helpers pour rafraîchir les onglets après reconstruction ---
    
    def refresh_summary_tab(self):
        """Rafraîchit l'onglet Résumé."""
        if hasattr(self, 'last_summary_data'):
            self.insert_colored_summary(*self.last_summary_data)

    def refresh_thermal_tab(self):
        """Rafraîchit l'onglet Thermique."""
        if not self.results: return
        # On appelle une méthode qui redessine les graphiques thermiques
        # Comme run_simulation fait tout, on peut extraire juste la partie graphique
        if "thermal_profile" in self.results:
            self.update_thermal_graphs()

    def refresh_optimizer_tab(self):
        """Rafraîchit l'onglet Optimiseur."""
        # Si une optimisation était finie, on pourrait restaurer le tableau
        # Pour l'instant, on laisse vide ou on restaure si self.optim_results_list existe
        if hasattr(self, 'optim_results_list') and self.optim_results_list:
            for r in self.optim_results_list:
                # Recréer les lignes (simplifié)
                pass

    def update_thermal_graphs(self):
        """Met à jour uniquement les graphiques thermiques (helper pour refresh)."""
        if "thermal_profile" not in self.results: return
        
        profile = self.results["thermal_profile"]
        X_mm = profile["X_mm"]
        Flux_MW = profile["Flux_MW"]
        T_gas = profile["T_gas"]
        T_wall_hot = profile["T_wall_hot"]
        
        self.ax_flux.clear()
        self.ax_temp.clear()
        self.apply_dark_axes([self.ax_flux, self.ax_temp])
        
        self.ax_flux.plot(X_mm, Flux_MW, color=self.accent, label="Flux (MW/m²)")
        self.ax_flux.fill_between(X_mm, 0, Flux_MW, color=self.accent, alpha=0.1)
        self.ax_flux.set_ylabel("Flux Thermique (MW/m²)")
        self.ax_flux.legend(loc='upper right', facecolor=self.bg_surface, labelcolor=self.text_primary)
        self.ax_flux.grid(True, color=self.grid_color, alpha=0.35)
        
        self.ax_temp.plot(X_mm, T_gas, color=self.accent_alt, linestyle='--', alpha=0.7, label="Gaz (Adiabatique)")
        self.ax_temp.plot(X_mm, T_wall_hot, color="#ff4444", linewidth=2, label="Paroi (Côté Gaz)")
        self.ax_temp.set_ylabel("Température (K)")
        self.ax_temp.set_xlabel("Position Axiale (mm)")
        self.ax_temp.legend(loc='upper right', facecolor=self.bg_surface, labelcolor=self.text_primary)
        self.ax_temp.grid(True, color=self.grid_color, alpha=0.35)
        
        self.canvas_thermal.draw()

    def toggle_sidebar(self):
        """Affiche ou cache la barre latérale des paramètres."""
        if self.left_panel.winfo_viewable():
            self.left_panel.pack_forget()
            self.btn_toggle.configure(text="▶", fg_color=self.accent, text_color=self.bg_main)
        else:
            self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 10), pady=0)
            self.btn_toggle.configure(text="◀", fg_color="transparent", text_color=self.accent)

    def create_inputs(self, parent):
        row = 0
        ctk.CTkButton(
            parent, text="🔥 CALCULER TOUT (CEA + THERMIQUE)",
            command=self.run_simulation,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=35,
            fg_color=self.accent,
            hover_color=self.accent_alt,
            text_color=self.bg_main,
            corner_radius=8
        ).grid(row=row, column=0, columnspan=2, pady=8, padx=10, sticky="ew")

        row += 1

        # --- SÉLECTION MATÉRIAU GLOBAL ---
        ctk.CTkLabel(parent, text="🔩 Matériau Paroi:", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=self.accent).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))
        row += 1
        
        self.global_material_var = tk.StringVar(value="Cuivre-Zirconium (CuZr)")
        mat_combo = ctk.CTkComboBox(
            parent, variable=self.global_material_var, 
            values=list(self.materials_db.keys()),
            width=280,
            fg_color=self.bg_surface,
            border_color=self.border_color,
            button_color=self.accent,
            button_hover_color=self.accent_alt,
            dropdown_fg_color=self.bg_surface,
            dropdown_hover_color=self.accent,
            dropdown_text_color=self.text_primary,
            command=lambda x: self.on_global_material_change()
        )
        mat_combo.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        self.inputs["material_name"] = (self.global_material_var, str)
        row += 1

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
            ("Temp. Paroi Max (K)", "twall", 1000.0, float),
            ("Épaisseur Paroi (mm)", "wall_thickness", 2.0, float),
            ("Conductivité Paroi (W/m-K)", "wall_k", 340.0, float),
            ("Coolant (Auto=fuel)", "coolant_name", "Auto", str),
            ("Débit Coolant (Auto=fuel)", "coolant_mdot", "Auto", str),
            ("Coolant Pression (bar)", "coolant_pressure", 15.0, float),
            ("Coolant T entrée (K)", "coolant_tin", 293.0, float),
            ("Coolant T sortie max (K)", "coolant_tout", 350.0, float),
            ("Marge Sécurité Coolant (%)", "coolant_margin", 20.0, float),
            ("Custom Cp (J/kg-K)", "custom_cp", 2500.0, float),
            ("Custom T ébullition @1bar (K)", "custom_tboil", 350.0, float),
            ("Custom T critique (K)", "custom_tcrit", 500.0, float),
            ("Custom Hvap (kJ/kg)", "custom_hvap", 400.0, float),
        ]
        
        for label, key, default, type_ in self.param_defs:
            lbl = ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12), text_color=self.text_primary)
            lbl.grid(row=row, column=0, sticky="w", padx=10, pady=3)
            var = tk.StringVar(value=str(default))
            entry = ctk.CTkEntry(
                parent, textvariable=var, width=140,
                fg_color=self.bg_surface,
                border_color=self.border_color,
                text_color=self.text_primary,
                placeholder_text_color=self.text_muted
            )
            entry.grid(row=row, column=1, sticky="ew", padx=10, pady=3)
            self.inputs[key] = (var, type_)
            row += 1
        
        # Séparateur visuel
        separator = ctk.CTkFrame(parent, height=2, fg_color=self.accent)
        separator.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=15)
        row += 1
        
        # Bouton principal

        
        # Boutons secondaires
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        row += 1
        
        ctk.CTkButton(
            btn_frame, text="💾 Sauvegarder", command=self.save_design,
            width=130, height=35,
            fg_color=self.accent_alt,
            hover_color=self.accent,
            text_color=self.bg_main,
            corner_radius=6
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ctk.CTkButton(
            btn_frame, text="📂 Charger", command=self.load_design,
            width=130, height=35,
            fg_color=self.accent_alt2,
            hover_color=self.accent_alt3,
            text_color=self.bg_main,
            corner_radius=6
        ).pack(side=tk.LEFT, padx=5)
        
        # Export buttons
        export_frame = ctk.CTkFrame(parent, fg_color="transparent")
        export_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        row += 1
        
        ctk.CTkButton(
            export_frame, text="📐 Export DXF", command=self.export_dxf,
            width=130, height=35,
            fg_color=self.accent_alt3,
            hover_color=self.accent_alt2,
            text_color=self.bg_main,
            corner_radius=6
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ctk.CTkButton(
            export_frame, text="📊 Graphes HD", command=self.export_graphs_hd,
            width=130, height=35,
            fg_color=self.accent_alt4,
            hover_color=self.accent,
            text_color=self.bg_main,
            corner_radius=6
        ).pack(side=tk.LEFT, padx=5)
        
        # Bouton aide
        ctk.CTkButton(
            parent, text="ℹ️ Aide & Wiki",
            command=lambda: self.open_wiki_at("1. INTRODUCTION"),
            width=280, height=32,
            fg_color="transparent",
            border_width=1,
            border_color=self.accent,
            hover_color=self.bg_surface,
            text_color=self.accent,
            corner_radius=6
        ).grid(row=row, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

    def on_global_material_change(self, event=None):
        """Met à jour les champs de propriétés quand le matériau change."""
        mat_name = self.global_material_var.get()
        if mat_name in self.materials_db:
            props = self.materials_db[mat_name]
            # Mettre à jour Conductivité (wall_k)
            if "wall_k" in self.inputs:
                self.inputs["wall_k"][0].set(str(props["k"]))
            # Mettre à jour T max (twall) - on utilise T_max service par défaut
            if "twall" in self.inputs:
                self.inputs["twall"][0].set(str(props["T_max"]))
            
            # Mettre à jour les sélections dans les autres onglets si possible
            if hasattr(self, 'solver_material'):
                try:
                    self.solver_material.set(mat_name)
                    self.update_material_info()
                except:
                    pass
            
            if hasattr(self, 'stress_material'):
                try:
                    self.stress_material.set(mat_name)
                    self.update_material_properties()
                except:
                    pass
            
            if hasattr(self, 'optim_mat_combo'):
                try:
                    self.optim_mat_combo.set(mat_name)
                    # Trigger update manually if needed
                    # self.optim_mat_combo.event_generate("<<ComboboxSelected>>") 
                except:
                    pass

    def get_val(self, key):
        var, type_ = self.inputs[key]
        return type_(var.get())

    # --- TABS INIT ---
    def init_summary_tab(self):
        """Onglet Résumé - Affiche les résultats des calculs"""
        # Barre d'accent en haut
        accent_bar = ctk.CTkFrame(self.tab_summary, height=4, fg_color=self.tab_accent.get("summary", self.accent))
        accent_bar.pack(fill=tk.X)
        
        summary_frame = ctk.CTkFrame(self.tab_summary, fg_color=self.bg_panel, corner_radius=10)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        fs = self.scaled_font_size(13)
        fs_title = self.scaled_font_size(16)
        
        # Utiliser tk.Text pour garder les tags de couleur (encapsulé dans CTkFrame)
        text_container = ctk.CTkFrame(summary_frame, fg_color=self.bg_surface, corner_radius=8)
        text_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.txt_summary = tk.Text(
            text_container,
            bg=self.bg_surface,
            fg=self.text_primary,
            insertbackground=self.accent,
            font=(MONOSPACE_FONT, fs),
            highlightthickness=0,
            bd=0,
            wrap=tk.WORD,
            padx=15,
            pady=10,
            relief=tk.FLAT,  # Style plat moderne
            selectbackground=self.accent,  # Couleur de sélection
            selectforeground=self.bg_main,  # Texte sélectionné
        )
        self.txt_summary.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # === TAGS DE COULEUR STYLE ÉDITEUR DE CODE ===
        self.txt_summary.tag_configure("title", foreground="#ff79c6", font=("Consolas", fs_title, "bold"))
        self.txt_summary.tag_configure("section", foreground="#ffb86c", font=("Consolas", fs, "bold"))
        self.txt_summary.tag_configure("label", foreground="#8be9fd")
        self.txt_summary.tag_configure("number", foreground="#bd93f9")
        self.txt_summary.tag_configure("unit", foreground="#6272a4")
        self.txt_summary.tag_configure("string", foreground="#f1fa8c")
        self.txt_summary.tag_configure("success", foreground="#50fa7b")
        self.txt_summary.tag_configure("warning", foreground="#ffb347")
        self.txt_summary.tag_configure("error", foreground="#ff5555")
        self.txt_summary.tag_configure("separator", foreground="#44475a")
        self.txt_summary.tag_configure("symbol", foreground="#ff79c6")
        
        # Scrollbar moderne
        scrollbar = ctk.CTkScrollbar(text_container, command=self.txt_summary.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)
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



    def init_cea_tab(self):
        # Barre d'accent
        accent_bar = ctk.CTkFrame(self.tab_cea, height=4, fg_color=self.tab_accent.get("cea", self.accent_alt2))
        accent_bar.pack(fill=tk.X)
        
        # Toolbar modernisée
        cea_toolbar = ctk.CTkFrame(self.tab_cea, fg_color="transparent")
        cea_toolbar.pack(fill=tk.X, pady=(10, 5), padx=10)
        
        ctk.CTkLabel(cea_toolbar, text="Sortie NASA CEA (Brut)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.accent).pack(side=tk.LEFT)
        
        ctk.CTkButton(cea_toolbar, text="📖 Aide Chimie", width=120, height=30,
                      fg_color="transparent", border_width=1, border_color=self.accent,
                      hover_color=self.bg_surface, text_color=self.accent,
                      command=lambda: self.open_wiki_at("5. CHIMIE DE COMBUSTION")).pack(side=tk.RIGHT)
        
        fs = self.scaled_font_size(13)
        
        # Container pour le texte
        text_container = ctk.CTkFrame(self.tab_cea, fg_color=self.bg_surface, corner_radius=8)
        text_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.txt_cea = scrolledtext.ScrolledText(
            text_container,
            font=(MONOSPACE_FONT, fs),
            state='disabled',
            bg=self.bg_surface,
            fg=self.text_primary,
            insertbackground=self.accent,
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,  # Style plat moderne
            selectbackground=self.accent,
            selectforeground=self.bg_main,
            padx=10,
            pady=10,
        )
        self.txt_cea.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Tags de coloration CEA style éditeur de code
        self.txt_cea.tag_configure("cea_header", foreground="#ff79c6", font=("Consolas", fs, "bold"))
        self.txt_cea.tag_configure("cea_section", foreground="#ffb86c")
        self.txt_cea.tag_configure("cea_property", foreground="#8be9fd")
        self.txt_cea.tag_configure("cea_value", foreground="#bd93f9")
        self.txt_cea.tag_configure("cea_unit", foreground="#6272a4")
        self.txt_cea.tag_configure("cea_species", foreground="#50fa7b")
        self.txt_cea.tag_configure("cea_comment", foreground="#6272a4", font=("Consolas", fs, "italic"))
        
    def init_thermal_tab(self):
        # Barre d'accent
        accent_bar = ctk.CTkFrame(self.tab_thermal, height=4, fg_color=self.tab_accent.get("thermal", self.accent_alt))
        accent_bar.pack(fill=tk.X)
        
        # Toolbar modernisée
        thermal_toolbar = ctk.CTkFrame(self.tab_thermal, fg_color="transparent")
        thermal_toolbar.pack(fill=tk.X, pady=(10, 5), padx=10)
        
        ctk.CTkLabel(thermal_toolbar, text="Graphiques : Flux & Température",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.accent_alt).pack(side=tk.LEFT)
        
        ctk.CTkButton(thermal_toolbar, text="📖 Aide Thermique", width=130, height=30,
                      fg_color="transparent", border_width=1, border_color=self.accent_alt,
                      hover_color=self.bg_surface, text_color=self.accent_alt,
                      command=lambda: self.open_wiki_at("6. TRANSFERT THERMIQUE")).pack(side=tk.RIGHT)
        
        # Container pour le graphique
        graph_container = ctk.CTkFrame(self.tab_thermal, fg_color=self.bg_panel, corner_radius=10)
        graph_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.fig_thermal, (self.ax_flux, self.ax_temp) = plt.subplots(2, 1, figsize=(6, 6), sharex=True)
        self.fig_thermal.patch.set_facecolor(self.bg_main)
        self.fig_thermal.subplots_adjust(hspace=0.35, left=0.12, right=0.95, top=0.95, bottom=0.1)
        for ax in [self.ax_flux, self.ax_temp]:
            ax.set_facecolor(self.bg_surface)
        self.apply_dark_axes([self.ax_flux, self.ax_temp])
        self.canvas_thermal = FigureCanvasTkAgg(self.fig_thermal, master=graph_container)
        self.canvas_thermal.get_tk_widget().configure(bg=self.bg_main, highlightthickness=0)
        self.canvas_thermal.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def init_heatmap_tab(self):
        """Initialise l'onglet Carte Thermique 2D avec visualisation colorée."""
        # Barre d'accent
        accent_bar = ctk.CTkFrame(self.tab_heatmap, height=4, fg_color="#ff6b35")
        accent_bar.pack(fill=tk.X)
        
        # Frame de contrôles modernisée (compacte)
        ctrl_frame = ctk.CTkFrame(self.tab_heatmap, fg_color=self.bg_panel, corner_radius=10)
        ctrl_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5, 5))
        
        # Titre (plus compact)
        header = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        header.pack(fill=tk.X, padx=10, pady=(5, 3))
        
        ctk.CTkLabel(header, text="🔥 Carte Thermique 2D",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color="#ff6b35").pack(side=tk.LEFT)
        
        ctk.CTkButton(header, text="🖼️ Ouvrir Visualisation", 
                      fg_color=self.accent_alt3, hover_color="#ff8c42", text_color=self.bg_main,
                      font=ctk.CTkFont(size=11, weight="bold"),
                      command=self.visualize_heatmap_in_window,
                      width=180, height=28).pack(side=tk.RIGHT, padx=5)
        
        ctk.CTkButton(header, text="📖", width=40, height=24,
                      fg_color="transparent", border_width=1, border_color=self.accent,
                      hover_color=self.bg_surface, text_color=self.accent,
                      command=lambda: self.open_wiki_at("23. CARTE THERMIQUE")).pack(side=tk.RIGHT, padx=2)
        
        # Ligne 1: Options de visualisation
        row1 = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        row1.pack(fill=tk.X, pady=10, padx=10)
        
        ctk.CTkLabel(row1, text="Mode:", text_color=self.text_primary).pack(side=tk.LEFT, padx=(0, 10))
        self.heatmap_mode = tk.StringVar(value="coupe_radiale")
        modes = [("Coupe Radiale", "coupe_radiale"), ("Développée", "developpee"), ("3D Surface", "surface_3d")]
        for text, mode in modes:
            ctk.CTkRadioButton(row1, text=text, variable=self.heatmap_mode, value=mode,
                               fg_color=self.accent, hover_color=self.accent_alt,
                               command=self.update_heatmap).pack(side=tk.LEFT, padx=8)
        
        # Séparateur vertical
        # Pour le premier séparateur (row1)
        sep1 = ctk.CTkFrame(row1, width=2, height=16, fg_color=self.border_color) # On définit une hauteur fixe
        sep1.pack(side=tk.LEFT, padx=15) # SURTOUT PAS de fill=tk.Y ici
        
        ctk.CTkLabel(row1, text="Colormap:", text_color=self.text_primary).pack(side=tk.LEFT, padx=(0, 5))
        self.heatmap_cmap_var = tk.StringVar(value="inferno")
        self.heatmap_cmap = ctk.CTkComboBox(row1, values=["inferno", "plasma", "hot", "jet", "coolwarm", "magma", "viridis"],
                                             variable=self.heatmap_cmap_var, width=100,
                                             fg_color=self.bg_surface, border_color=self.border_color,
                                             button_color=self.accent, button_hover_color=self.accent_alt,
                                             command=lambda x: self.update_heatmap())
        self.heatmap_cmap.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(row1, text="Résolution:", text_color=self.text_primary).pack(side=tk.LEFT, padx=(15, 5))
        self.heatmap_resolution_var = tk.StringVar(value="50")
        self.heatmap_resolution = ctk.CTkEntry(row1, textvariable=self.heatmap_resolution_var, width=50,
                                                fg_color=self.bg_surface, border_color=self.border_color)
        self.heatmap_resolution.pack(side=tk.LEFT)
        
        # Ligne 2: Options supplémentaires
        row2 = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        row2.pack(fill=tk.X, pady=5, padx=10)
        
        self.heatmap_show_isotherms = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(row2, text="Isothermes", variable=self.heatmap_show_isotherms,
                        fg_color=self.accent, hover_color=self.accent_alt,
                        command=self.update_heatmap).pack(side=tk.LEFT, padx=10)
        
        self.heatmap_show_limits = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(row2, text="Limites matériau", variable=self.heatmap_show_limits,
                        fg_color=self.accent, hover_color=self.accent_alt,
                        command=self.update_heatmap).pack(side=tk.LEFT, padx=10)
        
        self.heatmap_show_flux = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(row2, text="Vecteurs flux", variable=self.heatmap_show_flux,
                        fg_color=self.accent, hover_color=self.accent_alt,
                        command=self.update_heatmap).pack(side=tk.LEFT, padx=10)
        
        self.heatmap_show_channels = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(row2, text="Canaux coolant", variable=self.heatmap_show_channels,
                        fg_color=self.accent, hover_color=self.accent_alt,
                        command=self.update_heatmap).pack(side=tk.LEFT, padx=10)
        
        # Séparateur
        sep2 = ctk.CTkFrame(row2, width=2, height=16, fg_color=self.border_color)
        sep2.pack(side=tk.LEFT, padx=15)
        
        ctk.CTkLabel(row2, text="Position X (mm):", text_color=self.text_primary).pack(side=tk.LEFT, padx=(0, 5))
        self.heatmap_x_pos = ctk.CTkSlider(row2, from_=-100, to=200, width=150,
                                            fg_color=self.bg_surface, progress_color=self.accent,
                                            button_color=self.accent, button_hover_color=self.accent_alt,
                                            command=lambda v: self.update_heatmap())
        self.heatmap_x_pos.set(0)
        self.heatmap_x_pos.pack(side=tk.LEFT, padx=5)
        self.heatmap_x_label = ctk.CTkLabel(row2, text="0.0 mm", text_color=self.accent)
        self.heatmap_x_label.pack(side=tk.LEFT)
        
        # Bouton refresh
        ctk.CTkButton(row2, text="🔄", width=40, height=24,
                      fg_color=self.accent, hover_color=self.accent_alt, text_color=self.bg_main,
                      command=self.update_heatmap).pack(side=tk.RIGHT, padx=2)
        
        # Ligne 3: Informations thermiques en temps réel (compactée)
        info_frame = ctk.CTkFrame(ctrl_frame, fg_color=self.bg_surface, corner_radius=8)
        info_frame.pack(fill=tk.X, pady=(5, 10), padx=10)
        
        info_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_row.pack(fill=tk.X, padx=5, pady=3)
        
        self.heatmap_info_labels = {}
        info_items = [("T_gaz", "T gaz:"), ("T_hot", "T hot:"), ("T_cold", "T cold:"), 
                      ("T_cool", "T cool:"), ("flux", "Flux:"), ("hg", "h_g:")]
        for key, text in info_items:
            ctk.CTkLabel(info_row, text=text, text_color=self.text_muted, 
                        font=ctk.CTkFont(size=10)).pack(side=tk.LEFT, padx=(5, 1))
            lbl = ctk.CTkLabel(info_row, text="-", text_color=self.accent,
                              font=ctk.CTkFont(size=10))
            lbl.pack(side=tk.LEFT, padx=(0, 8))
            self.heatmap_info_labels[key] = lbl
        
        # Données stockées pour interaction
        self.heatmap_data = None
        self.heatmap_window = None  # Référence à la fenêtre de visualisation

    def update_heatmap(self):
        """Met à jour la carte thermique 2D - met à jour la fenêtre si elle est ouverte."""
        # Mettre à jour la fenêtre si elle est ouverte
        if hasattr(self, 'heatmap_window') and self.heatmap_window is not None:
            # Créer une variable temporaire pour le mode
            mode_var = tk.StringVar(value=self.heatmap_mode.get())
            self.update_heatmap_window(mode_var)

    def draw_heatmap_radial_cut(self):
        """Dessine la carte thermique en coupe radiale à une position X donnée."""
        # Nettoyer complètement la figure
        self.fig_heatmap.clear()
        self.ax_heatmap = self.fig_heatmap.add_subplot(111)
        self.ax_heatmap.set_facecolor(self.bg_surface)
        
        profile = self.results["thermal_profile"]
        X_mm = np.array(profile["X_mm"])
        Y_mm = np.array(profile["Y_mm"])
        T_gas = np.array(profile["T_gas"])
        T_wall_hot = np.array(profile["T_wall_hot"])
        T_wall_cold = profile["T_wall_cold"]
        Flux_MW = np.array(profile["Flux_MW"])
        
        # Position X sélectionnée
        x_pos = float(self.heatmap_x_pos.get())
        self.heatmap_x_label.configure(text=f"{x_pos:.1f} mm")
        
        # Trouver l'index le plus proche
        idx = np.argmin(np.abs(X_mm - x_pos))
        
        # Données à cette position
        r_inner = Y_mm[idx]  # Rayon intérieur (côté gaz)
        wall_thickness = self.results.get("wall_thickness_mm", 3.0)
        r_outer = r_inner + wall_thickness  # Rayon extérieur (côté coolant)
        
        t_gas_local = T_gas[idx]
        t_hot_local = T_wall_hot[idx]
        t_cold_local = T_wall_cold if isinstance(T_wall_cold, (int, float)) else T_wall_cold
        flux_local = Flux_MW[idx]
        
        # Température coolant (estimation)
        t_coolant = self.get_val("coolant_tin") if self.get_val("coolant_tin") else 300
        
        # Créer une grille pour la visualisation
        n_theta = int(self.heatmap_resolution_var.get())
        n_r = 30  # Nombre de points dans l'épaisseur
        
        theta = np.linspace(0, 2*np.pi, n_theta)
        r = np.linspace(r_inner, r_outer, n_r)
        
        THETA, R = np.meshgrid(theta, r)
        X = R * np.cos(THETA)
        Y = R * np.sin(THETA)
        
        # Interpolation linéaire de la température dans l'épaisseur
        # T(r) = T_hot + (T_cold - T_hot) * (r - r_inner) / wall_thickness
        T = t_hot_local + (t_cold_local - t_hot_local) * (R - r_inner) / wall_thickness
        
        # Tracer la carte de couleur
        cmap = self.heatmap_cmap_var.get()
        levels = np.linspace(t_cold_local - 50, t_hot_local + 50, 50)
        
        contour = self.ax_heatmap.contourf(X, Y, T, levels=levels, cmap=cmap, extend='both')
        
        # Barre de couleur
        cbar = self.fig_heatmap.colorbar(contour, ax=self.ax_heatmap, label='Température (K)', pad=0.02)
        cbar.ax.yaxis.label.set_color(self.text_primary)
        cbar.ax.tick_params(colors=self.text_primary)
        
        # Isothermes
        if self.heatmap_show_isotherms.get():
            iso_levels = np.linspace(t_cold_local, t_hot_local, 8)
            iso = self.ax_heatmap.contour(X, Y, T, levels=iso_levels, colors='white', linewidths=0.5, alpha=0.7)
            self.ax_heatmap.clabel(iso, inline=True, fontsize=8, fmt='%.0f K', colors='white')
        
        # Limites du matériau
        if self.heatmap_show_limits.get():
            # Cercle de limite de température
            wall_k = self.get_val("wall_k") if self.get_val("wall_k") else 320
            t_limit = self.get_val("twall") if self.get_val("twall") else 1000
            
            # Trouver le rayon où T = T_limit (si applicable)
            if t_hot_local > t_limit:
                r_limit = r_inner + (t_limit - t_hot_local) / (t_cold_local - t_hot_local) * wall_thickness
                if r_inner < r_limit < r_outer:
                    circle_limit = plt.Circle((0, 0), r_limit, fill=False, color='red', 
                                              linewidth=2, label=f'T_limite ({t_limit:.0f} K)')
                    self.ax_heatmap.add_patch(circle_limit)
        
        # Canaux de refroidissement (représentation schématique)
        if self.heatmap_show_channels.get():
            n_channels = 40  # Nombre de canaux (exemple)
            channel_width = 2  # mm
            for i in range(n_channels):
                angle = 2 * np.pi * i / n_channels
                # Rectangle représentant un canal
                x_ch = r_outer * np.cos(angle)
                y_ch = r_outer * np.sin(angle)
                self.ax_heatmap.plot(x_ch, y_ch, 's', color=self.accent, markersize=4, alpha=0.8)
        
        # Cercles de référence
        circle_inner = plt.Circle((0, 0), r_inner, fill=False, color=self.accent, linewidth=1.5, linestyle='-')
        circle_outer = plt.Circle((0, 0), r_outer, fill=False, color='#00ff88', linewidth=1.5, linestyle='-')
        self.ax_heatmap.add_patch(circle_inner)
        self.ax_heatmap.add_patch(circle_outer)
        
        # Zone gaz (intérieur)
        gas_circle = plt.Circle((0, 0), r_inner * 0.98, color='#ff4444', alpha=0.15)
        self.ax_heatmap.add_patch(gas_circle)
        self.ax_heatmap.text(0, 0, f'GAZ\n{t_gas_local:.0f} K', ha='center', va='center', 
                            fontsize=10, color='#ff6666', fontweight='bold')
        
        # Annotations
        self.ax_heatmap.annotate(f'T_hot = {t_hot_local:.0f} K', xy=(r_inner, 0), xytext=(r_inner + wall_thickness/4, wall_thickness),
                                fontsize=9, color='yellow', ha='center',
                                arrowprops=dict(color='yellow', lw=0.5))
        self.ax_heatmap.annotate(f'T_cold = {t_cold_local:.0f} K', xy=(r_outer, 0), xytext=(r_outer + 5, -wall_thickness),
                                fontsize=9, color='#00ff88', ha='center',
                                arrowprops=dict(color='#00ff88', lw=0.5))
        
        # Configuration des axes
        max_r = r_outer * 1.3
        self.ax_heatmap.set_xlim(-max_r, max_r)
        self.ax_heatmap.set_ylim(-max_r, max_r)
        self.ax_heatmap.set_aspect('equal')
        self.ax_heatmap.set_xlabel('Position (mm)', color=self.text_primary)
        self.ax_heatmap.set_ylabel('Position (mm)', color=self.text_primary)
        
        # Titre avec infos
        region = "Chambre" if x_pos < -self.results.get('lc', 0) else ("Col" if abs(x_pos) < 5 else "Divergent")
        self.ax_heatmap.set_title(f'Coupe Radiale @ X = {x_pos:.1f} mm ({region}) | Flux = {flux_local:.2f} MW/m²',
                                  color=self.text_primary, fontsize=12, fontweight='bold')
        
        self.apply_dark_axes([self.ax_heatmap])
        self.fig_heatmap.tight_layout()
        
        # Stocker les données pour interaction
        self.heatmap_data = {
            "x_pos": x_pos, "r_inner": r_inner, "r_outer": r_outer,
            "t_gas": t_gas_local, "t_hot": t_hot_local, "t_cold": t_cold_local,
            "flux": flux_local, "t_coolant": t_coolant
        }
        
        # Mettre à jour les labels d'info
        self.update_heatmap_info(x_pos, t_gas_local, t_hot_local, t_cold_local, t_coolant, flux_local)

    def draw_heatmap_developed(self):
        """Dessine la carte thermique développée (X vs épaisseur)."""
        self.fig_heatmap.clear()
        self.ax_heatmap = self.fig_heatmap.add_subplot(111)
        self.ax_heatmap.set_facecolor(self.bg_surface)
        
        profile = self.results["thermal_profile"]
        X_mm = np.array(profile["X_mm"])
        Y_mm = np.array(profile["Y_mm"])
        T_gas = np.array(profile["T_gas"])
        T_wall_hot = np.array(profile["T_wall_hot"])
        T_wall_cold = profile["T_wall_cold"]
        Flux_MW = np.array(profile["Flux_MW"])
        
        wall_thickness = self.results.get("wall_thickness_mm", 3.0)
        n_depth = 30  # Points dans l'épaisseur
        
        # Créer la grille 2D (X, profondeur)
        depth = np.linspace(0, wall_thickness, n_depth)  # 0 = côté gaz, wall_thickness = côté coolant
        
        X_grid, D_grid = np.meshgrid(X_mm, depth)
        
        # Température en fonction de X et de la profondeur
        # T(x, d) = T_hot(x) + (T_cold - T_hot(x)) * d / wall_thickness
        T_grid = np.zeros_like(X_grid)
        for i, x in enumerate(X_mm):
            t_hot = T_wall_hot[i]
            t_cold = T_wall_cold if isinstance(T_wall_cold, (int, float)) else T_wall_cold
            for j, d in enumerate(depth):
                T_grid[j, i] = t_hot + (t_cold - t_hot) * d / wall_thickness
        
        # Tracer
        cmap = self.heatmap_cmap_var.get()
        t_min = min(T_wall_cold if isinstance(T_wall_cold, (int, float)) else min(T_wall_cold), min(T_wall_hot)) - 50
        t_max = max(T_wall_hot) + 100
        levels = np.linspace(t_min, t_max, 50)
        
        contour = self.ax_heatmap.contourf(X_grid, D_grid, T_grid, levels=levels, cmap=cmap, extend='both')
        
        cbar = self.fig_heatmap.colorbar(contour, ax=self.ax_heatmap, label='Température (K)', pad=0.02)
        cbar.ax.yaxis.label.set_color(self.text_primary)
        cbar.ax.tick_params(colors=self.text_primary)
        
        # Isothermes
        if self.heatmap_show_isotherms.get():
            iso_levels = np.linspace(t_min + 100, t_max - 100, 10)
            iso = self.ax_heatmap.contour(X_grid, D_grid, T_grid, levels=iso_levels, 
                                          colors='white', linewidths=0.5, alpha=0.7)
            self.ax_heatmap.clabel(iso, inline=True, fontsize=7, fmt='%.0f K', colors='white')
        
        # Limites du matériau
        if self.heatmap_show_limits.get():
            t_limit = self.get_val("twall") if self.get_val("twall") else 1000
            # Contour de la limite
            limit_contour = self.ax_heatmap.contour(X_grid, D_grid, T_grid, levels=[t_limit], 
                                                     colors=['red'], linewidths=2, linestyles='--')
            # Matplotlib 3.8+: utiliser allsegs au lieu de collections
            if hasattr(limit_contour, 'allsegs') and any(len(seg) > 0 for seg in limit_contour.allsegs):
                self.ax_heatmap.clabel(limit_contour, inline=True, fontsize=9, fmt=f'T_limite = {t_limit:.0f} K', colors='red')
        
        # Ligne du profil (forme de la tuyère) - juste pour référence
        self.ax_heatmap.axhline(y=0, color=self.accent, linewidth=1.5, label='Côté gaz')
        self.ax_heatmap.axhline(y=wall_thickness, color='#00ff88', linewidth=1.5, label='Côté coolant')
        
        # Marquer le col
        self.ax_heatmap.axvline(x=0, color='white', linewidth=1, alpha=0.5)
        self.ax_heatmap.text(0, wall_thickness * 1.05, 'Col', ha='center', color='white', fontsize=9)
        
        # Ajouter le profil de flux en haut
        ax_flux = self.ax_heatmap.twinx()
        ax_flux.fill_between(X_mm, 0, Flux_MW, alpha=0.2, color='red')
        ax_flux.plot(X_mm, Flux_MW, 'r-', linewidth=1, alpha=0.6)
        ax_flux.set_ylabel('Flux (MW/m²)', color='red')
        ax_flux.tick_params(axis='y', colors='red')
        ax_flux.set_ylim(0, max(Flux_MW) * 3)
        
        self.ax_heatmap.set_xlabel('Position axiale X (mm)', color=self.text_primary)
        self.ax_heatmap.set_ylabel('Profondeur dans la paroi (mm)', color=self.text_primary)
        self.ax_heatmap.set_title('Carte Thermique Développée - Température dans la paroi', 
                                  color=self.text_primary, fontsize=12, fontweight='bold')
        
        self.ax_heatmap.legend(loc='upper right', fontsize=8)
        self.apply_dark_axes([self.ax_heatmap])
        self.fig_heatmap.tight_layout()

    def draw_heatmap_3d_surface(self):
        """Dessine une surface 3D de la température sur la tuyère."""
        from mpl_toolkits.mplot3d import Axes3D
        
        # Nettoyer complètement la figure
        self.fig_heatmap.clear()
        self.ax_heatmap = self.fig_heatmap.add_subplot(111, projection='3d')
        
        profile = self.results["thermal_profile"]
        X_mm = np.array(profile["X_mm"])
        Y_mm = np.array(profile["Y_mm"])
        T_wall_hot = np.array(profile["T_wall_hot"])
        
        # Créer la surface de révolution
        n_theta = int(self.heatmap_resolution_var.get())
        theta = np.linspace(0, 2*np.pi, n_theta)
        
        THETA, X = np.meshgrid(theta, X_mm)
        R = np.tile(Y_mm.reshape(-1, 1), (1, n_theta))
        T = np.tile(T_wall_hot.reshape(-1, 1), (1, n_theta))
        
        Y_3d = R * np.cos(THETA)
        Z_3d = R * np.sin(THETA)
        
        # Normaliser les températures pour le colormap
        cmap = self.heatmap_cmap_var.get()
        norm = plt.Normalize(vmin=min(T_wall_hot), vmax=max(T_wall_hot))
        
        # Matplotlib 3.7+: utiliser plt.colormaps.get_cmap() au lieu de plt.cm.get_cmap()
        colormap = plt.colormaps.get_cmap(cmap) if hasattr(plt, 'colormaps') else plt.cm.get_cmap(cmap)
        surf = self.ax_heatmap.plot_surface(X, Y_3d, Z_3d, facecolors=colormap(norm(T)),
                                             shade=True, alpha=0.9, antialiased=True)
        
        # Barre de couleur
        mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array(T)
        cbar = self.fig_heatmap.colorbar(mappable, ax=self.ax_heatmap, label='T paroi hot (K)', 
                                          shrink=0.6, pad=0.1)
        cbar.ax.yaxis.label.set_color(self.text_primary)
        cbar.ax.tick_params(colors=self.text_primary)
        
        # Configuration 3D améliorée
        self.ax_heatmap.set_xlabel('X (mm)', color=self.text_primary, labelpad=12)
        self.ax_heatmap.set_ylabel('Y (mm)', color=self.text_primary, labelpad=12)
        self.ax_heatmap.set_zlabel('Z (mm)', color=self.text_primary, labelpad=12)
        self.ax_heatmap.set_title('Surface 3D - Température paroi côté gaz', 
                                  color=self.text_primary, fontsize=13, fontweight='bold', pad=20)
        
        # Style sombre pour 3D amélioré
        self.ax_heatmap.set_facecolor(self.bg_surface)
        self.ax_heatmap.xaxis.pane.fill = False
        self.ax_heatmap.yaxis.pane.fill = False
        self.ax_heatmap.zaxis.pane.fill = False
        self.ax_heatmap.xaxis.pane.set_edgecolor(self.grid_color)
        self.ax_heatmap.yaxis.pane.set_edgecolor(self.grid_color)
        self.ax_heatmap.zaxis.pane.set_edgecolor(self.grid_color)
        self.ax_heatmap.xaxis.pane.set_alpha(0.05)
        self.ax_heatmap.yaxis.pane.set_alpha(0.05)
        self.ax_heatmap.zaxis.pane.set_alpha(0.05)
        self.ax_heatmap.tick_params(colors=self.text_primary, labelsize=9)
        
        # Grille améliorée
        self.ax_heatmap.grid(True, color=self.grid_color, alpha=0.3, linestyle='--', linewidth=0.5)
        
        # Vue 3D optimisée
        self.ax_heatmap.view_init(elev=20, azim=45)
        
        self.fig_heatmap.tight_layout()

    def update_heatmap_info(self, x_pos, t_gas, t_hot, t_cold, t_coolant, flux):
        """Met à jour les labels d'information de la carte thermique."""
        hg = profile["hg_throat"] if "hg_throat" in (profile := self.results.get("thermal_profile", {})) else 0
        
        self.heatmap_info_labels["T_gaz"].configure(text=f"{t_gas:.0f} K")
        self.heatmap_info_labels["T_hot"].configure(text=f"{t_hot:.0f} K")
        self.heatmap_info_labels["T_cold"].configure(text=f"{t_cold:.0f} K")
        self.heatmap_info_labels["T_cool"].configure(text=f"{t_coolant:.0f} K")
        self.heatmap_info_labels["flux"].configure(text=f"{flux:.2f} MW/m²")
        self.heatmap_info_labels["hg"].configure(text=f"{hg:.0f} W/m²K")

    def on_heatmap_hover(self, event):
        """Gère le survol de la carte thermique pour afficher les infos."""
        if event.inaxes != self.ax_heatmap or self.heatmap_data is None:
            return
        
        # En mode coupe radiale, calculer la température à partir de la position
        if self.heatmap_mode.get() == "coupe_radiale":
            x, y = event.xdata, event.ydata
            r = np.sqrt(x**2 + y**2)
            data = self.heatmap_data
            
            if data["r_inner"] <= r <= data["r_outer"]:
                # Interpoler la température
                wall_thickness = data["r_outer"] - data["r_inner"]
                depth = r - data["r_inner"]
                t_local = data["t_hot"] + (data["t_cold"] - data["t_hot"]) * depth / wall_thickness
                
                # Mettre à jour le titre avec l'info
                self.ax_heatmap.set_title(
                    f'Coupe @ X={data["x_pos"]:.1f}mm | r={r:.1f}mm | T={t_local:.0f}K | Flux={data["flux"]:.2f}MW/m²',
                    color=self.text_primary, fontsize=11
                )
                self.canvas_heatmap.draw_idle()

    def on_heatmap_click(self, event):
        """Gère le clic sur la carte thermique."""
        # Pourrait être étendu pour sélectionner un point et afficher plus de détails
        pass

    def draw_heatmap_radial_cut_in_window(self, ax, fig, canvas):
        """Dessine la carte thermique en coupe radiale dans la fenêtre."""
        profile = self.results["thermal_profile"]
        X_mm = np.array(profile["X_mm"])
        Y_mm = np.array(profile["Y_mm"])
        T_gas = np.array(profile["T_gas"])
        T_wall_hot = np.array(profile["T_wall_hot"])
        T_wall_cold = profile["T_wall_cold"]
        Flux_MW = np.array(profile["Flux_MW"])
        
        # Position X sélectionnée (depuis l'onglet principal)
        x_pos = float(self.heatmap_x_pos.get())
        self.heatmap_x_label.configure(text=f"{x_pos:.1f} mm")
        
        # Trouver l'index le plus proche
        idx = np.argmin(np.abs(X_mm - x_pos))
        
        # Données à cette position
        r_inner = Y_mm[idx]
        wall_thickness = self.results.get("wall_thickness_mm", 3.0)
        r_outer = r_inner + wall_thickness
        
        t_gas_local = T_gas[idx]
        t_hot_local = T_wall_hot[idx]
        t_cold_local = T_wall_cold if isinstance(T_wall_cold, (int, float)) else T_wall_cold
        flux_local = Flux_MW[idx]
        t_coolant = self.get_val("coolant_tin") if self.get_val("coolant_tin") else 300
        
        # Créer une grille pour la visualisation
        n_theta = int(self.heatmap_resolution_var.get())
        n_r = 30
        
        theta = np.linspace(0, 2*np.pi, n_theta)
        r = np.linspace(r_inner, r_outer, n_r)
        
        THETA, R = np.meshgrid(theta, r)
        X = R * np.cos(THETA)
        Y = R * np.sin(THETA)
        
        T = t_hot_local + (t_cold_local - t_hot_local) * (R - r_inner) / wall_thickness
        
        # Tracer la carte de couleur
        cmap = self.heatmap_cmap_var.get()
        levels = np.linspace(t_cold_local - 50, t_hot_local + 50, 50)
        
        contour = ax.contourf(X, Y, T, levels=levels, cmap=cmap, extend='both')
        
        # Barre de couleur
        cbar = fig.colorbar(contour, ax=ax, label='Température (K)', pad=0.02)
        cbar.ax.yaxis.label.set_color(self.text_primary)
        cbar.ax.tick_params(colors=self.text_primary)
        
        # Isothermes
        if self.heatmap_show_isotherms.get():
            iso_levels = np.linspace(t_cold_local, t_hot_local, 8)
            iso = ax.contour(X, Y, T, levels=iso_levels, colors='white', linewidths=0.5, alpha=0.7)
            ax.clabel(iso, inline=True, fontsize=8, fmt='%.0f K', colors='white')
        
        # Limites du matériau
        if self.heatmap_show_limits.get():
            t_limit = self.get_val("twall") if self.get_val("twall") else 1000
            if t_hot_local > t_limit:
                r_limit = r_inner + (t_limit - t_hot_local) / (t_cold_local - t_hot_local) * wall_thickness
                if r_inner < r_limit < r_outer:
                    circle_limit = plt.Circle((0, 0), r_limit, fill=False, color='red', 
                                              linewidth=2, label=f'T_limite ({t_limit:.0f} K)')
                    ax.add_patch(circle_limit)
        
        # Canaux de refroidissement
        if self.heatmap_show_channels.get():
            n_channels = 40
            for i in range(n_channels):
                angle = 2 * np.pi * i / n_channels
                x_ch = r_outer * np.cos(angle)
                y_ch = r_outer * np.sin(angle)
                ax.plot(x_ch, y_ch, 's', color=self.accent, markersize=4, alpha=0.8)
        
        # Cercles de référence
        circle_inner = plt.Circle((0, 0), r_inner, fill=False, color=self.accent, linewidth=1.5, linestyle='-')
        circle_outer = plt.Circle((0, 0), r_outer, fill=False, color='#00ff88', linewidth=1.5, linestyle='-')
        ax.add_patch(circle_inner)
        ax.add_patch(circle_outer)
        
        # Zone gaz
        gas_circle = plt.Circle((0, 0), r_inner * 0.98, color='#ff4444', alpha=0.15)
        ax.add_patch(gas_circle)
        ax.text(0, 0, f'GAZ\n{t_gas_local:.0f} K', ha='center', va='center', 
                fontsize=10, color='#ff6666', fontweight='bold')
        
        # Annotations
        ax.annotate(f'T_hot = {t_hot_local:.0f} K', xy=(r_inner, 0), xytext=(r_inner + wall_thickness/4, wall_thickness),
                    fontsize=9, color='yellow', ha='center',
                    arrowprops=dict(color='yellow', lw=0.5))
        ax.annotate(f'T_cold = {t_cold_local:.0f} K', xy=(r_outer, 0), xytext=(r_outer + 5, -wall_thickness),
                    fontsize=9, color='#00ff88', ha='center',
                    arrowprops=dict(color='#00ff88', lw=0.5))
        
        # Configuration des axes
        max_r = r_outer * 1.3
        ax.set_xlim(-max_r, max_r)
        ax.set_ylim(-max_r, max_r)
        ax.set_aspect('equal')
        ax.set_xlabel('Position (mm)', color=self.text_primary)
        ax.set_ylabel('Position (mm)', color=self.text_primary)
        
        region = "Chambre" if x_pos < -self.results.get('lc', 0) else ("Col" if abs(x_pos) < 5 else "Divergent")
        ax.set_title(f'Coupe Radiale @ X = {x_pos:.1f} mm ({region}) | Flux = {flux_local:.2f} MW/m²',
                     color=self.text_primary, fontsize=12, fontweight='bold')
        
        self.apply_dark_axes([ax])
        fig.tight_layout()
        
        # Mettre à jour les labels d'info dans l'onglet principal
        self.update_heatmap_info(x_pos, t_gas_local, t_hot_local, t_cold_local, t_coolant, flux_local)

    def draw_heatmap_developed_in_window(self, ax, fig, canvas):
        """Dessine la carte thermique développée dans la fenêtre."""
        profile = self.results["thermal_profile"]
        X_mm = np.array(profile["X_mm"])
        Y_mm = np.array(profile["Y_mm"])
        T_gas = np.array(profile["T_gas"])
        T_wall_hot = np.array(profile["T_wall_hot"])
        T_wall_cold = profile["T_wall_cold"]
        Flux_MW = np.array(profile["Flux_MW"])
        
        wall_thickness = self.results.get("wall_thickness_mm", 3.0)
        n_depth = 30
        
        depth = np.linspace(0, wall_thickness, n_depth)
        X_grid, D_grid = np.meshgrid(X_mm, depth)
        
        T_grid = np.zeros_like(X_grid)
        for i, x in enumerate(X_mm):
            t_hot = T_wall_hot[i]
            t_cold = T_wall_cold if isinstance(T_wall_cold, (int, float)) else T_wall_cold
            for j, d in enumerate(depth):
                T_grid[j, i] = t_hot + (t_cold - t_hot) * d / wall_thickness
        
        cmap = self.heatmap_cmap_var.get()
        t_min = min(T_wall_cold if isinstance(T_wall_cold, (int, float)) else min(T_wall_cold), min(T_wall_hot)) - 50
        t_max = max(T_wall_hot) + 100
        levels = np.linspace(t_min, t_max, 50)
        
        contour = ax.contourf(X_grid, D_grid, T_grid, levels=levels, cmap=cmap, extend='both')
        
        cbar = fig.colorbar(contour, ax=ax, label='Température (K)', pad=0.02)
        cbar.ax.yaxis.label.set_color(self.text_primary)
        cbar.ax.tick_params(colors=self.text_primary)
        
        if self.heatmap_show_isotherms.get():
            iso_levels = np.linspace(t_min + 100, t_max - 100, 10)
            iso = ax.contour(X_grid, D_grid, T_grid, levels=iso_levels, 
                             colors='white', linewidths=0.5, alpha=0.7)
            ax.clabel(iso, inline=True, fontsize=7, fmt='%.0f K', colors='white')
        
        if self.heatmap_show_limits.get():
            t_limit = self.get_val("twall") if self.get_val("twall") else 1000
            limit_contour = ax.contour(X_grid, D_grid, T_grid, levels=[t_limit], 
                                       colors=['red'], linewidths=2, linestyles='--')
            if hasattr(limit_contour, 'allsegs') and any(len(seg) > 0 for seg in limit_contour.allsegs):
                ax.clabel(limit_contour, inline=True, fontsize=9, fmt=f'T_limite = {t_limit:.0f} K', colors='red')
        
        ax.axhline(y=0, color=self.accent, linewidth=1.5, label='Côté gaz')
        ax.axhline(y=wall_thickness, color='#00ff88', linewidth=1.5, label='Côté coolant')
        ax.axvline(x=0, color='white', linewidth=1, alpha=0.5)
        ax.text(0, wall_thickness * 1.05, 'Col', ha='center', color='white', fontsize=9)
        
        ax_flux = ax.twinx()
        ax_flux.fill_between(X_mm, 0, Flux_MW, alpha=0.2, color='red')
        ax_flux.plot(X_mm, Flux_MW, 'r-', linewidth=1, alpha=0.6)
        ax_flux.set_ylabel('Flux (MW/m²)', color='red')
        ax_flux.tick_params(axis='y', colors='red')
        ax_flux.set_ylim(0, max(Flux_MW) * 3)
        
        ax.set_xlabel('Position axiale X (mm)', color=self.text_primary)
        ax.set_ylabel('Profondeur dans la paroi (mm)', color=self.text_primary)
        ax.set_title('Carte Thermique Développée - Température dans la paroi', 
                     color=self.text_primary, fontsize=12, fontweight='bold')
        ax.legend(loc='upper right', fontsize=8)
        self.apply_dark_axes([ax])
        fig.tight_layout()

    def draw_heatmap_3d_surface_in_window(self, ax, fig, canvas):
        """Dessine une surface 3D de la température dans la fenêtre."""
        from mpl_toolkits.mplot3d import Axes3D
        
        profile = self.results["thermal_profile"]
        X_mm = np.array(profile["X_mm"])
        Y_mm = np.array(profile["Y_mm"])
        T_wall_hot = np.array(profile["T_wall_hot"])
        
        n_theta = int(self.heatmap_resolution_var.get())
        theta = np.linspace(0, 2*np.pi, n_theta)
        
        THETA, X = np.meshgrid(theta, X_mm)
        R = np.tile(Y_mm.reshape(-1, 1), (1, n_theta))
        T = np.tile(T_wall_hot.reshape(-1, 1), (1, n_theta))
        
        Y_3d = R * np.cos(THETA)
        Z_3d = R * np.sin(THETA)
        
        cmap = self.heatmap_cmap_var.get()
        norm = plt.Normalize(vmin=min(T_wall_hot), vmax=max(T_wall_hot))
        colormap = plt.colormaps.get_cmap(cmap) if hasattr(plt, 'colormaps') else plt.cm.get_cmap(cmap)
        surf = ax.plot_surface(X, Y_3d, Z_3d, facecolors=colormap(norm(T)),
                                shade=True, alpha=0.9, antialiased=True)
        
        mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array(T)
        cbar = fig.colorbar(mappable, ax=ax, label='T paroi hot (K)', 
                            shrink=0.6, pad=0.1)
        cbar.ax.yaxis.label.set_color(self.text_primary)
        cbar.ax.tick_params(colors=self.text_primary)
        
        ax.set_xlabel('X (mm)', color=self.text_primary, labelpad=12)
        ax.set_ylabel('Y (mm)', color=self.text_primary, labelpad=12)
        ax.set_zlabel('Z (mm)', color=self.text_primary, labelpad=12)
        ax.set_title('Surface 3D - Température paroi côté gaz', 
                     color=self.text_primary, fontsize=13, fontweight='bold', pad=20)
        
        ax.set_facecolor(self.bg_surface)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor(self.grid_color)
        ax.yaxis.pane.set_edgecolor(self.grid_color)
        ax.zaxis.pane.set_edgecolor(self.grid_color)
        ax.xaxis.pane.set_alpha(0.05)
        ax.yaxis.pane.set_alpha(0.05)
        ax.zaxis.pane.set_alpha(0.05)
        ax.tick_params(colors=self.text_primary, labelsize=9)
        ax.grid(True, color=self.grid_color, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.view_init(elev=20, azim=45)
        
        fig.tight_layout()
        
        # La référence de l'axe est déjà mise à jour dans update_heatmap_window


    def visualize_heatmap_in_window(self):
        """Ouvre la visualisation de la carte thermique dans une nouvelle fenêtre (comme l'optimiseur)."""
        if not self.results or "thermal_profile" not in self.results:
            messagebox.showwarning("Attention", "Calculez d'abord le moteur (bouton CALCULER)!")
            return
        
        # Fermer la fenêtre précédente si elle existe
        if hasattr(self, 'heatmap_window') and self.heatmap_window is not None:
            try:
                self.heatmap_window.destroy()
            except:
                pass
        
        # Créer une nouvelle fenêtre Toplevel
        self.heatmap_window = tk.Toplevel(self.root)
        self.heatmap_window.title("Carte Thermique 2D - Visualisation")
        self.heatmap_window.geometry("1400x900")
        self.heatmap_window.configure(bg=self.bg_main)
        
        # Maximiser l'utilisation de l'espace
        try:
            self.heatmap_window.state('zoomed')
        except:
            pass
        
        # Pas de contrôles dans la fenêtre - juste le titre
        title_frame = ctk.CTkFrame(self.heatmap_window, fg_color=self.bg_panel, corner_radius=10)
        title_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))
        
        ctk.CTkLabel(title_frame, text="🔥 Carte Thermique 2D - Visualisation",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="#ff6b35").pack(padx=10, pady=8)
        
        ctk.CTkLabel(title_frame, text="Les paramètres sont contrôlés depuis l'onglet principal",
                     font=ctk.CTkFont(size=10), text_color=self.text_muted).pack(padx=10, pady=(0, 8))
        
        # Container pour le graphique - PRINCIPAL et bien visible
        graph_container_win = ctk.CTkFrame(self.heatmap_window, fg_color=self.bg_panel, corner_radius=10)
        graph_container_win.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Figure matplotlib pour la carte thermique (grande taille, adaptative)
        # Utiliser une taille plus grande pour mieux utiliser l'espace
        fig_heatmap_win = plt.Figure(figsize=(16, 10), dpi=100)
        fig_heatmap_win.patch.set_facecolor(self.bg_main)
        fig_heatmap_win.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.08)
        
        # Axe initial (sera recréé dans update_heatmap_window)
        ax_heatmap_win = fig_heatmap_win.add_subplot(111)
        ax_heatmap_win.set_facecolor(self.bg_surface)
        ax_heatmap_win.text(0.5, 0.5, "Chargement...", 
                           ha='center', va='center', fontsize=14, color=self.text_muted,
                           transform=ax_heatmap_win.transAxes)
        self.apply_dark_axes([ax_heatmap_win])
        
        canvas_heatmap_win = FigureCanvasTkAgg(fig_heatmap_win, master=graph_container_win)
        canvas_heatmap_win.get_tk_widget().configure(bg=self.bg_main, highlightthickness=0)
        canvas_heatmap_win.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Stocker les références dans la fenêtre pour les utiliser dans update_heatmap_window
        self.heatmap_window._fig = fig_heatmap_win
        self.heatmap_window._ax = ax_heatmap_win
        self.heatmap_window._canvas = canvas_heatmap_win
        
        # Mettre à jour le graphique initial
        self.update_heatmap_window()
        
        # Gérer la fermeture de la fenêtre
        def on_close():
            try:
                if self.heatmap_window is not None:
                    self.heatmap_window.destroy()
            except:
                pass
            finally:
                self.heatmap_window = None
        
        self.heatmap_window.protocol("WM_DELETE_WINDOW", on_close)

    def update_heatmap_window(self, mode_var=None):
        """Met à jour le graphique dans la fenêtre de visualisation."""
        if not hasattr(self, 'heatmap_window') or self.heatmap_window is None:
            return
        
        if not self.results or "thermal_profile" not in self.results:
            fig = self.heatmap_window._fig
            canvas = self.heatmap_window._canvas
            fig.clear()
            ax = fig.add_subplot(111)
            ax.set_facecolor(self.bg_surface)
            ax.text(0.5, 0.5, "Calculez d'abord le moteur\n(bouton CALCULER)", 
                    ha='center', va='center', fontsize=14, color=self.text_muted,
                    transform=ax.transAxes)
            self.apply_dark_axes([ax])
            self.heatmap_window._ax = ax
            canvas.draw()
            return
        
        fig = self.heatmap_window._fig
        canvas = self.heatmap_window._canvas
        
        # Nettoyer complètement la figure
        fig.clear()
        
        # Utiliser les valeurs de l'onglet principal
        mode = self.heatmap_mode.get() if mode_var is None else mode_var.get()
        
        try:
            if mode == "coupe_radiale":
                ax = fig.add_subplot(111)
                ax.set_facecolor(self.bg_surface)
                self.draw_heatmap_radial_cut_in_window(ax, fig, canvas)
            elif mode == "developpee":
                ax = fig.add_subplot(111)
                ax.set_facecolor(self.bg_surface)
                self.draw_heatmap_developed_in_window(ax, fig, canvas)
            elif mode == "surface_3d":
                from mpl_toolkits.mplot3d import Axes3D
                ax = fig.add_subplot(111, projection='3d')
                self.draw_heatmap_3d_surface_in_window(ax, fig, canvas)
            
            # Mettre à jour la référence de l'axe
            self.heatmap_window._ax = ax
            canvas.draw()
        except Exception as e:
            import traceback
            fig.clear()
            ax = fig.add_subplot(111)
            ax.set_facecolor(self.bg_surface)
            ax.text(0.5, 0.5, f"Erreur:\n{str(e)}", 
                    ha='center', va='center', fontsize=12, color='red',
                    transform=ax.transAxes)
            self.apply_dark_axes([ax])
            self.heatmap_window._ax = ax
            canvas.draw()

    def init_cad_tab(self):
        """Initialise l'onglet Visualisation & Export CAD."""
        # Barre d'accent
        tk.Frame(self.tab_cad, height=4, bg="#9b59b6").pack(fill=tk.X)
        
        # Frame principale divisée en deux
        main_frame = ctk.CTkFrame(self.tab_cad)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # === Panneau de contrôles à gauche ===
        ctrl_panel = ctk.CTkFrame(main_frame)
        ctrl_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Bouton d'aide en haut du panneau
        ctk.CTkButton(ctrl_panel, text="📖 Aide CAD", width=120,
                   command=lambda: self.open_wiki_at("12. EXPORT CAD")).pack(fill=tk.X, pady=(0, 5))
        
        # Section: Géométrie de base
        geo_frame = ctk.CTkFrame(ctrl_panel)
        geo_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(geo_frame, text="Résolution angulaire:").grid(row=0, column=0, sticky="w", pady=2)
        self.cad_n_theta = ctk.CTkEntry(geo_frame, width=80)
        self.cad_n_theta.insert(0, "72")
        self.cad_n_theta.grid(row=0, column=1, padx=5, pady=2)
        ctk.CTkLabel(geo_frame, text="segments").grid(row=0, column=2, sticky="w")
        
        ctk.CTkLabel(geo_frame, text="Résolution axiale:").grid(row=1, column=0, sticky="w", pady=2)
        self.cad_n_axial = ctk.CTkEntry(geo_frame, width=80)
        self.cad_n_axial.insert(0, "100")
        self.cad_n_axial.grid(row=1, column=1, padx=5, pady=2)
        ctk.CTkLabel(geo_frame, text="points").grid(row=1, column=2, sticky="w")
        
        # Section: Paroi et canaux
        wall_frame = ctk.CTkFrame(ctrl_panel)
        wall_frame.pack(fill=tk.X, pady=5)
        
        self.cad_include_wall = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(wall_frame, text="Inclure épaisseur paroi", variable=self.cad_include_wall,
                       command=self.update_cad_preview).grid(row=0, column=0, columnspan=2, sticky="w")
        
        self.cad_include_channels = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(wall_frame, text="Inclure canaux de refroidissement", variable=self.cad_include_channels,
                       command=self.update_cad_preview).grid(row=1, column=0, columnspan=2, sticky="w")
        
        ctk.CTkLabel(wall_frame, text="Nombre de canaux:").grid(row=2, column=0, sticky="w", pady=2)
        self.cad_n_channels = ctk.CTkEntry(wall_frame, width=80)
        self.cad_n_channels.insert(0, "48")
        self.cad_n_channels.grid(row=2, column=1, padx=5, pady=2)
        
        ctk.CTkLabel(wall_frame, text="Largeur canal (mm):").grid(row=3, column=0, sticky="w", pady=2)
        self.cad_channel_width = ctk.CTkEntry(wall_frame, width=80)
        self.cad_channel_width.insert(0, "2.0")
        self.cad_channel_width.grid(row=3, column=1, padx=5, pady=2)
        
        ctk.CTkLabel(wall_frame, text="Profondeur canal (mm):").grid(row=4, column=0, sticky="w", pady=2)
        self.cad_channel_depth = ctk.CTkEntry(wall_frame, width=80)
        self.cad_channel_depth.insert(0, "3.0")
        self.cad_channel_depth.grid(row=4, column=1, padx=5, pady=2)
        
        ctk.CTkLabel(wall_frame, text="Type de canaux:").grid(row=5, column=0, sticky="w", pady=2)
        self.cad_channel_type = ctk.CTkComboBox(wall_frame, values=["Axiaux", "Hélicoïdaux", "Bifurcation"], 
                                              state="readonly", width=115)
        self.cad_channel_type.set("Axiaux")
        self.cad_channel_type.grid(row=5, column=1, padx=5, pady=2)
        
        # Section: Options export
        export_frame = ctk.CTkFrame(ctrl_panel)
        export_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(export_frame, text="Format export:").grid(row=0, column=0, sticky="w", pady=2)
        self.cad_format = ctk.CTkComboBox(export_frame, values=["STEP (CAD)", "STL (Mesh)", "DXF (Profil)"], 
                                        width=115)
        self.cad_format.set("STEP (CAD)")
        self.cad_format.grid(row=0, column=1, padx=5, pady=2)
        
        ctk.CTkLabel(export_frame, text="Unités:").grid(row=1, column=0, sticky="w", pady=2)
        self.cad_units = ctk.CTkComboBox(export_frame, values=["mm", "m", "inch"], width=70)
        self.cad_units.set("mm")
        self.cad_units.grid(row=1, column=1, padx=5, pady=2)
        
        self.cad_export_separate = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(export_frame, text="Exporter séparément",
                       variable=self.cad_export_separate).grid(row=2, column=0, columnspan=2, sticky="w")
        
        # Boutons d'action
        btn_frame = ctk.CTkFrame(ctrl_panel)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ctk.CTkButton(btn_frame, text="🔄 Prévisualiser 3D", command=self.update_cad_preview).pack(fill=tk.X, pady=2)
        ctk.CTkButton(btn_frame, text="📐 Exporter STEP", command=self.export_step).pack(fill=tk.X, pady=2)
        ctk.CTkButton(btn_frame, text="💾 Exporter STL", command=self.export_stl).pack(fill=tk.X, pady=2)
        ctk.CTkButton(btn_frame, text="📏 Exporter DXF", command=self.export_dxf).pack(fill=tk.X, pady=2)
        
        # Informations
        info_frame = ctk.CTkFrame(ctrl_panel)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.cad_info_labels = {}
        info_items = [("vertices", "Vertices:"), ("faces", "Faces:"), ("volume", "Volume:"), 
                      ("surface", "Surface:"), ("mass", "Masse estimée:")]
        for i, (key, text) in enumerate(info_items):
            ctk.CTkLabel(info_frame, text=text).grid(row=i, column=0, sticky="w", pady=1)
            lbl = ctk.CTkLabel(info_frame, text_color=self.accent)
            lbl.grid(row=i, column=1, sticky="e", padx=10)
            self.cad_info_labels[key] = lbl
        
        # === Panneau de visualisation à droite (Notebook) ===
        vis_notebook = ctk.CTkTabview(main_frame)
        vis_notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Onglet 1: Profil 2D
        tab_2d = vis_notebook.add("Profil 2D")
        
        # Utiliser plt.Figure pour éviter les conflits avec le backend global
        self.fig_visu = plt.Figure(figsize=(8, 6), dpi=100)
        self.fig_visu.patch.set_facecolor(self.bg_main)
        self.ax_visu = self.fig_visu.add_subplot(111)
        self.apply_dark_axes(self.ax_visu)
        
        self.canvas_visu = FigureCanvasTkAgg(self.fig_visu, master=tab_2d)
        self.canvas_visu.get_tk_widget().configure(bg=self.bg_main, highlightthickness=0)
        self.canvas_visu.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Onglet 2: Modèle 3D
        tab_3d = vis_notebook.add("Modèle 3D")
        
        self.fig_cad = plt.Figure(figsize=(8, 6), dpi=100)
        self.fig_cad.patch.set_facecolor(self.bg_main)
        self.ax_cad = self.fig_cad.add_subplot(111, projection='3d')
        self.ax_cad.set_facecolor(self.bg_surface)
        
        self.canvas_cad = FigureCanvasTkAgg(self.fig_cad, master=tab_3d)
        self.canvas_cad.get_tk_widget().configure(bg=self.bg_main, highlightthickness=0)
        self.canvas_cad.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Message initial 3D
        self.ax_cad.text2D(0.5, 0.5, "Calculez d'abord le moteur\npuis cliquez sur Prévisualiser 3D", 
                          transform=self.ax_cad.transAxes, ha='center', va='center', 
                          fontsize=12, color=self.text_muted)

    def update_cad_preview(self):
        """Met à jour la prévisualisation 3D du modèle CAD (Optimisé)."""
        if not hasattr(self, 'ax_cad'):
            return
            
        # Sauvegarder l'angle de vue actuel
        elev = getattr(self.ax_cad, 'elev', None)
        azim = getattr(self.ax_cad, 'azim', None)
            
        self.fig_cad.clear()
        self.ax_cad = self.fig_cad.add_subplot(111, projection='3d')
        
        # Restaurer l'angle de vue
        if elev is not None and azim is not None:
            self.ax_cad.view_init(elev=elev, azim=azim)
        else:
            self.ax_cad.view_init(elev=20, azim=45)
        
        if not self.results or not self.geometry_profile:
            self.ax_cad.text2D(0.5, 0.5, "Calculez d'abord le moteur\n(bouton CALCULER)", 
                              transform=self.ax_cad.transAxes, ha='center', va='center', 
                              fontsize=12, color=self.text_muted)
            self.canvas_cad.draw()
            return
        
        X_profile, Y_profile = self.geometry_profile
        X_mm = np.array(X_profile)
        R_inner = np.array(Y_profile)  # Rayon intérieur
        
        wall_thickness = self.results.get("wall_thickness_mm", 3.0)
        R_outer = R_inner + wall_thickness  # Rayon extérieur
        
        # OPTIMISATION: Limiter la résolution pour l'affichage uniquement
        # Même si l'utilisateur demande 200 segments pour l'export, on n'en affiche que 40 max
        target_n_theta = int(self.cad_n_theta.get())
        display_n_theta = min(target_n_theta, 40)
        
        # Sous-échantillonnage axial si trop de points
        step_axial = max(1, len(X_mm) // 50)
        
        X_disp = X_mm[::step_axial]
        R_in_disp = R_inner[::step_axial]
        R_out_disp = R_outer[::step_axial]
        
        theta = np.linspace(0, 2*np.pi, display_n_theta)
        
        # Créer les surfaces
        THETA, X = np.meshgrid(theta, X_disp)
        
        # Surface intérieure (côté gaz)
        R_in_grid = np.tile(R_in_disp.reshape(-1, 1), (1, display_n_theta))
        Y_in = R_in_grid * np.cos(THETA)
        Z_in = R_in_grid * np.sin(THETA)
        
        # Surface extérieure (côté coolant)
        if self.cad_include_wall.get():
            R_out_grid = np.tile(R_out_disp.reshape(-1, 1), (1, display_n_theta))
            Y_out = R_out_grid * np.cos(THETA)
            Z_out = R_out_grid * np.sin(THETA)
        
        # Tracer surface intérieure (Wireframe partiel pour légèreté ou Surface)
        # Surface est plus jolie mais plus lourde. Avec l'optimisation ci-dessus, surface passe bien.
        surf_in = self.ax_cad.plot_surface(X, Y_in, Z_in, alpha=0.8, color=self.accent, 
                                            edgecolor='none', shade=True, antialiased=True)
        
        # Tracer surface extérieure
        if self.cad_include_wall.get():
            surf_out = self.ax_cad.plot_surface(X, Y_out, Z_out, alpha=0.3, color='#00ff88', 
                                                 edgecolor='none', shade=True, antialiased=True)
        
        # Tracer les canaux de refroidissement (simplifié)
        if self.cad_include_channels.get() and self.cad_include_wall.get():
            n_channels = int(self.cad_n_channels.get())
            # Limiter le nombre de canaux affichés pour la perf
            display_n_channels = min(n_channels, 24) 
            
            channel_depth_mm = float(self.cad_channel_depth.get())
            
            # Position angulaire des canaux
            channel_angles = np.linspace(0, 2*np.pi, display_n_channels, endpoint=False)
            
            for angle in channel_angles:
                # Fond du canal
                r_channel = R_in_disp + wall_thickness - channel_depth_mm
                x_ch = X_disp
                y_ch = r_channel * np.cos(angle)
                z_ch = r_channel * np.sin(angle)
                self.ax_cad.plot(x_ch, y_ch, z_ch, color='#0088ff', linewidth=0.8, alpha=0.6)
        
        # Configuration 3D STYLE "CLEAN" (comme Heatmap)
        self.ax_cad.set_xlabel('X (mm)', color=self.text_primary, labelpad=5)
        self.ax_cad.set_ylabel('Y (mm)', color=self.text_primary, labelpad=5)
        self.ax_cad.set_zlabel('Z (mm)', color=self.text_primary, labelpad=5)
        self.ax_cad.set_title(f"Modèle 3D - {self.get_val('name')}", color=self.text_primary, fontweight='bold')
        
        # Style sombre optimisé
        self.ax_cad.set_facecolor(self.bg_surface)
        
        # Supprimer les fonds de grille gris (panes)
        self.ax_cad.xaxis.pane.fill = False
        self.ax_cad.yaxis.pane.fill = False
        self.ax_cad.zaxis.pane.fill = False
        
        # Bordures de grille discrètes
        self.ax_cad.xaxis.pane.set_edgecolor(self.grid_color)
        self.ax_cad.yaxis.pane.set_edgecolor(self.grid_color)
        self.ax_cad.zaxis.pane.set_edgecolor(self.grid_color)
        self.ax_cad.xaxis.pane.set_alpha(0.1)
        self.ax_cad.yaxis.pane.set_alpha(0.1)
        self.ax_cad.zaxis.pane.set_alpha(0.1)
        
        self.ax_cad.tick_params(colors=self.text_primary, labelsize=8)
        self.ax_cad.grid(True, color=self.grid_color, alpha=0.3, linestyle='--')
        
        # Égaliser les axes
        max_range = max(max(X_mm) - min(X_mm), 2 * max(R_outer)) / 2
        mid_x = (max(X_mm) + min(X_mm)) / 2
        self.ax_cad.set_xlim(mid_x - max_range, mid_x + max_range)
        self.ax_cad.set_ylim(-max_range, max_range)
        self.ax_cad.set_zlim(-max_range, max_range)
        
        self.fig_cad.tight_layout()
        self.canvas_cad.draw()
        
        # Mettre à jour les infos
        self.update_cad_info()

    def update_cad_info(self):
        """Met à jour les informations du modèle CAD."""
        if not self.results or not self.geometry_profile:
            return
        
        X_profile, Y_profile = self.geometry_profile
        R_inner = np.array(Y_profile)
        wall_thickness = self.results.get("wall_thickness_mm", 3.0)
        R_outer = R_inner + wall_thickness
        
        n_theta = int(self.cad_n_theta.get())
        n_axial = len(X_profile)
        
        # Calcul approximatif
        n_vertices = n_axial * n_theta * 2  # Inner + outer
        n_faces = (n_axial - 1) * n_theta * 2 * 2  # Quads -> triangles
        
        # Volume approximatif (intégration)
        volume = 0
        for i in range(len(X_profile) - 1):
            dx = abs(X_profile[i+1] - X_profile[i])
            r_in_avg = (R_inner[i] + R_inner[i+1]) / 2
            r_out_avg = (R_outer[i] + R_outer[i+1]) / 2
            volume += np.pi * (r_out_avg**2 - r_in_avg**2) * dx  # mm³
        
        volume_cm3 = volume / 1000  # cm³
        
        # Surface
        surface = self.results.get("A_cooled", 0) * 1e6  # mm²
        
        # Masse (estimation avec cuivre: 8.96 g/cm³)
        density = 8.96  # g/cm³ pour cuivre
        mass = volume_cm3 * density  # g
        
        self.cad_info_labels["vertices"].configure(text=f"{n_vertices:,}")
        self.cad_info_labels["faces"].configure(text=f"{n_faces:,}")
        self.cad_info_labels["volume"].configure(text=f"{volume_cm3:.1f} cm³")
        self.cad_info_labels["surface"].configure(text=f"{surface:.0f} mm²")
        self.cad_info_labels["mass"].configure(text=f"{mass:.0f} g ({mass/1000:.2f} kg)")

    def export_stl(self):
        """Exporte le modèle 3D au format STL."""
        if not self.results or not self.geometry_profile:
            messagebox.showwarning("Attention", "Calculez d'abord le moteur!")
            return
        
        if not HAS_NUMPY_STL:
            messagebox.showwarning("Attention", 
                "Module numpy-stl non installé.\n\nInstallez-le avec:\npip install numpy-stl")
            return
        
        f = filedialog.asksaveasfilename(defaultextension=".stl", 
                                          filetypes=[("STL files", "*.stl")],
                                          initialfile=f"{self.get_val('name')}_nozzle.stl")
        if not f:
            return
        
        try:
            X_profile, Y_profile = self.geometry_profile
            X_mm = np.array(X_profile)
            R_inner = np.array(Y_profile)
            wall_thickness = self.results.get("wall_thickness_mm", 3.0)
            R_outer = R_inner + wall_thickness
            
            n_theta = int(self.cad_n_theta.get())
            theta = np.linspace(0, 2*np.pi, n_theta)
            
            n_axial = len(X_mm)
            
            # Générer les vertices pour surface intérieure
            vertices_inner = []
            for i, x in enumerate(X_mm):
                for t in theta:
                    y = R_inner[i] * np.cos(t)
                    z = R_inner[i] * np.sin(t)
                    vertices_inner.append([x, y, z])
            vertices_inner = np.array(vertices_inner)
            
            # Générer les vertices pour surface extérieure
            vertices_outer = []
            for i, x in enumerate(X_mm):
                for t in theta:
                    y = R_outer[i] * np.cos(t)
                    z = R_outer[i] * np.sin(t)
                    vertices_outer.append([x, y, z])
            vertices_outer = np.array(vertices_outer)
            
            # Combiner les vertices
            all_vertices = np.vstack([vertices_inner, vertices_outer])
            n_inner = len(vertices_inner)
            
            # Générer les faces (triangles)
            faces = []
            
            # Faces surface intérieure (normales vers l'intérieur)
            for i in range(n_axial - 1):
                for j in range(n_theta - 1):
                    v0 = i * n_theta + j
                    v1 = i * n_theta + j + 1
                    v2 = (i + 1) * n_theta + j
                    v3 = (i + 1) * n_theta + j + 1
                    # Triangle 1
                    faces.append([v0, v2, v1])
                    # Triangle 2
                    faces.append([v1, v2, v3])
            
            # Faces surface extérieure (normales vers l'extérieur)
            for i in range(n_axial - 1):
                for j in range(n_theta - 1):
                    v0 = n_inner + i * n_theta + j
                    v1 = n_inner + i * n_theta + j + 1
                    v2 = n_inner + (i + 1) * n_theta + j
                    v3 = n_inner + (i + 1) * n_theta + j + 1
                    # Triangle 1
                    faces.append([v0, v1, v2])
                    # Triangle 2
                    faces.append([v1, v3, v2])
            
            # Faces de fermeture aux extrémités
            # Entrée (chambre)
            for j in range(n_theta - 1):
                v_in = j
                v_in_next = j + 1
                v_out = n_inner + j
                v_out_next = n_inner + j + 1
                faces.append([v_in, v_in_next, v_out])
                faces.append([v_in_next, v_out_next, v_out])
            
            # Sortie (divergent)
            base_in = (n_axial - 1) * n_theta
            base_out = n_inner + (n_axial - 1) * n_theta
            for j in range(n_theta - 1):
                v_in = base_in + j
                v_in_next = base_in + j + 1
                v_out = base_out + j
                v_out_next = base_out + j + 1
                faces.append([v_in, v_out, v_in_next])
                faces.append([v_in_next, v_out, v_out_next])
            
            faces = np.array(faces)
            
            # Créer le mesh STL
            nozzle_mesh = stl_mesh.Mesh(np.zeros(len(faces), dtype=stl_mesh.Mesh.dtype))
            for i, face in enumerate(faces):
                for j in range(3):
                    nozzle_mesh.vectors[i][j] = all_vertices[face[j]]
            
            # Sauvegarder
            nozzle_mesh.save(f)
            
            messagebox.showinfo("Succès", f"Fichier STL exporté:\n{f}\n\n"
                               f"Vertices: {len(all_vertices)}\nFaces: {len(faces)}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export STL:\n{e}")

    def export_step(self):
        """Exporte le modèle 3D au format STEP (solide paramétrique)."""
        if not self.results or not self.geometry_profile:
            messagebox.showwarning("Attention", "Calculez d'abord le moteur!")
            return
        
        # Vérifier si CadQuery est disponible
        if HAS_CADQUERY:
            self._export_step_cadquery()
        else:
            # Proposer des alternatives
            result = messagebox.askyesno("Export STEP", 
                "CadQuery n'est pas installé.\n\n"
                "Pour l'installer:\n"
                "  py -3.10 -m pip install cadquery-ocp\n\n"
                "Voulez-vous exporter en format DXF à la place?\n"
                "(Le DXF peut être importé dans Fusion 360/SolidWorks\n"
                "et utilisé pour créer un solide de révolution)")
            if result:
                self._export_dxf_for_cad()

    def _export_step_cadquery(self):
        """Export STEP via CadQuery."""
        f = filedialog.asksaveasfilename(defaultextension=".step", 
                                          filetypes=[("STEP files", "*.step"), ("STEP files", "*.stp")],
                                          initialfile=f"{self.get_val('name')}_nozzle.step")
        if not f:
            return
        
        try:
            X_profile, Y_profile = self.geometry_profile
            X_mm = np.array(X_profile)
            R_inner = np.array(Y_profile)
            wall_thickness = self.results.get("wall_thickness_mm", 3.0)
            R_outer = R_inner + wall_thickness
            
            # Créer le profil de révolution
            inner_points = [(X_mm[i], R_inner[i]) for i in range(len(X_mm))]
            outer_points = [(X_mm[i], R_outer[i]) for i in range(len(X_mm)-1, -1, -1)]
            all_points = inner_points + outer_points
            all_points.append(inner_points[0])
            
            profile = cq.Workplane("XZ")
            profile = profile.moveTo(all_points[0][0], all_points[0][1])
            for pt in all_points[1:]:
                profile = profile.lineTo(pt[0], pt[1])
            profile = profile.close()
            
            nozzle = profile.revolve(360, (0, 0, 0), (1, 0, 0))
            cq.exporters.export(nozzle, f)
            
            messagebox.showinfo("Succès", f"Fichier STEP exporté:\n{f}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur export STEP:\n{e}")

    def _export_dxf_for_cad(self):
        """Exporte un DXF optimisé pour import CAD (profil de révolution)."""
        if not HAS_EZDXF:
            messagebox.showwarning("Attention", "Module ezdxf non installé.\npip install ezdxf")
            return
        
        f = filedialog.asksaveasfilename(defaultextension=".dxf", 
                                          filetypes=[("DXF files", "*.dxf")],
                                          initialfile=f"{self.get_val('name')}_profile_CAD.dxf")
        if not f:
            return
        
        try:
            X_profile, Y_profile = self.geometry_profile
            X_mm = np.array(X_profile)
            R_inner = np.array(Y_profile)
            wall_thickness = self.results.get("wall_thickness_mm", 3.0)
            R_outer = R_inner + wall_thickness
            
            # Créer le document DXF
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Profil fermé pour révolution
            # Layer pour le profil de révolution
            doc.layers.add("PROFILE_REVOLUTION", color=1)  # Rouge
            doc.layers.add("AXE_REVOLUTION", color=5)      # Bleu
            doc.layers.add("DIMENSIONS", color=3)          # Vert
            
            # Tracer l'axe de révolution (ligne centrale)
            msp.add_line((X_mm[0] - 10, 0), (X_mm[-1] + 10, 0), 
                        dxfattribs={"layer": "AXE_REVOLUTION", "linetype": "CENTER"})
            
            # Créer le profil fermé (polyline)
            # Intérieur: de gauche à droite
            points = []
            for i in range(len(X_mm)):
                points.append((X_mm[i], R_inner[i]))
            
            # Extérieur: de droite à gauche
            for i in range(len(X_mm)-1, -1, -1):
                points.append((X_mm[i], R_outer[i]))
            
            # Fermer le profil
            points.append(points[0])
            
            # Ajouter la polyline fermée
            msp.add_lwpolyline(points, dxfattribs={"layer": "PROFILE_REVOLUTION"}, close=True)
            
            # Ajouter des dimensions clés
            # Diamètre col
            idx_throat = np.argmin(R_inner)
            x_throat = X_mm[idx_throat]
            r_throat = R_inner[idx_throat]
            
            msp.add_text(f"Ø Col = {2*r_throat:.2f} mm", 
                        dxfattribs={"layer": "DIMENSIONS", "height": 2}).set_placement((x_throat, -5))
            
            # Diamètre sortie
            msp.add_text(f"Ø Sortie = {2*R_inner[-1]:.2f} mm",
                        dxfattribs={"layer": "DIMENSIONS", "height": 2}).set_placement((X_mm[-1], -5))
            
            # Épaisseur paroi
            msp.add_text(f"Épaisseur = {wall_thickness:.2f} mm",
                        dxfattribs={"layer": "DIMENSIONS", "height": 2}).set_placement((X_mm[0], R_outer[0] + 5))
            
            # Instructions
            msp.add_text("INSTRUCTIONS: Importer dans CAD, sélectionner PROFILE_REVOLUTION,",
                        dxfattribs={"layer": "DIMENSIONS", "height": 1.5}).set_placement((X_mm[0], -15))
            msp.add_text("faire Revolve 360° autour de l'axe AXE_REVOLUTION",
                        dxfattribs={"layer": "DIMENSIONS", "height": 1.5}).set_placement((X_mm[0], -18))
            
            doc.saveas(f)
            
            messagebox.showinfo("Succès", 
                f"Fichier DXF exporté:\n{f}\n\n"
                f"📌 INSTRUCTIONS:\n"
                f"1. Importer dans Fusion 360 / SolidWorks\n"
                f"2. Sélectionner le profil fermé (layer PROFILE_REVOLUTION)\n"
                f"3. Utiliser l'outil 'Revolve' (360°)\n"
                f"4. Axe = ligne centrale (layer AXE_REVOLUTION)\n\n"
                f"Cela créera un solide 3D paramétrique!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur export DXF:\n{e}")

    # =====================================================================
    # ONGLET OPTIMISEUR AUTOMATIQUE
    # =====================================================================
    def init_optimizer_tab(self):
        """Initialise l'onglet Optimiseur avec paramètres, contraintes et algorithmes."""
        # Barre d'accent orange
        tk.Frame(self.tab_optimizer, height=4, bg="#e67e22").pack(fill=tk.X)
        
        # Frame principale avec scroll
        main_canvas = tk.Canvas(self.tab_optimizer, bg=self.bg_main, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(self.tab_optimizer, command=main_canvas.yview)
        scroll_frame = ctk.CTkFrame(main_canvas)
        
        scroll_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Titre
        header = ctk.CTkFrame(scroll_frame)
        header.pack(fill=tk.X, pady=(5, 10))
        
        ctk.CTkLabel(header, text="🛠️ Optimiseur de Conception",
                  font=(UI_FONT, 14, "bold"), text_color=self.accent).pack(side=tk.LEFT)
        
        # Bouton d'aide Wiki
        ctk.CTkButton(header, text="📖 Aide Optimiseur",
                   command=lambda: self.open_wiki_at("11. UTILISATION DE L'OPTIMISEUR")).pack(side=tk.RIGHT, padx=10)
        
        # Section: Propriétés Matériau
        mat_frame = ctk.CTkFrame(scroll_frame)
        mat_frame.pack(fill=tk.X, pady=5, padx=5)
        
        row_mat = ctk.CTkFrame(mat_frame)
        row_mat.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(row_mat, text="Matériau:").pack(side=tk.LEFT)
        self.optim_mat_combo = ctk.CTkComboBox(row_mat, values=list(self.materials_db.keys()), width=25)
        self.optim_mat_combo.set("Cuivre-Zirconium (CuZr)")
        self.optim_mat_combo.pack(side=tk.LEFT, padx=10)
        
        self.optim_mat_props = {
            "rho": tk.DoubleVar(value=8920),
            "k": tk.DoubleVar(value=340),
            "T_melt": tk.DoubleVar(value=1356),
            "sigma_y": tk.DoubleVar(value=400)
        }
        
        ctk.CTkLabel(row_mat, text="ρ (kg/m³):").pack(side=tk.LEFT, padx=(10, 2))
        ctk.CTkEntry(row_mat, textvariable=self.optim_mat_props["rho"], width=8).pack(side=tk.LEFT)
        
        ctk.CTkLabel(row_mat, text="k (W/m-K):").pack(side=tk.LEFT, padx=(10, 2))
        ctk.CTkEntry(row_mat, textvariable=self.optim_mat_props["k"], width=8).pack(side=tk.LEFT)
        
        ctk.CTkLabel(row_mat, text="T fusion (K):").pack(side=tk.LEFT, padx=(10, 2))
        ctk.CTkEntry(row_mat, textvariable=self.optim_mat_props["T_melt"], width=8).pack(side=tk.LEFT)
        
        ctk.CTkLabel(row_mat, text="σy (MPa):").pack(side=tk.LEFT, padx=(10, 2))
        ctk.CTkEntry(row_mat, textvariable=self.optim_mat_props["sigma_y"], width=8).pack(side=tk.LEFT)
        
        def update_optim_material(event=None):
            name = self.optim_mat_combo.get()
            if name in self.materials_db:
                mat = self.materials_db[name]
                self.optim_mat_props["rho"].set(mat.get("rho", 8000))
                self.optim_mat_props["k"].set(mat.get("k", 20))
                self.optim_mat_props["T_melt"].set(mat.get("T_melt", 1500))
                self.optim_mat_props["sigma_y"].set(mat.get("sigma_y", 200))
        
        self.optim_mat_combo.configure(command=update_optim_material)
        
        # Section: Objectif d'optimisation
        obj_frame = ctk.CTkFrame(scroll_frame)
        obj_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.optim_objective = tk.StringVar(value="min_mass")
        objectives = [
            ("min_mass", "Minimiser la masse", "Réduit l'épaisseur de paroi tout en respectant les contraintes thermiques"),
            ("min_dp", "Minimiser Δp", "Optimise la géométrie des canaux pour réduire les pertes de charge"),
            ("max_margin", "Maximiser marge thermique", "Augmente l'écart entre T_paroi et T_fusion du matériau"),
            ("multi", "Multi-objectif (Pareto)", "Équilibre entre masse, Δp et marge thermique")
        ]
        
        for i, (value, text, desc) in enumerate(objectives):
            frame = ctk.CTkFrame(obj_frame)
            frame.pack(fill=tk.X, pady=2)
            ctk.CTkRadioButton(frame, text=text, variable=self.optim_objective, value=value).pack(side=tk.LEFT)
            ctk.CTkLabel(frame, text=f"  - {desc}", text_color=self.text_muted).pack(side=tk.LEFT, padx=10)
        
        # Section: Variables de design
        vars_frame = ctk.CTkFrame(scroll_frame)
        vars_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Tableau des variables
        headers = ["Variable", "Min", "Max", "Pas", "Actif"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(vars_frame, text=h, font=(UI_FONT, 10, "bold")).grid(row=0, column=col, padx=5, pady=2)
        
        self.optim_vars = {}
        design_vars = [
            ("wall_thickness", "Épaisseur paroi (mm)", 1.0, 10.0, 0.5),
            ("channel_depth", "Profondeur canaux (mm)", 1.0, 8.0, 0.5),
            ("channel_width", "Largeur canaux (mm)", 0.5, 5.0, 0.25),
            ("n_channels", "Nombre de canaux", 16, 120, 4),
            ("coolant_velocity", "Vitesse coolant (m/s)", 5.0, 50.0, 2.5),
            ("inlet_pressure", "Pression entrée (bar)", 20.0, 100.0, 5.0),
        ]
        
        for row, (key, label, vmin, vmax, step) in enumerate(design_vars, start=1):
            self.optim_vars[key] = {
                "active": tk.BooleanVar(value=True if row <= 3 else False),
                "min": tk.DoubleVar(value=vmin),
                "max": tk.DoubleVar(value=vmax),
                "step": tk.DoubleVar(value=step)
            }
            
            ctk.CTkLabel(vars_frame, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            ctk.CTkEntry(vars_frame, textvariable=self.optim_vars[key]["min"], width=8).grid(row=row, column=1, padx=5)
            ctk.CTkEntry(vars_frame, textvariable=self.optim_vars[key]["max"], width=8).grid(row=row, column=2, padx=5)
            ctk.CTkEntry(vars_frame, textvariable=self.optim_vars[key]["step"], width=8).grid(row=row, column=3, padx=5)
            ctk.CTkCheckBox(vars_frame, variable=self.optim_vars[key]["active"]).grid(row=row, column=4, padx=5)
        
        # Section: Contraintes
        constr_frame = ctk.CTkFrame(scroll_frame)
        constr_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.optim_constraints = {}
        constraints = [
            ("T_wall_max", "T paroi max (K)", 800, "K", "Température maximale admissible de la paroi chaude"),
            ("dp_max", "Δp max (bar)", 15.0, "bar", "Perte de charge maximale dans le circuit de refroidissement"),
            ("margin_min", "Marge thermique min (%)", 15, "%", "Marge minimale entre T_paroi et T_fusion"),
            ("velocity_max", "Vitesse coolant max (m/s)", 60, "m/s", "Pour éviter cavitation et érosion"),
        ]
        
        for row, (key, label, default, unit, tooltip) in enumerate(constraints):
            self.optim_constraints[key] = {
                "value": tk.DoubleVar(value=default),
                "active": tk.BooleanVar(value=True)
            }
            
            frame = ctk.CTkFrame(constr_frame)
            frame.pack(fill=tk.X, pady=2)
            ctk.CTkCheckBox(frame, variable=self.optim_constraints[key]["active"]).pack(side=tk.LEFT)
            ctk.CTkLabel(frame, text=label, width=20).pack(side=tk.LEFT)
            ctk.CTkEntry(frame, textvariable=self.optim_constraints[key]["value"], width=10).pack(side=tk.LEFT, padx=5)
            ctk.CTkLabel(frame, text=unit, width=5).pack(side=tk.LEFT)
            ctk.CTkLabel(frame, text=f"  ({tooltip})", text_color=self.text_muted).pack(side=tk.LEFT, padx=10)
        
        # Section: Algorithme
        algo_frame = ctk.CTkFrame(scroll_frame)
        algo_frame.pack(fill=tk.X, pady=5, padx=5)
        
        row1 = ctk.CTkFrame(algo_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(row1, text="Algorithme:").pack(side=tk.LEFT)
        self.optim_algorithm = ctk.CTkComboBox(row1, values=[
            "Grid Search (exhaustif)",
            "Gradient Descent (SLSQP)",
            "Algorithme Génétique",
            "Differential Evolution",
            "Bayesian Optimization",
            "Nelder-Mead (Simplex)"
        ], width=25)
        self.optim_algorithm.set("Differential Evolution")
        self.optim_algorithm.pack(side=tk.LEFT, padx=10)
        
        ctk.CTkLabel(row1, text="Max itérations:").pack(side=tk.LEFT, padx=(20, 5))
        self.optim_max_iter = ctk.CTkEntry(row1, width=80)
        self.optim_max_iter.insert(0, "100")
        self.optim_max_iter.pack(side=tk.LEFT)
        
        row2 = ctk.CTkFrame(algo_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(row2, text="Tolérance:").pack(side=tk.LEFT)
        self.optim_tolerance = ctk.CTkEntry(row2, width=10)
        self.optim_tolerance.insert(0, "1e-4")
        self.optim_tolerance.pack(side=tk.LEFT, padx=10)
        
        ctk.CTkLabel(row2, text="Population:").pack(side=tk.LEFT, padx=(20, 5))
        self.optim_population = ctk.CTkEntry(row2, width=80)
        self.optim_population.insert(0, "50")
        self.optim_population.pack(side=tk.LEFT)
        
        self.optim_parallel = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(row2, text="Parallèle", variable=self.optim_parallel).pack(side=tk.LEFT, padx=20)
        
        # Section: Boutons d'action
        action_frame = ctk.CTkFrame(scroll_frame)
        action_frame.pack(fill=tk.X, pady=10, padx=5)
        
        self.btn_run_optim = ctk.CTkButton(action_frame, text="🚀 Optimiser",
                                         command=self.run_optimization)
        self.btn_run_optim.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(action_frame, text="⏹ Arrêter", command=self.stop_optimization).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(action_frame, text="📊 Exporter", command=self.export_optimization_results).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(action_frame, text="📈 Visualiser", command=self.visualize_optimizer_results).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(action_frame, text="✅ Appliquer", command=self.apply_best_config).pack(side=tk.LEFT, padx=5)
        
        # Barre de progression
        prog_frame = ctk.CTkFrame(scroll_frame)
        prog_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ctk.CTkLabel(prog_frame, text="Progression:").pack(side=tk.LEFT)
        self.optim_progress = ctk.CTkProgressBar(prog_frame, width=400)
        self.optim_progress.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.optim_progress_label = ctk.CTkLabel(prog_frame, text="0%", text_color=self.accent)
        self.optim_progress_label.pack(side=tk.LEFT)
        
        # Section: Résultats
        results_frame = ctk.CTkFrame(scroll_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Tableau des résultats (Treeview)
        cols = ("rank", "wall_t", "ch_depth", "ch_width", "n_ch", "T_wall", "dp", "margin", "mass", "score")
        self.optim_tree = ttk.Treeview(results_frame, columns=cols, show="headings", height=10)
        
        col_names = ["#", "Épaisseur", "Prof. Can.", "Larg. Can.", "N Can.", "T Paroi", "Δp", "Marge", "Masse", "Score"]
        col_widths = [40, 80, 80, 80, 60, 80, 60, 60, 70, 70]
        
        for col, name, width in zip(cols, col_names, col_widths):
            self.optim_tree.heading(col, text=name)
            self.optim_tree.column(col, width=width, anchor="center")
        
        scrollbar_tree = ctk.CTkScrollbar(results_frame, command=self.optim_tree.yview)
        self.optim_tree.configure(yscrollcommand=scrollbar_tree.set)
        
        self.optim_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_tree.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Graphique de convergence
        conv_frame = ctk.CTkFrame(scroll_frame)
        conv_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.fig_optim = plt.Figure(figsize=(10, 3), dpi=100)
        self.fig_optim.patch.set_facecolor(self.bg_main)
        self.ax_optim = self.fig_optim.add_subplot(111)
        self.ax_optim.set_facecolor(self.bg_surface)
        
        self.canvas_optim = FigureCanvasTkAgg(self.fig_optim, master=conv_frame)
        self.canvas_optim.get_tk_widget().pack(fill=tk.X, expand=True)
        
        # Initialiser le flag d'arrêt
        self.optim_running = False
        self.optim_stop_flag = False
        
        # Dessiner un placeholder
        self.ax_optim.text(0.5, 0.5, "Lancez une optimisation pour voir la convergence",
                          transform=self.ax_optim.transAxes, ha='center', va='center',
                          fontsize=10, color=self.text_muted)
        self.ax_optim.set_xlabel("Itération", color=self.text_primary)
        self.ax_optim.set_ylabel("Score", color=self.text_primary)
        self.ax_optim.tick_params(colors=self.text_primary)
        self.canvas_optim.draw()

    def run_optimization(self):
        """Lance le processus d'optimisation."""
        if self.optim_running:
            messagebox.showwarning("Attention", "Optimisation déjà en cours!")
            return
        
        if not self.results:
            messagebox.showwarning("Attention", "Calculez d'abord un design de base (bouton CALCULER)")
            return
        
        # Collecter les variables actives
        active_vars = {k: v for k, v in self.optim_vars.items() if v["active"].get()}
        if not active_vars:
            messagebox.showwarning("Attention", "Activez au moins une variable de design!")
            return
        
        self.optim_running = True
        self.optim_stop_flag = False
        self.btn_run_optim.configure(state="disabled")
        
        # Nettoyer le tableau
        for item in self.optim_tree.get_children():
            self.optim_tree.delete(item)
        
        # Lancer dans un thread
        import threading
        thread = threading.Thread(target=self._optimization_worker, args=(active_vars,), daemon=True)
        thread.start()

    def _optimization_worker(self, active_vars):
        """Worker thread pour l'optimisation."""
        from scipy import optimize
        
        objective = self.optim_objective.get()
        algorithm = self.optim_algorithm.get()
        max_iter = int(self.optim_max_iter.get())
        
        # Définir les bornes
        bounds = []
        var_keys = list(active_vars.keys())
        for key in var_keys:
            vmin = active_vars[key]["min"].get()
            vmax = active_vars[key]["max"].get()
            bounds.append((vmin, vmax))
        
        # Historique pour convergence
        self.optim_history = []
        self.optim_results_list = []
        
        def objective_function(x):
            """Fonction objectif à minimiser."""
            if self.optim_stop_flag:
                return float('inf')
            
            # Mapper x aux variables
            config = {}
            for i, key in enumerate(var_keys):
                config[key] = x[i]
            
            # Évaluer le design avec cette config
            score, metrics = self._evaluate_design(config)
            
            # Stocker le résultat
            self.optim_results_list.append({
                "config": config.copy(),
                "metrics": metrics,
                "score": score
            })
            
            # Mettre à jour l'historique
            self.optim_history.append(score)
            
            # Mise à jour UI (thread-safe)
            progress = len(self.optim_history) / max_iter * 100
            self.root.after(0, self._update_optim_progress, progress, score, config, metrics)
            
            return score
        
        try:
            # Point initial
            x0 = [(active_vars[k]["min"].get() + active_vars[k]["max"].get()) / 2 for k in var_keys]
            n_vars = len(var_keys)
            pop_size = int(self.optim_population.get())
            
            # Estimation du nombre total d'évaluations pour la barre de progression
            if "Differential Evolution" in algorithm:
                # (maxiter + 1) * popsize * N
                total_evals = (max_iter + 1) * pop_size * n_vars
            elif "Grid Search" in algorithm:
                # Produit des pas
                total_evals = 1
                for key in var_keys:
                    steps = int((active_vars[key]["max"].get() - active_vars[key]["min"].get()) / active_vars[key]["step"].get()) + 1
                    total_evals *= steps
            else:
                # SLSQP, Nelder-Mead, etc. (difficile à prédire exactement, heuristique)
                total_evals = max_iter * 5  # Heuristique
            
            total_evals = max(total_evals, 1) # Eviter div/0
            
            # Fonction wrapper pour mettre à jour la progression
            def progress_callback(xk, convergence=None):
                """Callback appelé par l'optimiseur à chaque itération (pas évaluation)."""
                # Note: Scipy n'appelle ça qu'une fois par itération, pas par évaluation
                # On utilise objective_function pour le vrai tracking
                pass

            def objective_function(x):
                """Fonction objectif à minimiser."""
                if self.optim_stop_flag:
                    # Retourner une valeur haute pour forcer l'arrêt ou sortir
                    # Scipy ne s'arrête pas immédiatement, mais on peut influencer
                    return 1e9
                
                # Mapper x aux variables
                config = {}
                for i, key in enumerate(var_keys):
                    config[key] = x[i]
                
                # Évaluer le design avec cette config
                score, metrics = self._evaluate_design(config)
                
                # Stocker le résultat
                self.optim_results_list.append({
                    "config": config.copy(),
                    "metrics": metrics,
                    "score": score
                })
                
                # Mettre à jour l'historique
                self.optim_history.append(score)
                
                # Mise à jour UI (thread-safe)
                # Calculer le progrès basé sur le nombre d'appels
                n_calls = len(self.optim_results_list)
                progress = min(99, (n_calls / total_evals) * 100)
                
                # Update moins fréquent pour ne pas spammer l'UI (tous les 1% ou 10 appels)
                if n_calls % max(1, int(total_evals/100)) == 0:
                    self.root.after(0, self._update_optim_progress, progress, score, config, metrics)
                
                return score
            
            if "Grid Search" in algorithm:
                # Grid search
                self._grid_search(active_vars, var_keys, objective_function)
            elif "Differential Evolution" in algorithm:
                result = optimize.differential_evolution(
                    objective_function, bounds,
                    maxiter=max_iter,
                    popsize=pop_size,
                    tol=float(self.optim_tolerance.get()),
                    workers=1,
                    updating='deferred',
                    callback=progress_callback
                )
            elif "SLSQP" in algorithm or "Gradient" in algorithm:
                result = optimize.minimize(
                    objective_function, x0, method='SLSQP',
                    bounds=bounds,
                    options={'maxiter': max_iter},
                    callback=progress_callback
                )
            elif "Nelder-Mead" in algorithm:
                result = optimize.minimize(
                    objective_function, x0, method='Nelder-Mead',
                    options={'maxiter': max_iter},
                    callback=progress_callback
                )
            else:
                # Default to differential evolution
                result = optimize.differential_evolution(
                    objective_function, bounds,
                    maxiter=max_iter,
                    popsize=pop_size,
                    callback=progress_callback
                )
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur d'optimisation:\n{e}"))
        
        finally:
            self.root.after(0, self._finalize_optimization)

    def _evaluate_design(self, config):
        """Évalue un design donné et retourne le score et les métriques avec modèle thermique amélioré."""
        # Utiliser les valeurs de base du calcul actuel
        base_results = self.results.copy()
        
        # Modifier selon la config
        wall_t = config.get("wall_thickness", base_results.get("wall_thickness_mm", 3.0))
        ch_depth = config.get("channel_depth", base_results.get("channel_depth_mm", 3.0))
        ch_width = config.get("channel_width", base_results.get("channel_width_mm", 2.0))
        n_ch = int(config.get("n_channels", base_results.get("n_channels", 48)))
        v_coolant = config.get("coolant_velocity", base_results.get("coolant_velocity", 20.0))
        p_inlet = config.get("inlet_pressure", base_results.get("inlet_pressure_bar", 60.0))
        
        # === MODÈLE THERMIQUE AMÉLIORÉ ===
        # Propriétés du matériau (depuis l'interface Optimiseur)
        if hasattr(self, 'optim_mat_props'):
            k_wall = self.optim_mat_props["k"].get()
            T_fusion = self.optim_mat_props["T_melt"].get()
            rho_wall = self.optim_mat_props["rho"].get()
        else:
            k_wall = base_results.get("wall_conductivity", 340)
            T_fusion = base_results.get("T_melt_material", 1356)
            rho_wall = base_results.get("wall_density", 8920)
        
        # Flux thermique de base
        q_flux = base_results.get("q_flux_max", 10e6)  # W/m²
        
        # Propriétés coolant
        T_coolant_in = base_results.get("T_coolant", 300)  # K
        rho_coolant = base_results.get("coolant_density", 800)  # kg/m³ (RP-1)
        mu_coolant = base_results.get("coolant_viscosity", 0.001)  # Pa.s
        Cp_coolant = base_results.get("coolant_Cp", 2000)  # J/kg.K
        k_coolant = base_results.get("coolant_k", 0.15)  # W/m.K
        
        # === GÉOMÉTRIE DES CANAUX ===
        # Diamètre hydraulique
        D_h = 4 * ch_width * ch_depth / (2 * (ch_width + ch_depth))  # mm
        D_h_m = D_h / 1000  # m
        
        # Section de passage par canal
        A_ch = ch_width * ch_depth / 1e6  # m²
        A_total = n_ch * A_ch
        
        # Longueur refroidie
        L_channel = base_results.get("L_cooled", 0.2)  # m
        
        # === CALCULS HYDRAULIQUES ===
        # Reynolds
        Re = rho_coolant * v_coolant * D_h_m / mu_coolant
        Re = max(Re, 100)  # Éviter division par zéro
        
        # Coefficient de friction (Colebrook simplifié pour turbulent)
        if Re < 2300:
            f = 64 / Re  # Laminaire
        else:
            # Blasius (turbulent lisse)
            f = 0.316 / (Re ** 0.25)
        
        # Perte de charge Darcy-Weisbach avec coefficient de pertes singulières
        K_singular = 1.5  # Entrée + sortie + coudes
        dp_friction = f * L_channel / D_h_m * rho_coolant * v_coolant**2 / 2
        dp_singular = K_singular * rho_coolant * v_coolant**2 / 2
        dp = (dp_friction + dp_singular) / 1e5  # bar
        
        # === CALCULS THERMIQUES ===
        # Prandtl
        Pr = mu_coolant * Cp_coolant / k_coolant
        
        # Nusselt (Gnielinski pour turbulent 2300 < Re < 5e6)
        if Re > 2300:
            Nu = 0.023 * Re**0.8 * Pr**0.4  # Dittus-Boelter (chauffage)
        else:
            Nu = 3.66  # Laminaire
        
        # Coefficient convectif coolant
        h_coolant = Nu * k_coolant / D_h_m
        
        # Résistance thermique de la paroi
        R_wall = (wall_t / 1000) / k_wall  # m²K/W
        
        # Efficacité d'ailette (entre les canaux)
        rib_width = (2 * np.pi * base_results.get("r_throat", 30) / 1000) / n_ch - ch_width / 1000  # m
        rib_width = max(rib_width, 0.001)  # Au moins 1mm
        m_fin = np.sqrt(2 * h_coolant / (k_wall * rib_width))
        L_fin = ch_depth / 1000
        eta_fin = np.tanh(m_fin * L_fin) / (m_fin * L_fin) if m_fin * L_fin > 0.01 else 1.0
        
        # Facteur de surface effective (approximation)
        A_ratio = 1 + 2 * ch_depth / ch_width * eta_fin  # Surfaces des parois du canal
        h_eff = h_coolant * min(A_ratio, 3.0)  # Limiter le facteur
        
        # Échauffement du coolant (approximation linéaire)
        A_cooled = base_results.get("A_cooled", 0.05)  # m²
        Q_total = q_flux * A_cooled / 2  # Flux moyen * surface
        m_dot = rho_coolant * v_coolant * A_total  # kg/s
        m_dot = max(m_dot, 0.1)  # Minimum pour éviter division par zéro
        delta_T_coolant = Q_total / (m_dot * Cp_coolant)
        T_coolant_avg = T_coolant_in + delta_T_coolant / 2
        
        # Température côté chaud de la paroi (modèle 1D)
        # T_wall = T_coolant + q/h_eff + q*R_wall
        T_wall_hot = T_coolant_avg + q_flux * (1 / h_eff + R_wall)
        
        # Saturation à T_fusion pour cas extrêmes
        T_wall_hot = min(T_wall_hot, T_fusion * 0.99)
        
        # === MASSE ===
        # Volume de la paroi (approximation cylindrique au col)
        r_avg = base_results.get("r_throat", 30) / 1000  # m
        L_cooled = base_results.get("L_cooled", 0.2)  # m
        
        # Volume paroi interne
        V_wall_inner = 2 * np.pi * r_avg * L_cooled * (wall_t / 1000)
        
        # Volume des canaux (à soustraire)
        V_channels = n_ch * (ch_width / 1000) * (ch_depth / 1000) * L_cooled
        
        # Volume total (paroi + closeout externe estimé)
        V_closeout = 2 * np.pi * (r_avg + (wall_t + ch_depth) / 1000) * L_cooled * 0.002  # 2mm closeout
        V_total = V_wall_inner + V_closeout
        
        mass = V_total * rho_wall  # kg
        
        # === MARGE THERMIQUE ===
        T_max_service = base_results.get("T_max_service", T_fusion * 0.8)
        margin = (T_max_service - T_wall_hot) / T_max_service * 100  # %
        
        # === CONTRAINTES ET PÉNALITÉS ===
        constraints_ok = True
        penalty = 0
        
        if self.optim_constraints["T_wall_max"]["active"].get():
            T_max = self.optim_constraints["T_wall_max"]["value"].get()
            if T_wall_hot > T_max:
                penalty += (T_wall_hot - T_max) ** 2 / 100  # Pénalité quadratique
                constraints_ok = False
        
        if self.optim_constraints["dp_max"]["active"].get():
            dp_max = self.optim_constraints["dp_max"]["value"].get()
            if dp > dp_max:
                penalty += (dp - dp_max) ** 2 * 10
                constraints_ok = False
        
        if self.optim_constraints["margin_min"]["active"].get():
            margin_min = self.optim_constraints["margin_min"]["value"].get()
            if margin < margin_min:
                penalty += (margin_min - margin) ** 2
                constraints_ok = False
        
        if self.optim_constraints["velocity_max"]["active"].get():
            v_max = self.optim_constraints["velocity_max"]["value"].get()
            if v_coolant > v_max:
                penalty += (v_coolant - v_max) ** 2 * 5
                constraints_ok = False
        
        # === SCORE SELON L'OBJECTIF ===
        objective = self.optim_objective.get()
        
        # Normalisation pour multi-objectif
        mass_ref = base_results.get("mass_estimate", 5.0)  # kg référence
        dp_ref = 10.0  # bar référence
        margin_ref = 30.0  # % référence
        
        if objective == "min_mass":
            score = mass + penalty
        elif objective == "min_dp":
            score = dp + penalty
        elif objective == "max_margin":
            score = -margin + penalty  # Négatif car on minimise
        else:  # multi-objectif (Pareto)
            # Normaliser chaque objectif et pondérer
            score_mass = mass / mass_ref
            score_dp = dp / dp_ref
            score_margin = -margin / margin_ref  # Négatif = maximiser
            score = 0.35 * score_mass + 0.35 * score_dp + 0.30 * score_margin + penalty
        
        metrics = {
            "T_wall": T_wall_hot,
            "dp": dp,
            "margin": margin,
            "mass": mass,
            "constraints_ok": constraints_ok,
            "Re": Re,
            "h_coolant": h_eff
        }
        
        return score, metrics

    def _update_optim_progress(self, progress, score, config, metrics):
        """Met à jour l'interface avec la progression."""
        self.optim_progress["value"] = progress
        self.optim_progress_label.configure(text=f"{progress:.0f}%")
        
        # Ajouter au tableau
        rank = len(self.optim_tree.get_children()) + 1
        values = (
            rank,
            f"{config.get('wall_thickness', '-'):.1f}" if 'wall_thickness' in config else "-",
            f"{config.get('channel_depth', '-'):.1f}" if 'channel_depth' in config else "-",
            f"{config.get('channel_width', '-'):.1f}" if 'channel_width' in config else "-",
            f"{config.get('n_channels', '-'):.0f}" if 'n_channels' in config else "-",
            f"{metrics['T_wall']:.0f} K",
            f"{metrics['dp']:.2f}",
            f"{metrics['margin']:.1f}%",
            f"{metrics['mass']:.2f}",
            f"{score:.4f}"
        )
        self.optim_tree.insert("", "end", values=values)
        
        # Mettre à jour le graphique de convergence
        if len(self.optim_history) > 1:
            self.ax_optim.clear()
            self.ax_optim.plot(self.optim_history, color=self.accent, linewidth=1.5)
            self.ax_optim.set_xlabel("Itération", color=self.text_primary)
            self.ax_optim.set_ylabel("Score (objectif)", color=self.text_primary)
            self.ax_optim.set_title("Convergence de l'optimisation", color=self.text_primary)
            self.ax_optim.tick_params(colors=self.text_primary)
            self.ax_optim.set_facecolor(self.bg_surface)
            self.fig_optim.tight_layout()
            self.canvas_optim.draw()

    def _grid_search(self, active_vars, var_keys, objective_function):
        """Recherche exhaustive sur une grille."""
        import itertools
        
        # Créer les grilles pour chaque variable
        grids = []
        for key in var_keys:
            vmin = active_vars[key]["min"].get()
            vmax = active_vars[key]["max"].get()
            step = active_vars[key]["step"].get()
            grid = np.arange(vmin, vmax + step/2, step)
            grids.append(grid)
        
        # Produit cartésien
        for combo in itertools.product(*grids):
            if self.optim_stop_flag:
                break
            objective_function(list(combo))

    def _finalize_optimization(self):
        """Finalise l'optimisation et affiche les résultats."""
        self.optim_running = False
        self.btn_run_optim.configure(state="normal")
        self.optim_progress["value"] = 100
        self.optim_progress_label.configure(text="Terminé!")
        
        if self.optim_results_list:
            # Trier par score
            sorted_results = sorted(self.optim_results_list, key=lambda x: x["score"])
            best = sorted_results[0]
            
            messagebox.showinfo("Optimisation Terminée", 
                f"Meilleure configuration trouvée:\n\n"
                f"Score: {best['score']:.4f}\n"
                f"T paroi: {best['metrics']['T_wall']:.0f} K\n"
                f"Δp: {best['metrics']['dp']:.2f} bar\n"
                f"Marge: {best['metrics']['margin']:.1f}%\n"
                f"Masse: {best['metrics']['mass']:.2f} kg\n\n"
                f"Utilisez 'Appliquer Meilleur' pour utiliser cette config.")

    def stop_optimization(self):
        """Arrête l'optimisation en cours."""
        if self.optim_running:
            self.optim_stop_flag = True
            messagebox.showinfo("Info", "Arrêt demandé... L'optimisation va s'arrêter après l'itération en cours.")

    def export_optimization_results(self):
        """Exporte les résultats d'optimisation en CSV."""
        if not hasattr(self, 'optim_results_list') or not self.optim_results_list:
            messagebox.showwarning("Attention", "Pas de résultats à exporter!")
            return
        
        f = filedialog.asksaveasfilename(defaultextension=".csv",
                                          filetypes=[("CSV files", "*.csv")],
                                          initialfile="optimization_results.csv")
        if not f:
            return
        
        try:
            with open(f, 'w', encoding='utf-8') as file:
                # En-tête
                file.write("rank,wall_thickness,channel_depth,channel_width,n_channels,")
                file.write("T_wall_K,dp_bar,margin_pct,mass_kg,score\n")
                
                sorted_results = sorted(self.optim_results_list, key=lambda x: x["score"])
                for i, r in enumerate(sorted_results, 1):
                    cfg = r["config"]
                    m = r["metrics"]
                    file.write(f"{i},")
                    file.write(f"{cfg.get('wall_thickness', ''):.2f},")
                    file.write(f"{cfg.get('channel_depth', ''):.2f},")
                    file.write(f"{cfg.get('channel_width', ''):.2f},")
                    file.write(f"{cfg.get('n_channels', ''):.0f},")
                    file.write(f"{m['T_wall']:.1f},")
                    file.write(f"{m['dp']:.3f},")
                    file.write(f"{m['margin']:.2f},")
                    file.write(f"{m['mass']:.3f},")
                    file.write(f"{r['score']:.6f}\n")
            
            messagebox.showinfo("Succès", f"Résultats exportés:\n{f}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'export:\n{e}")

    def apply_best_config(self):
        """Applique la meilleure configuration trouvée aux paramètres."""
        if not hasattr(self, 'optim_results_list') or not self.optim_results_list:
            messagebox.showwarning("Attention", "Pas de résultats d'optimisation!")
            return
        
        sorted_results = sorted(self.optim_results_list, key=lambda x: x["score"])
        best = sorted_results[0]
        cfg = best["config"]
        
        # Appliquer aux champs d'entrée correspondants
        applied = []
        
        if "wall_thickness" in cfg and hasattr(self, 'entry_wall_thickness'):
            self.entry_wall_thickness.delete(0, tk.END)
            self.entry_wall_thickness.insert(0, f"{cfg['wall_thickness']:.1f}")
            applied.append(f"Épaisseur: {cfg['wall_thickness']:.1f} mm")
        
        if "n_channels" in cfg and hasattr(self, 'cad_n_channels'):
            self.cad_n_channels.set(int(cfg['n_channels']))
            applied.append(f"N canaux: {int(cfg['n_channels'])}")
        
        if "channel_depth" in cfg and hasattr(self, 'cad_channel_depth'):
            self.cad_channel_depth.set(cfg['channel_depth'])
            applied.append(f"Prof. canaux: {cfg['channel_depth']:.1f} mm")
        
        if "channel_width" in cfg and hasattr(self, 'cad_channel_width'):
            self.cad_channel_width.set(cfg['channel_width'])
            applied.append(f"Larg. canaux: {cfg['channel_width']:.1f} mm")
        
        if applied:
            messagebox.showinfo("Configuration Appliquée", 
                "Paramètres mis à jour:\n\n" + "\n".join(applied) + 
                "\n\nRecalculez le moteur pour voir les résultats.")
        else:
            messagebox.showinfo("Info", "Aucun paramètre correspondant trouvé dans l'interface.")

    def visualize_optimizer_results(self):
        """Affiche une visualisation graphique des résultats d'optimisation."""
        if not hasattr(self, 'optim_results_list') or not self.optim_results_list:
            messagebox.showwarning("Attention", "Pas de résultats d'optimisation à visualiser!")
            return
        
        # Créer une fenêtre Toplevel
        viz_window = tk.Toplevel(self.root)
        viz_window.title("Analyse des Résultats d'Optimisation")
        viz_window.geometry("900x750")
        viz_window.configure(bg=self.bg_main)
        
        # Extraire les données
        data = self.optim_results_list
        scores = [d['score'] for d in data]
        
        # Identifier les variables qui ont varié
        vars_keys = list(data[0]['config'].keys())
        varied_vars = []
        for key in vars_keys:
            vals = [d['config'][key] for d in data]
            if max(vals) - min(vals) > 1e-6:
                varied_vars.append(key)
        
        if not varied_vars:
            ctk.CTkLabel(viz_window, text="Aucune variable n'a varié.").pack(pady=20)
            return
            
        # Variables de métriques
        metric_keys = list(data[0]['metrics'].keys())
        # Filtrer les métriques numériques
        metric_keys = [k for k in metric_keys if isinstance(data[0]['metrics'][k], (int, float))]
        
        # Contrôles
        ctrl_frame = ctk.CTkFrame(viz_window)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=10)
        
        row1 = ctk.CTkFrame(ctrl_frame)
        row1.pack(fill=tk.X, pady=5)
        
        # Mode 2D/3D
        row0 = ctk.CTkFrame(ctrl_frame)
        row0.pack(fill=tk.X, pady=(0, 5))
        ctk.CTkLabel(row0, text="Mode:").pack(side=tk.LEFT, padx=(0, 10))
        mode_var = tk.StringVar(value="2D")
        ctk.CTkRadioButton(row0, text="2D (Scatter)", variable=mode_var, value="2D", 
                          command=lambda: update_plot()).pack(side=tk.LEFT, padx=5)
        ctk.CTkRadioButton(row0, text="3D (Scatter 3D)", variable=mode_var, value="3D",
                          command=lambda: update_plot()).pack(side=tk.LEFT, padx=5)
        
        row1 = ctk.CTkFrame(ctrl_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(row1, text="Axe X:").pack(side=tk.LEFT)
        var_x = tk.StringVar(value=varied_vars[0])
        cb_x = ctk.CTkComboBox(row1, variable=var_x, values=varied_vars, width=20)
        cb_x.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(row1, text="Axe Y:").pack(side=tk.LEFT, padx=(15,0))
        var_y = tk.StringVar(value="score")
        cb_y = ctk.CTkComboBox(row1, variable=var_y, values=["score"] + metric_keys, width=20)
        cb_y.pack(side=tk.LEFT, padx=5)
        
        # Axe Z (pour mode 3D - choisir une valeur par défaut intelligente)
        default_z = varied_vars[1] if len(varied_vars) > 1 else ("score" if metric_keys else varied_vars[0])
        ctk.CTkLabel(row1, text="Axe Z:").pack(side=tk.LEFT, padx=(15,0))
        var_z = tk.StringVar(value=default_z)
        cb_z = ctk.CTkComboBox(row1, variable=var_z, values=["score"] + metric_keys + varied_vars, width=20)
        cb_z.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(row1, text="Couleur:").pack(side=tk.LEFT, padx=(15,0))
        var_c = tk.StringVar(value="score")
        cb_c = ctk.CTkComboBox(row1, variable=var_c, values=["score"] + metric_keys, width=20)
        cb_c.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(row1, text="🔄 Actualiser", command=lambda: update_plot()).pack(side=tk.RIGHT, padx=10)
        
        # Zone graphique
        fig = plt.Figure(figsize=(8, 6), dpi=100)
        fig.patch.set_facecolor(self.bg_main)
        
        canvas = FigureCanvasTkAgg(fig, master=viz_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def update_plot(event=None):
            # Nettoyer complètement la figure pour éviter les bugs de colorbar
            fig.clear()
            
            mode = mode_var.get()
            x_key = var_x.get()
            y_key = var_y.get()
            z_key = var_z.get()
            c_key = var_c.get()
            
            # Récupérer les valeurs X
            if x_key in varied_vars:
                X = [d['config'][x_key] for d in data]
            elif x_key == "score":
                X = scores
            else:
                X = [d['metrics'][x_key] for d in data]
            
            # Récupérer les valeurs Y
            if y_key == "score":
                Y = scores
            elif y_key in varied_vars:
                Y = [d['config'][y_key] for d in data]
            else:
                Y = [d['metrics'][y_key] for d in data]
            
            # Récupérer les valeurs Z (pour mode 3D)
            if z_key == "score":
                Z = scores
            elif z_key in varied_vars:
                Z = [d['config'][z_key] for d in data]
            else:
                Z = [d['metrics'][z_key] for d in data]
                
            # Récupérer les valeurs pour la couleur
            if c_key == "score":
                C = scores
            elif c_key in varied_vars:
                C = [d['config'][c_key] for d in data]
            else:
                C = [d['metrics'][c_key] for d in data]
            
            if mode == "3D":
                # Mode 3D avec scatter plot 3D
                ax = fig.add_subplot(111, projection='3d')
                self.apply_dark_axes(ax)
                
                # Scatter 3D avec couleur
                sc = ax.scatter(X, Y, Z, c=C, cmap='viridis', s=50, alpha=0.8, 
                               edgecolors='black', linewidth=0.5, depthshade=True)
                
                ax.set_xlabel(x_key, color=self.text_primary, labelpad=10)
                ax.set_ylabel(y_key, color=self.text_primary, labelpad=10)
                ax.set_zlabel(z_key, color=self.text_primary, labelpad=10)
                ax.set_title(f"Optimisation 3D: {x_key} × {y_key} × {z_key}", 
                           color=self.text_primary, pad=20)
                
                # Colorbar pour 3D
                cbar = fig.colorbar(sc, ax=ax, shrink=0.6, aspect=20, pad=0.1, label=c_key)
                cbar.ax.yaxis.label.set_color(self.text_primary)
                cbar.ax.tick_params(colors=self.text_primary)
                
                # Mettre en évidence le meilleur point en 3D
                best_idx = scores.index(min(scores))
                ax.scatter([X[best_idx]], [Y[best_idx]], [Z[best_idx]], 
                          s=200, facecolors='none', edgecolors='red', linewidth=3, 
                          label="Meilleur", marker='*')
                
                # Configuration 3D améliorée
                ax.xaxis.pane.fill = False
                ax.yaxis.pane.fill = False
                ax.zaxis.pane.fill = False
                ax.xaxis.pane.set_edgecolor(self.grid_color)
                ax.yaxis.pane.set_edgecolor(self.grid_color)
                ax.zaxis.pane.set_edgecolor(self.grid_color)
                ax.xaxis.pane.set_alpha(0.1)
                ax.yaxis.pane.set_alpha(0.1)
                ax.zaxis.pane.set_alpha(0.1)
                ax.grid(True, color=self.grid_color, alpha=0.3, linestyle='--')
                
                # Améliorer la vue 3D
                ax.view_init(elev=20, azim=45)
                
            else:
                # Mode 2D classique
                ax = fig.add_subplot(111)
                self.apply_dark_axes(ax)
                
                sc = ax.scatter(X, Y, c=C, cmap='viridis', s=50, alpha=0.8, edgecolors='none')
                
                ax.set_xlabel(x_key, color=self.text_primary)
                ax.set_ylabel(y_key, color=self.text_primary)
                ax.set_title(f"Optimisation: {y_key} vs {x_key}", color=self.text_primary)
                
                # Colorbar pour 2D
                cbar = fig.colorbar(sc, ax=ax, label=c_key)
                cbar.ax.yaxis.label.set_color(self.text_primary)
                cbar.ax.tick_params(colors=self.text_primary)
                
                # Mettre en évidence le meilleur point
                best_idx = scores.index(min(scores))
                ax.scatter([X[best_idx]], [Y[best_idx]], s=150, facecolors='none', 
                          edgecolors='red', linewidth=2, label="Meilleur", marker='*')
            
            # Légende
            ax.legend(facecolor=self.bg_surface, edgecolor=self.accent, 
                     labelcolor=self.text_primary, loc='best')
            
            canvas.draw()
        
        # Bind events using configure(command=) for CTkComboBox
        cb_x.configure(command=lambda v: update_plot())
        cb_y.configure(command=lambda v: update_plot())
        cb_z.configure(command=lambda v: update_plot())
        cb_c.configure(command=lambda v: update_plot())
        
        # Initial plot
        update_plot()

    # =====================================================================
    # ONGLET CONTRAINTES THERMOMÉCANIQUES
    # =====================================================================
    def init_stress_tab(self):
        """Initialise l'onglet Contraintes Thermomécaniques."""
        # Barre d'accent verte
        tk.Frame(self.tab_stress, height=4, bg="#27ae60").pack(fill=tk.X)
        
        # Frame principale avec scroll
        main_canvas = tk.Canvas(self.tab_stress, bg=self.bg_main, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(self.tab_stress, command=main_canvas.yview)
        scroll_frame = ctk.CTkFrame(main_canvas)
        
        scroll_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Titre
        header = ctk.CTkFrame(scroll_frame)
        header.pack(fill=tk.X, pady=(5, 10))
        ctk.CTkLabel(header, text="🛡️ Contraintes Thermomécaniques",
                  font=(UI_FONT, 14, "bold"), text_color="#27ae60").pack(side=tk.LEFT)
        
        # Section: Paramètres du matériau
        mat_frame = ctk.CTkFrame(scroll_frame)
        mat_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Sélection du matériau - utilise la même base que le solveur coolant
        row_mat = ctk.CTkFrame(mat_frame)
        row_mat.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(row_mat, text="Matériau:").pack(side=tk.LEFT)
        # Matériaux identiques au solveur coolant avec propriétés mécaniques complètes
        self.stress_materials_db = self.materials_db
        self.stress_material = ctk.CTkComboBox(row_mat, values=list(self.stress_materials_db.keys()), 
                                            width=25)
        self.stress_material.set("Cuivre-Zirconium (CuZr)")
        self.stress_material.pack(side=tk.LEFT, padx=10)
        self.stress_material.configure(command=lambda v: self.update_material_properties())
        
        # Tableau des propriétés
        props_frame = ctk.CTkFrame(mat_frame)
        props_frame.pack(fill=tk.X, pady=5)
        
        self.stress_props = {}
        properties = [
            ("E", "Module d'Young E (GPa)", 120),
            ("nu", "Coefficient Poisson ν", 0.33),
            ("alpha", "Coef. dilatation α (µm/m/K)", 17.0),
            ("sigma_y", "Limite élastique σ_y (MPa)", 250),
            ("sigma_uts", "Résistance ultime σ_uts (MPa)", 350),
            ("T_fusion", "Température fusion (K)", 1356),
        ]
        
        for row, (key, label, default) in enumerate(properties):
            self.stress_props[key] = tk.DoubleVar(value=default)
            ctk.CTkLabel(props_frame, text=label, width=30).grid(row=row, column=0, sticky="w", pady=2)
            entry = ctk.CTkEntry(props_frame, textvariable=self.stress_props[key], width=12)
            entry.grid(row=row, column=1, padx=5, pady=2)
        
        # Section: Conditions de fonctionnement
        cond_frame = ctk.CTkFrame(scroll_frame)
        cond_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.stress_conditions = {}
        conditions = [
            ("p_chamber", "Pression chambre (bar)", 50),
            ("p_coolant", "Pression coolant (bar)", 80),
            ("T_ref", "Température de référence (K)", 293),
        ]
        
        cond_grid = ctk.CTkFrame(cond_frame)
        cond_grid.pack(fill=tk.X)
        
        for col, (key, label, default) in enumerate(conditions):
            self.stress_conditions[key] = tk.DoubleVar(value=default)
            ctk.CTkLabel(cond_grid, text=label).grid(row=0, column=col*2, sticky="w", padx=5)
            ctk.CTkEntry(cond_grid, textvariable=self.stress_conditions[key], width=10).grid(row=0, column=col*2+1, padx=5)
        
        # Bouton calcul
        btn_frame = ctk.CTkFrame(scroll_frame)
        btn_frame.pack(fill=tk.X, pady=10, padx=5)
        
        ctk.CTkButton(btn_frame, text="🔬 Calculer",
                   command=self.calculate_stresses).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="📊 Export Rapport",
                   command=self.export_stress_report).pack(side=tk.LEFT, padx=5)
        
        # Section: Résultats des contraintes
        results_frame = ctk.CTkFrame(scroll_frame)
        results_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Tableau des résultats
        self.stress_results_labels = {}
        result_items = [
            ("sigma_hoop", "Contrainte circonférentielle (hoop) σ_θ", "MPa", 
             "Due à la pression interne: σ = p·r/t"),
            ("sigma_axial", "Contrainte axiale σ_x", "MPa", 
             "Due à la pression et bridage: σ = p·r/(2t)"),
            ("sigma_radial", "Contrainte radiale σ_r", "MPa", 
             "Généralement négligeable: ≈ -p/2"),
            ("sigma_thermal", "Contrainte thermique σ_th", "MPa", 
             "Due au gradient: σ = E·α·ΔT/(1-ν)"),
            ("sigma_vm", "Contrainte équivalente Von Mises σ_vm", "MPa", 
             "Critère de plasticité"),
            ("safety_factor", "Facteur de sécurité", "", 
             "SF = σ_y / σ_vm"),
            ("creep_margin", "Marge fluage", "%", 
             "Marge avant déformation permanente"),
        ]
        
        for row, (key, label, unit, tooltip) in enumerate(result_items):
            ctk.CTkLabel(results_frame, text=label, width=40).grid(row=row, column=0, sticky="w", pady=2)
            lbl_val = ctk.CTkLabel(results_frame, text_color=self.accent, width=15)
            lbl_val.grid(row=row, column=1, padx=5)
            ctk.CTkLabel(results_frame, text=unit, width=5).grid(row=row, column=2)
            ctk.CTkLabel(results_frame, text=f"  ({tooltip})", text_color=self.text_muted).grid(row=row, column=3, sticky="w")
            self.stress_results_labels[key] = lbl_val
        
        # Section: Graphique des contraintes le long de la tuyère
        graph_frame = ctk.CTkFrame(scroll_frame)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        self.fig_stress = plt.Figure(figsize=(10, 5), dpi=100)
        self.fig_stress.patch.set_facecolor(self.bg_main)
        
        self.ax_stress1 = self.fig_stress.add_subplot(121)
        self.ax_stress2 = self.fig_stress.add_subplot(122)
        
        for ax in [self.ax_stress1, self.ax_stress2]:
            ax.set_facecolor(self.bg_surface)
            ax.tick_params(colors=self.text_primary)
            ax.spines['bottom'].set_color(self.text_muted)
            ax.spines['top'].set_color(self.text_muted)
            ax.spines['left'].set_color(self.text_muted)
            ax.spines['right'].set_color(self.text_muted)
        
        self.canvas_stress = FigureCanvasTkAgg(self.fig_stress, master=graph_frame)
        self.canvas_stress.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Messages initiaux
        self.ax_stress1.text(0.5, 0.5, "Calculez d'abord le moteur\npuis les contraintes",
                            transform=self.ax_stress1.transAxes, ha='center', va='center',
                            fontsize=10, color=self.text_muted)
        self.ax_stress2.text(0.5, 0.5, "Graphique circulaire\nFacteur de sécurité",
                            transform=self.ax_stress2.transAxes, ha='center', va='center',
                            fontsize=10, color=self.text_muted)
        self.canvas_stress.draw()
        
        # Section: Tableau position par position
        detail_frame = ctk.CTkFrame(scroll_frame)
        detail_frame.pack(fill=tk.X, pady=5, padx=5)
        
        cols = ("x_mm", "T_wall", "sigma_hoop", "sigma_thermal", "sigma_vm", "SF")
        self.stress_tree = ttk.Treeview(detail_frame, columns=cols, show="headings", height=8)
        
        col_names = ["X (mm)", "T Paroi (K)", "σ_hoop (MPa)", "σ_th (MPa)", "σ_VM (MPa)", "SF"]
        col_widths = [80, 100, 100, 100, 100, 80]
        
        for col, name, width in zip(cols, col_names, col_widths):
            self.stress_tree.heading(col, text=name)
            self.stress_tree.column(col, width=width, anchor="center")
        
        scrollbar_tree = ctk.CTkScrollbar(detail_frame, orientation="vertical", command=self.stress_tree.yview)
        self.stress_tree.configure(yscrollcommand=scrollbar_tree.set)
        
        self.stress_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar_tree.pack(side=tk.RIGHT, fill=tk.Y)

    def update_material_properties(self, event=None):
        """Met à jour les propriétés selon le matériau sélectionné (depuis stress_materials_db)."""
        material = self.stress_material.get()
        
        if material in self.stress_materials_db:
            props = self.stress_materials_db[material]
            # Mapper les propriétés vers les champs de l'interface
            mapping = {
                "E": props.get("E", 120),
                "nu": props.get("nu", 0.33),
                "alpha": props.get("alpha", 17.0),
                "sigma_y": props.get("sigma_y", 250),
                "sigma_uts": props.get("sigma_uts", 350),
                "T_fusion": props.get("T_melt", 1356),
            }
            for key, value in mapping.items():
                if key in self.stress_props:
                    self.stress_props[key].set(value)

    def calculate_stresses(self):
        """Calcule les contraintes thermomécaniques dans la paroi."""
        if not self.results:
            messagebox.showwarning("Attention", "Calculez d'abord le moteur!")
            return
        
        # Récupérer les propriétés
        E = self.stress_props["E"].get() * 1e9  # GPa -> Pa
        nu = self.stress_props["nu"].get()
        alpha = self.stress_props["alpha"].get() * 1e-6  # µm/m/K -> 1/K
        sigma_y = self.stress_props["sigma_y"].get() * 1e6  # MPa -> Pa
        T_ref = self.stress_conditions["T_ref"].get()
        
        # Conditions
        p_chamber = self.stress_conditions["p_chamber"].get() * 1e5  # bar -> Pa
        p_coolant = self.stress_conditions["p_coolant"].get() * 1e5  # bar -> Pa
        
        # Géométrie
        wall_t = self.results.get("wall_thickness_mm", 3.0) / 1000  # mm -> m
        
        # Nettoyer le tableau
        for item in self.stress_tree.get_children():
            self.stress_tree.delete(item)
        
        # Calcul pour chaque position
        X_profile, R_profile = self.geometry_profile if self.geometry_profile else ([], [])
        
        # Vérifier si le profil est vide (compatible avec numpy arrays)
        if len(X_profile) == 0:
            messagebox.showwarning("Attention", "Profil géométrique non disponible!")
            return
        
        stress_data = []
        max_sigma_vm = 0
        min_SF = float('inf')
        idx_critical = 0
        
        for i, (x, r_mm) in enumerate(zip(X_profile, R_profile)):
            r = r_mm / 1000  # mm -> m
            
            # Température paroi (interpoler depuis les résultats thermiques)
            T_wall = self.results.get("T_wall_hot", 600)  # Simplification
            
            # Contrainte hoop (circonférentielle) - pression différentielle
            delta_p = p_coolant - p_chamber  # Pression nette sur la paroi
            sigma_hoop = delta_p * r / wall_t
            
            # Contrainte axiale (longitudinale)
            sigma_axial = delta_p * r / (2 * wall_t)
            
            # Contrainte radiale (environ -p/2 au milieu de la paroi)
            sigma_radial = -delta_p / 2
            
            # Contrainte thermique
            delta_T = T_wall - T_ref
            sigma_thermal = E * alpha * delta_T / (1 - nu)
            
            # Contraintes totales (superposition)
            sigma_total_hoop = sigma_hoop + sigma_thermal
            sigma_total_axial = sigma_axial + sigma_thermal
            
            # Von Mises
            sigma_vm = np.sqrt(
                sigma_total_hoop**2 + 
                sigma_total_axial**2 + 
                sigma_radial**2 -
                sigma_total_hoop * sigma_total_axial -
                sigma_total_axial * sigma_radial -
                sigma_total_hoop * sigma_radial
            )
            
            # Facteur de sécurité
            SF = sigma_y / sigma_vm if sigma_vm > 0 else float('inf')
            
            stress_data.append({
                "x": x,
                "T_wall": T_wall,
                "sigma_hoop": sigma_total_hoop / 1e6,
                "sigma_thermal": sigma_thermal / 1e6,
                "sigma_vm": sigma_vm / 1e6,
                "SF": SF
            })
            
            # Trouver le point critique
            if sigma_vm > max_sigma_vm:
                max_sigma_vm = sigma_vm
                min_SF = SF
                idx_critical = i
            
            # Ajouter au tableau (tous les 5 points pour ne pas surcharger)
            if i % 5 == 0:
                self.stress_tree.insert("", "end", values=(
                    f"{x:.1f}", f"{T_wall:.0f}",
                    f"{sigma_total_hoop/1e6:.1f}", f"{sigma_thermal/1e6:.1f}",
                    f"{sigma_vm/1e6:.1f}", f"{SF:.2f}"
                ))
        
        # Mettre à jour les résultats principaux (point critique)
        critical = stress_data[idx_critical]
        self.stress_results_labels["sigma_hoop"].configure(text=f"{critical['sigma_hoop']:.1f}")
        self.stress_results_labels["sigma_axial"].configure(text=f"{critical['sigma_hoop']/2:.1f}")
        self.stress_results_labels["sigma_radial"].configure(text="~0")
        self.stress_results_labels["sigma_thermal"].configure(text=f"{critical['sigma_thermal']:.1f}")
        self.stress_results_labels["sigma_vm"].configure(text=f"{critical['sigma_vm']:.1f}")
        
        # Couleur selon le facteur de sécurité
        if min_SF > 2.0:
            sf_color = "#27ae60"  # Vert
            status = "SÉCURITAIRE"
        elif min_SF > 1.5:
            sf_color = "#f39c12"  # Orange
            status = "ATTENTION"
        elif min_SF > 1.0:
            sf_color = "#e67e22"  # Orange foncé
            status = "CRITIQUE"
        else:
            sf_color = "#e74c3c"  # Rouge
            status = "DANGER"
        
        self.stress_results_labels["safety_factor"].configure(text=f"{min_SF:.2f} ({status})", text_color=sf_color)
        
        # Marge fluage
        T_fusion = self.stress_props["T_fusion"].get()
        T_wall_max = max(d["T_wall"] for d in stress_data)
        creep_margin = (T_fusion - T_wall_max) / T_fusion * 100
        self.stress_results_labels["creep_margin"].configure(text=f"{creep_margin:.1f}")
        
        # Mettre à jour les graphiques
        self._update_stress_plots(stress_data, X_profile, min_SF, sigma_y / 1e6)

    def _update_stress_plots(self, stress_data, X_profile, min_SF, sigma_y_mpa):
        """Met à jour les graphiques des contraintes."""
        self.fig_stress.clear()
        self.ax_stress1 = self.fig_stress.add_subplot(121)
        self.ax_stress2 = self.fig_stress.add_subplot(122, projection='polar')
        
        for ax in [self.ax_stress1]:
            ax.set_facecolor(self.bg_surface)
            ax.tick_params(colors=self.text_primary)
        self.ax_stress2.set_facecolor(self.bg_surface)
        self.ax_stress2.tick_params(colors=self.text_primary)
        
        x_vals = [d["x"] for d in stress_data]
        
        # Graphique 1: Distribution des contraintes
        self.ax_stress1.plot(x_vals, [d["sigma_hoop"] for d in stress_data], 
                            label="σ_hoop", color=self.accent, linewidth=1.5)
        self.ax_stress1.plot(x_vals, [d["sigma_thermal"] for d in stress_data], 
                            label="σ_thermal", color="#e74c3c", linewidth=1.5)
        self.ax_stress1.plot(x_vals, [d["sigma_vm"] for d in stress_data], 
                            label="σ_VM", color="#f39c12", linewidth=2)
        
        # Ligne limite élastique
        self.ax_stress1.axhline(y=sigma_y_mpa, color="#e74c3c", linestyle="--", 
                               linewidth=1.5, label=f"σ_y = {sigma_y_mpa:.0f} MPa")
        
        self.ax_stress1.set_xlabel("Position X (mm)", color=self.text_primary)
        self.ax_stress1.set_ylabel("Contrainte (MPa)", color=self.text_primary)
        self.ax_stress1.set_title("Distribution des Contraintes", color=self.text_primary)
        self.ax_stress1.legend(fontsize=8)
        self.ax_stress1.grid(True, alpha=0.3)
        
        # Graphique 2: Facteur de sécurité (jauge circulaire)
        theta = np.linspace(0, 2 * np.pi, 100)
        
        # Zone de sécurité
        sf_normalized = min(min_SF / 3, 1)  # Normaliser sur échelle 0-3
        
        # Arcs colorés
        self.ax_stress2.fill_between(theta[:int(33)], 0, 1, color='#e74c3c', alpha=0.3, label='Danger (SF<1)')
        self.ax_stress2.fill_between(theta[33:66], 0, 1, color='#f39c12', alpha=0.3, label='Attention (1-2)')
        self.ax_stress2.fill_between(theta[66:], 0, 1, color='#27ae60', alpha=0.3, label='Sûr (>2)')
        
        # Aiguille du SF actuel
        sf_angle = min_SF / 3 * 2 * np.pi
        self.ax_stress2.plot([0, sf_angle], [0, 0.9], color='white', linewidth=3)
        self.ax_stress2.scatter([sf_angle], [0.9], color='white', s=100, zorder=5)
        
        self.ax_stress2.set_title(f"Facteur de Sécurité: {min_SF:.2f}", color=self.text_primary, pad=20)
        self.ax_stress2.set_ylim(0, 1)
        
        self.fig_stress.tight_layout()
        self.canvas_stress.draw()

    def export_stress_report(self):
        """Exporte un rapport des contraintes."""
        messagebox.showinfo("Info", "Fonctionnalité d'export en développement.\n\nLes données sont affichées dans le tableau ci-dessous.")

    # =====================================================================
    # ONGLET SIMULATION TRANSITOIRE
    # =====================================================================
    def init_graphs_tab(self):
        tk.Frame(self.tab_graphs, height=4, bg=self.tab_accent.get("graphs", self.accent)).pack(fill=tk.X)
        ctrl_frame = ctk.CTkFrame(self.tab_graphs)
        ctrl_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Ligne 0 : Catégorie d'analyse
        row0 = ctk.CTkFrame(ctrl_frame)
        row0.pack(fill=tk.X, pady=2)
        
        ctk.CTkLabel(row0, text="Catégorie:").pack(side=tk.LEFT)
        self.analysis_categories = [
            "🚀 Performances CEA",
            "🌡️ Thermique Paroi",
            "💧 Refroidissement",
            "📐 Géométrie"
        ]
        self.combo_category = ctk.CTkComboBox(row0, values=self.analysis_categories, width=200)
        self.combo_category.set(self.analysis_categories[0])
        self.combo_category.pack(side=tk.LEFT, padx=5)
        self.combo_category.configure(command=self.update_analysis_options)
        
        # Ligne 1 : Mode et Résolution
        row1 = ctk.CTkFrame(ctrl_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ctk.CTkLabel(row1, text="Mode:").pack(side=tk.LEFT)
        self.combo_mode = ctk.CTkComboBox(row1, values=["2D (Courbe)", "3D (Surface)"], width=120)
        self.combo_mode.set("2D (Courbe)")
        self.combo_mode.pack(side=tk.LEFT, padx=5)
        self.combo_mode.configure(command=self.update_mode_display)
        
        ctk.CTkLabel(row1, text="Résolution:").pack(side=tk.LEFT, padx=(15, 0))
        self.spin_res = ctk.CTkEntry(row1, width=60)
        self.spin_res.insert(0, "20")
        self.spin_res.pack(side=tk.LEFT, padx=5)
        
        # Ligne 2 : Axes
        row2 = ctk.CTkFrame(ctrl_frame)
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
        
        ctk.CTkLabel(row2, text="Axe X:").pack(side=tk.LEFT)
        self.combo_x = ctk.CTkComboBox(row2, values=self.input_vars, width=200)
        self.combo_x.set(self.input_vars[1] if len(self.input_vars) > 1 else self.input_vars[0])
        self.combo_x.pack(side=tk.LEFT, padx=5)
        
        # Axe Y (caché par défaut, visible seulement en 3D)
        ctk.CTkLabel(row2, text="Axe Y:").pack(side=tk.LEFT, padx=(10, 0))
        self.combo_y = ctk.CTkComboBox(row2, values=self.input_vars, width=200)
        self.combo_y.set(self.input_vars[0])
        self.combo_y.pack(side=tk.LEFT, padx=5)
        self.label_y = row2.winfo_children()[-2]  # Référence au label "Axe Y"
        
        # Masquer l'axe Y au démarrage (mode 2D par défaut)
        self.combo_y.pack_forget()
        self.label_y.pack_forget()
        
        ctk.CTkLabel(row2, text="Sortie (Z):").pack(side=tk.LEFT, padx=(10, 0))
        self.combo_z = ctk.CTkComboBox(row2, values=self.vars_out, width=200)
        self.combo_z.set(self.vars_out[0])
        self.combo_z.pack(side=tk.LEFT, padx=5)
        
        # Ligne 3 : Ranges X et Y
        self.f_range = ctk.CTkFrame(ctrl_frame)
        self.f_range.pack(fill=tk.X, pady=2)
        
        ctk.CTkLabel(self.f_range, text="Min X:").pack(side=tk.LEFT)
        self.e_xmin = ctk.CTkEntry(self.f_range, width=6)
        self.e_xmin.insert(0, "1.0")
        self.e_xmin.pack(side=tk.LEFT, padx=2)
        
        ctk.CTkLabel(self.f_range, text="Max X:").pack(side=tk.LEFT)
        self.e_xmax = ctk.CTkEntry(self.f_range, width=6)
        self.e_xmax.insert(0, "4.0")
        self.e_xmax.pack(side=tk.LEFT, padx=2)
        
        # Champs Min Y et Max Y (cachés par défaut en mode 2D)
        ctk.CTkLabel(self.f_range, text="Min Y:").pack(side=tk.LEFT, padx=(10, 0))
        self.e_ymin = ctk.CTkEntry(self.f_range, width=6)
        self.e_ymin.insert(0, "1.5")
        self.e_ymin.pack(side=tk.LEFT, padx=2)
        
        ctk.CTkLabel(self.f_range, text="Max Y:").pack(side=tk.LEFT)
        self.e_ymax = ctk.CTkEntry(self.f_range, width=6)
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
        
        ctk.CTkButton(ctrl_frame, text="📊 Tracer Graphe", command=self.plot_manager).pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Ligne 4 : Matériaux de référence (pour thermique)
        row4 = ctk.CTkFrame(ctrl_frame)
        row4.pack(fill=tk.X, pady=2)
        
        ctk.CTkLabel(row4, text="Matériau réf.:").pack(side=tk.LEFT)
        # Use unified database but map keys to format expected by graph logic if needed
        # The unified DB keys are already descriptive
        self.materials_ref = {}
        for name, props in self.materials_db.items():
            self.materials_ref[name] = {
                "k": props["k"],
                "t_melt": props["T_melt"],
                "color": props.get("color", "blue")
            }
            
        self.combo_material = ctk.CTkComboBox(row4, values=list(self.materials_ref.keys()), width=200)
        self.combo_material.set(list(self.materials_ref.keys())[0])
        self.combo_material.pack(side=tk.LEFT, padx=5)
        
        self.var_show_melt = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(row4, text="Afficher T fusion", variable=self.var_show_melt).pack(side=tk.LEFT, padx=10)
        
        self.var_multi_materials = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(row4, text="Multi-matériaux", variable=self.var_multi_materials).pack(side=tk.LEFT, padx=5)
        
        self.progress = ctk.CTkProgressBar(self.tab_graphs, mode='indeterminate')
        self.progress.pack(side=tk.TOP, fill=tk.X, padx=10)
        
        self.fig_graph = plt.Figure(figsize=(5, 4), dpi=100)
        self.fig_graph.patch.set_facecolor(self.bg_main)
        self.canvas_graph = FigureCanvasTkAgg(self.fig_graph, master=self.tab_graphs)
        self.canvas_graph.get_tk_widget().configure(bg=self.bg_main, highlightthickness=0)
        self.canvas_graph.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def apply_dark_axes(self, axes):
        """Applique le thème sombre aux axes matplotlib (2D et 3D)."""
        if not isinstance(axes, (list, tuple, np.ndarray)):
            axes = [axes]
        
        for ax in axes:
            ax.set_facecolor(self.bg_surface)
            ax.tick_params(colors=self.text_primary, which='both')
            
            # Gestion Labels
            if hasattr(ax, "xaxis"):
                ax.xaxis.label.set_color(self.text_primary)
            if hasattr(ax, "yaxis"):
                ax.yaxis.label.set_color(self.text_primary)
            if hasattr(ax, "zaxis"): # 3D specific
                ax.zaxis.label.set_color(self.text_primary)
                ax.zaxis.set_tick_params(colors=self.text_primary)
                
            # Titre
            if ax.get_title():
                ax.title.set_color(self.text_primary)
                
            # Bordures (Spines) pour 2D
            for spine in getattr(ax, "spines", {}).values():
                spine.set_color(self.accent)
            
            # --- Optimisation Spécifique 3D ---
            # Détection si l'axe est 3D (possède l'attribut 'w_xaxis' ou 'xaxis.pane')
            if hasattr(ax, 'xaxis') and hasattr(ax.xaxis, 'pane'):
                # Supprimer les fonds gris (panes)
                ax.xaxis.pane.fill = False
                ax.yaxis.pane.fill = False
                ax.zaxis.pane.fill = False
                
                # Bordures discrètes
                ax.xaxis.pane.set_edgecolor(self.grid_color)
                ax.yaxis.pane.set_edgecolor(self.grid_color)
                ax.zaxis.pane.set_edgecolor(self.grid_color)
                
                # Transparence
                ax.xaxis.pane.set_alpha(0.1)
                ax.yaxis.pane.set_alpha(0.1)
                ax.zaxis.pane.set_alpha(0.1)
                
                # Grille 3D
                ax.grid(True, color=self.grid_color, alpha=0.3, linestyle='--')
            else:
                # Grille 2D classique
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
        ctrl_frame = ctk.CTkFrame(self.tab_database)
        ctrl_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Ligne 1: Type et recherche
        row1 = ctk.CTkFrame(ctrl_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ctk.CTkLabel(row1, text="Type:").pack(side=tk.LEFT)
        self.db_type = ctk.CTkComboBox(row1, values=["Tous", "Fuels (Carburants)", "Oxydants", "Coolants Communs"], 
                                     width=180)
        self.db_type.set("Tous")
        self.db_type.pack(side=tk.LEFT, padx=5)
        self.db_type.configure(command=lambda v: self.search_database())
        
        ctk.CTkLabel(row1, text="Recherche:").pack(side=tk.LEFT, padx=(15, 0))
        self.db_search = ctk.CTkEntry(row1, width=25)
        self.db_search.pack(side=tk.LEFT, padx=5)
        self.db_search.bind("<KeyRelease>", lambda e: self.search_database())
        
        ctk.CTkButton(row1, text="🔍 Chercher", command=self.search_database).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(row1, text="📋 Copier Nom", command=self.copy_selected_name).pack(side=tk.LEFT, padx=5)
        
        # Frame pour la liste et les détails
        content_frame = ctk.CTkFrame(self.tab_database)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Liste des propergols (gauche)
        list_frame = ctk.CTkFrame(content_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Treeview avec colonnes
        columns = ("name", "type", "t_ref", "formula")
        self.db_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        self.db_tree.heading("name")
        self.db_tree.heading("type")
        self.db_tree.heading("t_ref")
        self.db_tree.heading("formula")
        
        self.db_tree.column("name", width=120)
        self.db_tree.column("type", width=80)
        self.db_tree.column("t_ref", width=80)
        self.db_tree.column("formula", width=200)
        
        scrollbar = ctk.CTkScrollbar(list_frame, width=2, command=self.db_tree.yview)
        self.db_tree.configure(yscrollcommand=scrollbar.set)
        
        self.db_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.db_tree.bind("<<TreeviewSelect>>", self.on_propellant_select)
        
        # Détails du propergol sélectionné (droite)
        detail_frame = ctk.CTkFrame(content_frame)
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        fs = self.scaled_font_size(13)
        fs_title = self.scaled_font_size(16)
        
        self.db_details = scrolledtext.ScrolledText(
            detail_frame,
            font=(MONOSPACE_FONT, fs),
            width=50,
            height=25,
            state='disabled',
            bg=self.bg_surface,
            fg=self.text_primary,
            insertbackground=self.accent,
            highlightthickness=0,
            bd=0,
            relief=tk.FLAT,  # Style plat moderne
            selectbackground=self.accent,
            selectforeground=self.bg_main,
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
        config_frame = ctk.CTkFrame(self.tab_solver)
        config_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Bouton d'aide Wiki
        ctk.CTkButton(config_frame, text="📖 Aide Solveur",
                   command=lambda: self.open_wiki_at("7. DIMENSIONNEMENT DES CANAUX")).pack(anchor='ne', pady=(0, 5))
        
        # Base de données des matériaux avec leurs propriétés
        # Utilise la base unifiée définie dans __init__
        
        # Base de données des coolants - sera enrichie avec RocketCEA
        self.coolants_db = self.build_coolants_database()
        
        # Ligne 1: Matériau
        row1 = ctk.CTkFrame(config_frame)
        row1.pack(fill=tk.X, pady=3)
        
        ctk.CTkLabel(row1, text="Matériau:").pack(side=tk.LEFT)
        self.solver_material = ctk.CTkComboBox(row1, values=list(self.materials_db.keys()), width=220)
        self.solver_material.set(list(self.materials_db.keys())[0])
        self.solver_material.pack(side=tk.LEFT, padx=5)
        self.solver_material.configure(command=lambda v: self.update_material_info())
        
        ctk.CTkLabel(row1, text="T fusion:").pack(side=tk.LEFT, padx=(15, 0))
        self.lbl_tmelt = ctk.CTkLabel(row1, text_color=self.accent_alt)
        self.lbl_tmelt.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(row1, text="T max:").pack(side=tk.LEFT, padx=(15, 0))
        self.lbl_tmax = ctk.CTkLabel(row1, text_color=self.accent_alt2)
        self.lbl_tmax.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(row1, text="k:").pack(side=tk.LEFT, padx=(15, 0))
        self.lbl_k = ctk.CTkLabel(row1, text_color=self.accent)
        self.lbl_k.pack(side=tk.LEFT, padx=5)
        
        # Ligne 2: Épaisseur et coolant
        row2 = ctk.CTkFrame(config_frame)
        row2.pack(fill=tk.X, pady=3)
        
        ctk.CTkLabel(row2, text="Épaisseur (mm):").pack(side=tk.LEFT)
        self.solver_thickness = ctk.CTkEntry(row2, width=8)
        self.solver_thickness.insert(0, "2.0")
        self.solver_thickness.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(row2, text="Coolant:").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_coolant = ctk.CTkEntry(row2, width=15)
        self.solver_coolant.insert(0, "RP1")
        self.solver_coolant.pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(row2, text="(nom RocketCEA ou H2O)", text_color=self.text_muted).pack(side=tk.LEFT)
        
        ctk.CTkLabel(row2, text="T entrée (K):").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_tcool_in = ctk.CTkEntry(row2, width=8)
        self.solver_tcool_in.insert(0, "300")
        self.solver_tcool_in.pack(side=tk.LEFT, padx=5)
        
        # Ligne 3: Pression coolant et marge
        row3 = ctk.CTkFrame(config_frame)
        row3.pack(fill=tk.X, pady=3)
        
        ctk.CTkLabel(row3, text="P coolant (bar):").pack(side=tk.LEFT)
        self.solver_pcool = ctk.CTkEntry(row3, width=8)
        self.solver_pcool.insert(0, "30")
        self.solver_pcool.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(row3, text="Marge (%):").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_margin = ctk.CTkEntry(row3, width=8)
        self.solver_margin.insert(0, "20")
        self.solver_margin.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(row3, text="Flux (MW/m²):").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_flux = ctk.CTkEntry(row3, width=8)
        self.solver_flux.insert(0, "")
        self.solver_flux.pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(row3, text="(auto depuis sim.)", text_color=self.text_muted).pack(side=tk.LEFT)
        
        # Ligne 3b: Paramètres canaux de refroidissement
        row3b = ctk.CTkFrame(config_frame)
        row3b.pack(fill=tk.X, pady=3)
        
        ctk.CTkLabel(row3b, text="V coolant (m/s):").pack(side=tk.LEFT)
        self.solver_vcool = ctk.CTkEntry(row3b, width=8)
        self.solver_vcool.insert(0, "20")
        self.solver_vcool.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(row3b, text="Dh (mm):").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_dh = ctk.CTkEntry(row3b, width=8)
        self.solver_dh.insert(0, "3.0")
        self.solver_dh.pack(side=tk.LEFT, padx=5)
        
        ctk.CTkLabel(row3b, text="Section (m²):").pack(side=tk.LEFT, padx=(15, 0))
        self.solver_area = ctk.CTkEntry(row3b, width=8)
        self.solver_area.insert(0, "0.01")
        self.solver_area.pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(row3b, text="(surface totale canaux)", text_color=self.text_muted).pack(side=tk.LEFT)
        
        # Ligne 4: Boutons
        row4 = ctk.CTkFrame(config_frame)
        row4.pack(fill=tk.X, pady=8)
        
        ctk.CTkButton(row4, text="🛠️ Résoudre", command=self.solve_cooling).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(row4, text="🔍 Comparer Matériaux", command=self.compare_materials).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(row4, text="💧 Comparer Coolants", command=self.compare_coolants).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(row4, text="🌡️ Carte Thermique", command=self.plot_thermal_map).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(row4, text="📥 Charger Sim.", command=self.load_from_simulation).pack(side=tk.LEFT, padx=5)
        
        # === ZONE DE RÉSULTATS ===
        results_frame = ctk.CTkFrame(self.tab_solver)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        fs = self.scaled_font_size(13)
        fs_title = self.scaled_font_size(16)
        
        self.txt_solver = tk.Text(
            results_frame,
            bg=self.bg_surface,
            fg=self.text_primary,
            insertbackground=self.accent,
            font=(MONOSPACE_FONT, fs),
            highlightthickness=0,
            bd=0,
            wrap=tk.WORD,
            relief=tk.FLAT,  # Style plat moderne
            selectbackground=self.accent,
            selectforeground=self.bg_main,
            padx=10,
            pady=10,
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
        
        scrollbar = ctk.CTkScrollbar(self.txt_solver, command=self.txt_solver.yview)
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
            self.lbl_tmelt.configure(text=f"{mat['T_melt']} K")
            self.lbl_tmax.configure(text=f"{mat['T_max']} K")
            self.lbl_k.configure(text=f"{mat['k']} W/m-K")

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
            ax1.axvline(0, color='cyan', alpha=0.7, linewidth=1)
            ax1.text(0, thicknesses.max() * 0.95, 'COL', color='cyan', ha='center', fontsize=9)
            
            # === GRAPHE 2: Épaisseur critique vs position ===
            ax2.fill_between(X_mm, 0, e_max_service, color='green', alpha=0.3, label='Zone OK')
            ax2.fill_between(X_mm, e_max_service, e_melt, color='orange', alpha=0.3, label='Zone limite')
            ax2.fill_between(X_mm, e_melt, 20, color='red', alpha=0.3, label='Zone FUSION')
            
            ax2.plot(X_mm, e_melt, 'r-', linewidth=2, label=f'Épaisseur FUSION ({T_melt}K)')
            ax2.plot(X_mm, e_max_service, 'orange', linewidth=2, linelabel=f'Épaisseur T_max ({T_max_service}K)')
            
            # Marquer l'épaisseur actuelle
            e_current = float(self.solver_thickness.get())
            ax2.axhline(e_current, color='cyan', linewidth=2, linelabel=f'Épaisseur actuelle ({e_current:.1f}mm)')
            
            # Point critique (min)
            idx_min = np.argmin(e_melt)
            ax2.plot(X_mm[idx_min], e_melt[idx_min], 'ro', markersize=10)
            ax2.annotate(f'Min: {e_melt[idx_min]:.1f}mm\n(x={X_mm[idx_min]:.0f}mm)',
                        xy=(X_mm[idx_min], e_melt[idx_min]),
                        xytext=(X_mm[idx_min] + 10, e_melt[idx_min] + 2),
                        fontsize=10, color='red', fontweight='bold',
                        arrowprops=dict(color='red'))
            
            ax2.set_xlabel('Position axiale (mm)', color=self.text_primary)
            ax2.set_ylabel('Épaisseur paroi (mm)', color=self.text_primary)
            ax2.set_title('📏 ÉPAISSEUR CRITIQUE vs POSITION', color=self.text_primary, fontsize=12, fontweight='bold')
            ax2.set_ylim(0, min(20, max(e_melt) * 1.5))
            ax2.set_xlim(X_mm.min(), X_mm.max())
            ax2.legend(loc='upper right', fontsize=9, facecolor=self.bg_surface, labelcolor=self.text_primary)
            ax2.grid(True, alpha=0.2)
            ax2.axvline(0, color='cyan', alpha=0.7)
            
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
            ax3.axvline(0, color='cyan', alpha=0.5)
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
    
    def launch_textual_viewer(self):
        """Lance le viewer wiki Textual dans une nouvelle fenêtre."""
        import subprocess
        import sys
        import os
        
        script_path = os.path.join(os.path.dirname(__file__), "wiki_app.py")
        if os.path.exists(script_path):
            try:
                if sys.platform == "win32":
                    subprocess.Popen(f'start python "{script_path}"', shell=True)
                else:
                    # Tentative générique pour Linux/Mac
                    subprocess.Popen(["python3", script_path])
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de lancer le viewer:\n{e}")
        else:
            messagebox.showerror("Erreur", f"Script introuvable: {script_path}")

    def init_wiki_tab(self):
        """Onglet Wiki - Documentation complète sur l'analyse thermique"""
        # Barre de couleur en haut
        tk.Frame(self.tab_wiki, height=4, bg="#9966ff").pack(fill=tk.X)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.tab_wiki)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Titre
        title_frame = ctk.CTkFrame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ctk.CTkLabel(title_frame, 
                 font=(UI_FONT, 16, "bold"), text_color=self.accent).pack(side=tk.LEFT)
        
        # Barre d'outils
        toolbar = ctk.CTkFrame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Variable pour la recherche
        self.wiki_search_var = tk.StringVar()
        ctk.CTkLabel(toolbar).pack(side=tk.LEFT, padx=(0, 5))
        search_entry = ctk.CTkEntry(toolbar, textvariable=self.wiki_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<Return>", lambda e: self.wiki_search())
        ctk.CTkButton(toolbar, command=self.wiki_search).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(toolbar, command=self.wiki_search_next).pack(side=tk.LEFT)
        
        # Bouton pour lancer le viewer Textual
        ctk.CTkButton(toolbar, text="🚀 Viewer Avancé (Textual)", 
                      command=self.launch_textual_viewer,
                      fg_color=self.accent_alt, hover_color=self.accent).pack(side=tk.RIGHT, padx=5)
        
        # Sommaire à gauche
        paned = ttk.PanedWindow(main_frame, height=2)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Panneau sommaire
        toc_frame = ctk.CTkFrame(paned)
        paned.add(toc_frame, weight=1)
        
        # Liste du sommaire
        self.wiki_toc = tk.Listbox(toc_frame, bg=self.bg_surface, fg=self.text_primary,
                                   selectbackground=self.accent, selectforeground="#000000",
                                   font=("Consolas", 10), height=25, activestyle='none')
        self.wiki_toc.pack(fill=tk.BOTH, expand=True)
        self.wiki_toc.bind("<<ListboxSelect>>", self.wiki_goto_section)
        
        # Sections du sommaire - GUIDE ULTIME
        toc_items = [
            "════ PARTIE 1 : LES BASES ════",
            "1. Action-Réaction : Comment ça vole",
            "2. La Tuyère de Laval",
            "3. Le Problème Thermique",
            "4. Refroidissement Régénératif",
            "",
            "════ PARTIE 2 : THÉORIE AVANCÉE ════",
            "5. Chimie Combustion (NASA CEA)",
            "6. Équation de Bartz",
            "7. Dimensionnement Canaux",
            "8. Mécanique & Contraintes",
            "",
            "════ PARTIE 3 : MATÉRIAUX ════",
            "9. Critères de Sélection",
            "10. Base de Données Matériaux",
            "",
            "════ PARTIE 4 : LOGICIEL ════",
            "11. Guide de l'Interface et Analyse",
            "12. Outils Avancés et Production",
            "",
            "════ PARTIE 5 : DOCUMENTATION APPROFONDIE ════",
            "13. Introduction & Concepts",
            "   13.1 Pourquoi refroidir ?",
            "   13.2 Stratégies refroidissement",
            "   13.3 Schéma du transfert",
            "   13.4 Équations fondamentales",
            "   13.5 Ordres de grandeur",
            "14. Théorie Transfert Thermique",
            "   14.1 Conduction thermique",
            "   14.2 Convection thermique", 
            "   14.3 Nombres adimensionnels",
            "15. Modèle de Bartz Détaillé",
            "   15.1 Historique",
            "   15.2 Équation complète",
            "   15.3 Formule simplifiée",
            "   15.4 Propriétés gaz",
            "   15.5 Valeurs typiques h_g",
            "   15.6 Limitations",
            "   15.7 Autres corrélations",
            "16. Calcul Températures Paroi",
            "   16.1 Système d'équations",
            "   16.2 Calcul T_wall_hot",
            "   16.3 Calcul T_wall_cold",
            "   16.4 Profil dans la paroi",
            "   16.5 Contraintes thermiques",
            "   16.6 Régime transitoire",
            "   16.7 Température adiabatique",
            "   16.8 Calcul itératif",
            "17. Corrélations Coolant",
            "   17.1 Dittus-Boelter",
            "   17.2 Gnielinski",
            "   17.3 Régime laminaire",
            "   17.4 Régime transitoire",
            "   17.5 Ébullition sous-refroidie",
            "   17.6 Géométrie canaux",
            "   17.7 Pertes de charge",
            "   17.8 Valeurs typiques h_c",
            "18. Épaisseur Critique",
            "   18.1 Épaisseur de fusion",
            "   18.2 Épaisseur de service",
            "   18.3 Processus d'ablation",
            "   18.4 Épaisseur sacrificielle",
            "   18.5 Temps d'ablation",
            "   18.6 Ablation acceptable?",
            "   18.7 Dimensionnement",
            "   18.8 Carte thermique",
            "19. Propriétés Matériaux",
            "   19.1 Tableau récapitulatif",
            "   19.2 Alliages de cuivre",
            "   19.3 Superalliages nickel",
            "   19.4 Alliages aluminium",
            "   19.5 Métaux réfractaires",
            "   19.6 Céramiques/composites",
            "   19.7 Critères de sélection",
            "   19.8 Exemples moteurs réels",
            "20. Propriétés Coolants",
            "   20.1 Tableau récapitulatif",
            "   20.2 Hydrogène (LH2)",
            "   20.3 Oxygène (LOX)",
            "   20.4 Méthane (LCH4)",
            "   20.5 RP-1 / Kérosène",
            "   20.6 Éthanol",
            "   20.7 Hydrazines",
            "   20.8 Eau (H2O)",
            "   20.9 Ammoniac (NH3)",
            "   20.10 Sélection coolant",
            "   20.11 Propriétés vs T",
            "21. Exemples de Calcul",
            "   21.1 Exemple LOX/RP-1",
            "   21.2 Exemple LOX/LH2",
            "   21.3 Exemple LOX/CH4",
            "   21.4 Dimensionnement canaux",
            "   21.5 Élévation T coolant",
            "   21.6 Analyse dimensionnelle",
            "   21.7 Tableau récapitulatif",
            "   21.8 Exercices",
            "22. Formules Rapides",
            "   22.1 Équations fondamentales",
            "   22.2 Équation de Bartz",
            "   22.3 Nombres adimensionnels",
            "   22.4 Corrélations convection",
            "   22.5 Température paroi",
            "   22.6 Épaisseur paroi",
            "   22.7 Puissance thermique",
            "   22.8 Pertes de charge",
            "   22.9 Film cooling",
            "   22.10 Propriétés gaz",
            "   22.11 Tableau formules",
            "   22.12 Ordres de grandeur",
            "   22.13 Conversions",
            "   22.14 Constantes",
            "23. Carte Thermique 2D/3D",
            "   23.1 Effet d'ailette",
            "   23.2 Interpolation 2D",
            "   23.3 Visualisations",
            "24. Export CAD Géométrie",
            "   24.1 Génération profil",
            "   24.2 Modélisation canaux",
            "   24.3 Formats d'export",
            "25. Optimisation Automatique",
            "   25.1 Fonction Objectif",
            "   25.2 Variables décision",
            "   25.3 Contraintes",
            "   25.4 Algorithme SLSQP",
            "26. Analyse Contraintes Méca",
            "   26.1 Contraintes primaires",
            "   26.2 Contraintes thermiques",
            "   26.3 Critère Von Mises",
            "   26.4 Fatigue LCF",
            "27. Simulation Transitoire",
            "   27.1 Équation chaleur",
            "   27.2 Stabilité numérique",
            "   27.3 Phénomènes clés",
            "",
            "Références & Bibliographie",
        ]
        for item in toc_items:
            self.wiki_toc.insert(tk.END, item)
        
        # Panneau contenu
        content_frame = ctk.CTkFrame(paned)
        paned.add(content_frame, weight=4)
        
        # Zone de texte avec scrollbar
        text_frame = ctk.CTkFrame(content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Widget Text Standard (pas de HTML)
        self.wiki_text = tk.Text(text_frame, bg=self.bg_surface, fg=self.text_primary,
                                 font=(UI_FONT, 11), wrap=tk.WORD,
                                 insertbackground=self.accent, padx=20, pady=15,
                                 highlightthickness=0, bd=0,
                                 relief=tk.FLAT,  # Style plat moderne
                                 selectbackground=self.accent,
                                 selectforeground=self.bg_main)
        
        scrollbar = ctk.CTkScrollbar(text_frame, command=self.wiki_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.wiki_text.config(yscrollcommand=scrollbar.set)
        self.wiki_text.pack(fill=tk.BOTH, expand=True)
        
        # === CONFIGURATION DES STYLES TEXTE ===
        # Titres
        self.wiki_text.tag_configure("h1", font=(UI_FONT, 20, "bold"), foreground="#ff79c6", spacing1=20, spacing3=15)
        self.wiki_text.tag_configure("h2", font=(UI_FONT, 15, "bold"), foreground="#ffb86c", spacing1=18, spacing3=8)
        self.wiki_text.tag_configure("h3", font=(UI_FONT, 13, "bold"), foreground="#8be9fd", spacing1=12, spacing3=5)
        self.wiki_text.tag_configure("h4", font=(UI_FONT, 12, "bold"), foreground="#bd93f9", spacing1=8, spacing3=3)
        
        # Listes
        self.wiki_text.tag_configure("bullet", font=(UI_FONT, 11), foreground=self.text_primary, lmargin1=30, lmargin2=50, spacing1=2)
        self.wiki_text.tag_configure("numbered_list", font=(UI_FONT, 11), foreground=self.text_primary, lmargin1=30, lmargin2=50, spacing1=2)
        
        # Code et Tableaux (Monospace)
        self.wiki_text.tag_configure("code", font=("Consolas", 10), background="#1a1a2e", foreground="#50fa7b", lmargin1=40, lmargin2=40, spacing1=1)
        self.wiki_text.tag_configure("table_header", font=("Consolas", 10, "bold"), foreground="#8be9fd", background="#1a1a2e")
        self.wiki_text.tag_configure("table_row", font=("Consolas", 10), foreground="#e8f1ff", background="#1a1a2e")
        self.wiki_text.tag_configure("formula", font=("Consolas", 11, "bold"), foreground="#bd93f9", background="#1a1a2e", lmargin1=40, lmargin2=40, spacing1=3, spacing3=3)
        
        # Mises en évidence
        self.wiki_text.tag_configure("important", foreground="#ff5555", font=(UI_FONT, 11, "bold"), lmargin1=20, lmargin2=40, spacing1=3, spacing3=3)
        self.wiki_text.tag_configure("warning", foreground="#ffb347", font=(UI_FONT, 11, "bold"), background="#2a1a0a", lmargin1=20, lmargin2=40, spacing1=3, spacing3=3)
        self.wiki_text.tag_configure("success", foreground="#50fa7b", font=(UI_FONT, 11, "bold"), lmargin1=20, lmargin2=40, spacing1=3, spacing3=3)
        self.wiki_text.tag_configure("quote", font=(UI_FONT, 11, "italic"), foreground="#9fb4d3", lmargin1=50, lmargin2=50, spacing1=5, spacing3=5)
        self.wiki_text.tag_configure("highlight", background="#3d3d00", foreground="#ffff00")
        self.wiki_text.tag_configure("center", justify='center')
        self.wiki_text.tag_configure("normal", font=(UI_FONT, 11), foreground=self.text_primary, spacing1=2)
        
        # Variable pour la recherche
        self.wiki_search_pos = "1.0"
        
        # Cache pour les images (LaTeX)
        self.wiki_images = []
        
        # Charger le contenu du wiki
        self.load_wiki_content()
    
    def render_latex(self, formula, fontsize=12):
        """Renders LaTeX formula to a tk.PhotoImage using Matplotlib"""
        try:
            # Create a small figure with transparent background
            fig = Figure(figsize=(5, 0.8), dpi=100)
            fig.patch.set_facecolor(self.bg_surface)
            
            # Matplotlib requires $ for math mode or unescaped string
            if not formula.startswith('$'):
                formula = f"${formula}$"
            
            # Add text centered
            fig.text(0.5, 0.5, formula, fontsize=fontsize, 
                     color=self.text_primary, 
                     ha='center', va='center')
            
            # Save to buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png', facecolor=self.bg_surface, edgecolor='none', bbox_inches='tight', pad_inches=0.1)
            buf.seek(0)
            
            img = tk.PhotoImage(data=buf.getvalue())
            buf.close()
            return img
        except Exception as e:
            print(f"LaTeX Error: {e}")
            return None

    def load_wiki_content(self):
        """Charge le contenu du wiki depuis un fichier externe"""
        # Charger le contenu depuis le fichier externe - préférer .md si disponible
        import os
        wiki_files = [
            ('wiki.md', 'markdown'),
            ('wiki.txt', 'text')
        ]
        
        content = None
        wiki_format = 'text'
        
        for filename, format_type in wiki_files:
            wiki_file = os.path.join(os.path.dirname(__file__), filename)
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
            content = "Erreur: Aucun fichier wiki trouvé (wiki.md ou wiki.txt).\n\nPlacez un fichier wiki.md ou wiki.txt dans le même répertoire que ce script."
            wiki_format = 'text'
        
        self.wiki_text.config(state=tk.NORMAL)
        self.wiki_text.delete(1.0, tk.END)
        
        # New: Clear TOC and positions
        self.wiki_toc.delete(0, tk.END)
        self.section_positions = {}
        self.wiki_images = [] # Clear image cache
        
        # Appliquer le formatage approprié
        if wiki_format == 'markdown':
            self._load_markdown_wiki(content)
        else:
            self._load_text_wiki(content)
        
        self.wiki_text.config(state=tk.DISABLED)
    
    def _load_markdown_wiki(self, content):
        """Parseur Markdown personnalisé pour Tkinter - Avec alignement de tableaux automatique"""
        lines = content.split('\n')
        i = 0
        in_code_block = False
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            # 1. Gestion des blocs de code
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                i += 1
                continue
            
            if in_code_block:
                self.wiki_text.insert(tk.END, line + '\n', "code")
                i += 1
                continue
            
            # 1.5. LaTeX Equations (Math Mode $$...$$)
            if line.strip().startswith('$$') and line.strip().endswith('$$'):
                formula = line.strip()[2:-2].strip()
                if formula:
                    img = self.render_latex(formula, fontsize=14)
                    if img:
                        self.wiki_images.append(img)
                        self.wiki_text.image_create(tk.END, image=img)
                        self.wiki_text.insert(tk.END, '\n')
                        self.wiki_text.tag_add("center", "end-2c", "end-1c")
                    else:
                        self.wiki_text.insert(tk.END, line + '\n', "code")
                i += 1
                continue

            # 2. Gestion des Tableaux (Détection et Formatage)
            if line.strip().startswith('|'):
                # Collecter toutes les lignes du tableau
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i].strip())
                    i += 1
                
                # Traiter le tableau si valide
                if len(table_lines) >= 2:
                    self._insert_formatted_table(table_lines)
                else:
                    # Ligne isolée, traiter comme texte normal
                    self.wiki_text.insert(tk.END, table_lines[0] + '\n', "normal")
                continue
            
            # 3. Headers
            # Doit commencer par # suivi d'un espace, et ne pas être dans un bloc de code
            if line.startswith('#') and not in_code_block:
                # Vérifier qu'il y a un espace après les # (ex: "## Titre" et pas "#Commentaire")
                if not re.match(r'^#+\s', line):
                    self.wiki_text.insert(tk.END, line + '\n', "normal")
                    i += 1
                    continue

                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                tag = f"h{min(level, 4)}"
                
                # Capture position
                start_index = self.wiki_text.index("end-1c")
                
                self.wiki_text.insert(tk.END, text + '\n', tag)
                
                # Add to TOC
                indent = "  " * (level - 1)
                self.wiki_toc.insert(tk.END, indent + text)
                self.section_positions[self.wiki_toc.size()-1] = start_index

                i += 1
                continue
            
            # 4. Listes
            if re.match(r'^\s*[\*\-\+]\s+', line):
                # Remplacer le marqueur par un point bullet propre
                clean_line = re.sub(r'^\s*[\*\-\+]\s+', '• ', line)
                self.wiki_text.insert(tk.END, clean_line + '\n', "bullet")
                i += 1
                continue
            
            if re.match(r'^\s*\d+\.\s+', line):
                self.wiki_text.insert(tk.END, line + '\n', "numbered_list")
                i += 1
                continue
            
            # 5. Blockquotes / Info / Alertes
            if line.startswith('>'):
                content_text = line.lstrip('>').strip()
                if "⚠️" in content_text or "Attention" in content_text:
                    self.wiki_text.insert(tk.END, content_text + '\n', "warning")
                elif "💡" in content_text or "Note" in content_text:
                    self.wiki_text.insert(tk.END, content_text + '\n', "quote")
                else:
                    self.wiki_text.insert(tk.END, content_text + '\n', "quote")
                i += 1
                continue
            
            # 6. Texte Normal
            if line.strip():
                self.wiki_text.insert(tk.END, line + '\n', "normal")
            else:
                self.wiki_text.insert(tk.END, '\n', "normal")
            
            i += 1

    def _insert_formatted_table(self, table_lines):
        """Formate et aligne un tableau Markdown pour affichage en monospace"""
        # Parser les cellules
        rows = []
        for line in table_lines:
            # Enlever les | de début et fin et split
            cells = [c.strip() for c in line.strip('|').split('|')]
            rows.append(cells)
        
        if not rows:
            return

        # Calculer la largeur max par colonne
        num_cols = max(len(row) for row in rows)
        col_widths = [0] * num_cols
        
        for row in rows:
            for idx, cell in enumerate(row):
                if idx < num_cols:
                    # Ignorer la ligne de séparation pour le calcul de largeur (---)
                    if set(cell) <= {'-', ':', ' '}: 
                        continue
                    col_widths[idx] = max(col_widths[idx], len(cell))
        
        # Construire les lignes formatées
        for r_idx, row in enumerate(rows):
            # Est-ce la ligne de séparation ?
            is_separator = all(set(c) <= {'-', ':', ' '} for c in row) and len(row) > 0
            
            if is_separator:
                # Créer une ligne de séparation jolie
                sep_parts = []
                for w in col_widths:
                    sep_parts.append('─' * (w + 2))
                formatted_line = "┼".join(sep_parts)
                # Utiliser un style différent pour le séparateur
                self.wiki_text.insert(tk.END, "  " + formatted_line + "\n", "code")
                continue
            
            # Formater les cellules avec padding
            formatted_cells = []
            for c_idx, cell in enumerate(row):
                if c_idx < len(col_widths):
                    width = col_widths[c_idx]
                    formatted_cells.append(f" {cell:<{width}} ") # Alignement gauche par défaut
            
            line_str = "│".join(formatted_cells)
            
            # Premier rang est le header
            tag = "table_header" if r_idx == 0 else "table_row"
            self.wiki_text.insert(tk.END, "  " + line_str + "\n", tag)

    def _load_text_wiki(self, content):
        """Charge et formate le contenu texte legacy du wiki"""
        lines = content.split('\n')
        for line in lines:
            line = line.rstrip()
            if line.startswith('🔥') or '════' in line:
                clean = line.replace('════', '').strip()
                if clean: self.wiki_text.insert(tk.END, clean + '\n', "h1")
            elif re.match(r'^\s*\d+\.\s+[A-ZÀ-ÖØ-Þ]', line) or line.strip().startswith("RÉFÉRENCES"):
                self.wiki_text.insert(tk.END, line + '\n', "h2")
            elif re.match(r'^\s*\d+\.\d+', line):
                self.wiki_text.insert(tk.END, line + '\n', "h3")
            elif line.strip().startswith('───'):
                # Ignorer ou traiter comme séparateur
                pass 
            elif line.strip().startswith(('⚠️', '💀', '🔥', '✅', '❌')):
                self.wiki_text.insert(tk.END, line + '\n', "important")
            elif '│' in line or '┌' in line: # Tableaux ASCII legacy
                self.wiki_text.insert(tk.END, line + '\n', "code")
            else:
                self.wiki_text.insert(tk.END, line + '\n', "normal")



    def open_wiki_at(self, search_text):
        """Ouvre l'onglet Wiki et scrolle vers le texte spécifié"""
        self.tabs.set("📖 Wiki")
        
        # Nettoyer les anciens highlights
        self.wiki_text.tag_remove("highlight", "1.0", tk.END)
        
        # Chercher le texte (insensible à la casse)
        pos = self.wiki_text.search(search_text, "1.0", stopindex=tk.END, nocase=True)
        
        if pos:
            # Scroller vers la position
            self.wiki_text.see(pos)
            
            # Mettre en évidence la ligne entière
            line_end = f"{pos} lineend"
            self.wiki_text.tag_add("highlight", pos, line_end)
            
            # Effet visuel temporaire (flash)
            def flash(count):
                if count % 2 == 0:
                    self.wiki_text.tag_config("highlight", background=self.accent, text_color=self.bg_main)
                else:
                    self.wiki_text.tag_config("highlight", background="#3d3d00", text_color="#ffff00")
                if count > 0:
                    self.root.after(150, lambda: flash(count - 1))
            
            flash(6)
        else:
            print(f"Section wiki non trouvée: {search_text}")

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
        
        index = selection[0]
        if hasattr(self, 'section_positions') and index in self.section_positions:
            pos = self.section_positions[index]
            self.wiki_text.see(pos)
            self.wiki_text.tag_remove("highlight", "1.0", tk.END)
            self.wiki_text.tag_add("highlight", pos, f"{pos} lineend")
        else:
            # Fallback legacy (si section_positions vide ou non init)
            pass

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
            
            # --- CEA LOGIC WITH FALLBACK ---
            if HAS_ROCKETCEA:
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
                
                # Propriétés de transport au col (pour Bartz)
                try:
                    transp = ispObj.get_Throat_Transport(Pc=pc_psi, MR=mr, eps=eps)
                    # transp = [Cp, Mu, K, Pr]
                    Cp_imp = transp[0]
                    Mu_poise = transp[1] / 1000.0
                    Pr = transp[3]
                except:
                    Cp_imp = 0.5
                    Mu_poise = 0.001
                    Pr = 0.7
                    
                # Conversion SI
                Mu_si = Mu_poise * 0.1  # Pa.s
                Cp_si = Cp_imp * 4186.8  # J/kg-K
                
            else:
                # --- FALLBACK MODE (Gaz Parfait) ---
                print("⚠️ Mode Fallback (Pas de RocketCEA)")
                gamma = 1.2
                MW = 24.0  # g/mol approx
                R_univ = 8314.46
                R_gas = R_univ / MW
                
                Tc_approx = 3300.0  # K approx
                
                # Pression ratio
                pr = pe_des / pc
                
                # Mach sortie (Isentropique)
                # pr = (1 + (g-1)/2 * M^2)^(-g/(g-1))
                try:
                    Me = math.sqrt(((pr ** (-(gamma-1)/gamma)) - 1) * 2 / (gamma - 1))
                except:
                    Me = 2.5
                
                # Eps (Area ratio)
                # A/A* = 1/M * ((2 + (g-1)M^2)/(g+1))^((g+1)/(2(g-1)))
                term = (2 + (gamma - 1) * Me**2) / (gamma + 1)
                eps = (1 / Me) * (term ** ((gamma + 1) / (2 * (gamma - 1))))
                
                # C* approx
                # C* = sqrt(R*Tc) / Gamma_func
                Gamma_func = math.sqrt(gamma) * (2 / (gamma + 1)) ** ((gamma + 1) / (2 * (gamma - 1)))
                cstar_mps = math.sqrt(R_gas * Tc_approx) / Gamma_func
                
                # Isp approx
                # Cf approx
                cf_vac = Gamma_func * math.sqrt(2 * gamma / (gamma - 1) * (1 - pr ** ((gamma - 1) / gamma))) + eps * (pe_des - 0) / pc
                cf_amb = cf_vac - eps * (pamb / pc)
                
                isp_vac = cstar_mps * cf_vac / 9.81
                isp_amb = cstar_mps * cf_amb / 9.81
                
                tc_k = Tc_approx
                tt_k = tc_k * (2 / (gamma + 1))
                te_k = tc_k * (pr ** ((gamma - 1) / gamma))
                
                # Transport properties approx
                Mu_si = 8.0e-5  # Pa.s (approx gaz chaud)
                Cp_si = 2000.0  # J/kg-K
                Pr = 0.8
            
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
            self.ax_flux.axhline(q_mean, color='green', linewidth=1.5, 
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
            self.ax_flux.axhline(0, color=self.grid_color, alpha=0.4)
            
            # Graphe Température avec projections
            self.ax_temp.plot(X_mm, T_gas_list, 'orange', linewidth=2, label="T gaz (adiabatique)")
            self.ax_temp.plot(X_mm, T_wall_hot_list, 'red', linewidth=2, label=f"T paroi hot ({t_wall_hot_max:.0f} K max)")
            self.ax_temp.axhline(t_wall_limit, color='blue', linewidth=2, 
                                label=f"T paroi cold ({t_wall_limit:.0f} K)")
            
            # Moyenne température gaz
            self.ax_temp.axhline(t_gas_mean, color='darkorange', linewidth=1.5,
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
            
            # Mettre à jour la carte thermique 2D
            self.update_heatmap()
            
            # Géométrie 2D
            self.draw_engine(X_mm, Y_mm)
            
            # --- SUMMARY ---
            thrust_n = mdot * isp_amb * 9.81
            thrust_kn = thrust_n / 1000  # Convertir en kN
            
            # Récupérer le nom du matériau pour le résumé
            mat_name = self.global_material_var.get() if hasattr(self, 'global_material_var') else "Inconnu"
            
            summary = f"""═══════════════════════════════════
    SITH MISCHUNG COMBUSTION : DARK SIDE EDITION v6.3
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
Matériau        : {mat_name}
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
            # Mettre à jour le widget texte (en activant l'état 'normal' temporairement)
            self.txt_summary.config(state='normal')
            self.txt_summary.delete(1.0, tk.END)
            self.insert_colored_summary(summary, cooling_status, coolant_warning)
            self.txt_summary.config(state='disabled')
            
            # Raw CEA output avec coloration
            try:
                if HAS_ROCKETCEA:
                    raw = ispObj.get_full_cea_output(Pc=pc_psi, MR=mr, eps=eps, pc_units='bar', output='calories')
                    self.txt_cea.config(state='normal')
                    self.txt_cea.delete(1.0, tk.END)
                    self.insert_colored_cea(raw)
                    self.txt_cea.config(state='disabled')
            except:
                pass
            
            self.tabs.set("📊 Résumé")
            
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
        self.ax_visu.axvline(0, color=self.accent_alt, alpha=0.7, label='Col')
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
            
            # Mise à jour spécifique du matériau global si présent
            if "material_name" in design_data and hasattr(self, 'global_material_var'):
                self.global_material_var.set(design_data["material_name"])
                # Mettre à jour les champs dépendants (conductivité, etc) sans écraser si ils sont customisés
                # self.on_global_material_change() # Optionnel: décommenter pour forcer le reset des props matériau
            
            # Charger les résultats si disponibles
            if "_results" in design_data:
                self.results = design_data["_results"]
                
                # Reconstruire le profil géométrique si disponible
                if "thermal_profile" in self.results:
                    try:
                        X = np.array(self.results["thermal_profile"]["X_mm"])
                        Y = np.array(self.results["thermal_profile"]["Y_mm"])
                        self.geometry_profile = (X, Y)
                        
                        # Rafraîchir la visualisation 2D
                        self.draw_engine(X, Y)
                        
                        # Rafraîchir le résumé avec un message temporaire
                        # Le prochain calcul régénérera tout
                        self.txt_summary.config(state='normal')
                        self.txt_summary.delete(1.0, tk.END)
                        self.txt_summary.insert(tk.END, "✅ Paramètres et résultats chargés avec succès.\n\n", "success")
                        self.txt_summary.insert(tk.END, "Visualisation 2D mise à jour.\n", "label")
                        self.txt_summary.insert(tk.END, "Pour voir tous les détails et recalculer, cliquez sur 'CALCULER TOUT'.\n", "warning")
                        self.txt_summary.config(state='disabled')
                        
                    except Exception as e:
                        print(f"Erreur reconstruction géométrie: {e}")
            else:
                # Aucun résultat sauvegardé, on efface juste les résultats existants
                self.results = {}
                self.geometry_profile = None
                
                # Message dans le résumé
                self.txt_summary.config(state='normal')
                self.txt_summary.delete(1.0, tk.END)
                self.txt_summary.insert(tk.END, "✅ Paramètres chargés avec succès.\n\n", "success")
                self.txt_summary.insert(tk.END, "Cliquez sur 'CALCULER TOUT' pour générer les résultats.\n", "warning")
                self.txt_summary.config(state='disabled')
            
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
        self.combo_x.configure(values=self.input_vars)
        self.combo_x.set(self.input_vars[0])
        self.combo_y.configure(values=self.input_vars)
        self.combo_y.set(self.input_vars[0])
        self.combo_z.configure(values=self.vars_out)
        self.combo_z.set(self.vars_out[0])

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
        self.combo_z.set(self.vars_out[0])
        
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
        
        # Surface 3D améliorée avec meilleures options visuelles
        # Utiliser une colormap plus moderne et visible
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', linewidth=0, 
                               antialiased=True, alpha=0.9, shade=True,
                               edgecolor='none', rstride=1, cstride=1)
        
        # Ajouter des courbes de niveau sur la surface pour plus de clarté
        ax.contour(X, Y, Z, zdir='z', offset=Z.min() - (Z.max() - Z.min()) * 0.1, 
                  cmap='viridis', alpha=0.5, linewidths=1)
        
        # Labels avec noms complets
        ax.set_xlabel(mode_x, color=self.text_primary, labelpad=12, fontsize=11)
        ax.set_ylabel(mode_y, color=self.text_primary, labelpad=12, fontsize=11)
        ax.set_zlabel(var_z, color=self.text_primary, labelpad=12, fontsize=11)
        
        # Titre
        ax.set_title(f"Surface 3D: {var_z} = f({mode_x}, {mode_y})", 
                    color=self.text_primary, fontsize=13, pad=20)
        
        # Colorbar améliorée
        cb = self.fig_graph.colorbar(surf, ax=ax, shrink=0.6, aspect=25, pad=0.1, label=var_z)
        cb.ax.yaxis.set_tick_params(color=self.text_primary)
        cb.ax.yaxis.label.set_color(self.text_primary)
        plt.setp(cb.ax.get_yticklabels(), color=self.text_primary)
        
        # Configuration 3D améliorée pour meilleure visibilité
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor(self.grid_color)
        ax.yaxis.pane.set_edgecolor(self.grid_color)
        ax.zaxis.pane.set_edgecolor(self.grid_color)
        ax.xaxis.pane.set_alpha(0.05)
        ax.yaxis.pane.set_alpha(0.05)
        ax.zaxis.pane.set_alpha(0.05)
        
        # Grille améliorée
        ax.grid(True, color=self.grid_color, alpha=0.3, linestyle='--', linewidth=0.5)
        
        # Vue 3D optimale
        ax.view_init(elev=25, azim=45)
        
        # Couleurs des axes
        ax.xaxis.label.set_color(self.text_primary)
        ax.yaxis.label.set_color(self.text_primary)
        ax.zaxis.label.set_color(self.text_primary)
        ax.tick_params(colors=self.text_primary, labelsize=9)
        
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
                ax.axhline(y=mat["t_melt"], color=color, alpha=0.5, 
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
            ax.axhline(y=T_boil, color='red', linelabel=f"T ébullition: {T_boil}K")
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

    def on_closing(self):
        """Gère la fermeture propre de l'application."""
        import sys
        import os
        
        # Fermer toutes les fenêtres secondaires
        if hasattr(self, 'heatmap_window') and self.heatmap_window is not None:
            try:
                self.heatmap_window.destroy()
            except:
                pass
        
        # Fermer la fenêtre principale
        try:
            self.root.destroy()
        except:
            pass
        
        # Forcer l'arrêt du processus Python
        try:
            sys.exit(0)
        except:
            os._exit(0)


if __name__ == "__main__":
    # Utiliser CustomTkinter comme fenêtre principale
    root = ctk.CTk()
    root.configure(fg_color="#0a0a0f")
    app = RocketApp(root)
    root.mainloop()
