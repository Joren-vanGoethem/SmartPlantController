import time
from RPi import GPIO
GPIO.setmode(GPIO.BCM)
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from threading import Thread

# Software SPI configuration:                                                                                           
CLK  = 21                                                                                                              
MISO = 19                                                                                                               
MOSI = 20                                                                                                               
CS   = 16 
# LampPin = 10
# PumpPin = 9
# Llowerlimit = 200
# Lupperlimit = 500
# Plowerlimit = 800
# Pupperlimit = 400

mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI) 

class LDR:
    def __init__(self, lamp, lowerlimit, upperlimit):
        GPIO.setup(lamp, GPIO.OUT)
        self.lowerlimit = lowerlimit
        self.upperlimit = upperlimit
        self.lamp = lamp
        self.manual = False
        self.status = 0
        
    def read_sensor(self):
        value = mcp.read_adc(1)                                                                                         
        return value   

    def lights(self, sensordata):
        if self.manual == True:
            GPIO.output(self.lamp, not self.status)
            return self.status
        elif sensordata <= (self.lowerlimit) and self.manual == False:
            GPIO.output(self.lamp, GPIO.LOW)
            self.status = 1
            return self.status
        elif sensordata >= (self.upperlimit) and self.manual == False:
            GPIO.output(self.lamp, GPIO.HIGH)
            self.status = 0
            return self.status
        else:
            GPIO.output(self.lamp, GPIO.HIGH)
            self.status = 0
            return self.status
        
    def turn_off(self):
        GPIO.output(self.lamp, GPIO.HIGH)
        self.manual = True
        self.status = 0
    
    def turn_on(self):
        GPIO.output(self.lamp, GPIO.LOW)
        self.manual = True
        self.status = 1

    def auto(self):
        self.manual = False
    
    def read_status(self):
        return self.status

class SOIL:
    def __init__(self, pump, lowerlimit, upperlimit):
        GPIO.setup(pump, GPIO.OUT)
        self.lowerlimit = lowerlimit
        self.upperlimit = upperlimit
        self.pump = pump
        self.manual = False
        self.status = 0        

    def read_sensor(self):
        value = 1023 - mcp.read_adc(0)                                                                                    
        return value 

    def pumps(self, sensordata):
        if self.manual:
            GPIO.output(self.pump, not self.status)
            return self.status
        elif sensordata <= (self.lowerlimit):
            GPIO.output(self.pump, GPIO.LOW)
            self.status = 1
            return self.status
        elif sensordata >= (self.upperlimit):
            GPIO.output(self.pump, GPIO.HIGH)
            self.status = 0
            return self.status
        else: 
            GPIO.output(self.pump, GPIO.HIGH)
            self.status = 0
            return self.status
        
    
    def turn_off(self):
        GPIO.output(self.pump, GPIO.HIGH)
        self.manual = True
        self.status = 0
    
    def turn_on(self):
        GPIO.output(self.pump, GPIO.LOW)
        self.manual = True
        self.status = 1
    
    def auto(self):
        self.manual = False

    def read_status(self):
        return self.status