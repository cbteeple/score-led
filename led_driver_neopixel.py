import time
import board
import neopixel
import numpy as np


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
		self.pixel_vectors = {}
		for pin, num_pixels in pixel_groups.items():
			pixels = neopixel.NeoPixel(
				self.PIN_MAP[pin],
				num_pixels,
				brightness=1.0,
				auto_write=False,
				pixel_order=self.ORDER_MAP[order],
			)
			self.pixel_groups[pin] = pixels
			self.pixel_vectors[pin] = np.empty((num_pixels,3))
			self.pixel_vectors[pin][:] = np.nan
		

	def stop(self):
		pass

	def show_group(self, group_idx):
		group_config = self.pin_configs[group_idx]
		pixels = self.pixel_groups[group_config['pin']]
		pixels.show()

	def show_all(self):
		for key, pixels in self.pixel_groups.items():
			pixels.show()

	def load_color_array(self, group_idx, colors, invert=False):
		group_config = self.pin_configs[group_idx]
		num_pixels = group_config['num_pixels']
		offset = group_config['start_idx']

		vec = self.pixel_vectors[group_config['pin']]

		if len(colors)!=num_pixels:
			raise ValueError("The number of colors in the input array must equla the number of pixels in the group")

		indices = list(range(num_pixels))

		if invert:
			indices = reversed(indices)

		for idx, i in enumerate(indices):
			vec[idx+offset] = colors[i]

		self.pixel_vectors[group_config['pin']] = vec
		

	def send_color_arrays(self, show=True):
		for key, pixels in self.pixel_groups.items():
			array = self.pixel_vectors[key]
			for idx, color in enumerate(array):
				if not np.isnan(color[0]): 
					pixels[idx] = color

			if show:
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
			if self.debug:
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

class Indicator:
	"""
	LED Indicator, a class to set up and control an indicator made
	of neopixels

	Args:
		num_pixels (int): The number of pixels in the color group.
		start_idx (int): The starting pixel index for the indicator.
		end_idx (int): The ending pixel index for the indicator.
		verbose (bool): Whether to print in verbose mode.
	"""
	def __init__(
			self,
			num_pixels,
			start_idx=None,
			end_idx=None,
			verbose=False,
		):
		self.num_pixels = num_pixels

		if start_idx is None:
			self.start_idx = 0
		else:
			self.start_idx = start_idx
		if end_idx is None:
			self.end_idx = num_pixels
		else:
			self.end_idx = end_idx
		
		self.verbose = verbose

		self.num_indicator_pixels = self.end_idx - self.start_idx

		# Initialize values
		self.pixel_vector = np.zeros((num_pixels,3))
		self._brightness = 1.0
		self.buffer_color = [[0,0,0],[0,0,0]]

		if self.verbose:
			print("Total of {} pixels:".format(self.num_pixels))
			print(self.num_indicator_pixels, self.start_idx, self.end_idx)

	@property
	def brightness(self):
		return self._brightness*100.0

	@brightness.setter
	def brightness(self, brightness):
		if (brightness < 0) or (brightness > 100):
			raise ValueError("Brightness must be between 0 and 100")
		
		self._brightness = brightness/100.0

	@property
	def buffer_color(self):
		return self._buffer_colors

	@buffer_color.setter
	def buffer_color(self, buffer_color):
		if isinstance(buffer_color, list):
			if len(buffer_color) >0:
				if isinstance(buffer_color[0], list):
					self._buffer_colors = buffer_color
				else:
					self._buffer_colors = [buffer_color, buffer_color]
			else:
				raise ValueError('Buffer color must be a 3-vector or a list of 3-vectors')
		else:
			raise ValueError('Buffer color must be a 3-vector or a list of 3-vectors')
			
		self.pixel_vector[0:self.start_idx,:] = self._buffer_colors[0]
		self.pixel_vector[self.end_idx+1:,:] = self._buffer_colors[1]

	def compute_fractional_colors(self, color1, color2, ratio):  
		"""
		Compute a color array indicator with fractional colors for the endpoint
		
		Args:
			color1 (list(int)): The first color
			color2 (list(int)): The second color
			ratio (float): The ratio of pixels to illuminate with color1/color2
			
		Returns:
			color_array (np.ndarray): The output color array 
		"""
		if ratio == 0:
			self.pixel_vector[:,:] = color2
		
		elif ratio ==1:
			self.pixel_vector[:,:] = color1
		else:
			num_pixels_full = np.floor(ratio*self.num_indicator_pixels).astype(int)
			pixel_partial = (ratio*self.num_indicator_pixels) - num_pixels_full
			
			# Generate the color array
			self.pixel_vector[self.start_idx: (self.start_idx+num_pixels_full),:] = color1
			self.pixel_vector[(self.start_idx+num_pixels_full+1):self.end_idx,:] = color2
			
			# Add the partial pixel
			partial_color = np.array(color1)*pixel_partial + np.array(color2)*(1-pixel_partial)
			self.pixel_vector[self.start_idx+num_pixels_full,:] = partial_color

		# Adjust the brightness
		color_array = self.pixel_vector*self._brightness
		
		if self.verbose:
			print("Ratio Input: {}".format(ratio))
			print("Color Vector:")
			for color in color_array:
				print(color)
			print("")
		return  color_array

	
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