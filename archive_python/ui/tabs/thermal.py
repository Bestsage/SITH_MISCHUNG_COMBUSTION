
import tkinter as tk
import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import *
from utils import *

def init(app):
    """Initialise l'onglet Thermique."""
    # Créer les frames principales (gauche: résultats, droite: graphique)
    thermal_main = ctk.CTkFrame(app.tab_thermal, fg_color="transparent")
    thermal_main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # --- Colonne Gauche : Résultats textuels ---
    left_col = ctk.CTkFrame(thermal_main, width=350, fg_color=app.bg_panel, corner_radius=10)
    left_col.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
    
    # En-tête
    header = ctk.CTkFrame(left_col, height=40, fg_color=app.tab_accent.get("thermal", app.accent))
    header.pack(fill=tk.X)
    ctk.CTkLabel(header, text="RÉSULTATS THERMIQUES", text_color=app.bg_main, 
                 font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
    
    # Scrollable frame pour les résultats
    app.thermal_results_frame = ctk.CTkScrollableFrame(left_col, fg_color="transparent")
    app.thermal_results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Labels pour les résultats (dictionnaire global pour mise à jour facile)
    app.thermal_labels = {}
    
    sections = [
        ("🔥 Chambre", ["T_gas_chambre", "h_g_chambre", "Flux_chambre", "T_paroi_gaz_chambre"]),
        ("⚡ Col", ["T_gas_col", "h_g_col", "Flux_col", "T_paroi_gaz_col"]),
        ("💨 Sortie", ["T_gas_sortie", "h_g_sortie", "Flux_sortie", "T_paroi_gaz_sortie"]),
        ("❄️ Refroidissement", ["T_coolant_out", "Delta_T_coolant", "Q_total", "Vitesse_coolant", "Re_coolant", "h_coolant", "DP_coolant"]),
        ("⚠️ Sécurité", ["Marge_Ebullition", "T_paroi_max", "Ratio_T_fusion"])
    ]
    
    for section_name, keys in sections:
        sec_frame = ctk.CTkFrame(app.thermal_results_frame, fg_color=app.bg_surface, corner_radius=6)
        sec_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(sec_frame, text=section_name, text_color=app.accent_alt,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        for key in keys:
            row = ctk.CTkFrame(sec_frame, fg_color="transparent", height=20)
            row.pack(fill=tk.X, padx=10, pady=1)
            
            # Nom lisible
            readable_name = key.replace("_", " ")
            ctk.CTkLabel(row, text=readable_name, text_color=app.text_muted,
                         font=ctk.CTkFont(size=11)).pack(side=tk.LEFT)
            
            value_lbl = ctk.CTkLabel(row, text="-", text_color=app.text_primary,
                                     font=ctk.CTkFont(size=11, weight="bold"))
            value_lbl.pack(side=tk.RIGHT)
            app.thermal_labels[key] = value_lbl

    # --- Colonne Droite : Graphiques ---
    right_col = ctk.CTkFrame(thermal_main, fg_color=app.bg_panel, corner_radius=10)
    right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Contrôles graphiques
    graph_ctrl = ctk.CTkFrame(right_col, height=40, fg_color=app.bg_surface)
    graph_ctrl.pack(fill=tk.X, padx=5, pady=5)
    
    ctk.CTkLabel(graph_ctrl, text="Vue:", text_color=app.text_primary).pack(side=tk.LEFT, padx=10)
    
    app.thermal_view_var = tk.StringVar(value="Températures")
    ctk.CTkSegmentedButton(graph_ctrl, values=["Températures", "Flux", "Coef. Échange", "Coolant"],
                           variable=app.thermal_view_var,
                           selected_color=app.accent_alt, selected_hover_color=app.accent_alt3,
                           command=lambda x: update_plot(app)).pack(side=tk.LEFT, padx=10)
    
    
    # Bouton Export CSV
    ctk.CTkButton(graph_ctrl, text="💾 Export CSV", width=100,
                  fg_color=app.grid_color, hover_color=app.accent,
                  command=lambda: export_thermal_csv(app)).pack(side=tk.RIGHT, padx=10)

    # Zone graphique
    app.fig_thermal = plt.Figure(figsize=(8, 6), dpi=100)
    app.fig_thermal.patch.set_facecolor(app.bg_panel)
    
    app.canvas_thermal = FigureCanvasTkAgg(app.fig_thermal, master=right_col)
    app.canvas_thermal.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Initialiser avec un graphique vide stylisé
    ax = app.fig_thermal.add_subplot(111)
    app.apply_dark_axes(ax)
    ax.text(0.5, 0.5, "Lancez un calcul pour voir les résultats", 
            color=app.text_muted, ha='center', va='center')
    app.canvas_thermal.draw()

def update(app):
    """Rafraîchit l'onglet Thermique."""
    if not hasattr(app, 'results') or 'thermal_profile' not in app.results:
        return
        
    # 1. Mettre à jour les labels
    _update_results_text(app)
    
    # 2. Mettre à jour le graphique
    update_plot(app)

def _update_results_text(app):
    """Met à jour les valeurs textuelles."""
    res = app.results
    profile = res.get("thermal_profile", {})
    
    # Mapper les clés internes vers les labels
    # Note: Ceci est une version simplifiée, il faudrait extraire les valeurs précises des vecteurs
    # Pour l'instant on prend les valeurs moyennes ou max gloables déjà calculées si dispo
    
    # Récupérer les index clés
    try:
        if "X_mm" in profile:
            X = np.array(profile["X_mm"])
            # Index approximatifs
            idx_chambre = 0
            idx_col = np.argmin(np.abs(X)) # Proche de 0
            idx_sortie = len(X) - 1
            
            # Helper pour set le text
            def set_lbl(key, val, unit=""):
                if key in app.thermal_labels:
                    app.thermal_labels[key].configure(text=f"{val} {unit}")

            # Chambre
            set_lbl("T_gas_chambre", f"{profile['T_gas'][idx_chambre]:.0f}", "K")
            set_lbl("h_g_chambre", f"{profile['hg'][idx_chambre]:.0f}", "W/m²K")
            set_lbl("Flux_chambre", f"{profile['Flux_MW'][idx_chambre]:.2f}", "MW/m²")
            set_lbl("T_paroi_gaz_chambre", f"{profile['T_wall_hot'][idx_chambre]:.0f}", "K")
            
            # Col
            set_lbl("T_gas_col", f"{profile['T_gas'][idx_col]:.0f}", "K")
            set_lbl("h_g_col", f"{profile['hg_throat']:.0f}", "W/m²K")
            set_lbl("Flux_col", f"{profile['Flux_max_MW']:.2f}", "MW/m²")
            set_lbl("T_paroi_gaz_col", f"{profile['T_wall_hot'][idx_col]:.0f}", "K")
            
            # Sortie
            set_lbl("T_gas_sortie", f"{profile['T_gas'][idx_sortie]:.0f}", "K")
            set_lbl("h_g_sortie", f"{profile['hg'][idx_sortie]:.0f}", "W/m²K")
            set_lbl("Flux_sortie", f"{profile['Flux_MW'][idx_sortie]:.2f}", "MW/m²")
            set_lbl("T_paroi_gaz_sortie", f"{profile['T_wall_hot'][idx_sortie]:.0f}", "K")
            
            # Refroidissement
            set_lbl("T_coolant_out", f"{res.get('coolant_tout', 0):.1f}", "K")
            set_lbl("Delta_T_coolant", f"{res.get('coolant_tout', 0) - res.get('coolant_tin', 0):.1f}", "K")
            set_lbl("Q_total", f"{res.get('Q_total_kW', 0):.1f}", "kW")
            set_lbl("Vitesse_coolant", f"{res.get('coolant_vel', 0):.1f}", "m/s")
            set_lbl("Re_coolant", f"{res.get('coolant_Re', 0):.0e}", "")
            set_lbl("h_coolant", f"{res.get('hc', 0):.0f}", "W/m²K")
            set_lbl("DP_coolant", f"{res.get('coolant_pressure_drop', 0):.2f}", "bar")
            
            # Sécurité
            t_boil = res.get("T_boil", 373)
            t_out = res.get("coolant_tout", 300)
            margin = (t_boil - t_out)
            color = app.accent_alt2 if margin > 20 else (app.accent_alt3 if margin > 0 else "#ff5555")
            
            lbl_margin = app.thermal_labels["Marge_Ebullition"]
            lbl_margin.configure(text=f"{margin:.1f} K", text_color=color)
            
            set_lbl("T_paroi_max", f"{max(profile['T_wall_hot']):.0f}", "K")

    except Exception as e:
        print(f"Erreur update results: {e}")

def update_plot(app):
    """Met à jour le graphique selon la vue sélectionnée."""
    app.fig_thermal.clear()
    ax = app.fig_thermal.add_subplot(111)
    app.apply_dark_axes(ax)
    
    profile = app.results["thermal_profile"]
    X = profile["X_mm"]
    view = app.thermal_view_var.get()
    
    if view == "Températures":
        ax.plot(X, profile["T_gas"], label="T Gaz (Rec)", color=app.accent_alt3, linestyle='--')
        ax.plot(X, profile["T_wall_hot"], label="T Paroi (Chaude)", color="#ff5555", linewidth=2)
        
        # T Paroi Froide (peut être scalaire ou vecteur)
        t_cold = profile["T_wall_cold"]
        if isinstance(t_cold, (int, float)):
             ax.axhline(y=t_cold, label="T Paroi (Froide)", color="#00ff88", linestyle='-')
        else:
            ax.plot(X, t_cold, label="T Paroi (Froide)", color="#00ff88")
            
        ax.set_ylabel("Température (K)")
        ax.set_title("Profils de Température")
        
    elif view == "Flux":
        ax.plot(X, profile["Flux_MW"], label="Flux Thermique", color="#ffbd44", linewidth=2)
        ax.fill_between(X, 0, profile["Flux_MW"], alpha=0.2, color="#ffbd44")
        
        ax.set_ylabel("Flux (MW/m²)")
        ax.set_title("Densité de Flux Thermique")
        
    elif view == "Coef. Échange":
        ax.plot(X, profile["hg"], label="h gaz", color=app.accent)
        
        # h coolant (peut être scalaire)
        hc = app.results.get("hc", 0)
        ax.axhline(y=hc, label=f"h coolant ({hc:.0f})", color=app.accent_alt, linestyle='--')
        
        ax.set_ylabel("Coefficient (W/m²K)")
        ax.set_title("Coefficients d'Échange Convectif")
        
    app.fig_thermal.tight_layout()
    ax.legend()
    ax.grid(True, color=app.grid_color, alpha=0.3)
    app.canvas_thermal.draw()

def export_thermal_csv(app):
    """Exporte les données actuelles en CSV."""
    from tkinter import filedialog
    import csv
    
    if not hasattr(app, 'results') or 'thermal_profile' not in app.results:
        return

    filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                          filetypes=[("CSV Files", "*.csv")])
    if not filename:
        return
        
    profile = app.results["thermal_profile"]
    X = profile["X_mm"]
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["X_mm", "T_gas_K", "T_wall_hot_K", "Flux_MW_m2", "h_g_Wm2K"])
        
        for i in range(len(X)):
            writer.writerow([
                X[i], 
                profile["T_gas"][i], 
                profile["T_wall_hot"][i], 
                profile["Flux_MW"][i],
                profile["hg"][i]
            ])
            
    tk.messagebox.showinfo("Export", f"Données exportées vers {filename}")
