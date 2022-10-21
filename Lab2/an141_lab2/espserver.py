import gc
import time
import network
import esp32
import machine
import time
from machine import Pin
try:
  import usocket as socket
except:
  import socket

gc.collect() # garbage collector

# Global variables
temp = 0 # measure temperature sensor data
hall = 0 # measure hall sensor data

ssid = 'Netgear84' # wifi ID
password = 'sweetboat200' # wifi password

# enable station interface and connect to WiFi access point
wlan = network.WLAN(network.STA_IF) # set the ESP32 as a Wi-Fi station
wlan.active(True) #  activate the station
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
print('network config:', wlan.ifconfig())

# initiate the LED pin
led = Pin(32, Pin.OUT)


# web page HTML generator
def web_page():
    gpio_state = "OFF" # string, check state of red led, ON or OFF
    # if the led is on the update the red led state to on etc.
    if led.value() == 1:
        gpio_state="ON"
    else:
        gpio_state="OFF"
  
    """Function to build the HTML webpage which should be displayed
    in client (web browser on PC or phone) when the client sends a request
    the ESP32 server.
    
    The server should send necessary header information to the client
    (YOU HAVE TO FIND OUT WHAT HEADER YOUR SERVER NEEDS TO SEND)
    and then only send the HTML webpage to the client.
    
    Global variables:
    temp, hall, red_led_state
    """
    
    html_webpage = """<!DOCTYPE HTML><html>
    <head>
    <title>ESP32 Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <style>
    html {
     font-family: Arial;
     display: inline-block;
     margin: 0px auto;
     text-align: center;
    }
    h1 { font-size: 3.0rem; }
    p { font-size: 3.0rem; }
    .units { font-size: 1.5rem; }
    .sensor-labels{
      font-size: 1.5rem;
      vertical-align:middle;
      padding-bottom: 15px;
    }
    .button {
        display: inline-block; background-color: #e7bd3b; border: none; 
        border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none;
        font-size: 30px; margin: 2px; cursor: pointer;
    }
    .button2 {
        background-color: #4286f4;
    }
    </style>
    </head>
    <body>
    <h1>ESP32 WEB Server</h1>
    <p>
    <i class="fas fa-thermometer-half" style="color:#059e8a;"></i> 
    <span class="sensor-labels">Temperature</span> 
    <span>"""+str(temp)+"""</span>
    <sup class="units">&deg;F</sup>
    </p>
    <p>
    <i class="fas fa-bolt" style="color:#00add6;"></i>
    <span class="sensor-labels">Hall</span>
    <span>"""+str(hall)+"""</span>
    <sup class="units">V</sup>
    </p>
    <p>
    RED LED Current State: <strong>""" + gpio_state + """</strong>
    </p>
    <p>
    <a href="/?led=on"><button class="button">RED ON</button></a>
    </p>
    <p>
    <a href="/?led=off"><button class="button button2">RED OFF</button></a>
    </p>
    </body>
    </html>"""
    return html_webpage

# start the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a new socket object called s with the given address family, and socket type
s.bind(('', 80)) # bind the socket to an address (network interface and port number)
s.listen(5) # specifies the maximum number of queued connections

# loop to refresh the server to send and receive
while True:
  conn, addr = s.accept() # accept the connection
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024) # gets the request received on the newly created socket and saves it in the request variable
  request = str(request)
  print('Content = %s' % request)
  led_on = request.find('/?led=on')
  led_off = request.find('/?led=off')
  
  # check if LED button is click
  if led_on == 6:
    print('LED ON')
    led.value(1)
  if led_off == 6:
    print('LED OFF')
    led.value(0)
  hall = esp32.hall_sensor() # measure hall sensor data
  temp = esp32.raw_temperature() # measure temperature sensor data
  response = web_page()
  
  # send the response to the socket client using the send() and sendall() methods
  conn.send('HTTP/1.1 200 OK\n')
  conn.send('Content-Type: text/html\n')
  conn.send('Connection: close\n\n')
  conn.sendall(response)
  conn.close()
  
  # reference https://randomnerdtutorials.com/esp32-esp8266-micropython-web-server/