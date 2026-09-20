
import pandas as pd 
import json

def Transform():
    with open('./data/bronze/weather_raw.json',encoding="utf-8") as f:
        data=json.load(f)
    data=pd.json_normalize(data)#json -> df

    # listes en column
    daily_columns = [
        "daily.time",
        "daily.temperature_2m_max",
        "daily.temperature_2m_min",
        "daily.precipitation_sum",
        "daily.precipitation_probability_max",
        "daily.wind_speed_10m_max",
        "daily.wind_gusts_10m_max",
        "daily.weather_code"
    ]
    data=data.explode(
        daily_columns,ignore_index=True
    )


    # print(data.head())

    # => numeric 
    # je doit  faire for
    data["daily.time"]=pd.to_datetime(data["daily.time"])
    column=[
        "daily.temperature_2m_min",
        "daily.temperature_2m_max",
        "daily.precipitation_sum",
        "daily.precipitation_probability_max",
        "daily.wind_speed_10m_max",
        "daily.wind_gusts_10m_max",
        "daily.weather_code"
    ]
    for ele in column:
        data[ele]=pd.to_numeric(data[ele],errors="coerce") 

    # virifier les valeur manquant
    print("valeurs manquantes :")
    print(data.isna().sum()) 

    # traitemantdes value manquantes
    data["timezone"]=data["timezone"].fillna("Africa/Casablanca")
    data["daily.temperature_2m_min"]=data["daily.temperature_2m_min"].fillna(data["daily.temperature_2m_min"].mean())

    # virifier les doublons 
    print(data.duplicated().sum())

    data.dropna(inplace=True)

    data.drop_duplicates(inplace=True)

    # incoherent 
    print("-----------INC-----------")
    incoherent = (
    (data["daily.temperature_2m_min"]>data["daily.temperature_2m_max"]) |
    (data["daily.precipitation_sum"] < 0) |
    (data["daily.wind_speed_10m_max"] < 0)|
    (data["daily.precipitation_probability_max"]<0) | 
    (data["daily.precipitation_probability_max"]>100) |
    (data["daily.wind_gusts_10m_max"] <data["daily.wind_speed_10m_max"])
    )

    # supp les ligne inco
    if incoherent.any():
        data=data[~incoherent]
        print("lignes incoherent supprimer")
    else:
        print("aucun ligne incoherente")



    print("------------ data ---------")
    print(data)


    # print(data.columns)
    # les column to keep
    columns_to_keep=[
        "city",
        "lat",
        "lng",
        "daily.time",
        "daily.temperature_2m_max",
        "daily.temperature_2m_min",
        "daily.precipitation_sum",
        "daily.precipitation_probability_max",
        "daily.wind_speed_10m_max",
        "daily.wind_gusts_10m_max",
        "daily.weather_code"
    ]
    data=data[columns_to_keep]

    print(data.dtypes)
    print(data.head())

    print(data)

    data.to_csv("./data/silver/weather_raw_clean.csv",index=False,encoding="utf-8")
    


Transform()

