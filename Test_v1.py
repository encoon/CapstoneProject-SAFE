import time, sys
from grove.adc import ADC

from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import random
import time


__all__ = ["EMGTEST"]

class EMGTEST(object):
	def __init__(self, channel):
		self.channel = channel
		self.adc = ADC()
		
	@property
	def value(self):
		return self.adc.read(self.channel)
		

Grove = EMGTEST


# Value monitoring
def main():
	from grove.helper import SlotHelper
	sh = SlotHelper(SlotHelper.ADC)
	pin = sh.argv2pin()
	
	sensor = EMGTEST(pin)
	
	#while True:
		#print("Current Voltage % is: {}".format(sensor.value/10))

		


# Plot monitoring/plot setup
fig = plt.figure()
ax = plt.axes(xlim=(0, 50), ylim=(0, 120)) #changed y axis from 120 to 10
line, = ax.plot([], [], lw = 1, c = 'blue', marker = 'd', ms = 0.1)
max_points = 50
line, = ax.plot(np.arange(max_points), np.ones(max_points, dtype = np.cfloat)*np.nan,
                lw = 1, c = 'blue', marker = 'd', ms = 0.1)

#Import data
from grove.helper import SlotHelper
sh = SlotHelper(SlotHelper.ADC)
pin = sh.argv2pin()
sensor = EMGTEST(pin)

def init():
	return line

# Display data on plot
def animate(i):
	y = sensor.value/10
	old_y = line.get_ydata()
	new_y = np.r_[old_y[1:], y]
	line.set_ydata(new_y)
	print(new_y)
	return line,

anim = animation.FuncAnimation(fig, animate, init_func=init, frames = 200, interval = 20, blit = False)
plt.show()                
                
if __name__ == '__main__':
	main()
