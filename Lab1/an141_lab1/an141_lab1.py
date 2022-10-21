from machine import RTC, Timer
from machine import PWM, Pin
import machine
import time

# timer interrup implements
weekdays = ("Monday", "Tuesady", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday") # lookup table for weekdays

rtc = machine.RTC()
# init the real time clock with default time and date
rtc.datetime((int(input('year? ')), int(input('Month? ')), int(input('Day? ')), int(input('Weekday? ')), int(input('Hour? ')), int(input('Minute? ')), int(input('Second? ')), int(input('Microsecond? '))))
# this function gets called every time the alarm is waked up
def alarm_handler (t):
    print(f'Date: {rtc.datetime()[0]}/{rtc.datetime()[1]}/{rtc.datetime()[2]}  {weekdays[rtc.datetime()[3]]}  time: {rtc.datetime()[4]}h/{rtc.datetime()[5]}min/{rtc.datetime()[6]}sec/{rtc.datetime()[7]}microsec')
# init the timer
tim = Timer(-1)
# periodic with 10s period
tim.init(mode=Timer.PERIODIC, period=10000, callback=alarm_handler)


# button interrup implements:
button_presses = 0 # the count of times the button has been pressed
last_time = 0 # the last time we pressed the button
# create a PWM object on a pin and initialise with a frequency of 1, duty of 256
pwm = PWM(Pin(32, Pin.OUT), freq=1, duty_u16=256)
# reconfigure pin #0 in input mode with a pull down resistor
p0 = Pin(15, Pin.IN, Pin.PULL_UP)
# this function gets called every time the button is pressed
def button_pressed_handler(pin):
    global last_time, button_presses
    new_time = time.ticks_ms()
    # if it has been more that 1/5 of a second since the last event, we have a new event
    if (new_time - last_time) > 200:
        if button_presses%2 == 0:
            pwm.init(freq=5, duty_u16=256) # reinitialise with a frequency of 5, duty of 256
        else:
            pwm.init(freq=1, duty_u16=256) # reinitialise with a frequency of 1, duty of 256
        button_presses +=1
        last_time = new_time
# configure an irq callback
p0.irq(handler=button_pressed_handler, trigger=Pin.IRQ_RISING)

# Reference:
# https://www.coderdojotc.org/micropython/advanced-labs/02-interrupt-handlers/
