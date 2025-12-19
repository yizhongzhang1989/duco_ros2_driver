# dk_ft_sensor

Standalone force/torque sensor driver for DUCO robot.

## Description

This package provides a simplified ROS2 node for reading force/torque sensor data from a UDP stream and publishing it as a ROS2 topic.

## Features

- Listens to UDP port 5566 for sensor data
- Extracts FTSensorData from JSON messages
- Publishes `/ft_sensor_wrench` topic (geometry_msgs/WrenchStamped)
- No calibration or gravity compensation (raw sensor data)
- Standalone operation (no dependencies on other robot controllers)

## Usage

### Build and Install the package

```bash
cd /home/robot/Documents/robot_control_examples
colcon build --packages-select dk_ft_sensor
source install/setup.bash
```

### Run the node

```bash
ros2 run dk_ft_sensor ft_sensor_node
```

Or use the launch file:

```bash
ros2 launch dk_ft_sensor ft_sensor.launch.py
```

### Monitor the output

```bash
ros2 topic echo /ft_sensor_wrench
```

## Topics

### Published Topics

- `/ft_sensor_wrench` (geometry_msgs/WrenchStamped): Raw force/torque sensor data
  - `force.x, force.y, force.z`: Force in Newtons
  - `torque.x, torque.y, torque.z`: Torque in Newton-meters

## Configuration

The UDP port is hardcoded to 5566. If you need to change it, modify the `port_data` parameter in `ft_sensor_node.py`.
