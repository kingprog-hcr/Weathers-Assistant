# 🌤️ WeatherProgramm

> A smart weather-based day planner : CS50 Final Project

#### Video Demo: <URL HERE>



## 📖 About This Project

**WeatherProgramm** is the final project for [CS50's Introduction to Programming with Python](https://cs50.harvard.edu/python/), offered by Harvard University through edX.

The goal was to build a complete, real-world Python application that goes beyond simple scripts : combining APIs, object-oriented programming, a graphical interface, data persistence, and AI-powered suggestions into a single cohesive product.

### The idea

We all check the weather every morning. But knowing it's 14°C and cloudy doesn't tell you *what to do* with your day. **WeatherProgramm** bridges that gap: it fetches real-time weather data for any city and builds a complete, personalized day plan, activities, outfit, meals, a daily score, and an inspiring quote all tailored to your tastes, mood, and preferred style.



## ✨ Features

### 🌦️ Real-time weather
- Fetches current conditions from **OpenWeatherMap API**
- Displays temperature, feels-like, humidity, wind speed, and condition icon
- Automatic city detection via IP geolocation with OpenWeatherMap validation
- Weather-based day score out of 10

### 📅 Personalized day program
- Generates a full schedule (08:00 - 21:00) adapted to the weather at each time slot
- Activities filtered by personal tastes (sport, culture, nature, gastronomy, etc.)
- Meal suggestions tailored to preferred cuisine : independent of weather
- Outfit recommendations based on temperature, rain, and clothing style
- Inspiring quote of the day from ZenQuotes API with local fallback

### 🤖 AI enrichment via Groq
- Optional integration with **Groq API** (llama-3.3-70b-versatile)
- Enriches existing activities with real venue names and GPS coordinates
- Fully optional the app works completely offline without a Groq key
- Silent fallback to local data if Groq is unavailable

### 🗺️ Interactive map
- OpenStreetMap-based interactive map via tkintermapview
- Centered on the current city using GPS coordinates from OpenWeatherMap
- Markers for each activity enriched with real GPS coordinates by the AI
- Updates automatically when the city changes

### 🎨 Customization
- Create custom activity categories with a personalized color (color picker)
- Add custom activities to any category for specific weather conditions
- Add custom dishes to any cuisine type
- Add custom clothing items to any style
- All customizations saved in local JSON files

### 👤 User profile
- Name, bio/description, tastes (multi-select pills), mood, clothing style, cuisine
- Profile saved locally in `data/profile.json` and reloaded at every launch
- Day history tracking with date, city, score, and activities
- Language selection (applied on next launch)

### 🚀 Executable distribution
- Packaged with **PyInstaller** into a single executable
- Cross-platform builds via **GitHub Actions** for Linux, Windows, and macOS
- Users only need to provide their own `.env` file with API keys

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
│   ├── weather_service.py  : OpenWeatherMap API + cache + geolocation
│   ├── activity_engine.py  : Activity, outfit & food suggestions
│   ├── day_planner.py      : Day program builder + scoring + AI enrichment
│   ├── ai_service.py       : Groq API integration (optional)
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
├── profile.json        : Saved user profile (auto-generated)
└── cache_meteo.json    : Weather cache 30 min TTL (auto-generated)

### Design principles applied
- **Single Responsibility** : each class has one job
- **Separation of concerns** : UI never calls APIs directly
- **Data models** : all data flows through typed `dataclasses`
- **Caching** : weather results cached for 30 minutes to reduce API calls
- **Centralized paths** : `core/config.py` handles all paths for dev and exe modes
- **Optional AI** : Groq enriches but never blocks; local fallback always available


## 📁 File descriptions

### `project.py`
Entry point of the application. Contains `main()` and the three CS50-required testable functions:
- `get_greeting(hour)` : returns a time-appropriate greeting based on the hour
- `is_first_launch()` : checks if `data/profile.json` exists to detect first run
- `add_day_to_history(program, weather)` : saves a day to the user's history in the profile JSON

Also contains `show_welcome()` which displays the onboarding screen on first launch.

### `test_project.py`
pytest test suite covering all three custom functions with edge cases and temporary file fixtures via `monkeypatch` and `tmp_path`.

### `models.py`
Dataclass definitions for `WeatherData`, `TimeSlot`, `DayProgram`, and `ProfileData`. These are the typed data structures that flow through the entire application.

### `core/config.py`
Centralized configuration handling. Detects whether the app runs in development or PyInstaller frozen mode, finds the correct `.env` and `data/` paths accordingly, and loads environment variables once at startup.

### `core/weather_service.py`
All OpenWeatherMap interactions: current weather, 5-day forecast, hourly slots, automatic city detection via IP geolocation (with OpenWeatherMap validation to reject unknown small towns), and a 30-minute JSON cache system.

### `core/activity_engine.py`
Generates suggestions from local JSON catalogs. Produces outfit recommendations by style and temperature category, meal suggestions by cuisine, and activity suggestions filtered by weather condition and user tastes. Supports custom items added by the user via `custom_frame.py`.

### `core/day_planner.py`
Builds the complete `DayProgram`. Always generates locally first (fast, offline), then optionally enriches activities with real GPS-located venues via `ai_service.py`. If AI is unavailable the local program is returned unchanged.

### `core/ai_service.py`
Optional Groq API integration. Sends the list of locally-generated activities to the AI and asks only for real venue names and GPS coordinates — never generates new activities. Returns `None` silently if unavailable.

### `core/user_profile.py`
Loads and saves `ProfileData` from/to `data/profile.json`. All paths use `core/config.py` for compatibility with the PyInstaller executable.

### `ui/config.py`
Shared UI constants: color palette, font helper, icon loader, category badge system loaded from `data/categories.json`, and helper functions for dynamic category management.

### `ui/main_window.py`
Main application window with sidebar navigation, city search bar, and frame management. Passes the current city to all frames and triggers cross-frame refresh when the city changes or the profile is saved.

### `ui/weather_frame.py`
Displays current weather conditions, day score, outfit suggestion with style badges, daily quote, and meal suggestions for four time slots.

### `ui/program_frame.py`
Displays the full day schedule as chronological cards. Each card shows the time, local temperature with weather icon, activity description, optional venue location, and a color-coded category badge.

### `ui/map_frame.py`
Interactive OpenStreetMap map centered on the current city using GPS coordinates from OpenWeatherMap. Displays markers for activities enriched with real coordinates by the AI. Shares the same `DayProgram` as `program_frame.py` to avoid regenerating activities.

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
- A free **OpenWeatherMap API key** : [openweathermap.org/api](https://openweathermap.org/api)
- Optional: a free **Groq API key** : [console.groq.com](https://console.groq.com) (for AI venue enrichment)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Weathers-Assistant.git
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

### 4. Configure your API keys

Create a `.env` file at the root of the project:

```env
API_KEY=your_openweathermap_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

The `GROQ_API_KEY` is optional. Without it the app works fully — AI venue enrichment is simply disabled.

### 5. Run the application

```bash
python project.py
```


## 📦 Download the executable

Pre-built executables for Linux, Windows, and macOS are available on the [Releases page](https://github.com/kingprog-hcr/Weathers-Assistant/releases).

**Setup:**
1. Download the executable for your system
2. Create a `.env` file in the same folder as the executable
3. Add your API keys to the `.env` file
4. Run the executable

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
| [OpenWeatherMap](https://openweathermap.org/api) | Current weather + forecast + city GPS | Free (1000 calls/day) |
| [ip-api.com](http://ip-api.com) | Automatic city detection via IP | Free |
| [ZenQuotes](https://zenquotes.io) | Daily inspirational quotes | Free |
| [Groq](https://console.groq.com) | AI venue enrichment (optional) | Free tier |



## 👨‍💻 Author

**Chrys-Renabell HASSAM**
CS50P Final Project : 2026



## 📄 License

This project was built for educational purposes as part of Harvard's CS50P course.
Feel free to explore, fork, and build upon it.



*This is CS50.*
