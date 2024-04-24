import time, sys
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

    while True:
        print("Current Voltage % is: {}".format(sensor.value/10))


if __name__ == '__main__':
    main()
