# Gazebo Installation

This documentation is intended as a additional material to the instructions from [AirSim's documentation](https://microsoft.github.io/AirSim/gazebo_drone/) and from the [PX4 manual](https://docs.px4.io/main/en/simulation/gazebo.html). After a successful installation Gazebo and PX4 on Linux should be linked to AirSim and Unreal Environment on the Windows host. You can use the following documentation when AirSim on Windows and PX4 on Linux are already installed and tested successfully.

1. Install AirSim on Linux to build the necessary dependencies to communicate with the Windows host in a later step. Therefore, follow the instructions in this [section](https://github.com/janik96v/SORASim/blob/main/Installation/AirSim_Installation_Guide.md#airsim-under-linux) of the AirSim installation guide. 

2. Install AirSim for GazeboDrone with the following commands:
```
sudo apt-get install libgazebo9-dev
./clean.sh
./setup.sh
./build.sh --gcc
cd GazeboDrone
mkdir build && cd build
cmake -DCMAKE_C_COMPILER=gcc-8 -DCMAKE_CXX_COMPILER=g++-8 .. 
make
```

>**NOTE:** If  `./build.sh` fails the necessary compilers could be missing. Install them with `sudo apt-get install gcc-8 g++-8``

3. In order to ensure no issues due to previous installed versions of PX4, delete the existing folders containing PX4 and make a clean install of PX4 Autopilot. Use the following commands and reboot the system afterwards:

```
mkdir -p PX4
cd PX4
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh
```

>**NOTE:** If the error *Failed building wheel for pillow* occurs, execute the commands below to install the missing packages manually:
```
sudo apt-get install libjpeg-dev zlib1g-dev
pip3 install Pillow
sudo pip install -U setuptools
```

4. Start PX4 and Gazebo with `make px4\_sitl gazebo`.

        - If you get an error that the compiler or the path to the compiler is not found, execute the commands `sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 20` and `sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-8 20`
        - If, after a successful build of PX4, the flight controller is waiting on the TCP port and does not connect to Gazebo (Gazebo will not boot), quit PX4 with CTRL+C and run the command `sudo apt upgrade libignition-math2`. After a succesful upgrade delete the actual PX4 build and rebuild it with `make clean` and `make px4\_sitl gazebo`.


4. PX4 should now connect to Gazebo and once Gazebo is open, the functionality of both systems can be tested by entering a takeoff and land command in the terminal, where PX4 is running.
```
commander takeoff
commander land
```

5. If the test was successful so far, continue with the documentatino to connect Gazebo / PX4 with AirSim on the Windows host.Therefore, change the directory to `/AirSim/GazeboDrone/src` and open the file `main.cpp` with a text editor. Add the IP-address of the host machine in line 42: `msr::airlib::MultirotorRpcLibClient client("Host IP Address");`

>**NOTE:** More information on how to find the IP-address of the host machine see [section](https://github.com/janik96v/SORASim/blob/main/Installation/PX4_SITL_Installation_Guide.md#installation-of-px4-sitl-using-wsl) step 5.


6. After adding the IP-address of the host machine rebuild AirSim with the following commands:

```
./clean.sh
./setup.sh
./build.sh –gcc
cd GazeboDrone/build
cmake -DCMAKE_C_COMPILER=gcc-8 -DCMAKE_CXX_COMPILER=g++-8 ..
make
```

7. To change the internal physic engine of AirSim (FastPhysics) and all the sensor models from AirSim to Gazebo make the following changes to the *settings.json* of AirSim:

```
"SettingsVersion": 1.2,
  "SimMode": "Multirotor",
  "ClockType": "SteppableClock",
  **"PhysicsEngineName": "ExternalPhysicsEngine"**,
  "Vehicles": {
    "PX4": {
      "VehicleType": "PX4Multirotor",

```

>**NOTE:** Leave the rest of *settings.json* file unchanged and change only the above lines. Actually only the *PhysicsEngineName* parameter.

8. In order for PX4 to communicate with the Windows Host (AirSim) and the ground control station (QGroundControl) on the same time, activate Mavlink Broadcast. Change the folder to `PX4/PX4-Autopilot/ROMFS/px4fmu\_common/init.d-posix` and open the file `px4-rc.mavlink`. The file will contain the following lines of code. Change the bold part from `-m` to `-p`. After the changes Mavlink is now broadcasting from the PX4 controller to the appropriate UDP ports on the host, where other software as AirSim and QGroundControl will listen for commands.

```
#!/bin/sh
# shellcheck disable=SC2154

udp_offboard_port_local=$((14580+px4_instance))
udp_offboard_port_remote=$((14540+px4_instance))
[ $px4_instance -gt 9 ] && udp_offboard_port_remote=14549 # use the same ports for more than 10 instances to avoid port overlaps
udp_onboard_payload_port_local=$((14280+px4_instance))
udp_onboard_payload_port_remote=$((14030+px4_instance))
udp_onboard_gimbal_port_local=$((13030+px4_instance))
udp_onboard_gimbal_port_remote=$((13280+px4_instance))
udp_gcs_port_local=$((18570+px4_instance))

# GCS link
mavlink start -x -u $udp_gcs_port_local -r 4000000 -f **-p**
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
mavlink start -x -u $udp_offboard_port_local -r 4000000 -f **-p** onboard -o $udp_offboard_port_remote

# Onboard link to camera
mavlink start -x -u $udp_onboard_payload_port_local -r 4000 -f **-p** onboard -o $udp_onboard_payload_port_remote

# Onboard link to gimbal
mavlink start -x -u $udp_onboard_gimbal_port_local -r 400000 **-p** gimbal -o $udp_onboard_gimbal_port_remote
```


9. The simulation can finally be started again with `make px4\_sitl gazebo` in the director `/PX4/PX4-Autopilot` and with `./GazeboDrone` in `/AirSim/GazeboDrone/build`. Both happens on the Linux side. 

10. On Windows start the Unreal Simulation and open QGroundControl. The `./GazeboDrone` script should now connect to AirSim on the Windows host and forward the calculated positions from the Gazebo Simulator. QGroundControl should connect automatically via UDP broadcast from PX4. The AirSim Pyhton API can still be used to retrieve sensor data from the Unreal simulation. However, the AirSim Pyhton API no longer works to control the UAV. This can now be done through MAVSDK. To do this, connect MAVSDK to the Windows host via UDP port 14540. For more information, see the instructions for installing MAVSDK. In the PX4 controller, there is no need to create an additional MAVLink connection/broadcast for the MAVSDK API, as the AirSim Pyhton API no longer accesses the flight controller. Thus, the AirSim Python API can be used to talk via MAVSDK to PX4.



 

## Additional Information

- To define PX4 specific UAV parameters by default when starting PX4, add them in the file `px4-rc.params` in the folder  `PX4/PX4-Autopilot/ROMFS/px4fmu\_common/init.d-posix`. The following parameters are recommended for offboard control:

```
#!/bin/sh
# shellcheck disable=SC2154

#param set-default MAV_SYS_ID $((px4_instance+1))
#param set-default IMU_INTEG_RATE 250

# Set Parameter for Offboard Control without Remote Controller
param set-default NAV_DLL_ACT 0
param set-default NAV_RCL_ACT 0
param set-default COM_OF_LOSS_T 30
param set-default COM_OBL_ACT 1
param set-default COM_RCL_EXCEPT 
```

>**NOTE:** All PX4 parameters are listed and explained on their [website](https://docs.px4.io/v1.12/en/advanced_config/parameter_reference.html)


- To set the GPS coordinates of the take-off location, open the following folder `~/PX4/PX4-Autopilot/Tools/sitl_gazebo/worlds ` . The folder contains all the predefined Gazebo world files. By default, the *empty.world* file is used. The content of the file is included below and the GPS coordinates to change are in bold. After the changes, the new take-off location should be visible in QGroundControl when the simulation is started. 

```
<?xml version="1.0" ?>
<sdf version="1.5">
<world name="default">
<!-- A global light source -->
<include>
<uri>model://sun</uri>
</include>
<!-- A ground plane -->
<include>
<uri>model://ground_plane</uri>
</include>
<include>
<uri>model://asphalt_plane</uri>
</include>
**<spherical_coordinates>**
**<surface_model>EARTH_WGS84</surface_model>**
**<latitude_deg>47.130633650952</latitude_deg>**
**<longitude_deg>7.24060672327239</longitude_deg>**
**<elevation>458.0</elevation>**
**</spherical_coordinates>**
<physics name='default_physics' default='0' type='ode'>
<gravity>0 0 -9.8066</gravity>
<ode>
<solver>
<type>quick</type>
<iters>10</iters>
<sor>1.3</sor>
<use_dynamic_moi_rescaling>0</use_dynamic_moi_rescaling>
</solver>
<constraints>
<cfm>0</cfm>
<erp>0.2</erp>
<contact_max_correcting_vel>100</contact_max_correcting_vel>
<contact_surface_layer>0.001</contact_surface_layer>
</constraints>
</ode>
<max_step_size>0.004</max_step_size>
<real_time_factor>1</real_time_factor>
<real_time_update_rate>250</real_time_update_rate>
<magnetic_field>6.0e-6 2.3e-5 -4.2e-5</magnetic_field>
</physics>
</world>
</sdf>

```


