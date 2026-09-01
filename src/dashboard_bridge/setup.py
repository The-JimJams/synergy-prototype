from setuptools import find_packages, setup

package_name = 'dashboard_bridge'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aditi',
    maintainer_email='aditi@todo.todo',
    description='Dashboard bridge node package.',
    license='Apache-2.0',
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'dashboard_bridge_node = dashboard_bridge.dashboard_bridge_node:main',
        ],
    },
)
