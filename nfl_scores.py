import urllib, json


SCORE_URL = 'http://www.nfl.com/liveupdate/scores/scores.json'
#TEAM1 = 'NE'
#TEAM2 = 'PHI'

#TEAM1 = 'AFC'
#TEAM2 = 'NFC'

TEAM1 = 'NE'
TEAM2 = 'LA'


# LET'S PLAY SOME FOOOOOOOTBAAAALLLLLL

def pretty_json(data):
    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

def get_scores():
    # https://stackoverflow.com/questions/12965203/how-to-get-json-from-webpage-into-python-script
    response = urllib.urlopen(SCORE_URL)
    try:
        data = json.loads(response.read())
    except ValueError, err:
        return None
    game_key = data.keys()[0]
    game_data = data[game_key]
    #pretty_json(game_data)
    return game_data
    
def get_team_data(game_data, team):
    key = 'away'
    temp_data = game_data[key]
    if temp_data['abbr'] == team:
        return temp_data
    key = 'home'
    temp_data = game_data[key]
    if temp_data['abbr'] == team:
        return temp_data
    else:
        raise ValueError('Team not playing')
        
def get_score(team_data):
    return team_data['score']['T']
    
def possession(game_data):
    return game_data['posteam']

def has_possession(game_data, team):
    return possession(game_data) == team

def is_redzone(game_data):
    return game_data['redzone']
      
def get_qtr(game_data):
    return game_data['qtr']
      
if __name__== "__main__":
    game_data = get_scores()
    team1_data = get_team_data(game_data, TEAM1)
    print get_score(team1_data)
    pretty_json(game_data)

