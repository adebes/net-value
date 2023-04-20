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

player_data = pd.read_csv("players_preprocessed1.csv")
player_data['league_id'].fillna(-1, inplace=True)
# Extract Player IDs and League Info
player_options = [{'label': str(row['player_firstname']) + " " + str(row['player_lastname']),
                   'value': str(row['player_id'])}
                  for index, row in player_data.iterrows()]
league_options = [{'label': str(row['league_name']),
                   'value': row['league_name']}
                  for index, row in player_data.drop_duplicates(subset=['league_name', 'league_id']).iterrows()]
season_options = [{'label': str(row['league_season']),
                   'value': row['league_season']}
                  for index, row in player_data.drop_duplicates(subset=['league_season']).iterrows()]


# Create a scatter plot
scatter_data = px.scatter(x=[1, 2, 3, 4], y=[2, 4, 1, 3])

# Create static radial charts
radial_chart_1 = go.Figure(go.Scatterpolar(
    r=[1, 3, 2], theta=['Attack', 'Mid', 'Defense'], fill='toself'))
radial_chart_2 = go.Figure(go.Scatterpolar(
    r=[4, 1, 2], theta=['Attack', 'Mid', 'Defense'], fill='toself'))
radial_chart_3 = go.Figure(go.Scatterpolar(
    r=[2, 4, 3], theta=['Attack', 'Mid', 'Defense'], fill='toself'))

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


# Define tab2 layout
tab2_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Label('League'),
            dcc.Dropdown(id='league-tab2', options=league_options),
            html.Label('Season'),
            dcc.Dropdown(id='season-tab2', options=season_options),
        ], width=3),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label('Goalkeeper', style={
                            'color': 'Black', 'font-weight': 'bold'}),
                        dcc.Dropdown(id='goalkeeper-dropdown',
                                     # options from callback
                                     options=[], searchable=True,
                                     clearable=True,
                                     placeholder='Select Goalkeeper(s)',
                                     style={'width': '100%'})
                    ], style={'width': '25%', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Defender', style={
                            'color': 'Black', 'font-weight': 'bold'}),
                        dcc.Dropdown(id='defender-dropdown',

                                     options=[], multi=True,
                                     searchable=True,  # adds auto fill search option
                                     clearable=True,  # adds clear button to deselect players
                                     placeholder='Select Defender(s)',
                                     style={'width': '100%'})
                    ], style={'width': '25%', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Midfielder', style={
                            'color': 'Black', 'font-weight': 'bold'}),
                        dcc.Dropdown(id='midfielder-dropdown',
                                     options=[], multi=True,
                                     searchable=True,
                                     clearable=True,
                                     placeholder='Select Midfielder(s)',
                                     style={'width': '100%'})
                    ], style={'width': '25%', 'display': 'inline-block'}),
                    html.Div([
                        html.Label('Attacker', style={
                            'color': 'Black', 'font-weight': 'bold'}),
                        dcc.Dropdown(id='attacker-dropdown',
                                     options=[], multi=True,
                                     searchable=True,
                                     clearable=True,
                                     placeholder='Select Attacker(s)',
                                     style={'width': '100%'})
                    ], style={'width': '25%', 'display': 'inline-block'}),
                ])
            ]),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            id='goalkeeper-circle',
                            children=[],
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'flex-direction': 'column',
                                'align-items': 'center',
                            }
                        )
                    ),
                    dbc.Col(
                        html.Div(
                            id='defender-circles',
                            children=[],
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'flex-direction': 'column',
                                'align-items': 'center',
                                'margin-left': '-120%'
                            }

                        )
                    ),
                    dbc.Col(
                        html.Div(
                            id='middle-fielder-circles',
                            children=[],
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'flex-direction': 'column',
                                'align-items': 'center',
                                'margin-left': '-150%'
                            }

                        )
                    ),
                    dbc.Col(
                        html.Div(
                            id='attacker-circles',
                            children=[],
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'flex-direction': 'column',
                                'align-items': 'center',
                                'margin-left': '-150%'
                            }

                        )
                    ),
                ],
                style={
                    'height': '100%',
                    'background-image': 'url(https://wallpapercave.com/wp/wp139791.jpg)',
                    'background-size': 'cover',
                    'background-position': 'center',
                    'position': 'relative',
                    'display': 'flex',
                    'align-items': 'center',
                    'justify-content': 'space-around',
                },
            )
        ], width=9, style={'height': '400px'}),
    ], style={'height': '400px'
              })
], fluid=True)

# callbacks for tab2
# callback for goalkeeper circle


@app.callback(
    Output('defender-dropdown', 'value'),
    Input('defender-dropdown', 'value')
)
def limit_selections(values):
    if values is not None and len(values) > 4:
        return values[:4]
    return values


@app.callback(
    Output('midfielder-dropdown', 'value'),
    Input('midfielder-dropdown', 'value')
)
def limit_selections(values):
    if values is not None and len(values) > 3:
        return values[:3]
    return values


@app.callback(
    Output('attacker-dropdown', 'value'),
    Input('attacker-dropdown', 'value')
)
def limit_selections(values):
    if values is not None and len(values) > 3:
        return values[:3]
    return values


@app.callback(
    Output('goalkeeper-circle', 'children'),
    Input('goalkeeper-dropdown', 'value')
)
def update_goalkeeper_circle(selected_player):
    if selected_player is None:
        return html.Div()
    player_info = player_data[player_data['player_name']
                              == selected_player].iloc[0]
    player_photo_url = player_info['player_photo']
    return (html.Div(
        style={
            'display': 'inline-block',
            'background-image': f'url({player_photo_url})',
            'background-size': 'cover',
            'background-position': 'center',
            'border-radius': '50%',
            'width': '50px',
            'height': '50px',
        },

    ),
        html.Div(selected_player, style={
            'font-size': '12px', 'color': '#ffff', 'font-weight': 'bold', 'background-color': '#FF5733',
            'padding': '5px',
            'border-radius': '5px'}))


@app.callback(
    Output('defender-circles', 'children'),
    Input('defender-dropdown', 'value'))
def update_defender_circles(selected_players):
    if selected_players is None:
        return [html.Div(), html.Div(), html.Div(), html.Div()]
    if len(selected_players) < 4:
        return [html.Div('Please select 4 defenders', style={'color': 'red'})]
    elif len(selected_players) > 4:
        selected_players = selected_players[:4]
    circles = []
    for i in range(1, 5):
        if len(selected_players) >= i:
            player_name = selected_players[i-1]
            player_photo = player_data[player_data['player_name']
                                       == player_name]['player_photo'].iloc[0]
            circles.append(html.Div(
                style={
                    'display': 'flex',
                    'justify-content': 'center',
                    'flex-direction': 'column',
                    'align-items': 'center',
                },
                children=[
                    html.Div(
                        style={
                            'display': 'block',
                            'background-image': f'url({player_photo})',
                            'background-size': 'contain',
                            'background-repeat': 'no-repeat',
                            'background-position': 'center',
                            'border-radius': '50%',
                            'width': '50px',
                            'height': '50px',
                            'position': 'relative',

                        }),
                    html.Div(selected_players[i-1], style={
                        'font-size': '12px', 'color': '#ffff', 'font-weight': 'bold', 'background-color': '#FF5733',
                        'padding': '5px',
                        'border-radius': '5px', 'margin-bottom': '20px'})
                ]

            ))
        else:
            circles.append(html.Div())
        # remove circles of deselected players
    for i in range(len(circles)):
        if i >= len(selected_players):
            circles[i] = html.Div()

    return circles


@app.callback(
    Output('middle-fielder-circles', 'children'),
    Input('midfielder-dropdown', 'value'))
def update_midfielder_circles(selected_players):
    if selected_players is None:
        return [html.Div(), html.Div(), html.Div()]
    if len(selected_players) < 3:
        return [html.Div('Please select 3 midfielders', style={'color': 'red'})]
    elif len(selected_players) > 3:
        selected_players = selected_players[:3]
    circles = []
    for i in range(1, 4):
        if len(selected_players) >= i:
            player_name = selected_players[i-1]
            player_photo = player_data[player_data['player_name']
                                       == player_name]['player_photo'].iloc[0]
            circles.append(html.Div(
                style={
                    'display': 'flex',
                    'justify-content': 'center',
                    'flex-direction': 'column',
                    'align-items': 'center',
                },
                children=[
                    html.Div(
                        style={
                            'display': 'block',
                            'background-image': f'url({player_photo})',
                            'background-size': 'contain',
                            'background-repeat': 'no-repeat',
                            'background-position': 'center',
                            'border-radius': '50%',
                            'width': '50px',
                            'height': '50px',
                            'position': 'relative',
                        }),
                    html.Div(selected_players[i-1], style={
                        'font-size': '12px', 'color': '#ffff', 'font-weight': 'bold', 'background-color': '#FF5733',
                        'padding': '5px',
                        'border-radius': '5px', 'margin-bottom': '20px'})
                ]

            ))
        else:
            circles.append(html.Div())
        # remove circles of deselected players
    for i in range(len(circles)):
        if i >= len(selected_players):
            circles[i] = html.Div()
    return circles


@app.callback(
    Output('attacker-circles', 'children'),
    Input('attacker-dropdown', 'value'))
def update_attacker_circles(selected_players):
    if selected_players is None:
        return [html.Div(), html.Div(), html.Div()]
    if len(selected_players) < 3:
        return [html.Div('Please select 3 attackers', style={'color': 'red'})]
    elif len(selected_players) > 3:
        selected_players = selected_players[:3]
    circles = []
    for i in range(1, 4):
        if len(selected_players) >= i:
            player_name = selected_players[i-1]
            player_photo = player_data[player_data['player_name']
                                       == player_name]['player_photo'].iloc[0]
            circles.append(html.Div(
                style={
                    'display': 'block',
                    'background-image': f'url({player_photo})',
                    'background-size': 'contain',
                    'background-repeat': 'no-repeat',
                    'background-position': 'center',
                    'border-radius': '50%',
                    'width': '50px',
                    'height': '50px',
                    'position': 'relative',
                },
            ))
            circles.append(html.Div(selected_players[i-1], style={
                'font-size': '12px', 'color': '#ffff', 'font-weight': 'bold', 'background-color': '#FF5733',
                'padding': '5px',
                'border-radius': '5px', 'margin-bottom': '20px'}))

        else:
            circles.append(html.Div())
    return circles

# call back for goalkeeper dropdown, defender-dropdown, midfielder-dropdown,attacker-dropdowns based on league and season, update the dropdowns options.


@app.callback(
    [Output('goalkeeper-dropdown', 'options'),
     Output('defender-dropdown', 'options'),
     Output('midfielder-dropdown', 'options'),
     Output('attacker-dropdown', 'options')],
    [Input('league-tab2', 'value'),
     Input('season-tab2', 'value')]
)
def update_goalkeeper_dropdown(league, season):
    if league and season:
        filtered_data = player_data[(
            player_data['league_name'] == league) & (player_data['league_season'] == season)]
        goalkeeper_data = filtered_data[filtered_data['games_position']
                                        == 'Goalkeeper']
        goalkeeper_names = goalkeeper_data['player_name'].unique()
        goalkeeper_options = [{'label': str(i), 'value': str(i)}
                              for i in goalkeeper_names]

        defender_data = filtered_data[filtered_data['games_position'] == 'Defender']
        defender_names = defender_data['player_name'].unique()
        defender_options = [{'label': str(i), 'value': str(i)}
                            for i in defender_names]

        midfielder_data = filtered_data[filtered_data['games_position']
                                        == 'Midfielder']
        midfielder_names = midfielder_data['player_name'].unique()
        midfielder_options = [{'label': str(i), 'value': str(i)}
                              for i in midfielder_names]

        attacker_data = filtered_data[filtered_data['games_position'] == 'Attacker']
        attacker_names = attacker_data['player_name'].unique()
        attacker_options = [{'label': str(i), 'value': str(i)}
                            for i in attacker_names]

        return goalkeeper_options, defender_options, midfielder_options, attacker_options
    else:
        return [], [], [], []


# Define the app layout
app.layout = dbc.Container([
    html.H1("Net Value", className="text-center"),
    html.H3("Combining AI and Soccer", className="text-center"),
    dbc.Tabs([
        dbc.Tab(tab1_layout, label='Tab 1'),
        dbc.Tab(tab2_layout, label='Tab 2')
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
