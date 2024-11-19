import time, sys, math, pywt
import RPi.GPIO as GPIO
from grove.adc import ADC  # type: ignore
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread
from collections import deque

__all__ = ["EMGTEST"]

class EMGTEST(object):
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def value(self):
        return self.adc.read(self.channel)

Grove = EMGTEST

# Graphing data storage with deque for optimized fixed-size buffer
COB_graph = deque(maxlen=50)
WSD_graph = deque(maxlen=50)
FC_graph = deque(maxlen=50)
EMG_graph = deque(maxlen=50)

# Graph setup
fig, axs = plt.subplots(4, 1, figsize=(10, 8))
plt.subplots_adjust(hspace=0.5)

def update_plot(frame):
    for ax in axs:
        ax.clear()

    # Plot each graph with reduced complexity
    axs[0].plot(COB_graph, label="COB", color="blue")
    axs[0].set_title("Center of Balance (COB)")
    axs[0].legend()
    axs[0].grid(False)  # Disable grid for faster rendering

    axs[1].plot(WSD_graph, label="WSD", color="orange")
    axs[1].set_title("Wavelet Standard Deviation (WSD)")
    axs[1].legend()
    axs[1].grid(False)

    axs[2].plot(FC_graph, label="Fatigue Coefficient (FC)", color="red")
    axs[2].set_title("Fatigue Coefficient (FC)")
    axs[2].legend()
    axs[2].grid(False)

    axs[3].plot(EMG_graph, label="EMG value (EMG)", color="yellow")
    axs[3].set_title("EMG Graph")
    axs[3].legend()
    axs[3].grid(False)

    plt.tight_layout()

def main_logic():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT)
    from grove.helper import SlotHelper  # type: ignore
    sh = SlotHelper(SlotHelper.ADC)
    pin = sh.argv2pin()

    sensor = EMGTEST(pin)

    # Holds multiple COB, WSD, and FC calculations
    COB_Arr = []
    WSD_Arr = []
    FC_Arr = []
    sens_arr = []

    while True:
        if len(sens_arr) < 100:
            sens_arr.append(sensor.value)
            EMG_graph.append(sensor.value)
            
            time.sleep(0.005)  # Add slight delay to reduce CPU usage
        else:
            # Grab Wavelet Coefficient (w)
            w = pywt.downcoef('a', sens_arr, 'db2')
            sens_arr = []

            if len(COB_Arr) < 30:
                w_sum = 0
                w_sum = sum(abs(n) for n in w)
                L = 12  # Placeholder for L

                if w_sum != 0:
                    cob_sum = 0
                    wsd_sum = 0
                    count = 0
                    cob_sum = sum(abs(n) * (2**(L - count - 1) - 1) for count, n in enumerate(w))
                    COB = cob_sum / w_sum
                    COB_Arr.append(COB)
                    COB_graph.append(COB)

                    count = 0

                    wsd_sum = sum(abs(n) * (L - count - COB)**2 for count, n in enumerate(w))
                    WSD = math.sqrt(abs(wsd_sum / w_sum))
                    WSD_Arr.append(WSD)
                    WSD_graph.append(WSD)
                else:
                    COB_Arr.append(0)
                    WSD_Arr.append(0)
                    COB_graph.append(0)
                    WSD_graph.append(0)
            else:
                avg_COB = sum(COB_Arr) / (len(COB_Arr) - 1)
                ICOB_sum = 0
                ICOB_sum = sum(abs(n - avg_COB) for n in COB_Arr)
                ICOB = math.sqrt((1 / len(COB_Arr)) * ICOB_sum)
                COB_Arr = []
  
                avg_WSD = sum(WSD_Arr) / (len(WSD_Arr) - 1)
                WSD_sum = 0
                WSD_sum = sum(abs(n - avg_WSD) for n in WSD_Arr)
                ME = WSD_sum / len(WSD_Arr)
                WSD_Arr = []

                FC = ME * ICOB
                FC_Arr.append(FC)
                FC_graph.append(FC)

                if len(FC_Arr) > 5:
                    last_FC = FC_Arr[0]
                    AVG_DIFF = []
                    for n in range(1,6):
                        AVG_Diff.append(abs(FC_Arr[n] - last_FC))
                        last_FC = FC_Arr[n]
                    if sum(AVG_Diff) / len(AVG_Diff) < 75:
                        print("Fatigued Muscle")
                        GPIO.output(4, GPIO.HIGH)
                    else:
                        GPIO.output(4, GPIO.LOW)

                    AVG_Diff = []
                    FC_Arr = []

ani = FuncAnimation(fig, update_plot, interval=100, blit=True)  # Update every 2 seconds with blit enabled

if __name__ == '__main__':
    # Run main logic in a separate thread
    thread = Thread(target=main_logic, daemon=True)
    thread.start()

    # Show the graph
    plt.show()
