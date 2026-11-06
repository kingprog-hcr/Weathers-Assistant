from core import config
from core.user_profile import UserProfile
from models import ProfileData, WeatherData


def test_frozen_windows_uses_persistent_appdata(monkeypatch, tmp_path):
    monkeypatch.setattr(config.sys, "frozen", True, raising=False)
    monkeypatch.setattr(config.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path))

    assert config._find_user_data_dir() == tmp_path / "WeatherProgramm"


def test_development_keeps_data_directory(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(config.sys, "frozen", False, raising=False)
    monkeypatch.setattr(config, "_find_data_dir", lambda: data_dir)

    assert config._find_user_data_dir() == data_dir


def test_profile_save_creates_directory_and_can_be_reloaded(monkeypatch, tmp_path):
    profile_file = tmp_path / "persistent" / "profile.json"
    monkeypatch.setattr(UserProfile, "PROFILE_FILE", profile_file)
    profile = ProfileData(name="Chrys")

    UserProfile().save(profile)

    assert profile_file.is_file()
    assert UserProfile().load().name == "Chrys"


def test_data_path_uses_bundled_default_until_user_override_exists(
    monkeypatch, tmp_path
):
    bundled_dir = tmp_path / "bundled"
    user_dir = tmp_path / "user"
    bundled_dir.mkdir()
    (bundled_dir / "activities.json").write_text('{"default": true}')
    monkeypatch.setattr(config, "DATA_DIR", bundled_dir)
    monkeypatch.setattr(config, "USER_DATA_DIR", user_dir)

    assert config.get_data_path("activities.json") == bundled_dir / "activities.json"

    user_file = user_dir / "activities.json"
    user_file.parent.mkdir()
    user_file.write_text('{"custom": true}')
    assert config.get_data_path("activities.json") == user_file


def test_category_changes_are_saved_to_user_data(monkeypatch, tmp_path):
    from ui import config as ui_config

    user_categories = tmp_path / "user" / "categories.json"
    monkeypatch.setattr(
        ui_config, "get_user_data_path", lambda name: user_categories
    )
    monkeypatch.setattr(ui_config, "get_data_path", lambda name: user_categories)
    categories = {"custom": {"label": "Custom", "keywords": ["custom"]}}

    assert ui_config.save_slot_categories(categories)
    assert ui_config.load_slot_categories() == categories


def test_weather_cache_save_creates_persistent_directory(monkeypatch, tmp_path):
    from core.weather_service import WeatherService

    cache_file = tmp_path / "user" / "cache_meteo.json"
    monkeypatch.setattr(WeatherService, "CACHE_FILE", str(cache_file))
    weather = WeatherData(
        city="Angers",
        temp=18,
        feels_like=17,
        condition="Clouds",
        description="nuageux",
        icon="02d",
        humidity=60,
        wind_speed=12,
    )

    WeatherService()._save_cache("Angers", weather)

    assert cache_file.is_file()
