
from utils import get_monospace_font, get_ui_font

# --- FONTS ---
MONOSPACE_FONT = get_monospace_font()
UI_FONT = get_ui_font()

# --- COLORS ---
# Theme: OLED + Néon
BG_MAIN = "#000000"
BG_PANEL = "#07080A"
BG_SURFACE = "#080a0c"
ACCENT = "#00d9ff"       # cyan néon
ACCENT_ALT = "#ff5af1"   # magenta néon
ACCENT_ALT2 = "#9dff6a"  # vert néon doux
ACCENT_ALT3 = "#ffb347"  # orange chaud
ACCENT_ALT4 = "#7b9bff"  # lavande
TEXT_PRIMARY = "#e8f1ff"
TEXT_MUTED = "#8b949e"
GRID_COLOR = "#15191d"
BORDER_COLOR = "#25292e"

TAB_ACCENT = {
    "summary": ACCENT,
    "visu": ACCENT_ALT3,
    "thermal": ACCENT_ALT,
    "graphs": ACCENT,
    "heatmap": "#ff5af1", # Added missing mapping if needed or reuse existing
    "cea": ACCENT_ALT2,
    "database": ACCENT_ALT4,
    "solver": "#00ffaa",
    "stress": "#e8f1ff", # Default fallback
    "optimizer": "#ffb347",
    "wiki": "#ffffff"
}

# --- PLOT STYLES ---
def setup_matplotlib_style():
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": BG_MAIN,
        "axes.facecolor": BG_SURFACE,
        "axes.edgecolor": ACCENT,
        "axes.labelcolor": TEXT_PRIMARY,
        "xtick.color": TEXT_PRIMARY,
        "ytick.color": TEXT_PRIMARY,
        "grid.color": GRID_COLOR,
        "text.color": TEXT_PRIMARY,
        "axes.titlecolor": TEXT_PRIMARY,
        "axes.prop_cycle": plt.cycler(color=[ACCENT, ACCENT_ALT, ACCENT_ALT2, ACCENT_ALT3, "#7b9bff"]),
    })
