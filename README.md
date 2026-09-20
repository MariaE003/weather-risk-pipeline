# weather-risk-pipeline

##  Description du projet

**Weather Risk Pipeline** est un pipeline de données de bout en bout permettant de collecter, transformer, analyser et visualiser des données météorologiques pour plusieurs villes marocaines.

Le projet s'inscrit dans un contexte de **livraison et de logistique** : les conditions météorologiques peuvent avoir un impact sur les opérations de livraison.

L'objectif principal est de répondre à la question :

> **Quelles villes et quelles périodes présentent le plus grand risque météorologique dans les prochains jours ?**

Le pipeline automatise les différentes étapes du traitement des données :

```text
API météo
   ↓
Extraction
   ↓
Bronze
   ↓
Transformation / Nettoyage
   ↓
Silver
   ↓
Feature Engineering / Risk Score
   ↓
Gold
   ↓
PostgreSQL
   ↓
Streamlit Dashboard
```

L'orchestration et l'automatisation sont réalisées avec **Apache Airflow**, exécuté avec Docker.

---

#  Architecture du projet

```text
                    ┌──────────────────┐
                    │   Open-Meteo API │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Extraction    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      Bronze      │
                    │   Raw JSON data  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Transformation  │
                    │ Cleaning + Types │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      Silver      │
                    │  Cleaned data    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Feature         │
                    │  Engineering     │
                    │  Risk Score      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │       Gold       │
                    │ Weather + Risk   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   PostgreSQL     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Streamlit     │
                    │    Dashboard     │
                    └──────────────────┘


              ┌──────────────────────────┐
              │       Apache Airflow     │
              │                          │
              │ Extract → Transform      │
              │          → Load          │
              └──────────────────────────┘
```

---

#  API choisie

## Open-Meteo

Le projet utilise **Open-Meteo** comme source de données météorologiques.

API utilisée :

```text
https://api.open-meteo.com/v1/forecast
```

Open-Meteo fournit notamment les prévisions météorologiques quotidiennes.

### Données récupérées

Pour chaque ville, les variables suivantes sont utilisées :

| Variable                        | Description                                   |
| ------------------------------- | --------------------------------------------- |
| `temperature_2m_max`            | Température maximale                          |
| `temperature_2m_min`            | Température minimale                          |
| `precipitation_sum`             | Quantité de précipitations                    |
| `precipitation_probability_max` | Probabilité maximale de précipitation         |
| `wind_speed_10m_max`            | Vitesse maximale du vent                      |
| `wind_gusts_10m_max`            | Rafales maximales                             |
| `weather_code`                  | Code représentant la condition météorologique |

Les prévisions sont récupérées sur plusieurs jours avec :

```text
forecast_days = 7
timezone = Africa/Casablanca
```

---

#  Données des villes

Les villes marocaines et leurs coordonnées géographiques sont récupérées depuis un fichier CSV.

Fichier :

```text
ma.csv
```

Colonnes principales :

```text
city
lat
lng
```

Ces coordonnées sont ensuite utilisées pour interroger l'API Open-Meteo.

---

#  Organisation des données

Le projet utilise une architecture en trois couches :

##  Bronze

La couche Bronze contient les données récupérées depuis l'API dans leur format brut.

```text
data/
└── bronze/
    └── weather_raw.json
```

Cette couche permet de conserver les données originales avant transformation.

---

##  Silver

La couche Silver contient les données nettoyées et structurées.

Les principales opérations sont :

* transformation des données JSON ;
* aplatissement des données imbriquées ;
* transformation des listes en lignes ;
* gestion des types ;
* vérification des valeurs manquantes ;
* vérification des doublons ;
* préparation des données pour l'analyse.

Fichier :

```text
data/
└── silver/
    └── weather_raw_clean.csv
```

---

##  Gold

La couche Gold contient les données finales utilisées pour l'analyse et le chargement dans PostgreSQL.

Les opérations réalisées comprennent :

* calcul de la température moyenne ;
* catégorisation des précipitations ;
* catégorisation de la température ;
* catégorisation du vent ;
* catégorisation des rafales ;
* catégorisation de la probabilité de précipitation ;
* classification de la condition météorologique ;
* calcul du `risk_score` ;
* détermination du `risk_level`.

Fichier :

```text
data/
└── gold/
    └── weather_risk.csv
```

---

#  Calcul du risque météorologique

Un score de risque est calculé pour chaque ville et chaque date.

Les facteurs pris en compte sont :

* précipitations ;
* température ;
* vitesse du vent ;
* rafales de vent ;
* probabilité de précipitation ;
* condition météorologique.

Chaque facteur reçoit un niveau de risque.

Le score final est ensuite normalisé sur une échelle de **0 à 100**.

```text
0 ─────────────────────────────── 100
        Risque météorologique
```

Les niveaux utilisés sont :

|    Score | Niveau    |
| -------: | --------- |
|   0 – 25 | Low       |
|  25 – 50 | Moderate  |
|  50 – 75 | High      |
| 75 – 100 | Very high |

Les seuils utilisés dans le projet sont des **règles de modélisation définies pour le projet**. Ils peuvent être ajustés selon les besoins métier ou de nouvelles données.

---

#  Schéma de la base de données

Les données finales sont stockées dans PostgreSQL.

La base contient principalement deux tables :

```text
┌──────────────────────┐
│       cities         │
├──────────────────────┤
│ id PK                │
│ name                 │
│ lat                  │
│ lng                  │
└──────────┬───────────┘
           │
           │ 1
           │
           │ N
┌──────────▼───────────┐
│       weather        │
├──────────────────────┤
│ id PK                │
│ city_id FK           │
│ date                 │
│ temperature_max      │
│ temperature_min      │
│ precipitation        │
│ precipitation_prob.  │
│ wind_speed           │
│ wind_gusts           │
│ weather_code         │
│ weather_condition    │
│ risk_score           │
│ risk_level           │
└──────────────────────┘
```

### Relation

Une ville peut avoir plusieurs prévisions météorologiques.

```text
cities 1 ─────────── N weather
```

La combinaison :

```text
city_id + date
```

est utilisée pour éviter de charger plusieurs fois la même prévision pour une ville et une date.

---

#  Dashboard Streamlit

Le dashboard permet de consulter les données météorologiques et les niveaux de risque.

Il contient notamment :

### KPI

* Nombre de villes ;
* Nombre de prévisions ;
* Risque moyen ;
* Nombre de jours à risque élevé.

### Filtres

* Filtre par ville ;
* Filtre par niveau de risque.

### Visualisations

* évolution du risque météorologique par date ;
* risque moyen par ville ;
* tableau détaillé des prévisions.

Les données sont récupérées directement depuis PostgreSQL.

Après l'exécution du pipeline Airflow, les nouvelles données sont disponibles dans PostgreSQL et peuvent être affichées dans le dashboard lors du prochain chargement ou rafraîchissement de Streamlit.

---

#  Orchestration avec Apache Airflow

Le pipeline est automatisé avec Apache Airflow.

Le DAG principal est :

```text
weather_risk_pipeline
```

Il contient trois tâches principales :

```text
extract_weather
       ↓
transform_weather
       ↓
load_postgres
```

### 1. Extraction

```text
extract_weather
```

Exécute le script :

```text
extraction/extract.py
```

Il récupère les données depuis Open-Meteo.

### 2. Transformation

```text
transform_weather
```

Exécute :

```text
transformation/transform.py
```

Il nettoie les données et réalise le feature engineering.

### 3. Chargement

```text
load_postgres
```

Exécute :

```text
load/main.py
```

Il charge les données finales dans PostgreSQL.

---

#  Planification

Le DAG est configuré pour être exécuté quotidiennement :

```python
schedule="@daily"
```

Le paramètre :

```python
catchup=False
```

évite l'exécution automatique des anciennes dates lorsque le DAG est démarré.

---

#  Gestion des erreurs

Le DAG utilise des retries :

```python
default_args = {
    "retries": 2
}
```

En cas d'échec d'une tâche, Airflow peut donc effectuer automatiquement des nouvelles tentatives.

---

#  Docker

Airflow est exécuté avec Docker Compose.

Les principaux services utilisés dans le projet sont :

```text
Docker
│
├── Airflow
├── PostgreSQL
└── Streamlit
```

Les dossiers du projet sont montés dans les conteneurs Airflow afin que les scripts soient accessibles :

```text
extraction/
transformation/
load/
data/
dags/
```

---

#  Structure du projet

```text
weather-risk-pipeline/
│
├── extraction/
│   └── extract.py
│
├── transformation/
│   └── transform.py
│
├── load/
│   └── main.py
│
├── data/
│   ├── bronze/
│   │   └── weather_raw.json
│   │
│   ├── silver/
│   │   └── weather_raw_clean.csv
│   │
│   └── gold/
│       └── weather_risk.csv
│
├── dashboard/
│   └── app.py
│
├── dags/
│   └── weather_risk_dag.py
│
├── docs/
│   └── screenshots/
│       ├── dashboard.png
│       ├── filters.png
│       └── charts.png
│
├── ma.csv
├── docker-compose.yaml
├── requirements.txt
├── .env
└── README.md
```
---

#  Installation

## 1. Cloner le projet

```bash
git clone <URL_DU_REPOSITORY>
cd weather-risk-pipeline
```

---

## 2. Créer un environnement Python

```bash
python -m venv venv
```

Activer l'environnement sous Windows :

```bash
venv\Scripts\activate
```

---

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Les principales bibliothèques utilisées sont :

```text
pandas
requests
sqlalchemy
psycopg
streamlit
```

Airflow est exécuté dans Docker.

---

#  Configuration PostgreSQL

Créer la base de données PostgreSQL utilisée par le projet.

La connexion utilisée par SQLAlchemy est de la forme :

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

Exemple de configuration locale :

```text
postgresql+psycopg://postgres:<PASSWORD>@localhost:5432/wheather-risk-pipline
```

Adapter les informations de connexion à l'environnement local.

---

#  Exécution manuelle du pipeline

## Extraction

```bash
python extraction/extract.py
```

Les données sont enregistrées dans :

```text
data/bronze/
```

## Transformation

```bash
python transformation/transform.py
```

Les données nettoyées sont enregistrées dans :

```text
data/silver/
```

et les données finales dans :

```text
data/gold/
```

## Chargement PostgreSQL

```bash
python load/main.py
```

Les données Gold sont chargées dans PostgreSQL.

---

#  Lancer le dashboard

Depuis la racine du projet :

```bash
streamlit run dashboard/app.py
```

Le dashboard est ensuite accessible localement avec l'URL affichée par Streamlit, généralement :

```text
http://localhost:8501
```

---

#  Lancer Airflow avec Docker

Depuis la racine du projet :

```bash
docker compose up -d
```

Vérifier les conteneurs :

```bash
docker compose ps
```

L'interface Airflow est accessible localement :

```text
http://localhost:8080
```

Le DAG à utiliser est :

```text
weather_risk_pipeline
```

---

#  Exécution complète avec Airflow

Une fois Airflow lancé :

```text
weather_risk_pipeline
        │
        ▼
extract_weather
        │
        ▼
transform_weather
        │
        ▼
load_postgres
```

Airflow orchestre automatiquement les différentes étapes du pipeline.

Le DAG est planifié quotidiennement et les tâches disposent de mécanismes de retry en cas d'échec.

---

#  Vérification du pipeline

Après l'exécution du DAG, vérifier que les trois tâches sont terminées avec succès :

```text
extract_weather     Success
transform_weather   Success
load_postgres       Success
```

Les données peuvent ensuite être vérifiées dans PostgreSQL.

Exemple :

```sql
SELECT COUNT(*) FROM cities;

SELECT COUNT(*) FROM weather;

SELECT *
FROM weather
LIMIT 10;
```

La logique de chargement vérifie également si une prévision existe déjà pour une combinaison donnée de :

```text
city_id + date
```

afin d'éviter les doublons lors des nouvelles exécutions du pipeline.

---

#  Technologies utilisées

| Technologie    | Utilisation                                |
| -------------- | ------------------------------------------ |
| Python         | Développement du pipeline                  |
| Pandas         | Manipulation et transformation des données |
| Requests       | Appels API                                 |
| Open-Meteo     | Source des données météo                   |
| SQLAlchemy     | Connexion et interaction avec PostgreSQL   |
| PostgreSQL     | Stockage des données                       |
| Streamlit      | Dashboard                                  |
| Apache Airflow | Orchestration et automatisation            |
| Docker         | Conteneurisation                           |
| Git / GitHub   | Versionnement du projet                    |

---

#  Objectifs réalisés

Le projet permet de :

* récupérer automatiquement les prévisions météorologiques ;
* stocker les données brutes dans une couche Bronze ;
* nettoyer et structurer les données dans Silver ;
* réaliser du feature engineering dans Gold ;
* calculer un score de risque météorologique ;
* stocker les données finales dans PostgreSQL ;
* visualiser les résultats avec Streamlit ;
* automatiser le pipeline avec Airflow ;
* planifier une exécution quotidienne ;
* gérer les échecs avec des retries ;
* éviter les doublons lors du chargement des prévisions.

---

#  Résultat final

Le projet fournit une chaîne complète de traitement de données :

```text
          Open-Meteo
              │
              ▼
        ┌─────────────┐
        │  Extraction │
        └──────┬──────┘
               ▼
            Bronze
               │
               ▼
        ┌─────────────┐
        │Transformation│
        └──────┬──────┘
               ▼
            Silver
               │
               ▼
     Feature Engineering
               │
               ▼
             Gold
               │
               ▼
         PostgreSQL
               │
               ▼
          Streamlit
               │
               ▼
       Weather Risk Dashboard

          ▲
          │
       Airflow
   Orchestration
```

Le pipeline permet ainsi de transformer des données météorologiques brutes en informations exploitables pour l'analyse du **risque météorologique dans les opérations de livraison**.