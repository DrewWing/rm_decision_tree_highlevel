#!/usr/bin/env python3

# Health publisher
# publishes the health of the robot for the goal node to subscribe to

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class HealthPublisher(Node):
    def __init__(self):
        super().__init__('health_publisher')
        # self.get_logger().info("[health_publisher] HealthPublisher init called.")
        print("[health_publisher] HealthPublisher init called") # TODO: change to actual logger


        self.publisher = self.create_publisher(
            Int32,
            '/health',
            10
        )

        # self.timer = self.create_timer(1.0, self.publish_health) # only publishing health when changed or on init.
        self.health = 100

        self.input_loop()

    def publish_health(self):
        msg = Int32()
        msg.data = self.health
        self.publisher.publish(msg)

        self.get_logger().info(f'Published health: {msg.data}')

    def input_loop(self):
        # Loops an input to get the health
        while True:
                try:
                    self.health = int(input("New health (int): "))
                    self.publish_health()

                except ValueError:
                    print("Invalid health input! To exit, use Ctrl+C")

                except KeyboardInterrupt:
                    break

        self.get_logger().info("[health_publisher] input loop broken.")


def main(args=None):
    rclpy.init(args=args)
    node = HealthPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except rclpy._rclpy_pybind11.RCLError as e:
        # This error is usual when shutting down
        if not('failed to create guard_condition: the given context is not valid, either rcl_init() was not called or rcl_shutdown() was called.' in e.__repr__()):
            raise e
    finally:
        node.destroy_node()
        try:
            rclpy.shutdown()

        except rclpy._rclpy_pybind11.RCLError as e:
                # This error is usual when shutting down
                if not('failed to shutdown: rcl_shutdown already called on the given context' in e.__repr__()):
                    raise e


if __name__ == '__main__':
    main()