# ui/main_window.py
"""
Module principal de l'interface graphique.

Contient la fenêtre principale de l'application WeatherProgramm,
incluant la sidebar de navigation, la barre de recherche de ville,
et le système de navigation entre les différentes pages.
"""

import sys
import tkinter as tk
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

from ui.config import COLORS, get_font

# Éléments de navigation : (texte affiché, clé interne)
NAV_ITEMS = [
    ("Météo du jour", "weather"),
    ("Programme",     "program"),
    ("Carte",         "map"),
    ("Profil",        "profile"),
]


class MainWindow(ctk.CTk):
    """
    Fenêtre principale de l'application WeatherProgramm.

    Gère la mise en page globale (sidebar + contenu),
    la navigation entre les pages, et la recherche de ville.

    Attributes

    sidebar : CTkFrame
        Panneau de navigation gauche.
    content : CTkFrame
        Zone d'affichage des pages.
    city_label : CTkLabel
        Label affichant la ville détectée dans la sidebar.
    city_entry : CTkEntry
        Champ de saisie pour rechercher une ville.
    update_label : CTkLabel
        Label affichant l'heure de dernière mise à jour.
    current_city : str
        Ville actuellement sélectionnée.
    """

    def __init__(self):
        """Initialise la fenêtre principale et construit l'interface."""
        super().__init__()
        self.title("WeatherProgramm")
         # Centre la fenêtre sur l'écran
        self.update_idletasks()
        x = (self.winfo_screenwidth()  // 2) - 600
        y = (self.winfo_screenheight() // 2) - 400
        self.geometry(f"1200x800+{x}+{y}")
        self.minsize(800, 550)

        self._active_frame = None   # frame actuellement affichée
        self._nav_buttons  = {}     # dict {clé: bouton} pour la nav
        self.current_city  = None   # ville actuellement sélectionnée
        self._frames       = {}     # dict {clé: frame} pour la nav

        self._setup_grid()
        self._build_sidebar()
        self._build_content()
        self._init_frames()
        self._set_active_nav("weather")
        self.show_frame("weather")

    # Grille principale 

    def _setup_grid(self):
        """
        Configure la grille principale de la fenêtre.

        Deux colonnes :
        - col 0 (sidebar)  : weight=1 — plus étroite
        - col 1 (contenu)  : weight=4 — plus large
        La sidebar s'adapte à la taille de la fenêtre
        mais reste proportionnellement plus petite que le contenu.
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)
        self.configure(fg_color=COLORS["bg_main"])

    # Sidebar

    def _build_sidebar(self):
        """
        Construit la sidebar gauche avec :
        - Logo + titre
        - Champ de recherche de ville
        - Boutons de navigation
        - Heure de mise à jour
        """
        self.sidebar = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["bg_sidebar"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(6, weight=1)  # espace extensible

        #row 0 Header : logo + titre 
        self._build_sidebar_header()

        # row 1 Séparateur
        self._make_separator(row=1)

        # row 2 Recherche de ville
        self._build_city_search()

        # row 3 — Séparateur
        self._make_separator(row=3)

        # row 4 Ville détectée 
        city_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        city_frame.grid(row=4, column=0, padx=16, pady=(10, 10), sticky="ew")
        city_frame.grid_columnconfigure(0, weight=1)

        # Ligne 0 du city_frame — label "Ville sélectionnée"
        ctk.CTkLabel(
            city_frame,
            text="Ville sélectionnée",
            font=get_font(13),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        # Ligne 1 du city_frame — nom de la ville (modifiable)
        self.city_label = ctk.CTkLabel(
            city_frame,
            text="Chargement...",
            font=get_font(16, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        self.city_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # row 5 Boutons de navigation
        self._build_nav_buttons()

        # row 6 Espace extensible 
        # géré par grid_rowconfigure(6, weight=1) plus haut

        # row 7 Séparateur 
        self._make_separator(row=7)

        # row 8 Mise à jour
        ctk.CTkLabel(
            self.sidebar,
            text="Mise à jour",
            font=get_font(11),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=8, column=0, padx=16, pady=(8, 2), sticky="w")

        self.update_label = ctk.CTkLabel(
            self.sidebar,
            text="—",
            font=get_font(11),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        self.update_label.grid(row=9, column=0, padx=16, pady=(0, 16), sticky="w")

    def _build_sidebar_header(self):
        """
        Construit le header de la sidebar :
        carré logo + nom de l'application sur la même ligne.
        """
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.grid(row=0, column=0, padx=16, pady=(20, 12), sticky="ew")

        # Carré bleu avec initiales
        logo_box = ctk.CTkFrame(
            header,
            fg_color=COLORS["accent"],
            corner_radius=8,
            width=40, height=40
        )
        logo_box.pack(side="left", padx=(0, 10))
        logo_box.pack_propagate(False)

        ctk.CTkLabel(
            logo_box,
            text="HCR",
            font=get_font(13, "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Titre
        ctk.CTkLabel(
            header,
            text="WeatherProgramm",
            font=get_font(14, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

    def _build_city_search(self):
        """
        Construit la zone de recherche de ville dans la sidebar.

        L'utilisateur peut taper une ville et appuyer sur Entrée
        ou cliquer sur le bouton pour actualiser toutes les données.
        """
        search_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        search_frame.grid(row=2, column=0, padx=12, pady=(10, 10), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        # Label
        ctk.CTkLabel(
            search_frame,
            text="Rechercher une ville",
            font=get_font(11),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, columnspan=2, padx=4, pady=(0, 6), sticky="w")

        # Champ de saisie
        self.city_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Ex: Paris, Libreville, Lisbonne...",
            font=get_font(13),
            fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            height=36,
        )
        self.city_entry.grid(row=1, column=0, sticky="ew", padx=(4, 6))

        # Appuyer sur Entrée -> recherche
        self.city_entry.bind("<Return>", lambda e: self._on_city_search())

        # Bouton de recherche
        search_btn = ctk.CTkButton(
            search_frame,
            text="→",
            font=get_font(14, "bold"),
            width=36,
            height=36,
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color="#2d47d4",
            command=self._on_city_search
        )
        search_btn.grid(row=1, column=1, padx=(0, 4))

    def _build_nav_buttons(self):
        """
        Construit les boutons de navigation dans la sidebar.
        Chaque bouton est associé à une clé qui correspond
        à une frame dans self._frames.
        """
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(row=5, column=0, padx=8, pady=12, sticky="ew")
        nav_frame.grid_columnconfigure(0, weight=1)

        for i, (label, key) in enumerate(NAV_ITEMS):
            btn = ctk.CTkButton(
                nav_frame,
                text=label,
                font=get_font(13),
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_card"],
                command=lambda k=key: self._on_nav_click(k)
            )
            btn.grid(row=i, column=0, sticky="ew", pady=2)
            self._nav_buttons[key] = btn

    def _make_separator(self, row: int):
        """
        Crée un séparateur horizontal d'1px dans la sidebar.

        Utilise tk.Canvas plutôt que CTkFrame car Tkinter
        ignore height=1 sur les frames sur certains OS.

        Parameters
        
        row : int
            Ligne de la grille sidebar où placer le séparateur.
        """
        sep = tk.Canvas(
            self.sidebar,
            height=1,
            bg=COLORS["border"],
            highlightthickness=0
        )
        sep.grid(row=row, column=0, sticky="ew")

    # Zone de contenu

    def _build_content(self):
        """
        Crée la zone de contenu principale (colonne 1).
        Les frames des différentes pages y sont placées
        et affichées via show_frame().
        """
        self.content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["bg_main"]
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _init_frames(self):
        """
        Instancie toutes les frames de l'application.
        Elles sont créées une seule fois au démarrage
        puis affichées/cachées selon la navigation.
        """
        from ui.weather_frame import WeatherFrame
        from ui.program_frame import ProgramFrame
        # from ui.map_frame     import MapFrame
        from ui.profile_frame import ProfileFrame

        self._frames["weather"] = WeatherFrame(self.content)
        self._frames["program"] = ProgramFrame(self.content)
        # self._frames["map"]     = MapFrame(self.content)
        self._frames["profile"] = ProfileFrame(self.content, on_save=self._refresh_frames)
        
        self.current_city = self._frames["weather"].city_label.cget("text")
        self.city_label.configure(text = self.current_city)
        
    # Navigation 

    def _set_active_nav(self, key: str):
        """
        Met le bouton de navigation correspondant à key
        en surbrillance bleue et remet les autres en transparent.

        Parameters

        key : str
            Clé du bouton à activer ("weather", "program"...).
        """
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=COLORS["accent"],
                    text_color="white"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"]
                )

    def _on_nav_click(self, key: str):
        """
        Appelée quand l'utilisateur clique sur un bouton de nav.
        Affiche la frame correspondante si elle existe.

        Parameters
        
        key : str
            Clé de la page à afficher.
        """
        if key in self._frames:
            self.show_frame(key)
        else:
            # Frame pas encore implémentée
            self._set_active_nav(key)

    def show_frame(self, key: str):
        """
        Affiche la frame correspondant à key dans la zone de contenu
        et met à jour le bouton actif dans la sidebar.

        Parameters
        
        key : str
            Clé de la page à afficher ("weather", "program"...).
        """
        if key not in self._frames:
            return

        if self._active_frame:
            self._active_frame.grid_remove()

        frame = self._frames[key]
        frame.grid(row=0, column=0, sticky="nsew")
        self._active_frame = frame
        self._set_active_nav(key)

    # Recherche de ville 

    def _on_city_search(self):
        """
        Appelée quand l'utilisateur valide une recherche de ville.

        Récupère la ville saisie, met à jour le label dans la sidebar,
        et demande à toutes les frames de se rafraîchir avec
        la nouvelle ville.
        """
        city = self.city_entry.get().strip()

        if not city:
            return

        # Met à jour le label ville dans la sidebar
        self.city_label.configure(text=f"{city}")
        self.current_city = city

        

        # Efface le champ de saisie
        self.city_entry.delete(0, "end")

        # Rafraîchit les frames qui supportent le changement de ville
        self._refresh_frames()

    def _refresh_frames(self):
        """
        Demande à toutes les frames instanciées de se rafraîchir
        avec la nouvelle ville.

        Chaque frame qui supporte le changement de ville
        doit implémenter une méthode refresh(city).

        Parameters
        
        city : str
            Nouvelle ville à utiliser pour toutes les frames.
        """
        # Met à jour l'heure de dernière recherche
        from datetime import datetime
        now = datetime.now().strftime("%H:%M")
        self.update_label.configure(text=f"à {now}\n\nBy HCR")
        
        city = self.current_city or "Libreville"
        for frame in self._frames.values():
            if hasattr(frame, "refresh"):
                frame.refresh(city)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()