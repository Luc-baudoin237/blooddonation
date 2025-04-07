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
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output

# Initialisation avec Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
app.title = "HEMOBOARD"

# Importation des pages
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

# Content style
CONTENT_STYLE = {
    "margin-left": "300px",
    "margin-right": "20px",
    "padding": "20px 10px",
}

# Sidebar
sidebar = html.Div(
    [
        html.Img(src="/assets/banner.png", style={"width": "100%", "border-radius": "10px"}),
        html.H3("HEMOBOARD-DSWB", style={"color": "#c0392b", "margin-top": "20px", "font-weight": "bold"}),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("🗺️ Donor Map", href="/", active="exact"),
                dbc.NavLink("🩺 Health Conditions", href="/health", active="exact"),
                dbc.NavLink("👥 Clustering", href="/clustering", active="exact"),
                dbc.NavLink("📊 Campaigns", href="/campaign", active="exact"),
                dbc.NavLink("♻️ Retention", href="/retention", active="exact"),
                dbc.NavLink("💬 Sentiments", href="/sentiment", active="exact"),
                dbc.NavLink("🔮 Eligibility Prediction", href="/prediction", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# App layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    html.Div(id="page-content", style=CONTENT_STYLE),
    html.Div([
        html.Img(src="/assets/down.png", style={
            "position": "fixed",
            "left": "0px",
            "bottom": "0px",
            "width": "280px",  # même largeur que la sidebar
            "zIndex": "999",
            "borderTopRightRadius": "15px"
        }),
        html.Div("down", style={
            "position": "fixed",
            "bottom": "5px",
            "left": "15px",
            "color": "#c0392b",
            "fontWeight": "bold",
            "fontSize": "14px",
            "zIndex": "1000"
        })
    ])
])

# Routing
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.Div([
            html.Div([
                html.Label("📅 Filtrer par date de remplissage :", style={"font-weight": "bold", "margin-right": "10px"}),
                dcc.DatePickerRange(
                    id='date-range-picker',
                    start_date_placeholder_text="Début",
                    end_date_placeholder_text="Fin",
                    display_format='YYYY-MM-DD',
                    style={"padding": "10px"}
                )
            ], style={"margin-bottom": "20px", "display": "flex", "align-items": "center", "gap": "10px"}),

            html.Div(id="map-container", children=get_map_layout(None, None))
        ])

    elif pathname == "/health":
        return html.Div([
            html.Div([
                html.Label("📅 Filtrer par date de remplissage :", style={"font-weight": "bold", "margin-right": "10px"}),
                dcc.DatePickerRange(
                    id='health-date-picker',
                    start_date_placeholder_text="Début",
                    end_date_placeholder_text="Fin",
                    display_format='YYYY-MM-DD',
                    style={"padding": "10px"}
                )
            ], style={"margin-bottom": "20px", "display": "flex", "align-items": "center", "gap": "10px"}),

            html.Div(id="health-container", children=get_health_conditions_layout(None, None))
        ])

    elif pathname == "/clustering":
        return html.Div([
            html.Div([
                html.Label("📅 Filtrer par date de remplissage :", style={"font-weight": "bold", "margin-right": "10px"}),
                dcc.DatePickerRange(
                    id='cluster-date-picker',
                    start_date_placeholder_text="Début",
                    end_date_placeholder_text="Fin",
                    display_format='YYYY-MM-DD',
                    style={"padding": "10px"}
                )
            ], style={"margin-bottom": "20px", "display": "flex", "align-items": "center", "gap": "10px"}),

            html.Div(id="cluster-container")
        ])
    elif pathname == "/campaign":
        return get_campaign_layout()
    elif pathname == "/retention":
        return html.Div([
            html.Div([
                html.Label("📅 Filtrer par date :", style={"font-weight": "bold", "margin-right": "10px"}),
                dcc.DatePickerRange(
                    id='retention-date-picker',
                    start_date_placeholder_text="Début",
                    end_date_placeholder_text="Fin",
                    display_format='YYYY-MM-DD',
                    style={"padding": "10px"}
                )
            ], style={"margin-bottom": "20px", "display": "flex", "align-items": "center", "gap": "10px"}),
    
            html.Div(id="retention-container", children=get_retention_layout(None, None))
        ])
        

    elif pathname == "/sentiment":
        return get_sentiment_layout()
    elif pathname == "/prediction":
        return get_prediction_layout()
    else:
        return html.H1("404: Page introuvable")

@app.callback(
    Output("map-container", "children"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date")
)
def update_map_layout(start_date, end_date):
    return get_map_layout(start_date, end_date)

@app.callback(
    Output("health-container", "children"),
    Input("health-date-picker", "start_date"),
    Input("health-date-picker", "end_date")
)
def update_health_layout(start_date, end_date):
    return get_health_conditions_layout(start_date, end_date)

@app.callback(
    Output("cluster-container", "children"),
    Input("cluster-date-picker", "start_date"),
    Input("cluster-date-picker", "end_date")
)
def update_cluster_layout(start_date, end_date):
    return get_clustering_layout(start_date, end_date)

@app.callback(
    Output("retention-container", "children"),
    Input("retention-date-picker", "start_date"),
    Input("retention-date-picker", "end_date")
)
def update_retention_layout(start_date, end_date):
    return get_retention_layout(start_date, end_date)

if __name__ == "__main__":
    app.run(debug=True)