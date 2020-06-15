#region imports
# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

# code voor fotos te maken met picamera
from picamera import PiCamera
from PIL import Image
import imageio

# code voor grafieken
import pygal
from pygal.style import Style

import time
import datetime
import threading
import os
from subprocess import call

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
#endregion

#region flask/socketio
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)
endpoint = '/api/v1'
#endregion

#region Variables
pollingspeed = float(DataRepository.read_data_setting("SensorPolling")['SpeedInSeconds'])
databaseWriteInterval = float(DataRepository.read_data_setting("dbWrite")['SpeedInSeconds'])
processes = []  
actuatorstatus = [0,0,0]
sensorvalues = [0,0,0]
resetVariables = False
ManualLDR = False
ManualSOIL = False
ManualTEMP = False
#endregion

#region API ENDPOINTS
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

@app.route(endpoint+'/pictures', methods=['GET'])
def get_pictures():
    if request.method == 'GET':
        s = DataRepository.get_picture_locations()
        return jsonify(data=s), 200

@app.route(endpoint+'/actuators/<Name>/<Status>', methods=['POST'])
def turn_on_or_off_actuator(Name,Status):
    if request.method == 'POST':
        threading.Thread(target=manual_actuator, args=[str(Name),int(Status)]).start()
        return jsonify(message='done'), 200

@app.route(endpoint+'/settings', methods=['GET'])
def getSettings():
    if request.method == 'GET':
        sensordata = {}
        pollingdata = {}
        timelimits = []
        Sensors = DataRepository.read_sensor_settings()
        polling = DataRepository.read_data_settings_all()
        limits = DataRepository.read_time_limits()
        i=1
        for sensor in Sensors:
            SensorID = sensor['DeviceID']
            LowerLimit = sensor['LowerLimit']
            UpperLimit = sensor['UpperLimit']
            Active = sensor['Active']
            sensordata.update({f'{i}':[SensorID,UpperLimit,LowerLimit,Active]})
            i+=1
        i=1
        for setting in polling:
            Name = setting['Name']
            Speed = float(setting['SpeedInSeconds'])
            pollingdata.update({f'{i}':[Name,Speed]})
            i+=1
        timelimits.append(f'{limits["startTime"]}')
        timelimits.append(f'{limits["stopTime"]}')
        return jsonify([sensordata, pollingdata, timelimits]), 200

#endregion

#region SOCKET IO
@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    socketio.emit('connected')
    
@socketio.on('F2B_ChangeSensorSettings')
def Change_sensor_settings(data):
    for i in range(len(data)):
        id = data[f'{i}'][0]
        UpperLimit = int(data[f'{i}'][1])
        LowerLimit = int(data[f'{i}'][2])
        Active = int(data[f'{i}'][3])
        DataRepository.update_sensorsettings(id,UpperLimit,LowerLimit,Active)

@socketio.on('F2B_ChangeDataSettings')
def Change_data_settings(data):
    for i in range(len(data)):
        Name = data[f'{i}'][0]
        Speed = float(data[f'{i}'][1])
        DataRepository.update_datasettings(Speed,Name)

@socketio.on('F2B_ChangeTimeSettings')
def Change_time_settings(data):
    startTime = data['0'][1]
    stopTime = data['1'][1]
    DataRepository.update_TimeLimits(startTime, stopTime)
    resetPollingspeeds()
    resetVars()

@socketio.on('F2B_ShutDown')
def ShutDown(data):
    call("sudo shutdown -f now", shell=True)
#endregion

#region processes
def CreateProcesses():
    global ldr
    global soil
    global temp
    global processes
    DataRepository.clear_old_data()
    Sensors = DataRepository.read_sensor_settings()
    timelimits = DataRepository.read_time_limits()
    StartTime = timelimits['startTime'].total_seconds()/3600
    StopTime = timelimits['stopTime'].total_seconds()/3600

    if len(processes) == 0:
        for sensor in Sensors:
            Name = DataRepository.read_sensorname_by_id(sensor['DeviceID'])
            
            Name = Name['DeviceName'] 

            LowerLimit = sensor['LowerLimit']
            UpperLimit = sensor['UpperLimit']
            Pin = sensor['ActuatorPin']

            if Name == "LDR":
                ldr = LDR(Pin, int(LowerLimit), int(UpperLimit))
                ldrprocess = threading.Thread(target=LightSensor, args=[ldr, actuatorstatus, StartTime, StopTime, sensorvalues, sensor['Active']])
                processes.append(ldrprocess)

            elif Name == "SOIL":
                soil = SOIL(Pin, int(LowerLimit), int(UpperLimit))
                soilprocess = threading.Thread(target=SoilSensor, args=[soil, actuatorstatus, sensorvalues, sensor['Active']])
                processes.append(soilprocess)

            elif Name == "TEMP":
                temp = TEMP(Pin, int(LowerLimit), int(UpperLimit))
                tempprocess = threading.Thread(target=TempSensor, args=[temp, actuatorstatus, sensorvalues, sensor['Active']])
                processes.append(tempprocess)
            
            
        PictureThread = threading.Thread(target=TakePictures, args=[DataRepository.read_deviceID_by_name('PiCamera')['DeviceID'],StartTime,StopTime,DataRepository.read_data_setting('CameraInterval')['SpeedInSeconds']])
        processes.append(PictureThread)

        lcd = LCD.lcd()
        ip = IP.IP()
        lcdprocess = threading.Thread(target=iplcd, args=[lcd, ip])
        processes.append(lcdprocess)

        emitprocess1 = threading.Thread(target=emitactuatorstatus, args=[actuatorstatus])
        processes.append(emitprocess1)

        emitprocess2 = threading.Thread(target=emitsensordata, args=[sensorvalues])
        processes.append(emitprocess2)

        writetodatabase = threading.Thread(target=writesensordata, args=[sensorvalues, databaseWriteInterval])
        processes.append(writetodatabase)

        graphCreator = threading.Thread(target=create_graphs)
        processes.append(graphCreator)

        startProcesses()

def startProcesses():
    global processes
    for process in processes:
        process.start()

def resetVars():
    global resetVariables
    resetVariables = True
    time.sleep(pollingspeed*1.5)
    resetVariables = False

def resetPollingspeeds():
    global pollingspeed
    global databaseWriteInterval
    pollingspeed = float(DataRepository.read_data_setting("SensorPolling")['SpeedInSeconds'])
    databaseWriteInterval = float(DataRepository.read_data_setting("dbWrite")['SpeedInSeconds'])
#endregion

#region hardwareprocesses
def LightSensor(ldr, actuatorstatus, StartTime, StopTime, sensorvalues, active):
    global resetVariables
    global ManualLDR
    while True:
        currentHour = datetime.datetime.now().hour
        if currentHour == 0.0:
            currentHour = 24.0
        if (active == 1 and resetVariables == False and ManualLDR == False): 
            if (currentHour < StopTime and currentHour >= StartTime):
                sensordata = ldr.read_sensor()
                status = ldr.lights(sensordata)
                actuatorstatus[0] = status
                sensorvalues[0] = sensordata 
            elif (currentHour >= StopTime or currentHour < StartTime):
                ldr.turn_off()
                sensordata = ldr.read_sensor()
                actuatorstatus[0] = 0
                sensorvalues[0] = sensordata
        elif (active == 0 and resetVariables == False and ManualLDR == False):
            ldr.turn_off()
            sensordata = ldr.read_sensor()
            actuatorstatus[0] = 0
            sensorvalues[0] = sensordata
        elif resetVariables == True:
            sensor = DataRepository.read_sensor_settings_by_id(1)
            LowerLimit = sensor['LowerLimit']
            UpperLimit = sensor['UpperLimit']
            Pin = sensor['ActuatorPin']
            ldr = LDR(Pin, int(LowerLimit), int(UpperLimit))
            active = sensor['Active']
        elif ManualLDR == True:
            sensordata = ldr.read_sensor()
            status = ldr.read_status()
            actuatorstatus[0] = status
            sensorvalues[0] = sensordata
        else:
            ldr.turn_off()
            sensordata = ldr.read_sensor()
            status = ldr.read_status()
            actuatorstatus[0] = 0
            sensorvalues[0] = sensordata
        time.sleep(pollingspeed)

def SoilSensor(soil, actuatorstatus, sensorvalues, active):
    global resetVariables
    global ManualSOIL
    
    soil.turn_off()
    time.sleep(pollingspeed)
    soil.auto()
    while True:
        if active == 1 and resetVariables == False and ManualSOIL == False:
            sensordata = soil.read_sensor()
            status = soil.pumps(sensordata)
            actuatorstatus[1] = status
            sensorvalues[1] = sensordata
        elif active == 0 and resetVariables == False and ManualSOIL == False:
            soil.turn_off()
            sensordata = soil.read_sensor()
            status = soil.pumps(sensordata)
            actuatorstatus[1] = 0
            sensorvalues[1] = sensordata    
        elif resetVariables == True:
            sensor = DataRepository.read_sensor_settings_by_id(2)
            LowerLimit = sensor['LowerLimit']
            UpperLimit = sensor['UpperLimit']
            Pin = sensor['ActuatorPin']
            soil = SOIL(Pin, int(LowerLimit), int(UpperLimit))
            active = sensor['Active']
        elif ManualSOIL == True:
            sensordata = soil.read_sensor()
            status = soil.read_status()
            actuatorstatus[1] = status
            sensorvalues[1] = sensordata
        time.sleep(pollingspeed)

def TempSensor(temp, actuatorstatus, sensorvalues, active):
    global resetVariables
    global ManualTEMP
    temp.turn_off()
    time.sleep(pollingspeed)
    temp.auto()
    while True:
        if active == 1 and resetVariables == False and ManualTEMP == False:
            sensordata = temp.read_sensor()
            status = temp.heating()
            actuatorstatus[2] = status
            sensorvalues[2] = sensordata
        elif active == 0 and resetVariables == False and ManualTEMP == False:
            sensordata = temp.read_sensor()
            status = temp.heating()
            actuatorstatus[2] = 0
            sensorvalues[2] = sensordata   
        elif resetVariables == True:
            sensor = DataRepository.read_sensor_settings_by_id(3)
            LowerLimit = sensor['LowerLimit']
            UpperLimit = sensor['UpperLimit']
            Pin = sensor['ActuatorPin']
            temp = TEMP(Pin, int(LowerLimit), int(UpperLimit))
            active = sensor['Active']
        elif ManualTEMP == True:
            sensordata = temp.read_sensor()
            status = temp.read_status()
            actuatorstatus[2] = status
            sensorvalues[2] = sensordata
        time.sleep(pollingspeed)

def iplcd(lcd, ip):
    while True:
        addresses = ip.return_ip()
        lcd.lcd_clear()
        for i in range(2):
            lcd.lcd_display_string(str(addresses[i]), int(i+1))
        time.sleep(pollingspeed*100)
       
def manual_actuator(Name, Status):
    global ldr
    global soil
    global temp
    global ManualLDR, ManualSOIL, ManualTEMP
    if Name == "LDR":
        ManualLDR = True
        time.sleep(0.3)
        if Status == 1:
            ldr.turn_on()
            time.sleep(5)
            ldr.auto()
        elif Status == 0:
            ldr.turn_off()
            time.sleep(5) 
            ldr.auto()
        ManualLDR = False

    elif Name == "SOIL":
        ManualSOIL = True
        time.sleep(0.3)
        if Status == 1:
            soil.turn_on()
            time.sleep(2) 
            soil.auto()
        else:
            soil.turn_off()
            time.sleep(2) 
            soil.auto()
        ManualSOIL = False

    elif Name == "TEMP":
        ManualTEMP = True
        time.sleep(0.3)
        if Status == 1:
            temp.turn_on()
            time.sleep(500) 
            temp.auto()
        else:
            temp.turn_off()
            time.sleep(500)
            temp.auto()
        ManualTEMP = False
#endregion

#region B2F
def emitactuatorstatus(actuatorstatus):
    while True:
        time.sleep(pollingspeed)
        led = actuatorstatus[0]
        pump = actuatorstatus[1]
        heater = actuatorstatus[2]
        data={'led': led, 'pump': pump,'heater': heater}
        data2=[]
        sensorsettings = DataRepository.read_sensor_settings()
        for sensor in sensorsettings:
            data2.append(sensor['Active'])
        socketio.emit('B2F_actuator_status', [data,data2])

def emitsensordata(sensorvalues):
    while True:
        time.sleep(pollingspeed)
        led = sensorvalues[0]
        pump = sensorvalues[1]
        heater = round(sensorvalues[2],2)
        data={'Light level': led, 'Soil moisture level': pump,'Temperature': heater}
        socketio.emit('B2F_sensor_data', data)
#endregion

#region Database
def writesensordata(sensorvalues, databaseWriteInterval):
    while True:
        time.sleep(databaseWriteInterval)
        for i in range(len(sensorvalues)):
            currentTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            DataRepository.insert_sensordata(i+1, currentTime, sensorvalues[i])
#endregion

#region Graphs
def create_graphs():
    periods =[1,7]
    while True:
        for p in range(len(periods)):
            s1,s2,s3 = [],[],[]
            v1,v2,v3 = [],[],[]
            sensors = [s1,s2,s3]
            values = [v1,v2,v3]
            for i in range(len(sensors)):
                sensors[i] = DataRepository.read_sensor_data_by_id(i+1, periods[p])
                for v in range(len(sensors[i])):
                    if i == 0 or i == 1:
                        values[i].append(float(sensors[i][v]['Value']/10.23))
                    elif i == 2:
                        values[i].append(float(sensors[i][v]['Value']))
            PygalGraphs(values, periods[p])
        print('graphs rendered')
        time.sleep(1800)

def PygalGraphs(values, period):
    try:
        custom_style = Style(
            colors=['#ffff00', '#00ff00','#ff0000'],
            background='White',
            plot_background='transparent',
            legend_font_size=18,
            label_font_size=18,
            major_label_font_size=18)
        if period == 1:
            filename = '/var/www/html/img/svg/graphDayALL.svg'
        elif period == 7: 
            filename = '/var/www/html/img/svg/graphWeekALL.svg'
    
        graph = pygal.Line(stroke_style={'width': 3, 'linecap': 'round', 'linejoin': 'round'}, style=custom_style, interpolate='cubic',show_dots=False,legend_at_bottom_columns=3,range=(0,100),secondary_range=(0,40))
        graph.add('Light Intensity', values[0])
        graph.add('Soil Moisture', values[1])
        graph.add('Temperature', values[2], secondary=True)

        graph.title = 'Sensor Data'
        graph.legend_at_bottom = True
        graph.render_to_file(filename=filename)
    except Exception as e:
        return(str(e))
#endregion

#region Camera
def TakePictures(id,startTime,stopTime, interval):
    camera = PiCamera()
    interval = int(interval/60)
    while True:
        latestPictureDate = DataRepository.get_latest_picture_date()
        latestPictureDate = latestPictureDate['DateTime']
        currentDate = datetime.datetime.now()
        if resetVariables == True:
            interval = int(DataRepository.read_data_setting('CameraInterval')['SpeedInSeconds']/60)
            print(interval)
        print(interval)
        if currentDate.hour >= startTime and currentDate.hour < stopTime and currentDate >= latestPictureDate+datetime.timedelta(minutes=interval):
            camera.resolution = (2592, 1944)
            location = f'/var/www/html/img/jpg/{currentDate}'
            # Camera warm-up time
            time.sleep(10)
            camera.capture(f'{location}.jpg')
            DataRepository.insert_new_picture_location(f'{location}.jpg', currentDate, id)
            print('picture')
            image = Image.open(f'{location}.jpg')
            image.save(f'{location}.jpg', "JPEG", quality=35)
            
            arr = os.listdir('/var/www/html/img/jpg/')
            # GIFList = []
            for i in range(len(arr)):
                pictureDate = datetime.datetime.strptime(arr[i][:-20], '%Y-%m-%d')
                if pictureDate < currentDate - datetime.timedelta(days=8):
                    os.remove(f'/var/www/html/img/jpg/{arr[i]}')
                    print(f'{arr[i]} removed')
                # else:
                    # GIFList.append(imageio.imread(f'/var/www/html/img/jpg/{arr[i]}'))
            # GIFList.sort()
            # imageio.mimsave('/var/www/html/img/gif/timelapse.gif', GIFList)
        time.sleep(pollingspeed)
#endregion

#region main loop
if __name__ == '__main__':
    try:
        CreateProcesses()
        socketio.run(app, debug=False,  host='0.0.0.0', port=5000)
    except KeyboardInterrupt as e:
        print(e)
        GPIO.cleanup()
#endregion
    
