import requests 
import os
from dotenv import load_dotenv

#use an API to connect with an IA like gpt or gemini

def main():
    city = input("Entrez une ville : ")
    print(get_weather(city))
    data = get_weather(city)


def get_weather(city):
    
    load_dotenv()
    api_key = os.getenv("API_KEY")
    
    params = {
        "q": city,  
        "appid": api_key,
        "units": "metric",
        "lang": "fr"
    }
    
    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        print("Erreur HTTP :", e)
    except requests.exceptions.ConnectionError:
        print("Pas de connexion internet")

if __name__== "__main__" :
    main()