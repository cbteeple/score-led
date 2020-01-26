#Get functions from external sources
from multiprocessing import Process
from hex2rgb import hex2rgb
import time
import nfl_scores
import led_driver as led
	

pin_vec = [[2, 3, 4],[17, 27, 22], [10, 9, 11], [5, 6, 13]]
pwm_freq = 100
pwm_vec = range(len(pin_vec))




#Setup all the groups of LED pins and begin PWM on them
led.init()

for i, pin_groups in enumerate(pin_vec):
	pwm_vec[i] = led.setup(pin_groups,pwm_freq)
	
pwm_vec[0]=led.runPulse(pwm_vec[0])	

time.sleep(1)



#color=hex2rgb("#16b5ff")
color=hex2rgb("#FFFFFF")
led.setColor(pwm_vec[0],color)
time.sleep(1)


#for i, blank in enumerate(pin_vec):
#	led.stop(pwm_vec[i])













#Print nfl game data just to try it.

#game_data = nfl_scores.get_scores()
#team1_data = nfl_scores.get_team_data(game_data, 'NE')
#print nfl_scores.get_score(team1_data)
#nfl_scores.pretty_json(game_data)
