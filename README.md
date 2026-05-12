# 🌤️ WeatherProgramm

> A smart weather-based day planner :  CS50 Final Project



## 📖 About This Project

**WeatherProgramm** is the final project for [CS50's Introduction to Programming with Python](https://cs50.harvard.edu/python/), offered by Harvard University through edX.

The goal was to build a complete, real-world Python application that goes beyond simple scripts combining APIs, object-oriented programming, a graphical interface, data persistence, and AI-powered suggestions into a single cohesive product.

### The idea

We all check the weather every morning. But knowing it's 14°C and cloudy doesn't tell you *what to do* with your day. **WeatherProgramm** bridges that gap: it fetches real-time weather data for any city and builds a complete, personalized day plan  activities, outfit, meals, a daily score, and an inspiring quote  all tailored to your tastes, mood, and preferred style.


## ✨ Features

### 🌦️ Real-time weather
- Fetches current conditions from **OpenWeatherMap API**
- Displays temperature, feels-like, humidity, wind speed, and condition icon
- Automatic city detection via IP geolocation (editable at any time)
- Weather-based day score out of 10

### 📅 Personalized day program
- Generates a full schedule (08:00 → 21:00) adapted to the weather at each time slot
- Activities filtered by your personal tastes (sport, culture, nature, gastronomy, etc.)
- Meal suggestions tailored to your preferred cuisine
- Outfit recommendations based on temperature, rain, and your style (streetwear, old money, casual, etc.)
- Inspiring quote of the day

### 👤 User profile
- Name, bio/description, tastes, mood of the day, clothing style, preferred cuisine
- Profile saved locally and reloaded at every launch
- Day history tracking

### 🗺️ Interactive map *(coming soon)*
- Visualize suggested activity locations on an interactive map

### 🤖 AI enrichment *(coming soon)*
- Integration with Google Gemini API to suggest real venues in your city
- Fully personalized programs based on your profile description



## 🏗️ Project Architecture

The project follows a clean **object-oriented architecture** with a strict separation of concerns:

```
Weathers-Assistant/
│
├── projet.py               ← CS50 entry point (main + 3 testable functions)
├── test_projet.py          ← pytest test suite
├── models.py               ← Data models (dataclasses)
├── requirements.txt
├── README.md
│
├── core/                   ← Business logic (no UI, no network calls from UI)
│   ├── weather_service.py  ← OpenWeatherMap API + cache + geolocation
│   ├── activity_engine.py  ← Activity, outfit & food suggestions
│   ├── day_planner.py      ← Day program builder + scoring + quotes
│   └── user_profile.py     ← Profile load/save (JSON)
│
├── ui/                     ← CustomTkinter interface
│   ├── config.py           ← Shared colors, fonts, utilities
│   ├── main_window.py      ← Main window + sidebar + navigation
│   ├── weather_frame.py    ← Weather page
│   ├── program_frame.py    ← Day program page
│   └── profile_frame.py    ← User profile page
│
└── data/                   ← Local data files
    ├── activities.json     ← Activity database by weather condition & taste
    ├── profile.json        ← Saved user profile (auto-generated)
    └── cache_meteo.json    ← Weather cache 30 min TTL (auto-generated)
```

### Design principles applied
- **Single Responsibility** : each class has one job
- **Separation of concerns** : UI never calls APIs directly
- **Data models** : all data flows through typed `dataclasses`
- **Caching** : weather results cached for 30 minutes to reduce API calls
- **Absolute paths** : all file access uses `Path(__file__)` for portability



## 🧪 CS50 Requirements

This project fulfills all CS50 final project requirements:

| Requirement | Implementation |
|---|---|
| Main file named `projet.py` | ✅ |
| `main()` function | ✅ |
| At least 3 custom functions | ✅ `get_greeting()`, `is_first_launch()`, `add_day_to_history()` |
| Test file named `test_projet.py` | ✅ |
| Tests using `pytest` | ✅ 3 test functions with full coverage of all 3 custom functions |

Run the tests:
```bash
pytest test_projet.py -v
```


## ⚙️ Installation

### Prerequisites

- Python **3.12** or higher
- A free **OpenWeatherMap API key** : [Get one here](https://openweathermap.org/api)

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

### 4. Configure your API key

Create a `.env` file at the root of the project:

```env
API_KEY=your_openweathermap_api_key_here
```

### 5. Run the application

```bash
python projet.py
```

On first launch, a welcome screen will appear, detect your city automatically, and invite you to configure your profile.



## 🖥️ How to Use

### First launch
When you open WeatherProgramm for the first time, a welcome screen greets you, shows your automatically detected city, and invites you to configure your profile. You can skip this and do it later.

### Changing your city
Use the search bar in the left sidebar at any time. Press **Enter** or click **→** to refresh all data for the new city.

### Weather page
Displays current conditions, a day score out of 10, your suggested outfit (based on your style preference), a quote of the day, and meal suggestions for breakfast, lunch, and dinner.

### Program page
Shows your full day schedule as cards, each with the time, local weather at that hour, the suggested activity, and a color-coded category badge. Click **Regénérer** to generate a new program.

### Profile page
Configure your name, bio, tastes (multi-select), mood of the day, clothing style, and preferred cuisine. Click **Sauvegarder le profil** to save all other pages refresh automatically.



## 📦 Dependencies

| Library | Purpose |
|---|---|
| `customtkinter` | Modern dark-mode UI framework |
| `requests` | HTTP calls to weather & geolocation APIs |
| `python-dotenv` | Loading API keys from `.env` |
| `Pillow` | Displaying weather icons (PNG) |
| `tkintermapview` | Interactive map *(upcoming)* |
| `pytest` | Test suite |

Install all at once:
```bash
pip install -r requirements.txt
```



## 🔑 APIs Used

| API | Purpose | Cost |
|---|---|---|
| [OpenWeatherMap](https://openweathermap.org/api) | Current weather + 5-day forecast | Free (1000 calls/day) |
| [ip-api.com](http://ip-api.com) | Automatic city detection via IP | Free |
| [ZenQuotes](https://zenquotes.io) | Random inspirational quotes | Free |
| Google Gemini *(upcoming)* | AI-powered venue & activity suggestions | Free tier |



## 🚀 Upcoming Features

- **Interactive map** : visualize suggested locations on a real map
- **AI integration** : Google Gemini for real venue suggestions based on your city
- **Multi-day forecast** : 5-day weather overview with daily activity suggestions
- **Windows .exe export** : standalone executable via PyInstaller
- **Voice output** : text-to-speech reading of your daily program


## 👨‍💻 Author

**Chrys-Renabell HASSAM**
CS50P Final Project  2026
Developed with Python

## 📄 License

This project was built for educational purposes as part of Harvard's CS50P course.
Feel free to explore, fork, and build upon it.


*This is CS50.*
