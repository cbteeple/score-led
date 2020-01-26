#Get functions from external sources
from multiprocessing import Process, Value, Array
from hex2rgb import hex2rgb
import nfl_scores
import time

import led_driver as led
	

pin_vec = [[2, 3, 4],[17, 27, 22], [10, 9, 11], [5, 6, 13]]
pwm_freq = 100
pwm_vec = range(len(pin_vec))
color=hex2rgb("#16b5ff")




#Setup all the groups of LED pins and begin PWM on them
led.init()
	
def pulse1(pwm_vec,color,goFlag,lock):
	for i, pin_groups in enumerate(pin_vec):
		pwm_vec[i] = led.setup(pin_groups,pwm_freq)

	whileGo=1;
	while whileGo:
		with lock:
			led.setColor(pwm_vec[0],color.value)
			whileGo=goFlag
		time.sleep(1)
		
	

	for i, blank in enumerate(pin_vec):
		led.stop(pwm_vec[i])


#Start a new process that pulses the intensity of the LEDs
if __name__ == '__main__':

	color_in = Array('color', color)
	goFlag=Value('goFlag',1);
	lock = Lock()
	print pwm_vec[0]
	ledUpdate = Process(target=pulse1, args=(pwm_vec,color_in,goFlag,lock))
	ledUpdate.Array(color)
	ledUpdate.start()

time.sleep(1)
color=hex2rgb("#FF00FF")
time.sleep(0.5)
color=hex2rgb("#000000")
time.sleep(1)
color=hex2rgb("#16b5ff")



print hex2rgb("#16b5ff")









#Print nfl game data just to try it.

#game_data = nfl_scores.get_scores()
#team1_data = nfl_scores.get_team_data(game_data, 'NE')
#print nfl_scores.get_score(team1_data)
#nfl_scores.pretty_json(game_data)
