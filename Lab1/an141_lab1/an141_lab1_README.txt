I used ESP32 and a pull-up button to control the system's interrupt. Meanwhile, an RTC timer refreshed every 10 seconds to print the date.
Pin 15 was connected using a pull-up configuration: https://learn.sparkfun.com/tutorials/pull-up-resistors/all
Pin for PWM: 32


# Reference:
# https://www.coderdojotc.org/micropython/advanced-labs/02-interrupt-handlers/