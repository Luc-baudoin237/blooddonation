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
# central_app.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Initialisation de l'application
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Analyse des Donnes de Sang"

# Importation des modules fonctionnels
from objectives.map_donor_distribution import get_map_layout
from objectives.health_conditions import get_health_conditions_layout
from objectives.donor_clustering import get_clustering_layout
from objectives.campaign_effectiveness import get_campaign_layout
from objectives.donor_retention import get_retention_layout
from objectives.sentiment_analysis import get_sentiment_layout
from objectives.eligibility_prediction import get_prediction_layout


# Sidebar style
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "280px",
    "padding": "20px",
    "background-color": "#f8f9fa",
    "box-shadow": "0 0 10px rgba(0,0,0,0.1)",
}
# Layout principal avec onglets
app.layout = html.Div([
    dcc.Tabs(
        id='tabs',
        value='map',
        children=[
            dcc.Tab(label='Distribution des Donneurs', value='map'),
            dcc.Tab(label='Conditions de Santé', value='health'),
            dcc.Tab(label='Clustering des Donneurs', value='clustering'),
            dcc.Tab(label='Efficacité des Campagnes', value='campaign'),
            dcc.Tab(label='Fidélisation', value='retention'),
            dcc.Tab(label='Analyse des Sentiments', value='sentiment'),
            dcc.Tab(label='Prédiction d\'Éligibilité', value='prediction')
        ]
    ),
    html.Div(id='tabs-content')
])

@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):
    if tab == 'map':
        return get_map_layout()
    elif tab == 'health':
        return get_health_conditions_layout()
    elif tab == 'clustering':
        return get_clustering_layout()
    elif tab == 'campaign':
        return get_campaign_layout()
    elif tab == 'retention':
        return get_retention_layout()
    elif tab == 'sentiment':
        return get_sentiment_layout()
    elif tab == 'prediction':
        return get_prediction_layout()

if __name__ == '__main__':
    app.run(debug=True)
