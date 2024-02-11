#Get functions from external sources
import threading
from hex2rgb import hex2rgb, rgb2hex
import nfl_scores
from collections import deque
import time
import random
import math

import led_driver_neopixel as led
	
#Define some low-level pin variables
pin_config = [
    {'pin': 10, 'num_pixels': 9, 'start_idx': 0},
	{'pin': 10, 'num_pixels': 22, 'start_idx': 9},
	{'pin': 21, 'num_pixels': 9, 'start_idx': 0},
	{'pin': 21, 'num_pixels': 22, 'start_idx': 9},
]

skipIntro=1
call_rate = 15  # seconds

#Start with a color (will change this eventually to start with #000000)

#SF
team2_bright = "#ff6a4f"
team2_color  = "#cc1f00"
team2_dim    = "#8a1500"

#KC
team1_bright = "#ff5959"
team1_color  = "#cc0000"
team1_dim    = "#910000"

team1_colors=["#cc0000","#d6d6d6"]
team2_colors=["#cc0000","#ff6a00"]

color_vec=[hex2rgb(team1_color), hex2rgb("#000000"), hex2rgb(team2_color), hex2rgb("#000000")]

fadeTime_default = 0.25
pulseTime = 3.5
pulseFlag=0
singlePulse=0;

team1_pulse=[team1_bright, team1_dim]
team2_pulse=[team2_bright, team2_dim]


team1 = 'KC'
team2 = 'SF'


def new_analysis(tag):
    # calling function to get tweets
    tweets = api.get_tweets(query = tag, count = num_tweets) 
    # Number of positive tweets from tweets
    pos_tweets = len([tweet for tweet in tweets if tweet['sentiment'] == 'positive'])
    # Number of negative tweets from tweets
    neg_tweets = len([tweet for tweet in tweets if tweet['sentiment'] == 'negative'])
    # Number of neutral tweets
    neut_tweets = len(tweets) - pos_tweets - neg_tweets 

    return pos_tweets, neg_tweets, neut_tweets










#Define the function that will become our led loom process
def ledLoop(led_handler, goFlag, updateFlag):
	#Setup all the groups of LED pins and begin PWM on them
	led_handler.set_all_colors(color_vec)
	
	curr_colors=color_vec[:][:]
	#Big loop - this is where colors actually get set
	trans_time=fadeTime_default
	
	while not goFlag.isSet():
		#led.setAllColors(pwm_vec,color_vec)
		#for i, pwm in enumerate(pwm_vec):
		#	led.setColor(pwm,color_vec[i])
		if pulseFlag:
			trans_time=pulseTime
		else:
			trans_time=fadeTime_default
			
		
		if updateFlag.isSet():
			led_handler.set_all_colors_fade(color_vec, curr_colors, trans_time)
			curr_colors=color_vec[:][:]
			updateFlag.clear()
		time.sleep(0.1)
	
	trans_time=fadeTime_default	
	led_handler.set_all_colors_fade(
		[[0 for i in range(3)] for j in range(4)],
		curr_colors,
		trans_time
	)
	time.sleep(fadeTime_default+1.0)
	
	#Once the loop is broken, we stop PWM and clean up the GPIO ports
	led_handler.stop()

#Run Stuff
if __name__ == '__main__':
	#Start a new process that pulses the intensity of the LEDs
	print("Starting...")
	led_handler = led.PixelHandler(pin_config, debug=True)
	
	goFlag=threading.Event()
	updateFlag = threading.Event()
	ledUpdate = threading.Thread(
		name='non-block',
		target=ledLoop,
		args=(led_handler,
		    goFlag,
			updateFlag
			))
	ledUpdate.start()
	
	#Change the color of some of the LED's at a test
	if not skipIntro:
		color_vec[0]=hex2rgb(team1_color)
		color_vec[1]=hex2rgb("#FF0000")
		color_vec[2]=hex2rgb(team2_color)
		color_vec[3]=hex2rgb("#00FF00")
		updateFlag.set()
		time.sleep(fadeTime_default+1.0)
	
		color_vec[0]=hex2rgb(team1_color)
		color_vec[1]=hex2rgb("#00FF00")
		color_vec[2]=hex2rgb(team2_color)
		color_vec[3]=hex2rgb("#FF0000")
		updateFlag.set()
		time.sleep(fadeTime_default+1.0)

		color_vec[0]=hex2rgb("#000000")
		color_vec[1]=hex2rgb("#000000")
		color_vec[2]=hex2rgb("#000000")
		color_vec[3]=hex2rgb("#000000")
		updateFlag.set()
		time.sleep(fadeTime_default+1.0)
	
	
		color_vec[0]=hex2rgb(team1_color)
		color_vec[1]=hex2rgb("#000000")
		color_vec[2]=hex2rgb(team2_color)
		color_vec[3]=hex2rgb("#000000")
		updateFlag.set()
		time.sleep(fadeTime_default+1.0)
	
	pulseFlag=1
	
	
	try:
		while 1:	
			#Check at regular intervals for the score
			try:
				game_data = nfl_scores.get_scores()
			except TypeError:
				print("Error getting scores...")
				continue
			
			team1_data = nfl_scores.get_team_data(game_data, team1)
			team2_data = nfl_scores.get_team_data(game_data, team2)
		
			team1_score=nfl_scores.get_score(team1_data)
			team2_score=nfl_scores.get_score(team2_data)
			
			# team1_posession = nfl_scores.has_possession(game_data,team1)
			# team2_posession = nfl_scores.has_possession(game_data,team2)
			
			qtr=nfl_scores.get_qtr(game_data)
		
			#Score to RGB
			#print team1_score, team2_score
			#print
			if 'pre' in qtr:
				team1_pulse=[team1_colors[0], team1_colors[1]]
				team2_pulse=[team2_colors[0], team2_colors[1]]
				pulseFlag=1;
				singlePulse=0
				pulseTime=3.5
				print("The game will begin soon...")
				
				
			else:
				if team1_score is not None and team2_score is not None:
					print(team1_score)
					print(team2_score)
					if team1_score > team2_score:
						color_vec[0]=hex2rgb(team1_bright)
						color_vec[2]=hex2rgb(team2_dim)
					elif team1_score < team2_score:
						color_vec[0]=hex2rgb(team1_dim)
						color_vec[2]=hex2rgb(team2_bright)
					else:
						color_vec[0]=hex2rgb(team1_color)
						color_vec[2]=hex2rgb(team2_color)
				
					pulseFlag=0
										
				else:
					pulseFlag=1;
					singlePulse=0
					pulseTime=3.5
					print('scores were null')
				

				print(color_vec[0])
				print(color_vec[2])
				'''if team1_posession:
					print('team1 has posession')
					pulseFlag=1
					singlePulse=1
					pulseTime=1.0
					rgb=[0, 0, 0]
					for idx in range(len(rgb)):
						rgb[idx]= int(color_vec[0][idx] + color_vec[0][idx]*0.5)
										
					team1_pulse=[rgb2hex(color_vec[0]),rgb2hex(rgb)]
					team2_pulse=[rgb2hex(color_vec[2]),rgb2hex(color_vec[2])]
				
				
				elif team2_posession:
					print('team2 has posession')
					pulseFlag=1
					singlePulse=1
					pulseTime=1.0
					rgb=[0, 0, 0]
					for idx in range(len(rgb)):
						rgb[idx]= int(color_vec[2][idx] + color_vec[2][idx]*0.5)
										
					team1_pulse=[rgb2hex(color_vec[0]),rgb2hex(color_vec[0])]
					team2_pulse=[rgb2hex(color_vec[2]),rgb2hex(rgb)]
				'''
								
			if pulseFlag:
				#Set color for 4 sec, 4 times
				
				if not singlePulse:
					numPulses=int(math.ceil(15/(pulseTime*2)))
					deadTime=0.0
				else:
					numPulses=1
					deadTime=15-pulseTime*2
					
				
				for idx in range(numPulses):
					color_vec[0]=hex2rgb(team1_pulse[0])
					color_vec[1]=hex2rgb(team1_pulse[1])
					color_vec[2]=hex2rgb(team2_pulse[0])
					color_vec[3]=hex2rgb(team2_pulse[1])
					updateFlag.set()
					time.sleep(pulseTime+0.25)
					
					
					color_vec[0]=hex2rgb(team1_pulse[1])
					color_vec[1]=hex2rgb(team1_pulse[0])
					color_vec[2]=hex2rgb(team2_pulse[1])
					color_vec[3]=hex2rgb(team2_pulse[0])
					updateFlag.set()
					time.sleep(pulseTime+0.25)
					
				time.sleep(deadTime)
					
					
			else:				
				color_temp=color_vec[:]
				
				
				color_vec[1]=hex2rgb("7C7C7C")
				color_vec[3]=hex2rgb("7C7C7C")
				
				updateFlag.set()
				time.sleep(fadeTime_default+0.2)
				
				color_vec[1]=color_temp[1]
				color_vec[3]=color_temp[3]
				updateFlag.set()
				#print nfl_scores.pretty_json(game_data)
				time.sleep(call_rate-1)
			
			
			
	except KeyboardInterrupt:
		pass

	
	
	#Set the flag to end the PWM process
	goFlag.set()
	
	
