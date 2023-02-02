# SORASim

This repository contains additional material to the master thesis “High Fidelity UAV Simulation Tool for the Support of SORA Process Based Validation of Operational Flight Volume and Ground Risk Buffer" which was part of the Master of Science in Engineering (MSE). The aim of the master thesis is to use a high-fidelity UAV simulation in order to validate the size of the ground risk buffer and contingency volume for a UAV operation within the specific class according to EU Regulation 947/2019. The flight authorization permit is granted under the SORA methodology. The simulator may help to give an applicant additional insight and knowledge about how the intended operational parameters (flight speed, altitude, flight path, etc.) will affect the size of operational volumes and boundaries. However, even if the simulator has been verified by real test flights, it must be explicitly stated that the simulator or parts of it are not certified by third parties. The operator of the UAV mission for the underlying use case used acceptable means of compliance other than this simulator for a successful authorization. The results of the simulation helped them to gain new knowledge and better understanding for future applications. 

The high-fidelity UAV simulation is based on open-source software and uses the Gazebo simulator, PX4 Autopilot (SITL-Version), QGroundControl and Python using the MAVSDK library for communication via offboard control. In addition the AirSim simulator can be used to enable high quality rendering via Unreal Engine. For more information about the architecture of the simulator, see the thesis. The additional material as part of this repository will guide the user to install all the software and change the parts of the simulators to meet the goal of the underlying thesis. Among others, the changes include the adapation of the UAV model to mimic the DJI M300 RTK or the development of the offboard control script to fly the mission. 


## Repository Structure

- **Experiment**: Contains all the scripts for flying the mission and analysing the results of the contingency volume and ground risk buffer validation
- **Flight_Plans**: Includes the waypoints of the UAV mission for the use case as well as the geofence for the contingency volume and ground risk buffer
- **Installation**: Includes documentation on how to install and change parts of the simulator
- **Scripts**: Contains the offboard mission script to fly the UAV operation according to the SORA and its permit to fly
- **Simulation_Verification**: Includes the offboard mission script, the flight logs from flight test and simulation, the changes to the UAV model to mimic the UAV from the flight test and the analysis of the results


## Further Material / Documentation / Links

- [PX4 Autopilot](https://docs.px4.io/main/en/)
- [QGroundControl](http://qgroundcontrol.com/)
- [AirSim](https://microsoft.github.io/AirSim/)
- [Gazebo/PX4](https://docs.px4.io/main/en/simulation/gazebo.html) or the Website of [Gazebo Simulator](https://gazebosim.org/home)
- [MAVSDK](https://mavsdk.mavlink.io/main/en/)