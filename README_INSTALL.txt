📥 TÉLÉCHARGEMENT
https://github.com/kingprog-hcr/Weathers-Assistant/releases/latest

Choisis selon ton système :
- Windows : WeatherProgramm-Setup.exe (recommandé, installe tout automatiquement)
- Mac     : WeatherProgramm-macOS
- Linux   : WeatherProgramm-Linux


⚙️ INSTALLATION

WINDOWS :
1. Double-clique sur WeatherProgramm-Setup.exe
2. Si Windows affiche "Windows a protégé votre ordinateur" (SmartScreen) :
   → clique sur "Informations complémentaires" puis "Exécuter quand même"
   C'est normal, l'app n'est pas signée numériquement (ça coûte de l'argent)
3. Si ton antivirus (Avast, Norton, etc.) bloque ou met en quarantaine :
   → c'est un faux positif, autorise le fichier ou ajoute une exception
   → si l'antivirus supprime ton fichier .env après création, désactive
     temporairement la protection en temps réel le temps de créer le fichier

MAC :
1. Télécharge WeatherProgramm-macOS
2. Clic droit sur le fichier → "Ouvrir" (PAS double-clic, sinon macOS bloque)
3. Une popup "développeur non identifié" apparaît → clique "Ouvrir" pour confirmer

LINUX :
1. Télécharge WeatherProgramm-Linux
2. Ouvre un terminal dans le dossier de téléchargement
3. chmod +x WeatherProgramm-Linux
4. ./WeatherProgramm-Linux


🔑 ÉTAPE OBLIGATOIRE : fichier .env

Sans ce fichier, l'app ne pourra pas récupérer la météo !

1. Va sur https://openweathermap.org/api
2. Crée un compte gratuit (clique "Sign up")
3. Une fois connecté, va dans "My API keys" et copie ta clé
   ⚠️ La clé prend ~10-15 minutes à s'activer après création, sois patient

4. Dans le dossier où est installé WeatherProgramm, crée un fichier
   nommé exactement ".env" (avec le point, sans extension) contenant :

   API_KEY=ta_cle_openweathermap_ici
   GROQ_API_KEY=
   STADIA_MAPS_API_KEY=

   Les lignes GROQ_API_KEY et STADIA_MAPS_API_KEY peuvent rester vides.
   Sans STADIA_MAPS_API_KEY, l'onglet Carte reste désactivé.

   Pour activer la carte, crée un compte Stadia Maps et génère une clé :
   https://client.stadiamaps.com/signup/
   Ajoute ensuite ta clé après STADIA_MAPS_API_KEY=.
   Le compte gratuit a une limite mensuelle. Une clé utilisée par une
   application de bureau peut être récupérée depuis les requêtes réseau :
   ne partage pas ta clé personnelle dans une version publique.

   ⚠️ IMPORTANT : crée ce fichier avec le Bloc-notes ou VS Code,
   PAS avec PowerShell (problèmes d'encodage). Si tu utilises Notepad,
   choisis "UTF-8" dans le menu Encodage en bas de la fenêtre
   "Enregistrer sous" (pas "Unicode" ni "UTF-16").

5. Lance WeatherProgramm !


❓ PROBLÈMES COURANTS

- "Pas de connexion internet" → vérifie ta connexion, l'app a besoin
  d'internet pour la météo

- L'app se ferme immédiatement au lancement → vérifie que le fichier
  .env existe bien dans le même dossier que l'exécutable, avec le bon
  nom (commence par un point)

- Erreur bizarre liée à "utf-8" ou "codec" → le fichier .env a été créé
  avec le mauvais encodage, recrée-le avec Notepad en UTF-8
