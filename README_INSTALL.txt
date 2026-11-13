📥 TÉLÉCHARGEMENT
https://github.com/kingprog-hcr/Weathers-Assistant/releases/latest

Choisis selon ton système :
- Windows : WeatherProgramm-Setup.exe (recommandé, installe tout automatiquement)
- Mac     : WeatherProgramm-macOS
- Linux   : WeatherProgramm-Linux

Les téléchargements portables sont accompagnés d'un fichier de licence MIT.
L'installeur Windows place aussi LICENSE.txt dans le dossier de l'application.


⚙️ INSTALLATION

WINDOWS :
1. Double-clique sur WeatherProgramm-Setup.exe
   L'application est installée dans ton profil utilisateur, sans droits
   administrateur. Aucune clé fournisseur ne doit être ajoutée à l'application.
2. Si Windows affiche "Windows a protégé votre ordinateur" (SmartScreen) :
   → vérifie que le fichier vient bien de la page officielle des releases GitHub.
   Ne contourne l'avertissement que si tu fais confiance à la source et au fichier.
3. Si ton antivirus bloque le fichier :
   → ne désactive pas l'antivirus et n'ajoute pas d'exception sans avoir vérifié
   la provenance du fichier.

MAC :
1. Télécharge WeatherProgramm-macOS
   depuis la page officielle des releases GitHub.
2. macOS peut signaler que le développeur est non identifié. Ne poursuis que si
   tu fais confiance à la provenance du fichier.

LINUX :
1. Télécharge WeatherProgramm-Linux
2. Ouvre un terminal dans le dossier de téléchargement
3. chmod +x WeatherProgramm-Linux
4. ./WeatherProgramm-Linux


ℹ️ À PROPOS DES SERVICES EN LIGNE

La météo et l'enrichissement IA passent par le backend WeatherProgramm.
Les clés OpenWeatherMap et Groq sont conservées côté serveur; ne crée pas
un fichier .env avec ces clés à côté de l'exécutable.

La carte télécharge directement les tuiles visibles depuis OpenStreetMap.
Elle ne demande pas de clé, nécessite Internet et n'offre pas de mode hors
ligne.

L'application utilise par défaut le backend HTTPS déployé, sans configuration
à faire côté utilisateur :
https://weathers-assistant.onrender.com

Pour le développement local uniquement, un fichier .env à la racine peut
remplacer cette URL par http://127.0.0.1:8001. Les clés OpenWeatherMap et Groq
doivent rester dans la configuration du backend, jamais dans l'application.
Sur Render Free, le backend peut s'endormir après une période sans trafic; la
première requête peut être lente et le cache local du géocodeur est perdu lors
des redémarrages.


❓ PROBLÈMES COURANTS

- "Service météo indisponible" → vérifie ta connexion et la disponibilité
  du backend WeatherProgramm

- La carte ne s'affiche pas → vérifie ta connexion Internet; les tuiles
  proviennent directement du service OpenStreetMap
