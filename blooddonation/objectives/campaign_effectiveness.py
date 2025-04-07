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
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Chargement des données
candidats_df = pd.read_csv("data/Candidat_au_don_2019_cleaned.csv", sep=";")
donneurs_df = pd.read_csv("data/Donneurs_2019_cleaned.csv", sep=";")

# Nettoyage donneurs_df
donneurs_df.columns = donneurs_df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("’", "'")
donneurs_df["horodateur"] = pd.to_datetime(donneurs_df["horodateur"], errors="coerce")
donneurs_df = donneurs_df.dropna(subset=["horodateur"])
donneurs_df["jour"] = donneurs_df["horodateur"].dt.date

donneurs_df["jour_semaine"] = donneurs_df["horodateur"].dt.day_name()
donneurs_df["mois"] = donneurs_df["horodateur"].dt.month

donneurs_df["type_de_donation_"] = donneurs_df["type_de_donation_"].fillna("Autres")
donneurs_df["type_de_donation_"] = donneurs_df["type_de_donation_"].replace({"B": "Bénévole", "F": "Familial", "": "Autres"})

# Nettoyage candidats_df pour le taux de retour
donneurs_deja = candidats_df["A-t-il_(elle)_déjà_donné_le_sang"].str.lower().map({"oui": 1, "non": 0}).fillna(0)
taux_retour = round((donneurs_deja.sum() / len(donneurs_deja)) * 100, 1)

# Fonction layout Dash
def get_campaign_layout():

    # KPI
    total_dons = len(donneurs_df)
    total_poches = total_dons

    # Graphique 1 : dons par jour
    dons_jour = donneurs_df.groupby("jour")["type_de_donation_"].count().reset_index(name="Nombre de Dons")
    fig_journalier = px.line(
        dons_jour,
        x="jour",
        y="Nombre de Dons",
        title="\ud83d\uddd3\ufe0f Nombre de Dons par Jour",
        markers=True
    )

    # Graphique 2 : groupes sanguins
    groupes = donneurs_df.groupby("groupe_sanguin_abo_/_rhesus_")["type_de_donation_"].count().reset_index(name="Dons")
    groupes = groupes.sort_values("Dons", ascending=False)
    fig_groupes = px.bar(
        groupes,
        x="groupe_sanguin_abo_/_rhesus_",
        y="Dons",
        title="\ud83e\uddea Distribution des Groupes Sanguins",
        color="Dons",
        text_auto=True
    )

    # Graphique 3 : jours de la semaine
    jours = donneurs_df.groupby("jour_semaine")["type_de_donation_"].count().reset_index(name="Nombre de Dons")
    jours = jours.sort_values("Nombre de Dons", ascending=False)
    fig_jours = px.bar(
        jours,
        x="jour_semaine",
        y="Nombre de Dons",
        title="\ud83d\udc65 Dons par Jour de la Semaine",
        color="Nombre de Dons",
        text_auto=True
    )

    return html.Div([
        html.H3("\ud83d\udcca Analyse de l'Efficacité des Campagnes de Don"),

        # KPIs
        html.Div([
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("Poches Disponibles", className="card-title"),
                        html.H2(f"{total_poches}", className="card-text")
                    ])
                ], color="success", inverse=True), width=3),

                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("Taux de Retour", className="card-title"),
                        html.H2(f"{taux_retour}%", className="card-text")
                    ])
                ], color="info", inverse=True), width=3),

                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H5("Total Donneurs", className="card-title"),
                        html.H2(f"{total_dons}", className="card-text")
                    ])
                ], color="primary", inverse=True), width=3)
            ], justify="around", style={"marginBottom": "40px"})
        ]),

        dcc.Graph(figure=fig_journalier),
        dcc.Graph(figure=fig_groupes),
        dcc.Graph(figure=fig_jours),

        html.Div([
            html.H4("\ud83d\udd0d Interprétation"),
            html.P("Ces visualisations permettent de détecter les pics de collecte, les groupes sanguins les plus fréquents et la dynamique des dons par jour de semaine."),
            html.P("Le taux de retour est estimé à partir des donneurs ayant déclaré avoir déjà donné leur sang."),
        ], className="legend")
    ])