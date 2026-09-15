import pandas as pd 

def Transform():
    data=pd.read_json('./data/bronze/weather_raw.json',encoding='utf-8',encoding_errors='ignore')
    # print(type(data))
    

Transform()