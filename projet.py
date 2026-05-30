# projet.py
"""
Point d'entrée principal de WeatherProgramm :  CS50 Final Project.

Ce fichier contient :
    main()              : lance l'application
    is_first_launch()   : détecte le premier lancement
    add_day_to_history(): enregistre une journée dans le profil
    get_greeting()      : salutation selon l'heure et la langue 
"""

import os
import sys
import json
from ui.config import COLORS, get_font
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

BASE_DIR = Path(__file__).parent
PROFILE_FILE = BASE_DIR / "data" / "profile.json"


def is_first_launch() -> bool:
    """
    Vérifie si c'est le premier lancement de l'application.

    Returns
    -------
    bool
        True si data/profile.json n'existe pas encore.
        False si un profil a déjà été sauvegardé.
    """
    return not PROFILE_FILE.exists()


def add_day_to_history(program: dict, weather: dict) -> bool:
    """
    Ajoute une journée au profil utilisateur.

    Charge le profil, ajoute l'entrée et sauvegarde.
    Une entrée contient la date, la ville, le score et les activités.

    Parameters
    ----------
    program : dict
        Représentation du DayProgram ex:
        {"score": 8, "slots": [...], "quote": "..."}
    weather : dict
        Météo du jour ex:
        {"city": "Paris", "condition": "clear", "temp": 22}

    Returns
    -------
    bool
        True si la sauvegarde a réussi, False sinon.
    """

    # 1. charger le profil depuis PROFILE_FILE
    # 2. construire l'entrée :
    #    {"date": datetime.now().strftime("%Y-%m-%d"), "city": ..., "score": ..., "slots": ...}
    # 3. ajouter à profile["history"]
    # 4. sauvegarder dans PROFILE_FILE
    # 5. retourner True si succès, False si exception
    try:
        with open(PROFILE_FILE, "r") as p:
            profile = json.load(p)
    except:
        return False
    day = {
        "date":  datetime.now().strftime("%Y-%m-%d"),
        "city":  weather.get("city", ""),
        "score": program.get("score", 0),
        "slots": program.get("slots", []),
    }
    profile["history"].append(day)

    try:
        with open(PROFILE_FILE, "w") as p:
            json.dump(profile, p, indent=2, ensure_ascii=False)
    except:
        return False
    
    return True


def get_greeting(hour: int) -> str:
    """
    Retourne une salutation selon l'heure de la journée.

    Parameters
    ----------
    hour : int
        Heure entre 0 et 23.

    Returns
    -------
    str
        "Bonjour" entre 0 et 11,
        "Bon après-midi" entre 12 et 17,
        "Bonsoir" entre 18 et 23.
    """

    if hour <= 11:
        return "Bonjour"
    elif hour <= 17:
        return "Bon après-midi"
    else:
        return "Bonsoir"


def show_welcome(detected_city: str) -> bool:
    """
    Affiche la fenêtre de bienvenue au premier lancement.

    S'ouvre avant MainWindow. Bloque jusqu'à fermeture via root.mainloop().
    Retourne True si l'utilisateur veut aller au profil, False sinon.

    Parameters
    ----------
    detected_city : str
        Ville détectée automatiquement par géolocalisation IP.

    Returns
    -------
    bool
        True si l'utilisateur clique "Configurer mon profil".
        False s'il clique "Passer".
    """
    import customtkinter as ctk

    result = {"go_to_profile": False}

    root = ctk.CTk()
    root.title("Bienvenu sur WeatherProgramm")
    root.geometry("600x420")
    root.resizable(False, False)
    root.configure(fg_color=COLORS["bg_main"])

    # Centre la fenêtre sur l'écran
    root.update_idletasks()
    x = (root.winfo_screenwidth()  // 2) - 300
    y = (root.winfo_screenheight() // 2) - 210
    root.geometry(f"600x400+{x}+{y}")

    root.grid_columnconfigure(0, weight=1)
    

    # Logo / icône en haut
    logo_frame = ctk.CTkFrame(
        root,
        fg_color=COLORS["accent"],
        corner_radius=16,
        width=64, height=64
    )
    logo_frame.grid(row=0, column=0, pady=(36, 0))
    logo_frame.grid_propagate(False)

    ctk.CTkLabel(
        logo_frame,
        text="WP",
        font=get_font(22, "bold"),
        text_color="white"
    ).place(relx=0.5, rely=0.5, anchor="center")

    # Salutation
    greeting = get_greeting(datetime.now().hour)
    ctk.CTkLabel(
        root,
        text=f"{greeting} !",
        font=get_font(22, "bold"),
        text_color=COLORS["text_primary"]
    ).grid(row=1, column=0, pady=(16, 4))

    # Sous-titre
    ctk.CTkLabel(
        root,
        text="Bienvenue sur WeatherProgramm",
        font=get_font(18),
        text_color=COLORS["text_secondary"]
    ).grid(row=2, column=0, pady=(0, 20))

    # Carte ville détectée
    city_card = ctk.CTkFrame(
        root,
        fg_color=COLORS["bg_card"],
        corner_radius=10,
        border_width=1,
        border_color=COLORS["border"]
    )
    city_card.grid(row=3, column=0, padx=48, sticky="ew", pady=(0, 8))
    city_card.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        city_card,
        text="Ville détectée",
        font=get_font(15),
        text_color=COLORS["text_muted"]
    ).grid(row=0, column=0, pady=(10, 2))

    ctk.CTkLabel(
        city_card,
        text=f"{detected_city}",
        font=get_font(18, "bold"),
        text_color=COLORS["text_primary"]
    ).grid(row=1, column=0, pady=(0, 4))

    ctk.CTkLabel(
        city_card,
        text= "Vous pourrez la modifier plus tard depuis la barre de recherche",
        font=get_font(15),
        text_color=COLORS["text_muted"]
    ).grid(row=2, column=0, pady=(0, 10))

    # Boutons
    btn_frame = ctk.CTkFrame(root, fg_color="transparent")
    btn_frame.grid(row=4, column=0, padx=48, pady=(16, 0), sticky="ew")
    btn_frame.grid_columnconfigure((0, 1), weight=1)

    def on_configure():
        result["go_to_profile"] = True
        root.destroy()

    def on_skip():
        root.destroy()

    ctk.CTkButton(
        btn_frame,
        text="Configurer mon profil",
        command=on_configure,
        corner_radius=10,
        fg_color=COLORS["accent"],
        height=42,
        text_color="white",
        font=get_font(13, "bold"),
        hover_color="#2d47d4",
    ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

    ctk.CTkButton(
        btn_frame,
        text="Passer",
        command=on_skip,
        corner_radius=10,
        fg_color="transparent",
        height=42,
        text_color=COLORS["text_secondary"],
        font=get_font(13),
        border_width=1,
        border_color=COLORS["border"],
        hover_color=COLORS["bg_card"],
    ).grid(row=0, column=1, sticky="ew", padx=(6, 0))
    

    root.mainloop()
    return result["go_to_profile"]


def main():
    """
    Point d'entrée de l'application.

    Charge la langue du profil existant, lance la fenêtre
    de bienvenue au premier lancement, puis ouvre MainWindow.
    Si l'utilisateur choisit de configurer son profil depuis
    la fenêtre de bienvenue, l'onglet Profil s'ouvre directement.
    """
    from ui.main_window import MainWindow
    from core.weather_service import WeatherService
    from core.user_profile import UserProfile


    go_to_profile = False

    if is_first_launch():
        city = WeatherService().get_city_auto()  or "Libreville"
        go_to_profile = show_welcome(city)

    app = MainWindow()

    if go_to_profile:
        app.show_frame("profile")

    app.mainloop()
    
if __name__ == "__main__":
    main()
