import tkinter.font as tkfont
import customtkinter as ctk
import io
import urllib.request
from PIL import Image


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


def load_icon(icon_code: str, size: int = 80) -> ctk.CTkImage | None:
    """
    Télécharge une icône météo depuis OpenWeatherMap et retourne
    un CTkImage prêt à afficher dans Tkinter.

    Parameters
    ----------
    icon_code : str
        Code icône OpenWeatherMap ex: "01d", "10n".
        Voir https://openweathermap.org/weather-conditions
    size : int
        Taille en pixels du carré de l'image (défaut: 80).
        Passer 28 pour les petites icônes dans les slots,
        110 pour la grande icône de la carte météo principale.

    Returns
    -------
    ctk.CTkImage | None
        Image prête à afficher, ou None si le téléchargement échoue.
    """
    url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            img_data = response.read()
        img = Image.open(io.BytesIO(img_data)).resize((size, size))
        return ctk.CTkImage(img, size=(size, size))
    except Exception:
        return None

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

