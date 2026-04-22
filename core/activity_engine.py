# core/activity_engine.py

"""
Activity engine responsible for generating contextual suggestions
(activities, outfits and food) based on weather conditions and user preferences.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import random
from models import WeatherData


class ActivityEngine:

    BASE_DIR = Path(__file__).resolve().parent.parent
    ACTIVITIES_FILE = BASE_DIR / "data" / "activities.json"

    def __init__(self):
        """Initialise le moteur et charge les activités."""
        self.activities = self._load_activities()

    def _load_activities(self) -> dict:
        """Charge le fichier activities.json."""
        try:
            with open(self.ACTIVITIES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def suggest_activities(
        self,
        weather: WeatherData,
        tastes: list[str] | None = None,
        max_results: int = 6
    ) -> list[str]:
        """
        Génère des suggestions d'activités en fonction de la météo.

        Parameters
    
        weather : WeatherData
            Données météorologiques actuelles.
        tastes : list[str] | None
            Catégories d'activités préférées (sport, culture, etc.).
        max_results : int
            Nombre maximum d'activités retournées.

        Returns

        list[str]
            Liste d'activités suggérées.
        """

        condition = weather.condition.lower()

        if condition not in self.activities.keys():
            return []

        condition_activities = self.activities[condition]

        # Si aucun goût spécifié , prendre toutes les catégories
        if not tastes:
            tastes = list(condition_activities.keys())

        suggestions = []

        for taste in tastes:
            if taste in condition_activities:
                suggestions.extend(condition_activities[taste])

        if not suggestions:
            return []

        return random.sample(
            suggestions,
            k=min(max_results, len(suggestions))
        )

    def suggest_outfit(self, weather: WeatherData, style: str = "random") -> list[str]:
        """
        Retourne une tenue complète adaptée à la météo et au style vestimentaire.

        Parameters
        weather : WeatherData
            Données météo actuelles.
        style : str
            Style vestimentaire : "streetwear" | "oldmoney" | "casual" |
            "boheme" | "sportswear" | "minimaliste" | "preppy" | "random"
        """

        temp = weather.temp
        is_rainy = weather.is_rainy()
        condition = weather.condition.lower()

        # Catalogues par style 

        STYLES = {
            "streetwear": {
                "froid_extreme":  ["doudoune oversize", "hoodie graphique", "cargo pants", "sneakers montantes", "bonnet streetwear"],
                "froid":          ["bomber jacket", "hoodie épais", "jogging cargo", "Air Force 1 ou Jordan"],
                "frais":          ["jacket en nylon", "sweat à capuche", "baggy jeans", "sneakers chunky"],
                "doux":           ["t-shirt graphique oversize", "cargo pants", "sneakers basses"],
                "chaud":          ["jersey mesh", "short cargo", "claquettes avec chaussettes", "casquette snapback"],
                "pluie":          ["trench technique imperméable", "hoodie waterproof", "sneakers Gore-Tex"],
                "neige":          ["doudoune puffer oversize", "jogger imperméable", "bottes de neige chunky"],
            },
            "oldmoney": {
                "froid_extreme":  ["manteau en cachemire", "pull col roulé en laine", "pantalon en flanelle", "chelsea boots"],
                "froid":          ["trench coat beige", "pull en merinos", "pantalon droit", "loafers en cuir"],
                "frais":          ["blazer en tweed", "chemise oxford", "chino beige", "mocassins"],
                "doux":           ["chemise en lin boutonnée", "pantalon chino", "loafers sans chaussettes"],
                "chaud":          ["chemise en lin blanc", "short chino", "mocassins en cuir clair", "montre sobre"],
                "pluie":          ["trench coat classique", "pull fin", "pantalon imperméable", "bottes en caoutchouc élégantes"],
                "neige":          ["manteau en laine longue", "écharpe en cachemire", "bottes en cuir doublées"],
            },
            "casual": {
                "froid_extreme":  ["doudoune", "pull chaud", "jean épais", "bottes chaudes"],
                "froid":          ["veste chaude", "sweat", "jean", "baskets montantes"],
                "frais":          ["veste légère", "t-shirt manches longues", "jean slim", "sneakers"],
                "doux":           ["t-shirt", "jean ou chino", "baskets"],
                "chaud":          ["t-shirt léger", "short ou jupe", "sandales"],
                "pluie":          ["imperméable", "pull", "jean", "chaussures imperméables"],
                "neige":          ["manteau chaud", "pull", "jean doublé", "bottes"],
            },
            "boheme": {
                "froid_extreme":  ["manteau en laine bouclée", "pull en mohair", "jupe longue en velours", "bottines à franges"],
                "froid":          ["kimono en velours", "robe longue superposée", "gilet en laine", "bottines"],
                "frais":          ["cardigan oversized", "robe midi fleurie", "collants", "bottines"],
                "doux":           ["robe fluide imprimée", "gilet en crochet", "sandales plates"],
                "chaud":          ["robe légère tie-dye", "top crochet", "sandales en cuir tressé", "chapeau de paille"],
                "pluie":          ["poncho en laine", "robe longue", "bottines imperméables"],
                "neige":          ["cape en laine", "robe en velours", "collants épais", "bottes fourrées"],
            },
            "sportswear": {
                "froid_extreme":  ["veste running thermique", "collant thermique", "t-shirt technique", "chaussures trail"],
                "froid":          ["coupe-vent", "legging de sport", "t-shirt technique", "running shoes"],
                "frais":          ["veste légère sport", "jogging slim", "t-shirt dry-fit"],
                "doux":           ["t-shirt technique", "short de sport", "sneakers running"],
                "chaud":          ["débardeur sport", "short léger", "chaussures respirantes", "casquette sport"],
                "pluie":          ["veste imperméable sport", "legging imperméable", "chaussures trail imperméables"],
                "neige":          ["veste ski", "pantalon de ski ou snow", "chaussures imperméables chaudes"],
            },
            "minimaliste": {
                "froid_extreme":  ["manteau long noir ou beige", "col roulé blanc", "pantalon droit", "chelsea boots noires"],
                "froid":          ["manteau structuré", "pull uni", "pantalon droit", "boots simples"],
                "frais":          ["blazer épuré", "t-shirt blanc", "pantalon tailleur", "sneakers blanches"],
                "doux":           ["chemise oversize unie", "pantalon flottant", "mules simples"],
                "chaud":          ["robe droite unie", "sandales minimalistes", "sac structuré"],
                "pluie":          ["imperméable épuré", "tenue monochrome", "boots simples"],
                "neige":          ["manteau long uni", "tenue monochrome", "bottes simples"],
            },
            "preppy": {
                "froid_extreme":  ["duffel coat", "pull jacquard", "pantalon en velours côtelé", "loafers"],
                "froid":          ["blazer à carreaux", "chemise rayée", "chino", "mocassins"],
                "frais":          ["gilet en maille", "chemise à col boutonné", "chino beige", "boat shoes"],
                "doux":           ["polo brodé", "chino pastel", "loafers colorés"],
                "chaud":          ["polo en coton", "short madras", "topsiders", "lunettes de soleil"],
                "pluie":          ["ciré jaune ou marine", "pull fin", "pantalon imperméable", "loafers caoutchouc"],
                "neige":          ["duffel coat", "pull en laine d'agneau", "pantalon chaud", "bottes"],
            },
        }

        # Déterminer la catégorie de température 

        if condition == "snow":
            temp_key = "neige"
        elif is_rainy:
            temp_key = "pluie"
        elif temp < 0:
            temp_key = "froid_extreme"
        elif temp < 8:
            temp_key = "froid"
        elif temp < 15:
            temp_key = "frais"
        elif temp < 23:
            temp_key = "doux"
        else:
            temp_key = "chaud"

        # Choisir le style 

        if style == "random" or style not in STYLES:
            style = random.choice(list(STYLES.keys()))

        outfit = list(STYLES[style][temp_key])

        # Accessoires universels

        if condition == "clear" and temp > 22:
            outfit.append("lunettes de soleil", "crème solaire")
        if temp < 5 and "bonnet" not in str(outfit):
            outfit.append("bonnet")

        # Note du style choisi
        outfit.append(f"✨ Style : {style.capitalize()}")

        return outfit


    def suggest_food(self, weather: WeatherData, cuisine: str = "random") -> list[str]:
        """
        Retourne des suggestions de plats et boissons selon la météo
        et le type de cuisine préféré.

        Parameters
        weather : WeatherData
            Données météo actuelles.
        cuisine : str
            Type de cuisine : "asiatique" | "méditerranéenne" | "africaine" |
            "américaine" | "française" | "moyen-orientale" | "latino" |
            "fastfood" | "random"
        """

        temp = weather.temp
        condition = weather.condition.lower()
        is_rainy = weather.is_rainy()

        # Catalogues par cuisine et météo 

        CUISINES = {
            "asiatique": {
                "chaud":      ["bubble tea glacé", "sushi bowl frais", "salade de papaye verte", "ramune citronnée", "rouleaux de printemps frais"],
                "froid":      ["ramen tonkotsu fumant", "gyoza poêlés", "thé matcha chaud", "miso soup", "riz sauté au gingembre"],
                "pluie":      ["ramen épicé", "udon en bouillon", "dumplings vapeur", "thé chai japonais"],
                "neige":      ["hot pot japonais", "shabu-shabu", "thé sencha chaud", "nikujaga (ragoût japonais)"],
                "nuageux":    ["pad thaï", "bol de riz au curry", "dim sum", "café vietnamien"],
            },
            "méditerranéenne": {
                "chaud":      ["gaspacho andalou", "salade grecque", "houmous et pita", "eau citronnée à la menthe", "carpaccio de tomates"],
                "froid":      ["pasta e fagioli", "soupe de lentilles à l'huile d'olive", "pain pita grillé", "café turc"],
                "pluie":      ["pasta al forno", "soupe minestrone", "pain focaccia", "vin chaud aux épices"],
                "neige":      ["osso buco", "polenta crémeuse", "soupe de poisson", "vin rouge corsé"],
                "nuageux":    ["tapas variées", "risotto", "salade niçoise", "pastis"],
            },
            "africaine": {
                "chaud":      ["bissap glacé (jus d'hibiscus)", "salade de mangue épicée", "thiéboudienne légère", "gingembre frais pressé"],
                "froid":      ["mafé (ragoût d'arachide)", "soupe de yassa", "thé à la menthe sucré", "riz au gras"],
                "pluie":      ["tagine de poulet aux olives", "soupe harira", "pain msemen", "café touba"],
                "neige":      ["mafé épicé", "couscous aux légumes chauds", "thé à la menthe bien chaud"],
                "nuageux":    ["injera et wot éthiopien", "brochettes suya", "plantain frit", "jus de gingembre"],
            },
            "américaine": {
                "chaud":      ["ice tea maison", "burger sur le grill", "salade Caesar", "limonade fraîche", "sundae glacé"],
                "froid":      ["chili con carne", "clam chowder", "mac and cheese gratiné", "café filtre américain"],
                "pluie":      ["pot roast mijoté", "cornbread", "soupe de tomates", "hot chocolate américain"],
                "neige":      ["chili épais", "pancakes au sirop d'érable", "café chaud", "brownies chauds"],
                "nuageux":    ["club sandwich", "soupe de palourdes", "Buffalo wings", "milkshake"],
            },
            "française": {
                "chaud":      ["salade lyonnaise", "vichyssoise froide", "rosé bien frais", "tarte aux fraises"],
                "froid":      ["soupe à l'oignon gratinée", "boeuf bourguignon", "vin rouge de Bourgogne", "tarte tatin chaude"],
                "pluie":      ["croque-monsieur", "quiche lorraine", "café crème", "pain au chocolat"],
                "neige":      ["fondue savoyarde", "tartiflette", "vin chaud", "bugnes ou beignets chauds"],
                "nuageux":    ["crêpes au beurre", "steak-frites", "kir breton", "éclair au chocolat"],
            },
            "moyen-orientale": {
                "chaud":      ["ayran (yaourt salé)", "fattoush frais", "falafel léger", "eau de rose citronnée"],
                "froid":      ["chorba (soupe épicée)", "shawarma chaud", "thé à la cannelle", "msabbaha (houmous chaud)"],
                "pluie":      ["lentilles à la libanaise", "pain pita chaud", "soupe de pois chiches", "thé cardamome"],
                "neige":      ["kibbeh au four", "riz aux vermicelles", "soupe harira", "café à la cardamome"],
                "nuageux":    ["mezze complet", "manakish zaatar", "labneh et légumes", "jus de grenade"],
            },
            "latino": {
                "chaud":      ["agua fresca au citron vert", "ceviche péruvien", "tacos al pastor", "horchata glacée"],
                "froid":      ["pozole (soupe mexicaine)", "empanadas chaudes", "café de olla", "tamales"],
                "pluie":      ["sopa de lima", "arepas garnies", "chocolate caliente mexicain", "bandeja paisa"],
                "neige":      ["chupe de camarones (soupe péruvienne)", "tamales chauds", "champurrado (chocolat mexicain épais)"],
                "nuageux":    ["quesadillas", "pico de gallo et chips", "horchata", "churros"],
            },
            "fastfood": {
                "chaud":      ["burger végétarien frais", "wrap poulet grillé", "milkshake vanille", "salade bowl", "frozen lemonade"],
                "froid":      ["burger double bacon", "nuggets sauce barbecue", "café chaud", "frites bien chaudes"],
                "pluie":      ["burger fromage fondu", "hot-dog grillé", "soupe de tomates maison", "chocolat chaud"],
                "neige":      ["burger double viande", "frites extra croustillantes", "sauce spéciale maison", "café chaud"],
                "nuageux":    ["burger classique", "onion rings", "milkshake chocolat", "soda pression"],
            },
        }

        # Déterminer la catégorie météo 

        if condition == "snow":
            weather_key = "neige"
        elif is_rainy or condition == "thunderstorm":
            weather_key = "pluie"
        elif temp > 23:
            weather_key = "chaud"
        elif temp < 10:
            weather_key = "froid"
        else:
            weather_key = "nuageux"

        # Choisir la cuisine 

        if cuisine == "random" or cuisine not in CUISINES:
            cuisine = random.choice(list(CUISINES.keys()))

        suggestions = list(CUISINES[cuisine][weather_key])

        # Note de la cuisine choisie 
        suggestions.append(f"🍽️ Cuisine : {cuisine.capitalize()}")

        return suggestions
