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
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def load_health_data(start_date=None, end_date=None):
    df = pd.read_csv("data/Candidat_au_don_2019_cleaned.csv", sep=";")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("’", "'")

    df["date_de_remplissage_de_la_fiche"] = pd.to_datetime(df["date_de_remplissage_de_la_fiche"], errors='coerce')

    if start_date is not None and end_date is not None:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df = df[(df["date_de_remplissage_de_la_fiche"] >= start_date) & (df["date_de_remplissage_de_la_fiche"] <= end_date)]

    df["eligibilite_statut"] = df["éligibilité_au_don."].str.strip().str.lower()

    total_cols = [
        'raison_de_non-eligibilité_totale__[hypertendus]',
        'raison_de_non-eligibilité_totale__[diabétique]',
        'raison_de_non-eligibilité_totale__[porteur(hiv,hbs,hcv)]',
        'raison_de_non-eligibilité_totale__[asthmatiques]'
    ]

    temp_cols = [
        col for col in df.columns if col.startswith("raison_indisponibilité__") or col.startswith("raison_de_l'indisponibilité_de_la_femme_")
    ]

    total_cols = [col for col in total_cols if col in df.columns]
    temp_cols = [col for col in temp_cols if col in df.columns]

    return df, total_cols, temp_cols

def create_eligibility_pie(df):
    counts = df['eligibilite_statut'].value_counts().reset_index()
    counts.columns = ['Statut', 'Effectif']
    counts['Pourcentage'] = round(counts['Effectif'] / counts['Effectif'].sum() * 100, 1)
    counts['Label'] = counts['Statut'] + '<br>' + counts['Effectif'].astype(str) 

    color_map = {
        'eligible': 'green',
        'temporairement noneligible': 'orange',
        'definitivement noneligible': 'red'
    }

    fig = px.pie(
        counts,
        names='Label',
        values='Effectif',
        title="Répartition des Statuts d'Éligibilité",
        hole=0.3,
        color='Statut',
        color_discrete_map=color_map
    )
    fig.update_traces(textinfo='label+percent')
    fig.update_layout(
        width=1100,
        height=650,
        margin=dict(l=50, r=50, t=90, b=80),
        legend=dict(orientation="h", y=1.2, x=1.0, xanchor='right', yanchor='top')
    )
    return fig

def create_reason_bars(df, cols, title):
    reasons = {}
    for col in cols:
        if col in df.columns:
            count = df[col].apply(lambda x: 1 if str(x).strip().lower() == "oui" else 0).sum()
            label = col.split("[")[-1].replace("]", "").capitalize()
            reasons[label] = count
    bar_df = pd.DataFrame({"Raison": reasons.keys(), "Nombre": reasons.values()})
    bar_fig = px.bar(bar_df, x="Nombre", y="Raison", orientation="h", title=title, text="Nombre")
    bar_fig.update_traces(textposition="outside")
    bar_fig.update_layout(
        height=400,
        margin=dict(l=180),
        paper_bgcolor='white',
        plot_bgcolor='white',
        title_font=dict(size=18, color='#333'),
        font=dict(color='#333')
    )
    return bar_fig

def create_gender_impact_bar(df):
    genre_counts = df.groupby(['genre', 'eligibilite_statut']).size().reset_index(name='Effectif')
    total_per_genre = genre_counts.groupby('genre')['Effectif'].transform('sum')
    genre_counts['Pourcentage'] = round(genre_counts['Effectif'] / total_per_genre * 100, 1)

    color_map = {
        'eligible': 'green',
        'temporairement noneligible': 'orange',
        'definitivement noneligible': 'red'
    }

    fig = px.bar(
        genre_counts,
        x="genre",
        y="Pourcentage",
        color="eligibilite_statut",
        barmode="group",
        text="Effectif",
        title="Distribution de l'Éligibilité selon le Genre",
        color_discrete_map=color_map
    )
    fig.update_traces(texttemplate='%{text} (%{y:.1f}%)', textposition="outside")
    return fig

def generate_interpretation(df):
    total = len(df)
    if total == 0:
        return "Aucune donnée disponible pour cette période."

    eligible_pct = (df['eligibilite_statut'] == 'eligible').mean() * 100
    def_pct = (df['eligibilite_statut'] == 'definitivement noneligible').mean() * 100
    temp_pct = (df['eligibilite_statut'] == 'temporairement noneligible').mean() * 100

    def_counts = df[[
        'raison_de_non-eligibilité_totale__[hypertendus]',
        'raison_de_non-eligibilité_totale__[diabétique]',
        'raison_de_non-eligibilité_totale__[porteur(hiv,hbs,hcv)]',
        'raison_de_non-eligibilité_totale__[asthmatiques]'
    ]].apply(lambda col: (col == 'oui').sum())

    top_def = def_counts.idxmax() if not def_counts.empty else None
    top_def_label = top_def.replace('raison_de_non-eligibilité_totale__', '').strip('[]') if top_def else "aucune"

    interpretation = (
        f"Sur cette période, environ {eligible_pct:.1f}% des donneurs étaient éligibles, "
        f"{temp_pct:.1f}% temporairement non éligibles et {def_pct:.1f}% définitivement non éligibles. "
        f"La condition de non-éligibilité la plus fréquente est : {top_def_label}."
    )
    return interpretation

def get_health_conditions_layout(start_date=None, end_date=None):
    df, total_cols, temp_cols = load_health_data(start_date, end_date)

    pie_elig = create_eligibility_pie(df)
    bar_total = create_reason_bars(df, total_cols, "Raisons de Non-Éligibilité Définitive")
    bar_temp = create_reason_bars(df, temp_cols, "Raisons d'Indisponibilité Temporaire")
    gender_fig = create_gender_impact_bar(df)
    interpretation = generate_interpretation(df)

    card_style = {
        "backgroundColor": "white",
        "borderRadius": "12px",
        "boxShadow": "0 2px 6px rgba(0, 0, 0, 0.1)",
        "padding": "15px"
    }

    return html.Div([
        html.H3("Analyse des Conditions Médicales et Éligibilité"),

        html.Div([
            html.Div([dcc.Graph(figure=pie_elig)], style={"flex": "2", "minWidth": "600px", "margin": "auto", "textAlign": "center", "padding": "20px", **card_style}),
            html.Div([
                html.Div([dcc.Graph(figure=bar_total)], style={"width": "100%", "marginBottom": "20px", **card_style}),
                html.Div([dcc.Graph(figure=bar_temp)], style={"width": "100%", **card_style})
            ], style={"flex": "1", "paddingLeft": "30px"})
        ], style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "alignItems": "flex-start", "width": "100%"}),

        html.Hr(style={"marginTop": "40px", "marginBottom": "20px", "borderTop": "4px solid #444"}),

        html.Div([
            dcc.Graph(figure=gender_fig)
        ], style={"marginTop": "30px", **card_style}),

        html.Div([
            html.H4("Interprétation Automatique"),
            html.P(interpretation, style={"fontSize": "16px"}),

            html.H4("Guide de Lecture"),
            html.P("1. Le graphique en anneau montre la répartition globale des statuts d'éligibilité avec les effectifs."),
            html.P("2. Les deux graphiques à droite montrent les raisons principales de non-éligibilité (définitive et temporaire)."),
            html.P("3. Le dernier graphique montre la répartition des statuts selon le genre avec effectifs et pourcentages."),
        ], style={"marginTop": "30px", **card_style})
    ])
