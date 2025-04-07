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

# donor_retention.py

# donor_retention.py

import pandas as pd
import plotly.express as px
from dash import dcc, html

def load_retention_data():
    df_cand = pd.read_csv("data/Candidat_au_don_2019_cleaned.csv", sep=";")

    # Nettoyage des colonnes
    df_cand.columns = [c.strip().lower()
                       .replace("’", "'")
                       .replace("é", "e").replace("É", "e")
                       .replace("à", "a").replace("â", "a")
                       .replace("î", "i").replace("ô", "o")
                       .replace("û", "u").replace("ù", "u") for c in df_cand.columns]

    # Conversion des dates
    df_cand["date_de_remplissage_de_la_fiche"] = pd.to_datetime(df_cand["date_de_remplissage_de_la_fiche"], errors="coerce")
    df_cand["mois"] = df_cand["date_de_remplissage_de_la_fiche"].dt.to_period("M").astype(str)

    # Nettoyage genre
    df_cand["genre"] = df_cand["genre"].str.lower()

    # Indicateurs
    df_cand["eligibilite"] = df_cand["eligibilite_au_don."].str.lower().str.strip() == "eligible"
    df_cand["fidele"] = df_cand["a-t-il_(elle)_deja_donne_le_sang"].str.lower().str.strip() == "oui"

    # Ajout tranche d'âge
    df_cand["age"] = pd.to_numeric(df_cand["age"], errors="coerce")
    df_cand = df_cand[df_cand["age"].between(15, 80)]
    df_cand["tranche_age"] = pd.cut(
        df_cand["age"],
        bins=[15, 25, 35, 45, 55, 65, 80],
        labels=["15-25", "26-35", "36-45", "46-55", "56-65", "66-80"]
    )

    return df_cand

def create_retention_charts(df):
    # 1️⃣ Donneurs reçus vs éligibles par mois
    donneurs_mois = df.groupby("mois").agg(
        total_donneurs=("date_de_remplissage_de_la_fiche", "count"),
        eligibles=("eligibilite", "sum")
    ).reset_index()

    fig1 = px.bar(
        donneurs_mois,
        x="mois",
        y=["total_donneurs", "eligibles"],
        barmode="group",
        title="📅 Donneurs Reçus et Éligibles par Mois",
        labels={"value": "Nombre", "variable": "Statut"}
    )

    # 2️⃣ Répartition des donneurs par sexe
    sexe_counts = df["genre"].value_counts().reset_index()
    sexe_counts.columns = ["sexe", "nombre"]

    fig2 = px.pie(
        sexe_counts,
        names="sexe",
        values="nombre",
        title="🚻 Répartition des Donneurs par Sexe"
    )

    # 3️⃣ Fidélité par tranche d’âge
    fidelite = df.groupby(["tranche_age", "fidele"]).size().reset_index(name="count")

    fig3 = px.bar(
        fidelite,
        x="tranche_age",
        y="count",
        color="fidele",
        barmode="group",
        title="🧬 Fidélité au Don selon les Tranches d’Âge",
        labels={"tranche_age": "Tranche d’âge", "fidele": "Fidèle"}
    )

    return fig1, fig2, fig3

def generate_retention_summary(df):
    total = df.shape[0]
    hommes = (df["genre"] == "homme").sum()
    femmes = (df["genre"] == "femme").sum()
    eligibles = df["eligibilite"].sum()
    fideles = df["fidele"].sum()

    return (
        f"📝 Durant cette période, nous avons reçu {total} donneurs "
        f"({hommes} hommes et {femmes} femmes). "
        f"{eligibles} d’entre eux étaient éligibles, "
        f"et {fideles} étaient des donneurs fidèles."
    )

def get_retention_layout(start_date=None, end_date=None):
    df = load_retention_data()

    if start_date and end_date:
        df = df[(df["date_de_remplissage_de_la_fiche"] >= start_date) & (df["date_de_remplissage_de_la_fiche"] <= end_date)]

    fig1, fig2, fig3 = create_retention_charts(df)
    commentaire = generate_retention_summary(df)

    return html.Div([
        html.H3("♻️ Fidélisation des Donneurs", style={"marginBottom": "30px"}),

        dcc.Graph(figure=fig1),
        dcc.Graph(figure=fig2),
        dcc.Graph(figure=fig3),

        html.Div([
            html.H4("📌 Interprétation"),
            html.P(commentaire, style={"fontStyle": "italic", "color": "green"})
        ], className="legend", style={"marginTop": "40px"})
    ], className="tab-content")
