import subprocess
import rclpy
from rclpy.node import Node

class GStreamerNode(Node):
    def __init__(self):
        super().__init__('gstreamer_node')

        self.declare_parameter('latency', 80)#ms
        self.latency = self.get_parameter('latency').value

        pipeline = (
            f'gst-launch-1.0 -v '
            f'udpsrc port=5000 caps="application/x-rtp, media=video, encoding-name=H264, payload=96" ! '
            f'rtpjitterbuffer latency={self.latency} drop-on-latency=true ! '
            f'rtph264depay ! h264parse ! '
            f'avdec_h264 max-threads=8 ! '
            f'videoconvert ! gtksink sync=false'
        )

        self.get_logger().info(f"Starting GStreamer pipeline with jitter latency={self.latency} ms")
        self.process = subprocess.Popen(pipeline, shell=True)

    def destroy_node(self):
        self.get_logger().info("Stopping GStreamer pipeline...")
        self.process.terminate()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = GStreamerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
