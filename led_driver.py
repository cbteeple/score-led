import RPi.GPIO as GPIO
import time

def init():
	GPIO.setmode(GPIO.BCM)

# PWM setup
def setup(pins,pwm_freq):
	pwm=range(len(pins))
	for i, pin in enumerate(pins):
		GPIO.setup(pin, GPIO.OUT)
		pwm[i] = GPIO.PWM(pin, pwm_freq)
		pwm[i].start(0)
		pwm[i].ChangeDutyCycle(100)
	return pwm

#Stop the PWM Signal
def stop(pwm):
	for p in pwm:
		p.ChangeDutyCycle(0)
		p.stop()
		
	GPIO.cleanup()
	
	
def setColor(pwm_group,color):
	print " "
	for i, p in enumerate(pwm_group):
		color_dc=int(color[i]*(100)/255)
		p.ChangeDutyCycle(color_dc)
		print("Pin %d is set to: %d (%0.2f %% dc)" % (i,color[i],color_dc))
		
		
		
def setAllColors(pwm_vec,color_vec):
	print " "
	for i, pwm in enumerate(pwm_vec):
		for j, p in enumerate(pwm):
			color_dc=int(color_vec[i][j]*(100)/255)
			p.ChangeDutyCycle(color_dc)
			print("Pin %d is set to: %d (%0.2f %% dc)" % (j,color_vec[i][j],color_dc))
			
			
def setAllColorsFade(pwm_vec, new_color_vec, cur_color_vec, time_tot):
	new_color_all= [];
	cur_color_all= [];
	pwm_all = [];
	
	#Put all of the pwm objects and color values into single-level arrays
	for i, blank in enumerate(new_color_vec):
		for j ,blank in enumerate(new_color_vec[0]):
			new_color_all.append(new_color_vec[i][j])
			cur_color_all.append(cur_color_vec[i][j])
			pwm_all.append(pwm_vec[i][j])
		
	#Precompute a ramp from "cur_color" to "new_color"
	timestep=0.025; #Always use a refresh rate of 40 Hz to avoid flickering	
	fadeList, numSteps = getRamp(new_color_all,cur_color_all,time_tot, timestep)
				
	#Perform the fade
	for stepIdx in range(numSteps+1):
		#print(" ")			
		for pinIdx, p in enumerate(pwm_all):
			#print("%0.2f" % fadeList[pinIdx][stepIdx]),		
			p.ChangeDutyCycle(fadeList[pinIdx][stepIdx])
				#print("Pin %d is set to: %d (%0.2f %% dc)" % (j,color_vec[i][j],color_dc))
		time.sleep(timestep)
	
	
	
	
	
	
	
	
#Create a long array with ramps of duty cycle values
def getRamp(new_color_all,cur_color_all,time_tot,timestep):
	numSteps=int(time_tot/timestep)
	
	fadeList = [[0.0 for x in range(numSteps+1)] for y in range(len(new_color_all))]
	
	#For each color pin
	for pinIdx, blank in enumerate(new_color_all):
		#find the increment value
		color_inc = (float(new_color_all[pinIdx]) - float(cur_color_all[pinIdx]))/float(numSteps);
		color_inc=color_inc*100/255
		
		#For each timestep, store the value of the duty cycle
		fadeList[pinIdx][0]= float(cur_color_all[pinIdx])*100/255
		for stepIdx in range(1,numSteps+1):
			fadeList[pinIdx][stepIdx] = fadeList[pinIdx][stepIdx-1]+color_inc
			
			#Make sure the duty cycle values are between 0 and 100
			if fadeList[pinIdx][stepIdx]>100:
				fadeList[pinIdx][stepIdx]=100
				
			if fadeList[pinIdx][stepIdx]<0:
				fadeList[pinIdx][stepIdx]=0
				
	for pinIdx in range(len(new_color_all)):
		fadeList[pinIdx][numSteps]=float(new_color_all[pinIdx])*100/255;
				
	return (fadeList, numSteps)
	

	
	

def clearColors(pins):
	GPIO.setmode(GPIO.BCM)
	for i, pin in enumerate(pins):
		GPIO.setup(pin, GPIO.OUT)
		GPIO.output(pin, GPIO.LOW)
		
def setColors(pins):
	GPIO.setmode(GPIO.BCM)
	for i, pin in enumerate(pins):
		GPIO.setup(pin, GPIO.OUT)
		GPIO.output(pin, GPIO.HIGH)



#For Testing Purposes
	
# PWM
def runPulse(pwm):
	for dc in range(0, 101, 5):
		for p in pwm:
			print p
			p.ChangeDutyCycle(dc)
		time.sleep(0.03)
	for dc in range(100, -1, -5):
		for p in pwm:
			p.ChangeDutyCycle(dc)
		time.sleep(0.03)
	return pwm
