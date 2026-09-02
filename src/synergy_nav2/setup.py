import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'synergy_nav2'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='synergy',
    maintainer_email='synergy@todo.todo',
    description='Nav2 launch and configuration for AMR A',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'dynamic_lidar_tf = synergy_nav2.dynamic_lidar_tf:main',
        ],
    },
)
