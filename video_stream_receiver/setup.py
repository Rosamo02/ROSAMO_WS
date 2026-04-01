from setuptools import setup

package_name = 'video_stream_receiver'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='RodrigoMoreira',
    maintainer_email='moreirarodrigo02@gmail.com',
    description='GStreamer video receiver node',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'video_stream_receiver = video_stream_receiver.video_stream_receiver:main',
        ],
    },
)
