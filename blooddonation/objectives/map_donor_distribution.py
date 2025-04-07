# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3 
# ---

# +
# map_donor_distribution.py
import os
import dash
import plotly.express as px
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from dash import dcc, html
from dash.dependencies import Input, Output
import time

def geocode_location(location):
    geolocator = Nominatim(user_agent="blood_donation_app")
    try:
        time.sleep(2)  # éviter les blocages
        geo = geolocator.geocode(location + ", Cameroun")
        return (geo.latitude, geo.longitude) if geo else (None, None)
    except:
        return (None, None)

# Fonction de nettoyage des noms d'arrondissements
def nettoyer_arrondissement(val):
    if pd.isna(val):
        return "Douala 1"
    
    val = val.strip().lower()

    douala_1 = ["douala", "douala non precise", "douala (non précisé )", "pas précisé", "pas precise", 
        "pas precise ", "pas mentionné", "non précisé", "non precise", "non precisé", 
        "ras", "ras ", "r a s", "r a s ","r a s ", "dcankongmondo", "deido","Pas Mentionne"]
    douala_2 = ["douala 2"]
    douala_3 = ["douala 3", "bomono ba mbegue", "oyack", "ngodi bakoko", "ngodi bakoko "]
    douala_4 = ["douala 4", "boko"]
    douala_5 = ["douala 5"]
    douala_6 = ["douala 6"]

    mapping = {
        **dict.fromkeys(douala_1, "Douala 1"),
        **dict.fromkeys(douala_2, "Douala 2"),
        **dict.fromkeys(douala_3, "Douala 3"),
        **dict.fromkeys(douala_4, "Douala 4"),
        **dict.fromkeys(douala_5, "Douala 5"),
        **dict.fromkeys(douala_6, "Douala 6"),
        "bafoussam": "Bafoussam",
        "dschang": "Dschang",
        "buea": "Buea",
        "kribi": "Kribi",
        "njombe": "Njombe",
        "tiko": "Tiko",
        "edea": "Edea",
        "manjo": "Manjo",
        "west": "Région de l'Ouest",
        "yaoundé": "Yaoundé",
        "nkouabang": "Yaoundé",
        "yaounde": "Yaoundé",
        "meiganga": "Meiganga",
        "batie": "Batié",
        "sud ouest tombel": "Tombel",
        "limbe": "Limbe",
        "limbe ": "Limbe"
    }

    return mapping.get(val, val.title())


def load_and_prepare_data(start_date=None, end_date=None):
    """Charge et prépare les données pour la cartographie avec mise à jour intelligente du cache"""
    df = pd.read_csv('data/Candidat_au_don_2019_cleaned.csv', sep=';')
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("’", "'")

    df['arrondissement_de_résidence'] = df['arrondissement_de_résidence'].apply(nettoyer_arrondissement)
    cache_path = 'data/geocoded_coords.csv'

    # Charger le cache s’il existe, sinon on crée un DataFrame vide
    if os.path.exists(cache_path):
        coords_df = pd.read_csv(cache_path)
    else:
        coords_df = pd.DataFrame(columns=["arrondissement_de_résidence", "latitude", "longitude"])

    # Trouver les nouveaux arrondissements à géocoder
    arrondissements_existants = set(coords_df["arrondissement_de_résidence"].dropna())
    arrondissements_dans_data = set(df["arrondissement_de_résidence"].dropna())
    nouveaux = list(arrondissements_dans_data - arrondissements_existants)

    # Géocoder uniquement les nouveaux
    if nouveaux:
        print(f"🔍 Géocodage de {len(nouveaux)} nouvel(s) arrondissement(s)...")
        nouveaux_coords = []
        for loc in nouveaux:
            lat, lon = geocode_location(loc)
            nouveaux_coords.append({
                "arrondissement_de_résidence": loc,
                "latitude": lat,
                "longitude": lon
            })
        nouveaux_df = pd.DataFrame(nouveaux_coords)
        coords_df = pd.concat([coords_df, nouveaux_df], ignore_index=True)
        coords_df.to_csv(cache_path, index=False)
        print("✅ Cache mis à jour.")

    # Fusion coordonnées
    df = pd.merge(df, coords_df, on='arrondissement_de_résidence', how='left')
    df = df.dropna(subset=['latitude', 'longitude'])

    # Agrégation
    district_stats = df.groupby('arrondissement_de_résidence').agg(
        total_candidats=('éligibilité_au_don.', 'count'),
        pourcentage_eligibles=('éligibilité_au_don.', lambda x: (x == 'eligible').mean() * 100),
        nombre_hommes=('genre', lambda x: (x == 'homme').sum()),
        latitude=('latitude', 'first'),
        longitude=('longitude', 'first')
    ).reset_index()
    print("✅ Données géographiques chargées :", district_stats.shape)
    return df, district_stats




def create_folium_map(df):
    """Crée une carte Folium avec des marqueurs pour chaque donneur"""
    donor_map = folium.Map(location=[3.848, 11.502], zoom_start=6)
    for _, row in df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Profession : {row.get('profession', 'N/A')}<br>Éligible : {row.get('éligibilité_au_don.', 'N/A')}"
        ).add_to(donor_map)
    return donor_map._repr_html_()

def get_map_layout(start_date=None, end_date=None):


    df_geo, district_stats = load_and_prepare_data(start_date, end_date)

       
    # Calcul des KPI
    total_donneurs = len(df_geo)
    taux_eligibilite = round((df_geo["éligibilité_au_don."] == "eligible").mean() * 100, 1)
    total_hommes = (df_geo["genre"] == "homme").sum()
    total_femmes = (df_geo["genre"] == "femme").sum()
    
    # Carte Folium HTML
    folium_map_html = create_folium_map(df_geo)

    return html.Div([
        html.H3('Distribution Géographique des Donneurs'),

        dcc.DatePickerRange(
            id='date-picker-range',
            display_format='DD-MM-YYYY',
            start_date_placeholder_text='Date début',
            end_date_placeholder_text='Date fin',
            style={"margin-bottom": "20px"}
        ),

        
        # --- KPI Cards ---
        html.Div([
            html.Div([
                html.H4("🧍‍ Total donneurs"),
                html.H2(f"{total_donneurs}")
            ], className="card"),
            html.Div([
                html.H4("🩸 Taux moyen d’éligibilité"),
                html.H2(f"{taux_eligibilite}%")
            ], className="card"),
            html.Div([
                html.H4("👨 Hommes / 👩 Femmes"),
                html.H2(f"{total_hommes} / {total_femmes}")
            ], className="card"),
        ], style={"display": "flex", "gap": "20px"}),

        html.Br(),

        # --- Carte Folium ---
        html.Div([
            html.Iframe(
                srcDoc=folium_map_html,
                width="100%",
                height="600",
                style={"border": "none"}
            )
        ], className="graph-container"),

        html.Div([
            html.H4('Légende', style={"font-size": "16px", "margin-bottom": "5px"}),
            html.P("Cette carte montre les localisations des donneurs selon leur arrondissement de résidence.",
               style={"font-size": "14px", "margin": "0"}),
            html.P("Clique sur un marqueur pour voir la profession et l'éligibilité.",
           style={"font-size": "14px", "margin": "0"})
        ], className="legend", style={
            "background-color": "#f9f9f9",
            "padding": "10px",
            "border-radius": "5px",
            "margin-top": "20px",
            "font-size": "14px",
            "max-width": "600px"
        })
    ])
        
