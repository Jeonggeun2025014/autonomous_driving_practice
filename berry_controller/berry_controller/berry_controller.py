# Copyright 2026 Inhatc
# Authors: Jeonggeun Lim

from geometry_msgs.msg import Twist 
import rclpy
from rclpy.node import Node

from flask import Flask, jsonify, render_template
import RPi.GPIO as gpio
import atexit

app = Flask(__name__, template_folder="../web")

PWM_PIN_DIR = [18, 20, 22, 24]
PWM_PIN_VEL = [19, 21, 23, 25]

pwm_frequency = 1000
default_speed = 20

gpio.setmode(gpio.BCM)

gpio.setup(PWM_PIN_DIR[0], gpio.OUT)
gpio.setup(PWM_PIN_DIR[1], gpio.OUT)
gpio.setup(PWM_PIN_DIR[2], gpio.OUT)
gpio.setup(PWM_PIN_DIR[3], gpio.OUT)

gpio.setup(PWM_PIN_VEL[0], gpio.OUT)
gpio.setup(PWM_PIN_VEL[1], gpio.OUT)
gpio.setup(PWM_PIN_VEL[2], gpio.OUT)
gpio.setup(PWM_PIN_VEL[3], gpio.OUT)

pwms = [0, 0, 0, 0]
pwms[0] = gpio.setup(PWM_PIN_VEL[0], gpio.OUT)
pwms[1] = gpio.setup(PWM_PIN_VEL[1], gpio.OUT)
pwms[2] = gpio.setup(PWM_PIN_VEL[2], gpio.OUT)
pwms[3] = gpio.setup(PWM_PIN_VEL[3], gpio.OUT)

pwms[0] = gpio.PWM(PWM_PIN_VEL[0], pwm_frequency)
pwms[1] = gpio.PWM(PWM_PIN_VEL[1], pwm_frequency)
pwms[2] = gpio.PWM(PWM_PIN_VEL[2], pwm_frequency)
pwms[3] = gpio.PWM(PWM_PIN_VEL[3], pwm_frequency)

pwms[0].start(0)
pwms[1].start(0)
pwms[2].start(0)
pwms[3].start(0)

class BerryController(Node):
    def __init__(self):
        super().__init__('robowell_korea_agv_controller')
        self.init_parameters()
        self.init_publishers()
        self.timer_ = self.create_timer(self.control_period, self.controller_timer)

    def init_parameters(self):
        self.declare_parameter('control.control_period', 0.5)
        self.control_period = self.get_parameter('control.control_period').value

    def init_publishers(self):
        self.cmd_vel_publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)

    def controller_timer(self):
        msg = Twist()
        msg.linear.x = 0.2
        msg.angular.z = 0.1
        self.cmd_vel_publisher_.publish(msg)

    def motor_forward(speed=default_speed):
        # left
        gpio.output(PWM_PIN_DIR[0], gpio.HIGH)
        gpio.output(PWM_PIN_DIR[2], gpio.HIGH)
        pwms[0].start(speed)
        pwms[2].start(speed)

        # right
        gpio.output(PWM_PIN_DIR[1], gpio.LOW)
        gpio.output(PWM_PIN_DIR[3], gpio.LOW)
        pwms[1].start(speed)
        pwms[3].start(speed)

    def motor_backward(speed=default_speed):
        # left
        gpio.output(PWM_PIN_DIR[0], gpio.LOW)
        gpio.output(PWM_PIN_DIR[2], gpio.LOW)
        pwms[0].start(speed)
        pwms[2].start(speed)

        # right
        gpio.output(PWM_PIN_DIR[1], gpio.HIGH)
        gpio.output(PWM_PIN_DIR[3], gpio.HIGH)
        pwms[1].start(speed)
        pwms[3].start(speed)

    def motor_left(speed=default_speed):
        # left
        gpio.output(PWM_PIN_DIR[0], gpio.LOW)
        gpio.output(PWM_PIN_DIR[2], gpio.LOW)
        pwms[0].start(speed)
        pwms[2].start(speed)

        # right
        gpio.output(PWM_PIN_DIR[1], gpio.LOW)
        gpio.output(PWM_PIN_DIR[3], gpio.LOW)
        pwms[1].start(speed)
        pwms[3].start(speed)

    def motor_right(speed=default_speed):
        # left
        gpio.output(PWM_PIN_DIR[0], gpio.HIGH)
        gpio.output(PWM_PIN_DIR[2], gpio.HIGH)
        pwms[0].start(speed)
        pwms[2].start(speed)

        # right
        gpio.output(PWM_PIN_DIR[1], gpio.HIGH)
        gpio.output(PWM_PIN_DIR[3], gpio.HIGH)
        pwms[1].start(speed)
        pwms[3].start(speed)

    def motor_stop():
        speed = 0
        # left
        gpio.output(PWM_PIN_DIR[0], gpio.HIGH)
        gpio.output(PWM_PIN_DIR[2], gpio.HIGH)
        pwms[0].start(speed)
        pwms[2].start(speed)

        # right
        gpio.output(PWM_PIN_DIR[1], gpio.LOW)
        gpio.output(PWM_PIN_DIR[3], gpio.LOW)
        pwms[1].start(speed)
        pwms[3].start(speed)


def main(args=None):
    rclpy.init(args=args)

    berry_controller = BerryController()

    try:
        rclpy.spin(berry_controller)
    except KeyboardInterrupt:
        pass
    finally:
        berry_controller.destroy_node()
        rclpy.shutdown()


 @app.route("/")
def index():
    return render_template("web_controller_10_week_4_direction.html")

@app.route("/forward")
def forward():
    motor_forward()
    return jsonify({"status": "forward"})

@app.route("/backward")
def backward():
    motor_backward()
    return jsonify({"status": "backward"})

@app.route("/left")
def left():
    motor_left()
    return jsonify({"status": "left"})

@app.route("/right")
def right():
    motor_right()
    return jsonify({"status": "backward"})

@app.route("/stop")
def stop():
    motor_stop()
    return jsonify({"status": "stop"})

def cleanup():
    motor_stop()
    pwm.stop()
    gpio.cleanup()

atexit.register(cleanup)

if __name__ == '__main__':
    main()