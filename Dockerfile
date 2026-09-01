FROM ros:lyrical

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    ros-lyrical-nav2-amcl \
    ros-lyrical-nav2-bt-navigator \
    ros-lyrical-nav2-controller \
    ros-lyrical-nav2-costmap-2d \
    ros-lyrical-nav2-dwb-controller \
    ros-lyrical-nav2-lifecycle-manager \
    ros-lyrical-nav2-map-server \
    ros-lyrical-nav2-msgs \
    ros-lyrical-nav2-navfn-planner \
    ros-lyrical-nav2-planner \
    ros-lyrical-nav2-regulated-pure-pursuit-controller \
    ros-lyrical-nav2-velocity-smoother \
    ros-lyrical-nav2-behaviors \
    ros-lyrical-ros-gz-bridge \
    ros-lyrical-ros-gz-sim \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN echo "source /opt/ros/lyrical/setup.bash" >> /root/.bashrc

CMD ["/bin/bash"]
