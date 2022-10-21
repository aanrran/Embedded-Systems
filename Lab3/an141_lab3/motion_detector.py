import network
import urequests as requests
import ujson
import esp32
import machine
import time
from machine import Timer
from machine import SoftI2C, Pin
import mpu6050

global AcX_scaled
global AcY_scaled
global AcZ_scaled
global device_status
global device_moved
global AcX_scaled_lastime
global AcY_scaled_lastime
global AcZ_scaled_lastime
global accelerometer

device_status = 'activate'
device_moved = False

i2c = SoftI2C(scl=Pin(22), sda=Pin(23)) # initialize the i2C
accelerometer = mpu6050.accel(i2c) # initialize the accelerometer
# initialize the leds
red_led = Pin(32, Pin.OUT) 
green_led = Pin(33, Pin.OUT)
red_led.value(0)
green_led.value(1)
# calibrating the MPU6050 by
#  placing the MPU6050 upwards and read 3 sets of data.
#  placing the MUP6050 downwards and read 3 sets of data.
#  averaging the above datas to find the zero reading
#  subtracting acceleration of z axis from the above two groups of readings. And find the scale of the reading by comparing to gravity
input('please place MPU6050 upwards and click return key ')
AcX_avg = 0; # average acceleration in X axis
AcY_avg = 0; # average acceleration in Y axis
AcZ_avg = 0; # average acceleration in Z axis
AcZ_facingup_avg = 0; # average acceleration of Z axis when MPU6050 is facing up
for i in range(3): # measure 3 times to find the average
    AcX_avg = AcX_avg + accelerometer.get_values()['AcX']
    AcY_avg = AcY_avg + accelerometer.get_values()['AcY']
    AcZ_facingup_avg = AcZ_facingup_avg + accelerometer.get_values()['AcZ']
    time.sleep(0.5)

input('please place MPU6050 downwards and click return key ')
AcZ_facingdown_avg = 0; # average acceleration of Z axis when MPU6050 is facing down
for i in range(3): # measure 3 times to find the average
    AcX_avg = AcX_avg + accelerometer.get_values()['AcX']
    AcY_avg = AcY_avg + accelerometer.get_values()['AcY']
    AcZ_facingdown_avg = AcZ_facingdown_avg + accelerometer.get_values()['AcZ']
    time.sleep(0.5)
# find the true zero reading and the scale
AcX_avg = AcX_avg/6;
AcY_avg = AcY_avg/6;
AcZ_avg = (AcZ_facingup_avg + AcZ_facingdown_avg)/6;
Ac_scale = 9.8*2*3/(AcZ_facingdown_avg - AcZ_facingup_avg)

# print(accelerometer.get_values())


# enable station interface and connect to WiFi access point
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect('Netgear84', 'sweetboat200')
    while not wlan.isconnected():
        pass
print('network config:', wlan.ifconfig())


# check the device status should be activate or deactivate
def activation_handler (t):
    global device_status
    global device_moved
    global AcX_scaled
    global AcY_scaled
    global AcZ_scaled
    global AcX_scaled_lastime
    global AcY_scaled_lastime
    global AcZ_scaled_lastime
    global accelerometer
    # get results from the thingspeak
    get_url = 'https://api.thingspeak.com/channels/1716592/feeds.json?api_key=PZRABTW8AJMKF775&results=2'
    res = requests.get(get_url).json() 
    if res['feeds'][-1]['field1'] == 'activate': # read data from the thingspeak field1. The result should be activate or deactivate
        device_status = 'activate'
        # turn on green led and turn off the red led
        red_led.value(0)
        green_led.value(1)
        time.sleep(1)
        
        # initialize the sensor readings
        AcX_scaled = (accelerometer.get_values()['AcX'] - AcX_avg)*Ac_scale
        AcY_scaled = (accelerometer.get_values()['AcY'] - AcY_avg)*Ac_scale
        AcZ_scaled = (accelerometer.get_values()['AcZ'] - AcZ_avg)*Ac_scale

        AcX_scaled_lastime = AcX_scaled
        AcY_scaled_lastime = AcY_scaled
        AcZ_scaled_lastime = AcZ_scaled
        time.sleep(1)
    else:
        # reset the device
        device_status = 'deactivate'
        device_moved = False
        # turn off green led and the red led
        red_led.value(0)
        green_led.value(0)
        print('Motion Sensor Deactivated', end="\r")

def notification_handler (t):
    global AcX_scaled
    global AcY_scaled
    global AcZ_scaled
    if device_status == 'activate' and device_moved == True:
        # request url for posting the sensor values to the notification
        request_url = 'http://maker.ifttt.com/trigger/motion_detected/with/key/p5E6GuWJjUDyBNt1IEqwo?'+ 'value1=' + str(AcX_scaled) + '&value2=' + str(AcY_scaled) + '&value3=' + str(AcZ_scaled)
        res = requests.post(request_url)
        #print(res.text) # print the status of the posting request
# init the timer
activation_timer = Timer(0)
notification_timer =  Timer(1)
# periodic with 30s period
activation_timer.init(mode=Timer.PERIODIC, period=30000, callback=activation_handler)
# periodic with 60s period
notification_timer.init(mode=Timer.PERIODIC, period=60000, callback=notification_handler)

# initialize the sensor readings
AcX_scaled_lastime = (accelerometer.get_values()['AcX'] - AcX_avg)*Ac_scale
AcY_scaled_lastime = (accelerometer.get_values()['AcY'] - AcY_avg)*Ac_scale
AcZ_scaled_lastime = (accelerometer.get_values()['AcZ'] - AcZ_avg)*Ac_scale
time.sleep(1)

# background system, check the sensor reading every 1 sec
while True:
    if device_status == 'activate':
        # find the sensor reading and scale the reading to m/s2
        AcX_scaled = (accelerometer.get_values()['AcX'] - AcX_avg)*Ac_scale
        AcY_scaled = (accelerometer.get_values()['AcY'] - AcY_avg)*Ac_scale
        AcZ_scaled = (accelerometer.get_values()['AcZ'] - AcZ_avg)*Ac_scale
        print('Motion Sensor Activated ---',' AcX: ', AcX_scaled, ' AcY: ', AcY_scaled, ' AcZ: ', AcZ_scaled, end="\r") # print the system status
        if abs(AcX_scaled - AcX_scaled_lastime) > 1 or abs(AcY_scaled - AcY_scaled_lastime) > 1 or abs(AcZ_scaled - AcZ_scaled_lastime) > 1: # check if the sensor moved
            device_moved = True
            red_led.value(1) # turn on red LED to indicate motion
        # record the last sensor reading
        AcX_scaled_lastime = AcX_scaled
        AcY_scaled_lastime = AcY_scaled
        AcZ_scaled_lastime = AcZ_scaled
        time.sleep(1)
    else:
        time.sleep(1)
    


# reference https://esp32io.com/tutorials/esp32-ifttt
# reference https://www.youtube.com/watch?v=X-_25tzo8Cw
# reference https://makeblock-micropython-api.readthedocs.io/en/latest/public_library/Third-party-libraries/urequests.html
