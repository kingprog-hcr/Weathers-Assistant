import tkinter.font as tkfont
import customtkinter as ctk
import io
import urllib.request
from PIL import Image
import json
from pathlib import Path


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


#  Catalogue des badges 
# Associe des mots clés d'activité à un badge coloré.
# Format : mot_clé : (label, bg, fg, border_color)
# Les couleurs sont choisies pour être lisibles sur fond sombre.
# Aligné avec les catégories de data/activities.json.


_BASE_DIR         = Path(__file__).parent.parent
_CATEGORIES_FILE  = _BASE_DIR / "data" / "categories.json"


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

    Appelée par CustomFrame quand l'utilisateur ajoute
    une catégorie ou un keyword personnalisé.

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
    Chaque catégorie contient une liste de keywords, chaque keyword
    est mappé vers le même tuple badge.

    Ex: {"sport": ("Sport", "#2a0a2a", "#cc55cc", "#991a99")}
    """
    raw        = load_slot_categories()
    categories = {}
    for key, data in raw.items():
        badge = (data["label"], data["bg"], data["fg"], data["border"])
        for keyword in data.get("keywords", []):
            categories[keyword.lower()] = badge
    return categories


# Chargé une fois au démarrage utilisé dans program_frame et custom_frame
SLOT_CATEGORIES = build_slot_categories()