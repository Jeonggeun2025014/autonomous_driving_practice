import os
os.environ["GPIOZERO_PIN_FACTORY"] = "rpgpio"

from gpiozero import LED
import time

user_led = LED(16)

for i in range(1, 10):
    user_led.on()
    time.sleep(1)
    user_led.off()
    time.sleep(1)