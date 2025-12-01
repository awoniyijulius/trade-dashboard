import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Global Trade Dashboard"

# Example API call function
def fetch_comtrade_data(reporter="NGA", partner="WLD", year="2024", commodity="HS"):
    """
    Fetch data from UN Comtrade API.
    Reporter: country code (e.g., NGA = Nigeria)
    Partner: country code (e.g., IND = India, WLD = World)
    Year: e.g., 2024
    Commodity: HS, SITC, BEC
    """
    url = f"https://comtradeapi.un.org/public/v1/preview/partner/{reporter}?type=C&freq=A&px={commodity}&ps={year}&r={reporter}&p={partner}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data.get("data", []))
    else:
        return pd.DataFrame()

# Layout
app.layout = html.Div([
    html.H1("🌍 Global Trade Dashboard", style={"textAlign": "center"}),

    html.Div([
        dcc.Dropdown(
            id="reporter",
            options=[{"label": "Nigeria", "value": "NGA"},
                     {"label": "United States", "value": "USA"},
                     {"label": "China", "value": "CHN"}],
            value="NGA",
            clearable=False
        ),
        dcc.Dropdown(
            id="partner",
            options=[{"label": "World", "value": "WLD"},
                     {"label": "India", "value": "IND"},
                     {"label": "United States", "value": "USA"},
                     {"label": "China", "value": "CHN"}],
            value="WLD",
            clearable=False
        ),
        dcc.Input(id="year", type="text", value="2024", placeholder="Enter Year"),
    ], style={"display": "flex", "gap": "10px"}),

    dcc.Graph(id="sankey"),
    dcc.Graph(id="treemap"),
    dcc.Graph(id="trendline")
])

# Callbacks
@app.callback(
    [Output("sankey", "figure"),
     Output("treemap", "figure"),
     Output("trendline", "figure")],
    [Input("reporter", "value"),
     Input("partner", "value"),
     Input("year", "value")]
)
def update_charts(reporter, partner, year):
    df = fetch_comtrade_data(reporter, partner, year)

    if df.empty:
        return go.Figure(), go.Figure(), go.Figure()

    # Sankey Diagram
    sankey_fig = go.Figure(go.Sankey(
        node=dict(label=[reporter] + df["cmdDescE"].tolist() + [partner]),
        link=dict(
            source=[0]*len(df),
            target=list(range(1, len(df)+1)),
            value=df["TradeValue"].tolist()
        )
    ))

    # Treemap
    treemap_fig = px.treemap(df, path=["cmdDescE"], values="TradeValue",
                             title="Commodity Share of Trade")

    # Trend Line
    trend_fig = px.line(df, x="period", y="TradeValue", color="cmdDescE",
                        title="Trade Trends Over Time")

    return sankey_fig, treemap_fig, trend_fig

if __name__ == "__main__":
    app.run_server(debug=True)
