import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/rodrigomoreira/ros2_ws/src/install/pole_detector'
