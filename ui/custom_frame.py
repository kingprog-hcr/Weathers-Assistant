# ui/custom_frame.py
"""
Page de personnalisation de WeatherProgramm.

Permet à l'utilisateur de :
    - Créer ses propres catégories d'activités avec une couleur personnalisée
    - Ajouter ses propres activités dans n'importe quelle catégorie
      pour des conditions météo spécifiques
    - Supprimer ses activités et catégories personnalisées
    - Ajouter un plat dans un type de cuisine specifique
    - Ajouter un habit dans un style vestimentaire precis

Les modifications sont sauvegardées directement dans :
    - data/categories.json  : catégories et leurs keywords/couleurs
    - data/activities.json  : activités par condition météo et catégorie
    - data/food.json pour la cuisine
    -data/styles.json pour ;es styles vestimentaire
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import customtkinter as ctk
from CTkColorPicker import AskColor
from ui.config import COLORS, get_font, load_slot_categories, save_slot_categories, build_slot_categories


BASE_DIR        = Path(__file__).parent.parent
ACTIVITIES_FILE = BASE_DIR / "data" / "activities.json"


# Conditions météo disponibles avec leurs 

WEATHER_CONDITIONS = {
    "clear":        " Beau temps",
    "clouds":       " Nuageux",
    "rain":         " Pluie",
    "drizzle":      " Bruine",
    "thunderstorm": " Orage",
    "snow":         " Neige",
    "mist":         " Brume",
}

# Conditions météo pour les STYLES correspondent aux clés de styles.json
STYLE_CONDITIONS = {
    "chaud":        " Chaud",
    "doux":         " Doux",
    "frais":        " Frais",
    "froid":        " Froid",
    "froid_extreme":" Froid extrême",
    "pluie":        " Pluie",
    "neige":        " Neige",
}


def _load_activities() -> dict:
    """Charge activities.json."""
    try:
        with open(ACTIVITIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _save_activities(data: dict) -> bool:
    """Sauvegarde activities.json."""
    try:
        with open(ACTIVITIES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erreur sauvegarde activities.json : {e}")
        return False

class CustomFrame(ctk.CTkFrame):
    """
    Page de personnalisation des activités et catégories.

    Attributes
    ----------
    scroll : CTkScrollableFrame
        Conteneur scrollable de toute la page.
    _selected_color : str
        Couleur hex actuellement sélectionnée pour une nouvelle catégorie.
    _color_preview : CTkFrame
        Carré de prévisualisation de la couleur choisie.
    _weather_vars : dict[str, ctk.BooleanVar]
        Variables des checkboxes de sélection météo.
    """

    def __init__(self, parent, on_category_added=None):
        """
        Initialise la CustomFrame.

        Parameters
        ----------
        parent : CTkFrame
            Frame parente.
        lang : str
            Langue de l'interface.
        """
        super().__init__(parent, fg_color="transparent")
        self._on_category_added = on_category_added
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Couleur sélectionnée pour la nouvelle catégorie, bleu par défaut
        self._selected_color = COLORS["accent"]

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"]
        )
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        self._build_ui()
        self._refresh_categories_list()
        self._refresh_activities_list()

    def _make_section_card(self, row: int, title: str) -> ctk.CTkFrame:
        """
        Crée une carte de section avec un titre.

        Parameters
        ----------
        row : int
            Ligne dans le scroll frame.
        title : str
            Titre affiché en haut de la carte.

        Returns
        -------
        CTkFrame
            Carte créée.
        """
        card = ctk.CTkFrame(
            self.scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        card.grid(row=row, column=0, padx=24, pady=(0, 14), sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text=title,
            font=get_font(15),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, padx=16, pady=(12, 6), sticky="w")

        return card

    def _build_ui(self):
        """Construit l'interface complète de la page."""

        # En-tête
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 14), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Personnalisation",
            font=get_font(15),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header, text="Mes activités",
            font=get_font(24, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).grid(row=1, column=0, sticky="w")

        # Section 1 : Nouvelle catégorie
        self._build_new_category_section(row=1)

        # Section 2 : Catégories existantes
        self._build_categories_section(row=2)

        # Section 3 : Nouvelle activité
        self._build_new_activity_section(row=3)

        # Section 4 : Activités personnalisées
        self._build_activities_section(row=4)
        
        # Section 5 : food personalisee
        self._build_new_food_section(row=5)   
        
        # Section  6 : styles perso  
        self._build_new_style_section(row=6)  

    def _build_new_category_section(self, row: int):
        """
        Construit la section de création de nouvelle catégorie.

        Champs : nom + sélecteur couleur visuel + bouton Ajouter.
        """
        card = self._make_section_card(row=row, title="Créer une catégorie")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")
        inner.grid_columnconfigure(0, weight=1)

        # Champ nom
        ctk.CTkLabel(
            inner, text="Nom de la catégorie",
            font=get_font(15),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.cat_name_entry = ctk.CTkEntry(
            inner,
            placeholder_text="Ex: Famille, Spirituel, Bénévolat...",
            font=get_font(13),
            fg_color=COLORS["bg_main"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            height=38
        )
        self.cat_name_entry.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # Sélecteur de couleur
        ctk.CTkLabel(
            inner, text="Couleur du badge",
            font=get_font(13),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=2, column=0, sticky="w", pady=(0, 6))

        color_row = ctk.CTkFrame(inner, fg_color="transparent")
        color_row.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        # Carré de prévisualisation de la couleur choisie
        self._color_preview = ctk.CTkFrame(
            color_row,
            width=38, height=38,
            corner_radius=8,
            fg_color=self._selected_color
        )
        self._color_preview.pack(side="left", padx=(0, 10))
        self._color_preview.pack_propagate(False)

        ctk.CTkButton(
            color_row,
            text="Choisir une couleur",
            font=get_font(13),
            height=38,
            corner_radius=8,
            fg_color=COLORS["bg_main"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_card"],
            # Ouvre le sélecteur de couleur CTkColorPicker
            command=self._open_color_picker
        ).pack(side="left")

        # Bouton Ajouter
        ctk.CTkButton(
            inner,
            text="Créer la catégorie",
            font=get_font(13, "bold"),
            height=40,
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color="#2d47d4",
            text_color="white",
            command=self._add_category
        ).grid(row=4, column=0, sticky="ew")
    

    def _build_categories_section(self, row: int):
        """
        Construit la section listant les catégories existantes.

        Chaque catégorie est affichée avec sa couleur et un bouton suppression.
        """
        card = self._make_section_card(row=row, title="Catégories existantes")

        # Frame qui sera vidée et reconstruite par _refresh_categories_list()
        self.categories_list_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.categories_list_frame.grid(
            row=1, column=0, padx=16, pady=(0, 16), sticky="ew"
        )
        self.categories_list_frame.grid_columnconfigure(0, weight=1)

    def _build_new_activity_section(self, row: int):
        """
        Construit la section d'ajout d'une activité personnalisée.

        Champs : description, catégorie, météos concernées.
        """
        card = self._make_section_card(row=row, title="Ajouter une activité personnalisée")
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")
        inner.grid_columnconfigure(0, weight=1)

        # Description
        ctk.CTkLabel(
            inner, text="Description de l'activité",
            font=get_font(12),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.activity_entry = ctk.CTkEntry(
            inner,
            placeholder_text="Ex: Lecture de Descartes, Randonnée en famille...",
            font=get_font(13),
            fg_color=COLORS["bg_main"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            height=38
        )
        self.activity_entry.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # Catégorie
        ctk.CTkLabel(
            inner, text="Catégorie",
            font=get_font(12),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.category_menu = ctk.CTkComboBox(
            inner,
            values=self._get_category_names(),
            fg_color=COLORS["bg_main"],
            border_color=COLORS["border"],
            border_width=1,
            button_color=COLORS["accent"],
            button_hover_color="#2d47d4",
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["accent"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            font=get_font(13),
            height=38,
            state="readonly"
        )
        self.category_menu.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        # Sélection météos
        ctk.CTkLabel(
            inner, text="Météo(s) concernée(s)",
            font=get_font(12),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=4, column=0, sticky="w", pady=(0, 6))

        # BooleanVar pour chaque condition météo cochées par défaut
        self._weather_vars = {}
        weather_frame = ctk.CTkFrame(inner, fg_color="transparent")
        weather_frame.grid(row=5, column=0, sticky="ew", pady=(0, 12))

        for i, (condition, label) in enumerate(WEATHER_CONDITIONS.items()):
            var = ctk.BooleanVar(value=True)
            self._weather_vars[condition] = var

            ctk.CTkCheckBox(
                weather_frame,
                text=label,
                variable=var,
                font=get_font(12),
                text_color=COLORS["text_secondary"],
                fg_color=COLORS["accent"],
                hover_color="#2d47d4",
                checkmark_color="white",
                border_color=COLORS["border"]
            ).grid(
                row=i // 3, column=i % 3,
                padx=(0, 12), pady=4, sticky="w"
            )

        # Bouton ajouter
        ctk.CTkButton(
            inner,
            text="Ajouter l'activité",
            font=get_font(13, "bold"),
            height=40,
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color="#2d47d4",
            text_color="white",
            command=self._add_activity
        ).grid(row=6, column=0, sticky="ew")

    def _build_activities_section(self, row: int):
        """
        Construit la section listant les activités personnalisées.
        """
        card = self._make_section_card(row=row, title="Mes activités ajoutées")

        self.activities_list_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.activities_list_frame.grid(
            row=1, column=0, padx=16, pady=(0, 16), sticky="ew"
        )
        self.activities_list_frame.grid_columnconfigure(0, weight=1)
        
    def _build_new_food_section(self, row: int):
        """
        Section d'ajout d'un plat personnalisé dans food.json.
        Champs : description du plat + cuisine uniquement.
        La météo n'influence plus le choix des plats.
        """
        card = self._make_section_card(row=row, title="Ajouter un plat personnalisé")
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")
        inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            inner, text="Description du plat",
            font=get_font(12),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.food_entry = ctk.CTkEntry(
            inner,
            placeholder_text="Ex: Pizza, Poulet nyembwe, Thiéboudienne...",
            font=get_font(13),
            fg_color=COLORS["bg_main"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            height=38
        )
        self.food_entry.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(
            inner, text="Cuisine",
            font=get_font(12),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.food_cuisine_menu = ctk.CTkComboBox(
            inner,
            values=self._get_food_cuisine_names(),
            fg_color=COLORS["bg_main"],
            border_color=COLORS["border"],
            border_width=1,
            button_color=COLORS["accent"],
            button_hover_color="#2d47d4",
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["accent"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            font=get_font(13),
            height=38,
            state="readonly"
        )
        self.food_cuisine_menu.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkButton(
            inner,
            text="Ajouter le plat",
            font=get_font(13, "bold"),
            height=40,
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color="#2d47d4",
            text_color="white",
            command=self._add_food
        ).grid(row=4, column=0, sticky="ew")

    def _build_new_style_section(self, row: int):
        """
        Section d'ajout d'un vêtement personnalisé dans styles.json.
        Champs : description du vêtement, style, météo(s).
        """
        card = self._make_section_card(row=row, title="Ajouter un vêtement personnalisé")
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")
        inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            inner, text="Description du vêtement",
            font=get_font(12),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.style_item_entry = ctk.CTkEntry(
            inner,
            placeholder_text="Ex: boubou , dashiki coloré...",
            font=get_font(13),
            fg_color=COLORS["bg_main"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            height=38
        )
        self.style_item_entry.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(
            inner, text="Style vestimentaire",
            font=get_font(12),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.style_menu_custom = ctk.CTkComboBox(
            inner,
            values=self._get_style_names(),
            fg_color=COLORS["bg_main"],
            border_color=COLORS["border"],
            border_width=1,
            button_color=COLORS["accent"],
            button_hover_color="#2d47d4",
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["accent"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            font=get_font(13),
            height=38,
            state="readonly"
        )
        self.style_menu_custom.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(
            inner, text="Météo(s) concernée(s)",
            font=get_font(12),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=4, column=0, sticky="w", pady=(0, 6))

        self._style_weather_vars = {}
        weather_frame = ctk.CTkFrame(inner, fg_color="transparent")
        weather_frame.grid(row=5, column=0, sticky="ew", pady=(0, 12))

        for i, (condition, label) in enumerate(STYLE_CONDITIONS.items()):
            var = ctk.BooleanVar(value=True)
            self._style_weather_vars[condition] = var
            ctk.CTkCheckBox(
                weather_frame,
                text=label,
                variable=var,
                font=get_font(12),
                text_color=COLORS["text_secondary"],
                fg_color=COLORS["accent"],
                hover_color="#2d47d4",
                checkmark_color="white",
                border_color=COLORS["border"]
            ).grid(row=i // 3, column=i % 3, padx=(0, 12), pady=4, sticky="w")

        ctk.CTkButton(
            inner,
            text="Ajouter le vêtement",
            font=get_font(13, "bold"),
            height=40,
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color="#2d47d4",
            text_color="white",
            command=self._add_style_item
        ).grid(row=6, column=0, sticky="ew")


    def _add_food(self):
        """
        Ajoute un plat personnalisé dans food.json.

        food.json est maintenant une liste plate par cuisine :
        {"Gabonaise": ["plat1", "plat2", ...]}
        """
        food_name    = self.food_entry.get().strip()
        cuisine_name = self.food_cuisine_menu.get()

        if not food_name or not cuisine_name:
            return

        food_file = BASE_DIR / "data" / "food.json"
        try:
            with open(food_file, "r", encoding="utf-8") as f:
                food_data = json.load(f)
        except FileNotFoundError:
            food_data = {}

        cuisine_key = cuisine_name.lower()

        if cuisine_key not in food_data:
            food_data[cuisine_key] = []

        # Vérifie que le plat n'existe pas déjà
        existing = [
            item for item in food_data[cuisine_key]
            if (isinstance(item, str) and item == food_name)
            or (isinstance(item, dict) and item.get("name") == food_name)
        ]

        if not existing:
            # Stocke comme dict avec marqueur custom pour pouvoir supprimer
            food_data[cuisine_key].append({
                "name":   food_name,
                "custom": True
            })

        try:
            with open(food_file, "w", encoding="utf-8") as f:
                json.dump(food_data, f, indent=2, ensure_ascii=False)
            self.food_entry.delete(0, "end")
        except Exception as e:
            print(f"Erreur sauvegarde food.json : {e}")

    def _add_style_item(self):
        """
        Ajoute un vêtement personnalisé dans styles.json.
        Même logique que _add_activity mais pour styles.json.
        """
        item_name  = self.style_item_entry.get().strip()
        style_name = self.style_menu_custom.get()

        if not item_name or not style_name:
            return

        selected_conditions = [
            cond for cond, var in self._style_weather_vars.items()
            if var.get()
        ]
        if not selected_conditions:
            return

        styles_file = BASE_DIR / "data" / "styles.json"
        try:
            with open(styles_file, "r", encoding="utf-8") as f:
                styles_data = json.load(f)
        except FileNotFoundError:
            styles_data = {}

        style_key = style_name.lower()

        for condition in selected_conditions:
            if style_key not in styles_data:
                styles_data[style_key] = {}
            if condition not in styles_data[style_key]:
                styles_data[style_key][condition] = []

            existing = [
                item for item in styles_data[style_key][condition]
                if (isinstance(item, str) and item == item_name)
                or (isinstance(item, dict) and item.get("name") == item_name)
            ]
            if not existing:
                styles_data[style_key][condition].append({
                    "name":   item_name,
                    "custom": True
                })

        try:
            with open(styles_file, "w", encoding="utf-8") as f:
                json.dump(styles_data, f, indent=2, ensure_ascii=False)
            self.style_item_entry.delete(0, "end")
        except Exception as e:
            print(f"Erreur sauvegarde styles.json : {e}")
        

    def _open_color_picker(self):
        """
        Ouvre le sélecteur de couleur CTkColorPicker.

        Met à jour self._selected_color et le carré de prévisualisation
        avec la couleur choisie par l'utilisateur.
        """
        # AskColor() ouvre une fenêtre modale et retourne la couleur hex
        picker = AskColor()          # ouvre la fenêtre modale
        color  = picker.get()        # récupère la couleur hex ex: "#a855f7"
        if color:
            self._selected_color = color
            self._color_preview.configure(fg_color=color)

    def _get_category_names(self) -> list[str]:
        """
        Retourne la liste des noms de catégories depuis categories.json.
        """
        raw = load_slot_categories()
        return [data["label"] for data in raw.values()]

    def _get_category_key_by_label(self, label: str) -> str | None:
        """
        Retourne la clé JSON d'une catégorie depuis son label affiché.

        Ex: "Sport" = "sport"
        """
        raw = load_slot_categories()
        for key, data in raw.items():
            if data["label"] == label:
                return key
        return None

    def _refresh_categories_list(self):
        """
        Vide et reconstruit la liste des catégories affichées.

        Appelée après chaque ajout ou suppression de catégorie.
        Met aussi à jour le ComboBox de sélection de catégorie.
        """
        for widget in self.categories_list_frame.winfo_children():
            widget.destroy()

        raw = load_slot_categories()

        if not raw:
            ctk.CTkLabel(
                self.categories_list_frame,
                text="Aucune catégorie pour l'instant.",
                font=get_font(13),
                text_color=COLORS["text_muted"]
            ).grid(row=0, column=0, pady=8, sticky="w")
            return

        for i, (key, data) in enumerate(raw.items()):
            row_frame = ctk.CTkFrame(
                self.categories_list_frame,
                fg_color=COLORS["bg_main"],
                corner_radius=8,
                border_width=1,
                border_color=COLORS["border"]
            )
            row_frame.grid(row=i, column=0, sticky="ew", pady=(0, 6))
            row_frame.grid_columnconfigure(1, weight=1)

            # Carré couleur
            ctk.CTkFrame(
                row_frame,
                width=16, height=16,
                corner_radius=4,
                fg_color=data["fg"]
            ).grid(row=0, column=0, padx=(12, 8), pady=10)

            # Label
            ctk.CTkLabel(
                row_frame,
                text=data["label"],
                font=get_font(13),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).grid(row=0, column=1, sticky="w", pady=10)

            # Nombre de keywords
            n = len(data.get("keywords", []))
            ctk.CTkLabel(
                row_frame,
                text=f"{n} mot{'s' if n > 1 else ''}-clé{'s' if n > 1 else ''}",
                font=get_font(12),
                text_color=COLORS["text_muted"]
            ).grid(row=0, column=2, padx=12, pady=10)

            # Bouton supprimer désactivé pour les catégories de base
            is_custom = data.get("custom", False)
            ctk.CTkButton(
                row_frame,
                text="Supprimer" if is_custom else "Intégrée",
                font=get_font(11),
                height=28, width=80,
                corner_radius=6,
                fg_color="#2a0a0a" if is_custom else "transparent",
                text_color="#cc4444" if is_custom else COLORS["text_muted"],
                hover_color="#3a0a0a" if is_custom else None,
                hover=True if is_custom else False,
                border_width=1,
                border_color="#cc4444" if is_custom else COLORS["border"],
                state="normal" if is_custom else "disabled",
                command=lambda k=key: self._delete_category(k)
            ).grid(row=0, column=3, padx=12, pady=8)

        # Met à jour le ComboBox de la section activités
        if hasattr(self, "category_menu"):
            self.category_menu.configure(values=self._get_category_names())

    def _refresh_activities_list(self):
        """
        Vide et reconstruit la liste des activités personnalisées.

        Lit activities.json et affiche uniquement les activités
        marquées comme custom.
        """
        for widget in self.activities_list_frame.winfo_children():
            widget.destroy()

        activities = _load_activities()
        custom_items = []

        # Collecte toutes les activités marquées custom dans toutes les conditions
        for condition, categories in activities.items():
            for category, items in categories.items():
                for item in items:
                    if isinstance(item, dict) and item.get("custom"):
                        custom_items.append({
                            "condition": condition,
                            "category":  category,
                            "activity":  item["name"]
                        })

        if not custom_items:
            ctk.CTkLabel(
                self.activities_list_frame,
                text="Aucune activité personnalisée pour l'instant.",
                font=get_font(13),
                text_color=COLORS["text_muted"]
            ).grid(row=0, column=0, pady=8, sticky="w")
            return

        for i, item in enumerate(custom_items):
            row_frame = ctk.CTkFrame(
                self.activities_list_frame,
                fg_color=COLORS["bg_main"],
                corner_radius=8,
                border_width=1,
                border_color=COLORS["border"]
            )
            row_frame.grid(row=i, column=0, sticky="ew", pady=(0, 6))
            row_frame.grid_columnconfigure(0, weight=1)

            # Nom de l'activité
            ctk.CTkLabel(
                row_frame,
                text=item["activity"],
                font=get_font(13, "bold"),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).grid(row=0, column=0, padx=12, pady=(10, 2), sticky="w")

            # Catégorie + condition météo
            weather_label = WEATHER_CONDITIONS.get(item["condition"], item["condition"])
            ctk.CTkLabel(
                row_frame,
                text=f"{item['category'].capitalize()} : {weather_label}",
                font=get_font(11),
                text_color=COLORS["text_muted"],
                anchor="w"
            ).grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

            # Bouton supprimer
            ctk.CTkButton(
                row_frame,
                text="Supprimer",
                font=get_font(11),
                height=28, width=80,
                corner_radius=6,
                fg_color="#2a0a0a",
                text_color="#cc4444",
                hover_color="#3a0a0a",
                border_width=1,
                border_color="#cc4444",
                command=lambda c=item["condition"], cat=item["category"],
                               a=item["activity"]: self._delete_activity(c, cat, a)
            ).grid(row=0, column=1, rowspan=2, padx=12, pady=8)

    def _add_category(self):
        """
        Ajoute une nouvelle catégorie dans categories.json.

        La catégorie est marquée custom:true pour pouvoir être supprimée.
        Le keyword utilisé est le nom en minuscules.
        """
        name = self.cat_name_entry.get().strip()
        if not name:
            return

        raw = load_slot_categories()
        key = name.lower().replace(" ", "_")

        if key in raw:
            return  # catégorie déjà existante

        # Calcule une couleur de fond sombre depuis la couleur choisie
        fg_color = self._selected_color

        raw[key] = {
            "label":    name.capitalize(),
            "bg":       "#1a1a2e",    # fond sombre standard
            "fg":       fg_color,
            "border":   fg_color,
            "keywords": [key],        # le nom lui-même est le keyword principal
            "custom":   True          # marqué custom pour pouvoir supprimer
        }

        if save_slot_categories(raw):
            self.cat_name_entry.delete(0, "end")
            self._selected_color = COLORS["accent"]
            self._color_preview.configure(fg_color=COLORS["accent"])
            self._refresh_categories_list()
            if self._on_category_added:
                self._on_category_added()

    def _delete_category(self, key: str):
        """
        Supprime une catégorie personnalisée de categories.json.

        Seules les catégories marquées custom:true peuvent être supprimées.

        Parameters
        ----------
        key : str
            Clé JSON de la catégorie ex: "famille".
        """
        raw = load_slot_categories()
        if key in raw and raw[key].get("custom"):
            del raw[key]
            save_slot_categories(raw)
            self._refresh_categories_list()
        if self._on_category_added:
                self._on_category_added()

    def _add_activity(self):
        """
        Ajoute une activité personnalisée dans activities.json.

        L'activité est stockée comme un dict {"name": ..., "custom": True}
        pour être identifiable et supprimable.
        Elle est ajoutée dans chaque condition météo cochée.
        """
        activity_name = self.activity_entry.get().strip()
        category_label = self.category_menu.get()

        if not activity_name or not category_label:
            return

        # Récupère la clé JSON de la catégorie depuis son label affiché
        category_key = self._get_category_key_by_label(category_label)
        if not category_key:
            return

        # Conditions météo sélectionnées
        selected_conditions = [
            cond for cond, var in self._weather_vars.items()
            if var.get()
        ]

        if not selected_conditions:
            return

        activities = _load_activities()

        for condition in selected_conditions:
            if condition not in activities:
                activities[condition] = {}
            if category_key not in activities[condition]:
                activities[condition][category_key] = []

            # Vérifie que l'activité n'existe pas déjà dans cette condition
            existing = [
                item for item in activities[condition][category_key]
                if (isinstance(item, str) and item == activity_name)
                or (isinstance(item, dict) and item.get("name") == activity_name)
            ]

            if not existing:
                # Stocke comme dict avec marqueur custom
                activities[condition][category_key].append({
                    "name":   activity_name,
                    "custom": True
                })

        if _save_activities(activities):
            self.activity_entry.delete(0, "end")
            self._refresh_activities_list()

    def _delete_activity(self, condition: str, category: str, activity_name: str):
        """
        Supprime une activité personnalisée de activities.json.

        Parameters
        ----------
        condition : str
            Condition météo ex: "clear".
        category : str
            Catégorie ex: "religion".
        activity_name : str
            Nom de l'activité à supprimer.
        """
        activities = _load_activities()

        if condition in activities and category in activities[condition]:
            activities[condition][category] = [
                item for item in activities[condition][category]
                if not (
                    isinstance(item, dict)
                    and item.get("name") == activity_name
                    and item.get("custom")
                )
            ]

        if _save_activities(activities):
            self._refresh_activities_list()
        
    def _get_food_cuisine_names(self) -> list[str]:
        """Retourne les noms de cuisines depuis food.json."""
        food_file = BASE_DIR / "data" / "food.json"
        try:
            with open(food_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return list(data.keys())
        except FileNotFoundError:
            return []

    def _get_style_names(self) -> list[str]:
        """Retourne les noms de styles depuis styles.json."""
        styles_file = BASE_DIR / "data" / "styles.json"
        try:
            with open(styles_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return list(data.keys())
        except FileNotFoundError:
            return []


    def refresh(self, city: str = None):
        """
        Méthode de refresh, pas de données météo à recharger.
        Existe pour respecter l'interface commune des frames.
        """
        pass


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("900x700")
    root.configure(fg_color=COLORS["bg_main"])
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    frame = CustomFrame(root)
    frame.grid(row=0, column=0, sticky="nsew")
    root.mainloop()