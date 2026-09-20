from sqlalchemy import create_engine,text,ForeignKey,Date
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,Session
from datetime import date
import pandas as pd
engine = create_engine("postgresql+psycopg://weather_user:weather_password@postgres:5432/wheather-risk-pipline")

# virifier si la connection est bien fait
# with engine.connect() as connection:
#     result=connection.execute(text("SELECT 1"))
#     print(result.scalar())

class Base(DeclarativeBase):
    pass

class City(Base):
    __tablename__="cities"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]
    lat:Mapped[float]
    lng:Mapped[float]

class Weather(Base):
    __tablename__="weather"
    id:Mapped[int]=mapped_column(primary_key=True)
    city_id:Mapped[int]=mapped_column(ForeignKey("cities.id"))#cities.id
    date:Mapped[date]=mapped_column(Date)
    temperature_max:Mapped[float]
    temperature_min:Mapped[float]

    precipitation:Mapped[float]
    precipitation_probability:Mapped[int]

    wind_speed:Mapped[float]
    wind_gusts:Mapped[float]

    weather_code:Mapped[int]
    weather_condition:Mapped[str]

    risk_score:Mapped[float]
    risk_level:Mapped[str]
    

def load_cities(data):
    with Session(engine) as sess:
        for index,row in data.iterrows():
            city = sess.query(City).filter_by(name=row["city"]).first()
            if city is None:
                city=City(name=row["city"],lat=row["lat"],lng=row["lng"])
                sess.add(city)
                sess.commit()

def load_meteo(data):
    with Session(engine) as sess:
        for index,row in data.iterrows():
            city=sess.query(City).filter_by(name=row["city"]).first()
            meteo_date=pd.to_datetime(row["daily.time"]).date()
            meteo=sess.query(Weather).filter_by(city_id=city.id , date=meteo_date).first()
            if meteo is None:
                meteo=Weather(
                        city_id=city.id,
                        date=meteo_date,
                        temperature_max=row["daily.temperature_2m_max"],
                        temperature_min=row["daily.temperature_2m_min"],
                        precipitation=row["daily.precipitation_sum"],
                        precipitation_probability=row["daily.precipitation_probability_max"],
                        wind_speed=row["daily.wind_speed_10m_max"],
                        wind_gusts=row["daily.wind_gusts_10m_max"],
                        weather_code=row["daily.weather_code"],
                        weather_condition=row["weather_condition"],
                        risk_score=row["risk_score"],
                        risk_level=row["risk_level"]
                )
                sess.add(meteo)
            sess.commit()

def fetch_data():
    data=pd.read_csv("./data/gold/weather_risk.csv")
    load_cities(data)
    load_meteo(data)
    # print(data.columns)
    # print(data.head())



Base.metadata.create_all(engine)
fetch_data()
