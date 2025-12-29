
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from config import *

# Optional Dependencies
try:
    import stl as stl_mesh
    HAS_NUMPY_STL = True
except ImportError:
    HAS_NUMPY_STL = False

try:
    import cadquery as cq
    HAS_CADQUERY = True
except ImportError:
    HAS_CADQUERY = False

try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False


def init(app):
    """Initialise l'onglet Visualisation & Export CAD."""
    # Barre d'accent
    tk.Frame(app.tab_cad, height=4, bg="#9b59b6").pack(fill=tk.X)
    
    # Frame principale divisée en deux
    main_frame = ctk.CTkFrame(app.tab_cad)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # === Panneau de contrôles à gauche ===
    ctrl_panel = ctk.CTkFrame(main_frame)
    ctrl_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
    
    # Bouton d'aide en haut du panneau
    ctk.CTkButton(ctrl_panel, text="📖 Aide CAD", width=120,
               command=lambda: app.open_wiki_at("12. EXPORT CAD")).pack(fill=tk.X, pady=(0, 5))
    
    # Section: Géométrie de base
    geo_frame = ctk.CTkFrame(ctrl_panel)
    geo_frame.pack(fill=tk.X, pady=5)
    
    ctk.CTkLabel(geo_frame, text="Résolution angulaire:").grid(row=0, column=0, sticky="w", pady=2)
    app.cad_n_theta = ctk.CTkEntry(geo_frame, width=80)
    app.cad_n_theta.insert(0, "72")
    app.cad_n_theta.grid(row=0, column=1, padx=5, pady=2)
    ctk.CTkLabel(geo_frame, text="segments").grid(row=0, column=2, sticky="w")
    
    ctk.CTkLabel(geo_frame, text="Résolution axiale:").grid(row=1, column=0, sticky="w", pady=2)
    app.cad_n_axial = ctk.CTkEntry(geo_frame, width=80)
    app.cad_n_axial.insert(0, "100")
    app.cad_n_axial.grid(row=1, column=1, padx=5, pady=2)
    ctk.CTkLabel(geo_frame, text="points").grid(row=1, column=2, sticky="w")
    
    # Section: Paroi et canaux
    wall_frame = ctk.CTkFrame(ctrl_panel)
    wall_frame.pack(fill=tk.X, pady=5)
    
    app.cad_include_wall = tk.BooleanVar(value=True)
    ctk.CTkCheckBox(wall_frame, text="Inclure épaisseur paroi", variable=app.cad_include_wall,
                   command=lambda: update_cad_preview(app)).grid(row=0, column=0, columnspan=2, sticky="w")
    
    app.cad_include_channels = tk.BooleanVar(value=True)
    ctk.CTkCheckBox(wall_frame, text="Inclure canaux de refroidissement", variable=app.cad_include_channels,
                   command=lambda: update_cad_preview(app)).grid(row=1, column=0, columnspan=2, sticky="w")
    
    ctk.CTkLabel(wall_frame, text="Nombre de canaux:").grid(row=2, column=0, sticky="w", pady=2)
    app.cad_n_channels = ctk.CTkEntry(wall_frame, width=80)
    app.cad_n_channels.insert(0, "48")
    app.cad_n_channels.grid(row=2, column=1, padx=5, pady=2)
    
    ctk.CTkLabel(wall_frame, text="Largeur canal (mm):").grid(row=3, column=0, sticky="w", pady=2)
    app.cad_channel_width = ctk.CTkEntry(wall_frame, width=80)
    app.cad_channel_width.insert(0, "2.0")
    app.cad_channel_width.grid(row=3, column=1, padx=5, pady=2)
    
    ctk.CTkLabel(wall_frame, text="Profondeur canal (mm):").grid(row=4, column=0, sticky="w", pady=2)
    app.cad_channel_depth = ctk.CTkEntry(wall_frame, width=80)
    app.cad_channel_depth.insert(0, "3.0")
    app.cad_channel_depth.grid(row=4, column=1, padx=5, pady=2)
    
    ctk.CTkLabel(wall_frame, text="Type de canaux:").grid(row=5, column=0, sticky="w", pady=2)
    app.cad_channel_type = ctk.CTkComboBox(wall_frame, values=["Axiaux", "Hélicoïdaux", "Bifurcation"], 
                                          state="readonly", width=115)
    app.cad_channel_type.set("Axiaux")
    app.cad_channel_type.grid(row=5, column=1, padx=5, pady=2)
    
    # Section: Options export
    export_frame = ctk.CTkFrame(ctrl_panel)
    export_frame.pack(fill=tk.X, pady=5)
    
    ctk.CTkLabel(export_frame, text="Format export:").grid(row=0, column=0, sticky="w", pady=2)
    app.cad_format = ctk.CTkComboBox(export_frame, values=["STEP (CAD)", "STL (Mesh)", "DXF (Profil)"], 
                                    width=115)
    app.cad_format.set("STEP (CAD)")
    app.cad_format.grid(row=0, column=1, padx=5, pady=2)
    
    ctk.CTkLabel(export_frame, text="Unités:").grid(row=1, column=0, sticky="w", pady=2)
    app.cad_units = ctk.CTkComboBox(export_frame, values=["mm", "m", "inch"], width=70)
    app.cad_units.set("mm")
    app.cad_units.grid(row=1, column=1, padx=5, pady=2)
    
    app.cad_export_separate = tk.BooleanVar(value=False)
    ctk.CTkCheckBox(export_frame, text="Exporter séparément",
                   variable=app.cad_export_separate).grid(row=2, column=0, columnspan=2, sticky="w")
    
    # Boutons d'action
    btn_frame = ctk.CTkFrame(ctrl_panel)
    btn_frame.pack(fill=tk.X, pady=10)
    
    ctk.CTkButton(btn_frame, text="🔄 Prévisualiser 3D", command=lambda: update_cad_preview(app)).pack(fill=tk.X, pady=2)
    ctk.CTkButton(btn_frame, text="📐 Exporter STEP", command=lambda: export_step(app)).pack(fill=tk.X, pady=2)
    ctk.CTkButton(btn_frame, text="💾 Exporter STL", command=lambda: export_stl(app)).pack(fill=tk.X, pady=2)
    ctk.CTkButton(btn_frame, text="📏 Exporter DXF", command=lambda: export_dxf(app)).pack(fill=tk.X, pady=2)
    
    # Informations
    info_frame = ctk.CTkFrame(ctrl_panel)
    info_frame.pack(fill=tk.X, pady=5)
    
    app.cad_info_labels = {}
    info_items = [("vertices", "Vertices:"), ("faces", "Faces:"), ("volume", "Volume:"), 
                  ("surface", "Surface:"), ("mass", "Masse estimée:")]
    for i, (key, text) in enumerate(info_items):
        ctk.CTkLabel(info_frame, text=text).grid(row=i, column=0, sticky="w", pady=1)
        lbl = ctk.CTkLabel(info_frame, text_color=app.accent)
        lbl.grid(row=i, column=1, sticky="e", padx=10)
        app.cad_info_labels[key] = lbl
    
    # === Panneau de visualisation à droite (Notebook) ===
    vis_notebook = ctk.CTkTabview(main_frame)
    vis_notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # Onglet 1: Profil 2D
    tab_2d = vis_notebook.add("Profil 2D")
    
    # Utiliser plt.Figure pour éviter les conflits avec le backend global
    app.fig_visu = plt.Figure(figsize=(8, 6), dpi=100)
    app.fig_visu.patch.set_facecolor(app.bg_main)
    app.ax_visu = app.fig_visu.add_subplot(111)
    app.apply_dark_axes(app.ax_visu)
    
    app.canvas_visu = FigureCanvasTkAgg(app.fig_visu, master=tab_2d)
    app.canvas_visu.get_tk_widget().configure(bg=app.bg_main, highlightthickness=0)
    app.canvas_visu.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Onglet 2: Modèle 3D
    tab_3d = vis_notebook.add("Modèle 3D")
    
    app.fig_cad = plt.Figure(figsize=(8, 6), dpi=100)
    app.fig_cad.patch.set_facecolor(app.bg_main)
    app.ax_cad = app.fig_cad.add_subplot(111, projection='3d')
    app.ax_cad.set_facecolor(app.bg_surface)
    
    app.canvas_cad = FigureCanvasTkAgg(app.fig_cad, master=tab_3d)
    app.canvas_cad.get_tk_widget().configure(bg=app.bg_main, highlightthickness=0)
    app.canvas_cad.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Message initial 3D
    app.ax_cad.text2D(0.5, 0.5, "Calculez d'abord le moteur\npuis cliquez sur Prévisualiser 3D", 
                      transform=app.ax_cad.transAxes, ha='center', va='center', 
                      fontsize=12, color=app.text_muted)


def update_cad_preview(app):
    """Met à jour la prévisualisation 3D du modèle CAD (Optimisé)."""
    if not hasattr(app, 'ax_cad'):
        return
        
    # Sauvegarder l'angle de vue actuel
    elev = getattr(app.ax_cad, 'elev', None)
    azim = getattr(app.ax_cad, 'azim', None)
        
    app.fig_cad.clear()
    app.ax_cad = app.fig_cad.add_subplot(111, projection='3d')
    
    # Restaurer l'angle de vue
    if elev is not None and azim is not None:
        app.ax_cad.view_init(elev=elev, azim=azim)
    else:
        app.ax_cad.view_init(elev=20, azim=45)
    
    if not app.results or not app.geometry_profile:
        app.ax_cad.text2D(0.5, 0.5, "Calculez d'abord le moteur\n(bouton CALCULER)", 
                          transform=app.ax_cad.transAxes, ha='center', va='center', 
                          fontsize=12, color=app.text_muted)
        app.canvas_cad.draw()
        return
    
    X_profile, Y_profile = app.geometry_profile
    X_mm = np.array(X_profile)
    R_inner = np.array(Y_profile)  # Rayon intérieur
    
    wall_thickness = app.results.get("wall_thickness_mm", 3.0)
    R_outer = R_inner + wall_thickness  # Rayon extérieur
    
    # OPTIMISATION: Limiter la résolution pour l'affichage uniquement
    # Même si l'utilisateur demande 200 segments pour l'export, on n'en affiche que 40 max
    target_n_theta = int(app.cad_n_theta.get())
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
    if app.cad_include_wall.get():
        R_out_grid = np.tile(R_out_disp.reshape(-1, 1), (1, display_n_theta))
        Y_out = R_out_grid * np.cos(THETA)
        Z_out = R_out_grid * np.sin(THETA)
    
    # Tracer surface intérieure (Wireframe partiel pour légèreté ou Surface)
    # Surface est plus jolie mais plus lourde. Avec l'optimisation ci-dessus, surface passe bien.
    surf_in = app.ax_cad.plot_surface(X, Y_in, Z_in, alpha=0.8, color=app.accent, 
                                        edgecolor='none', shade=True, antialiased=True)
    
    # Tracer surface extérieure
    if app.cad_include_wall.get():
        surf_out = app.ax_cad.plot_surface(X, Y_out, Z_out, alpha=0.3, color='#00ff88', 
                                             edgecolor='none', shade=True, antialiased=True)
    
    # Tracer les canaux de refroidissement (simplifié)
    if app.cad_include_channels.get() and app.cad_include_wall.get():
        n_channels = int(app.cad_n_channels.get())
        # Limiter le nombre de canaux affichés pour la perf
        display_n_channels = min(n_channels, 24) 
        
        channel_depth_mm = float(app.cad_channel_depth.get())
        
        # Position angulaire des canaux
        channel_angles = np.linspace(0, 2*np.pi, display_n_channels, endpoint=False)
        
        for angle in channel_angles:
            # Fond du canal
            r_channel = R_in_disp + wall_thickness - channel_depth_mm
            x_ch = X_disp
            y_ch = r_channel * np.cos(angle)
            z_ch = r_channel * np.sin(angle)
            app.ax_cad.plot(x_ch, y_ch, z_ch, color='#0088ff', linewidth=0.8, alpha=0.6)
    
    # Configuration 3D STYLE "CLEAN" (comme Heatmap)
    app.ax_cad.set_xlabel('X (mm)', color=app.text_primary, labelpad=5)
    app.ax_cad.set_ylabel('Y (mm)', color=app.text_primary, labelpad=5)
    app.ax_cad.set_zlabel('Z (mm)', color=app.text_primary, labelpad=5)
    app.ax_cad.set_title(f"Modèle 3D - {app.get_val('name')}", color=app.text_primary, fontweight='bold')
    
    # Style sombre optimisé
    app.ax_cad.set_facecolor(app.bg_surface)
    
    # Supprimer les fonds de grille gris (panes)
    app.ax_cad.xaxis.pane.fill = False
    app.ax_cad.yaxis.pane.fill = False
    app.ax_cad.zaxis.pane.fill = False
    
    # Bordures de grille discrètes
    app.ax_cad.xaxis.pane.set_edgecolor(app.grid_color)
    app.ax_cad.yaxis.pane.set_edgecolor(app.grid_color)
    app.ax_cad.zaxis.pane.set_edgecolor(app.grid_color)
    app.ax_cad.xaxis.pane.set_alpha(0.1)
    app.ax_cad.yaxis.pane.set_alpha(0.1)
    app.ax_cad.zaxis.pane.set_alpha(0.1)
    
    app.ax_cad.tick_params(colors=app.text_primary, labelsize=8)
    app.ax_cad.grid(True, color=app.grid_color, alpha=0.3, linestyle='--')
    
    # Égaliser les axes
    max_range = max(max(X_mm) - min(X_mm), 2 * max(R_outer)) / 2
    mid_x = (max(X_mm) + min(X_mm)) / 2
    app.ax_cad.set_xlim(mid_x - max_range, mid_x + max_range)
    app.ax_cad.set_ylim(-max_range, max_range)
    app.ax_cad.set_zlim(-max_range, max_range)
    
    app.fig_cad.tight_layout()
    app.canvas_cad.draw()
    
    # Mettre à jour les infos
    update_cad_info(app)


def update_cad_info(app):
    """Met à jour les informations du modèle CAD."""
    if not app.results or not app.geometry_profile:
        return
    
    X_profile, Y_profile = app.geometry_profile
    R_inner = np.array(Y_profile)
    wall_thickness = app.results.get("wall_thickness_mm", 3.0)
    R_outer = R_inner + wall_thickness
    
    n_theta = int(app.cad_n_theta.get())
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
    surface = app.results.get("A_cooled", 0) * 1e6  # mm²
    
    # Masse (estimation avec cuivre: 8.96 g/cm³)
    density = 8.96  # g/cm³ pour cuivre
    mass = volume_cm3 * density  # g
    
    app.cad_info_labels["vertices"].configure(text=f"{n_vertices:,}")
    app.cad_info_labels["faces"].configure(text=f"{n_faces:,}")
    app.cad_info_labels["volume"].configure(text=f"{volume_cm3:.1f} cm³")
    app.cad_info_labels["surface"].configure(text=f"{surface:.0f} mm²")
    app.cad_info_labels["mass"].configure(text=f"{mass:.0f} g ({mass/1000:.2f} kg)")


def export_stl(app):
    """Exporte le modèle 3D au format STL."""
    if not app.results or not app.geometry_profile:
        messagebox.showwarning("Attention", "Calculez d'abord le moteur!")
        return
    
    if not HAS_NUMPY_STL:
        messagebox.showwarning("Attention", 
            "Module numpy-stl non installé.\n\nInstallez-le avec:\npip install numpy-stl")
        return
    
    f = filedialog.asksaveasfilename(defaultextension=".stl", 
                                      filetypes=[("STL files", "*.stl")],
                                      initialfile=f"{app.get_val('name')}_nozzle.stl")
    if not f:
        return
    
    try:
        X_profile, Y_profile = app.geometry_profile
        X_mm = np.array(X_profile)
        R_inner = np.array(Y_profile)
        wall_thickness = app.results.get("wall_thickness_mm", 3.0)
        R_outer = R_inner + wall_thickness
        
        n_theta = int(app.cad_n_theta.get())
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

def export_step(app):
    """Exporte le modèle 3D au format STEP (solide paramétrique)."""
    if not app.results or not app.geometry_profile:
        messagebox.showwarning("Attention", "Calculez d'abord le moteur!")
        return
    
    # Vérifier si CadQuery est disponible
    if HAS_CADQUERY:
        _export_step_cadquery(app)
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
            _export_dxf_for_cad(app)

def _export_step_cadquery(app):
    """Export STEP via CadQuery."""
    f = filedialog.asksaveasfilename(defaultextension=".step", 
                                      filetypes=[("STEP files", "*.step"), ("STEP files", "*.stp")],
                                      initialfile=f"{app.get_val('name')}_nozzle.step")
    if not f:
        return
    
    try:
        X_profile, Y_profile = app.geometry_profile
        X_mm = np.array(X_profile)
        R_inner = np.array(Y_profile)
        wall_thickness = app.results.get("wall_thickness_mm", 3.0)
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

def export_dxf(app):
    """Frontend call for DXF export"""
    _export_dxf_for_cad(app)

def _export_dxf_for_cad(app):
    """Exporte un DXF optimisé pour import CAD (profil de révolution)."""
    if not HAS_EZDXF:
        messagebox.showwarning("Attention", "Module ezdxf non installé.\npip install ezdxf")
        return
    
    f = filedialog.asksaveasfilename(defaultextension=".dxf", 
                                      filetypes=[("DXF files", "*.dxf")],
                                      initialfile=f"{app.get_val('name')}_profile_CAD.dxf")
    if not f:
        return
    
    try:
        X_profile, Y_profile = app.geometry_profile
        X_mm = np.array(X_profile)
        R_inner = np.array(Y_profile)
        wall_thickness = app.results.get("wall_thickness_mm", 3.0)
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
