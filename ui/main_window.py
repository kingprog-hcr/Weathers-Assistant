# ui/main_window.py
import tkinter.font as tkfont
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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

# Éléments de navigation : (texte, clé interne)
NAV_ITEMS = [
    ("Météo du jour", "weather"),
    ("Programme",     "program"),
    ("Carte",         "map"),
    ("Profil",        "profile"),
]


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


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("WeatherProgramm")
        self.geometry("950x650")
        self.minsize(750, 500)      # taille minimale de la fenêtre

        self._active_frame = None   # frame actuellement affichée
        self._nav_buttons  = {}     # dict {clé: bouton} pour la nav

        self._setup_grid()
        self._build_sidebar()
        self._build_content()
        self._set_active_nav("weather")  # bouton Météo actif au démarrage

    # Grille principale

    def _setup_grid(self):
        """
        Définit 2 colonnes :
          col 0 -> sidebar  : proportionnelle (weight=1)
          col 1 -> contenu  : plus large (weight=4)
        Ainsi la sidebar grandit en plein écran mais reste plus petite
        que le contenu.
        """ 
        self.grid_columnconfigure(0, weight=1)  # sidebar : s'étire (1 part)
        self.grid_columnconfigure(1, weight=4)  # contenu : s'étire (4 parts)
        self.grid_rowconfigure(0, weight=1)     # unique ligne : pleine hauteur
        self.configure(fg_color=COLORS["bg_main"])

    # Sidebar 

    def _build_sidebar(self):
        """
        Construit la sidebar gauche.
        Elle s'adapte à la taille de la fenêtre grâce à sticky='nsew'
        et aux weights de la grille principale.
        la sidebar s'étire librement.
        """
        self.sidebar = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["bg_sidebar"]
        )
        # sticky="nsew" -> la sidebar remplit toute sa cellule de grille
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # La colonne 0 de la sidebar s'étire pour remplir la largeur
        self.sidebar.grid_columnconfigure(0, weight=1)

        # row=6 sera l'espace vide extensible qui pousse le bas vers le bas
        self.sidebar.grid_rowconfigure(6, weight=1)

        # row 0 Header : logo + titre sur la même ligne 
        # On utilise un frame intermédiaire + pack pour aligner
        # logo et titre horizontalement

        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.grid(row=0, column=0, padx=16, pady=(20, 12), sticky="ew")
        # sticky="ew" -> le header s'étire en largeur dans sa cellule

        # Carré bleu accent taille fixe 
        # grid_propagate(False) uniquement ici pour garder la taille du carré
        logo_box = ctk.CTkFrame(
            header,
            fg_color=COLORS["accent"],
            corner_radius=8,
            width=40, height=40
        )
        logo_box.pack(side="left", padx=(0, 10))
        # pack_propagate(False)  le carré garde ses dimensions
        logo_box.pack_propagate(False)

        # "HCR" centré dans le carré via place()
        # relx=0.5, rely=0.5 : position à 50% horizontal et 50% vertical
        # anchor="center" : le centre du label est à cette position
        ctk.CTkLabel(
            logo_box, text="HCR",
            font=get_font(15, "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Titre à droite du logo
        ctk.CTkLabel(
            header, text="WeatherProgramm",
            font=get_font(14, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")

        #row 1 : Séparateur 
        # sur les frames. highlightthickness=0 supprime la bordure du canvas.
        self._make_separator(row=1)

        #row 2: Label "Ville détectée" 
        ctk.CTkLabel(
            self.sidebar, text="Ville détectée",
            font=get_font(11),
            text_color=COLORS["text_muted"],
            anchor="w"          # texte aligné à gauche dans le label
        ).grid(row=2, column=0, padx=16, pady=(12, 2), sticky="w")

        # row 3  Nom de la ville 
        # self.city_label : attribut a modifier plus tard avec la vraie ville depuis WeatherService
        self.city_label = ctk.CTkLabel(
            self.sidebar, text="Chargement...",
            font=get_font(13, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        self.city_label.grid(row=3, column=0, padx=16, pady=(0, 12), sticky="w")

        # row 4 Séparateur
        self._make_separator(row=4)

        # row 5 Boutons de navigation
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(
            row=5, column=0,
            padx=8, pady=12, #petite marge des deux côtés
            sticky="ew"         # s'étire en largeur
        )
        nav_frame.grid_columnconfigure(0, weight=1)

        for i, (label, key) in enumerate(NAV_ITEMS):
            btn = ctk.CTkButton(
                nav_frame,
                text=label,
                font=get_font(13),
                anchor="w",                     # texte aligné à gauche
                height=40,
                corner_radius=8,
                fg_color="transparent",         # inactif = sans fond
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_card"],  # survol = fond carte
                command=lambda k=key: self._on_nav_click(k)
                # lambda k=key capture la valeur de key à chaque itération
                # sans ça, tous les boutons auraient la dernière valeur de key
            )
            btn.grid(row=i, column=0, sticky="ew", pady=2)
            self._nav_buttons[key] = btn      # stocke le bouton par clé

        # row 6 Espace extensible 

        #row 7  Séparateur 
        self._make_separator(row=7)

        # row 8 Label "Mise à jour" 
        ctk.CTkLabel(
            self.sidebar, text="Mise à jour",
            font=get_font(11),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=8, column=0, padx=16, pady=(8, 2), sticky="w")

        # row 9  Heure de mise à jour
        self.update_label = ctk.CTkLabel(
            self.sidebar, text="il y a 2 min",
            font=get_font(11),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        self.update_label.grid(row=9, column=0, padx=16, pady=(0, 16), sticky="w")

    def _make_separator(self, row: int):
        """
        Crée un séparateur horizontal d'1px dans la sidebar.
        Utilise CTkCanvas car CTkFrame ignore height=1 sur certains OS.
        """
        import tkinter as tk
        sep = tk.Canvas(
            self.sidebar,
            height=1,
            bg=COLORS["border"],
            highlightthickness=0    # supprime la bordure du canvas lui-même
        )
        sep.grid(row=row, column=0, sticky="ew")  # s'étire en largeur

    # Zone de contenu 

    def _build_content(self):
        """
        Crée la zone de contenu principale (colonne 1).
        Les frames des différentes pages seront placées ici.
        """
        self.content = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["bg_main"]
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    # Navigation

    def _set_active_nav(self, key: str):
        """
        Met le bouton correspondant à key en surbrillance bleue,
        remet tous les autres en transparent.
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
        Plus tard on appellera show_frame() ici.
        """
        self._set_active_nav(key)

    def show_frame(self, frame, nav_key: str):
        """
        Affiche un frame dans la zone de contenu
        et met à jour le bouton actif dans la sidebar.

        Paramètres
        frame   : CTkFrame à afficher
        nav_key : clé du bouton à activer ("weather", "program"...)
        """
        if self._active_frame:
            self._active_frame.grid_remove()  # cache le frame précédent
        frame.grid(row=0, column=0, sticky="nsew")  # affiche le nouveau
        self._active_frame = frame
        self._set_active_nav(nav_key)


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()