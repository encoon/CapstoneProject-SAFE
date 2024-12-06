import RPi.GPIO as GPIO
import time

buzzer = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setwarnings(False)

pwm = GPIO.PWM(buzzer, 1200)
pwm.start(25.0)
time.sleep(0.5)

pwm.stop()
GPIO.cleanup()
