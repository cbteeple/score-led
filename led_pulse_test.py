import RPi.GPIO as GPIO
import time

pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19]
pwm = range(len(pins))

led_freq = 100

# PWM setup
GPIO.setmode(GPIO.BCM)
for i, pin in enumerate(pins):
	GPIO.setup(pin, GPIO.OUT)
	pwm[i] = GPIO.PWM(pin, led_freq)
	pwm[i].start(0)

# PWM
try:
	while 1:
		for dc in range(0, 101, 2):
			for p in pwm:
				p.ChangeDutyCycle(dc)
			time.sleep(0.03)
		for dc in range(100, -1, -2):
			for p in pwm:
				p.ChangeDutyCycle(dc)
			time.sleep(0.03)
except KeyboardInterrupt:
    pass

p.ChangeDutyCycle(0)
p.stop()
GPIO.cleanup()
