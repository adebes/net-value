import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from dash import dash_table
import copy
import numpy as np
import plotly.figure_factory as ff

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

player_data = pd.read_csv("E:\GATech_MSA\Spring2023\CSE6242\Project\players_preprocessed1.csv")
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

# Define data for tab2
# Create an empty table with the required columns
table_columns = [{'name': 'Performance', 'id': 'Performance'},
                 {'name': 'Selected Player', 'id': 'Selected Player'},
                 {'name': 'Alternate Player 1', 'id': 'Alternate Player 1'},
                 {'name': 'Alternate Player 2', 'id': 'Alternate Player 2'}]
table_data = []
feats = ['passes_90min_I', 'saves_90min_I',
    'shots_90mins', 'shots_on_90mins', 'goals_total_90mins',
    'goals_conceded_90mins', 'goals_assists_90mins', 'goals_saves_90mins',
    'passes_total_90mins', 'passes_key_90mins', 'passes_accuracy_90mins',
    'tackles_total_90mins', 'tackles_blocks_90mins',
    'tackles_interceptions_90mins', 'duels_total_90mins',
    'duels_won_90mins', 'dribbles_attempts_90mins',
    'dribbles_success_90mins', 'fouls_drawn_90mins',
    'fouls_committed_90mins', 'cards_yellow_90mins',
    'cards_yellowred_90mins', 'cards_red_90mins', 'penalty_won_90mins',
    'penalty_commited_90mins', 'penalty_scored_90mins',
    'penalty_missed_90mins', 'penalty_saved_90mins']

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
              }
    ),
    dbc.Row([
    dbc.Col([
    dbc.Row([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label('Player', style={'color': 'Black', 'font-weight': 'bold'}),
                dcc.Dropdown(id='current-dropdown',
                                # options from callback
                                options=[], #multi=True,
                                searchable=True,
                                clearable=True,
                                placeholder='Selected Player',
                                style={'width': '95%'})
            ], style={'width': '25%', 'display': 'inline-block'}),
            html.Div([
                html.Label('Alternative 1', style={'color': 'Black', 'font-weight': 'bold'}),
                dcc.Dropdown(id='suggestion1-dropdown',
                                options=[], multi=True,
                                searchable=True,  # adds auto fill search option
                                clearable=True,  # adds clear button to deselect players
                                placeholder='Similar Player 1',
                                style={'width': '95%'})
            ], style={'width': '25%', 'display': 'inline-block'}),
            html.Div([
                html.Label('Alternative 2', style={'color': 'Black', 'font-weight': 'bold'}),
                dcc.Dropdown(id='suggestion2-dropdown',
                                options=[], multi=True,
                                searchable=True,
                                clearable=True,
                                placeholder='Similar Player 2',
                                style={'width': '95%'})
            ], style={'width': '25%', 'display': 'inline-block'})
        ],width=8),
    ], style={
            'height': '50px',
            'position': 'relative',
            'display': 'flex',
            'margin-top': '+20%',
            'margin-left': '+10%'
            },
    )
    ], style={'height':'50px','align-items': 'center'}),
    dbc.Row([
        #dbc.Col(dcc.Graph(id='stats-table'))
        html.Div([
                dash_table.DataTable(id='stats-table', 
                                     columns=table_columns, 
                                     data=[],editable=True,
                                     style_cell={'minWidth': '200px', 'maxWidth': '200px'}
                                     ) #table_data)
            ], style={'width': '25%', 'display': 'inline-block'}
        )
    ],style={
            'height': '100px',
            'position': 'relative',            
            'display': 'flex',
            'margin-top': '+22%',
            'margin-left': '-5%'
            },
    )
    
    ]),
    dbc.Col([
            html.Div(id='compare-radial', className='text-center'),
            dcc.Graph(id='compare-radial-chart')
    ],width=8,style={
            'margin-left': '+60%'
            })
    ])
], fluid=True)

# callbacks for tab2
# Define a callback to update the dynamic radial chart for player comparision
@app.callback(
    Output('compare-radial-chart', 'figure'),
    [Input('current-dropdown', 'value'),
     Input('league-tab2', 'value'),
     Input('season-tab2', 'value'),
     Input('suggestion1-dropdown', 'value'),
     Input('suggestion2-dropdown', 'value')]
)
def update_radial_chart(player1,league, season, player2=None,player3=None):
    filter_data = player_data[(player_data['league_name'] == league) &
                              (player_data['league_season'] == season)]
    fig = go.Figure()

    if player1:
        #return dynamic_chart
        p1data = filter_data[filter_data['player_name'] == str(player1)]
        p1data = p1data[feats].iloc[0]
        feat_cols = [col for col in p1data.keys()]
        vals1 = [i for i  in p1data.values]
        trace1 = go.Scatterpolar(r=vals1, theta=feat_cols, fill='none',fillcolor='#FF6347',name=str(player1))
        if player2:
            p2data = filter_data[filter_data['player_name'] == str(player2[0])]
            p2data = p2data[feats].iloc[0]
            vals2 = [i for i  in p2data.values]
            trace2 = go.Scatterpolar(r=vals2, theta=feat_cols, fill='none',fillcolor='#00CED1',name=str(player2[0]))
        else:
            p2data = [0*i for i in p1data]
            vals2 = p2data
            trace2 = go.Scatterpolar(r=vals2, theta=feat_cols, fill='none',fillcolor='#00CED1',name=str(player2))
        if player3:
            p3data = filter_data[filter_data['player_name'] == str(player3[0])]
            p3data = p3data[feats].iloc[0]
            vals3 = [i for i  in p3data.values]
            trace3 = go.Scatterpolar(r=vals3, theta=feat_cols, fill='none',fillcolor='#FFD700',name=str(player3[0]))
        else:
            p3data = [0*i for i in p1data]
            vals3 = p3data
            trace3 = go.Scatterpolar(r=vals3, theta=feat_cols, fill='none',fillcolor='#FFD700',name=str(player3))

        fig.add_trace(trace1)
        fig.add_trace(trace2)
        fig.add_trace(trace3)
        fig.update_layout(legend=dict(
                                        orientation='h',
                                        yanchor='top',
                                        y=1.25,
                                        xanchor='left',
                                        x=0
                                     )
                         )
        return fig
    return fig

# callback to update option for current player
@app.callback(
    Output('current-dropdown', 'options'),
    [Input('goalkeeper-dropdown', 'value'),
     Input('defender-dropdown', 'value'),
     Input('midfielder-dropdown', 'value'),
     Input('attacker-dropdown', 'value')]
)
def update_selected_dropdown(gk = None,defend = None,midf = None,attack = None):
    options = []
    if(gk is not None and len(gk)>0):
        options.append({'label': str(gk), 'value': str(gk)})
    if(defend is not None and len(defend)>0):
        for i in range(len(defend)):
            options.append({'label': str(defend[i]), 'value': str(defend[i])})
    if(midf is not None and len(midf)>0):
        for i in range(len(midf)):
            options.append({'label': str(midf[i]), 'value': str(midf[i])})
    if(attack is not None and len(attack)>0):
        for i in range(len(attack)):
            options.append({'label': str(attack[i]), 'value': str(attack[i])})
    return options

# callback to update option for current player
@app.callback(
    Output('suggestion1-dropdown', 'options'),
    [Input('current-dropdown', 'value'),
     Input('league-tab2', 'value'),
     Input('season-tab2', 'value'),
     Input('suggestion1-dropdown', 'value'),
     Input('suggestion2-dropdown', 'value')]
)
def update_suggest_dropdown(main_player,league,season,select1=None,select2=None):
    if main_player:
        filter_data = player_data[(player_data['league_name'] == league) &
                                (player_data['league_season'] == season)]
        reqpos = filter_data[filter_data['player_name']==main_player]
        reqpos = reqpos['games_position'].iloc[0]
        reqdata = filter_data[player_data['games_position'] == reqpos]
        reqdata = reqdata['player_name'].unique()
        remove_list = [main_player, select1, select2]
        req_options = [{'label': str(i), 'value': str(i)} for i in reqdata if str(i) not in remove_list]

        return req_options#, req_options
    return []

# callback to update option for current player
@app.callback(
    Output('suggestion2-dropdown', 'options'),
    [Input('current-dropdown', 'value'),
     Input('league-tab2', 'value'),
     Input('season-tab2', 'value'),
     Input('suggestion1-dropdown', 'value'),
     Input('suggestion2-dropdown', 'value')]
)
def update_suggest_dropdown(main_player,league,season,select1=None,select2=None):
    if main_player:
        filter_data = player_data[(player_data['league_name'] == league) &
                                (player_data['league_season'] == season)]
        reqpos = filter_data[filter_data['player_name']==main_player]
        reqpos = reqpos['games_position'].iloc[0]
        reqdata = filter_data[player_data['games_position'] == reqpos]
        reqdata = reqdata['player_name'].unique()
        remove_list = [main_player, select1, select2]
        req_options = [{'label': str(i), 'value': str(i)} for i in reqdata if str(i) not in remove_list]
        """
        reqdict = {'label': str(main_player), 'value': str(main_player)}
        index = req_options.index(reqdict)
        _ = req_options.pop(index)
        """
        return req_options #, req_options
    return []

# Stats table callback
@app.callback(
    Output('stats-table', 'data'),
    [Input('current-dropdown', 'value'),
     Input('league-tab2', 'value'),
     Input('season-tab2', 'value'),
     Input('suggestion1-dropdown', 'value'),
     Input('suggestion2-dropdown', 'value')]
)
def update_table(player1, league, season, player2=None, player3=None):
    filter_data = player_data[(player_data['league_name'] == league) &
                            (player_data['league_season'] == season)]    
    if player1:
        p1data = filter_data[filter_data['player_name'] == str(player1)]
        p1data = p1data[feats]
        if player2:
            p2data = filter_data[filter_data['player_name'] == str(player2)]
            p2data = p2data[feats]
        else:
            p2data = copy.deepcopy(p1data)
            p2data = np.nan*p2data
        if player3:
            p3data = filter_data[filter_data['player_name'] == str(player3)]
            p3data = p3data[feats]
        else:
            p3data = copy.deepcopy(p1data)
            p3data = np.nan*p3data
        feat_cols = [col for col in p1data.keys()]
        vals1 = [i for i  in p1data.values]
        vals2 = [i for i  in p2data.values]
        vals3 = [i for i  in p3data.values]
        #data = [{'Performance':feat_cols[i],'Selected Player':vals1[i], 'Alternate Player 1':vals2[i], 'Alternate Player 2':vals3[i]} for i in range(len(p1data))]
        #data = [{'Performance':feat_cols,'Selected Player':vals1, 'Alternate Player 1':vals2, 'Alternate Player 2':vals3}]
        data_mat = []
        data_mat.append(['Performance', 'Selected Player', 'Alternative 1', 'Alternative 2'])
        for i in range(len(feat_cols)):
            row = [feat_cols[i],vals1[i],vals2[i],vals3[i]]
            data_mat.append(row)
        fig = ff.create_table(data_mat)
        return data_mat #go.Figure(data=data)

# callback for suggestion selection limits
@app.callback(
    [Output('suggestion1-dropdown', 'value'),
     Output('suggestion2-dropdown', 'value')],
    [Input('suggestion1-dropdown', 'value'),
     Input('suggestion2-dropdown', 'value')]
)
def limit_selections(values1,values2):
    if values1 is not None and len(values1) > 1:
        values1 = values1[0]
    if values2 is not None and len(values2) > 1:
        values2 = values2[0]
    return values1,values2


# callback for season dropdown, shows only available seasons for selected league
@app.callback(
    Output('season-tab2', 'options'),
    Input('league-tab2', 'value')
)
def set_season_options(selected_league):
    df_filtered = player_data[player_data['league_name'] == selected_league]
    return [{'label': str(i), 'value': i} for i in df_filtered['league_season'].unique()]


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
    port = 8052
    app.run_server(debug=True,port=port)
