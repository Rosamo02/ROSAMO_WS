import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import Int32
from math import sqrt

class ImuThresholdNode(Node):
    def __init__(self):
        super().__init__('imu_threshold_node')

        # Thresholds
        self.l_acc_threshold = 2.0
        self.h_acc_threshold = 5.0
        self.gyro_threshold = 1.0

        # counters
        self.count_1 = 0
        self.count_2 = 0

        # cooldown timers
        self.cooldown = 3.0
        self.last_hit_time_1 = 0.0
        self.last_hit_time_2 = 0.0

        # Publishers
        self.pub_count_1 = self.create_publisher(Int32, '/tree_1/hit_count', 10)
        self.pub_count_2 = self.create_publisher(Int32, '/tree_2/hit_count', 10)
        self.pub_mag = self.create_publisher(Int32, '/hit_magnitude', 10)

        # Subscriptions
        self.create_subscription(Imu, '/tree_1/imu', lambda msg: self.process_imu(msg, 1), 10)
        self.create_subscription(Imu, '/tree_2/imu', lambda msg: self.process_imu(msg, 2), 10)

        self.get_logger().info("Subscribed to /tree_1/imu and /tree_2/imu")

    def process_imu(self, msg: Imu, sensor_id: int):

        # IMU values
        ax = msg.linear_acceleration.x
        ay = msg.linear_acceleration.y
        az = msg.linear_acceleration.z

        gx = msg.angular_velocity.x
        gy = msg.angular_velocity.y
        gz = msg.angular_velocity.z

        # Magnitudes
        total_acc = sqrt(ax**2 + az**2) #dont consider y as that is the gravitational acceleration
        total_gyro = sqrt(gx**2 + gy**2 + gz**2)

        # Current time
        now = self.get_clock().now().nanoseconds / 1e9

        # Select correct cooldown timer
        last_hit = self.last_hit_time_1 if sensor_id == 1 else self.last_hit_time_2

        # Cooldown check
        if now - last_hit < self.cooldown:
            return

        hit = False

        if total_acc > self.l_acc_threshold:
            self.get_logger().warn(f'tree_{sensor_id}: Acc threshold exceeded |a|={total_acc:.2f}')
            hit = True

            self.Hmag = (total_acc - self.l_acc_threshold) / (self.h_acc_threshold - self.l_acc_threshold)

            if self.Hmag > 1.0:
                self.Hmag = 1.0

            # Publish magnitude
            msg_mag = Int32()
            msg_mag.data = int(self.Hmag * 100)
            self.pub_mag.publish(msg_mag)

        # Gyro threshold
        if total_gyro > self.gyro_threshold:
            self.get_logger().warn(f'tree_{sensor_id}: Gyro threshold exceeded |ω|={total_gyro:.2f}')
            hit = True

        # COUNTER UPDATE
        if hit:
            msg_out = Int32()

            if sensor_id == 1:
                self.count_1 += 1
                self.last_hit_time_1 = now
                msg_out.data = self.count_1
                self.pub_count_1.publish(msg_out)
                self.get_logger().info(f"tree_1 hit! Total hits: {self.count_1}")

            else:
                self.count_2 += 1
                self.last_hit_time_2 = now
                msg_out.data = self.count_2
                self.pub_count_2.publish(msg_out)
                self.get_logger().info(f"tree_2 hit! Total hits: {self.count_2}")

def main(args=None):
    rclpy.init(args=args)
    node = ImuThresholdNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
