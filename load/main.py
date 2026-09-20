import pandas as pd

#virification du weather_code
def get_weather_condition(code):
    match code:
        case 0 | 1:
            return "Clear"
        case 2 | 3:
            return "Cloudy"
        case 45 | 48:
            return "Fog"
        case 51 | 53 | 55 | 56 | 57:
            return "Drizzle"
        case  61 | 63 | 65 | 66 | 67:
            return "Rain"
        case 80 | 81 | 82:
            return "Rain showers"
        case 95 | 96 | 99:
            return "Thunderstorm"
        case _:
            return "Unknown"

def test():
    data=pd.read_csv('./data/silver/weather_raw_clean.csv')

    # tmp moyenne
    data["temperature_moyenne"]=(data["daily.temperature_2m_max"] + data["daily.temperature_2m_min"])/2

    #
    data["is_rainy"] = data["daily.precipitation_sum"] > 0

    # categorie


    # perci...
    # print(data["daily.precipitation_sum"].max()) 
    # print(data["daily.precipitation_sum"].min()) 
    # ...
    # print(data["daily.temperature_2m_max"].max()) 
    # print(data["temperature_moyenne"].min()) 



    data["rain_risk"]=pd.cut(data["daily.precipitation_sum"],bins=[-0.001,0,1,5,float("inf")],labels=["No rain", "Light", "Moderate", "Heavy"])
    data["temperature_risk"]=pd.cut(data["daily.temperature_2m_max"],bins=[-float("inf"),30,35,40,float("inf")],labels=["Normal", "Warm", "High", "Very high"])

    data["wind_speed_risk"]=pd.cut(data["daily.wind_speed_10m_max"],bins=[-float("inf"),20,30,40,float("inf")],labels=["Low","Moderate","High","Very high"])
    data["wind_gusts_risk"]=pd.cut(data["daily.wind_gusts_10m_max"],bins=[-float("inf"),40,50,65,float("inf")],labels=["Low","Moderate","High","Very high"])

    data["precipitation_probability_risk"]=pd.cut(data["daily.precipitation_probability_max"],bins=[-0.001,20,50,100],labels=["Low","Moderate","High"])


    # resk_global
    # data["resk_level"]= pd.cut(data["daily.precipitation_sum"],bins=[0,20,30,40],labels=categories)
   
    # categoriser
    data["weather_condition"]=data["daily.weather_code"].apply(get_weather_condition)

    # risk level
    #  score
    
    data["risk_score"]=((
        data["rain_risk"].map({
            "No rain": 0,
            "Light": 1,
            "Moderate": 2,
            "Heavy": 3
        }).astype(float)
        +
        data["temperature_risk"].map({
            "Normal": 0,
            "Warm": 1,
            "High": 2,
            "Very high": 3
        }).astype(float)
        +
        data["wind_speed_risk"].map({
            "Low": 0,
            "Moderate": 1,
            "High": 2,
            "Very high": 3
        }).astype(float)
        +
        data["wind_gusts_risk"].map({
            "Low": 0,
            "Moderate": 1,
            "High": 2,
            "Very high": 3
        }).astype(float)
        +
        data["precipitation_probability_risk"].map({
            "Low": 0,
            "Moderate": 1,
            "High": 2
        }).astype(float)
        +
        data["weather_condition"].map({
            "Clear": 0,
            "Cloudy": 0,
            "Drizzle": 1,
            "Fog": 2,
            "Rain": 2,
            "Rain showers": 2,
            "Thunderstorm": 3,
            "Unknown": 0
        }).astype(float)
    ) / 17 * 100).round(2)

    data["risk_level"]=pd.cut(data["risk_score"],bins=[-1,25,50,75,100],labels=["Low","Moderate","High","Very high"])

    # print(data[[
    #     "city",
    #     "daily.time",
    #     "rain_risk",
    #     "temperature_risk",
    #     "wind_speed_risk",
    #     "wind_gusts_risk",
    #     "weather_condition",
    #     "risk_score"
    # ]].head())
    # print(data)

    # sauvegarde Gold
    data.to_csv("./data/gold/weather_risk.csv",index=False,encoding="utf-8")
test()