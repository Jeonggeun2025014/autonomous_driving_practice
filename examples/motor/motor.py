import RPi.GPIO as gpio
import time

PWM_PIN_DIR = {18, 20, 22, 24}
PWM_PIN_VEL = {19, 21, 23, 25}
pwm = [0, 0, 0, 0]

pwm_frequency = 1000

gpio.setmode(gpio.BCM)

for pin in range(len(PWM_PIN_DIR)):
    gpio.setup(PWM_PIN_DIR[pin], gpio.OUT)
    gpio.PWM(PWM_PIN_DIR[pin], gpio.HIGH)
    pwm[pin] = gpio.setup(PWM_PIN_VEL[pin], gpio.OUT)
    pwm[pin] = gpio.PWM(PWM_PIN_VEL[pin], pwm_frequency)

pwm[0].start(10)
pwm[1].start(10)
pwm[2].start(10)
pwm[3].start(10)

try:
    while True:
        pass
except KeyboardInterrupt:
    for each_pwm in pwm:
        each_pwm.stop()
    gpio.cleanup()
