import urllib.request, json


SCORE_URL = 'http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'

# LET'S PLAY SOME FOOOOOOOTBAAAALLLLLL

def pretty_json(data):
    print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

def get_scores():
    # https://stackoverflow.com/questions/12965203/how-to-get-json-from-webpage-into-python-script
    
    response = urllib.request.urlopen(SCORE_URL)
    try:
        data = json.loads(response.read())
    except ValueError:
        return None

    return data
    
def get_team_data(game_data, team):
    competitors = game_data['events'][0]['competitions'][0]['competitors']

    data = None
    for curr_data in competitors:
        if curr_data['team']['abbreviation'] == team:
            data = curr_data
            break

    if data is None:
        raise ValueError("{} not found".format(team))
    return data
        

def get_score(team_data):
    return int(team_data['score'])
    
def possession(game_data):
    return game_data['posteam']

def has_possession(game_data, team):
    return possession(game_data) == team

def is_redzone(game_data):
    return game_data['redzone']
      
def get_qtr(game_data):
    period = game_data['events'][0]['competitions'][0]['status']['period']
    state = game_data['events'][0]['competitions'][0]['status']['type']['state']
    return period, state