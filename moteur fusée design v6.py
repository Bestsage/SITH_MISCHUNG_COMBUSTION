import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np
from rocketcea.cea_obj import CEA_Obj
import math
import json
import os
from datetime import datetime

# Essayer d'importer ezdxf, sinon on désactive l'export DXF
try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False

class RocketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rocket Engine Designer v6.1 (PROMETHEUS - Regen Cooling)")
        self.root.geometry("1600x1000")
        
        # --- VARIABLES ---
        self.inputs = {}
        self.results = {}
        self.geometry_profile = None  # Pour stocker X, Y du profil
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- LAYOUT PRINCIPAL ---
        main_frame = ttk.Frame(root)
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
        
        self.tabs.add(self.tab_summary, text="📊 Résumé")
        self.tabs.add(self.tab_visu, text="Visualisation 2D")
        self.tabs.add(self.tab_thermal, text="Analyse Thermique (Bartz)")
        self.tabs.add(self.tab_graphs, text="Analyses Paramétriques")
        self.tabs.add(self.tab_cea, text="Sortie NASA CEA (Raw)")
        self.tabs.add(self.tab_database, text="🔍 Base de Données")
        
        self.create_inputs(left_panel)
        self.init_summary_tab()
        self.init_visu_tab()
        self.init_thermal_tab()
        self.init_cea_tab()
        self.init_graphs_tab()
        self.init_database_tab()

    def create_inputs(self, parent):
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
        
        ttk.Button(parent, text="🔥 CALCULER TOUT (CEA + THERMIQUE)", command=self.run_simulation).grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
        row += 1
        
        # Boutons de sauvegarde/chargement
        ttk.Button(parent, text="💾 Sauvegarder Paramètres", command=self.save_design).grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
        row += 1
        ttk.Button(parent, text="📂 Charger Paramètres", command=self.load_design).grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
        row += 1
        
        # Bouton d'export DXF et graphes
        ttk.Button(parent, text="💾 EXPORTER DXF", command=self.export_dxf).grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")
        row += 1
        ttk.Button(parent, text="📊 Exporter Graphes HD", command=self.export_graphs_hd).grid(row=row, column=0, columnspan=2, pady=5, sticky="ew")

    def get_val(self, key):
        var, type_ = self.inputs[key]
        return type_(var.get())

    # --- TABS INIT ---
    def init_summary_tab(self):
        """Onglet Résumé - Affiche les résultats des calculs"""
        summary_frame = ttk.Frame(self.tab_summary)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.txt_summary = tk.Text(summary_frame, bg="#f0f0f0", font=("Consolas", 10))
        self.txt_summary.pack(fill=tk.BOTH, expand=True)
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(self.txt_summary, command=self.txt_summary.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_summary.config(yscrollcommand=scrollbar.set)

    def init_visu_tab(self):
        self.fig_visu, self.ax_visu = plt.subplots(figsize=(5, 5))
        self.canvas_visu = FigureCanvasTkAgg(self.fig_visu, master=self.tab_visu)
        self.canvas_visu.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def init_cea_tab(self):
        self.txt_cea = scrolledtext.ScrolledText(self.tab_cea, font=("Consolas", 10), state='disabled')
        self.txt_cea.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def init_thermal_tab(self):
        self.fig_thermal, (self.ax_flux, self.ax_temp) = plt.subplots(2, 1, figsize=(6, 6), sharex=True)
        self.canvas_thermal = FigureCanvasTkAgg(self.fig_thermal, master=self.tab_thermal)
        self.canvas_thermal.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.fig_thermal.subplots_adjust(hspace=0.3)

    def init_graphs_tab(self):
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
        
        ttk.Label(row1, text="Résolution:").pack(side=tk.LEFT, padx=(15, 0))
        self.spin_res = ttk.Spinbox(row1, from_=5, to=100, width=5)
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
        
        ttk.Label(row2, text="Sortie (Y/Z):").pack(side=tk.LEFT, padx=(10, 0))
        self.combo_z = ttk.Combobox(row2, values=self.vars_out, width=22, state="readonly")
        self.combo_z.current(0)
        self.combo_z.pack(side=tk.LEFT, padx=5)
        
        # Ligne 3 : Ranges
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
        self.canvas_graph = FigureCanvasTkAgg(self.fig_graph, master=self.tab_graphs)
        self.canvas_graph.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def init_database_tab(self):
        """Onglet Base de Données - Explorateur de propergols RocketCEA"""
        
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
        
        self.db_details = scrolledtext.ScrolledText(detail_frame, font=("Consolas", 10), 
                                                      width=50, height=25, state='disabled')
        self.db_details.pack(fill=tk.BOTH, expand=True)
        
        # Charger la base de données au démarrage
        self.root.after(100, self.load_database)
    
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
        """Affiche les détails du propergol sélectionné"""
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
        
        # Construire les détails
        t_ref = prop['t_ref'] if prop['t_ref'] is not None else 298
        details = f"""═══════════════════════════════════════
  PROPERGOL: {prop['name']}
═══════════════════════════════════════

Type            : {prop['type']}
T référence     : {t_ref:.2f} K ({t_ref-273.15:.1f}°C)

"""
        
        # Ajouter les propriétés thermiques si disponibles
        if prop['type'] == 'Coolant':
            details += "--- PROPRIÉTÉS COOLANT ---\n"
            details += f"Info: {prop['formula']}\n\n"
            details += "Utilisable directement comme coolant externe.\n"
            details += "Tapez ce nom dans le champ 'Coolant' du simulateur.\n"
        
        elif prop['type'] == 'Fuel':
            from rocketcea.blends import fuelCards, getFuelRefTempDegK, getFloatTokenFromCards
            
            details += "--- CARTE NASA CEA ---\n"
            if prop['cards']:
                for card in prop['cards']:
                    details += f"{card}\n"
            
            details += "\n--- PROPRIÉTÉS EXTRAITES ---\n"
            try:
                cards = fuelCards.get(prop['name'], [])
                rho = getFloatTokenFromCards(cards, 'rho')
                if rho:
                    details += f"Densité (rho)   : {rho:.4f} g/cm³ ({rho*1000:.1f} kg/m³)\n"
                
                # Chercher h,cal (enthalpie)
                for card in cards:
                    if 'h,cal' in card:
                        import re
                        match = re.search(r'h,cal=(-?\d+\.?\d*)', card)
                        if match:
                            h_cal = float(match.group(1))
                            details += f"Enthalpie (h)   : {h_cal:.1f} cal/mol\n"
            except Exception as e:
                details += f"Erreur extraction: {e}\n"
            
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
                details += f"\n--- PROPRIÉTÉS THERMIQUES (table interne) ---\n"
                details += f"Cp liquide      : {cp_table[prop['name']]} J/kg-K\n"
            if prop['name'] in hvap_table:
                details += f"Hvap            : {hvap_table[prop['name']]} kJ/kg\n"
            if prop['name'] in t_crit_table:
                details += f"T critique      : {t_crit_table[prop['name']]} K\n"
            
            details += "\n--- UTILISATION ---\n"
            details += f"CEA Fuel    : Tapez '{prop['name']}' dans Carburant (CEA)\n"
            details += f"Coolant     : Tapez '{prop['name']}' dans Coolant (Auto=fuel)\n"
        
        elif prop['type'] == 'Oxydant':
            from rocketcea.blends import oxCards, getOxRefTempDegK, getFloatTokenFromCards
            
            details += "--- CARTE NASA CEA ---\n"
            if prop['cards']:
                for card in prop['cards']:
                    details += f"{card}\n"
            
            details += "\n--- PROPRIÉTÉS EXTRAITES ---\n"
            try:
                cards = oxCards.get(prop['name'], [])
                rho = getFloatTokenFromCards(cards, 'rho')
                if rho:
                    details += f"Densité (rho)   : {rho:.4f} g/cm³ ({rho*1000:.1f} kg/m³)\n"
            except Exception as e:
                details += f"Erreur extraction: {e}\n"
            
            details += "\n--- UTILISATION ---\n"
            details += f"CEA Oxydant : Tapez '{prop['name']}' dans Oxydant (CEA)\n"
            details += f"Coolant     : Peut être utilisé comme coolant (LOX cooling)\n"
        
        # Afficher
        self.db_details.config(state='normal')
        self.db_details.delete(1.0, tk.END)
        self.db_details.insert(tk.END, details)
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
            
            # Stocker Q_total_kW dans self.results pour l'accès depuis les analyses paramétriques
            self.results["Q_total_kW"] = Q_total_kW
            
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
            self.ax_flux.clear()
            self.ax_temp.clear()
            
            # Graphe Flux avec projections
            self.ax_flux.plot(X_mm, Flux_list, 'r-', linewidth=2, label='Flux thermique')
            self.ax_flux.set_ylabel("Flux (MW/m²)", color='r')
            self.ax_flux.set_title("Profil de Flux Thermique (Bartz)")
            self.ax_flux.grid(True, alpha=0.3)
            
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
            
            self.ax_flux.legend(loc='upper right', fontsize=8)
            self.ax_flux.axhline(0, color='gray', linestyle='-', alpha=0.3)
            
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
            self.ax_temp.legend(loc='upper right', fontsize=8)
            self.ax_temp.grid(True, alpha=0.3)
            
            self.canvas_thermal.draw()
            
            # Géométrie 2D
            self.draw_engine(X_mm, Y_mm)
            
            # --- SUMMARY ---
            thrust_n = mdot * isp_amb * 9.81
            thrust_kn = thrust_n / 1000  # Convertir en kN
            
            summary = f"""═══════════════════════════════════
    PROMETHEUS v6.1 - ENGINE REPORT
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
            self.txt_summary.insert(tk.END, summary)
            
            # Raw CEA output
            try:
                raw = ispObj.get_full_cea_output(Pc=pc_psi, MR=mr, eps=eps, pc_units='bar', output='calories')
                self.txt_cea.config(state='normal')
                self.txt_cea.delete(1.0, tk.END)
                self.txt_cea.insert(tk.END, raw)
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
        self.ax_visu.plot(X, Y, 'k', linewidth=2)
        self.ax_visu.plot(X, -Y, 'k', linewidth=2)
        self.ax_visu.fill_between(X, Y, -Y, color='#ff7f50', alpha=0.2)
        self.ax_visu.set_aspect('equal')
        self.ax_visu.set_title(f"Géométrie Moteur - {self.get_val('name')}")
        self.ax_visu.set_xlabel("Position axiale (mm)")
        self.ax_visu.set_ylabel("Rayon (mm)")
        self.ax_visu.grid(True, alpha=0.3)
        self.ax_visu.axvline(0, color='red', linestyle='--', alpha=0.5, label='Col')
        self.ax_visu.legend()
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
            self.fig_graph.savefig(png_file, dpi=300, bbox_inches='tight', facecolor='white')
            
            # Export en PDF (vecteur)
            pdf_file = os.path.join(export_folder, f"{title}.pdf")
            self.fig_graph.savefig(pdf_file, format='pdf', bbox_inches='tight', facecolor='white')
            
            # Export en SVG (vecteur)
            svg_file = os.path.join(export_folder, f"{title}.svg")
            self.fig_graph.savefig(svg_file, format='svg', bbox_inches='tight', facecolor='white')
            
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
        self.combo_z['values'] = self.vars_out
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
            ax.plot(X_vals, Y_vals, 'b-', linewidth=2, marker='o', markersize=3)
            ax.set_xlabel(mode_x)
            ax.set_ylabel(var_out)
            ax.set_title(f"{var_out} vs {mode_x}")
            ax.grid(True, alpha=0.3)
            
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
        except:
            xmin, xmax = 1.0, 4.0
        
        mode_x = self.combo_x.get()
        var_z = self.combo_z.get()
        
        # X = variable choisie, Y = O/F ou Pression
        X_range = np.linspace(xmin, xmax, steps)
        
        if "O/F" in mode_x:
            Y_range = np.linspace(5, 30, steps)  # Pression
            y_label = "Pression (bar)"
        else:
            Y_range = np.linspace(1.5, 4.0, steps)  # O/F
            y_label = "O/F Ratio"
        
        X, Y = np.meshgrid(X_range, Y_range)
        Z = np.zeros_like(X)
        
        pe_def = self.get_val("pe")
        pamb_def = self.get_val("pamb")
        
        for i in range(steps):
            for j in range(steps):
                vx = X[i, j]
                vy = Y[i, j]
                
                if "O/F" in mode_x:
                    mr = vx
                    pc = vy
                elif "Pression Chambre" in mode_x:
                    pc = vx
                    mr = vy
                else:
                    pc = self.get_val("pc")
                    mr = vy
                
                pc_psi = pc * 14.5038
                pe_psi = pe_def * 14.5038
                pamb_psi = pamb_def * 14.5038
                
                eps_ov = vx if "Expansion" in mode_x else 0
                
                Z[i, j] = self.get_cea_value_safe(ispObj, pc_psi, mr, pe_psi, eps_ov, pamb_psi, var_z)
        
        surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=True)
        ax.set_xlabel(mode_x.split(" ")[0])
        ax.set_ylabel(y_label)
        ax.set_zlabel(var_z.split(" ")[0])
        self.fig_graph.colorbar(surf, shrink=0.5, aspect=5)
        
        self.canvas_graph.draw()

    # ==========================================================================
    # ANALYSE THERMIQUE PARAMÉTRIQUE
    # ==========================================================================
    def plot_thermal_parametric(self):
        """Analyse paramétrique thermique - T paroi vs épaisseur, conductivité, etc."""
        self.fig_graph.clear()
        ax = self.fig_graph.add_subplot(111)
        
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
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=7, ncol=min(2, len(materials_to_plot)+1), framealpha=0.95)
        
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
        
        ax.plot(X_vals, Y_vals, 'b-', linewidth=2, marker='o', markersize=3)
        
        # Ligne d'ébullition si température
        if "T Sortie" in var_out:
            ax.axhline(y=T_boil, color='red', linestyle='--', label=f"T ébullition: {T_boil}K")
            ax.legend()
        
        ax.set_xlabel(mode_x)
        ax.set_ylabel(var_out)
        ax.set_title(f"Analyse Refroidissement: {var_out} vs {mode_x}")
        ax.grid(True, alpha=0.3)
        
        self.canvas_graph.draw()

    def plot_geometry_parametric(self):
        """Analyse paramétrique géométrique"""
        self.fig_graph.clear()
        ax = self.fig_graph.add_subplot(111)
        
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
        
        ax.plot(X_vals, Y_vals, 'g-', linewidth=2, marker='s', markersize=4)
        ax.set_xlabel(mode_x)
        ax.set_ylabel(var_out)
        ax.set_title(f"Analyse Géométrie: {var_out} vs {mode_x}")
        ax.grid(True, alpha=0.3)
        
        self.canvas_graph.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = RocketApp(root)
    root.mainloop()
