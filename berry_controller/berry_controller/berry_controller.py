# # Copyright 2026 Inhatc
# # Authors: Jeonggeun Lim


# Copyright 2026 Inhatc
# Authors: Jeonggeun Lim

import os
import threading
import atexit
import time

from flask import Flask, jsonify, render_template

import RPi.GPIO as gpio

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


# =========================
# Flask 설정
# =========================
# web 폴더 위치를 현재 파일 기준으로 지정
# 폴더 구조 예:
# berry_controller/
# ├── motor/
# │   └── motor_controller.py
# └── web/
#     └── web_controller_10_week_4_direction.html

WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../web"))
app = Flask(__name__, template_folder=WEB_DIR)


# =========================
# GPIO 핀 설정
# =========================
PWM_PIN_DIR = [18, 20, 22, 24]
PWM_PIN_VEL = [19, 21, 23, 25]

PWM_FREQUENCY = 1000
DEFAULT_SPEED = 40

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

for pin in PWM_PIN_DIR:
    gpio.setup(pin, gpio.OUT)

for pin in PWM_PIN_VEL:
    gpio.setup(pin, gpio.OUT)

pwms = []

for pin in PWM_PIN_VEL:
    pwm = gpio.PWM(pin, PWM_FREQUENCY)
    pwm.start(0)
    pwms.append(pwm)


# =========================
# 모터 제어 함수
# =========================
def set_motor(index, direction, speed):
    # 방향 전환 전 잠깐 정지
    pwms[index].ChangeDutyCycle(0)
    time.sleep(0.02)

    gpio.output(PWM_PIN_DIR[index], direction)
    pwms[index].ChangeDutyCycle(speed)


def motor_forward(speed=DEFAULT_SPEED):
    # 왼쪽 모터
    set_motor(0, gpio.HIGH, speed)
    set_motor(2, gpio.HIGH, speed)

    # 오른쪽 모터
    set_motor(1, gpio.LOW, speed)
    set_motor(3, gpio.LOW, speed)


def motor_backward(speed=DEFAULT_SPEED):
    # 왼쪽 모터
    set_motor(0, gpio.LOW, speed)
    set_motor(2, gpio.LOW, speed)

    # 오른쪽 모터
    set_motor(1, gpio.HIGH, speed)
    set_motor(3, gpio.HIGH, speed)


def motor_left(speed=DEFAULT_SPEED):
    # 왼쪽 모터 후진
    set_motor(0, gpio.LOW, speed)
    set_motor(2, gpio.LOW, speed)

    # 오른쪽 모터 전진
    set_motor(1, gpio.LOW, speed)
    set_motor(3, gpio.LOW, speed)


def motor_right(speed=DEFAULT_SPEED):
    # 왼쪽 모터 전진
    set_motor(0, gpio.HIGH, speed)
    set_motor(2, gpio.HIGH, speed)

    # 오른쪽 모터 후진
    set_motor(1, gpio.HIGH, speed)
    set_motor(3, gpio.HIGH, speed)


def motor_stop():
    for pwm in pwms:
        pwm.ChangeDutyCycle(0)


# =========================
# ROS2 Node
# =========================
class BerryController(Node):
    def __init__(self):
        super().__init__("berry_controller")

        self.cmd_vel_publisher = self.create_publisher(Twist, "cmd_vel", 10)

        self.cmd_vel_subscription = self.create_subscription(
            Twist,
            "cmd_vel",
            self.cmd_vel_callback,
            10
        )

        self.get_logger().info("Berry Controller Node Started")

    def publish_cmd_vel(self, linear_x, angular_z):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z

        self.cmd_vel_publisher.publish(msg)

    def cmd_vel_callback(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z

        self.get_logger().info(
            f"cmd_vel received: linear.x={linear_x:.2f}, angular.z={angular_z:.2f}"
        )

        if linear_x > 0.01:
            motor_forward()

        elif linear_x < -0.01:
            motor_backward()

        elif angular_z > 0.01:
            motor_left()

        elif angular_z < -0.01:
            motor_right()

        else:
            motor_stop()


controller_node = None


# =========================
# Flask 라우터
# =========================
@app.route("/")
def index():
    return render_template("web_controller_10_week_4_direction.html")


@app.route("/forward")
def forward():
    controller_node.publish_cmd_vel(0.2, 0.0)
    return jsonify({"status": "forward"})


@app.route("/backward")
def backward():
    controller_node.publish_cmd_vel(-0.2, 0.0)
    return jsonify({"status": "backward"})


@app.route("/left")
def left():
    controller_node.publish_cmd_vel(0.0, 0.5)
    return jsonify({"status": "left"})


@app.route("/right")
def right():
    controller_node.publish_cmd_vel(0.0, -0.5)
    return jsonify({"status": "right"})


@app.route("/stop")
def stop():
    controller_node.publish_cmd_vel(0.0, 0.0)
    return jsonify({"status": "stop"})


# =========================
# Flask 실행 함수
# =========================
def run_flask():
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )


# =========================
# 종료 처리
# =========================
def cleanup():
    motor_stop()

    for pwm in pwms:
        pwm.stop()

    gpio.cleanup()


atexit.register(cleanup)


# =========================
# main
# =========================
def main(args=None):
    global controller_node

    rclpy.init(args=args)

    controller_node = BerryController()

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    try:
        rclpy.spin(controller_node)

    except KeyboardInterrupt:
        pass

    finally:
        controller_node.destroy_node()
        rclpy.shutdown()
        cleanup()


if __name__ == "__main__":
    main()


# from geometry_msgs.msg import Twist 
# import rclpy
# from rclpy.node import Node

# from flask import Flask, jsonify, render_template
# import RPi.GPIO as gpio
# import atexit

# app = Flask(__name__, template_folder="../web")

# PWM_PIN_DIR = [18, 20, 22, 24]
# PWM_PIN_VEL = [19, 21, 23, 25]

# pwm_frequency = 1000
# default_speed = 20

# gpio.setmode(gpio.BCM)

# gpio.setup(PWM_PIN_DIR[0], gpio.OUT)
# gpio.setup(PWM_PIN_DIR[1], gpio.OUT)
# gpio.setup(PWM_PIN_DIR[2], gpio.OUT)
# gpio.setup(PWM_PIN_DIR[3], gpio.OUT)

# gpio.setup(PWM_PIN_VEL[0], gpio.OUT)
# gpio.setup(PWM_PIN_VEL[1], gpio.OUT)
# gpio.setup(PWM_PIN_VEL[2], gpio.OUT)
# gpio.setup(PWM_PIN_VEL[3], gpio.OUT)

# pwms = [0, 0, 0, 0]
# pwms[0] = gpio.setup(PWM_PIN_VEL[0], gpio.OUT)
# pwms[1] = gpio.setup(PWM_PIN_VEL[1], gpio.OUT)
# pwms[2] = gpio.setup(PWM_PIN_VEL[2], gpio.OUT)
# pwms[3] = gpio.setup(PWM_PIN_VEL[3], gpio.OUT)

# pwms[0] = gpio.PWM(PWM_PIN_VEL[0], pwm_frequency)
# pwms[1] = gpio.PWM(PWM_PIN_VEL[1], pwm_frequency)
# pwms[2] = gpio.PWM(PWM_PIN_VEL[2], pwm_frequency)
# pwms[3] = gpio.PWM(PWM_PIN_VEL[3], pwm_frequency)

# pwms[0].start(0)
# pwms[1].start(0)
# pwms[2].start(0)
# pwms[3].start(0)

# class BerryController(Node):
#     def __init__(self):
#         super().__init__('robowell_korea_agv_controller')
#         self.init_parameters()
#         self.init_publishers()
#         self.timer_ = self.create_timer(self.control_period, self.controller_timer)

#     def init_parameters(self):
#         self.declare_parameter('control.control_period', 0.5)
#         self.control_period = self.get_parameter('control.control_period').value

#     def init_publishers(self):
#         self.cmd_vel_publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)

#     def controller_timer(self):
#         msg = Twist()
#         msg.linear.x = 0.2
#         msg.angular.z = 0.1
#         self.cmd_vel_publisher_.publish(msg)

#     def motor_forward(speed=default_speed):
#         # left
#         gpio.output(PWM_PIN_DIR[0], gpio.HIGH)
#         gpio.output(PWM_PIN_DIR[2], gpio.HIGH)
#         pwms[0].start(speed)
#         pwms[2].start(speed)

#         # right
#         gpio.output(PWM_PIN_DIR[1], gpio.LOW)
#         gpio.output(PWM_PIN_DIR[3], gpio.LOW)
#         pwms[1].start(speed)
#         pwms[3].start(speed)

#     def motor_backward(speed=default_speed):
#         # left
#         gpio.output(PWM_PIN_DIR[0], gpio.LOW)
#         gpio.output(PWM_PIN_DIR[2], gpio.LOW)
#         pwms[0].start(speed)
#         pwms[2].start(speed)

#         # right
#         gpio.output(PWM_PIN_DIR[1], gpio.HIGH)
#         gpio.output(PWM_PIN_DIR[3], gpio.HIGH)
#         pwms[1].start(speed)
#         pwms[3].start(speed)

#     def motor_left(speed=default_speed):
#         # left
#         gpio.output(PWM_PIN_DIR[0], gpio.LOW)
#         gpio.output(PWM_PIN_DIR[2], gpio.LOW)
#         pwms[0].start(speed)
#         pwms[2].start(speed)

#         # right
#         gpio.output(PWM_PIN_DIR[1], gpio.LOW)
#         gpio.output(PWM_PIN_DIR[3], gpio.LOW)
#         pwms[1].start(speed)
#         pwms[3].start(speed)

#     def motor_right(speed=default_speed):
#         # left
#         gpio.output(PWM_PIN_DIR[0], gpio.HIGH)
#         gpio.output(PWM_PIN_DIR[2], gpio.HIGH)
#         pwms[0].start(speed)
#         pwms[2].start(speed)

#         # right
#         gpio.output(PWM_PIN_DIR[1], gpio.HIGH)
#         gpio.output(PWM_PIN_DIR[3], gpio.HIGH)
#         pwms[1].start(speed)
#         pwms[3].start(speed)

#     def motor_stop():
#         speed = 0
#         # left
#         gpio.output(PWM_PIN_DIR[0], gpio.HIGH)
#         gpio.output(PWM_PIN_DIR[2], gpio.HIGH)
#         pwms[0].start(speed)
#         pwms[2].start(speed)

#         # right
#         gpio.output(PWM_PIN_DIR[1], gpio.LOW)
#         gpio.output(PWM_PIN_DIR[3], gpio.LOW)
#         pwms[1].start(speed)
#         pwms[3].start(speed)


# def main(args=None):
#     rclpy.init(args=args)

#     berry_controller = BerryController()

#     try:
#         rclpy.spin(berry_controller)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         berry_controller.destroy_node()
#         rclpy.shutdown()


# @app.route("/")
# def index():
#     return render_template("web_controller_10_week_4_direction.html")

# @app.route("/forward")
# def forward():
#     motor_forward()
#     return jsonify({"status": "forward"})

# @app.route("/backward")
# def backward():
#     motor_backward()
#     return jsonify({"status": "backward"})

# @app.route("/left")
# def left():
#     motor_left()
#     return jsonify({"status": "left"})

# @app.route("/right")
# def right():
#     motor_right()
#     return jsonify({"status": "backward"})

# @app.route("/stop")
# def stop():
#     motor_stop()
#     return jsonify({"status": "stop"})

# def cleanup():
#     motor_stop()
#     pwm.stop()
#     gpio.cleanup()

# atexit.register(cleanup)

# if __name__ == '__main__':
#     main()

# # sudo usermod -aG gpio auto
# # sudo chown root:root /dev/gpiomem
# # sudo chmod 666 /dev/gpiomem