import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

class JoyToTwist(Node):
    def __init__(self):
        super().__init__('joy_to_twist')

        # Subscribe to joystick buttons
        self.subscription = self.create_subscription(Joy,'joy',self.joy_callback,10)

        # Publisher for Twist
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)

        # Button indices
        self.button_z = 4     # Button for z 
        self.button_z_inverse = 6   # Button 2

        #axes
        self.axis_forward = 1
        self.axis_sideways = 0

        self.get_logger().info("Controller interpreter turned on")

    def joy_callback(self, msg: Joy):
        twist = Twist()

        if msg.buttons[self.button_z] == 1:
            twist.linear.z = 1.0
        elif msg.buttons[self.button_z_inverse] == 1:
            twist.linear.z = -1.0
        else:
            twist.linear.z = 0.0

        twist.linear.x=msg.axes[self.axis_forward]
        twist.angular.z=msg.axes[self.axis_sideways]


        self.pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = JoyToTwist()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
