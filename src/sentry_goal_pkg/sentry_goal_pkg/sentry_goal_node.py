#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

from std_msgs.msg import Int32


# x pos, y pos, z pos, rot_x, rot_y, rot_z, rot_w
CENTER:tuple[float,float,float,float,float,float,float] = ( 2.0, 0.5, 0.0, 0.0, 0.0, 0.0, 1.0)
HOME:  tuple[float,float,float,float,float,float,float] = (-2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)

class State:
    # Pose is x, y, z, rot_x, rot_y, rot_z, rot_w
    def __init__(self, 
                 name:str, 
                 hasPose: bool, 
                 pose: tuple[float,float,float,float,float,float,float] = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)
                 ):
        self.name: str = name
        self.hasPose: bool = hasPose
        self.pose: tuple[float,float,float,float,float,float,float] = pose

    def __repr__(self) -> str:
        return self.name


CENTER_STATE = State("Center State", hasPose=True, pose=CENTER)
HOME_STATE = State("Home State", hasPose=True, pose=HOME)


class GoalNode(Node):
    def __init__(self,
                 lowHealthState: State = HOME_STATE,
                 highHealthState:State = CENTER_STATE,
                 lowHealthTrigger: int = 25, 
                 highHealthTrigger:int = 100
                 ):
        super().__init__('goal_node')

        # Nav2 stuff
        self._action_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

        # Health and state stuff
        self.health = 50
        self.lowHealthTrigger: int = lowHealthTrigger
        self.highHealthTrigger:int = highHealthTrigger
        self.lowHealthState: State = lowHealthState
        self.highHealthState:State = highHealthState

        self.state: State = highHealthState

        self.health_subscription = self.create_subscription(
            Int32,
            '/health',
            self.health_callback,
            10
        )

        # Doing stuff
        self.get_logger().info('Waiting for Nav2 action server...')
        self._action_client.wait_for_server()
        self.get_logger().info('Nav2 server setup and ready.')

        self.send_goal()


    def updateState(self):
        if self.state == self.lowHealthState and self.health >= self.highHealthTrigger:
            self.state = self.highHealthState
            self.get_logger().info(f"Changing state to {self.state}")
            self.send_goal()
        
        elif self.state == self.highHealthState and self.health <= self.lowHealthTrigger:
            self.state = self.lowHealthState
            self.get_logger().info(f"Changing state to {self.state}")
            self.send_goal()
                    


    def health_callback(self, msg):
        self.health = msg.data
        self.get_logger().info(
            f'Received health: {self.health}'
        )
        # self.get_logger().info(f"Current state {self.state}  self.health={self.health} (type {type(self.health)})")
        # self.get_logger().info(f"self.lowhealthstate={self.lowHealthState} self.lowhealthtrigger={self.lowHealthTrigger}")
        # self.get_logger().info(f"self.highhealthstate={self.highHealthState} self.highealthtrigger={self.highHealthTrigger}")
        # self.get_logger().info(f"self.state == self.lowHealthState {self.state == self.lowHealthState}  self.health >= self.highHealthTrigger {self.health >= self.highHealthTrigger}")
        
        self.updateState()


    def send_goal(self):
        goal = NavigateToPose.Goal()

        # Goal position in the map frame
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        (   goal.pose.pose.position.x, 
            goal.pose.pose.position.y, 
            goal.pose.pose.position.z,
            goal.pose.pose.orientation.x,
            goal.pose.pose.orientation.y,
            goal.pose.pose.orientation.z,
            goal.pose.pose.orientation.w
            ) = self.state.pose

        # Orientation: yaw = 0 radians

        self.get_logger().info('Sending navigation goal...')

        future = self._action_client.send_goal_async(
            goal#,
            # feedback_callback=self.feedback_callback
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
            rclpy.shutdown()
        else:
            self.get_logger().info(
                f'Navigation finished with status: {result.status}'
            )



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