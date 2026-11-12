# 🌤️ WeatherProgramm

> A smart weather-based day planner : CS50 Final Project

#### Video Demo: (https://youtu.be/bPU5fps7p8o)



## 📖 About This Project

**WeatherProgramm** is the final project for [CS50's Introduction to Programming with Python](https://cs50.harvard.edu/python/), offered by Harvard University through edX.

The goal was to build a complete, real-world Python application that goes beyond simple scripts : combining APIs, object-oriented programming, a graphical interface, data persistence, and AI-powered suggestions into a single cohesive product.

### The idea

We all check the weather every morning. But knowing it's 14°C and cloudy doesn't tell you *what to do* with your day. **WeatherProgramm** bridges that gap: it fetches real-time weather data for any city and builds a complete, personalized day plan, activities, outfit, meals, a daily score, and an inspiring quote all tailored to your tastes, mood, and preferred style.



## ✨ Features

### 🌦️ Real-time weather
- Fetches current conditions through the **WeatherProgramm FastAPI backend**, which calls OpenWeatherMap
- Displays temperature, feels-like, humidity, wind speed, and condition icon
- Automatic city detection via HTTPS IP geolocation
- Weather-based day score out of 10

### 📅 Personalized day program
- Generates a full schedule (08:00 - 21:00) adapted to the weather at each time slot
- Activities filtered by personal tastes (sport, culture, nature, gastronomy, etc.)
- Meal suggestions tailored to preferred cuisine : independent of weather
- Outfit recommendations based on temperature, rain, and clothing style
- Inspiring quote of the day from ZenQuotes API with local fallback

### 🤖 AI enrichment via Groq
- Optional server-side integration with **Groq API** (openai/gpt-oss-120b)
- Enriches existing activities with suggested venue names and addresses
- The backend geocodes those suggestions and only returns coordinates matched to the requested city
- The Groq key stays on the backend, never in the desktop app
- Silent fallback to local data if Groq is unavailable

### 🗺️ Interactive map
- OpenStreetMap standard raster tiles displayed with tkintermapview
- Centered on the current city using GPS coordinates from OpenWeatherMap
- Markers for activities whose suggested venues were successfully geocoded
- Updates automatically when the city changes
- Requests visible map tiles directly from OpenStreetMap; no API key is required
- Displays OpenStreetMap attribution and caches tiles according to HTTP cache headers
- No offline-map or bulk tile download feature is provided
- Activity place searches use the backend geocoder, are cached, and are limited to at most one Nominatim request per second

### 🎨 Customization
- Create custom activity categories with a personalized color (color picker)
- Add custom activities to any category for specific weather conditions
- Add custom dishes to any cuisine type
- Add custom clothing items to any style
- Customizations are saved in user-owned JSON files, separate from bundled defaults

### 👤 User profile
- Name, bio/description, tastes (multi-select pills), mood, clothing style, cuisine
- Profile saved in the persistent user data directory and reloaded at every launch
- Day history tracking with date, city, score, and activities
- Language selection (applied on next launch)

### 🚀 Executable distribution
- Packaged with **PyInstaller** into a single executable
- Cross-platform builds via **GitHub Actions** for Linux, Windows, and macOS
- OpenWeatherMap and Groq keys are kept by the backend, not distributed with the desktop app
- A public release must be configured to use the deployed HTTPS backend

---

## 🏗️ Project Architecture

Weathers-Assistant/
│
├── project.py              : CS50 entry point (main + 3 testable functions)
├── test_project.py         : pytest test suite
├── models.py               : Data models (dataclasses)
├── requirements.txt
├── README.md
├── project.spec            : PyInstaller build configuration
│
├── .github/
│   └── workflows/
│       └── build.yml       : GitHub Actions: builds Linux + Windows + macOS
│
├── core/                   : Business logic (no UI, no network calls from UI)
│   ├── config.py           : Centralized path and .env management
│   ├── weather_service.py  : Backend API client + cache + geolocation
│   ├── osm_tile_service.py : OSM tile client + persistent HTTP cache
│   ├── activity_engine.py  : Activity, outfit & food suggestions
│   ├── day_planner.py      : Day program builder + scoring + AI enrichment
│   ├── ai_service.py       : Backend AI-enrichment API client
│   └── user_profile.py     : Profile load/save (JSON)
│
├── ui/                     : CustomTkinter interface
│   ├── config.py           : Colors, fonts, translations, categories
│   ├── main_window.py      : Main window + sidebar + navigation
│   ├── weather_frame.py    : Weather page
│   ├── program_frame.py    : Day program page
│   ├── map_frame.py        : Interactive map page
│   ├── profile_frame.py    : User profile page
│   └── custom_frame.py     : Customization page (activities, food, styles)
│
└── data/                   : Local data files
├── activities.json     : Activity database by weather condition & category
├── categories.json     : Badge categories with colors and keywords
├── food.json           : Meal suggestions by cuisine type
├── styles.json         : Outfit suggestions by style and temperature

In packaged applications, the user profile, weather cache, and customizations
are stored separately from these bundled defaults so they persist between
launches. When running from source, the project `data/` directory remains in use.
On Windows, the user data directory is `%APPDATA%/WeatherProgramm`; on macOS
it is `~/Library/Application Support/WeatherProgramm`; on Linux it is
`$XDG_DATA_HOME/WeatherProgramm` or `~/.local/share/WeatherProgramm`.

### Design principles applied
- **Single Responsibility** : each class has one job
- **Separation of concerns** : UI never calls APIs directly
- **Data models** : all data flows through typed `dataclasses`
- **Caching** : weather results cached for 30 minutes to reduce API calls
- **Centralized paths** : `core/config.py` handles all paths for dev and exe modes
- **Optional AI** : the backend's Groq enrichment never blocks the local program


## 📁 File descriptions

### `project.py`
Entry point of the application. Contains `main()` and the three CS50-required testable functions:
- `get_greeting(hour)` : returns a time-appropriate greeting based on the hour
- `is_first_launch()` : checks if the persistent user profile exists to detect first run
- `add_day_to_history(program, weather)` : saves a day to the user's history in the profile JSON

Also contains `show_welcome()` which displays the onboarding screen on first launch.

### `test_project.py`
pytest test suite covering all three custom functions with edge cases and temporary file fixtures via `monkeypatch` and `tmp_path`.

### `models.py`
Dataclass definitions for `WeatherData`, `TimeSlot`, `DayProgram`, and `ProfileData`. These are the typed data structures that flow through the entire application.

### `core/config.py`
Centralized configuration handling. Detects whether the app runs in development or PyInstaller frozen mode, finds bundled resources and the persistent user data directory, and loads environment variables once at startup.

### `core/weather_service.py`
Calls the backend for current weather and today's forecast, performs HTTPS IP geolocation, and maintains a 30-minute JSON cache in the user data directory.

### `core/activity_engine.py`
Generates suggestions from local JSON catalogs. Produces outfit recommendations by style and temperature category, meal suggestions by cuisine, and activity suggestions filtered by weather condition and user tastes. Supports custom items added by the user via `custom_frame.py`.

### `core/day_planner.py`
Builds the complete `DayProgram`. Always generates locally first, then optionally sends activities to the backend for venue enrichment via `ai_service.py`. If AI is unavailable the local program is returned unchanged.

### `ui/map_frame.py`
Displays visible OpenStreetMap raster tiles directly from `tile.openstreetmap.org`, with activity markers and visible attribution. Tile requests use an application-identifying `User-Agent` and a persistent HTTP cache. The map requires an internet connection and does not support offline tile downloads.

### `core/osm_tile_service.py`
Fetches visible OSM tiles directly from the official raster tile endpoint. Uses a persistent SQLite HTTP cache that honors server cache directives and conditional validators.

### `core/ai_service.py`
Optional backend API client for activity enrichment. Sends locally-generated activities to the backend and returns `None` if enrichment is unavailable.

### `core/user_profile.py`
Loads and saves `ProfileData` in the persistent user data directory. Paths are provided by `core/config.py` for development and PyInstaller builds.

### `ui/config.py`
Shared UI constants: color palette, font helper, icon loader, category badge system loaded from user customizations or bundled defaults, and helper functions for dynamic category management.

### `ui/main_window.py`
Main application window with sidebar navigation, city search bar, and frame management. Passes the current city to all frames and triggers cross-frame refresh when the city changes or the profile is saved.

### `ui/weather_frame.py`
Displays current weather conditions, day score, outfit suggestion with style badges, daily quote, and meal suggestions for four time slots.

### `ui/program_frame.py`
Displays the full day schedule as chronological cards. Each card shows the time, local temperature with weather icon, activity description, optional venue location, and a color-coded category badge.

### `ui/map_frame.py`
Interactive OpenStreetMap raster map centered on the current city using GPS coordinates from the backend. Displays markers for activities whose suggested venues were successfully geocoded by the backend. Shares the same `DayProgram` as `program_frame.py` to avoid regenerating activities. Visible tiles are requested directly from OpenStreetMap; its tile server receives the user's IP address and requested map area.

### `ui/profile_frame.py`
Full profile configuration: name, bio, taste pills (dynamically loaded from `categories.json`), mood selector, style and cuisine dropdowns, language selector, and history management.

### `ui/custom_frame.py`
Personalization interface allowing users to create custom badge categories with a color picker, add custom activities to any category for specific weather conditions, add custom dishes to any cuisine, and add custom clothing items to any style.


## 🧪 CS50 Requirements

| Requirement | Implementation |
|---|---|
| Main file named `project.py` | ✅ |
| `main()` function | ✅ |
| At least 3 custom functions | ✅ `get_greeting()`, `is_first_launch()`, `add_day_to_history()` |
| Test file named `test_project.py` | ✅ |
| Tests using `pytest` | ✅ 3 test functions covering all 3 custom functions |

```bash
pytest test_project.py -v
```

---

## ⚙️ Installation

### Prerequisites
- Python **3.12** or higher
- A running WeatherProgramm FastAPI backend for weather and AI enrichment
- OpenStreetMap tiles require an internet connection but no API key

### 1. Clone the repository

```bash
git clone https://github.com/kingprog-hcr/Weathers-Assistant.git
cd Weathers-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the desktop backend URL

For local development, the default backend URL is `http://127.0.0.1:8001`. To override it, create a root `.env` file:

```env
WEATHER_API_BASE_URL=http://127.0.0.1:8001
```

Set `OPENWEATHER_API_KEY` and, optionally, `GROQ_API_KEY` in `backend/.env`, not in the desktop `.env`. Never ship these provider keys in a desktop build. For local backend setup, install `backend/requirements.txt` and create `backend/.env` with those server-side variables. Public releases must use the deployed backend's HTTPS URL; do not distribute a build that still points to localhost.

The backend uses the public [Nominatim geocoding service](https://operations.osmfoundation.org/policies/nominatim/) for activity venues by default. It receives place names/addresses and the backend's IP address, identifies WeatherProgramm, caches results in `backend/.cache/nominatim.sqlite3` (or `NOMINATIM_CACHE_PATH`), and spaces uncached requests by at least one second. For deployment, point the cache path at persistent storage. This public service is intended for moderate, user-triggered use; do not send private information, run multiple backend instances against it without a shared rate limiter/cache, or use it for bulk geocoding. Set `NOMINATIM_BASE_URL` to switch to another compatible service without changing the desktop application.

### 5. Start the backend and desktop

```bash
# Terminal 1, from backend/
uvicorn app.main:app --reload --port 8001

# Terminal 2, from the project root
python project.py
```


## 📦 Download the executable

The project has a cross-platform build workflow, but a public release must
only be produced after the backend is deployed and the build is configured
with its HTTPS URL. The current development default is
`http://127.0.0.1:8001`; it requires a backend running on the same computer.
Desktop users must not be asked to provide OpenWeatherMap or Groq keys.

❓ COMMON ISSUES

• "Weather service unavailable"
→ Check your internet connection and confirm the WeatherProgramm backend is running.

• The map is blank
→ Check your internet connection. Visible map tiles are requested directly from OpenStreetMap.

The desktop `.env` file is optional and is only used to override
`WEATHER_API_BASE_URL` during development. Do not put provider API keys in it.


No Python installation required.


## 🖥️ How to Use

**First launch** : a welcome screen detects your city automatically and invites you to configure your profile.

**Weather page** : current conditions, day score, outfit suggestion, daily quote, and meal suggestions.

**Program page** : full day schedule as cards with time, weather, activity, optional venue, and category badge. Click Regénérer to generate a new program.

**Map page** : interactive map centered on your city. Activities enriched by the AI appear as clickable markers.

**Profile page** : configure your name, bio, tastes, mood, style, cuisine, and language.

**Customize page** : add your own categories (with custom colors), activities, dishes, and clothing items.


## 🔑 APIs Used

| API | Purpose | Cost |
|---|---|---|
| [WeatherProgramm backend](./backend/) | Weather and AI requests; provider keys stay server-side | Depends on hosting/provider plans |
| [OpenWeatherMap](https://openweathermap.org/api) | Weather data used by the backend | Provider plan |
| [ipinfo](https://ipinfo.io/) | Automatic city detection via HTTPS | Provider terms |
| [ZenQuotes](https://zenquotes.io) | Daily inspirational quotes | Free |
| [Groq](https://console.groq.com) | Server-side AI venue enrichment (optional) | Provider plan |
| [OpenStreetMap tile server policy](https://operations.osmfoundation.org/policies/tiles/) | Interactive raster map tiles | Community service; policy and availability limits apply |



## 👨‍💻 Author

**Chrys-Renabell HASSAM**
CS50P Final Project : 2026



## 📄 License

This project was built for educational purposes as part of Harvard's CS50P course.
Feel free to explore, fork, and build upon it.



*This is CS50.*
