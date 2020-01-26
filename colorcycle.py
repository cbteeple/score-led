from hex2rgb import hex2rgb
import nfl_scores
import time

import led_driver as led

pin_vec = [[2, 3, 4],[17, 27, 22], [10, 9, 11], [5, 6, 13]] 

for i, pin_group in enumerate(pin_vec):
	led.clearColors(pin_group)

time.sleep(3)

for i, pin_group in enumerate(pin_vec):	
	led.setColors(pin_group)

	
'''time.sleep(3)
for i, pin_group in enumerate(pin_vec):
	led.clearColors(pin_group)
'''
