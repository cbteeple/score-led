#Get functions from external sources
import threading
from hex2rgb import hex2rgb, rgb2hex
import time
import random
import math
import datetime


import led_driver as led
	
#Define some low-level pin variables
pin_vec = [[2, 3, 4],[17, 27, 22], [10, 9, 11], [5, 6, 13]] #color groups of 3 pins each
pwm_freq = 100 #This is the low-level pwm frequency
pwm_vec = range(len(pin_vec)) #Initialize the pwm object vector

color_LUT=['#2d0000','#472200','#634f00','#5f7a00',
	'#1d9100','#00aa38','#00bf9c','#00bf9c',
	'#0003db','#0003db','#e500d6','FFFFFF']

skipIntro=1



#Start with #000000

color_vec=[hex2rgb("#000000"), hex2rgb("#000000"), hex2rgb("#000000"), hex2rgb("#000000")]

fadeTime_default = 0.2
pulseTime=2.5
pulseFlag=0
singlePulse=0;




#Initiatlize the board for LED stuff
led.init()

#Define the function that will become our led loom process
def ledLoop(pin_vec,stopFlag,updateFlag):
	#Setup all the groups of LED pins and begin PWM on them
	for i, pin_groups in enumerate(pin_vec):
		pwm_vec[i] = led.setup(pin_groups,pwm_freq)
	
	led.setAllColors(pwm_vec,color_vec)
	
	curr_colors=color_vec[:][:]
	#Big loop - this is where colors actually get set
	trans_time=fadeTime_default
	
	while not stopFlag.isSet():
		#led.setAllColors(pwm_vec,color_vec)
		#for i, pwm in enumerate(pwm_vec):
		#	led.setColor(pwm,color_vec[i])
		if pulseFlag:
			trans_time=pulseTime
		else:
			trans_time=fadeTime_default
			
		
		if updateFlag.isSet():
			led.setAllColorsFade(pwm_vec, color_vec, curr_colors,trans_time)
			curr_colors=color_vec[:][:]
			updateFlag.clear()
		time.sleep(0.1)
	
	trans_time=fadeTime_default	
	led.setAllColorsFade(pwm_vec,
		[[0 for i in range(3)] for j in range(4)],
		curr_colors,trans_time)
	time.sleep(fadeTime_default+1.0)
	
	#Once the loop is broken, we stop PWM and clean up the GPIO ports
	for i, blank in enumerate(pin_vec):
		led.stop(pwm_vec[i])
		
		
	for i, pin_groups in enumerate(pin_vec):
		led.clearColors(pin_groups)
		time.sleep(0.5)




#Run Stuff
if __name__ == '__main__':
	#Start a new process that pulses the intensity of the LEDs
	stopFlag=threading.Event()
	updateFlag = threading.Event()
	ledUpdate = threading.Thread(
		name='non-block',
		target=ledLoop,
		args=(pin_vec,stopFlag,updateFlag))
	ledUpdate.start()


	prev_hour_idx=0
	prev_min_idx=0
	prev_sec_idx=0
	
	
	pulseFlag=1
	
	try:
		while 1:
		
			d=datetime.datetime.now().timetuple()
			curr_hour=d[3]
			curr_min=d[4]
			curr_sec=d[5]
			
			
			curr_hour_idx=curr_hour/2
			curr_min_idx=curr_min/5
			curr_sec_idx=curr_sec/5
			
			'''print(curr_hour_idx),
			print(curr_min_idx),
			print(curr_sec_idx)
			'''
			
			
			
			if ((curr_hour_idx != prev_hour_idx)
				or (curr_min_idx != prev_min_idx)
				or (curr_sec_idx != prev_sec_idx)):
				#print('update colors')
				
				color_vec[0]=hex2rgb(color_LUT[curr_min_idx])
				color_vec[1]=hex2rgb(color_LUT[curr_hour_idx])
				
				color_vec[2]=hex2rgb("FFFFFF")
				color_vec[3]=hex2rgb(color_LUT[curr_sec_idx])
				
				prev_hour_idx=curr_hour_idx
				prev_min_idx=curr_min_idx
				prev_sec_idx=curr_sec_idx
				
				updateFlag.set()
			
			
			time.sleep(1.0)
					
			
			
	except KeyboardInterrupt:
		pass


	#Set the flag to end the PWM process
	stopFlag.set()
	
	
