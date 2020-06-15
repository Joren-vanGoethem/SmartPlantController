# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

import time
import threading
import multiprocessing

# Code voor led
from RPi import GPIO

#code voor licht en soil moisture sensor
import HardwareControl.MCP
from HardwareControl.MCP import LDR, SOIL

#code voor temperatuur sensor
import HardwareControl.TEMP
from HardwareControl.TEMP import TEMP

#code voor LCD en IP class
import HardwareControl.LCD as LCD
import HardwareControl.IP as IP

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

pollingspeed = 1
processes = []
# actuatorstatus = multiprocessing.Array('i', 3)
actuatorstatus = [0,0,0]
# API ENDPOINTS
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

# SOCKET IO
@socketio.on('connect')
def initial_connection():
    global actuatorstatus
    print('A new client connect')
    Sensors = DataRepository.read_sensor_settings()
    if len(processes) == 0:
        for sensor in Sensors:
            if sensor['Active'] == 1:
                Name = DataRepository.read_sensorname_by_id(sensor['SensorID'])
                Name = Name['SensorName']
                LowerLimit = sensor['LowerLimit']
                UpperLimit = sensor['UpperLimit']
                Pin = sensor['ActuatorPin']

                if Name == "LDR":
                    ldr = LDR(Pin, int(LowerLimit), int(UpperLimit))
                    ldrprocess = threading.Thread(target=LightSensor, args=[ldr, actuatorstatus])
                    processes.append(ldrprocess)

                elif Name == "SOIL":
                    soil = SOIL(Pin, int(LowerLimit), int(UpperLimit))
                    soilprocess = threading.Thread(target=SoilSensor, args=[soil, actuatorstatus])
                    processes.append(soilprocess)

                elif Name == "TEMP":
                    temp = TEMP(Pin, int(LowerLimit), int(UpperLimit))
                    tempprocess = threading.Thread(target=TempSensor, args=[temp, actuatorstatus])
                    processes.append(tempprocess)
        lcd = LCD.lcd()
        ip = IP.IP()
        lcdprocess = threading.Thread(target=iplcd, args=[lcd, ip])
        processes.append(lcdprocess)
        emitprocess = threading.Thread(target=emitsensordata, args=[actuatorstatus])
        processes.append(emitprocess)

        startProcesses(processes)
    socketio.emit('connected', broadcast=True)
    
def startProcesses(processes):
    for process in processes:
        process.start()

def LightSensor(ldr, actuatorstatus):
    while True:
        print('ldr')
        sensordata = ldr.read_sensor()
        status = ldr.lights(sensordata)
        actuatorstatus[0] = status
        time.sleep(pollingspeed)

def SoilSensor(soil, actuatorstatus):
    while True:
        print('soil')
        sensordata = soil.read_sensor()
        status = soil.pumps(sensordata)
        actuatorstatus[1] = status
        time.sleep(pollingspeed)

def TempSensor(temp, actuatorstatus):
    while True:
        print('temp')
        temp.read_sensor()
        status = temp.heating()
        actuatorstatus[2] = status
        time.sleep(pollingspeed)

def iplcd(lcd, ip):
    while True:
        addresses = ip.return_ip()
        for i in range(2):
            lcd.lcd_display_string(str(addresses[i]), int(i+1))
        time.sleep(pollingspeed)

def emitsensordata(actuatorstatus):
    while True:
        led = actuatorstatus[0]
        pump = actuatorstatus[1]
        heater = actuatorstatus[2]
        print(led,pump,heater)
        data={'led': led, 'pump': pump,'heater': heater}
        socketio.emit('B2F_verandering_actuator', data, broadcast=True)
        time.sleep(pollingspeed)



if __name__ == '__main__':
    socketio.run(app, debug=True,  host='0.0.0.0')
