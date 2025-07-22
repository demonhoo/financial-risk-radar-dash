import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

# Load data
df = pd.read_csv("financial_risk_data.csv")
regions = df["Region"].unique()
quarters = sorted(df["Time"].unique(), key=lambda x: (int(x.split("_")[0]), int(x.split("_")[1][1])))

# App setup
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("📊 Financial Risk Radar", style={'textAlign': 'center', 'fontSize': '32px'}),
    html.Div([
        html.Label("Select Region:"),
        dcc.Dropdown(
            id="region-dropdown",
            options=[{"label": r, "value": r} for r in regions],
            value="Global",
            clearable=False
        )
    ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

    html.Div([
        html.Label("Select Quarter:"),
        dcc.Slider(
            id="quarter-slider",
            min=0,
            max=len(quarters) - 1,
            value=len(quarters) // 2,
            marks={i: q for i, q in enumerate(quarters) if i % 4 == 0},
            step=None
        )
    ], style={'padding': '20px'}),

    dcc.Graph(id="radar-chart")
])

@app.callback(
    Output("radar-chart", "figure"),
    Input("region-dropdown", "value"),
    Input("quarter-slider", "value")
)
def update_chart(region, quarter_index):
    time = quarters[quarter_index]
    dff = df[(df["Region"] == region) & (df["Time"] == time)]

    theta = [f"{r} {t}" for r, t in zip(dff["Risk Dimension"], dff["Trend"])]
    r = dff["Score"].tolist()
    theta.append(theta[0])
    r.append(r[0])
    color_map = {"Global": "#1f77b4", "USA": "#d62728", "China": "#2ca02c", "Eurozone": "#9467bd"}
    color = color_map.get(region, "blue")
    pressure_index = dff["Pressure Index"].iloc[0]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=r,
        theta=theta,
        fill='toself',
        name=region,
        line=dict(color=color)
    ))

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=pressure_index,
        title={'text': "Financial Stress Index"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': "lightgreen"},
                {'range': [40, 70], 'color': "orange"},
                {'range': [70, 100], 'color': "red"}
            ]
        },
        domain={'x': [0.75, 1], 'y': [0, 0.3]}
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5])
        ),
        showlegend=False,
        height=600,
        margin=dict(t=60, b=60)
    )

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
