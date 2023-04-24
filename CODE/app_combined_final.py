# Import required libraries
# import dash_html_components as html
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, ALL
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import copy
import numpy as np
from dash import dash_table
import plotly.figure_factory as ff
import timeit
import csv
from functools import wraps


# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
scatter_plot_width = 1000
scatter_plot_length = 650

# Set this to False if you don't want to store execution times
ENABLE_TIMING_DECORATOR = True


# Common variables for tab2
# Create an empty table with the required columns
player_positions = ['Goalkeeper', 'Defender-1', 'Defender-2', 'Defender-3', 'Defender-4',
                    'Midfielder-1', 'Midfielder-2', 'Midfielder-3', 'Attacker-1', 'Attacker-2', 'Attacker-3']
table_columns = [{'name': 'Selected Player', 'id': 'Selected Player',
                  'presentation': 'dropdown'},
                 {'name': 'Alternate Player 1', 'id': 'Alternate Player 1',
                     'presentation': 'dropdown'},
                 {'name': 'Alternate Player 2', 'id': 'Alternate Player 2',
                     'presentation': 'dropdown'},
                 {'name': 'Performance (per 90 mins)', 'id': 'Performance (per 90 mins)'}]
# table_columns = []
table_data = []
feats = ['passing', 'defending', 'fouling',
         'dribbling', 'shooting', 'goalkeeping']
theta_metrics = ['Passing', 'Defending', 'Fouling',
                 'Dribbling', 'Shooting', 'Goalkeeping']
"""
feats_table = ['passes_90min_I', 'saves_90min_I',
    'shots_90mins', 'shots_on_90mins', 'goals_total_90mins',
    'goals_conceded_90mins', 'goals_assists_90mins',
    'passes_key_90mins', 'passes_accuracy_90mins',
    'tackles_total_90mins', 'tackles_blocks_90mins',
    'tackles_interceptions_90mins', 'duels_total_90mins',
    'duels_won_90mins', 'dribbles_attempts_90mins',
    'dribbles_success_90mins', 'fouls_drawn_90mins',
    'fouls_committed_90mins', 'cards_yellow_90mins',
    'cards_yellowred_90mins', 'cards_red_90mins', 'penalty_won_90mins',
    'penalty_commited_90mins', 'penalty_scored_90mins',
    'penalty_missed_90mins', 'penalty_saved_90mins']
"""
feats_table_dict = {
    'passes_90min_I': 'Total passes',
    # 'passes_accuracy_90mins': 'Pass accuracy',
    'passes_key_90mins': 'Key passes',
    'goals_assists_90mins': 'Assists',
    'shots_90mins': 'Total shots',
    'shots_on_90mins': 'Shots on target',
    'goals_total_90mins': 'Total goals',
    'penalty_scored_90mins': 'Penalties scored',
    'penalty_missed_90mins': 'Penalties missed',
    'tackles_total_90mins': 'Total tackles',
    'tackles_blocks_90mins': 'Blocks',
    'tackles_interceptions_90mins': 'Interceptions',
    'duels_total_90mins': 'Total duels',
    'duels_won_90mins': 'Duels won',
    'dribbles_attempts_90mins': 'Attempted dribbles',
    'dribbles_success_90mins': 'Successful dribbles',
    'penalty_won_90mins': 'Penalties won',
    'fouls_drawn_90mins': 'Fouls drawn',
    'fouls_committed_90mins': 'Fouls committed',
    'cards_yellow_90mins': 'Yellow cards received',
    'cards_yellowred_90mins': 'Double Yellow cards received',
    'cards_red_90mins': 'Red cards received',
    'penalty_commited_90mins': 'Penalties committed',
    'saves_90min_I': 'Total saves',
    'goals_conceded_90mins': 'Goals conceded',
    'penalty_saved_90mins': 'Penalties saved'
}

centroids_data = pd.read_csv('centroids.csv')[
    ['passing', 'defending', 'fouling', 'dribbling', 'shooting', 'goalkeeping']]
player_data = pd.read_csv("output.csv")

cluster_labels = {0: 'Goal Machine',
                  1: 'Disciplined Anchor',
                  2: 'Precision Agitator',
                  3: 'Unruly Artisan',
                  4: 'Adaptable Ace',
                  5: 'Dual Catalyst',
                  6: 'Pass Maestro',
                  7: 'Steadfast Guardian',
                  -1: 'Not Selected'}

color_codes = {
    'Goal Machine': '#FF4136',      # Red
    'Disciplined Anchor': '#0074D9',  # Blue
    'Precision Agitator': '#FF851B',  # Orange
    'Unruly Artisan': '#FFDC00',     # Yellow
    'Adaptable Ace': '#2ECC40',    # Green
    'Dual Catalyst': '#B10DC9',      # Purple
    'Pass Maestro': '#39CCCC',       # Turquoise
    'Steadfast Guardian': '#7d4705',  # Brown
    'Not Selected': '#808080'
}

grouped_playstyles = [
    [
        (0, 'Goal Machine'),
        (2, 'Precision Agitator'),
        (5, 'Dual Catalyst')
    ],
    [
        (1, 'Disciplined Anchor'),
        (4, 'Adaptable Ace'),
        (6, 'Pass Maestro')
    ],
    [
        (3, 'Unruly Artisan'),
        (7, 'Steadfast Guardian')
    ]
]


# Extract Player IDs and League Info
player_options = [{'label': str(row['player_firstname']) + " " + str(row['player_lastname']),
                   'value': int(row['player_id'])}
                  for index, row in player_data.iterrows()]
league_options = [{'label': str(row['league_name']) + " - " + str(row['league_country']),
                   'value': int(row['league_id'])}
                  for index, row in player_data.drop_duplicates(subset=['league_name', 'league_id']).iterrows()]
season_options = [{'label': str(row['league_season']),
                   'value': int(row['league_season'])}
                  for index, row in player_data.drop_duplicates(subset=['league_season']).iterrows()]
team_options = [{'label': str(row['team_name']),
                 'value': int(row['team_id'])}
                for index, row in player_data.drop_duplicates(subset=['team_name', 'team_id']).iterrows()]

gk_filter = player_data[player_data['games_position'] == 'Goalkeeper']
def_filter = player_data[player_data['games_position'] == 'Defender']
mid_filter = player_data[player_data['games_position'] == 'Midfielder']
atk_filter = player_data[player_data['games_position'] == 'Attacker']

gk_options = [{'label': str(row['player_name']) + " - " + str(row['league_name']) + " - " + str(row['league_season']),
               'value': index}
              for index, row in gk_filter.drop_duplicates(subset=['league_name', 'league_season', 'player_name']).iterrows()]
def_options = [{'label': str(row['player_name']) + " - " + str(row['league_name']) + " - " + str(row['league_season']),
                'value': index}
               for index, row in def_filter.drop_duplicates(subset=['league_name', 'league_season', 'player_name']).iterrows()]
mid_options = [{'label': str(row['player_name']) + " - " + str(row['league_name']) + " - " + str(row['league_season']),
                'value': index}
               for index, row in mid_filter.drop_duplicates(subset=['league_name', 'league_season', 'player_name']).iterrows()]
atk_options = [{'label': str(row['player_name']) + " - " + str(row['league_name']) + " - " + str(row['league_season']),
                'value': index}
               for index, row in atk_filter.drop_duplicates(subset=['league_name', 'league_season', 'player_name']).iterrows()]

xmin, xmax = player_data['x'].min(), player_data['x'].max()
ymin, ymax = player_data['y'].min(), player_data['y'].max()


# Time Util Functions

def timing_decorator(func):
    if not ENABLE_TIMING_DECORATOR:
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()
        execution_time = end_time - start_time

        function_name = func.__name__
        csv_data = [{'function_name': function_name,
                     'execution_time': execution_time}]
        write_to_csv('execution_times.csv', csv_data)

        return result
    return wrapper


def write_to_csv(filename, data):
    with open(filename, mode='a', newline='') as csvfile:
        fieldnames = ['function_name', 'execution_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvfile.seek(0, 2)
        if csvfile.tell() == 0:
            writer.writeheader()
        for row in data:
            writer.writerow(row)


# Create a scatter plot
scatter_plot = go.Figure()

for cluster, label in cluster_labels.items():
    filtered_df = player_data[player_data['cluster']
                              == cluster].sample(frac=0.1)
    scatter_plot.add_trace(go.Scatter(x=filtered_df['x'], y=filtered_df['y'], mode='markers', marker=dict(
        color=color_codes[label]), name=label))

# Update the layout if needed
scatter_plot.update_layout(width=scatter_plot_width, height=scatter_plot_length,
                           yaxis=dict(range=[ymin - 20, ymax + 20]), xaxis=dict(range=[xmin - 20, xmax + 20]),
                           legend=dict(
                               orientation="h",  # Set the legend orientation to horizontal
                               xanchor="center",  # Anchor the legend horizontally to the center
                               yanchor="top",     # Anchor the legend vertically to the top
                               x=0.5,             # Position the legend in the center of the x-axis
                               y=1.1,             # Position the legend slightly above the plot area
                           ))

# Create static radial charts


@timing_decorator
def create_static_radial_charts():
    theta_metrics = ['Passing', 'Defending', 'Fouling',
                     'Dribbling', 'Shooting', 'Goalkeeping']
    radial_charts = []
    for grouping in grouped_playstyles:
        for line in grouping:
            radial_chart_1 = go.Figure()
            centroid_values = centroids_data.iloc[line[0]].values
            centroid_values = np.clip(centroid_values, 0, 0.5)

            hover_text = [f"{theta_metrics[i]}: {round(centroid_values[i], 3)}" for i in range(
                len(theta_metrics))]
            radial_chart_1.add_trace(go.Scatterpolar(r=centroid_values,
                                                     theta=theta_metrics, name=line[1], fill='toself',
                                                     line=dict(
                                                         color=color_codes[line[1]]),
                                                     hovertemplate=hover_text,
                                                     customdata=list(
                                                         range(len(theta_metrics))),
                                                     hoverlabel=dict(namelength=-1)))

            radial_chart_1.update_layout(
                showlegend=False,
                polar=dict(
                    radialaxis=dict(
                        # Set a constant range for the radial axis centroids_data.max().max()
                        range=[0, 0.5],
                    ),
                    angularaxis=dict()
                ),
                title=dict(
                    text=line[1],
                    font=dict(size=24, color=color_codes[line[1]]),
                    y=0.9,
                    x=0.5,
                    xanchor="center"
                ),
                margin=dict(t=40)
            )

            radial_charts.append(radial_chart_1)
    return radial_charts


radial_charts = create_static_radial_charts()

# Define the first tab layout
tab1_layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("League"),
                        dcc.Dropdown(
                            id="leagues", options=league_options, multi=True
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        html.Label("Team"),
                        dcc.Dropdown(
                            id="teams", options=season_options, multi=True
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        html.Label("Season"),
                        dcc.Dropdown(
                            id="seasons", options=season_options, multi=True
                        ),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        html.Label("Players"),
                        dcc.Dropdown(
                            id="players", options=player_options, multi=True
                        ),
                    ],
                    width=3,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Graph(id="dynamic-radial-chart")], width=4, className="mb-4"
                ),
                dbc.Col(
                    [
                        dcc.Graph(id="scatter-plot", figure=scatter_plot)
                    ],
                    width=8,
                    className="mb-4",
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Graph(figure=radial_charts[0])],
                    width=3,
                    className="mb-4",
                ),
                dbc.Col(
                    [dcc.Graph(figure=radial_charts[1])],
                    width=3,
                    className="mb-4",
                ),
                dbc.Col(
                    [dcc.Graph(figure=radial_charts[2])],
                    width=3,
                    className="mb-4",
                ),
                dbc.Col(
                    [dcc.Graph(figure=radial_charts[3])],
                    width=3,
                    className="mb-4",
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Graph(figure=radial_charts[4])],
                    width=3,
                    className="mb-4",
                ),
                dbc.Col(
                    [dcc.Graph(figure=radial_charts[5])],
                    width=3,
                    className="mb-4",
                ),
                dbc.Col(
                    [dcc.Graph(figure=radial_charts[6])],
                    width=3,
                    className="mb-4",
                ),
                dbc.Col(
                    [dcc.Graph(figure=radial_charts[7])],
                    width=3,
                    className="mb-4",
                ),
            ],
        ),
    ],
    fluid=True,
)

# Define the second tab layout

tab2_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Label('Player Position'),
            dcc.Dropdown(id='player-position-tab2', options=player_positions,
                         placeholder='Select Player Position', searchable=True),
            html.Label('League'),
            dcc.Dropdown(id='league-tab2', options=league_options,
                         placeholder='Select League', searchable=True),
            html.Label('Season'),
            dcc.Dropdown(id='season-tab2', options=season_options,
                         placeholder='Select Season', searchable=True),
            html.Label('Player'),
            dcc.Dropdown(id='player-select-tab2', options=[],
                         placeholder='Select Player', searchable=True),
            dbc.Button('Add Player', id='add-player-button',
                       color='primary', className='mt-2'),
            dbc.Button('Clear All', id='clear-players-button',
                       color='danger', className='mt-2'),
            # html.Label('Selected Players'),
            html.Ul(id='selected-players'),
            dcc.Store(id="player-store")
        ], width=3),
        dbc.Col([

            dbc.Row(
                [
                    dbc.Col([

                        html.Div(
                            id='goalkeeper-circles',
                            children=[],
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'flex-direction': 'column',
                                'align-items': 'center',
                            }

                        ),]),
                    dbc.Col([

                            html.Div(
                                id='defender-circles-1',
                                children=[],
                                style={
                                    'display': 'flex',
                                    'justify-content': 'center',
                                    'flex-direction': 'column',
                                    'align-items': 'center',
                                    'margin-left': '-75%',
                                    'margin-bottom': '7%',
                                }
                            ),
                            html.Div(
                                id='defender-circles-2',
                                children=[],
                                style={
                                    'display': 'flex',
                                    'justify-content': 'center',
                                    'flex-direction': 'column',
                                    'align-items': 'center',
                                    'margin-left': '-100%',
                                    'margin-bottom': '7%',
                                }

                            ),
                            html.Div(
                                id='defender-circles-3',
                                children=[],
                                style={
                                    'display': 'flex',
                                    'justify-content': 'center',
                                    'flex-direction': 'column',
                                    'align-items': 'center',
                                    'margin-left': '-100%',
                                    'margin-bottom': '7%',
                                }
                            ),
                            html.Div(
                                id='defender-circles-4',
                                children=[],
                                style={
                                    'display': 'flex',
                                    'justify-content': 'center',
                                    'flex-direction': 'column',
                                    'align-items': 'center',
                                    'margin-left': '-75%',
                                }

                            )
                            ],
                            style={
                            'display': 'flex',
                            'justify-content': 'center',
                            'flex-direction': 'column',
                            'align-items': 'center',
                            }

                            ),
                    dbc.Col([
                        html.Div(
                            id='midfielder-circles-1',
                            children=[],
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'flex-direction': 'column',
                                'align-items': 'center',
                                'margin-left': '-130%',
                                'margin-bottom': '7%',
                            }

                        ),
                        html.Div(
                            id='midfielder-circles-2',
                            children=[],
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'flex-direction': 'column',
                                'align-items': 'center',
                                'margin-left': '-150%',
                                'margin-bottom': '7%',
                            }

                        ),
                        html.Div(
                            id='midfielder-circles-3',
                            children=[],
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'flex-direction': 'column',
                                'align-items': 'center',
                                'margin-left': '-130%'
                            }
                        ),]

                    ),
                    dbc.Col([
                        html.Div(
                            id='attacker-circles-1',
                            children=[],
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'flex-direction': 'column',
                                'align-items': 'center',
                                'margin-left': '-130%',
                                'margin-bottom': '7%',
                            }

                        ),
                        html.Div(
                            id='attacker-circles-2',
                            children=[],
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'flex-direction': 'column',
                                'align-items': 'center',
                                'margin-left': '-150%',
                                'margin-bottom': '7%',
                            }

                        ),
                        html.Div(
                            id='attacker-circles-3',
                            children=[],
                            style={
                                'display': 'flex',
                                'justify-content': 'center',
                                'flex-direction': 'column',
                                'align-items': 'center',
                                'margin-left': '-130%',
                            }

                        )]
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
    ], style={'height': '400px'}
    ),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Label('Player', style={
                                'color': 'Black', 'font-weight': 'bold'}),
                            dcc.Dropdown(id='current-dropdown',
                                         # options from callback
                                         options=[],  # multi=True,
                                         searchable=True,
                                         clearable=True,
                                         placeholder='Selected Player',
                                         optionHeight=75,
                                         style={'width': '90%'})
                        ], style={'width': '25%', 'display': 'inline-block', 'margin-right': '0px'}),
                        html.Div([
                            html.Label('Alternative 1', style={
                                'color': 'Black', 'font-weight': 'bold'}),
                            dcc.Dropdown(id='suggestion1-dropdown',
                                         options=[], multi=True,
                                         searchable=True,  # adds auto fill search option
                                         clearable=True,  # adds clear button to deselect players
                                         placeholder='Alternate 1',
                                         optionHeight=75,
                                         style={'width': '90%'})
                        ], style={'width': '25%', 'display': 'inline-block', 'margin-left': '-25px'}),
                        html.Div([
                            html.Label('Alternative 2', style={
                                'color': 'Black', 'font-weight': 'bold'}),
                            dcc.Dropdown(id='suggestion2-dropdown',
                                         options=[], multi=True,
                                         searchable=True,
                                         clearable=True,
                                         placeholder='Alternate 2',
                                         optionHeight=75,
                                         style={'width': '90%'})
                        ], style={'width': '25%', 'display': 'inline-block', 'margin-left': '-25px'})
                    ], width=8),
                ], style={
                    'height': '80px',
                    'position': 'relative',
                    'display': 'flex',
                    'margin-top': '+01%',
                    'margin-left': '+0%'
                },
                )
            ], style={'height': '100px', 'align-items': 'center'}),
            dbc.Row([
                html.Div([
                    dash_table.DataTable(id='stats-table',
                                         columns=[],  # table_columns,
                                         data=[], editable=True,
                                         style_cell={
                                             'minWidth': '200px', 'maxWidth': '250px'}
                                         )  # table_data)
                ], style={'width': '25%', 'display': 'inline-block'}
                )
            ], style={
                # 'width': '85%',
                'position': 'relative',
                'display': 'flex',
                'margin-top': '+02%',
                'margin-left': '-0%'
            },
            )

        ]),
        dbc.Col([
            html.Div([
                html.Div(id='compare-radial', className='text-center'),
                dcc.Graph(id='compare-radial-chart', style={'display': 'none'})
            ])
        ], width=5, style={
            'margin-top': '-60%',
            'margin-left': '+60%'
        })
    ])
], fluid=True)


# Define the modal window content

modal_body = html.Div([
    html.H5("Net Value Dashboard User Guide"),
    html.Br(),
    html.H6("Tab: PLAY STYLE"),
    html.P("Net Value is an innovative visualization tool designed to help understand the evolution of play styles for individual soccer players."),
    html.P("TLDR : Filter League, Season and Player (multiple selections supported) to update the scatter plot and radar plot. Scatter plot has hover, zoom, download, auto scaling and selection capabilities. View benchmark radar plots to view the centroid attributes."),
    html.Br(),
    html.P("This tab displays the results of the clustering analysis. More than 123K league-season-player combinations were clustered in 8 groups, namely, Goal Machine, Disciplined Anchor, Precision Agitator, Unruly Artisan, Adaptable Ace, Dual Catalyst, Pass Maestro and Steadfast Guardian. The interpretations for these clusters are listed below. The user can modify the League, Season and Player filters to get a selection of their choice. These filters support multiple selection. The scatter plot and the corresponding radar plot will be updated accordingly. In any particular selection, the visible clusters in the scatter plot can be selected/ deselected by clicking on the cluster labels on top of the scatter plot. Hovering over a particular point on the scatter plot shows details about that particular data point. The scatter plot can be zoomed in and out, auto-scaled, selected (box and lasso select) and downloaded as a png file using the tools bar at the top right of the plot. In the bottom section of this tab, users can see the radar plots of the cluster averages."),
    html.Br(),
    html.P("The eight clusters can be interpreted as below :"),
    html.Ol([
        html.Li("Goal Machine - Excellent in attack with high goal contributions"),
        html.Li(
            "Disciplined Anchor - Below average performances but good at game discipline"),
        html.Li(
            "Precision Agitator - Good shooting, excellent dribbling, committing and drawing a lot of fouls"),
        html.Li("Unruly Artisan - Jack of all trades, but poor in game discipline"),
        html.Li("Adaptable Ace - Extremely versatile performances"),
        html.Li("Dual Catalyst - Good attacking and midfield contributions"),
        html.Li("Pass Maestro - Good passers but moderate performance level"),
        html.Li("Steadfast Guardian - Good at defence but not versatile")
    ]),
    html.Br(),
    html.P("Radar Plots : The radar plots display aggregated scores in six distinct player traits : Passing, Dribbling, Shooting, Defending, Fouling, Goalkeeping. These plots update according to the current filter selection. The individual features in each of these traits are listed below."),
    html.Ol([
        html.Li("Passing - Total passes, key passes, pass accuracy and assists"),
        html.Li(
            "Dribbling - Dribbling attempts, successes, penalties won and fouls drawn"),
        html.Li(
            "Shooting - Goals scored, penalties scored, total shots and shots on target"),
        html.Li(
            "Defending - Total duels, duels won, tackles, blocks and interceptions"),
        html.Li(
            "Fouling - Fouls committed, yellow cards, red cards, double yellow and penalties committed"),
        html.Li("Goalkeeping - Total saves, goals conceded, penalties saved")
    ]),
    html.Br(),
    html.H6("Tab: DREAM TEAM"),
    html.P("TLDR: Select position to be filled in the team and filter League and Season to update the list of players and then choose a player to be selected into the team. Find all selected players in the player dropdown at the bottom of the page. Select one or two more league-season-player combinations to compare players and observe updated radar plots and features."),
    html.Br(),
    html.P("This tab allows users to build their own team by selecting players in each of the positions. The chosen format is 4-3-3, which means 4 Defenders, 3 Midfielders and 3 Attackers. These positions are their actual playing position in that particular league and season. To select players, select position from the Position dropdown and then select League and Season. Once League and Season are selected, the players list in the Player dropdown is updated and then the required player can be selected. After selection, observe the player being populated spatially in the team layout on the right. Other players can be selected similarly. When hovering over a player, you can view their team affiliation and the performance cluster they were assigned to during that particular league and season."),
    html.Br(),
    html.P("In the bottom section of this tab, one of the selected players can be compared to other players in order to find suitable player replacements in the user’s team. The tool allows users to compare to two other players at once. The corresponding radar plot shows the individual radar plots superimposed on each other. The individual radar plots can be selected/deselected by clicking on the player name above the plot. The list of features, for every 90 mins of gameplay, are also listed which can be used for deeper comparisons.")
])

modal = dbc.Modal(
    [
        dbc.ModalHeader("README"),
        modal_body,
        dbc.ModalFooter(
            dbc.Button("Close", id="close", className="ml-auto")
        ),
    ],
    id="modal",
    size='xl'
)

# Define the app layout
app.layout = dbc.Container(
    [
        # Define the info pop-up
        html.H3("Net Value: Combining AI and Soccer", className="text-center"),

        html.Div(
            [
                dcc.Location(id="url", refresh=False),

                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Tabs(
                                    [
                                        dbc.Tab(
                                            label="Play Styles",
                                            label_style={
                                                "color": "#00AEF9",
                                                "fontSize": "1rem",
                                            },
                                            tab_id="tab-1",
                                        ),
                                        dbc.Tab(
                                            label="Dream Team",
                                            label_style={
                                                "color": "#00AEF9",
                                                "fontSize": "1rem",
                                            },
                                            tab_id="tab-2",
                                        ),
                                    ],
                                    id="tabs",
                                    active_tab="tab-1",
                                    className="mb-3",
                                ),
                            ],
                            width=10,  # Adjust the width
                            className="d-flex align-items-center",  # Align the tabs vertically
                        ),
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Read Me",
                                    id="open",
                                    className="mb-3 btn-sm float-right",
                                ),
                                modal,
                            ],
                            width=2,  # Adjust the width
                            className="d-flex align-items-center",  # Align the button vertically
                        ),
                    ]
                ),
                html.Div(id="tab-content"),
            ],
            className="mb-4",
        ),
    ],
    fluid=True,
)


@app.callback(Output("tab-content", "children"), [Input("tabs", "active_tab")])
def display_tab_content(active_tab):
    if active_tab == "tab-1":
        return tab1_layout
    else:
        return tab2_layout

# Toggle the modal window


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [dash.dependencies.State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Define callback to update player options when league or season dropdowns change


@app.callback(Output('players', 'options'),
              Input('leagues', 'value'),
              Input('teams', 'value'),
              Input('seasons', 'value'))
@timing_decorator
def update_player_options(league, team, season):
    filtered_df = player_data
    if league:
        filtered_df = filtered_df[filtered_df['league_id'].isin(
            [int(x) for x in league])]
    if team:
        filtered_df = filtered_df[filtered_df['team_id'].isin(
            [int(x) for x in team])]
    if season:
        filtered_df = filtered_df[(
            filtered_df['league_season'].isin([int(x) for x in season]))]

    player_options = [{'label': str(row['player_firstname']) + " " + str(row['player_lastname']),
                       'value': int(row['player_id'])}
                      for index, row in filtered_df.iterrows()]
    return player_options

# Define callback to update team options when league or season dropdowns change


@app.callback(Output('teams', 'options'),
              Input('leagues', 'value'),
              Input('seasons', 'value'))
@timing_decorator
def update_team_options(league, season):
    filtered_df = player_data
    if league:
        filtered_df = filtered_df[filtered_df['league_id'].isin(
            [int(x) for x in league])]
    if season:
        filtered_df = filtered_df[(
            filtered_df['league_season'].isin([int(x) for x in season]))]

    team_options = [{'label': str(row['team_name']),
                     'value': int(row['team_id'])}
                    for index, row in filtered_df.drop_duplicates(subset=['team_name', 'team_id']).iterrows()]
    return team_options


# Define a callback to update the dynamic radial chart based on data filters
@app.callback(
    Output('dynamic-radial-chart', 'figure'),
    [Input('leagues', 'value'),
     Input('teams', 'value'),
     Input('seasons', 'value'),
     Input('players', 'value')]
)
@timing_decorator
def update_radial_chart(league, team, season, player):

    filtered_df = player_data
    if league:
        filtered_df = filtered_df[filtered_df['league_id'].isin(
            [int(x) for x in league])]
    if team:
        filtered_df = filtered_df[filtered_df['team_id'].isin(
            [int(x) for x in team])]
    if season:
        filtered_df = filtered_df[(
            filtered_df['league_season'].isin([int(x) for x in season]))]
    if player:
        filtered_df = filtered_df[(filtered_df['player_id']).isin([
            int(x) for x in player])]

    # print(league, season, player)
    # print(filtered_df[["league_id", "league_name",
    #      "league_season", "player_id"]])

    radial_data = filtered_df[['passing',
                               'defending', 'fouling', 'dribbling', 'shooting', 'goalkeeping']].mean()

    r = radial_data.values
    r = np.clip(r, None, 0.5)
    theta = theta_metrics
    hover_text = [f"{theta[i]}: {round(r[i], 3)}" for i in range(len(theta))]

    dynamic_chart = go.Figure(go.Scatterpolar(r=r, theta=theta, fill='toself',
                                              hovertemplate=hover_text,
                                              customdata=list(
                                                  range(len(theta_metrics))),
                                              hoverlabel=dict(namelength=-1)))

    dynamic_chart.update_layout(
        showlegend=False,
        polar=dict(
            radialaxis=dict(
                range=[0, 0.5],  # Set a constant range for the radial axis
            ),
            angularaxis=dict()
        ),
        title=dict(

            y=0.9,
            x=0.5,
            xanchor="center"
        ),
        margin=dict(t=40)
    )

    return dynamic_chart


@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('leagues', 'value'),
     Input('teams', 'value'),
     Input('seasons', 'value'),
     Input('players', 'value')]
)
@timing_decorator
def update_scatter_plot(league, team, season, player):

    selected_data = copy.deepcopy(player_data)

    filtered_df = player_data
    if league:
        filtered_df = filtered_df[filtered_df['league_id'].isin(
            [int(x) for x in league])]
    if team:
        filtered_df = filtered_df[filtered_df['team_id'].isin(
            [int(x) for x in team])]
    if season:
        filtered_df = filtered_df[(
            filtered_df['league_season'].isin([int(x) for x in season]))]
    if player:
        filtered_df = filtered_df[(filtered_df['player_id']).isin([
            int(x) for x in player])]

    selected_data.loc[~selected_data.index.isin(
        filtered_df.index.values), 'cluster'] = -1

    scatter_plot = go.Figure()
    # print(selected_data.cluster.value_counts())

    for cluster, label in list(cluster_labels.items())[::-1]:
        ratio = 0.1
        if cluster != -1 and ((player or season or league or team)):
            ratio = 1.0

        trace_df = selected_data[selected_data['cluster']
                                 == cluster].sample(frac=ratio)
        trace_df['label'] = trace_df['cluster'].apply(
            lambda x: cluster_labels[x])
        scatter_plot.add_trace(go.Scatter(x=trace_df['x'], y=trace_df['y'],
                                          customdata=trace_df[[
                                              'league_season', 'league_name', 'player_name', 'games_position', 'team_name', 'league_country']],
                                          mode='markers',
                                          hovertemplate=(
            # Player name
            "<b>%{customdata[2]}</b> (%{customdata[3]})<br>"
            # League season
            "%{customdata[4]} (%{customdata[0]})<br>"
            # League name
            "%{customdata[1]} - %{customdata[5]}<br>"
            "<extra></extra>"
        ),
            marker=dict(color=color_codes[label]), name=label))

    scatter_plot.update_layout(width=scatter_plot_width, height=scatter_plot_length,
                               yaxis=dict(range=[ymin - 20, ymax + 20]), xaxis=dict(range=[xmin - 20, xmax + 20]),
                               legend=dict(
                                   orientation="h",  # Set the legend orientation to horizontal
                                   xanchor="center",  # Anchor the legend horizontally to the center
                                   yanchor="top",     # Anchor the legend vertically to the top
                                   x=0.5,             # Position the legend in the center of the x-axis
                                   y=1.1,             # Position the legend slightly above the plot area
                               ))

    return scatter_plot


# Common variables for tab2
# Create an empty table with the required columns
"""
table_columns = [{'name': 'Performance', 'id': 'Performance'},
                 {'name': 'Selected Player', 'id': 'Selected Player',
                     'presentation': 'dropdown'},
                 {'name': 'Alternate Player 1', 'id': 'Alternate Player 1',
                     'presentation': 'dropdown'},
                 {'name': 'Alternate Player 2', 'id': 'Alternate Player 2', 'presentation': 'dropdown'}]
table_data = []
feats = ['passing', 'defending', 'fouling',
         'dribbling', 'shooting', 'goalkeeping']

player_positions = ['Goalkeeper', 'Defender-1', 'Defender-2', 'Defender-3', 'Defender-4',
                    'Midfielder-1', 'Midfielder-2', 'Midfielder-3', 'Attacker-1', 'Attacker-2', 'Attacker-3']
"""

# call backs for tab2 upper part


@app.callback(
    Output('player-select-tab2', 'options'),
    Input('league-tab2', 'value'),
    Input('season-tab2', 'value'),
    Input('player-position-tab2', 'value')
)
@timing_decorator
def set_player_options(selected_league, selected_season, selected_position):
    if selected_position is not None:
        if selected_position == 'Goalkeeper':
            df_filtered = player_data[(player_data['league_id'] == selected_league) & (
                player_data['league_season'] == selected_season) & (player_data['games_position'] == selected_position)]
        else:
            df_filtered = player_data[(player_data['league_id'] == selected_league) & (
                player_data['league_season'] == selected_season) & (player_data['games_position'].str.contains(selected_position[:-2]))]

        if not df_filtered.empty:
            return [{'label': i, 'value': i} for i in df_filtered['player_name'].unique()]
    return []

# callback for season dropdown, shows only available seasons for selected league


@app.callback(
    Output('season-tab2', 'options'),
    Input('league-tab2', 'value')
)
@timing_decorator
def set_season_options(selected_league):
    df_filtered = player_data[player_data['league_id'] == selected_league]
    return [{'label': str(i), 'value': i} for i in df_filtered['league_season'].unique()]


selected_players = []


def fetch_player_image(player_name, player_dict, player_card):
    temp_dict = copy.deepcopy(player_dict)
    if player_name is None:
        return html.Div()
    player_info = player_data[player_data['player_name']
                              == player_name].iloc[0]
    player_photo_url = player_info['player_photo']
    # delete player_name from player_dict
    # getting the league name- league_country using the league_id and concatenating it update the player_dict with the league name
    temp_league_name = player_info['league_name']
    league_country = player_info['league_country']
    league_name = temp_league_name + ' - ' + league_country
    # print(league_name, flush=True)
    temp_dict['league_name'] = league_name
    temp_dict.pop('player_name', None)
    temp_dict.pop('league_id', None)
    temp_dict.pop('league', None)
    # print(temp_dict, flush=True)

    return (html.Div(title=str(player_card),

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
        html.Div(player_name, style={
            'font-size': '12px', 'color': '#ffff', 'font-weight': 'bold', 'background-color': '#FF5733',
            'padding': '5px',
            'border-radius': '5px'}))

# global goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3


already_selected_players = []

goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3 = (html.Div(), html.Div()), (html.Div(
), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div())


@app.callback(
    [Output('goalkeeper-circles', 'children'),
     Output('defender-circles-1', 'children'),
     Output('defender-circles-2', 'children'),
     Output('defender-circles-3', 'children'),
     Output('defender-circles-4', 'children'),
     Output('midfielder-circles-1', 'children'),
     Output('midfielder-circles-2', 'children'),
     Output('midfielder-circles-3', 'children'),
     Output('attacker-circles-1', 'children'),
     Output('attacker-circles-2', 'children'),
     Output('attacker-circles-3', 'children'),
     Output("player-store", "data")],
    Input('add-player-button', 'n_clicks'),
    Input('clear-players-button', 'n_clicks'),
    Input({'type': 'remove-player-button', 'index': ALL}, 'n_clicks'),
    State('player-position-tab2', 'value'),
    State('league-tab2', 'value'),
    State('season-tab2', 'value'),
    State('player-select-tab2', 'value'),
    State('selected-players', 'children'),
)
@timing_decorator
def update_selected_players(n_clicks_add, n_clicks_clear, n_clicks_remove,
                            position, league, season, player, selected_players_divs):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split(
        '.')[0] if ctx.triggered else ''
    global selected_players
    global goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3
    global already_selected_players
    if n_clicks_add is None:
        selected_players = []
        already_selected_players = []
        goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3 = (html.Div(), html.Div()), (html.Div(
        ), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div())
    elif n_clicks_add < 2:
        goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3 = (html.Div(), html.Div()), (html.Div(
        ), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div())

    if button_id == 'add-player-button' and player:
        player_dict = {
            'position': position,
            'league': league,
            'season': season,
            'player_name': player
        }
        if player_dict not in selected_players:
            # filter player_data using league_id, season_id, player_name
            df_filtered = player_data[(player_data['league_id'] == league) & (
                player_data['league_season'] == season) & (player_data['player_name'] == player)]
            # print(df_filtered)
            player_cluster = df_filtered['cluster'].values[0]
            player_team = df_filtered['team_name'].values[0]
            season_str = str(season)
            league_name = df_filtered['league_name'].values[0]
            cluster_name = cluster_labels[player_cluster]

            # format above strings to be displayed in the player card like player_team(season_str)\nleague_name\ncluster_name
            player_card = player_team + \
                ' (' + season_str + ')' + '\n' + \
                league_name + '\n' + cluster_name
            # print(player_card)
            selected_players.append(player_dict)
    if player not in already_selected_players:
        if position == 'Goalkeeper':
            already_selected_players.append(player)
            goalkeeper_circle_1 = fetch_player_image(
                player, player_dict, player_card)
            return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]
        elif position == 'Defender-1':
            already_selected_players.append(player)
            defender_circles_1 = fetch_player_image(
                player, player_dict, player_card)
            return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]
        elif position == 'Defender-2':
            already_selected_players.append(player)
            defender_circles_2 = fetch_player_image(
                player, player_dict, player_card)
            return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]
        elif position == 'Defender-3':
            already_selected_players.append(player)
            defender_circles_3 = fetch_player_image(
                player, player_dict, player_card)
            return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]
        elif position == 'Defender-4':
            already_selected_players.append(player)
            defender_circles_4 = fetch_player_image(
                player, player_dict, player_card)
            return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]
        elif position == 'Midfielder-1':
            already_selected_players.append(player)
            midfielder_circles_1 = fetch_player_image(
                player, player_dict, player_card)
            return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]
        elif position == 'Midfielder-2':
            already_selected_players.append(player)
            midfielder_circles_2 = fetch_player_image(
                player, player_dict, player_card)
            return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]
        elif position == 'Midfielder-3':
            already_selected_players.append(player)
            midfielder_circles_3 = fetch_player_image(
                player, player_dict, player_card)
            return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]
        elif position == 'Attacker-1':
            already_selected_players.append(player)
            attacker_circle_1 = fetch_player_image(
                player, player_dict, player_card)
            return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]
        elif position == 'Attacker-2':
            already_selected_players.append(player)
            attacker_circle_2 = fetch_player_image(
                player, player_dict, player_card)
            return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]
        elif position == 'Attacker-3':
            already_selected_players.append(player)
            attacker_circle_3 = fetch_player_image(
                player, player_dict, player_card)
            return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]

    if button_id == 'clear-players-button':
        selected_players = []
        already_selected_players = []
        goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3 = (html.Div(), html.Div()), (html.Div(
        ), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div()), (html.Div(), html.Div())
        return [goalkeeper_circle_1, defender_circles_1, defender_circles_2, defender_circles_3, defender_circles_4, midfielder_circles_1, midfielder_circles_2, midfielder_circles_3, attacker_circle_1, attacker_circle_2, attacker_circle_3, selected_players]

# callbacks for tab2 lower section

# Define a callback to update the dynamic radial chart for player comparision


@app.callback(
    [Output('compare-radial-chart', 'figure'),
     Output('compare-radial-chart', 'style')],
    [Input('current-dropdown', 'value'),
     Input('player-store', 'data'),
     Input('suggestion1-dropdown', 'value'),
     Input('suggestion2-dropdown', 'value')]
)
@timing_decorator
def update_radial_chart(player1, playingxi, player2=None, player3=None):

    layout = go.Layout(margin=go.layout.Margin(
        l=0,  # left margin
        r=0,  # right margin
        b=0,  # bottom margin
        t=0,  # top margin
    )
    )
    fig = go.Figure(layout=layout)

    if player1:
        c = ['#FF4136', '#0074D9', '#FF851B']
        # """
        for p in playingxi:
            if (player1 == p['player_name']):
                # reqpos = p['position']
                league = p['league']
                season = p['season']
        filter_data = player_data[(player_data['league_id'] == league) &
                                  (player_data['league_season'] == season)]
        # """
        # return dynamic_chart
        p1data = filter_data[filter_data['player_name'] == str(player1)]
        p1data = p1data[feats].iloc[0]
        feat_cols = [col for col in p1data.keys()]
        vals1 = [i for i in p1data.values]
        trace1 = go.Scatterpolar(r=vals1, theta=feat_cols, fill='toself',
                                 fillcolor=c[0], name=str(player1),
                                 line=dict(color=c[0]), opacity=0.3)
        if player2:
            p2data = player_data.loc[player2[0]]
            vals2 = [i for i in p2data[feat_cols].values]
            trace2 = go.Scatterpolar(r=vals2, theta=feat_cols, fill='toself',
                                     fillcolor=c[1], name=p2data['player_name'],
                                     line=dict(color=c[1]), opacity=0.3)
        else:
            p2data = [0*i for i in p1data]
            vals2 = p2data
            trace2 = go.Scatterpolar(r=vals2, theta=feat_cols, fill='toself',
                                     fillcolor=c[1], name=str(player2),
                                     line=dict(color=c[1]), opacity=0.3)
        if player3:
            p3data = player_data.loc[player3[0]]
            vals3 = [i for i in p3data[feat_cols].values]
            trace3 = go.Scatterpolar(r=vals3, theta=feat_cols, fill='toself',
                                     fillcolor=c[2], name=p3data['player_name'],
                                     line=dict(color=c[2]), opacity=0.3)
        else:
            p3data = [0*i for i in p1data]
            vals3 = p3data
            trace3 = go.Scatterpolar(r=vals3, theta=feat_cols, fill='toself',
                                     fillcolor=c[2], name=str(player3),
                                     line=dict(color=c[2]), opacity=0.3)

        fig.add_trace(trace1)
        fig.add_trace(trace2)
        fig.add_trace(trace3)
        fig.update_layout(legend=dict(
            orientation='h',
            yanchor='top',
            y=1.25,
            xanchor='left',
            x=0.15
        )
        )
        # print(fig.layout())

        return fig, {'display': 'block'}
    return fig, {'display': 'none'}

# callback to update option for current player


@app.callback(
    Output('current-dropdown', 'options'),
    Input('player-store', 'data')
)
@timing_decorator
def update_selected_dropdown(playingxi):
    options = []
    if playingxi:
        for d in playingxi:
            options.append(d['player_name'])
    return options

# callback to update option for atl 1


@app.callback(
    Output('suggestion1-dropdown', 'options'),
    [Input('current-dropdown', 'value'),
     Input('player-store', 'data'),
     Input('suggestion1-dropdown', 'value'),
     Input('suggestion2-dropdown', 'value')]
)
@timing_decorator
def update_suggest_dropdown1(main_player, playingxi, select1=None, select2=None):
    if main_player:
        for p in playingxi:
            if (main_player == p['player_name']):
                reqpos = p['position']
                if (reqpos != 'Goalkeeper'):
                    reqpos = reqpos[:-2]
                league = p['league']
                season = p['season']
        if (reqpos[0] == "G"):
            return gk_options
        elif (reqpos[0] == "D"):
            return def_options
        elif (reqpos[0] == "M"):
            return mid_options
        elif (reqpos[0] == "A"):
            return atk_options
        """
        filter_data = player_data[player_data['games_position']==reqpos]
        p1data = filter_data[(filter_data['league_id'] == league) &
                                   (filter_data['player_name'] == main_player) &
                                   (filter_data['league_season'] == season)]
        filter_data = filter_data.drop(p1data.index[0],axis='index')
        if select2 is not None:
            filter_data = filter_data.drop(int(select2[0]),axis='index')
        
        suggest_options = [{'label': str(row['player_name']) + " - " + str(row['league_name']) + " - " + str(row['league_season']),
                 'value': index}
                for index, row in filter_data.drop_duplicates(subset=['league_name', 'league_season','player_name']).iterrows()]
        return suggest_options

        filter_data = player_data[(player_data['league_id'] == league) &
                                  (player_data['league_season'] == season) &
                                  (player_data['games_position'] == reqpos)]
        reqdata = filter_data['player_name'].unique()
        remove_list = [main_player]
        if select2 is not None:
            remove_list.append(select2[0])
        req_options = [{'label': str(i), 'value': str(i)}
                       for i in reqdata if str(i) not in remove_list]
        return req_options
        """
    return []

# callback to update option for atl 1


@app.callback(
    Output('suggestion2-dropdown', 'options'),
    [Input('current-dropdown', 'value'),
     Input('player-store', 'data'),
     Input('suggestion1-dropdown', 'value'),
     Input('suggestion2-dropdown', 'value')]
)
@timing_decorator
def update_suggest_dropdown2(main_player, playingxi, select1=None, select2=None):
    if main_player:
        for p in playingxi:
            if main_player == p['player_name']:
                reqpos = p['position']
                if (reqpos != 'Goalkeeper'):
                    reqpos = reqpos[:-2]
                league = p['league']
                season = p['season']
        if (reqpos[0] == "G"):
            return gk_options
        elif (reqpos[0] == "D"):
            return def_options
        elif (reqpos[0] == "M"):
            return mid_options
        elif (reqpos[0] == "A"):
            return atk_options
        """
        filter_data = player_data[player_data['games_position']==reqpos]
        p1data = filter_data[(filter_data['league_id'] == league) &
                                   (filter_data['player_name'] == main_player) &
                                   (filter_data['league_season'] == season)]
        filter_data = filter_data.drop(p1data.index[0],axis='index')
        if select1 is not None:
            filter_data = filter_data.drop(int(select1[0]),axis='index')        
        suggest_options = [{'label': str(row['player_name']) + " - " + str(row['league_name']) + " - " + str(row['league_season']),
                 'value': index}
                for index, row in filter_data.drop_duplicates(subset=['league_name', 'league_season','player_name']).iterrows()]
        return suggest_options
    
        filter_data = player_data[(player_data['league_id'] == league) &
                                  (player_data['league_season'] == season) &
                                  (player_data['games_position'] == reqpos)]
        reqdata = filter_data['player_name'].unique()
        remove_list = [main_player]
        if select1 is not None:
            remove_list.append(select1[0])
        req_options = [{'label': str(i), 'value': str(i)}
                       for i in reqdata if str(i) not in remove_list]
        return req_options
        """
    return []

# callback to limit selections to one player


@app.callback(
    [Output('suggestion1-dropdown', 'value'),
     Output('suggestion2-dropdown', 'value')],
    [Input('suggestion1-dropdown', 'value'),
     Input('suggestion2-dropdown', 'value')]
)
def limit_selections(values1, values2):
    if values1 is not None and len(values1) > 1:
        values1 = values1[0]
    if values2 is not None and len(values2) > 1:
        values2 = values2[0]
    return values1, values2

# Callback for table data


@app.callback(
    [Output('stats-table', 'data'),
     Output('stats-table', 'columns')],
    [Input('current-dropdown', 'value'),
     Input('player-store', 'data'),
     Input('suggestion1-dropdown', 'value'),
     Input('suggestion2-dropdown', 'value')]
)
@timing_decorator
def update_table(player1, playingxi, player2=None, player3=None):
    if player1:
        for p in playingxi:
            if player1 == p['player_name']:
                reqpos = p['position']
                league = p['league']
                season = p['season']
        filter_data = player_data[(player_data['league_id'] == league) &
                                  (player_data['league_season'] == season)]
        p1data = filter_data[filter_data['player_name'] == str(player1)]
        feats_table = [k for k in feats_table_dict.keys()]
        p1data = p1data[feats_table].iloc[0]
        feat_cols, vals1 = [], []
        feat_cols = feats_table  # [col for col in p1data.keys()]
        vals1 = [i for i in p1data.values]
        if player2:
            p2data = player_data.loc[player2[0]]
            # p2data = filter_data[filter_data['player_name'] == str(player2[0])]
            # p2data = p2data[feats].iloc[0]
            vals2 = []
            vals2 = [i for i in p2data[feat_cols].values]
        else:
            vals2 = []
            vals2 = [0*i for i in p1data]
        if player3:
            p3data = player_data.loc[player3[0]]
            # p3data = filter_data[filter_data['player_name'] == str(player3[0])]
            # p3data = p3data[feats].iloc[0]
            vals3 = []
            vals3 = [i for i in p3data[feat_cols].values]
        else:
            vals3 = []
            vals3 = [0*i for i in p1data]
        data_mat = []
        data_mat.append(['Selected Player',
                         'Alternate Player 1',
                         'Alternate Player 2',
                         'Performance (per 90 mins)'])
        for i in range(len(feat_cols)):
            row = [vals1[i], vals2[i], vals3[i],
                   feats_table_dict[feat_cols[i]]]
            data_mat.append(row)
        data_df = pd.DataFrame(data=data_mat[1:], columns=data_mat[0])
        data_df.fillna(0, inplace=True)

        data = data_df.round(3).to_dict('records')
        return data, table_columns
    return [], []


if __name__ == '__main__':
    app.run_server(debug=False)
