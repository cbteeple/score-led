import RPi.GPIO as GPIO
import time
import board
import neopixel




def init():
	GPIO.setmode(GPIO.BCM)

class PixelHandler:

	PIN_MAP={
		10: board.D10,
		12: board.D12,
		18: board.D18,
		21: board.D21,
	}

	ORDER_MAP = {
		'GRB': neopixel.GRB,
		'RGB': neopixel.RGB,
	}

	# Pixel setup
	def __init__(self, pin_configs, order='GRB', debug=False):
		self.pin_configs = pin_configs
		self.debug = debug
		pixel_groups={}
		for config in pin_configs:
			num_pixels = config['num_pixels']

			if pixel_groups.get(config['pin']):
				pixel_groups[config['pin']]+=num_pixels
			else:
				pixel_groups[config['pin']]=num_pixels

		self.pixel_groups = {}
		for pin, num_pixels in pixel_groups.items():
			pixels = neopixel.NeoPixel(
				self.PIN_MAP[pin],
				num_pixels,
				brightness=1.0,
				auto_write=False,
				pixel_order=self.ORDER_MAP[order],
			)
			self.pixel_groups[pin] = pixels

	def stop(self):
		pass

	def show_group(self, group_idx):
		group_config = self.pin_configs[group_idx]
		pixels = self.pixel_groups[group_config['pin']]
		pixels.show()

	def show_all(self):
		for key, pixels in self.pixel_groups.items():
			pixels.show()

	def set_color_array(self, group_idx, colors, invert=False, show=True):
		group_config = self.pin_configs[group_idx]
		pixels = self.pixel_groups[group_config['pin']]
		num_pixels = group_config['num_pixels']
		offset = group_config['start_idx']

		if len(colors)!=num_pixels:
			raise ValueError("The number of colors in the input array must equla the number of pixels in the group")

		indices = list(range(num_pixels))

		if invert:
			indices = reversed(indices)

		for idx, i in enumerate(indices):
			pixels[idx+offset] = colors[i]

		if show:
			self.show_group(group_idx)
	
	def set_color(self, group_idx, color, show=True):
		if self.debug:
			print("Setting group %d to: %d, %d, %d"%(
				group_idx,
				color[0],
				color[1],
				color[2],
			))

		group_config = self.pin_configs[group_idx]
		pixels = self.pixel_groups[group_config['pin']]
		offset = group_config['start_idx']

		for i in range(group_config['num_pixels']):
			pixels[i+offset] = color

		if show:
			self.show_group(group_idx)
		
	def set_all_colors(self, color_vec, show=True):
		if self.debug:
			print("Setting all groups at once.")

		for i, color in enumerate(color_vec):
			self.set_color(i, color, show=False)
		
		if show:
			self.show_all()
			
	def set_all_colors_fade(
			self,
			new_color_vec,
			cur_color_vec,
			time_tot,
			timestep=0.05,
		):
		ramps= []
		num_steps=int(time_tot/timestep)
		
		#Precompute all color ramps
		for new_color, curr_color in zip(new_color_vec, cur_color_vec):
			print("{} --> {}".format(curr_color, new_color))
			fade_list = get_ramp(new_color, curr_color, num_steps)
			ramps.append(fade_list)

		#Perform the fade
		for step in range(num_steps+1):
			color_vec=[]
			for ramp in ramps:
				color_vec.append(ramp[step])
			self.set_all_colors(color_vec, show=True)
			time.sleep(timestep)

	
#Create a long array with ramps of color values
def get_ramp(
		new_color_all,
		cur_color_all,
		num_steps,
	):
	
	fadeList = [[0 for y in range(len(new_color_all))] for x in range(num_steps+1)]
	
	#For each color pin
	for pinIdx, _ in enumerate(new_color_all):
		#find the increment value
		color_inc = (float(new_color_all[pinIdx]) - float(cur_color_all[pinIdx]))/float(num_steps)
		#For each timestep, store the value of the duty cycle
		fadeList[0][pinIdx]= int(cur_color_all[pinIdx])
		for stepIdx in range(1,num_steps+1):
			fadeList[stepIdx][pinIdx] = int(cur_color_all[pinIdx]+stepIdx*color_inc)
			
			# #Make sure the duty cycle values are between 0 and 100
			if fadeList[stepIdx][pinIdx]>255:
				fadeList[stepIdx][pinIdx]=int(255)
				
			if fadeList[stepIdx][pinIdx]<0:
				fadeList[stepIdx][pinIdx]=int(0)
				
	for pinIdx in range(len(new_color_all)):
		fadeList[num_steps][pinIdx]=int(new_color_all[pinIdx])
				
	return fadeList
	

	
	

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
			print(p)
			p.ChangeDutyCycle(dc)
		time.sleep(0.03)
	for dc in range(100, -1, -5):
		for p in pwm:
			p.ChangeDutyCycle(dc)
		time.sleep(0.03)
	return pwm
