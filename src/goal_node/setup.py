import os
from glob import glob
from setuptools import setup

package_name = 'goal_node'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        # Install marker file in the package index
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        # Include our package.xml file
        (os.path.join('share', package_name), ['package.xml']),
        # Include all launch files.
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.launch.py'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='github.com/DrewWing',
    maintainer_email='89153952+DrewWing@users.noreply.github.com',
    description='Goal-setting node for Nav2',
    entry_points={
        'console_scripts': [
            'goal-node = goal_node.goal_node:main',
        ],
    },
)