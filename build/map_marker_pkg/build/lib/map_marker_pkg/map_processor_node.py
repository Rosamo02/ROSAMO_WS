import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from tf2_ros import TransformListener, Buffer
import numpy as np

class MapProcessor(Node):
    def __init__(self):
        super().__init__('map_processor')
        
        # Subscribe to the original map
        self.subscription = self.create_subscription(
            OccupancyGrid, '/map', self.map_callback, 10)
        
        # Publisher for the modified map
        self.publisher = self.create_publisher(
            OccupancyGrid, '/map_processed', 10)
        
        # TF setup for your specific frames
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def map_callback(self, msg):
        # Create a copy of the map to modify
        processed_map = msg
        
        # Convert the tuple data to a mutable numpy array for editing
        grid_data = np.array(msg.data).reshape((msg.info.height, msg.info.width))

        # Frames to mark on the map
        # Using 100 (Occupied) so it shows up clearly as a "wall/point"
        targets = {
            'base_link_ekf': 100, 
            'livox_frame': 100
        }

        for frame, value in targets.items():
            try:
                # Get transform from map to the target frame
                t = self.tf_buffer.lookup_transform('map', frame, rclpy.time.Time())
                
                # Extract coordinates in meters
                x = t.transform.translation.x
                y = t.transform.translation.y

                # Convert meters to pixel indices
                # Index = (Position - Origin) / Resolution
                px = int((x - msg.info.origin.position.x) / msg.info.info.resolution)
                py = int((y - msg.info.origin.position.y) / msg.info.info.resolution)

                # Draw a small 3x3 square so it's visible on the HMI
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= px+i < msg.info.width and 0 <= py+j < msg.info.height:
                            grid_data[py+j, px+i] = value

            except Exception as e:
                # Log warning if TF fails (common at startup)
                self.get_logger().debug(f"Could not find {frame}: {str(e)}")

        # Flatten back to list and publish
        processed_map.data = grid_data.flatten().tolist()
        self.publisher.publish(processed_map)

def main(args=None):
    rclpy.init(args=args)
    node = MapProcessor()
    rclpy.spin(node)
    rclpy.shutdown()