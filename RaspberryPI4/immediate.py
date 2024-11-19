import time, sys, math, pywt
import RPi.GPIO as GPIO
from grove.adc import ADC  # type: ignore
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

__all__ = ["EMGTEST"]

class EMGTEST(object):
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def value(self):
        return self.adc.read(self.channel)

Grove = EMGTEST

# Graphing data storage
COB_graph = []
WSD_graph = []
FC_graph = []

# Graph setup
fig, axs = plt.subplots(3, 1, figsize=(10, 8))
plt.subplots_adjust(hspace=0.5)

def update_plot(frame):
    for ax in axs:
        ax.clear()

    axs[0].plot(COB_graph[-50:], label="COB", color="blue")
    axs[0].set_title("Center of Balance (COB)")
    axs[0].legend()
    axs[0].grid()

    axs[1].plot(WSD_graph[-50:], label="WSD", color="orange")
    axs[1].set_title("Wavelet Standard Deviation (WSD)")
    axs[1].legend()
    axs[1].grid()

    axs[2].plot(FC_graph[-50:], label="Fatigue Coefficient (FC)", color="red")
    axs[2].set_title("Fatigue Coefficient (FC)")
    axs[2].legend()
    axs[2].grid()

    plt.tight_layout()

def main():
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
        if len(sens_arr) < 1000:
            sens_arr.append(sensor.value)
        else:
            # Grab Wavelet Coefficient (w)
            w = pywt.downcoef('a', sens_arr, 'db2')
            sens_arr = []

            if len(COB_Arr) < 30:
                w_sum = sum(abs(n) for n in w)
                L = 12  # Placeholder for L

                if w_sum != 0:
                    cob_sum = sum(abs(n) * (2**(L - count - 1) - 1) for count, n in enumerate(w))
                    COB = cob_sum / w_sum
                    COB_Arr.append(COB)
                    COB_graph.append(COB)

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
                avg_COB = sum(COB_Arr) / len(COB_Arr)
                ICOB_sum = sum(abs(n - avg_COB) for n in COB_Arr)
                ICOB = math.sqrt((1 / len(COB_Arr)) * ICOB_sum)
                COB_Arr = []

                avg_WSD = sum(WSD_Arr) / len(WSD_Arr)
                ME = sum(abs(n - avg_WSD) for n in WSD_Arr) / len(WSD_Arr)
                WSD_Arr = []

                FC = ME * ICOB
                FC_Arr.append(FC)
                FC_graph.append(FC)

                if len(FC_Arr) > 5:
                    last_FC = FC_Arr[0]
                    AVG_Diff = [abs(FC_Arr[n] - last_FC) for n in range(1, 6)]
                    if sum(AVG_Diff) / len(AVG_Diff) < 75:
                        print("Fatigued Muscle")
                        GPIO.output(4, GPIO.HIGH)
                    else:
                        GPIO.output(4, GPIO.LOW)
                    FC_Arr = []

ani = FuncAnimation(fig, update_plot, interval=1000)

if __name__ == '__main__':
    plt.show(block=False)
    main()
