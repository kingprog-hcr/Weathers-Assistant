📥 TÉLÉCHARGEMENT
https://github.com/kingprog-hcr/Weathers-Assistant/releases/latest

Choisis selon ton système :
- Windows : WeatherProgramm-Setup.exe (recommandé, installe tout automatiquement)
- Mac     : WeatherProgramm-macOS
- Linux   : WeatherProgramm-Linux


⚙️ INSTALLATION

WINDOWS :
1. Double-clique sur WeatherProgramm-Setup.exe
   L'application est installée dans ton profil utilisateur, sans droits
   administrateur. Aucune clé fournisseur ne doit être ajoutée à l'application.
2. Si Windows affiche "Windows a protégé votre ordinateur" (SmartScreen) :
   → clique sur "Informations complémentaires" puis "Exécuter quand même"
   C'est normal, l'app n'est pas signée numériquement (ça coûte de l'argent)
3. Si ton antivirus (Avast, Norton, etc.) bloque ou met en quarantaine :
   → c'est un faux positif, autorise le fichier ou ajoute une exception

MAC :
1. Télécharge WeatherProgramm-macOS
2. Clic droit sur le fichier → "Ouvrir" (PAS double-clic, sinon macOS bloque)
3. Une popup "développeur non identifié" apparaît → clique "Ouvrir" pour confirmer

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

Un exécutable destiné au public doit être construit avec l'URL HTTPS du
backend déployé. Le code de développement utilise par défaut
http://127.0.0.1:8001 et nécessite donc un backend local.


❓ PROBLÈMES COURANTS

- "Service météo indisponible" → vérifie ta connexion et la disponibilité
  du backend WeatherProgramm

- La carte ne s'affiche pas → vérifie ta connexion Internet; les tuiles
  proviennent directement du service OpenStreetMap
