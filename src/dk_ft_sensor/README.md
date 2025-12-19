# dk_ft_sensor

Standalone force/torque sensor driver for DUCO robot.

## Description

This package provides a simplified ROS2 node for reading force/torque sensor data from a UDP stream and publishing it as a ROS2 topic.

## Features

- Listens to UDP port for sensor data (configurable)
- Extracts FTSensorData from JSON messages
- Publishes force/torque data as WrenchStamped messages
- No calibration or gravity compensation (raw sensor data)
- Standalone operation (no dependencies on other robot controllers)

## Parameters

- `host` (string, default: `"0.0.0.0"`): UDP host address to bind to
- `port` (int, default: `5566`): UDP port number to listen on
- `topic_name` (string, default: `"ft_sensor_raw"`): Topic name for publishing force/torque data

## Usage

### Build and Install the package

```bash
cd /home/robot/Documents/robot_control_examples
colcon build --packages-select dk_ft_sensor
source install/setup.bash
```

### Run the node

**Basic usage:**

```bash
ros2 run dk_ft_sensor ft_sensor_node
```

**With custom parameters:**

```bash
ros2 run dk_ft_sensor ft_sensor_node --ros-args -p host:="0.0.0.0" -p port:=5566 -p topic_name:="ft_sensor_raw"
```

**Using the launch file:**
raw
```

Or with a custom topic name:

```bash
ros2 topic echo /<your_topic_name>
```bash
ros2 launch dk_ft_sensor ft_sensor.launch.py
```

**Launch file with custom parameters:**

```bash
ros2 launch dk_ft_sensor ft_sensor.launch.py host:="0.0.0.0" port:=5566 topic_name:="ft_sensor_raw"
```

### Monitor the output

```bash
ros2 topic echo /ft_sensor_wrench
```<topic_name>` (geometry_msgs/WrenchStamped, default: `/ft_sensor_raw`): Raw force/torque sensor data
  - `force.x, force.y, force.z`: Force in Newtons
  - `torque.x, torque.y, torque.z`: Torque in Newton-meters

## Configuration

The UDP port is configurable via parameters. By default, it listens on `0.0.0.0:5566
  - `force.x, force.y, force.z`: Force in Newtons
  - `torque.x, torque.y, torque.z`: Torque in Newton-meters

## Configuration

The UDP port is hardcoded to 5566. If you need to change it, modify the `port_data` parameter in `ft_sensor_node.py`.
