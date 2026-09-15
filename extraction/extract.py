import requests
import pandas as pd
import json

def extract():

    try:
        open_meteo = "https://api.open-meteo.com/v1/forecast"
        simpleMaps="./ma.csv"

        test=pd.read_csv(simpleMaps)# -> dataFrame
        data=[]

        for index,row in test.iterrows():
            lat = row["lat"]
            lng = row["lng"]
            city = row["city"]
            # print(city)
            params={
                "latitude":lat,
                "longitude": lng,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "wind_speed_10m_max",
                    "wind_gusts_10m_max",
                    "weather_code"
                ],
                "forecast_days": 7,
                "timezone": "Africa/Casablanca"
            }
            try:
                result=requests.get(open_meteo,params=params,timeout=10)

                result.raise_for_status()#virifier les erreur http
                
                weather_data=result.json()

                if weather_data.get("error"):
                    print(f"erreur api pour {city} : {weather_data.get('reason')}")
                    continue

                weather_data["city"]=city
                weather_data["lat"]=lat
                weather_data["lng"]=lng

                data.append(weather_data)
            except requests.exceptions.Timeout:
                print(f"Timeout pour {city}")
            except requests.exceptions.HTTPError as e:
                print(f"erreur Http pour {city} : {e}")
            except requests.exceptions.RequestException as e:
                print(f"erreur reseau pour {city} : {e}")
            except ValueError:
                print(f"reponse json invalide pour {city}")
                
        with open("./data/bronze/weather_raw.json","w") as f:
            json.dump(data,f,ensure_ascii=True,indent=4)
    except FileNotFoundError:
        print("le fichier csv est vide")
    except pd.errors.EmptyDataError:
        print("le fichier csv est introuvable")
    except Exception as e:
        print(f"erreur inattendue : {e}")
    
extract()

