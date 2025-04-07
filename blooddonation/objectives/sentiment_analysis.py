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
from textblob import TextBlob

def load_sentiment_data():
    """Charge les commentaires et calcule les sentiments"""
    df = pd.read_csv("data/Candidat_au_don_2019_cleaned.csv", sep=";")
    df.columns = df.columns.str.strip()

    # Ne garder que les lignes avec un texte utile
    df = df.dropna(subset=["Si_autres_raison_préciser"])
    df = df[df["Si_autres_raison_préciser"].str.strip() != ""]

    # Fonction pour catégoriser le sentiment
    def detect_sentiment(text):
        polarity = TextBlob(str(text)).sentiment.polarity
        if polarity > 0.1:
            return "Positif"
        elif polarity < -0.1:
            return "Négatif"
        else:
            return "Neutre"

    df["Sentiment"] = df["Si_autres_raison_préciser"].apply(detect_sentiment)

    # Sécurité si "Profession" est vide
    df["Profession"] = df["Profession"].fillna("Inconnu")

    # Agrégation pour bar chart
    sentiment_stats = df.groupby(["Profession", "Sentiment"]).size().reset_index(name="Count")
    sentiment_global = df["Sentiment"].value_counts().reset_index()
    sentiment_global.columns = ["Sentiment", "Count"]

    return sentiment_stats, sentiment_global

def create_sentiment_charts(df_by_profession, df_global):
    """Crée les visualisations des sentiments"""
    fig_bar = px.bar(
        df_by_profession,
        x="Profession",
        y="Count",
        color="Sentiment",
        title="Analyse des Sentiments par Profession",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_bar.update_layout(xaxis_title="Profession", yaxis_title="Nombre")

    fig_pie = px.pie(
        df_global,
        names="Sentiment",
        values="Count",
        title="Répartition Globale des Sentiments",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    return fig_bar, fig_pie

def get_sentiment_layout():
    df_by_profession, df_global = load_sentiment_data()
    fig_bar, fig_pie = create_sentiment_charts(df_by_profession, df_global)

    return html.Div([
        html.H3("Analyse des Sentiments des Donneurs"),

        html.Div(className="graph-container", children=[
            html.Div([dcc.Graph(figure=fig_bar)], className="card"),
            html.Div([dcc.Graph(figure=fig_pie)], className="card")
        ]),

        html.Div(className="legend", children=[
            html.H4("Interprétation"),
            html.P("Le graphique à barres montre les sentiments exprimés par les donneurs selon leur profession."),
            html.P("Le graphique circulaire illustre la répartition globale des retours positifs, neutres et négatifs."),
        ])
    ], className="tab-content")

