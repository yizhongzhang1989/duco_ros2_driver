cmake_minimum_required(VERSION 3.8)
project(dk_ft_sensor)

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)

# Install Python modules
ament_python_install_package(${PROJECT_NAME})

# Install Python executables
install(PROGRAMS
  dk_ft_sensor/ft_sensor_node.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME ft_sensor_node
)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
