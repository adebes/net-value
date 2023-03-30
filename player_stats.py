import json
import requests
from ratelimit import limits, sleep_and_retry

MINUTE = 60
CALLS = 450 #use 30 if using the Basic (free) API plan

headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': "6f2169a92cmshe15752e67adad31p1e5025jsnddc863e73853"
}

# Get all available seasons
#
# Output: a list of all seasons (i.e. years) as strings
def get_seasons(start: int = None, end: int = None) -> list[int]:
    r = requests.get("https://api-football-v1.p.rapidapi.com/v3/leagues/seasons",
                     headers=headers)

    # throw error if query not successful
    if r.status_code != 200:
        raise Exception('API response: {}'.format(r.status_code))

    seasons = r.json()['response']

    start = seasons[0] if (start == None) else start
    end = seasons[-1] if (end == None) else end

    return [year for year in seasons if (year >= start and year <= end)]


# Given a list of leagues, get all teams that belong to each league in a given
# season.
#
# Input:
#   league_ids: list of str representing ids of all leagues
#   season: str representing year of the season
#
# Output: a list of all teams in the leagues
#           [{"team1": {...}, "venue1": {...}},
#           {"team2": {...}, "venue2": {...}},
#           ...]
@sleep_and_retry
@limits(calls=CALLS, period=MINUTE)
def get_teams(league_ids: list[str], season: str):
    teams = []

    for league_id in league_ids:
        payload = {
            "league": league_id,
            "season": season
        }

        r = requests.get("https://api-football-v1.p.rapidapi.com/v3/teams",
                        headers=headers,
                        params=payload)

        # throw error if query not successful
        if r.status_code != 200:
            raise Exception('API response: {}'.format(r.status_code))

        teams += r.json()['response']

    return teams


# Given a list of leagues, get all players that belong to each league in a given
# season.
#
# Input:
#   league_ids: list of str representing ids of all leagues
#   season: str representing year of the season
#
# Output: a list of all players in the leagues
#           [{"player1": {...}, "statistics1": {...}},
#           {"player2": {...}, "statistics2": {...}},
#           ...]
def get_players(league_ids: list[str], seasons: list[str]) -> list:
    players = []

    for league_id in league_ids:
        for season in seasons:
            print("Starting - League:", league_id, "Season:", season)
            print()
            try:
                get_players_helper(league_id, season, players, 1)
            except Exception as e:
                print(e)
            print()
            
            with open("players.json", "w") as out:
                out.write(json.dumps(players))
        
    return players


# Helper function to recursively get all players in a league for a given season.
#
# Input:
#   league_id: str representing ids of a given leagues
#   season: str representing year of the season
#
# Output: None; updates "players" parameter with all players in the
# league/season.
@sleep_and_retry
@limits(calls=CALLS, period=MINUTE)
def get_players_helper(league_id: str, season: str, players: list = [],
                       page: int = 1, verbose: str = True):
    payload = {
        "league": league_id,
        "season": season,
        "page": page
    }

    # make get call to API
    r = requests.get("https://api-football-v1.p.rapidapi.com/v3/players",
                     headers=headers,
                     params=payload)
    
    # throw error if query not successful
    if r.status_code != 200:
        raise Exception('API response: {}'.format(r.status_code))

    # convert response to list of players in current page
    r = r.json()

    # append players to overall list of players
    players += r["response"]

    # print info about current iteration
    if verbose:
        print("Page:", str(page) + "/" + str(r["paging"]["total"]),
              "Num players:", len(r["response"]))

    # recursive call to get players in subsequent pages
    if int(r["paging"]["current"]) < int(r["paging"]["total"]):
        get_players_helper(league_id, season, players, page + 1)


# Get a list of all teams in the given league for the lastest season available
# Write separate json files with all seasons, teams, and players in each
# league
#
# Note: we assume the number teams does not change over time to avoid
#       duplicate team entries.
#
# Output: write json file with all teams in each leagues
#         [{"team1": {}, "venue1": {}}, {"team2": {}, "venue2": {}}]
def update_files(leagues: list[str]):
    # get all available seasons
    # write json file with seasons
    seasons = get_seasons(end=2022)
    with open("seasons.json", "w") as out:
        for year in seasons:
            if year <= 2022:
                out.write(f"{year}\n")

    # get all teams in the leagues
    # write json file with all teams in each leagues
    # teams = get_teams(leagues, seasons[-1])
    # with open("teams.json", "w") as out:
    #     out.write(json.dumps(teams))

    # get all players across all leagues in the season
    # write json file with all players in each leagues
    #team_ids = [str(team["team"]["id"]) for team in teams]
    players = get_players(leagues, seasons)
    with open("players.json", "w") as out:
        out.write(json.dumps(players))
