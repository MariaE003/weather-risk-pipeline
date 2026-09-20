import streamlit as st
import pandas as pd
from sqlalchemy import create_engine,text,select


st.title("Weather Risk Dashboard")
# virifier si la connection est bien fait
# with engine.connect() as connection:
#     result=connection.execute(text("SELECT 1"))
#     print(result.scalar())


# engine=create_engine("postgresql+psycopg://postgres:maria@localhost:5432/wheather-risk-pipline")
engine=create_engine("postgresql+psycopg://weather_user:weather_password@postgres:5432/wheather-risk-pipline")

data=pd.read_sql("SELECT c.name,c.lat,c.lng,w.date,w.temperature_max,w.temperature_min,w.precipitation,w.precipitation_probability,w.wind_speed,w.wind_gusts,w.risk_score,w.risk_level FROM cities c INNER JOIN weather w ON w.city_id=c.id",engine)
data["date"] = pd.to_datetime(data["date"])
# statis
cities=pd.read_sql("SELECT * FROM cities",engine)
total_cities=len(cities)


temp_max=pd.read_sql("SELECT MAX(temperature_max) AS temp_max FROM weather",engine)

precip_max=pd.read_sql("SELECT MAX(precipitation) AS precip_max FROM weather",engine)

nbr_preiode_a_risque=pd.read_sql("SELECT COUNT(*) AS nbr FROM weather WHERE risk_level IN ('Moderate','High','Very high')",engine)

ville_risk_eleve=pd.read_sql("SELECT c.name FROM cities c INNER JOIN weather w ON w.city_id=c.id ORDER BY w.risk_score DESC LIMIT 1",engine)
col1,col2,col3,col4,col5=st.columns(5)

with col1:
    st.metric("Cities",total_cities)
with col2:
    st.metric("température maximale",temp_max.iloc[0]["temp_max"])
with col3:
    st.metric("précipitations maximales",precip_max.iloc[0]["precip_max"])
with col4:
    st.metric("nombre de périodes à risque",nbr_preiode_a_risque.iloc[0]["nbr"])
with col5:
    st.metric("ville présentant le risque le plus élevé",ville_risk_eleve.iloc[0]["name"])



# filtring
st.sidebar.title("Filters")
#par ville
city_filter=st.sidebar.selectbox(
    "Ville",
    ["Toutes"] + data["name"].unique().tolist()
) 

#par date

date_range=st.sidebar.date_input(
    "Periode",
    value=(data["date"].min(),data["date"].max())
)

#niveau de risque
risk_filter=st.sidebar.multiselect(
    "Niveau de risque",
    data["risk_level"].unique().tolist()
)


filtered=data.copy()

#ville
if city_filter != "Toutes":
    filtered=filtered[filtered["name"]== city_filter]

# date
if(len(date_range))==2:
    start_date,end_date=date_range
    filtered=filtered[
        (filtered["date"]>=pd.Timestamp(start_date))&
        (filtered["date"]<=pd.Timestamp(end_date))

    ]

if risk_filter:
    filtered=filtered[filtered["risk_level"].isin(risk_filter)]

st.subheader("Prévisions et périodes à risque")
st.dataframe(filtered,hide_index=True)

#risk par periode 
risk_par_date=filtered.groupby("date")["risk_score"].mean()
st.line_chart(risk_par_date)
