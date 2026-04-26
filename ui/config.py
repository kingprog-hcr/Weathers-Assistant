import tkinter.font as tkfont

COLORS = {
    "bg_main":        "#1a1a2e",
    "bg_sidebar":     "#12122a",
    "bg_card":        "#1e1e38",
    "accent":         "#3d5af1",
    "text_primary":   "#e0e0f0",
    "text_secondary": "#8888aa",
    "text_muted":     "#6b6b9a",
    "border":         "#2a2a4a",
}

def get_font(size: int, weight: str = "normal") -> tuple:
    """
    Retourne la meilleure police disponible sur le système.
    Priorité : Bell MT → Helvetica → police système par défaut.
    """
    available = tkfont.families()
    for family in ("Bell MT", "Helvetica Neue", "Helvetica", "Arial"):
        if family in available:
            return (family, size, weight)
    return ("TkDefaultFont", size, weight)
