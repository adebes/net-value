import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

player_data = pd.read_csv("dashboard/players_preprocessed1.csv")
player_data['league_id'].fillna(-1, inplace=True)
# Extract Player IDs and League Info
player_options = [{'label': str(row['player_firstname']) + " " + str(row['player_lastname']), 
                   'value': str(row['player_id'])} 
                  for index, row in player_data.iterrows()]
league_options = [{'label': str(row['league_name']), 
                   'value': str(row['league_id'])} 
                  for index, row in player_data.drop_duplicates(subset=['league_name', 'league_id']).iterrows()]
season_options = [{'label': str(row['league_season']), 
                   'value': str(row['league_season'])} 
                  for index, row in player_data.drop_duplicates(subset=['league_season']).iterrows()]


# Create a scatter plot
scatter_data = px.scatter(x=[1, 2, 3, 4], y=[2, 4, 1, 3])

# Create static radial charts
radial_chart_1 = go.Figure(go.Scatterpolar(r=[1, 3, 2], theta = ['Attack', 'Mid', 'Defense'], fill='toself'))
radial_chart_2 = go.Figure(go.Scatterpolar(r=[4, 1, 2], theta = ['Attack', 'Mid', 'Defense'], fill='toself'))
radial_chart_3 = go.Figure(go.Scatterpolar(r=[2, 4, 3], theta = ['Attack', 'Mid', 'Defense'], fill='toself'))

# Define the first tab layout
tab1_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Label('League'),
            dcc.Dropdown(id='league', options=league_options),
            html.Label('Season'),
            dcc.Dropdown(id='season', options=season_options),
            html.Label('Players'),
            dcc.Dropdown(id='player', options=player_options,
                         )
        ], width=3),
        dbc.Col([
            dcc.Graph(id='scatter-plot', figure=scatter_data)
        ], width=9),
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='dynamic-header', className='text-center'),
            dcc.Graph(id='dynamic-radial-chart')
        ], width=6),
        dbc.Col([
            dcc.Graph(figure=radial_chart_1),
            dcc.Graph(figure=radial_chart_2),
            dcc.Graph(figure=radial_chart_3)
        ], width=6)
    ])
])

# Define the app layout
app.layout = dbc.Container([
    html.H1("Net Value", className="text-center"),
    html.H3("Combining AI and Soccer", className="text-center"),
    dbc.Tabs([
        dbc.Tab(tab1_layout, label='Tab 1'),
        dbc.Tab(label='Tab 2')
    ])
])


# Define a callback to update the dynamic radial chart header based on data filters
@app.callback(
    Output('dynamic-header', 'children'),
    [Input('league', 'value'),
     Input('season', 'value'),
     Input('player', 'value')]
)
def update_dynamic_header(league, season, player):
    header_text = "{} - {} - {}".format(league, season, player)
    return header_text


# Define a callback to update the dynamic radial chart based on data filters
@app.callback(
    Output('dynamic-radial-chart', 'figure'),
    [Input('league', 'value'),
     Input('season', 'value'),
     Input('player', 'value')]
)
def update_radial_chart(league, season, player):
    import random
    r = [random.uniform(1, 5), random.uniform(1, 5), random.uniform(1, 5)]
    theta = ['Attack', 'Mid', 'Defense']
    dynamic_chart = go.Figure(go.Scatterpolar(r=r, theta=theta, fill='toself'))
    return dynamic_chart

if __name__ == '__main__':
    app.run_server(debug=True)
