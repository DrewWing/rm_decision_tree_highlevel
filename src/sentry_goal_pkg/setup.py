from setuptools import find_packages, setup

package_name = 'sentry_goal_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='DrewWing',
    maintainer_email='89153952+DrewWing@users.noreply.github.com',
    description='Goal-setting node for Nav2',
    # license='TODO: License declaration',
    # extras_require={
        # 'test': [
            # 'pytest',
        # ],
    # },
    entry_points={
        'console_scripts': [
            'sentry_goal_node = sentry_goal_pkg.sentry_goal_node:main'
        ],
    },
)
