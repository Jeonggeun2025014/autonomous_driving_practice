# # Copyright 2026 Inhatc
# # Authors: Jeonggeun Lim

import os
import threading
import atexit
import time

from flask import Flask, jsonify, render_template

import RPi.GPIO as gpio

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


# Flask 설정

# html 폴더 위치를 현재 파일 기준으로 지정
# 폴더 구조 예:
# berry_controller/
# ├── berry_controller.py
# └── html/
#     └── web_controller_10_week_4_direction.html

WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../berry_controller/html"))
app = Flask(__name__, template_folder=WEB_DIR)


# GPIO 핀 설정
PWM_PIN_DIR = [18, 20, 22, 24]
PWM_PIN_VEL = [19, 21, 23, 25]

PWM_FREQUENCY = 1000
DEFAULT_SPEED = 40

LEFT_WHEEL_FORWARD = gpio.HIGH
LEFT_WHEEL_BACKWARD = gpio.LOW
RIGHT_WHEEL_FORWARD = gpio.LOW
RIGHT_WHEEL_BACKWARD = gpio.HIGH

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

# 모터 제어 함수
def set_motor(index, direction, speed):
    # 방향 전환 전 잠깐 정지
    pwms[index].ChangeDutyCycle(0)
    time.sleep(0.02)

    gpio.output(PWM_PIN_DIR[index], direction)
    pwms[index].ChangeDutyCycle(speed)

def left_wheels(direction, speed):
    set_motor(0, direction, speed)
    set_motor(2, direction, speed)
    
def right_wheels(direction, speed):
    set_motor(1, direction, speed)
    set_motor(3, direction, speed)
    

def motor_forward(speed=DEFAULT_SPEED):
    left_wheels(LEFT_WHEEL_FORWARD, speed)
    right_wheels(RIGHT_WHEEL_FORWARD, speed)

def motor_backward(speed=DEFAULT_SPEED):
    left_wheels(LEFT_WHEEL_BACKWARD, speed)
    right_wheels(RIGHT_WHEEL_BACKWARD, speed)

def motor_left(speed=DEFAULT_SPEED):
    left_wheels(LEFT_WHEEL_BACKWARD, speed)
    right_wheels(RIGHT_WHEEL_FORWARD, speed)

def motor_right(speed=DEFAULT_SPEED):
    left_wheels(LEFT_WHEEL_FORWARD, speed)
    right_wheels(RIGHT_WHEEL_BACKWARD, speed)

def motor_stop():
    for pwm in pwms:
        pwm.ChangeDutyCycle(0)

# ROS2 Node
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

        self.lidar_subscription = self.create_subscription(
            LaserScan,
            "scan",
            self.scan_callback,
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

    def scan_callback(self, msg):
        range_count = len(msg.ranges)

        # 정면 방향 거리값
        front_index = range_count // 2
        front_distance = msg.ranges[front_index]

        self.get_logger().info(
            f"LiDAR received | data count: {range_count}, front distance: {front_distance:.2f} m"
        )

controller_node = None

# Flask 라우터
@app.route("/")
def index():
    print(WEB_DIR)
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

# Flask 실행 함수
def run_flask():
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )

# 종료 처리
def cleanup():
    motor_stop()
    for pwm in pwms:
        pwm.stop()
    gpio.cleanup()

atexit.register(cleanup)

# main
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

# sudo usermod -aG gpio auto
# sudo chown root:root /dev/gpiomem
# sudo chmod 666 /dev/gpiomem