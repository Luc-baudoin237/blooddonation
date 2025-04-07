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
from dash import dcc, html, Input, Output
from dash import dash_table
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import dash_bootstrap_components as dbc

# Étape 1 : Préparation des données

def prepare_clustering_data(start_date=None, end_date=None):
    df = pd.read_csv("data/Candidat_au_don_2019_cleaned.csv", sep=";")

    df.rename(columns={
        "Taux_d’hémoglobine(g/dl)": "taux_hb",
        "Genre": "genre",
        "A-t-il_(elle)_déjà_donné_le_sang": "deja_donne",
        "Age": "age",
        "Poids": "poids",
        "Taille": "taille"
    }, inplace=True)

    if start_date and end_date:
        df["date_de_remplissage_de_la_fiche"] = pd.to_datetime(df["date_de_remplissage_de_la_fiche"])
        df = df[(df["date_de_remplissage_de_la_fiche"] >= start_date) & (df["date_de_remplissage_de_la_fiche"] <= end_date)]

    df = df[["age", "poids", "taille", "genre", "deja_donne", "taux_hb"]].copy()

    for col in ["age", "poids", "taille", "taux_hb"]:
        df[col] = df[col].fillna(round(df[col].mean(), 1))

    df["genre"] = df["genre"].map({"homme": 0, "femme": 1}).fillna(0)
    df["deja_donne"] = df["deja_donne"].map({"oui": 1, "non": 0}).fillna(0)

    scaler = StandardScaler()
    df_scaled_values = scaler.fit_transform(df)

    df_scaled = pd.DataFrame(df_scaled_values, columns=[
        "Age", "Poids", "Taille", "Genre", "DonSang", "Taux_Hb"
    ])

    return df_scaled.round(3), df.round(1)

# Étape 2 : Clustering + Graphe

def create_cluster_figure(df_scaled, original_df, n_clusters=3):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(df_scaled)

    df_scaled["Cluster"] = clusters
    original_df["Cluster"] = clusters

    fig = px.scatter(
        original_df,
        x="age",
        y="taux_hb",
        color=original_df["Cluster"].astype(str),
        hover_data=["poids", "taille", "deja_donne", "genre"],
        title=f"Clustering des Donneurs (k={n_clusters})",
        labels={"Cluster": "Cluster"}
    )
    fig.update_layout(height=600)
    return fig, original_df, df_scaled

# Étape 3 : Résumé des clusters + texte dynamique

def generate_cluster_summary(original_df):
    summary = original_df.groupby("Cluster").agg({
        "age": "mean",
        "poids": "mean",
        "taille": "mean",
        "taux_hb": "mean",
        "deja_donne": lambda x: "oui" if x.mean() >= 0.5 else "non",
        "genre": lambda x: "femme" if x.mean() >= 0.5 else "homme"
    }).reset_index()

    summary.columns = [
        "Cluster", "Âge moyen", "Poids moyen", "Taille moyenne",
        "Taux Hb moyen", "Don de sang dominant", "Genre dominant"
    ]

    ideal_cluster_row = summary.sort_values("Taux Hb moyen", ascending=False).iloc[0]
    ideal_description = (
        f"\U0001F4A1 Profil idéal : donneur typique du cluster avec le plus fort taux d’hémoglobine : "
        f"{ideal_cluster_row['Genre dominant']} de {int(round(ideal_cluster_row['Âge moyen']))} ans, "
        f"{int(round(ideal_cluster_row['Poids moyen']))} kg, {int(round(ideal_cluster_row['Taille moyenne']))} cm, "
        f"taux Hb {round(ideal_cluster_row['Taux Hb moyen'], 1)} g/dL, "
        f"ayant {'déjà' if ideal_cluster_row['Don de sang dominant'] == 'oui' else 'jamais'} donné son sang."
    )

    return summary.round(1), ideal_description

# Étape 4 : Layout du composant Dash

def get_clustering_layout(start_date=None, end_date=None):
    df_scaled, original_df = prepare_clustering_data(start_date, end_date)
    fig, updated_df, scaled_df = create_cluster_figure(df_scaled.copy(), original_df.copy(), 3)
    summary_df, ideal_text = generate_cluster_summary(updated_df)
    columns = [{"name": i, "id": i} for i in summary_df.columns]

    layout = html.Div([
        html.H3("Clustering des Donneurs (Profilage Automatique - 3 groupes)"),
        html.Div(className="graph-container", children=[dcc.Graph(id="clustering-graph", figure=fig)]),
        html.Div(className="card", children=[
            html.H4("Résumé des Clusters"),
            dash_table.DataTable(
                data=summary_df.to_dict("records"),
                columns=columns,
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "center"},
                style_header={"backgroundColor": "#f2f2f2", "fontWeight": "bold"},
            )
        ], style={"marginTop": "40px", "padding": "20px", "borderRadius": "10px", "boxShadow": "2px 2px 10px lightgrey"}),
        html.Div(className="legend", children=[
            html.H4("Interprétation"),
            html.P("Chaque point représente un donneur selon son âge et taux d’hémoglobine."),
            html.P("Les couleurs correspondent aux groupes identifiés automatiquement."),
            html.Hr(),
            html.Div(ideal_text, id="ideal-profile-text", style={"fontStyle": "italic", "marginTop": "10px", "color": "green"})
        ])
    ])

    return layout
