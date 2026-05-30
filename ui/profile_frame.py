# ui/profile_frame.py
"""
Page Profil utilisateur de l'application WeatherProgramm.

Permet à l'utilisateur de configurer ses préférences personnelles :
nom, description, goûts, humeur du jour, style vestimentaire et cuisine.
Les modifications sont persistées dans data/profile.json via UserProfile.

Sections de la page :
    Avatar + Nom    : cercle avec initiales générées automatiquement
    Description     : bio courte transmise à l'IA pour personnaliser les suggestions
    Goûts           : sélection multiple par boutons toggle
    Humeur          : choix unique parmi Repos, Aventure, Aléatoire
    Préférences     : menus déroulants pour le style et la cuisine
    Historique      : nombre de journées enregistrées avec option d'effacement
    Sauvegarder     : bouton pleine largeur avec feedback visuel
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import customtkinter as ctk

from core.user_profile import UserProfile
from models import ProfileData
from ui.config import COLORS, get_font, get_all_tastes, ALL_CUISINES, ALL_STYLES, MOODS




class ProfileFrame(ctk.CTkFrame):
    """
    Page de configuration du profil utilisateur.

    Charge le profil au démarrage depuis data/profile.json et
    permet de modifier toutes les préférences. Les changements
    sont sauvegardés uniquement au clic sur le bouton Sauvegarder,
    sauf les goûts et l'humeur qui sont mis à jour en temps réel
    dans self._profile (mais pas persistés avant la sauvegarde).

    Attributes
    ----------
    scroll : CTkScrollableFrame
        Conteneur scrollable de toute la page.
    avatar_label : CTkLabel
        Label affichant les initiales dans le cercle avatar.
    name_entry : CTkEntry
        Champ de saisie du nom complet.
    description : CTkTextbox
        Zone de texte multi-lignes pour la description.
    style_menu : CTkComboBox
        Menu déroulant pour le style vestimentaire.
    cuisine_menu : CTkComboBox
        Menu déroulant pour la cuisine préférée.
    history_label : CTkLabel
        Label indiquant le nombre de journées enregistrées.
    save_btn : CTkButton
        Bouton de sauvegarde avec feedback visuel temporaire.
    """

    def __init__(self, parent, on_save = None, lang: str = "fr"):
        """
        Initialise la ProfileFrame.

        Parameters
        ----------
        parent : CTkFrame
            Frame parente, typiquement self.content de MainWindow.
        on_save : callable, optional
            Fonction appelée après chaque sauvegarde du profil.
            Normalement MainWindow._refresh_frames().
        """
        super().__init__(parent, fg_color="transparent")
        self._on_save = on_save
        self._all_tastes = get_all_tastes()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._profile       = UserProfile().load()
        self._taste_buttons = {}
        self._mood_buttons  = {}

        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"]
        )
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

        self._build_ui()
        self._load_profile()

    def _build_ui(self):
        """
        Construit la structure complète de la page.

        Crée tous les widgets avec des valeurs placeholder.
        Les vraies données sont injectées par _load_profile().
        """

        # En-tête de page
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 14), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Paramètres",
            font=get_font(15),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header, text="Mon profil",
            font=get_font(24, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).grid(row=1, column=0, sticky="w")

        # Section avatar et nom
        # Le cercle bleu affiche les deux premières initiales du nom.
        # Il se met à jour en temps réel à chaque frappe dans le champ nom.
        main = ctk.CTkFrame(
            self.scroll,
            fg_color=COLORS["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        main.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 14))
        main.grid_columnconfigure(1, weight=1)

        # Cercle avatar corner_radius = moitié de width/height pour un cercle parfait
        # grid_propagate(False) empêche le frame de rétrécir selon son contenu
        initials_frame = ctk.CTkFrame(
            main,
            fg_color=COLORS["accent"],
            corner_radius=35,
            width=70,
            height=70,
        )
        initials_frame.grid(row=0, column=0, padx=20, pady=16)
        initials_frame.grid_propagate(False)

        # place() pour centrer le label, grid() ne centre pas dans un frame de taille fixe
        self.avatar_label = ctk.CTkLabel(
            initials_frame,
            text="",
            font=get_font(22, "bold"),
            text_color="white"
        )
        self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        name_frame = ctk.CTkFrame(main, fg_color="transparent")
        name_frame.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=16)
        name_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            name_frame,
            text="Nom complet",
            font=get_font(15),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="Ton prénom et nom...",
            font=get_font(15),
            fg_color=COLORS["bg_main"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_primary"],
            height=38
        )
        self.name_entry.grid(row=1, column=0, sticky="ew")
        self.name_entry.bind("<KeyRelease>", lambda e: self._update_avatar())

        # Section description
        # CTkTextbox permet la saisie multi-lignes contrairement à CTkEntry.
        # Le contenu se lit avec .get("1.0", "end") où "1.0" = ligne 1 caractère 0.
        description_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        description_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=12)
        description_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            description_frame,
            text="Description",
            font=get_font(15),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.description = ctk.CTkTextbox(
            description_frame,
            height=80,
            corner_radius=10,
            fg_color=COLORS["bg_main"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_muted"],
            font=get_font(15)
        )
        self.description.grid(row=1, column=0, sticky="ew")

        # Section goûts
        # Grille fixe à 6 colonnes. Chaque bouton est un toggle :
        # bleu = goût sélectionné, blanc = non sélectionné.
        # La formule row = i // max_per_row et col = i % max_per_row
        # place automatiquement les boutons en lignes de 6.
        tastes_card = self._make_section_card(
            row=3, title="Mes goûts : sélectionne ce que tu aimes"
        )
        
        self.pills_frame = ctk.CTkFrame(tastes_card, fg_color="transparent")
        self.pills_frame.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")

        self._reload_tastes()
        # Section humeur
        # Trois boutons radio visuels  un seul peut être actif (bleu) à la fois.
        # _set_mood() remet tous les boutons en blanc puis active le bon.
        mood_card = self._make_section_card(row=4, title="Humeur du jour")
        mood_frame = ctk.CTkFrame(mood_card, fg_color="transparent")
        mood_frame.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")
        mood_frame.grid_columnconfigure((0, 1, 2), weight=1)

        for i, mood in enumerate(MOODS):
            btn = ctk.CTkButton(
                mood_frame,
                text=mood.capitalize(),
                height=38,
                corner_radius=8,
                fg_color="white",
                hover_color="#6174d7",
                border_width=1,
                border_color=COLORS["border"],
                text_color=COLORS["text_secondary"],
                font=get_font(15),
                command=lambda m=mood: self._set_mood(m)
            )
            btn.grid(row=0, column=i, padx=(0, 8) if i < 2 else 0, sticky="ew")
            self._mood_buttons[mood] = btn

        # Section préférences
        # CTkComboBox est préféré à CTkOptionMenu car son dropdown est
        # entièrement stylisable et reste dans la fenêtre de l'application.
        # state="readonly" empêche la saisie libre tout en permettant la sélection.
        pref_card = self._make_section_card(row=5, title = "Préférences")
        pref_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            pref_card, text="Style vestimentaire",
            font=get_font(15),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=1, column=0, padx=16, pady=(0, 4), sticky="w")

        self.style_menu = ctk.CTkComboBox(
            pref_card,
            values=ALL_STYLES,
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
        self.style_menu.grid(row=2, column=0, padx=(16, 8), pady=(0, 16), sticky="ew")

        ctk.CTkLabel(
            pref_card, text="Cuisine préférée",
            font=get_font(15),
            text_color=COLORS["text_muted"],
            anchor="w"
        ).grid(row=1, column=1, padx=16, pady=(0, 4), sticky="w")

        self.cuisine_menu = ctk.CTkComboBox(
            pref_card,
            values=ALL_CUISINES,
            fg_color=COLORS["bg_main"],
            border_color=COLORS["border"],
            border_width=1,
            button_color=COLORS["accent"],
            button_hover_color="#2d47d4",
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["accent"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            font=get_font(15),
            height=38,
            state="readonly"
        )
        self.cuisine_menu.grid(row=2, column=1, padx=(8, 16), pady=(0, 16), sticky="ew")
    
        # Section historique
        # Affiche le nombre de journées enregistrées dans self._profile.history.
        # Le bouton Effacer vide la liste et met à jour le label sans sauvegarder.
        # La suppression n'est réellement persistée qu'au prochain clic Sauvegarder.
        history_card = self._make_section_card(row=6, title="Historique")

        self.history_label = ctk.CTkLabel(
            history_card,
            text="0 journée enregistrée",
            text_color=COLORS["text_muted"],
            font=get_font(13)
        )
        self.history_label.grid(row=1, column=0, sticky="w", padx=16, pady=12)

        ctk.CTkButton(
            history_card,
            corner_radius=8,
            fg_color="transparent",
            height=34,
            border_width=1,
            border_color=COLORS["border"],
            text="Effacer",
            text_color=COLORS["text_secondary"],
            hover_color="#2a0a0a",
            command=self._clear_history
        ).grid(row=1, column=1, sticky="e", padx=16, pady=12)

        # Bouton de sauvegarde
        # Pleine largeur, persistance réelle du profil au clic.
        # Affiche "Sauvegardé !" pendant 2 secondes via self.after().
        self.save_btn = ctk.CTkButton(
            self.scroll,
            corner_radius=10,
            fg_color=COLORS["accent"],
            height=44,
            text="Sauvegarder",
            text_color="white",
            font=get_font(14, "bold"),
            hover_color="#2d47d4",
            command=self._save_profile
        )
        self.save_btn.grid(row=8, column=0, sticky="ew", padx=24, pady=(0, 24))

    def _make_section_card(self, row: int, title: str) -> ctk.CTkFrame:
        """
        Crée une carte de section avec un titre en haut.

        Toutes les sections de la page utilisent ce format uniforme.

        Parameters
        ----------
        row : int
            Ligne de la grille du scroll frame.
        title : str
            Titre affiché en haut de la carte en text_muted.

        Returns
        -------
        CTkFrame
            La carte créée, dans laquelle placer les widgets de la section.
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

    def _get_initials(self, name: str) -> str:
        """
        Génère les initiales depuis un nom complet.

        Prend la première lettre du prénom et la première lettre
        du deuxième mot. Si un seul mot, prend les deux premières lettres.

        Parameters
        ----------
        name : str
            Nom complet ex: "Chrysostome HCR"

        Returns
        -------
        str
            Initiales en majuscules ex: "CH", max 2 caractères.
        """
        if not name.strip():
            return "?"
        names = name.strip().split()
        if len(names) == 1:
            return names[0][:2].upper()
        return (names[0][0] + names[1][0]).upper()

    def _toggle_taste(self, taste: str):
        """
        Active ou désactive un goût dans le profil en mémoire.

        Si le goût est déjà sélectionné, le retire de self._profile.tastes
        et remet le bouton en blanc. Sinon l'ajoute et passe le bouton en bleu.
        Les changements ne sont pas persistés avant _save_profile().

        Parameters
        ----------
        taste : str
            Identifiant du goût ex: "sport", "culture".
        """
        if taste in self._profile.tastes:
            self._profile.tastes.remove(taste)
            self._taste_buttons[taste].configure(
                fg_color="white",
                text_color=COLORS["text_muted"]
            )
        else:
            self._profile.tastes.append(taste)
            self._taste_buttons[taste].configure(
                fg_color=COLORS["accent"],
                text_color="white"
            )

    def _set_mood(self, mood: str):
        """
        Définit l'humeur active et met à jour les boutons visuellement.

        Remet tous les boutons en blanc puis passe le bouton sélectionné en bleu.

        Parameters
        ----------
        mood : str
            Humeur choisie parmi "repos", "aventure", "random".
        """
        self._profile.mood = mood
        for m, btn in self._mood_buttons.items():
            if m == mood:
                btn.configure(fg_color=COLORS["accent"], text_color="white")
            else:
                btn.configure(fg_color="white", text_color=COLORS["text_muted"])

    def _update_avatar(self):
        """
        Recalcule et affiche les initiales dans l'avatar.

        Appelée automatiquement à chaque frappe dans name_entry
        via le binding KeyRelease.
        """
        name = self.name_entry.get()
        self.avatar_label.configure(text=self._get_initials(name))

    def _clear_history(self):
        """
        Efface l'historique des journées en mémoire et met à jour le label.

        L'effacement n'est persisté dans le fichier JSON qu'au prochain
        clic sur Sauvegarder.
        """
        self._profile.history = []
        self.history_label.configure(text="Aucune journée enregistrée")

    def _load_profile(self):
        """
        Charge le profil depuis self._profile et remplit tous les widgets.

        Appelée une fois au démarrage après _build_ui().
        Remplit nom, description, goûts, humeur, style, cuisine et historique.
        """
        # Nom et avatar
        self.name_entry.insert(0, self._profile.name)
        self._update_avatar()

        # Description
        self.description.delete("1.0", "end")
        if self._profile.description:
            self.description.insert("1.0", self._profile.description)

        # Goûts
        for taste, btn in self._taste_buttons.items():
            if taste in self._profile.tastes:
                btn.configure(fg_color=COLORS["accent"], text_color="white")
            else:
                btn.configure(fg_color="white", text_color=COLORS["text_muted"])

        # Humeur
        self._set_mood(self._profile.mood)

        # Style et cuisine
        self.style_menu.set(self._profile.style)
        self.cuisine_menu.set(self._profile.cuisine)
        # Historique
        n = len(self._profile.history)
        self.history_label.configure(
            text=f"{n} journée{'s' if n > 1 else ''} enregistrée{'s' if n > 1 else ''}"
        )

    def _save_profile(self):
        """
        Lit tous les champs, met à jour self._profile et persiste dans le JSON.

        Après la sauvegarde, affiche "Sauvegardé !" sur le bouton
        pendant 2 secondes avant de revenir au texte original.
        self.after() est utilisé pour ne pas bloquer l'interface.
        """
        self._profile.name        = self.name_entry.get().strip()
        self._profile.description = self.description.get("1.0", "end").strip()
        self._profile.style       = self.style_menu.get()
        self._profile.cuisine     = self.cuisine_menu.get()
        
        UserProfile().save(self._profile)
        if self._on_save:
            self._on_save()
            
        self.save_btn.configure(text="Sauvegardé !")
        self.after(2000, lambda: self.save_btn.configure(text="Sauvegarder"))
        
    def _reload_tastes(self):
        """
        Recharge les goûts depuis categories.json et reconstruit les pills.
        Appelée par MainWindow quand CustomFrame ajoute ou spprime une catégorie.
        """
        self._all_tastes = get_all_tastes()

        # Détruit et recrée les pills
        for widget in self.pills_frame.winfo_children():
            widget.destroy()
        self._taste_buttons = {}

        max_per_row = 5
        for i, taste in enumerate(self._all_tastes):
            r = i // max_per_row
            c = i % max_per_row
            btn = ctk.CTkButton(
                self.pills_frame,
                text=taste.capitalize(),
                width=110,
                height=40,
                corner_radius=16,
                fg_color="white",
                hover_color="#6174d7",
                border_width=1,
                border_color=COLORS["border"],
                text_color=COLORS["text_secondary"],
                font=get_font(15),
                command=lambda t=taste: self._toggle_taste(t)
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="w")
            self._taste_buttons[taste] = btn

        # Réapplique les goûts sélectionnés
        for taste, btn in self._taste_buttons.items():
            if taste in self._profile.tastes:
                btn.configure(fg_color=COLORS["accent"], text_color="white")
            else:
                btn.configure(fg_color="white", text_color=COLORS["text_muted"])
            

    def refresh(self, city: str = None):
        """
        Méthode de refresh appelée par MainWindow lors d'un changement de ville.

        Le profil n'est pas lié à la ville donc cette méthode ne fait rien.
        Elle existe pour respecter l'interface commune des frames.
        """
        pass


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("800x700")
    root.configure(fg_color=COLORS["bg_main"])
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    frame = ProfileFrame(root, lang = "es")
    frame.grid(row=0, column=0, sticky="nsew")
    root.mainloop()