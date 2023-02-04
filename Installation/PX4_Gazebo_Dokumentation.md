# PX4 & Gazebo Dokumentation:

## Adding new aircraft/drone model:

1. Create a folder in `/PX4-Autopilot/Tools/sitl_gazebo/models` for the new model (my_vehicle)
2. Create the following files in `/PX4-Autopilot/Tools/sitl_gazebo/models/my_vehicle`
        - model.config
        - my_vehicle.sdf (these can be based off the iris or solo models in `/Tools/sitl_gazebo/models`)
3. Create a new airframe file in `/PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes` and add default parameters inclusive mixer settings from similar models
4. Add the airframe name to `/PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes/CMakeLists.txt`
5. Create a file with the name of the new airframe in `/PX4-Autopilot/build/px4_sitl_default/etc/init.d-posix/airframes`. The file can be empty. All the settings will be written while building PX4 from the file located in `/PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes` (step 3)
6. Add the airframe name to `/platforms/posix/cmake/sitl_target.cmake` under the command line `set(models …)`

## Adding new world file:


