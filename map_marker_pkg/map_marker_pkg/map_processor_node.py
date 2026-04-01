import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from tf2_ros import TransformListener, Buffer
import numpy as np

class MapProcessor(Node):
    def __init__(self):
        super().__init__('map_processor')
        
        # Subscribe to the raw map from slam_toolbox
        self.subscription = self.create_subscription(
            OccupancyGrid, '/map', self.map_callback, 10)
        
        # Publish the new map for your HMI
        self.publisher = self.create_publisher(
            OccupancyGrid, '/map_processed', 10)
        
        # TF Buffer and Listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        self.get_logger().info("Map Processor Node Started. Listening to /map...")

    def map_callback(self, msg):
        # 1. Convert the constant data to a mutable numpy array
        # We reshape it to (height, width) to make 2D drawing easier
        grid_data = np.array(msg.data, dtype=np.int8).reshape((msg.info.height, msg.info.width))

        # 2. Define the frames from your TF tree to draw
        # Format: 'frame_name': (occupancy_value, pixel_size)
        markers = {
            'base_link_ekf': (100, 6),  # Robot: Black, 6x6 pixels
            'livox_frame': (75, 4)      # LiDAR: Dark Gray, 4x4 pixels
        }

        res = msg.info.resolution
        origin_x = msg.info.origin.position.x
        origin_y = msg.info.origin.position.y

        for frame, (value, size) in markers.items():
            try:
                # CRITICAL: We use rclpy.time.Time() [Time Zero] 
                # This grabs the LATEST transform available to avoid TF_OLD_DATA errors.
                t = self.tf_buffer.lookup_transform(
                    'map', 
                    frame, 
                    rclpy.time.Time())
                
                # World coordinates (meters) -> Pixel coordinates
                px = int((t.transform.translation.x - origin_x) / res)
                py = int((t.transform.translation.y - origin_y) / res)

                # Draw the square marker
                half = size // 2
                for i in range(-half, half):
                    for j in range(-half, half):
                        # Stay within map boundaries
                        if 0 <= px + i < msg.info.width and 0 <= py + j < msg.info.height:
                            grid_data[py + j, px + i] = value

            except Exception:
                # Skip if transform isn't available yet
                continue

        # 3. Create the output message
        processed_msg = msg
        processed_msg.data = grid_data.flatten().tolist()
        
        # Publish to /map_processed
        self.publisher.publish(processed_msg)

def main(args=None):
    rclpy.init(args=args)
    node = MapProcessor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()