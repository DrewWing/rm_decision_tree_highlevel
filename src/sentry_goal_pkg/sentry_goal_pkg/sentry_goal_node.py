#!/usr/bin/env python3
# Vibe coded bc unfortunately I don't have time for this

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

from std_msgs.msg import Int32



class GoalNode(Node):
    def __init__(self):
        super().__init__('goal_node')

        self._action_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

        self.health = None
        self.health_subscription = self.create_subscription(
            Int32,
            '/health',
            self.health_callback,
            10
        )

        self.get_logger().info('Waiting for Nav2 action server...')
        self._action_client.wait_for_server()

        self.send_goal()


    def health_callback(self, msg):
        self.health = msg.data
        self.get_logger().info(
            f'Received health: {self.health}'
        )

        # if self.health >= 80:
        #     self.set_destination('normal')
        # elif self.health >= 40:
        #     self.set_destination('safe')
        # else:
        #     self.set_destination('emergency')

    def send_goal(self):
        goal = NavigateToPose.Goal()

        # Goal position in the map frame
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        goal.pose.pose.position.x = 2.0
        goal.pose.pose.position.y = 1.0
        goal.pose.pose.position.z = 0.0

        # Orientation: yaw = 0 radians
        goal.pose.pose.orientation.x = 0.0
        goal.pose.pose.orientation.y = 0.0
        goal.pose.pose.orientation.z = 0.0
        goal.pose.pose.orientation.w = 1.0

        self.get_logger().info('Sending navigation goal...')

        future = self._action_client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        distance = feedback_msg.feedback.distance_remaining
        self.get_logger().info(
            f'Distance remaining: {distance:.2f} m'
        )

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by Nav2')
            return

        self.get_logger().info('Goal accepted!')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result()

        if result.status == 4:  # STATUS_ABORTED
            self.get_logger().error('Navigation aborted')
        elif result.status == 5:  # STATUS_CANCELED
            self.get_logger().warning('Navigation canceled')
        else:
            self.get_logger().info(
                f'Navigation finished with status: {result.status}'
            )

        rclpy.shutdown()


def main(args=None):
    print("[sentry_goal_node] MAIN started!")
    rclpy.init(args=args)
    node = GoalNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()