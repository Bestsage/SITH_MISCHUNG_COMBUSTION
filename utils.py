
import platform
import tkinter as tk
from tkinter import font as tkfont
import subprocess
import os

def get_monospace_font():
    """Retourne une police monospace appropriée selon le système."""
    # Test des polices dans l'ordre de préférence
    test_fonts = ["Consolas", "Monaco", "Menlo", "Courier New", "Liberation Mono", "DejaVu Sans Mono", "Courier"]
    
    # Créer une fenêtre temporaire pour tester les polices (non affichée)
    try:
        test_root = tk.Tk()
        test_root.withdraw()
    except:
        # Fallback si pas d'interface graphique (ex: test CI)
        return "Courier"

    for font_name in test_fonts:
        try:
            test_font = tkfont.Font(family=font_name, size=10)
            # Vérifier si la police existe en testant ses métriques
            if test_font.actual()['family'] == font_name:
                test_root.destroy()
                return font_name
        except:
            continue
    
    test_root.destroy()
    # Fallback: utiliser la police monospace par défaut du système
    return "Courier" if platform.system() != "Linux" else "Liberation Mono"

def get_ui_font():
    """Retourne une police UI appropriée selon le système."""
    # Test des polices dans l'ordre de préférence
    test_fonts = ["Segoe UI", "Roboto", "Ubuntu", "Cantarell", "DejaVu Sans", "Liberation Sans", "Arial", "Helvetica", "Sans"]
    
    try:
        test_root = tk.Tk()
        test_root.withdraw()
    except:
        return "Arial"
    
    for font_name in test_fonts:
        try:
            test_font = tkfont.Font(family=font_name, size=10)
            # Vérifier si la police existe
            if test_font.actual()['family'] == font_name:
                test_root.destroy()
                return font_name
        except:
            continue
    
    test_root.destroy()
    # Fallback: utiliser la police sans serif par défaut
    return "Sans"

def get_linux_desktop_scale():
    """Détecte le facteur de scaling du bureau Linux (GNOME/KDE)."""
    if platform.system() != "Linux":
        return 1.0
    
    scale = 1.0
    detection_method = "none"
    
    # Méthode 1: Détection via DPI réel vs logique
    try:
        root_temp = tk.Tk()
        root_temp.withdraw()
        root_temp.update_idletasks()
        real_dpi = root_temp.winfo_fpixels('1i')
        logical_dpi = root_temp.winfo_pixels('1i')
        root_temp.destroy()
        
        if real_dpi > 0 and logical_dpi > 0:
            detected_scale = real_dpi / logical_dpi
            if 0.5 < detected_scale < 5.0:
                common_scales = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
                detected_scale = min(common_scales, key=lambda x: abs(x - detected_scale))
                scale = detected_scale
                detection_method = "DPI"
    except Exception:
        pass
    
    # Méthode 2: Variables d'environnement
    if scale == 1.0:
        try:
            gdk_scale = os.environ.get("GDK_SCALE", "")
            if gdk_scale:
                scale = float(gdk_scale)
                detection_method = "GDK_SCALE"
            
            if scale == 1.0:
                qt_scale = os.environ.get("QT_SCALE_FACTOR", "")
                if qt_scale:
                    scale = float(qt_scale)
                    detection_method = "QT_SCALE_FACTOR"
        except:
            pass
            
    # Méthode 3: GNOME gsettings
    if scale == 1.0:
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "scaling-factor"],
                capture_output=True, text=True, timeout=1, stderr=subprocess.DEVNULL
            )
            if result.returncode == 0 and result.stdout:
                scale_str = result.stdout.strip()
                if scale_str.startswith("uint32"):
                    parts = scale_str.split()
                    if len(parts) >= 2:
                        scale = float(int(parts[1]))
                        detection_method = "gsettings"
        except:
            pass

    # Méthode 4: xrandr
    if scale == 1.0:
        try:
            result = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True, text=True, timeout=1, stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ' connected' in line and 'mm' in line:
                        import re
                        match = re.search(r'\((\d+)mm.*?(\d+)mm\)', line)
                        if match:
                            width_mm = float(match.group(1))
                            height_mm = float(match.group(2))
                            res_match = re.search(r'(\d+)x(\d+)', line)
                            if res_match:
                                width_px = float(res_match.group(1))
                                height_px = float(res_match.group(2))
                                width_dpi = width_px / (width_mm / 25.4)
                                height_dpi = height_px / (height_mm / 25.4)
                                avg_dpi = (width_dpi + height_dpi) / 2
                                detected_scale = avg_dpi / 96.0
                                if 0.5 < detected_scale < 5.0:
                                    common_scales = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
                                    scale = min(common_scales, key=lambda x: abs(x - detected_scale))
                                    detection_method = "xrandr"
                                    break
        except:
            pass
            
    return max(1.0, min(5.0, scale)), detection_method
