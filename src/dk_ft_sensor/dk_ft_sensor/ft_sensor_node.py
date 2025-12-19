#!/usr/bin/env python3
"""
FT Sensor Node

Simplified standalone force/torque sensor node for DUCO robot.
Listens to UDP data and publishes force/torque sensor data.

The node:
1. Listens for UDP packets (configurable host/port)
2. Extracts FTSensorData from the UDP messages
3. Publishes force/torque data in WrenchStamped format

Parameters:
- host: UDP host address (default: "0.0.0.0")
- port: UDP port number (default: 5566)
- topic_name: Output topic name (default: "ft_sensor_raw")
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import WrenchStamped
import socket
import json
import threading


class FTSensorNode(Node):
    def __init__(self):
        super().__init__('ft_sensor_node')
        
        # Declare parameters
        self.declare_parameter('host', '0.0.0.0')
        self.declare_parameter('port', 5566)
        self.declare_parameter('topic_name', 'ft_sensor_raw')
        
        # Get parameter values
        self.host = self.get_parameter('host').get_parameter_value().string_value
        self.port_data = self.get_parameter('port').get_parameter_value().integer_value
        self.topic_name = self.get_parameter('topic_name').get_parameter_value().string_value
        
        # Create publisher for force/torque data
        self.ft_sensor_publisher = self.create_publisher(
            WrenchStamped, self.topic_name, 10)
        
        # Start UDP receiver
        self.start_udp_receiver()
        
        self.get_logger().info('FT Sensor Node started')
        self.get_logger().info(f'Listening on {self.host}:{self.port_data} for sensor data')
        self.get_logger().info(f'Publishing to /{self.topic_name} topic')
    
    def start_udp_receiver(self):
        """Start UDP receiver thread"""
        data_thread = threading.Thread(
            target=self.udp_data_receiver, 
            daemon=True, 
            name="ft_data_receiver"
        )
        data_thread.start()
    
    def create_sensor_wrench_msg(self, ft_data):
        """Create WrenchStamped message from 6D FT sensor data"""
        msg = WrenchStamped()
        
        # Set timestamp
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "ft_sensor_frame"
        
        # FTSensorData is 6D: [Fx, Fy, Fz, Tx, Ty, Tz]
        if len(ft_data) >= 6:
            msg.wrench.force.x = float(ft_data[0])
            msg.wrench.force.y = float(ft_data[1])
            msg.wrench.force.z = float(ft_data[2])
            msg.wrench.torque.x = float(ft_data[3])
            msg.wrench.torque.y = float(ft_data[4])
            msg.wrench.torque.z = float(ft_data[5])
        else:
            self.get_logger().warning(
                f'FTSensorData has insufficient elements: {len(ft_data)}, expected 6')
            # Set all to zero if insufficient data
            msg.wrench.force.x = 0.0
            msg.wrench.force.y = 0.0
            msg.wrench.force.z = 0.0
            msg.wrench.torque.x = 0.0
            msg.wrench.torque.y = 0.0
            msg.wrench.torque.z = 0.0
        
        return msg
    
    def udp_data_receiver(self):
        """UDP receiver for sensor data on port 5566"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Use SO_REUSEPORT to share port with other processes if needed
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self.get_logger().info('SO_REUSEPORT enabled for port sharing')
        except AttributeError:
            self.get_logger().warning('SO_REUSEPORT not available on this system')
        
        try:
            sock.bind((self.host, self.port_data))
            self.get_logger().info(f'FT sensor receiver bound to {self.host}:{self.port_data}')
            self.get_logger().info('Waiting for UDP data...')
        except Exception as e:
            self.get_logger().error(f'Failed to bind socket: {e}')
            return
        
        while rclpy.ok():
            try:
                data, addr = sock.recvfrom(4096)
                message = data.decode("utf-8").strip()
                
                # Parse JSON to extract FTSensorData
                try:
                    parsed_data = json.loads(message)
                    ft_sensor_data = parsed_data.get("FTSensorData", None)
                    
                    if ft_sensor_data is not None:
                        # Create sensor wrench message
                        ft_wrench_msg = self.create_sensor_wrench_msg(ft_sensor_data)
                        
                        # Publish wrench data
                        self.ft_sensor_publisher.publish(ft_wrench_msg)
                    else:
                        self.get_logger().debug(
                            f'No FTSensorData found in message from {addr[0]}:{addr[1]}')
                        
                except json.JSONDecodeError:
                    self.get_logger().warning(
                        f'Invalid JSON from {addr[0]}:{addr[1]}: {message[:100]}')
                except (IndexError, ValueError) as e:
                    self.get_logger().warning(f'Error processing FTSensorData: {e}')
                
            except Exception as e:
                if rclpy.ok():
                    self.get_logger().error(f'Error in FT data receiver: {e}')
                break
        
        sock.close()
        self.get_logger().info('FT data socket closed')


def main(args=None):
    rclpy.init(args=args)
    
    try:
        ft_sensor_node = FTSensorNode()
        
        try:
            rclpy.spin(ft_sensor_node)
        except KeyboardInterrupt:
            ft_sensor_node.get_logger().info('Shutting down FT sensor node...')
        finally:
            ft_sensor_node.destroy_node()
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
