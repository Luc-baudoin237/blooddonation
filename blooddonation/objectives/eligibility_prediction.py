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

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import dash

# ⚙️ Initialisation
scaler = StandardScaler()
model = RandomForestClassifier(n_estimators=100, random_state=42)
feature_names = ["Age", "Poids", "Taille", "Taux_Hb", "Genre", "Niveau_d_etude"]

# Liste descriptive pour Niveau d’étude
education_options = {
    "Aucun": 0,
    "Primaire": 1,
    "Secondaire": 2,
    "Lycée": 3,
    "Université": 4,
    "Autre": 5
}

def load_prediction_data():
    df = pd.read_csv("data/Candidat_au_don_2019_cleaned.csv", sep=";")
    df.columns = df.columns.str.strip()

    # Renommer les colonnes critiques
    df = df.rename(columns={
        "Taux_d’hémoglobine(g/dl)": "Taux_Hb",
        "ÉLIGIBILITÉ_AU_DON.": "Eligibilite"
    })

    # Nettoyage & transformation
    df["Genre"] = df["Genre"].str.lower().map({"m": 0, "f": 1}).fillna(0)
    df["Poids"] = df["Poids"].fillna(df["Poids"].mean())
    df["Taille"] = df["Taille"].fillna(df["Taille"].mean())
    df["Taux_Hb"] = df["Taux_Hb"].fillna(df["Taux_Hb"].mean())

    # Encodage du niveau d’étude
    df["Niveau_d_etude"] = df["Niveau_d_etude"].map(education_options).fillna(5)

    df = df[["Age", "Poids", "Taille", "Taux_Hb", "Genre", "Niveau_d_etude", "Eligibilite"]].dropna()

    if df.empty:
        raise ValueError("⚠️ Le DataFrame après nettoyage est vide. Vérifie les valeurs et noms des colonnes.")

    X = df[feature_names]
    y = df["Eligibilite"].astype(str).str.lower().str.strip().map(lambda x: 1 if x == "eligible" else 0)

    X_scaled = scaler.fit_transform(X)
    model.fit(X_scaled, y)

    return model

# Entraînement du modèle
model = load_prediction_data()

# 📊 Graphique d’importance
def create_importance_chart():
    importance_df = pd.DataFrame({
        "Variable": feature_names,
        "Importance": model.feature_importances_
    }).sort_values("Importance", ascending=True)

    fig = px.bar(
        importance_df,
        x="Importance",
        y="Variable",
        orientation="h",
        title="Importance des Variables pour la Prédiction"
    )
    fig.update_layout(height=500)
    return fig

# 📋 Layout de l’onglet
def get_prediction_layout():
    importance_fig = create_importance_chart()

    return html.Div([
        html.H3("🔮 Prédiction de l'Éligibilité au Don", style={"marginBottom": "30px"}),

        html.Div(className="card", children=[
            html.Label("Âge"),
            dcc.Input(id="input-age", type="number", min=18, max=100, step=1),

            html.Label("Poids (kg)"),
            dcc.Input(id="input-weight", type="number", min=30, max=200, step=0.1),

            html.Label("Taille (cm)"),
            dcc.Input(id="input-height", type="number", min=100, max=220, step=1),

            html.Label("Taux d’hémoglobine (g/dl)"),
            dcc.Input(id="input-hb", type="number", min=5, max=20, step=0.1),

            html.Label("Genre"),
            dcc.Dropdown(
                id="input-gender",
                options=[{"label": "Homme", "value": 0}, {"label": "Femme", "value": 1}],
                placeholder="Sélectionnez le genre"
            ),

            html.Label("Niveau d'étude"),
            dcc.Dropdown(
                id="input-education",
                options=[{"label": k, "value": v} for k, v in education_options.items()],
                placeholder="Sélectionnez le niveau"
            ),

            html.Br(),
            html.Button("Prédire", id="predict-button", n_clicks=0, className="btn btn-danger"),

            html.Div(id="prediction-output", style={"marginTop": "20px", "fontWeight": "bold"}),
            dcc.Graph(id="prediction-gauge", style={"marginTop": "30px"})
        ]),

        html.Div(className="graph-container", children=[
            html.Div([dcc.Graph(figure=importance_fig)], className="card")
        ])
    ], className="tab-content")

# 🔁 Callback
@dash.callback(
    Output("prediction-output", "children"),
    Output("prediction-gauge", "figure"),
    Input("predict-button", "n_clicks"),
    State("input-age", "value"),
    State("input-weight", "value"),
    State("input-height", "value"),
    State("input-hb", "value"),
    State("input-gender", "value"),
    State("input-education", "value")
)
def predict_eligibility(n_clicks, age, weight, height, hb, gender, edu):
    if None in (age, weight, height, hb, gender, edu):
        return "⚠️ Veuillez remplir tous les champs.", go.Figure()

    df_input = pd.DataFrame([[age, weight, height, hb, gender, edu]], columns=feature_names)
    scaled = scaler.transform(df_input)
    prediction = model.predict(scaled)[0]
    proba = model.predict_proba(scaled)[0][prediction]

    result = "✅ ÉLIGIBLE" if prediction == 1 else "❌ NON ÉLIGIBLE"
    interpretation = (
        f"Résultat : {result} (Confiance : {proba:.1%})\n\n"
        "→ Vous présentez les caractéristiques d’un donneur "
        f"{'éligible' if prediction == 1 else 'non éligible'} selon le modèle."
    )

    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=proba * 100,
        number={"suffix": "%"},
        title={"text": "Probabilité d'Éligibilité"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "green" if prediction == 1 else "red"},
            "steps": [
                {"range": [0, 50], "color": "#f8d7da"},
                {"range": [50, 75], "color": "#fff3cd"},
                {"range": [75, 100], "color": "#d4edda"},
            ],
        }
    ))

    return interpretation, gauge
