import tkinter.font as tkfont
import customtkinter as ctk
import io
import urllib.request
from PIL import Image


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

ALL_TASTES = [
    "sport",        "culture",      "nature",
    "shopping",     "repos",        "social",
    "creatif",      "gastronomie",  "academique",
    "religion",     "maison",       "professionnel",
]

TRANSLATIONS = {
    "fr": {
        "nav_weather":   "Météo du jour",
        "nav_program":   "Programme",
        "nav_map":       "Carte",
        "nav_profile":   "Profil",
        "city_detected": "Ville sélectionnée",
        "search_city":   "Rechercher une ville",
        "search_placeholder": "Ex: Paris, Libreville, Lisbonne...",
        "last_update":   "Mise à jour",
        "weather_title": "Météo du jour",
        "feels_like":    "Ressenti",
        "wind":          "Vent",
        "score":         "Score journée",
        "humidity":      "Humidité",
        "outfit_title":  "Tenue suggérée",
        "food_title":    "Suggestions repas",
        "program_title": "Programme du jour",
        "regenerate":    "Regénérer",
        "activities":    "Activités",
        "mood_label":    "Humeur",
        "slots_label":   "créneaux planifiés",
        "profile_title": "Mon profil",
        "settings":      "Paramètres",
        "full_name":     "Nom complet",
        "description":   "Description",
        "my_tastes":     "Mes goûts : sélectionne ce que tu aimes",
        "mood_day":      "Humeur du jour",
        "preferences":   "Préférences",
        "style_label":   "Style vestimentaire",
        "cuisine_label": "Cuisine préférée",
        "history":       "Historique",
        "clear":         "Effacer",
        "save":          "Sauvegarder le profil",
        "saved":         "Sauvegardé !",
        "language":      "Langue de l'application",
        "lang_restart":  "Le changement de langue sera appliqué au prochain lancement.",
        "welcome_title": "Bienvenue sur WeatherProgramm",
        "detected_city": "Ville détectée automatiquement",
        "city_hint":     "Vous pourrez la modifier depuis la barre de recherche",
        "configure":     "Configurer mon profil",
        "skip":          "Passer",
        "greeting_morning":   "Bonjour",
        "greeting_afternoon": "Bon après-midi",
        "greeting_evening":   "Bonsoir",
    },
    "en": {
        "nav_weather":   "Today's Weather",
        "nav_program":   "Program",
        "nav_map":       "Map",
        "nav_profile":   "Profile",
        "city_detected": "Selected city",
        "search_city":   "Search a city",
        "search_placeholder": "Ex: London, Paris, Libreville...",
        "last_update":   "Last update",
        "weather_title": "Today's Weather",
        "feels_like":    "Feels like",
        "wind":          "Wind",
        "score":         "Day score",
        "humidity":      "Humidity",
        "outfit_title":  "Suggested outfit",
        "food_title":    "Meal suggestions",
        "program_title": "Today's Program",
        "regenerate":    "Regenerate",
        "activities":    "Activities",
        "mood_label":    "Mood",
        "slots_label":   "planned slots",
        "profile_title": "My Profile",
        "settings":      "Settings",
        "full_name":     "Full name",
        "description":   "Description",
        "my_tastes":     "My tastes : select what you enjoy",
        "mood_day":      "Mood of the day",
        "preferences":   "Preferences",
        "style_label":   "Clothing style",
        "cuisine_label": "Preferred cuisine",
        "history":       "History",
        "clear":         "Clear",
        "save":          "Save profile",
        "saved":         "Saved !",
        "language":      "App language",
        "lang_restart":  "Language change will apply on next launch.",
        "welcome_title": "Welcome to WeatherProgramm",
        "detected_city": "Automatically detected city",
        "city_hint":     "You can change it from the search bar",
        "configure":     "Set up my profile",
        "skip":          "Skip",
        "greeting_morning":   "Good morning",
        "greeting_afternoon": "Good afternoon",
        "greeting_evening":   "Good evening",
    },
    "es": {
        "nav_weather":   "Clima del día",
        "nav_program":   "Programa",
        "nav_map":       "Mapa",
        "nav_profile":   "Perfil",
        "city_detected": "Ciudad seleccionada",
        "search_city":   "Buscar una ciudad",
        "search_placeholder": "Ej: Madrid, Oyem, Barcelona...",
        "last_update":   "Última actualización",
        "weather_title": "Clima del día",
        "feels_like":    "Sensación térmica",
        "wind":          "Viento",
        "score":         "Puntuación del día",
        "humidity":      "Humedad",
        "outfit_title":  "Outfit sugerido",
        "food_title":    "Sugerencias de comida",
        "program_title": "Programa del día",
        "regenerate":    "Regenerar",
        "activities":    "Actividades",
        "mood_label":    "Humor",
        "slots_label":   "franjas planificadas",
        "profile_title": "Mi perfil",
        "settings":      "Configuración",
        "full_name":     "Nombre completo",
        "description":   "Descripción",
        "my_tastes":     "Mis gustos : selecciona lo que te gusta",
        "mood_day":      "Humor del día",
        "preferences":   "Preferencias",
        "style_label":   "Estilo de ropa",
        "cuisine_label": "Cocina preferida",
        "history":       "Historial",
        "clear":         "Borrar",
        "save":          "Guardar perfil",
        "saved":         "¡Guardado!",
        "language":      "Idioma de la aplicación",
        "lang_restart":  "El cambio de idioma se aplicará en el próximo inicio.",
        "welcome_title": "Bienvenido a WeatherProgramm",
        "detected_city": "Ciudad detectada automáticamente",
        "city_hint":     "Puedes cambiarla desde la barra de búsqueda",
        "configure":     "Configurar mi perfil",
        "skip":          "Omitir",
        "greeting_morning":   "Buenos días",
        "greeting_afternoon": "Buenas tardes",
        "greeting_evening":   "Buenas noches",
    },
    "pt": {
        "nav_weather":   "Clima do dia",
        "nav_program":   "Programa",
        "nav_map":       "Mapa",
        "nav_profile":   "Perfil",
        "city_detected": "Cidade selecionada",
        "search_city":   "Pesquisar uma cidade",
        "search_placeholder": "Ex: Lisboa, Paris...",
        "last_update":   "Última atualização",
        "weather_title": "Clima do dia",
        "feels_like":    "Sensação térmica",
        "wind":          "Vento",
        "score":         "Pontuação do dia",
        "humidity":      "Humidade",
        "outfit_title":  "Roupa sugerida",
        "food_title":    "Sugestões de refeições",
        "program_title": "Programa do dia",
        "regenerate":    "Regenerar",
        "activities":    "Atividades",
        "mood_label":    "Humor",
        "slots_label":   "horários planeados",
        "profile_title": "O meu perfil",
        "settings":      "Definições",
        "full_name":     "Nome completo",
        "description":   "Descrição",
        "my_tastes":     "Os meus gostos : seleciona o que gostas",
        "mood_day":      "Humor do dia",
        "preferences":   "Preferências",
        "style_label":   "Estilo de roupa",
        "cuisine_label": "Cozinha preferida",
        "history":       "Histórico",
        "clear":         "Apagar",
        "save":          "Guardar perfil",
        "saved":         "Guardado !",
        "language":      "Idioma da aplicação",
        "lang_restart":  "A mudança de idioma será aplicada no próximo início.",
        "welcome_title": "Bem-vindo ao WeatherProgramm",
        "detected_city": "Cidade detetada automaticamente",
        "city_hint":     "Pode alterá-la na barra de pesquisa",
        "configure":     "Configurar o meu perfil",
        "skip":          "Ignorar",
        "greeting_morning":   "Bom dia",
        "greeting_afternoon": "Boa tarde",
        "greeting_evening":   "Boa noite",
    },
    "zh": {
        "nav_weather":   "今日天气",
        "nav_program":   "日程",
        "nav_map":       "地图",
        "nav_profile":   "个人资料",
        "city_detected": "已选城市",
        "search_city":   "搜索城市",
        "search_placeholder": "例如：巴黎、里昂...",
        "last_update":   "最后更新",
        "weather_title": "今日天气",
        "feels_like":    "体感温度",
        "wind":          "风速",
        "score":         "今日评分",
        "humidity":      "湿度",
        "outfit_title":  "穿搭建议",
        "food_title":    "餐饮建议",
        "program_title": "今日日程",
        "regenerate":    "重新生成",
        "activities":    "活动",
        "mood_label":    "心情",
        "slots_label":   "个计划时段",
        "profile_title": "我的资料",
        "settings":      "设置",
        "full_name":     "全名",
        "description":   "简介",
        "my_tastes":     "我的喜好 : 选择你喜欢的",
        "mood_day":      "今日心情",
        "preferences":   "偏好设置",
        "style_label":   "穿衣风格",
        "cuisine_label": "饮食偏好",
        "history":       "历史记录",
        "clear":         "清除",
        "save":          "保存资料",
        "saved":         "已保存！",
        "language":      "应用语言",
        "lang_restart":  "语言更改将在下次启动时生效。",
        "welcome_title": "欢迎使用 WeatherProgramm",
        "detected_city": "自动检测到的城市",
        "city_hint":     "您可以通过搜索栏更改城市",
        "configure":     "配置我的资料",
        "skip":          "跳过",
        "greeting_morning":   "早上好",
        "greeting_afternoon": "下午好",
        "greeting_evening":   "晚上好",
    },
}


#  Catalogue des badges 
# Associe des mots clés d'activité à un badge coloré.
# Format : mot_clé : (label, bg, fg, border_color)
# Les couleurs sont choisies pour être lisibles sur fond sombre.
# Aligné avec les catégories de data/activities.json.

SLOT_CATEGORIES = {
    #  Repas (créneaux fixes du DayPlanner) 
    "déjeuner":     ("Repas",        "#1a1a4a", "#6b8fff", "#3d5af1"),
    "dîner":        ("Repas",        "#1a1a4a", "#6b8fff", "#3d5af1"),
    "gouté":       ("Repas",        "#1a1a4a", "#6b8fff", "#3d5af1"),
    "petit":        ("Repas",        "#1a1a4a", "#6b8fff", "#3d5af1"),

    # Sport 
    "sport":        ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "yoga":         ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "salle":        ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "natation":     ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "jogging":      ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "vélo":         ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "football":     ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "tennis":       ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "escalade":     ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "kayak":        ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "fitness":      ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "pilates":      ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "boxe":         ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "danse":        ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "ski":          ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "randonnée":    ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),
    "course":       ("Sport",        "#2a0a2a", "#cc55cc", "#991a99"),

    # Culture 
    "musée":        ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),
    "cinéma":       ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),
    "galerie":      ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),
    "visite":       ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),
    "exposition":   ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),
    "festival":     ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),
    "concert":      ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),
    "théâtre":      ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),
    "opéra":        ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),
    "conférence":   ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),
    "librairie":    ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),
    "château":      ("Culture",      "#0f2a1a", "#4dbb7a", "#1a8a4a"),

    # Nature 
    "parc":         ("Nature",       "#0a2a0a", "#5dcc5d", "#1a991a"),
    "balade":       ("Nature",       "#0a2a0a", "#5dcc5d", "#1a991a"),
    "jardin":       ("Nature",       "#0a2a0a", "#5dcc5d", "#1a991a"),
    "pique-nique":  ("Nature",       "#0a2a0a", "#5dcc5d", "#1a991a"),
    "forêt":        ("Nature",       "#0a2a0a", "#5dcc5d", "#1a991a"),
    "aquarium":     ("Nature",       "#0a2a0a", "#5dcc5d", "#1a991a"),
    "serre":        ("Nature",       "#0a2a0a", "#5dcc5d", "#1a991a"),
    "observation":  ("Nature",       "#0a2a0a", "#5dcc5d", "#1a991a"),
    "astronomie":   ("Nature",       "#0a2a0a", "#5dcc5d", "#1a991a"),
    "cueillette":   ("Nature",       "#0a2a0a", "#5dcc5d", "#1a991a"),

    # Shopping 
    "marché":       ("Shopping",     "#2a1a08", "#cc8844", "#995511"),
    "shopping":     ("Shopping",     "#2a1a08", "#cc8844", "#995511"),
    "brocante":     ("Shopping",     "#2a1a08", "#cc8844", "#995511"),
    "vide-grenier": ("Shopping",     "#2a1a08", "#cc8844", "#995511"),
    "boutique":     ("Shopping",     "#2a1a08", "#cc8844", "#995511"),

    # Social 
    "soirée":       ("Social",       "#2a2a08", "#ccbb44", "#99991a"),
    "amis":         ("Social",       "#2a2a08", "#ccbb44", "#99991a"),
    "jeux":         ("Social",       "#2a2a08", "#ccbb44", "#99991a"),
    "barbecue":     ("Social",       "#2a2a08", "#ccbb44", "#99991a"),
    "rencontre":    ("Social",       "#2a2a08", "#ccbb44", "#99991a"),
    "discussion":   ("Social",       "#2a2a08", "#ccbb44", "#99991a"),
    "escape":       ("Social",       "#2a2a08", "#ccbb44", "#99991a"),
    "tournoi":      ("Social",       "#2a2a08", "#ccbb44", "#99991a"),

    # Repos 
    "café":         ("Repos",        "#1a2a2a", "#44bbcc", "#119999"),
    "lecture":      ("Repos",        "#1a2a2a", "#44bbcc", "#119999"),
    "méditation":   ("Repos",        "#1a2a2a", "#44bbcc", "#119999"),
    "spa":          ("Repos",        "#1a2a2a", "#44bbcc", "#119999"),
    "podcast":      ("Repos",        "#1a2a2a", "#44bbcc", "#119999"),
    "sieste":       ("Repos",        "#1a2a2a", "#44bbcc", "#119999"),
    "terrasse":     ("Repos",        "#1a2a2a", "#44bbcc", "#119999"),
    "journaling":   ("Repos",        "#1a2a2a", "#44bbcc", "#119999"),

    # Créatif
    "photographie": ("Créatif",      "#2a1a2a", "#bb66cc", "#881188"),
    "dessin":       ("Créatif",      "#2a1a2a", "#bb66cc", "#881188"),
    "écriture":     ("Créatif",      "#2a1a2a", "#bb66cc", "#881188"),
    "peinture":     ("Créatif",      "#2a1a2a", "#bb66cc", "#881188"),
    "musique":      ("Créatif",      "#2a1a2a", "#bb66cc", "#881188"),
    "composition":  ("Créatif",      "#2a1a2a", "#bb66cc", "#881188"),
    "poterie":      ("Créatif",      "#2a1a2a", "#bb66cc", "#881188"),
    "tricot":       ("Créatif",      "#2a1a2a", "#bb66cc", "#881188"),
    "couture":      ("Créatif",      "#2a1a2a", "#bb66cc", "#881188"),
    "improvisation":("Créatif",      "#2a1a2a", "#bb66cc", "#881188"),

    # Gastronomie 
    "brunch":       ("Gastro",       "#2a0a0a", "#cc4444", "#991111"),
    "dégustation":  ("Gastro",       "#2a0a0a", "#cc4444", "#991111"),
    "restaurant":   ("Gastro",       "#2a0a0a", "#cc4444", "#991111"),
    "cuisine":      ("Gastro",       "#2a0a0a", "#cc4444", "#991111"),
    "pâtisserie":   ("Gastro",       "#2a0a0a", "#cc4444", "#991111"),
    "atelier":      ("Gastro",       "#2a0a0a", "#cc4444", "#991111"),
    "gastronomique":("Gastro",       "#2a0a0a", "#cc4444", "#991111"),

    #  Académique 
    "révision":     ("Académique",   "#1a1a08", "#aaaa33", "#777711"),
    "étudier":      ("Académique",   "#1a1a08", "#aaaa33", "#777711"),
    "cours":        ("Académique",   "#1a1a08", "#aaaa33", "#777711"),
    "mooc":         ("Académique",   "#1a1a08", "#aaaa33", "#777711"),
    "programmer":   ("Académique",   "#1a1a08", "#aaaa33", "#777711"),
    "flashcards":   ("Académique",   "#1a1a08", "#aaaa33", "#777711"),

    # Religion 
    "messe":        ("Religion",     "#1a0a0a", "#cc7744", "#994422"),
    "prière":       ("Religion",     "#1a0a0a", "#cc7744", "#994422"),
    "chapelet":     ("Religion",     "#1a0a0a", "#cc7744", "#994422"),
    "pèlerinage":   ("Religion",     "#1a0a0a", "#cc7744", "#994422"),
    "adoration":    ("Religion",     "#1a0a0a", "#cc7744", "#994422"),

    # Maison 
    "jardinage":    ("Maison",       "#0a1a0a", "#66aa44", "#337711"),
    "bricolage":    ("Maison",       "#0a1a0a", "#66aa44", "#337711"),
    "ménage":       ("Maison",       "#0a1a0a", "#66aa44", "#337711"),
    "organisation": ("Maison",       "#0a1a0a", "#66aa44", "#337711"),
    "décoration":   ("Maison",       "#0a1a0a", "#66aa44", "#337711"),
    "compostage":   ("Maison",       "#0a1a0a", "#66aa44", "#337711"),
    
    # Professionnel 
    "réunion":      ("Pro",          "#0a0a1a", "#5577cc", "#223388"),
    "travail":      ("Pro",          "#0a0a1a", "#5577cc", "#223388"),
    "networking":   ("Pro",          "#0a0a1a", "#5577cc", "#223388"),
    "formation":    ("Pro",          "#0a0a1a", "#5577cc", "#223388"),
    "brainstorming":("Pro",          "#0a0a1a", "#5577cc", "#223388"),
    "coworking":    ("Pro",          "#0a0a1a", "#5577cc", "#223388"),
}


# Noms affichés dans le sélecteur de langue
LANGUAGE_NAMES = {
    "fr": "Français",
    "en": "English",
    "es": "Español",
    "pt": "Português",
    "zh": "中文 (Mandarin)",
}


def get_translation(lang: str) -> dict:
    """
    Retourne le dictionnaire de traductions pour la langue donnée.
    Fallback sur le français si la langue n'est pas supportée.

    Parameters
    ----------
    lang : str
        Code langue ex: "fr", "en", "zh"

    Returns
    -------
    dict
        Dictionnaire de traductions.
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS["fr"])


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

