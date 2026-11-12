# ui/map_frame.py
"""
Page Carte interactive de l'application WeatherProgramm.

Affiche une carte centrée sur la ville avec des marqueurs pour chaque
activité du programme du jour qui dispose de coordonnées GPS.
Utilise le même programme que ProgramFrame via un callback get_program.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import io
import logging
import webbrowser

import customtkinter as ctk
import tkintermapview as tkmap
import requests
from PIL import Image, ImageTk, UnidentifiedImageError

from core.osm_tile_service import OSMTileCacheError, OSMTileService
from core.weather_service import WeatherService
from ui.config import COLORS, get_font


logger = logging.getLogger(__name__)


class _VisibleTilesMapView(tkmap.TkinterMapView):
    def __init__(self, *args, tile_service: OSMTileService, **kwargs):
        self._tile_service = tile_service
        self._tiles_enabled = False
        super().__init__(*args, **kwargs)
        self.set_tile_server(
            OSMTileService.TILE_URL_TEMPLATE,
            max_zoom=OSMTileService.MAX_ZOOM,
        )

    def pre_cache(self):
        # tkintermapview otherwise downloads a large ring of tiles outside the view.
        pass

    def center_on(self, latitude: float, longitude: float):
        self.set_position(latitude, longitude)
        if not self._tiles_enabled:
            self._tiles_enabled = True
            self.draw_initial_array()

    def request_image(self, zoom: int, x: int, y: int, db_cursor=None):
        if not self._tiles_enabled or not self.running:
            return self.empty_tile_image

        try:
            tile_data = self._tile_service.get_tile(zoom, x, y)
        except (OSMTileCacheError, requests.RequestException) as error:
            logger.warning(
                "Could not load OpenStreetMap tile %s/%s/%s: %s",
                zoom,
                x,
                y,
                error,
            )
            return self.empty_tile_image

        if tile_data is None:
            return self.empty_tile_image

        try:
            with Image.open(io.BytesIO(tile_data)) as tile_image:
                tile_image.load()
                if not self.running:
                    return self.empty_tile_image
                image = ImageTk.PhotoImage(tile_image)
        except (UnidentifiedImageError, OSError) as error:
            logger.warning(
                "OpenStreetMap returned an invalid tile %s/%s/%s: %s",
                zoom,
                x,
                y,
                error,
            )
            return self.empty_tile_image

        self.tile_image_cache[f"{zoom}{x}{y}"] = image
        return image


class MapFrame(ctk.CTkFrame):
    """
    Page carte interactive du programme du jour.

    Affiche la carte avec les marqueurs correspondent
    exactement aux activités affichées dans le programme, sans régénérer
    un nouveau programme.

    Attributes
    ----------
    _current_city : str | None
        Ville actuellement affichée.
    _get_program : callable | None
        Callback vers MainWindow pour récupérer le DayProgram actuel
        de ProgramFrame sans le régénérer.
    mapp : TkinterMapView | None
        Widget de carte interactif OpenStreetMap.
    info_label : CTkLabel
        Label affichant le nombre de lieux géolocalisés.
    """

    def __init__(self, parent, get_program=None):
        """
        Initialise la MapFrame.

        Parameters
        ----------
        parent : CTkFrame
            Frame parente.
        lang : str
            Langue de l'interface.
        get_program : callable | None
            Fonction sans argument qui retourne le DayProgram actuel
            de ProgramFrame. Passé par MainWindow.
        """
        super().__init__(parent, fg_color="transparent")
        self._current_city = None
        self._get_program  = get_program

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        """
        Construit l'interface : header compact + carte pleine hauteur.
        """

        # Header : titre + info 
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(16, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Carte du jour",
            font=get_font(22, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        self.info_label = ctk.CTkLabel(
            header,
            text="Chargement...",
            font=get_font(15),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.info_label.grid(row=0, column=1, sticky="e")

        # Conteneur carte prend tout l'espace restant
        map_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        map_container.grid(
            row=1, column=0,
            padx=24, pady=(0, 20),
            sticky="nsew"   # s'étire dans toutes les directions
        )
        map_container.grid_columnconfigure(0, weight=1)
        map_container.grid_rowconfigure(0, weight=1)

        try:
            tile_service = OSMTileService()
        except OSMTileCacheError as error:
            self.mapp = None
            ctk.CTkLabel(
                map_container,
                text=(
                    "La carte ne peut pas créer son cache local.\n"
                    "Vérifiez les droits d’accès au dossier de données."
                ),
                font=get_font(15),
                text_color=COLORS["text_secondary"],
                justify="center",
                wraplength=600
            ).grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
            self.info_label.configure(text="Carte indisponible")
            logger.error("Could not initialize OpenStreetMap tiles: %s", error)
            return

        self.mapp = _VisibleTilesMapView(
            map_container,
            corner_radius=10,
            tile_service=tile_service,
        )
        self.mapp.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.mapp.set_zoom(13)

        attribution = ctk.CTkFrame(map_container, fg_color="transparent")
        attribution.grid(row=1, column=0, sticky="e", padx=12, pady=(0, 6))
        link = ctk.CTkLabel(
            attribution,
            text="© OpenStreetMap contributors",
            font=get_font(11),
            text_color=COLORS["text_secondary"],
            cursor="hand2",
        )
        link.pack(side="left")
        link.bind(
            "<Button-1>",
            lambda _event: webbrowser.open(
                "https://www.openstreetmap.org/copyright"
            ),
        )

    def _load_data(self, city: str = None):
        """
        Charge la carte avec la ville et les marqueurs du programme actuel.

        Récupère le programme depuis ProgramFrame via _get_program()
        pour afficher exactement les mêmes activités.
        Si _get_program est None ou que le programme est vide,
        affiche juste la carte centrée sur la ville.

        Parameters
        ----------
        city : str, optional
            Ville à centrer. Si None, utilise la ville mémorisée
            ou la géolocalisation automatique.
        """
        if self.mapp is None:
            return

        service = WeatherService()

        city = city or self._current_city or service.get_city_auto() or "Libreville"
        self._current_city = city
        weather = service.get_current(city)

        # Récupère le programme de ProgramFrame via le callback
        # Si aucun programme n'est disponible encore, slots sera vide
        slots = []
        if self._get_program:
            program = self._get_program()
            if program is None:
                # ProgramFrame n'a pas encore fini de charge donc on Réessaie dans 2 secondes
                self.after(2000, lambda: self._load_data(city))
                return
            slots = program.slots

        self._update_ui(weather, slots)

    def _update_ui(self, weather, slots: list):
        """
        Centre la carte et place les marqueurs des activités géolocalisées.

        Parameters
        ----------
        city : str
            Ville à centrer sur la carte.
        slots : list[TimeSlot]
            Créneaux du programme seuls ceux avec lat/lon ont un marqueur.
        """
        # set_position avec coordonnées réelles
        if weather and weather.lat is not None and weather.lon is not None:
            self.mapp.after(
                100,
                lambda: self.mapp.center_on(weather.lat, weather.lon),
            )

        # Supprime les anciens marqueurs
        self.mapp.delete_all_marker()

        # Filtre uniquement les slots avec coordonnées GPS valides
        slots_with_coords = [
            s for s in slots
            if s.lat is not None and s.lon is not None
        ]

        for slot in slots_with_coords:
            # Texte du marqueur : heure + activité + lieu si disponible
            text = f"{slot.time} : {slot.activity}"
            if slot.location:
                text += f"\n {slot.location}"

            self.mapp.set_marker(slot.lat, slot.lon, text=text)

        # Met à jour le label d'info
        n = len(slots_with_coords)
        if n == 0:
            self.info_label.configure(
                text="Aucun lieu géolocalisé, donc utilise ton imagination pour savoir où aller."
            )
        else:
            self.info_label.configure(
                text=f"{n} lieu{'x' if n > 1 else ''} affiché{'s' if n > 1 else ''} sur la carte"
            )

    def refresh(self, city: str):
        """
        Rafraîchit la carte avec une nouvelle ville.

        Appelée par MainWindow._refresh_frames() lors d'un changement de ville.
        """
        self._load_data(city)


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1200x800")
    root.configure(fg_color=COLORS["bg_main"])
    root.title("WeatherProgramm : Carte")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    frame = MapFrame(root)
    frame.grid(row=0, column=0, sticky="nsew")
    root.mainloop()