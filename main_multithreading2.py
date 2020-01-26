#Get functions from external sources
import threading
from hex2rgb import hex2rgb, rgb2hex
import nfl_scores
from twitter_sentiment import TwitterClient
from collections import deque
import time
import random
import math

import led_driver as led
	
#Define some low-level pin variables
pin_vec = [[2, 3, 4],[17, 27, 22], [10, 9, 11], [5, 6, 13]] #color groups of 3 pins each
pwm_freq = 100 #This is the low-level pwm frequency
pwm_vec = range(len(pin_vec)) #Initialize the pwm object vector


skipIntro=1



#Start with a color (will change this eventually to start with #000000)

#Eagles
team2_bright = "#00cc2a"
team2_color  = "#005b12"
team2_dim    = "#002808"

#Patriots
team1_bright = "#0031e8"
team1_color  = "#001875"
team1_dim    = "#000b35"

color_vec=[hex2rgb(team1_color), hex2rgb("#000000"), hex2rgb(team2_color), hex2rgb("#000000")]

fadeTime_default = 0.25
pulseTime = 3.5
pulseFlag=0
singlePulse=0;

team1_pulse=[team1_bright, team1_dim]
team2_pulse=[team2_bright, team2_dim]







# Collect the tweets!

# How many past twitter api calls to save
save_num_calls = 4
num_tweets = 400
call_rate = 15  # seconds

team1 = 'NE'
team2 = 'PHI'

tags = {
    team1: '#Patriots',
    team2: '#Eagles'
}

# Keep an array of the # of tweets sentiment
# [ positive, negative, neutral ]
tweet_sentiment = {
    team1: deque([]),
    team2: deque([])
}

# creating object of TwitterClient Class
api = TwitterClient()



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











#Initiatlize the board for LED stuff
led.init()

#Define the function that will become our led loom process
def ledLoop(pin_vec,goFlag,updateFlag):
	#Setup all the groups of LED pins and begin PWM on them
	for i, pin_groups in enumerate(pin_vec):
		pwm_vec[i] = led.setup(pin_groups,pwm_freq)
	
	led.setAllColors(pwm_vec,color_vec)
	
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
	goFlag=threading.Event()
	updateFlag = threading.Event()
	ledUpdate = threading.Thread(
		name='non-block',
		target=ledLoop,
		args=(pin_vec,goFlag,updateFlag))
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
		positivity = {}
		while 1:	
			#Check at regular intervals for the twitter sentiment
			for team, vals in tweet_sentiment.iteritems():
				new_tweets = new_analysis(tags[team])
				tweet_sentiment[team].append(new_tweets)

				if len(tweet_sentiment[team]) > save_num_calls:
					tweet_sentiment[team].popleft()

				# Get the percentage of positive/negative/neutral tweets in the list
				t_s = tweet_sentiment[team]
				pos = sum([t[0] for t in t_s])
				neg = sum([t[1] for t in t_s])
				neut = sum([t[2] for t in t_s])

				positivity[team] =  100 * float(pos) / (pos + neg)
				
				#positivity[team]=random.randint(0,100)
				print team + ': ' + str(positivity[team])
			
			
			#find the R and G values (B is always 0)
			
			R=25.5*math.sqrt(-positivity[team1]+100)
			G=255./10000*(positivity[team1]**2)
			B=0
			
			color_vec[1]= [R,G,B]
			
			R=25.5*math.sqrt(-positivity[team2]+100)
			G=255./10000*(positivity[team2]**2)
			B=0
			color_vec[3]= [R,G,B]
			
			
			
			#Check at regular intervals for the score
			try:
				game_data = nfl_scores.get_scores()
				team1_data = nfl_scores.get_team_data(game_data, team1)
				team2_data = nfl_scores.get_team_data(game_data, team2)
			
				team1_score=nfl_scores.get_score(team1_data)
				team2_score=nfl_scores.get_score(team2_data)
				
				team1_posession = nfl_scores.has_possession(game_data,team1)
				team2_posession = nfl_scores.has_possession(game_data,team2)
				
				qtr=nfl_scores.get_qtr(game_data)
			
				#Score to RGB
				#print team1_score, team2_score
				#print
				if qtr == "Pregame":
					team1_pulse=[team1_bright, team1_dim]
					team2_pulse=[team2_bright, team2_dim]
					pulseFlag=1;
					singlePulse=0
					pulseTime=3.5
					
					
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
					
			except TypeError:
				pass					

				
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
					color_vec[2]=hex2rgb(team2_pulse[0])
					updateFlag.set()
					time.sleep(pulseTime+0.25)
					
					
					color_vec[0]=hex2rgb(team1_pulse[1])
					color_vec[2]=hex2rgb(team2_pulse[1])
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
	
	
