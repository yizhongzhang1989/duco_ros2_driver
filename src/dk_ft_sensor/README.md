# dk_ft_sensor

Standalone ROS2 driver for Dapkon force/torque sensors used with DUCO robots.

## Description

This package provides a ROS2 node specifically designed for **Dapkon force/torque (F/T) sensors** that communicate via **UDP protocol**. The node listens for UDP packets containing force and torque measurements transmitted by Dapkon sensors, parses the JSON-formatted data, and publishes it as standard ROS2 WrenchStamped messages.

**Sensor Compatibility:** This driver is designed for Dapkon F/T sensors that transmit `FTSensorData` through UDP in JSON format.

## Features

- **UDP communication**: Receives sensor data via UDP protocol (configurable host/port)
- **Dapkon sensor support**: Parses JSON-formatted `FTSensorData` from Dapkon F/T sensors
- **Raw data publishing**: Publishes force/torque data as WrenchStamped messages
- **No post-processing**: Direct sensor readings without calibration or gravity compensation
- **Configurable parameters**: Easily configure UDP settings and topic names
- **Standalone operation**: No dependencies on other robot controllers

## Parameters

- `host` (string, default: `"0.0.0.0"`): UDP host address to bind to
- `port` (int, default: `5566`): UDP port number to listen on
- `topic_name` (string, default: `"ft_sensor_raw"`): Topic name for publishing force/torque data

## Usage

### Build and Install the package

\`\`\`bash
cd /home/robot/Documents/robot_control_examples
colcon build --packages-select dk_ft_sensor
source install/setup.bash
\`\`\`

### Run the node

**Basic usage:**

\`\`\`bash
ros2 run dk_ft_sensor ft_sensor_node
\`\`\`

**With custom parameters:**

\`\`\`bash
ros2 run dk_ft_sensor ft_sensor_node --ros-args -p host:="0.0.0.0" -p port:=5566 -p topic_name:="ft_sensor_raw"
\`\`\`

**Using the launch file:**

\`\`\`bash
ros2 launch dk_ft_sensor ft_sensor.launch.py
\`\`\`

**Launch file with custom parameters:**

\`\`\`bash
ros2 launch dk_ft_sensor ft_sensor.launch.py host:="0.0.0.0" port:=5566 topic_name:="ft_sensor_raw"
\`\`\`

### Monitor the output

\`\`\`bash
ros2 topic echo /ft_sensor_raw
\`\`\`

Or with a custom topic name:

\`\`\`bash
ros2 topic echo /<your_topic_name>
\`\`\`

## Topics

### Published Topics

- \`/<topic_name>\` (geometry_msgs/WrenchStamped, default: \`/ft_sensor_raw\`): Raw force/torque sensor data from Dapkon sensor
  - \`force.x, force.y, force.z\`: Force in Newtons
  - \`torque.x, torque.y, torque.z\`: Torque in Newton-meters

## Configuration

### UDP Communication

The Dapkon F/T sensor transmits force and torque measurements via UDP. Configure the following parameters to match your sensor's network settings:

- **Host**: UDP address to bind to (default: \`0.0.0.0\` - listens on all interfaces)
- **Port**: UDP port number (default: \`5566\` - typical for Dapkon sensors)
- **Topic Name**: ROS2 topic for publishing sensor data (default: \`ft_sensor_raw\`)

### Data Format

The node expects UDP packets containing JSON data with the following structure:
\`\`\`json
{
  "FTSensorData": [Fx, Fy, Fz, Tx, Ty, Tz]
}
\`\`\`

Where:
- \`Fx, Fy, Fz\`: Force measurements along X, Y, Z axes (Newtons)
- \`Tx, Ty, Tz\`: Torque measurements around X, Y, Z axes (Newton-meters)
