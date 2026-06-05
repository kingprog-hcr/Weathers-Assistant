# ui/config.py

import tkinter.font as tkfont
import customtkinter as ctk
import io
import urllib.request
from PIL import Image
import json
from core.config import DATA_DIR


COLORS = {
    "bg_main":        "#1a1a2e",
    "bg_sidebar":     "#12122a",
    "bg_card":        "#1e1e38",
    "accent":         "#2749f4",
    "text_primary":   "#e0e0f0",
    "text_secondary": "#8888aa",
    "text_muted":     "#6b6b9a",
    "border":         "#2a2a4a",
}

ALL_STYLES = [
    "random",
    "casual",
    "streetwear",
    "oldmoney",
    "boheme",
    "sportswear",
    "minimaliste",
    "preppy",
    "traditionnel"
]

ALL_CUISINES = [
    "random",
    "française",
    "asiatique",
    "américaine",
    "moyen-orientale",
    "latino",
    "fastfood",
    "gabonaise",
    "sénégalaise",
    "ivoirienne",
    "camerounaise",
    "marocaine",
    "algérienne",
    "italienne",
    "espagnole",
    "portugaise"
]

MOODS = ["repos", "aventure", "random"]

def load_icon(icon_code: str, size: int = 80) -> ctk.CTkImage | None:
    """
    Télécharge une icône météo depuis OpenWeatherMap et retourne
    un CTkImage prêt à afficher dans Tkinter.

    Parameters
    ----------
    icon_code : str
        Code icône OpenWeatherMap ex: "01d", "10n".
    size : int
        Taille en pixels du carré de l'image (défaut: 80).

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


def get_font(size: int, weight: str = "normal") -> ctk.CTkFont:
    """
    Retourne la meilleure police disponible sous forme d'objet CTkFont.
    Priorité : Bell MT -> Helvetica -> Arial -> police système par défaut.
    """
    # 1. Sécuriser la récupération des polices
    try:
        # Ne fonctionnera que si la fenêtre principale a déjà été initialisée
        available = tkfont.families()
    except Exception:
        available = []

    # 2. Chercher la famille disponible
    chosen_family = "TkDefaultFont" # Fallback sécurisé
    
    # Si 'available' est vide (appel trop tôt), on force quand même la vérification en laissant CustomTkinter gérer le fallback natif s'il ne trouve pas la police
    if not available:
        chosen_family = "Bell MT" 
    else:
        for family in ("Bell MT", "Helvetica Neue", "Helvetica", "Arial"):
            if family in available:
                chosen_family = family
                break

    # 3. Retourner un objet propre à CustomTkinter
    return ctk.CTkFont(family=chosen_family, size=size, weight=weight)


_CATEGORIES_FILE = DATA_DIR / "categories.json"


def load_slot_categories() -> dict:
    """
    Charge les catégories de badges depuis data/categories.json.
    Retourne un dict vide si le fichier est absent.
    """
    try:
        with open(_CATEGORIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_slot_categories(categories: dict) -> bool:
    """
    Sauvegarde les catégories dans data/categories.json.
    Appelée par CustomFrame quand l'utilisateur modifie ses catégories.

    Returns
    -------
    bool
        True si sauvegarde réussie, False sinon.
    """
    try:
        with open(_CATEGORIES_FILE, "w", encoding="utf-8") as f:
            json.dump(categories, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erreur sauvegarde categories.json : {e}")
        return False


def build_slot_categories() -> dict:
    """
    Construit le dict SLOT_CATEGORIES depuis categories.json.

    Format retourné : {keyword: (label, bg, fg, border)}
    Chaque catégorie contient une liste de keywords  chaque keyword est mappe vers le même tuple badge.
    """
    raw        = load_slot_categories()
    categories = {}
    for key, data in raw.items():
        badge = (data["label"], data["bg"], data["fg"], data["border"])
        for keyword in data.get("keywords", []):
            categories[keyword.lower()] = badge
    return categories



def get_all_tastes() -> list[str]:
    """
    Retourne la liste des clés de catégories depuis categories.json.
    Inclut automatiquement les catégories personnalisées ajoutées
    par l'utilisateur dans CustomFrame.
    Exclut "repas" qui est une catégorie interne, pas un goût.
    """
    raw = load_slot_categories()
    return [key for key in raw.keys() if key != "repas"]


# Chargé une fois au démarrage utilisé dans program_frame et custom_frame
SLOT_CATEGORIES = build_slot_categories()