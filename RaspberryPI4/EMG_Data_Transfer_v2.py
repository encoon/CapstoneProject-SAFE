import time, sys, math, pywt
import RPi.GPIO as GPIO
from grove.adc import ADC                                                                           # type: ignore

__all__ = ["EMGTEST"]

class EMGTEST(object):
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def value(self):
        return self.adc.read(self.channel)


Grove = EMGTEST

def main():

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT)
    from grove.helper import SlotHelper                                                             #type: ignore
    sh = SlotHelper(SlotHelper.ADC)
    pin = sh.argv2pin()

    sensor = EMGTEST(pin)

    #Holds multiple COB, WSD, and FC calculations
    COB_Arr = []
    WSD_Arr = []
    FC_Arr = []
    sens_arr = []

    while True:
        #print("Current Voltage % is: {}".format(sensor.value/10))

        if(len(sens_arr) < 100):
            sens_arr.append(sensor.value)
            #print("Sensor Value: {}".format(sensor.value))
        else:
            #Grab Wavelet Coefficient (w)
            w = pywt.downcoef('a', sens_arr, 'db2')
            #print("Wavelete coefficients: {}".format(w))
            #print("Wavelete coefficients: {}".format(w))
            sens_arr = []

            if(len(COB_Arr)<30): #51 is arbitrary number chosen until testing is done
                #Get sum of wavelet coefficients
                w_sum = 0
                for n in w:
                    w_sum+=abs(n)

                #Get length of w, Note that this isn't the L that should be used, this is a place holder
                
###
###             # L is not the length of the wavelet coefficient array! 
###
                
                L = 12

                #Calculate Wavelet Center of Balance (COB)
                #COB = 1/(sum_1^L(|w_k|))*sum_1^L(|w_k|*(2^{L-k}-1))
                #Calculate Wavelet Standard Deviation (WSD)
                #WSD = sqrt((sum_k^L(|w_k|*(L-k-COB^2)))/(sum_1^L(w_k)))
                if(w_sum!=0):
                    cob_sum = 0
                    wsd_sum = 0
                    count = 0
                    for n in w:
                        count+=1
                        cob_sum += abs(n)*(2**(L-count)-1)
                        #print("cob_sum using L-count: {}".format(cob_sum))
                        #print("current w_sum is: {}".format(w_sum))
                        #print("L-count: {}".format(L-count))
                    COB = cob_sum/w_sum
                    COB_Arr.append(COB)
                    #print("COB: {}".format(COB))

                    count = 0
                    for n in w:
                        count+=1
                        wsd_sum+=abs(n)*(L-count-COB)**2
                    WSD_Arr.append(math.sqrt(abs(wsd_sum/w_sum)))
                    #print("WSD: {}".format(math.sqrt(abs(wsd_sum/w_sum))))
                else:
                    COB_Arr.append(0)
                    WSD_Arr.append(0)
            else:
                #Calculate Center of Balance Transition (ICOB)
                #ICOB = sqrt((1/N)sum_1^N((COB - avg(COB))^2))
                avg_COB = sum(COB_Arr)/(len(COB_Arr)-1)

                ICOB_sum = 0
                for n in COB_Arr:
                    ICOB_sum += abs(n-avg_COB)
                ICOB = math.sqrt((1/len(COB_Arr)*ICOB_sum))
                #print("ICOB: {}".format(ICOB))

		        #Reset COB_Arr
                COB_Arr = []

		        #Calculate Muscular Tissue Effeciency (ME)
		        #ME = avg(|WSD - avg(WSD)|)
                avg_WSD = sum(WSD_Arr)/(len(WSD_Arr)-1)
                WSD_sum = 0
                for n in WSD_Arr:
                    WSD_sum += abs(n - avg_WSD)
                ME = WSD_sum/len(WSD_Arr)
                #print("ME: {}".format(ME))

                #Reset WSD_Arr
                WSD_Arr = []

		        #Add Fatigue Coefficiant
                FC_Arr.append(ME*ICOB)
                #print("FC: {}".format(ME*ICOB))
                #print("Current Voltage % is: {}".format(sensor.value/10))
	
	        #Check if we have enough fatigue coefficients to test the average difference
            #Amount of Fatigue Coefficients chosen to have a balance between amount of data and speed of code
	        #If the average difference is low enough, alert the user their muscles are fatigued
            if(len(FC_Arr) > 5): 
                last_FC = FC_Arr[0]
                AVG_Diff = []
                for n in range(1,6):
                    AVG_Diff.append(abs(FC_Arr[n]-last_FC))
                    last_FC = FC_Arr[n]

                #print("Current sum of AVG Diff is: {}".format(sum(AVG_Diff)))
                #print("Current length of AVG Diff is: {}".format(len(AVG_Diff)))

                #TODO: Find best value for threshold - follows similar trend to simulations
                #Current testing shows 75 to be vaguely best value for threshold - more testing required - suggest raising to 77 or 78
                if(sum(AVG_Diff)/(len(AVG_Diff))<75):
                    print("Fatigued Muscle")
                    GPIO.output(4, GPIO.HIGH)
                else:
                    GPIO.output(4, GPIO.LOW)
                
                AVG_Diff = []
                FC_Arr = []


if __name__ == '__main__':
    main()
