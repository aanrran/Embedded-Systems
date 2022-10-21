import network
import esp32
import machine
import time
from machine import Timer
try:
  import usocket as socket
except:
  import socket


global counter
counter = 0
base_url = 'https://api.thingspeak.com/update'
API_key = '?api_key=NHRBE6TNM29CZ086'

# enable station interface and connect to WiFi access point
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect('Netgear84', 'sweetboat200')
    while not wlan.isconnected():
        pass
print('network config:', wlan.ifconfig())
    

# function to send the temperature data and the hall sensor data to thingspeak with socket lib
def http_get(url):
    global counter # a counter to count how many times the data has been sent
    _, _, host, path = url.split('/', 3) # process the url
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8')) # send the data to thingspeak
    while True:
        data = s.recv(100)
        if data:
            machine.idle()
        else:
            break
    counter = counter + 1 # increment the counter once the data is sent
    s.close()

# this function gets called every time the alarm is waked up
def alarm_handler (t):
    hall = esp32.hall_sensor() # measure hall sensor data
    temp = esp32.raw_temperature() # measure temperature sensor data
    url = base_url + API_key + '&field1=' + str(temp) + '&field2=' + str(hall) # preprocess the data and server info
    http_get(url) # send the data to thingspeak
    print(f'temperature: {temp}F and Hall: {hall}')

# init the timer
tim = Timer(-1)

# periodic with 30s period
tim.init(mode=Timer.PERIODIC, period=30000, callback=alarm_handler)
# if ten data has sent, turn off the system
while True:
    if counter > 9:
        tim.deinit() # turn off the timer interrupt
        wlan.disconnect() # turn off the internet
        print('finish!')
        break
# reference: https://pythonforundergradengineers.com/micropython-wifi.html
