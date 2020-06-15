from RPi import GPIO
GPIO.setmode(GPIO.BCM)
import time

sensor_file_name = '/sys/bus/w1/devices/w1_bus_master1/28-01191b1a69fd/w1_slave'

class TEMP:
    def __init__(self, heater, lowerlimit, upperlimit):
        GPIO.setup(heater, GPIO.OUT)
        self.heater = heater
        self.lowerlimit = lowerlimit
        self.upperlimit = upperlimit
        self.manual = False
        self.status = 0

    def read_sensor(self):
        self.sensor = open(sensor_file_name, 'r')
        for line in self.sensor:
            if 't=' in line:
                split = line.split('=', 1)
                # print(split[1])
                self.temp_sensor = float(split[1]) / 1000.00
                # print("Temperatuur: ",self.temp_sensor,"\u00b0C")
        return self.temp_sensor

    #.1 toegevoegd als kleine hysterese waarde, meer was niet nodig aangezien de sensor geen grote variaties had in temperatuur 
    def heating(self):
        if self.manual:
            GPIO.output(self.heater, not self.status)
            return self.status
        elif self.temp_sensor <= (self.lowerlimit):
            GPIO.output(self.heater, GPIO.LOW)
            return 1
        elif self.temp_sensor >= (self.upperlimit):
            GPIO.output(self.heater, GPIO.HIGH)
            return 0
        else: #gaf error als waarde tussen de 2 limits lag bij opstart
            GPIO.output(self.heater, GPIO.HIGH)
            return 0

    def turn_off(self):
        GPIO.output(self.heater, GPIO.HIGH)
        self.manual = True
        self.status = 0
    
    def turn_on(self):
        GPIO.output(self.heater, GPIO.LOW)
        self.manual = True
        self.status = 1
    
    def auto(self):
        self.manual = False

    def read_status(self):
        return self.status
    
        
        
    
