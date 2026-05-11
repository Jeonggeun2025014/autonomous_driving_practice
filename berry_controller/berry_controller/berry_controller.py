# Copyright 2026 Inhatc
# Authors: Jeonggeun Lim

from geometry_msgs.msg import Twist 
import rclpy
from rclpy.node import Node

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

if __name__ == '__main__':
    main()