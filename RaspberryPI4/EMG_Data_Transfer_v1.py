import time, sys, math, pywt
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
    from grove.helper import SlotHelper                                                             #type: ignore
    sh = SlotHelper(SlotHelper.ADC)
    pin = sh.argv2pin()

    sensor = EMGTEST(pin)

    #Holds multiple COB, WSD, and FC calculations
    COB_Arr = [0]
    WSD_Arr = [0]
    FC_Arr = [0]
    sens_arr = [0]

    while True:
        print("Current Voltage % is: {}".format(sensor.value/10))

        if(len(sens_arr) < 51):
            sens_arr.append(sensor.value)
        else:
            #Grab Wavelet Coefficient (w)
            w = pywt.wavedec(sens_arr, 'db2')
            sens_arr = [0]

            if(len(COB_Arr)<51): #51 is arbitrary number chosen until testing is done
                #Get sum of wavelet coefficients
                w_sum = 0
                for n in w:
                    w_sum+=abs(n)

                #Get length of w, Note that this isn't the L that should be used, this is a place holder
                L = len(w)

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
                    COB = cob_sum/w_sum
                    COB_Arr.append(COB)

                    for n in w:
                         wsd_sum+=abs(n)*(L-count-COB**2)
                    WSD_Arr.append(math.sqrt(wsd_sum/w_sum))
            else:
                #Calculate Center of Balance Transition (ICOB)
                #ICOB = sqrt((1/N)sum_1^N((COB - avg(COB))^2))
                avg_COB = sum(COB_Arr)/(len(COB_Arr)-1)

                ICOB_sum = 0
                for n in COB_Arr:
                    ICOB_sum += (n-avg_COB)**2
                ICOB = math.sqrt((1/len(COB_Arr)*ICOB_sum))

		        #Reset COB_Arr
                COB_Arr = [0]

		        #Calculate Muscular Tissue Effeciency (ME)
		        #ME = avg(|WSD - avg(WSD)|)
                avg_WSD = sum(WSD_Arr)/(len(WSD_Arr)-1)
                WSD_sum = 0
                for n in WSD_Arr:
                    WSD_sum += math.abs(n - avg_WSD)
                ME = WSD_sum/len(WSD_Arr)

                #Reset WSD_Arr
                WSD_Arr = [0]

		        #Add Fatigue Coefficiant
                FC_Arr.append(ME*ICOB)
	
	        #Check if we have enough fatigue coefficients to test the average difference
	        #If the average difference is low enough, alert the user their muscles are fatigued
            if(len(FC_Arr) == 10): #10 is an arbitrary number chosen until testing is done
                last_FC = 0
                AVG_Diff = [0]
                for n in FC_Arr:
                    last_FC = n
                AVG_Diff.append(math.abs(n-last_FC))

                if(sum(AVG_Diff)/(len(AVG_Diff)-1)<1): #using placeholder until testing gives us better values to use, need to change <1
                    do_something = 1 #Placeholder for sent signal to out


if __name__ == '__main__':
    main()
