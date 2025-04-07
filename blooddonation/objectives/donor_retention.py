# objectives/donor_retention.py

import pandas as pd
import numpy as np

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# Data loading / simulation
# -----------------------------------------------------------------------------
def load_retention_data(start_date=None, end_date=None):
    # TODO: replace with real data loading & filtering by start_date/end_date
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    # Simulate retention rates ~70% ±5%
    retention_rates = np.clip(np.random.normal(70, 5, size=12), 40, 100)
    new_donors       = np.random.randint(100, 500, size=12)
    returning_donors = np.random.randint(200, 700, size=12)

    retention_df = pd.DataFrame({
        'month': months,
        'retention_rate': retention_rates,
        'new_donors': new_donors,
        'returning_donors': returning_donors
    })
    retention_df['total_donors'] = retention_df['new_donors'] + retention_df['returning_donors']

    # Cohort simulation for first six months
    cohorts = months[:6]
    cohort_data = []
    for cohort in cohorts:
        row = {'cohort': cohort}
        prev = 100.0
        for i in range(6):
            if i == 0:
                row[f'month{i}'] = 100.0
            else:
                drop = np.random.normal(10, 2)
                val  = max(prev - drop, 35.0)
                row[f'month{i}'] = val
                prev = val
        cohort_data.append(row)
    cohort_df = pd.DataFrame(cohort_data)

    return retention_df, cohort_df

# -----------------------------------------------------------------------------
# Main layout function
# -----------------------------------------------------------------------------
def get_retention_layout(start_date=None, end_date=None):
    retention_df, cohort_df = load_retention_data(start_date, end_date)

    # 1) Monthly Retention Line
    retention_fig = px.line(
        retention_df, x='month', y='retention_rate', markers=True,
        labels={'retention_rate':'Retention Rate (%)'},
        title='Monthly Retention Rate'
    )
    retention_fig.update_traces(line=dict(color='#e63946', width=3), marker=dict(size=8))
    retention_fig.update_layout(
        margin=dict(l=20,r=20,t=40,b=20),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        legend=dict(orientation='h', y=1.02, x=1),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)')
    )

    # 2) New vs Returning Bar
    donor_fig = go.Figure([
        go.Bar(x=retention_df['month'], y=retention_df['returning_donors'],
               name='Returning Donors', marker_color='#1d3557'),
        go.Bar(x=retention_df['month'], y=retention_df['new_donors'],
               name='New Donors', marker_color='#e63946'),
    ])
    donor_fig.update_layout(
        barmode='stack', title='New vs Returning Donors',
        margin=dict(l=20,r=20,t=40,b=20),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        legend=dict(orientation='h', y=1.02, x=1),
        xaxis=dict(title='Month', showgrid=False),
        yaxis=dict(title='Number of Donors', gridcolor='rgba(0,0,0,0.1)')
    )

    # 3) Cohort Heatmap
    month_cols = [c for c in cohort_df.columns if c.startswith('month')]
    cohort_fig = px.imshow(
        cohort_df.set_index('cohort')[month_cols],
        labels=dict(x='Month', y='Cohort', color='Retention %'),
        x=[f"M{i}" for i in range(len(month_cols))],
        y=cohort_df['cohort'],
        color_continuous_scale='Blues',
        text_auto='.1f',
        title='Donor Cohort Analysis'
    )
    cohort_fig.update_layout(
        margin=dict(l=20,r=20,t=40,b=20),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )

    # 4) KPI Cards
    avg_ret = retention_df['retention_rate'].mean()
    sum_new = retention_df['new_donors'].sum()
    sum_ret = retention_df['returning_donors'].sum()

    kpis = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H3(f"{avg_ret:.1f}%", className="text-primary"),
                html.P("Avg. Retention Rate", className="text-muted")
            ]),
            dbc.CardFooter([
                html.Small("YTD", className="text-muted"),
                html.Span([html.I(className="fas fa-arrow-up text-success me-1"), html.Small("4.2%", className="text-success")])
            ], className="d-flex justify-content-between")
        ], className="h-100 shadow-sm"), md=4, sm=12, className="mb-4"),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H3(f"{sum_new:,}", className="text-primary"),
                html.P("New Donors", className="text-muted")
            ]),
            dbc.CardFooter([
                html.Small("Last 12m", className="text-muted"),
                html.Span([html.I(className="fas fa-arrow-up text-success me-1"), html.Small("12.3%", className="text-success")])
            ], className="d-flex justify-content-between")
        ], className="h-100 shadow-sm"), md=4, sm=12, className="mb-4"),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H3(f"{sum_ret:,}", className="text-primary"),
                html.P("Returning Donors", className="text-muted")
            ]),
            dbc.CardFooter([
                html.Small("Last 12m", className="text-muted"),
                html.Span([html.I(className="fas fa-arrow-down text-danger me-1"), html.Small("2.1%", className="text-danger")])
            ], className="d-flex justify-content-between")
        ], className="h-100 shadow-sm"), md=4, sm=12, className="mb-4"),
    ])

    # 5) Insights & Actions
    insights = dbc.Card([
        dbc.CardHeader("Insights & Recommendations"),
        dbc.CardBody([
            html.Div([
                html.I(className="fas fa-lightbulb text-warning me-2"),
                html.Div([
                    html.H6("Feb Cohort Best Retention"),
                    html.P("Feb donors retain at 62.3% by month 6; analyze Feb campaigns.", className="text-muted mb-0")
                ])
            ], className="d-flex mb-3"),
            html.Hr(),
            html.Div([
                html.I(className="fas fa-chart-line text-success me-2"),
                html.Div([
                    html.H6("Drop After Month 3"),
                    html.P("Significant retention drop after M3; plan 3‑month follow‑up.", className="text-muted mb-0")
                ])
            ], className="d-flex")
        ])
    ], className="shadow-sm mb-4")

    actions = dbc.Card([
        dbc.CardHeader("Recommended Actions"),
        dbc.CardBody(dbc.ListGroup([
            dbc.ListGroupItem([
                html.H6("3‑Month Re‑engagement Campaign"),
                html.P("Target donors at 3‑month mark with personalized messages.", className="text-muted mb-0"),
                dbc.Button("Plan Campaign", color="primary", size="sm", className="mt-2")
            ], className="border-0"),
            dbc.ListGroupItem([
                html.H6("Analyze Feb Campaign"),
                html.P("Identify success factors from February donors.", className="text-muted mb-0"),
                dbc.Button("Review Data", color="primary", size="sm", className="mt-2")
            ], className="border-0")
        ]))
    ], className="shadow-sm mb-4")

    # 6) Cohort Popover
    popover = dbc.Popover(
        [
            dbc.PopoverHeader("Cohort Analysis"),
            dbc.PopoverBody(
                "Rows = donors first donated in that month; columns = % who returned in subsequent months."
            )
        ],
        target="cohort-info-button",
        trigger="hover",
        placement="right"
    )

    # Assemble layout
    return dbc.Container(fluid=True, children=[
        kpis,
        dbc.Row([
            dbc.Col(dcc.Graph(figure=retention_fig, config={'responsive':True}), lg=6, sm=12, className="mb-4"),
            dbc.Col(dcc.Graph(figure=donor_fig,    config={'responsive':True}), lg=6, sm=12, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.Div([
                    html.H5("Donor Cohort Analysis", className="mb-0 float-start"),
                    dbc.Button([html.I(className="fas fa-info-circle me-1"), "What is this?"],
                               id="cohort-info-button", color="link", size="sm", className="float-end")
                ], className="d-flex justify-content-between")),
                dbc.CardBody(dcc.Graph(figure=cohort_fig, config={'responsive':True}))
            ]), width=12, className="mb-4")
        ]),
        popover,
        dbc.Row([
            dbc.Col(insights, width=12, lg=6),
            dbc.Col(actions,  width=12, lg=6),
        ])
    ])
