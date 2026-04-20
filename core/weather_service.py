import requests
import os
from dotenv import load_dotenv


class WeatherService:

    def __init__(self, city=None):
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        self.city = city

    def get_weather(self):
        if not self.api_key:
            print("Erreur : API_KEY non configurée")
            return None

        params = {
            "q": self.city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "fr",
        }

        try:
            response = requests.get(
                "https://api.openweathermap.org/data/2.5/weather", params=params
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            print("Erreur HTTP :", e)
        except requests.exceptions.ConnectionError:
            print("Pas de connexion internet")

    def set_city(self, city):
        self.city = city

    def get_city(self):
        return self.city

    def get_city_auto(self):
        try:
            response = requests.get("https://ipinfo.io/json")
            response.raise_for_status()
            data = response.json()
            self.set_city(data.get("city", "Unknown"))
            return self.get_city()
        except requests.exceptions.HTTPError as e:
            print("Erreur HTTP :", e)
        except requests.exceptions.ConnectionError:
            print("Pas de connexion internet")

    def get_forecast(self, city, days):
        pass


if __name__ == "__main__":
    a = WeatherService()
    print(a.get_city_auto())
