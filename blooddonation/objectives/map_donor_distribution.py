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

import os
import time
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output, State
from geopy.geocoders import Nominatim

# ------------------------
# Data Loading, Cleaning and Geocoding
# ------------------------
def geocode_location(location):
    geolocator = Nominatim(user_agent="blood_donation_app")
    try:
        time.sleep(2)  # avoid rate limiting
        geo = geolocator.geocode(location + ", Cameroun")
        return (geo.latitude, geo.longitude) if geo else (None, None)
    except Exception as e:
        return (None, None)

def nettoyer_arrondissement(val):
    if pd.isna(val):
        return "Douala 1"
    val = val.strip().lower()
    douala_1 = ["douala", "douala non precise", "douala (non précisé )", "pas précisé", "pas precise", 
                "pas precise ", "pas mentionné", "non précisé", "non precise", "non precisé", 
                "ras", "ras ", "r a s", "r a s ","r a s ", "dcankongmondo", "deido", "pas mentionne"]
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

def load_and_prepare_data():
    """Load candidate data, clean district names and merge geocoded coordinates."""
    data_path = os.path.join("data", "Candidat_au_don_2019_cleaned.csv")
    df = pd.read_csv(data_path, sep=';')
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("’", "'")
    
    # Clean district names
    df['arrondissement_de_résidence'] = df['arrondissement_de_résidence'].apply(nettoyer_arrondissement)
    
    # Create eligibility column (assuming 'éligibilité_au_don.' contains strings like "eligible")
    df['eligible'] = df['éligibilité_au_don.'].str.lower().str.strip() == 'eligible'
    
    # Geocode caching
    cache_path = os.path.join("data", "geocoded_coords.csv")
    if os.path.exists(cache_path):
        coords_df = pd.read_csv(cache_path)
    else:
        coords_df = pd.DataFrame(columns=["arrondissement_de_résidence", "latitude", "longitude"])
    
    # Identify new districts that need geocoding
    existing = set(coords_df["arrondissement_de_résidence"].dropna())
    districts = set(df["arrondissement_de_résidence"].dropna())
    new_districts = list(districts - existing)
    
    if new_districts:
        print(f"🔍 Geocoding {len(new_districts)} new district(s)...")
        new_coords = []
        for loc in new_districts:
            lat, lon = geocode_location(loc)
            new_coords.append({
                "arrondissement_de_résidence": loc,
                "latitude": lat,
                "longitude": lon
            })
        new_coords_df = pd.DataFrame(new_coords)
        coords_df = pd.concat([coords_df, new_coords_df], ignore_index=True)
        coords_df.to_csv(cache_path, index=False)
        print("✅ Cache updated.")
    
    # Merge coordinates into main dataframe and drop rows without coordinates
    df_geo = pd.merge(df, coords_df, on='arrondissement_de_résidence', how='left')
    df_geo = df_geo.dropna(subset=['latitude', 'longitude'])
    return df_geo

# ------------------------
# Build the Map Layout
# ------------------------
def get_map_layout(start_date, end_date):
    """
    Returns the layout for the donor map page.
    The start_date and end_date parameters can be used for filtering if needed.
    """
    # Load data
    df_geo = load_and_prepare_data()
    
    # For demonstration, we use the following interactive filters.
    # You can adjust the filtering logic based on start_date, end_date, etc.
    layout = dbc.Container([
        dbc.Row(html.H1("🌍 Advanced Donor Distribution Analysis"), className="my-3"),
        
        dbc.Row([
            dbc.Col([
                html.H4("Data Filters"),
                html.Label("District"),
                dcc.Dropdown(
                    id='district-filter',
                    options=[{'label': d, 'value': d} for d in sorted(df_geo['arrondissement_de_résidence'].unique())],
                    value=sorted(df_geo['arrondissement_de_résidence'].unique()),
                    multi=True
                ),
                html.Br(),
                html.Label("Gender"),
                dcc.Dropdown(
                    id='gender-filter',
                    options=[{'label': gen.title(), 'value': gen} for gen in sorted(df_geo['genre'].unique())],
                    value=sorted(df_geo['genre'].unique()),
                    multi=True
                ),
            ], width=3),
            
            dbc.Col([
                dcc.Graph(id='map-graph'),
                html.Div(id='metrics-div', className="my-3")
            ], width=9)
        ]),
        
        dbc.Row(
            dbc.Button("Toggle Deep Analysis", id="toggle-collapse", n_clicks=0, className="mt-3")
        ),
        
        dbc.Row(
            dbc.Collapse(
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Deep Analysis"),
                        html.Div(id='desc-stats', className="mb-3"),
                        dcc.Graph(id='district-bar'),
                        dcc.Graph(id='gender-pie')
                    ])
                ),
                id='collapse',
                is_open=False
            )
        )
    ], fluid=True)
    
    return layout

# ------------------------
# Callbacks for the Map Page
# ------------------------
# These callbacks can be registered if you run this page independently or via a central app.
# In the central app, you may include these callbacks in an "init_callbacks" function.
def init_callbacks(app):
    @app.callback(
        [Output('map-graph', 'figure'),
         Output('metrics-div', 'children'),
         Output('desc-stats', 'children'),
         Output('district-bar', 'figure'),
         Output('gender-pie', 'figure')],
        [Input('district-filter', 'value'),
         Input('gender-filter', 'value')]
    )
    def update_analysis(selected_districts, selected_genders):
        df_geo = load_and_prepare_data()
        filtered_df = df_geo[
            (df_geo['arrondissement_de_résidence'].isin(selected_districts)) &
            (df_geo['genre'].isin(selected_genders))
        ]
        
        # Build interactive map
        map_fig = px.scatter_mapbox(
            filtered_df,
            lat="latitude",
            lon="longitude",
            hover_name="arrondissement_de_résidence",
            hover_data={
                "genre": True,
                "éligibilité_au_don.": True
            },
            color="eligible",
            color_discrete_map={True: "#2ecc71", False: "#e74c3c"},
            zoom=6,
            height=700
        )
        map_fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_center={"lat": 4.0, "lon": 11.0},
            margin={"r":0, "t":40, "l":0, "b":0},
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Compute key metrics
        total_candidates = len(filtered_df)
        eligibility_rate = f"{(filtered_df['eligible'].mean()*100):.1f}%" if total_candidates > 0 else "N/A"
        total_males = (filtered_df['genre'] == 'homme').sum()
        total_females = (filtered_df['genre'] == 'femme').sum()
        metrics = html.Div([
            html.H4("Key Metrics"),
            html.P(f"Total Candidates: {total_candidates}"),
            html.P(f"Eligibility Rate: {eligibility_rate}"),
            html.P(f"Gender Distribution: ♂️ {total_males} / ♀️ {total_females}")
        ])
        
        # Descriptive statistics (if available numeric data, e.g., age)
        if 'age' in filtered_df.columns:
            desc_table = filtered_df[['age']].describe().round(2).to_html(classes="table table-striped")
            desc_stats = html.Div([
                html.H5("Descriptive Statistics (Age)"),
                html.Div(dcc.Markdown(desc_table), style={'overflowX': 'auto'})
            ])
        else:
            desc_stats = html.Div([
                html.H5("Descriptive Statistics"),
                html.P("No numeric data available for analysis.")
            ])
        
        # Bar chart: count by district
        district_counts = filtered_df['arrondissement_de_résidence'].value_counts().reset_index()
        district_counts.columns = ['District', 'Count']
        district_bar = px.bar(district_counts, x='District', y='Count', title="Candidates by District")
        
        # Pie chart: Gender distribution
        gender_counts = filtered_df['genre'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        gender_pie = px.pie(gender_counts, values='Count', names='Gender', title="Gender Distribution")
        
        return map_fig, metrics, desc_stats, district_bar, gender_pie

    @app.callback(
        Output("collapse", "is_open"),
        [Input("toggle-collapse", "n_clicks")],
        [State("collapse", "is_open")]
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

# If running this module directly, initialize a Dash app and callbacks.
if __name__ == "__main__":
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = get_map_layout(None, None)
    init_callbacks(app)
    app.run_server(debug=True)
