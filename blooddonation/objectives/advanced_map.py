# objectives/advanced_map.py
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

def load_data():
    """
    Load the geocoded blood donation data.
    Expected columns: 'lat', 'lon', 'ÉLIGIBILITÉ_AU_DON.', 'Age', 'Genre_', 'Taux_d’hémoglobine_'
    """
    df = pd.read_csv("data/blood_data_geocoded.csv")
    # Create a boolean eligibility column (assumes eligible entries are marked with "Eligible")
    df['eligible'] = df['ÉLIGIBILITÉ_AU_DON.'].str.strip().str.lower() == "eligible"
    # Drop rows with missing geographic coordinates
    df = df.dropna(subset=["lat", "lon"])
    return df

def get_advanced_map_layout(start_date=None, end_date=None):
    """
    Returns a Dash layout for the advanced map page.
    The start_date and end_date parameters are provided for potential date filtering.
    """
    # Load data to build initial filter ranges
    df = load_data()
    
    layout = dbc.Container([
        dbc.Row(html.H1("Advanced Donor Map with Clustering and Interactive Filters"), className="my-3"),
        dbc.Row([
            dbc.Col([
                html.H4("Filters"),
                html.Label("Age Range"),
                dcc.RangeSlider(
                    id="age-slider",
                    min=int(df["Age"].min()),
                    max=int(df["Age"].max()),
                    value=[int(df["Age"].min()), int(df["Age"].max())],
                    marks={i: str(i) for i in range(int(df["Age"].min()), int(df["Age"].max())+1, 5)}
                ),
                html.Br(),
                html.Label("Gender"),
                dcc.Dropdown(
                    id="gender-dropdown",
                    options=[{"label": g, "value": g} for g in sorted(df["Genre_"].unique())],
                    value=sorted(df["Genre_"].unique()),
                    multi=True
                ),
                html.Br(),
                html.Label("Eligibility"),
                dcc.RadioItems(
                    id="eligibility-radio",
                    options=[
                        {"label": "All", "value": "all"},
                        {"label": "Eligible", "value": "eligible"},
                        {"label": "Not Eligible", "value": "not_eligible"}
                    ],
                    value="all",
                    labelStyle={"display": "inline-block", "margin-right": "10px"}
                )
            ], width=3),
            dbc.Col([
                dcc.Graph(id="advanced-map-graph")
            ], width=9)
        ])
    ], fluid=True)
    
    return layout

def init_callbacks(app):
    @app.callback(
        Output("advanced-map-graph", "figure"),
        [Input("age-slider", "value"),
         Input("gender-dropdown", "value"),
         Input("eligibility-radio", "value")]
    )
    def update_map(age_range, genders, eligibility_filter):
        df = load_data()
        # Filter by Age and Gender
        filtered = df[(df["Age"] >= age_range[0]) & (df["Age"] <= age_range[1])]
        filtered = filtered[filtered["Genre_"].isin(genders)]
        
        if eligibility_filter == "eligible":
            filtered = filtered[filtered["eligible"] == True]
        elif eligibility_filter == "not_eligible":
            filtered = filtered[filtered["eligible"] == False]
        
        # Create a scatter mapbox with advanced features
        fig = px.scatter_mapbox(
            filtered,
            lat="lat",
            lon="lon",
            hover_name="Genre_",
            hover_data={"Age": True, "Taux_d’hémoglobine_": ":.1f", "eligible": True},
            color="eligible",
            color_discrete_map={True: "#2ecc71", False: "#e74c3c"},
            size="Taux_d’hémoglobine_",
            size_max=15,
            zoom=5,
            height=700
        )
        
        # Enable clustering of points with custom settings
        fig.update_traces(
            cluster={
                'enabled': True,
                'size': 20,
                'step': [10, 30, 50],
                'color': 'rgba(231, 76, 60, 0.3)'
            }
        )
        
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_center={"lat": df["lat"].mean(), "lon": df["lon"].mean()},
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

if __name__ == "__main__":
    # For standalone testing:
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = get_advanced_map_layout()
    init_callbacks(app)
    app.run(debug=True)