# MAVSDK-Python Installation

The installation guide should be used as additional information to the instructions on their [GitHub page](https://github.com/mavlink/MAVSDK-Python). AirSim, PX4 SITL (in combination with Gazebo) and the Python API must be successfully installed beforehand.

1. Open Anaconda Command Prompt

2.  Use the command `conda activate myenv` to open the created conda environment (myenv), which is already needed for the AirSim Python API.

3. Install the following packages
```
pip3 install mavsdk
pip3 install aioconsole
```

4. If MAVSDK runs on a Windows host, the appropriate `mavsdk_server.exe` must be downloaded from their [GitHub page](https://github.com/mavlink/MAVSDK/releases/tag/v1.4.2) under the *Releases* tab. If MAVSDK is used on Linux, the `mavsdk_server.exe` is usually installed with it. The *mavsdk_server* must be placed in the folder `C:\Users\username\anaconda3\envs\airsimpy2\Lib\site-packages\mavsdk\bin` (location of the MAVSDK Python package)

5. In order for the previously installed *mavsdk_server* on the Windows host to be able to communicate with the PX4 SITL on the virtual machine, Mavlink UDP Broadcast must be activated on PX4. However, it should be already activated when [section](https://github.com/janik96v/SORASim/blob/main/Installation/Gazebo_Installation_Guide.md#gazebo-installatin-guide) (step 8) was followed.

6. Add a second Mavlink broadcast for offboard controls to the file `px4-rc.mavlink` which is located under `PX4/PX4-Autopilot/ROMFS/px4fmu\_common/init.d-posix`. The second broadcast instance allows to communicate to PX4 with offboard controls from either the AirSim Python API or via MAVSDK library. The content of the file is added below and the necessary changes are made in bold.

```
#!/bin/sh
# shellcheck disable=SC2154

udp_offboard_port_local=$((14580+px4_instance))
udp_offboard_port_remote=$((14540+px4_instance))
[ $px4_instance -gt 9 ] && udp_offboard_port_remote=14549 # use the same ports for more than 10 instances to avoid port overlaps
**udp_offboard_port_local_mavsdk=$((14581+px4_instance))**
**udp_offboard_port_remote_mavsdk=$((14541+px4_instance))**
udp_onboard_payload_port_local=$((14280+px4_instance))
udp_onboard_payload_port_remote=$((14030+px4_instance))
udp_onboard_gimbal_port_local=$((13030+px4_instance))
udp_onboard_gimbal_port_remote=$((13280+px4_instance))
udp_gcs_port_local=$((18570+px4_instance))

# GCS link
mavlink start -x -u $udp_gcs_port_local -r 4000000 -f -p
mavlink stream -r 50 -s POSITION_TARGET_LOCAL_NED -u $udp_gcs_port_local
mavlink stream -r 50 -s LOCAL_POSITION_NED -u $udp_gcs_port_local
mavlink stream -r 50 -s GLOBAL_POSITION_INT -u $udp_gcs_port_local
mavlink stream -r 50 -s ATTITUDE -u $udp_gcs_port_local
mavlink stream -r 50 -s ATTITUDE_QUATERNION -u $udp_gcs_port_local
mavlink stream -r 50 -s ATTITUDE_TARGET -u $udp_gcs_port_local
mavlink stream -r 50 -s SERVO_OUTPUT_RAW_0 -u $udp_gcs_port_local
mavlink stream -r 20 -s RC_CHANNELS -u $udp_gcs_port_local
mavlink stream -r 10 -s OPTICAL_FLOW_RAD -u $udp_gcs_port_local

# API/Offboard link
mavlink start -x -u $udp_offboard_port_local -r 4000000 -f -p onboard -o $udp_offboard_port_remote
**mavlink start -x -u $udp_offboard_port_local_mavsdk -r 4000000 -f -p onboard -o $udp_offboard_port_remote_mavsdk**

# Onboard link to camera
mavlink start -x -u $udp_onboard_payload_port_local -r 4000 -f -p onboard -o $udp_onboard_payload_port_remote

# Onboard link to gimbal
mavlink start -x -u $udp_onboard_gimbal_port_local -r 400000 -p gimbal -o $udp_onboard_gimbal_port_remote

```

>**NOTE:** The changes will open a new local and remote port when PX4 is started. On the Windows host, the corresponding remote port (port 14541) must be opened in the firewall. For more information on how to open ports see [section](https://github.com/janik96v/SORASim/blob/main/Installation/PX4_SITL_Installation_Guide.md#installation-of-px4-sitl-using-wsl) or watch the [video](https://www.youtube.com/watch?v=xMGPyZtdP00&ab_channel=RobertMcMillen).


7. To activate the MAVSDK - Python interface, start *mavsdk_server* manually if the executable is not copied to the directory of the MAVSDK-Python package as described in step 4. To manually start the *mavsdk_server* go to the corresponding directory and execute *mavsdk_server* with the command `Mavsdk_server udp://:14541`. The UDP port number must be identical with the one added to the broadcast file in step 6. If the *mavsdk_server* is added to the directory of the MAVSDK-Python package, *mavsdk_server* can be started directly via the Python script. Therefore, enter the UDP port in the following command `await drone.connect(system_address='udp://:14541')`. If the server is started manually, the command `await drone.connect()` can be left empty.

