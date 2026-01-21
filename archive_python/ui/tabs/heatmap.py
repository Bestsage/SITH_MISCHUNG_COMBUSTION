
import tkinter as tk
import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from config import *

def init(app):
    """Initialise l'onglet Carte Thermique 2D avec visualisation colorée."""
    # Barre d'accent
    accent_bar = ctk.CTkFrame(app.tab_heatmap, height=4, fg_color="#ff6b35")
    accent_bar.pack(fill=tk.X)
    
    # Frame de contrôles modernisée (compacte)
    ctrl_frame = ctk.CTkFrame(app.tab_heatmap, fg_color=app.bg_panel, corner_radius=10)
    ctrl_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5, 5))
    
    # Titre (plus compact)
    header = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
    header.pack(fill=tk.X, padx=10, pady=(5, 3))
    
    ctk.CTkLabel(header, text="🔥 Carte Thermique 2D",
                 font=ctk.CTkFont(size=13, weight="bold"), text_color="#ff6b35").pack(side=tk.LEFT)
    
    # Bouton visualisation externe
    ctk.CTkButton(header, text="🖼️ Ouvrir Visualisation", 
                  fg_color=app.accent_alt3, hover_color="#ff8c42", text_color=app.bg_main,
                  font=ctk.CTkFont(size=11, weight="bold"),
                  command=lambda: open_window(app),
                  width=180, height=28).pack(side=tk.RIGHT, padx=5)
    
    ctk.CTkButton(header, text="📖", width=40, height=24,
                  fg_color="transparent", border_width=1, border_color=app.accent,
                  hover_color=app.bg_surface, text_color=app.accent,
                  command=lambda: app.open_wiki_at("23. CARTE THERMIQUE")).pack(side=tk.RIGHT, padx=2)
    
    # Ligne 1: Options de visualisation
    row1 = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
    row1.pack(fill=tk.X, pady=10, padx=10)
    
    ctk.CTkLabel(row1, text="Mode:", text_color=app.text_primary).pack(side=tk.LEFT, padx=(0, 10))
    app.heatmap_mode = tk.StringVar(value="coupe_radiale")
    modes = [("Coupe Radiale", "coupe_radiale"), ("Développée", "developpee"), ("3D Surface", "surface_3d")]
    for text, mode in modes:
        ctk.CTkRadioButton(row1, text=text, variable=app.heatmap_mode, value=mode,
                           fg_color=app.accent, hover_color=app.accent_alt,
                           command=lambda: update(app)).pack(side=tk.LEFT, padx=8)
    
    # Séparateur vertical
    sep1 = ctk.CTkFrame(row1, width=2, height=16, fg_color=app.border_color) 
    sep1.pack(side=tk.LEFT, padx=15) 
    
    ctk.CTkLabel(row1, text="Colormap:", text_color=app.text_primary).pack(side=tk.LEFT, padx=(0, 5))
    app.heatmap_cmap_var = tk.StringVar(value="inferno")
    app.heatmap_cmap = ctk.CTkComboBox(row1, values=["inferno", "plasma", "hot", "jet", "coolwarm", "magma", "viridis"],
                                         variable=app.heatmap_cmap_var, width=100,
                                         fg_color=app.bg_surface, border_color=app.border_color,
                                         button_color=app.accent, button_hover_color=app.accent_alt,
                                         command=lambda x: update(app))
    app.heatmap_cmap.pack(side=tk.LEFT, padx=5)
    
    ctk.CTkLabel(row1, text="Résolution:", text_color=app.text_primary).pack(side=tk.LEFT, padx=(15, 5))
    app.heatmap_resolution_var = tk.StringVar(value="50")
    app.heatmap_resolution = ctk.CTkEntry(row1, textvariable=app.heatmap_resolution_var, width=50,
                                            fg_color=app.bg_surface, border_color=app.border_color)
    app.heatmap_resolution.pack(side=tk.LEFT)
    
    # Ligne 2: Options supplémentaires
    row2 = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
    row2.pack(fill=tk.X, pady=5, padx=10)
    
    app.heatmap_show_isotherms = tk.BooleanVar(value=True)
    ctk.CTkCheckBox(row2, text="Isothermes", variable=app.heatmap_show_isotherms,
                    fg_color=app.accent, hover_color=app.accent_alt,
                    command=lambda: update(app)).pack(side=tk.LEFT, padx=10)
    
    app.heatmap_show_limits = tk.BooleanVar(value=True)
    ctk.CTkCheckBox(row2, text="Limites matériau", variable=app.heatmap_show_limits,
                    fg_color=app.accent, hover_color=app.accent_alt,
                    command=lambda: update(app)).pack(side=tk.LEFT, padx=10)
    
    app.heatmap_show_flux = tk.BooleanVar(value=False)
    ctk.CTkCheckBox(row2, text="Vecteurs flux", variable=app.heatmap_show_flux,
                    fg_color=app.accent, hover_color=app.accent_alt,
                    command=lambda: update(app)).pack(side=tk.LEFT, padx=10)
    
    app.heatmap_show_channels = tk.BooleanVar(value=True)
    ctk.CTkCheckBox(row2, text="Canaux coolant", variable=app.heatmap_show_channels,
                    fg_color=app.accent, hover_color=app.accent_alt,
                    command=lambda: update(app)).pack(side=tk.LEFT, padx=10)
    
    # Séparateur
    sep2 = ctk.CTkFrame(row2, width=2, height=16, fg_color=app.border_color)
    sep2.pack(side=tk.LEFT, padx=15)
    
    ctk.CTkLabel(row2, text="Position X (mm):", text_color=app.text_primary).pack(side=tk.LEFT, padx=(0, 5))
    app.heatmap_x_pos = ctk.CTkSlider(row2, from_=-100, to=200, width=150,
                                        fg_color=app.bg_surface, progress_color=app.accent,
                                        button_color=app.accent, button_hover_color=app.accent_alt,
                                        command=lambda v: update(app))
    app.heatmap_x_pos.set(0)
    app.heatmap_x_pos.pack(side=tk.LEFT, padx=5)
    app.heatmap_x_label = ctk.CTkLabel(row2, text="0.0 mm", text_color=app.accent)
    app.heatmap_x_label.pack(side=tk.LEFT)
    
    # Bouton refresh
    ctk.CTkButton(row2, text="🔄", width=40, height=24,
                  fg_color=app.accent, hover_color=app.accent_alt, text_color=app.bg_main,
                  command=lambda: update(app)).pack(side=tk.RIGHT, padx=2)
    
    # Ligne 3: Informations thermiques en temps réel (compactée)
    info_frame = ctk.CTkFrame(ctrl_frame, fg_color=app.bg_surface, corner_radius=8)
    info_frame.pack(fill=tk.X, pady=(5, 10), padx=10)
    
    info_row = ctk.CTkFrame(info_frame, fg_color="transparent")
    info_row.pack(fill=tk.X, padx=5, pady=3)
    
    app.heatmap_info_labels = {}
    info_items = [("T_gaz", "T gaz:"), ("T_hot", "T hot:"), ("T_cold", "T cold:"), 
                  ("T_cool", "T cool:"), ("flux", "Flux:"), ("hg", "h_g:")]
    for key, text in info_items:
        ctk.CTkLabel(info_row, text=text, text_color=app.text_muted, 
                    font=ctk.CTkFont(size=10)).pack(side=tk.LEFT, padx=(5, 1))
        lbl = ctk.CTkLabel(info_row, text="-", text_color=app.accent,
                          font=ctk.CTkFont(size=10))
        lbl.pack(side=tk.LEFT, padx=(0, 8))
        app.heatmap_info_labels[key] = lbl
    
    # Container pour le graphique
    graph_container = ctk.CTkFrame(app.tab_heatmap, fg_color=app.bg_panel, corner_radius=10)
    graph_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    app.fig_heatmap = plt.Figure(figsize=(8, 6), dpi=100)
    app.fig_heatmap.patch.set_facecolor(app.bg_panel)
    
    app.canvas_heatmap = FigureCanvasTkAgg(app.fig_heatmap, master=graph_container)
    app.canvas_heatmap.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Initialisation vide
    app.ax_heatmap = app.fig_heatmap.add_subplot(111)
    app.apply_dark_axes(app.ax_heatmap)
    
    # Données stockées pour interaction
    app.heatmap_data = None
    app.heatmap_window = None  # Référence à la fenêtre de visualisation

    # Bind events
    app.canvas_heatmap.mpl_connect('motion_notify_event', lambda event: on_hover(app, event))
    app.canvas_heatmap.mpl_connect('button_press_event', lambda event: on_click(app, event))


def update(app):
    """Met à jour la carte thermique."""
    if not hasattr(app, 'results') or 'thermal_profile' not in app.results:
        return

    mode = app.heatmap_mode.get()
    
    if mode == "coupe_radiale":
        _draw_radial_cut(app)
    elif mode == "developpee":
        _draw_developed(app)
    elif mode == "surface_3d":
        _draw_3d_surface(app)
        
    # Mise à jour de la fenêtre détachée
    update_window(app)


def open_window(app):
    """Ouvre la visualisation dans une nouvelle fenêtre."""
    from tkinter import messagebox
    
    if not app.results or "thermal_profile" not in app.results:
        messagebox.showwarning("Attention", "Calculez d'abord le moteur (bouton CALCULER)!")
        return
    
    # Fermer la fenêtre précédente si elle existe
    if hasattr(app, 'heatmap_window') and app.heatmap_window is not None:
        try:
            app.heatmap_window.destroy()
        except:
            pass
    
    # Créer une nouvelle fenêtre Toplevel
    app.heatmap_window = tk.Toplevel(app.root)
    app.heatmap_window.title("Carte Thermique 2D - Visualisation")
    app.heatmap_window.geometry("1400x900")
    app.heatmap_window.configure(bg=app.bg_main)
    
    # Maximiser
    try:
        app.heatmap_window.state('zoomed')
    except:
        pass
    
    # Titre
    title_frame = ctk.CTkFrame(app.heatmap_window, fg_color=app.bg_panel, corner_radius=10)
    title_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))
    
    ctk.CTkLabel(title_frame, text="🔥 Carte Thermique 2D - Visualisation",
                 font=ctk.CTkFont(size=14, weight="bold"), text_color="#ff6b35").pack(padx=10, pady=8)
    
    ctk.CTkLabel(title_frame, text="Les paramètres sont contrôlés depuis l'onglet principal",
                 font=ctk.CTkFont(size=10), text_color=app.text_muted).pack(padx=10, pady=(0, 8))
    
    # Container graphique
    graph_container_win = ctk.CTkFrame(app.heatmap_window, fg_color=app.bg_panel, corner_radius=10)
    graph_container_win.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
    
    # Figure matplotlib
    fig_win = plt.Figure(figsize=(16, 10), dpi=100)
    fig_win.patch.set_facecolor(app.bg_main)
    fig_win.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.08)
    
    # Axe initial
    ax_win = fig_win.add_subplot(111)
    ax_win.set_facecolor(app.bg_surface)
    ax_win.text(0.5, 0.5, "Chargement...", 
                       ha='center', va='center', fontsize=14, color=app.text_muted,
                       transform=ax_win.transAxes)
    app.apply_dark_axes([ax_win])
    
    canvas_win = FigureCanvasTkAgg(fig_win, master=graph_container_win)
    canvas_win.get_tk_widget().configure(bg=app.bg_main, highlightthickness=0)
    canvas_win.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Stockage des références
    app.heatmap_window._fig = fig_win
    app.heatmap_window._ax = ax_win
    app.heatmap_window._canvas = canvas_win
    
    # Premier update
    update_window(app)
    
    # Gestion fermeture
    def on_close():
        try:
            if app.heatmap_window is not None:
                app.heatmap_window.destroy()
        except:
            pass
        finally:
            app.heatmap_window = None
    
    app.heatmap_window.protocol("WM_DELETE_WINDOW", on_close)


def update_window(app):
    """Met à jour le graphique dans la fenêtre de visualisation."""
    if not hasattr(app, 'heatmap_window') or app.heatmap_window is None:
        return
    
    fig = app.heatmap_window._fig
    canvas = app.heatmap_window._canvas
    
    if not app.results or "thermal_profile" not in app.results:
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor(app.bg_surface)
        ax.text(0.5, 0.5, "Calculez d'abord le moteur\n(bouton CALCULER)", 
                ha='center', va='center', fontsize=14, color=app.text_muted,
                transform=ax.transAxes)
        app.apply_dark_axes([ax])
        app.heatmap_window._ax = ax
        canvas.draw()
        return
    
    # Clear existing
    fig.clear()
    
    mode = app.heatmap_mode.get()
    ax = None
    
    try:
        if mode == "coupe_radiale":
             _draw_radial_cut(app, fig=fig, ax=None, canvas=canvas)
             # Note: _draw_radial_cut handles clearing and adding subplot if we pass fig but no ax
             # Actually my implementation clears fig if fig==app.fig_heatmap, checking strict equality.
             # I need to check the helper _setup_plot_target.
             pass
        elif mode == "developpee":
             _draw_developed(app, fig=fig, ax=None, canvas=canvas)
        elif mode == "surface_3d":
             _draw_3d_surface(app, fig=fig, ax=None, canvas=canvas)
             
        # Reference ax is updated inside the draw functions if we passed fig?
        # My draw functions return nothing.
        # But they do `if fig == app.fig_heatmap: app.ax_heatmap = ax`
        # They don't update app.heatmap_window._ax
        # That's fine, we might not need to store _ax explicitly if we don't use it elsewhere.
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor(app.bg_surface)
        ax.text(0.5, 0.5, f"Erreur:\n{str(e)}", 
                ha='center', va='center', fontsize=12, color='red',
                transform=ax.transAxes)
        app.apply_dark_axes([ax])
        canvas.draw()

def on_hover(app, event):
    """Gère le survol de la carte thermique pour afficher les infos."""
    if event.inaxes != app.ax_heatmap or app.heatmap_data is None:
        return
    
    # En mode coupe radiale, calculer la température à partir de la position
    if app.heatmap_mode.get() == "coupe_radiale":
        x, y = event.xdata, event.ydata
        r = np.sqrt(x**2 + y**2)
        data = app.heatmap_data
        
        if data["r_inner"] <= r <= data["r_outer"]:
            # Interpoler la température
            wall_thickness = data["r_outer"] - data["r_inner"]
            depth = r - data["r_inner"]
            t_local = data["t_hot"] + (data["t_cold"] - data["t_hot"]) * depth / wall_thickness
            
            # Mettre à jour le titre avec l'info
            app.ax_heatmap.set_title(
                f'Coupe @ X={data["x_pos"]:.1f}mm | r={r:.1f}mm | T={t_local:.0f}K | Flux={data["flux"]:.2f}MW/m²',
                color=app.text_primary, fontsize=11
            )
            app.canvas_heatmap.draw_idle()

def on_click(app, event):
    pass

def _setup_plot_target(app, fig, ax, canvas):
    """Helper to determine where to draw."""
    if fig is None:
        fig = app.fig_heatmap
    if ax is None:
        # We always create a new subplot, clearing the fig
        # Using 3d projection or not is handled by the caller or specialized setup?
        # My draw functions call `ax = fig.add_subplot(111)` if ax is None.
        pass
    if canvas is None:
        canvas = app.canvas_heatmap
    return fig, ax, canvas

def update_heatmap_info(app, x_pos, t_gas, t_hot, t_cold, t_coolant, flux):
    """Met à jour les labels d'information."""
    profile = app.results.get("thermal_profile", {})
    if "hg_throat" in profile:
        hg = profile["hg_throat"]
    else:
        hg = 0
    
    # Check if markers exist
    if hasattr(app, "heatmap_info_labels") and "T_gaz" in app.heatmap_info_labels:
        app.heatmap_info_labels["T_gaz"].configure(text=f"{t_gas:.0f} K")
        app.heatmap_info_labels["T_hot"].configure(text=f"{t_hot:.0f} K")
        app.heatmap_info_labels["T_cold"].configure(text=f"{t_cold:.0f} K")
        app.heatmap_info_labels["T_cool"].configure(text=f"{t_coolant:.0f} K")
        app.heatmap_info_labels["flux"].configure(text=f"{flux:.2f} MW/m²")
        app.heatmap_info_labels["hg"].configure(text=f"{hg:.0f} W/m²K")


def _draw_radial_cut(app, fig=None, ax=None, canvas=None):
    """Dessine la carte thermique en coupe radiale a une position X donnee."""
    fig, ax, canvas = _setup_plot_target(app, fig, ax, canvas)
    
    if ax is None: 
         fig.clear()
         ax = fig.add_subplot(111)

    ax.set_facecolor(app.bg_surface)
    
    profile = app.results["thermal_profile"]
    X_mm = np.array(profile["X_mm"])
    Y_mm = np.array(profile["Y_mm"])
    T_gas = np.array(profile["T_gas"])
    T_wall_hot = np.array(profile["T_wall_hot"])
    T_wall_cold = profile["T_wall_cold"]
    Flux_MW = np.array(profile["Flux_MW"])
    
    # Position X selectionnee
    x_pos = float(app.heatmap_x_pos.get())
    app.heatmap_x_label.configure(text=f"{x_pos:.1f} mm")
    
    # Trouver l'index le plus proche
    idx = np.argmin(np.abs(X_mm - x_pos))
    
    # Donnees a cette position
    r_inner = Y_mm[idx]  # Rayon interieur (cote gaz)
    wall_thickness = app.results.get("wall_thickness_mm", 3.0)
    r_outer = r_inner + wall_thickness  # Rayon extérieur (côté coolant)
    
    t_gas_local = T_gas[idx]
    t_hot_local = T_wall_hot[idx]
    t_cold_local = T_wall_cold if isinstance(T_wall_cold, (int, float)) else T_wall_cold
    flux_local = Flux_MW[idx]
    
    # Temperature coolant
    t_coolant = app.get_val("coolant_tin") if app.get_val("coolant_tin") else 300
    
    # Grille
    n_theta = int(app.heatmap_resolution_var.get())
    n_r = 30
    theta = np.linspace(0, 2*np.pi, n_theta)
    r = np.linspace(r_inner, r_outer, n_r)
    THETA, R = np.meshgrid(theta, r)
    X = R * np.cos(THETA)
    Y = R * np.sin(THETA)
    T = t_hot_local + (t_cold_local - t_hot_local) * (R - r_inner) / wall_thickness
    
    # Tracer
    cmap = app.heatmap_cmap_var.get()
    levels = np.linspace(t_cold_local - 50, t_hot_local + 50, 50)
    contour = ax.contourf(X, Y, T, levels=levels, cmap=cmap, extend='both')
    
    # Cbar
    cbar = fig.colorbar(contour, ax=ax, label='Température (K)', pad=0.02)
    cbar.ax.yaxis.label.set_color(app.text_primary)
    cbar.ax.tick_params(colors=app.text_primary)
    
    # Isothermes
    if app.heatmap_show_isotherms.get():
        iso_levels = np.linspace(t_cold_local, t_hot_local, 8)
        iso = ax.contour(X, Y, T, levels=iso_levels, colors='white', linewidths=0.5, alpha=0.7)
        ax.clabel(iso, inline=True, fontsize=8, fmt='%.0f K', colors='white')
    
    # Limites
    if app.heatmap_show_limits.get():
        wall_k = app.get_val("wall_k") if app.get_val("wall_k") else 320
        t_limit = app.get_val("twall") if app.get_val("twall") else 1000
        if t_hot_local > t_limit:
            r_limit = r_inner + (t_limit - t_hot_local) / (t_cold_local - t_hot_local) * wall_thickness
            if r_inner < r_limit < r_outer:
                circle_limit = plt.Circle((0, 0), r_limit, fill=False, color='red', 
                                          linewidth=2, label=f'T_limite ({t_limit:.0f} K)')
                ax.add_patch(circle_limit)
    
    # Channels
    if app.heatmap_show_channels.get():
        n_channels = 40
        for i in range(n_channels):
            angle = 2 * np.pi * i / n_channels
            x_ch = r_outer * np.cos(angle)
            y_ch = r_outer * np.sin(angle)
            ax.plot(x_ch, y_ch, 's', color=app.accent, markersize=4, alpha=0.8)
    
    # Cercles ref
    ax.add_patch(plt.Circle((0, 0), r_inner, fill=False, color=app.accent, linewidth=1.5))
    ax.add_patch(plt.Circle((0, 0), r_outer, fill=False, color='#00ff88', linewidth=1.5))
    
    # Gaz
    ax.add_patch(plt.Circle((0, 0), r_inner * 0.98, color='#ff4444', alpha=0.15))
    ax.text(0, 0, f'GAZ\\n{t_gas_local:.0f} K', ha='center', va='center', 
                        fontsize=10, color='#ff6666', fontweight='bold')
    
    # Annotations
    ax.annotate(f'T_hot = {t_hot_local:.0f} K', xy=(r_inner, 0), xytext=(r_inner + wall_thickness/4, wall_thickness),
                            fontsize=9, color='yellow', ha='center', arrowprops=dict(color='yellow', lw=0.5))
    ax.annotate(f'T_cold = {t_cold_local:.0f} K', xy=(r_outer, 0), xytext=(r_outer + 5, -wall_thickness),
                            fontsize=9, color='#00ff88', ha='center', arrowprops=dict(color='#00ff88', lw=0.5))
    
    # Axes
    max_r = r_outer * 1.3
    ax.set_xlim(-max_r, max_r)
    ax.set_ylim(-max_r, max_r)
    ax.set_aspect('equal')
    ax.set_xlabel('Position (mm)', color=app.text_primary)
    ax.set_ylabel('Position (mm)', color=app.text_primary)
    
    region = "Chambre" if x_pos < -app.results.get('lc', 0) else ("Col" if abs(x_pos) < 5 else "Divergent")
    ax.set_title(f'Coupe Radiale @ X = {x_pos:.1f} mm ({region}) | Flux = {flux_local:.2f} MW/m²',
                              color=app.text_primary, fontsize=12, fontweight='bold')
    
    app.apply_dark_axes([ax])
    fig.tight_layout()
    
    # Stockage (uniquement si affichage principal)
    if fig == app.fig_heatmap:
        app.ax_heatmap = ax # Update ref
        app.heatmap_data = {
            "x_pos": x_pos, "r_inner": r_inner, "r_outer": r_outer,
            "t_gas": t_gas_local, "t_hot": t_hot_local, "t_cold": t_cold_local,
            "flux": flux_local, "t_coolant": t_coolant
        }
        update_heatmap_info(app, x_pos, t_gas_local, t_hot_local, t_cold_local, t_coolant, flux_local)
        canvas.draw_idle()
    else:
        # Pour les fenêtres détachées, on dessine juste
        canvas.draw_idle()


def _draw_developed(app, fig=None, ax=None, canvas=None):
    """Dessine la carte thermique développée."""
    fig, ax, canvas = _setup_plot_target(app, fig, ax, canvas)
    
    if ax is None: 
         fig.clear()
         ax = fig.add_subplot(111)

    ax.set_facecolor(app.bg_surface)
    
    profile = app.results["thermal_profile"]
    X_mm = np.array(profile["X_mm"])
    T_wall_hot = np.array(profile["T_wall_hot"])
    T_wall_cold = profile["T_wall_cold"]
    Flux_MW = np.array(profile["Flux_MW"])
    
    wall_thickness = app.results.get("wall_thickness_mm", 3.0)
    n_depth = 30
    
    depth = np.linspace(0, wall_thickness, n_depth)
    X_grid, D_grid = np.meshgrid(X_mm, depth)
    
    # Calcul T
    T_grid = np.zeros_like(X_grid)
    for i, x in enumerate(X_mm):
        t_hot = T_wall_hot[i]
        t_cold = T_wall_cold if isinstance(T_wall_cold, (int, float)) else T_wall_cold
        for j, d in enumerate(depth):
            T_grid[j, i] = t_hot + (t_cold - t_hot) * d / wall_thickness
    
    cmap = app.heatmap_cmap_var.get()
    t_min = min(T_wall_cold if isinstance(T_wall_cold, (int, float)) else min(T_wall_cold), min(T_wall_hot)) - 50
    t_max = max(T_wall_hot) + 100
    levels = np.linspace(t_min, t_max, 50)
    
    contour = ax.contourf(X_grid, D_grid, T_grid, levels=levels, cmap=cmap, extend='both')
    
    cbar = fig.colorbar(contour, ax=ax, label='Température (K)', pad=0.02)
    cbar.ax.yaxis.label.set_color(app.text_primary)
    cbar.ax.tick_params(colors=app.text_primary)
    
    if app.heatmap_show_isotherms.get():
        iso_levels = np.linspace(t_min + 100, t_max - 100, 10)
        iso = ax.contour(X_grid, D_grid, T_grid, levels=iso_levels, colors='white', linewidths=0.5, alpha=0.7)
        ax.clabel(iso, inline=True, fontsize=7, fmt='%.0f K', colors='white')
    
    if app.heatmap_show_limits.get():
        t_limit = app.get_val("twall") if app.get_val("twall") else 1000
        limit_contour = ax.contour(X_grid, D_grid, T_grid, levels=[t_limit], colors=['red'], linewidths=2, linestyles='--')
        if hasattr(limit_contour, 'allsegs') and any(len(seg) > 0 for seg in limit_contour.allsegs):
            ax.clabel(limit_contour, inline=True, fontsize=9, fmt=f'T_limite = {t_limit:.0f} K', colors='red')
    
    ax.axhline(y=0, color=app.accent, linewidth=1.5, label='Côté gaz')
    ax.axhline(y=wall_thickness, color='#00ff88', linewidth=1.5, label='Côté coolant')
    ax.axvline(x=0, color='white', linewidth=1, alpha=0.5)
    ax.text(0, wall_thickness * 1.05, 'Col', ha='center', color='white', fontsize=9)
    
    # Twin axis for flux
    ax_flux = ax.twinx()
    ax_flux.fill_between(X_mm, 0, Flux_MW, alpha=0.2, color='red')
    ax_flux.plot(X_mm, Flux_MW, 'r-', linewidth=1, alpha=0.6)
    ax_flux.set_ylabel('Flux (MW/m²)', color='red')
    ax_flux.tick_params(axis='y', colors='red')
    ax_flux.set_ylim(0, max(Flux_MW) * 3)
    
    ax.set_xlabel('Position axiale X (mm)', color=app.text_primary)
    ax.set_ylabel('Profondeur dans la paroi (mm)', color=app.text_primary)
    ax.set_title('Carte Thermique Développée - Température dans la paroi', 
                 color=app.text_primary, fontsize=12, fontweight='bold')
    
    ax.legend(loc='upper right', fontsize=8)
    app.apply_dark_axes([ax])
    fig.tight_layout()
    canvas.draw_idle()
    
    if fig == app.fig_heatmap:
        app.ax_heatmap = ax

def _draw_3d_surface(app, fig=None, ax=None, canvas=None):
    """Dessine une surface 3D."""
    from mpl_toolkits.mplot3d import Axes3D
    
    # Helper tweaked for 3D
    fig, ax, canvas = _setup_plot_target(app, fig, ax, canvas)
    
    if ax is None:
         fig.clear()
         ax = fig.add_subplot(111, projection='3d')

    profile = app.results["thermal_profile"]
    X_mm = np.array(profile["X_mm"])
    Y_mm = np.array(profile["Y_mm"])
    T_wall_hot = np.array(profile["T_wall_hot"])
    
    n_theta = int(app.heatmap_resolution_var.get())
    theta = np.linspace(0, 2*np.pi, n_theta)
    
    THETA, X = np.meshgrid(theta, X_mm)
    R = np.tile(Y_mm.reshape(-1, 1), (1, n_theta))
    T = np.tile(T_wall_hot.reshape(-1, 1), (1, n_theta))
    Y_3d = R * np.cos(THETA)
    Z_3d = R * np.sin(THETA)
    
    cmap = app.heatmap_cmap_var.get()
    norm = plt.Normalize(vmin=min(T_wall_hot), vmax=max(T_wall_hot))
    colormap = plt.colormaps.get_cmap(cmap) if hasattr(plt, 'colormaps') else plt.cm.get_cmap(cmap)
    
    surf = ax.plot_surface(X, Y_3d, Z_3d, facecolors=colormap(norm(T)), shade=True, alpha=0.9, antialiased=True)
    
    mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    mappable.set_array(T)
    cbar = fig.colorbar(mappable, ax=ax, label='T paroi hot (K)', shrink=0.6, pad=0.1)
    cbar.ax.yaxis.label.set_color(app.text_primary)
    cbar.ax.tick_params(colors=app.text_primary)
    
    ax.set_xlabel('X (mm)', color=app.text_primary, labelpad=12)
    ax.set_ylabel('Y (mm)', color=app.text_primary, labelpad=12)
    ax.set_zlabel('Z (mm)', color=app.text_primary, labelpad=12)
    ax.set_title('Surface 3D - Température paroi côté gaz', color=app.text_primary, fontsize=13, fontweight='bold', pad=20)
    
    ax.set_facecolor(app.bg_surface)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(True, color=app.grid_color, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.view_init(elev=20, azim=45)
    
    fig.tight_layout()
    canvas.draw_idle()
    
    if fig == app.fig_heatmap:
         app.ax_heatmap = ax
