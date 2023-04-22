import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import copy
import numpy as np

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
scatter_plot_width = 1000
scatter_plot_length = 650


centroids_data = pd.read_csv('dashboard/centroids.csv')[['passing',
       'defending', 'fouling', 'dribbling', 'shooting', 'goalkeeping']]
# centroids_data['fouling'] = 1- centroids_data['fouling']

cluster_labels = {0: 'Goal Machine',
                  1: 'Disciplined Anchor',
                  2: 'Precision Agitator',
                  3: 'Unruly Artisan',
                  4: 'Role Specialist',
                  5: 'Dual Catalyst',
                  6: 'Pass Maestro',
                  7: 'Steadfast Guardian',
                  -1: 'Not Selected'}

color_codes = {
    'Goal Machine': '#FF4136',      # Red
    'Disciplined Anchor': '#0074D9', # Blue
    'Precision Agitator': '#FF851B', # Orange
    'Unruly Artisan': '#FFDC00',     # Yellow
    'Role Specialist': '#2ECC40',    # Green
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
        (4, 'Role Specialist'),
        (6, 'Pass Maestro')
    ],
    [
        (3, 'Unruly Artisan'),
        (7, 'Steadfast Guardian')
    ]
]



player_data = pd.read_csv("dashboard/output.csv")
player_data.fillna(-1, inplace = True)
# Extract Player IDs and League Info
player_options = [{'label': str(row['player_firstname']) + " " + str(row['player_lastname']), 
                   'value': int(row['player_id'])} 
                  for index, row in player_data.iterrows()]
league_options = [{'label': str(row['league_name'] + " - " + str(row['league_country'])), 
                   'value': int(row['league_id'])} 
                  for index, row in player_data.drop_duplicates(subset=['league_name', 'league_id']).iterrows()]
season_options = [{'label': str(row['league_season']), 
                   'value': int(row['league_season'])} 
                  for index, row in player_data.drop_duplicates(subset=['league_season']).iterrows()]
team_options = [{'label': str(row['team_name']), 
                   'value': int(row['team_id'])} 
                  for index, row in player_data.drop_duplicates(subset=['team_name', 'team_id']).iterrows()]

# player_options = [{'label': '', 'value': ''}]

xmin, xmax = player_data['x'].min(), player_data['x'].max()
ymin, ymax = player_data['y'].min(), player_data['y'].max()


# Create a scatter plot
scatter_plot = go.Figure()

for cluster, label in cluster_labels.items():
    filtered_df = player_data[player_data['cluster'] == cluster].sample(frac=0.1)
    scatter_plot.add_trace(go.Scatter(x=filtered_df['x'], y=filtered_df['y'], mode='markers', marker=dict(color=color_codes[label]), name=label))

# Update the layout if needed
scatter_plot.update_layout(width=scatter_plot_width, height=scatter_plot_length,
                           yaxis=dict(range=[ymin - 20, ymax + 20]),xaxis=dict(range=[xmin -20, xmax + 20]),
                           legend=dict(
        orientation="h",  # Set the legend orientation to horizontal
        xanchor="center",  # Anchor the legend horizontally to the center
        yanchor="top",     # Anchor the legend vertically to the top
        x=0.5,             # Position the legend in the center of the x-axis
        y=1.1,             # Position the legend slightly above the plot area
    ))

# Create static radial charts
theta_metrics = ['Passing','Defending', 'Fouling', 'Dribbling', 'Shooting', 'Goalkeeping']
radial_charts = []
for grouping in grouped_playstyles:
    for line in grouping:
        radial_chart_1 = go.Figure()
        centroid_values = centroids_data.iloc[line[0]].values
        centroid_values = np.clip(centroid_values, 0, 0.5)

        hover_text = [f"{theta_metrics[i]}: {round(centroid_values[i], 3)}" for i in range(len(theta_metrics))]
        radial_chart_1.add_trace(go.Scatterpolar(r=centroid_values, 
                                                theta=theta_metrics, name=line[1],fill='toself',
                                             line=dict(color=color_codes[line[1]]),
                                             hovertemplate=hover_text,
                                            customdata=list(range(len(theta_metrics))),
                                            hoverlabel=dict(namelength=-1)))

        
        radial_chart_1.update_layout(
            showlegend=False,
            polar=dict(
            radialaxis=dict(
                range=[0, 0.5],  # Set a constant range for the radial axis centroids_data.max().max()
                ),
            angularaxis=dict()
            ),
            title=dict(
                text=line[1],
                font=dict(size=24, color=color_codes[line[1]]),
                y=0.9   ,
                x=0.5,
                xanchor="center"
            ),
            margin=dict(t=40)
        )

        radial_charts.append(radial_chart_1)

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

# Define the modal window content
modal = dbc.Modal(
    [
        dbc.ModalHeader("README"),
        dbc.ModalBody(
            """
            This is a simple Dash app that demonstrates how to create a pop-up README window. To use this app, click the 'Info' button to display the instructions.
            """
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close", className="ml-auto")
        ),
    ],
    id="modal",
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
                                            label="Tab 1",
                                            label_style={
                                                "color": "#00AEF9",
                                                "fontSize": "1rem",
                                            },
                                            tab_id="tab-1",
                                        ),
                                        dbc.Tab(
                                            label="Tab 2",
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
        return html.Div("Tab 2 content goes here")

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


# # Define a callback to update the dynamic radial chart header based on data filters
# @app.callback(
#     Output('dynamic-header', 'children'),
#     [Input('leagues', 'value'),
#      Input('teams', 'value'),
#      Input('seasons', 'value'),
#      Input('players', 'value')]
# )
# def update_dynamic_header(league, team, season, player):
#     header_text = "{} - {} -{}- {}".format(league, team,season, player)
#     return header_text

# Define callback to update player options when league or season dropdowns change
@app.callback(Output('players', 'options'),
              Input('leagues', 'value'),
              Input('teams', 'value'),
              Input('seasons', 'value'))
def update_player_options(league, team, season):
    filtered_df = player_data
    if league:
        filtered_df = filtered_df[filtered_df['league_id'].isin([int(x) for x in league ])]
    if team:
        filtered_df = filtered_df[filtered_df['team_id'].isin([int(x) for x in team ])]
    if season:
        filtered_df = filtered_df[(filtered_df['league_season'].isin([int(x) for x in season ]))]

    player_options = [{'label': str(row['player_firstname']) + " " + str(row['player_lastname']), 
                   'value': int(row['player_id'])} 
                  for index, row in filtered_df.iterrows()]
    return player_options

# Define callback to update team options when league or season dropdowns change
@app.callback(Output('teams', 'options'),
              Input('leagues', 'value'),
              Input('seasons', 'value'))
def update_team_options(league, season):
    filtered_df = player_data
    if league:
        filtered_df = filtered_df[filtered_df['league_id'].isin([int(x) for x in league ])]
    if season:
        filtered_df = filtered_df[(filtered_df['league_season'].isin([int(x) for x in season ]))]

    team_options = [{'label': str(row['team_name']), 
                   'value': int(row['team_id'])} 
                  for index, row in filtered_df.drop_duplicates(subset=['team_name', 'team_id']).iterrows()]
    return team_options

# # Define callback to update player dropdown options when player options data changes
# @app.callback(Output('player-dropdown', 'options'),
#               Input('player-options-store', 'data'))
# def update_player_dropdown(player_options):
#     return player_options


# Define a callback to update the dynamic radial chart based on data filters
@app.callback(
    Output('dynamic-radial-chart', 'figure'),
    [Input('leagues', 'value'),
     Input('teams', 'value'),
     Input('seasons', 'value'),
     Input('players', 'value')]
)
def update_radial_chart(league, team, season, player):

    filtered_df = player_data
    if league:
        filtered_df = filtered_df[filtered_df['league_id'].isin([int(x) for x in league ])]
    if team:
        filtered_df = filtered_df[filtered_df['team_id'].isin([int(x) for x in team ])]
    if season:
        filtered_df = filtered_df[(filtered_df['league_season'].isin([int(x) for x in season ]))]
    if player:
        filtered_df = filtered_df[(filtered_df['player_id']).isin([int(x) for x in player ])]

    print(league, season, player)
    print(filtered_df[["league_id", "league_name", "league_season", "player_id"]])

    radial_data = filtered_df[['passing',
       'defending', 'fouling', 'dribbling', 'shooting', 'goalkeeping']].mean()
    
    r = radial_data.values
    r = np.clip(r, None, 0.5)
    theta = theta_metrics
    hover_text = [f"{theta[i]}: {round(r[i], 3)}" for i in range(len(theta))]


    dynamic_chart = go.Figure(go.Scatterpolar(r=r, theta=theta, fill='toself', 
                                              hovertemplate=hover_text,
                                                customdata=list(range(len(theta_metrics))),
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

                y=0.9   ,
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
def update_scatter_plot(league, team, season, player):

    selected_data = copy.deepcopy(player_data)

    filtered_df = player_data
    if league:
        filtered_df = filtered_df[filtered_df['league_id'].isin([int(x) for x in league ])]
    if team:
        filtered_df = filtered_df[filtered_df['team_id'].isin([int(x) for x in team ])]
    if season:
        filtered_df = filtered_df[(filtered_df['league_season'].isin([int(x) for x in season ]))]
    if player:
        filtered_df = filtered_df[(filtered_df['player_id']).isin([int(x) for x in player ])]


    selected_data.loc[~selected_data.index.isin(filtered_df.index.values), 'cluster'] = -1

    scatter_plot = go.Figure()
    print(selected_data.cluster.value_counts())

    for cluster, label in list(cluster_labels.items())[::-1]:
        ratio = 0.1
        if cluster != -1 and ((player or season or league or team)):
            ratio = 1.0

        trace_df = selected_data[selected_data['cluster'] == cluster].sample(frac=ratio)
        trace_df['label'] = trace_df['cluster'].apply(lambda x : cluster_labels[x])
        scatter_plot.add_trace(go.Scatter(x=trace_df['x'], y=trace_df['y'], 
                                          customdata=trace_df[['league_season', 'league_name', 'player_name', 'games_position', 'team_name', 'league_country']],
                                        mode='markers',
                                        hovertemplate=(
                                            "<b>%{customdata[2]}</b> (%{customdata[3]})<br>"  # Player name
                                            "%{customdata[4]} (%{customdata[0]})<br>"  # League season
                                            "%{customdata[1]} - %{customdata[5]}<br>"  # League name
                                            "<extra></extra>"
                                        ),
                                        marker=dict(color=color_codes[label]), name=label))

    scatter_plot.update_layout(width=scatter_plot_width, height=scatter_plot_length,
                                yaxis=dict(range=[ymin - 20, ymax + 20]),xaxis=dict(range=[xmin -20, xmax + 20]),
                                legend=dict(
        orientation="h",  # Set the legend orientation to horizontal
        xanchor="center",  # Anchor the legend horizontally to the center
        yanchor="top",     # Anchor the legend vertically to the top
        x=0.5,             # Position the legend in the center of the x-axis
        y=1.1,             # Position the legend slightly above the plot area
    ))

    return scatter_plot
if __name__ == '__main__':
    app.run_server(debug=False)
