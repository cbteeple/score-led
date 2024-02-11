#Get functions from external sources
import copy
import threading
from hex2rgb import hex2rgb, rgb2hex
import nfl_scores
from collections import deque
import time
import random
import math
import numpy as np

import led_driver_neopixel as led
	
#Define some low-level pin variables
pin_config = [
    {'pin': 10, 'num_pixels': 9, 'start_idx': 0},
	{'pin': 10, 'num_pixels': 15, 'start_idx': 9},
	{'pin': 21, 'num_pixels': 9, 'start_idx': 0},
	{'pin': 21, 'num_pixels': 15, 'start_idx': 9},
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

team1_colors=["#ff0000","#858585"]
team2_colors=["#ff0000","#ff6a00"]
score_indicator_color="#0d6600"

color_vec=[hex2rgb(team1_color), hex2rgb("#000000"), hex2rgb(team2_color), hex2rgb("#000000")]
curr_colors=color_vec[:][:]

fadeTime_default = 0.25
pulseTime = 5.0
pulseFlag=0
singlePulse=0;

team1_pulse=[team1_bright, team1_dim]
team2_pulse=[team2_bright, team2_dim]


team1 = 'KC'
team2 = 'SF'

team1_score_last = 0
team2_score_last = 0



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
	led_handler = led.PixelHandler(pin_config)
	
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
			except:
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
			if ('pre' in qtr):
				team1_pulse=[team1_colors[0], team1_colors[1]]
				team2_pulse=[team2_colors[0], team2_colors[1]]
				pulseFlag=1;
				singlePulse=0
				pulseTime=3.5
				print("The game will begin soon...")
				
				
			else:
				# Team Logos
				idx_0 = int(pin_config[0]['num_pixels']*(0.6))
				idx_2 = int(pin_config[2]['num_pixels']*(0.6))
				
				color_array_0 = np.zeros((pin_config[0]['num_pixels'],3))
				color_array_0[:,:] = hex2rgb(team1_colors[1])
				color_array_0[0:idx_0, :] = hex2rgb(team1_colors[0])
				color_array_2 = np.zeros((pin_config[2]['num_pixels'],3))
				color_array_2[:,:] = hex2rgb(team2_colors[1])
				color_array_2[0:idx_2, :] = hex2rgb(team2_colors[0])

				for idx in range(len(color_array_0)):
					color_array_0_tmp = np.roll(color_array_0, idx, axis=0).tolist()
					color_array_2_tmp = np.roll(color_array_2, idx, axis=0).tolist()
					led_handler.set_color_array(0, color_array_0_tmp, invert=False)
					led_handler.set_color_array(2, color_array_2_tmp, invert=False)
					time.sleep(0.05)
				
				led_handler.set_color_array(0, color_array_0, invert=False)
				led_handler.set_color_array(2, color_array_2, invert=False)


				if team1_score != 0 or team2_score != 0:
					print(team1_score, team2_score)
					indicator_offset = 2
					num_pixels_indicator = pin_config[1]['num_pixels']-2*indicator_offset

					# If the score changed, animate!
					if team1_score != team1_score_last:
						idx_1 = int(pin_config[1]['num_pixels']*(0.5))
						
						color_array_1 = np.zeros((pin_config[1]['num_pixels'],3))
						color_array_1[:,:] = hex2rgb(team1_colors[1])
						color_array_1[0:idx_1, :] = hex2rgb(team1_colors[0])

						for i in range(abs(team1_score-team1_score_last)):
							for idx in range(len(color_array_1)):
								color_array_1_tmp = np.roll(color_array_1, idx, axis=0).tolist()
								led_handler.set_color_array(1, color_array_1_tmp, invert=True)
								time.sleep(0.04)

					if team2_score != team2_score_last:
						idx_3 = int(pin_config[3]['num_pixels']*(0.5))
						
						color_array_3 = np.zeros((pin_config[3]['num_pixels'],3))
						color_array_3[:,:] = hex2rgb(team2_colors[1])
						color_array_3[0:idx_3, :] = hex2rgb(team2_colors[0])

						for i in range(abs(team2_score-team2_score_last)):
							for idx in range(len(color_array_3)):
								color_array_3_tmp = np.roll(color_array_3, idx, axis=0).tolist()
								led_handler.set_color_array(3, color_array_3_tmp, invert=True)
								time.sleep(0.04)

					# Display the idicator
					if team1_score == 0 and team2_score == 0:
						ratio = 0.5
					elif team1_score == 0:
						ratio = 0.2
					elif team2_score == 0:
						ratio = 0.8
					else:
						ratio = team2_score/team1_score

					idx_1 = int(num_pixels_indicator*ratio) + indicator_offset
					idx_3 = int(num_pixels_indicator*(1-ratio)) + indicator_offset

					# Score Indicator
					color_array_1 = np.zeros((pin_config[1]['num_pixels'],3))
					color_array_1[indicator_offset:idx_1, :] = hex2rgb(score_indicator_color)

					color_array_3 = np.zeros((pin_config[3]['num_pixels'],3))
					color_array_3[indicator_offset:idx_3, :] = hex2rgb(score_indicator_color)
	
					# Update indicators
					led_handler.set_color_array(1, color_array_1, invert=True)
					led_handler.set_color_array(3, color_array_3, invert=True)
				
					pulseFlag=0
										
				else:
					color_array_1 = np.zeros((pin_config[1]['num_pixels'],3))
					color_array_3 = np.zeros((pin_config[1]['num_pixels'],3))
					led_handler.set_color_array(1, color_array_1, invert=True)
					led_handler.set_color_array(3, color_array_3, invert=True)
					pulseFlag=0
					print('scores were null')
			
			team1_score_last = team1_score
			team2_score_last = team2_score
								
			if pulseFlag:
				#Set color for 4 sec, 4 times
				
				if not singlePulse:
					numPulses=int(math.ceil(call_rate/(pulseTime*2)))
					deadTime=0.0
				else:
					numPulses=1
					deadTime=call_rate-pulseTime*2
					
				
				for idx in range(numPulses):
					print("Pulse Number {}".format(idx))
					color_vec[0]=hex2rgb(team1_pulse[0])
					color_vec[1]=hex2rgb(team1_pulse[1])
					color_vec[2]=hex2rgb(team2_pulse[0])
					color_vec[3]=hex2rgb(team2_pulse[1])
					updateFlag.set()
					time.sleep(pulseTime+0.25)
					while updateFlag.isSet():
						time.sleep(0.25)
					
					
					color_vec[0]=hex2rgb(team1_pulse[1])
					color_vec[1]=hex2rgb(team1_pulse[0])
					color_vec[2]=hex2rgb(team2_pulse[1])
					color_vec[3]=hex2rgb(team2_pulse[0])
					updateFlag.set()
					time.sleep(pulseTime+0.25)
					while updateFlag.isSet():
						time.sleep(0.25)
					
				time.sleep(deadTime)
					
					
			else:		
				print("Not changing LEDs")		
				# color_temp=color_vec[:]
				
				# color_vec[1]=hex2rgb("7C7C7C")
				# color_vec[3]=hex2rgb("7C7C7C")
				
				# updateFlag.set()
				# time.sleep(fadeTime_default+0.2)
				
				# color_vec[1]=color_temp[1]
				# color_vec[3]=color_temp[3]
				# updateFlag.set()
				# #print nfl_scores.pretty_json(game_data)
				time.sleep(call_rate-1)
			
			
			
	except KeyboardInterrupt:
		pass

	
	
	#Set the flag to end the PWM process
	goFlag.set()
	
	
