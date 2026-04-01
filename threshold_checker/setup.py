from setuptools import setup

package_name = 'threshold_checker'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='RodrigoSantosMoreira',
    maintainer_email='moreirarodrigo02@gmail.com',
    description='Pole detector node',
    license='MIT',
    entry_points={
        'console_scripts': [
            'imu_threshold_node = threshold_checker.imu_threshold_node:main'
        ],
    },
)

