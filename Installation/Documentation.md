# Table of Content

- [AirSim Installation](#airsim-installation-guide-windows)
  * [AirSim on Windows](#airsim-on-windows)
  * [AirSim on Linux](#airsim-on-linux)
    + [Sub-sub-heading](#sub-sub-heading)
- [AirSim-Python API Installation](#airsim-python-api-installation)
- [Installation of PX4 SITL (using WSL)](#installation-of-px4-sitl-using-wsl)
  * [Troubleshooting if AirSim and PX4 won't connect](#troubleshooting-if-airsim-and-px4-wont-connect)
  * [Some usful additional information](#some-usful-additional-information)
    + [PX4 Log File Storage Folder](#px4-log-file-storage-folder)
    + [Helpful Linux Code](#helpful-linux-code)

# AirSim Installation

The installation guide is intended to add information to AirSim's [official documenetation](https://microsoft.github.io/AirSim/build_windows/) and the [installation video](https://www.youtube.com/watch?v=1oY8Qu5maQQ&ab_channel=ChrisLovett) of Chris Lovett. This file contains certain details that were not included in either of the other two sources. 

## AirSim on Windows

1. Download Unreal Launcher and install Unreal Engine \>= 4.25
2. Install Microsoft Visual Studio 2019 and 2022 and the following packages:
    - Desktop Development with C++
    - Windows 10 SDK 10.0.18362
    - Newest .NET Framework SDK

> **NOTE:** Visual Studio 2019 is only required to install AirSim (v1.7.0). To set up the Unreal project the newer version of Visual Studio was needed as with the version of 2019 several issues where experienced. According to the [AirSim's repository](https://github.com/microsoft/AirSim) newer version should also support VS 2022


3. Create an Unreal project and download a suitable Unreal World (e.g. Landscape Mountains) from the Unreal Editor or from the **Assets** list of the corresponding release on the [AirSim repository](https://github.com/microsoft/AirSim/releases/tag/v1.8.1-windows).
4. To create the Unreal project correctly select: "New Project Categories>Games>Blank Projec>" then change the option Blueprint to C++ keep the rest of the settings as default and change the location and name of the project. 
5 .Merge the downloaded world environment with the created project: 
    - Copy the folder "Maps" and "Assets" from the "Content" folder of the downloaded Unreal World (e.g. Landscape Mountains) to the "Content" folder of the creatd project
    - Copy the folder "DerivedDataCache" from the downloaded Unreal World (e.g. Landscape Mountains) to the "Content" folder of the creatd project
    - Copy the content of the "DefaultEngine.ini" file from the "Config" folder of the downloaded Unreal World (e.g. Landscape Mountains) to same file of the new Unreal project. Only add new content but do not overwrite the existing content
6. Install AirSim by opening the Developer Command Prompt for Visual Studio 2022.
7. Change the directory to a folder that is not in the C: directory, otherwise the permissions to download the AirSim files are missing and Visual Studio must be executed as Admin
8. Execute the command `git clone https://github.com/Microsoft/AirSim.git`


> **NOTE:** If the command can not found Git, it must be installed first with the following link: [http://git-scm.com/download/win](http://git-scm.com/download/win)

9. After successfully downloading the AirSim files, change to the AirSim folder `cd AirSim`
10. Install them by type in `build.cmd`. It will create a folder which can then be added to the existing Unreal project
    - Copy the folder `AirSim\Unreal\Plugins` into the main directory of your Unreal project
11. Restart Visual Studio 2022 and open the file 'xxxx.uproject' which is in the folder of your Unreal project.
12. Copy the following [code](https://microsoft.github.io/AirSim/unreal_custenv/) to the end of the file you just opened

```
"AdditionalDependencies": [
    "AirSim"
]
"Plugins": [
    {
        "Name": "AirSim",
        "Enabled": true
    }
]
```

13. Open the created Unreal project with the Unreal Editor select `File>Refresh Visual Studio Projects` to apply the changes and open Visual Studio
14. Open the settings inside the Unreal Editor through `Window>World Settings` and change the Game Mode to **AirSimGameMode**.
15. Search in the search bar of the *World Outliner* settings for *Player Start Position* and delete all available start positions except for one
16. Move the launch position close to the ground and start the simulation through *Play* . If a UAV appears on screen, the installation was successful!
17. In the Unreal Editor go to `Edit>Editor Preferences` and serach for *CPU* and disable *Use Less CPU when in Background*


## AirSim on Linux
> **NOTE:** If AirSim is installed in Linux (Ubuntu 18.04) follow the steps in this section. Use it as additional information to the [AirSim Github page](https://microsoft.github.io/AirSim/build_linux/). Instructions on how to build the Unreal environment is also available under the same webpage. 

```
git clone https://github.com/Microsoft/AirSim.git
cd AirSim
 ./setup.sh
 ./build.sh
```

- If `./build.sh` gives an error, try to install the following `sudo apt-get install libstdc++-8-dev`
- If AirSim is installed on Linux and used in combination with Gazebo, the following code must be executed

```
sudo apt-get install libstdc++-8-dev
./clean.sh
./setup.sh
./build.sh –gcc
```
 
- If the necessary compiler is not yet installed `./build.sh -gcc` will produce an error. Install the compiler with `sudo apt-get install gcc-8 g++-8`


# AirSim-Python API Installation:

This documentation adds additional informatin to the [AirSim documentatin about its APIs](https://microsoft.github.io/AirSim/apis/). In order to follow the documentation, AirSim must be installed and embedded in an Unreal project. Furthermore, Anaconda must already be installed.

1. Open the Anaconda Command Prompt
2. Create a new Conda environment with the command `conda create --name myenv` (myenv = name of the environment).
3. Open the new environment with `conda activate myenv`
4. Install the pip library `conda install -n myenv pip`
5. Run the two commands to install the AirSim package
```
pip install msgpack-rpc-python
pip install airsim
```

6. The new Anaconda environment has now all packages required to access the AirSim-Python API. The AirSim packages allow to control the drone via offboard commands or to display telemetry data from the drone. More information about the available APIs through the AirSim package are on their [website](https://microsoft.github.io/AirSim/apis/).


# Installation of PX4 SITL (using WSL)

The following documentation is intended as an additional information to [AirSim's PX4 installation guide](https://microsoft.github.io/AirSim/px4_sitl/) and the [video](https://www.youtube.com/watch?v=DiqgsWIOoW4&t=297s&ab_channel=ChrisLovett). The documentation has further information which is not included in either of the other two instructions. The installation guide assumes that AirSim has already been successfully integrated into an Unreal project.

1. Install WSL (Windows Subsystem for Linux). Open Windows Powershell as administrator and execute `wsl - - install`. It installs all necessary packages including the Ubuntu distribution.
2. Reboot your computer and open Ubuntu as a normal application
3. Execute the following:
```
mkdir -p PX4
cd PX4
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh --no-nuttx --no-sim-tools
cd PX4-Autopilot
```

4. Build PX4 and boot the firmware in SITL mode with `make px4_sitl_default none_iris'. To quit the software press CTRL+C.
5. Open a command prompt execute `ipconfig`. It shows you the following output and you must copy the IP-address `IPv4-Adresse . . . . . . . . . . : 192.16.118.1` of your output. It contains the IP address of the host so that WSL can reach it.

```
Ethernet-Adapter vEthernet (WSL):
Verbindungsspezifisches DNS-Suffix:
Verbindungslokale IPv6-Adresse . : fe80::b00e:4bf6:569c:23fa%68
**IPv4-Adresse . . . . . . . . . . : 192.16.118.1**
Subnetzmaske . . . . . . . . . . : 255.255.240.0
Standardgateway . . . . . . . . . :
```

6. Back in Linux, run `nano ~/.bashrc` and add the expression `export PX4\_SIM\_HOST\_ADDR=192.16.118.1` to the end of the document. The last digits are the IP-address of your Windows host and must be identical with the one copied in step 5.

> **NOTE:** If `nano` is not installed yet, install it first. After installation and the changes in the previous step save the file with CTRL+X

7. In Linux, execute the command `ip address show`. It gives you the output below from which you copy the IP-address `inet 192.16.123.122`. This describes the IP address of the Linux system.

```
6: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:15:5d:05:cc:3c brd ff:ff:ff:ff:ff:ff
    inet 192.16.123.122/20 brd 192.16.126.255 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::215:5dff:fe05:cc3c/64 scope link
       valid_lft forever preferred_lft forever
```

8. Open the AirSim *settings.json* in Windows which where located at the author's computer at `C:\Users\Username\OneDrive\Documents\AirSim`. Add the following to the settins file:

```
{
"SeeDocsAt": "https://github.com/Microsoft/AirSim/blob/master/docs/settings.md",
"SettingsVersion": 1.2,
"SimMode": "Multirotor",
"ClockType": "SteppableClock",
"Vehicles": {
"PX4": {
"VehicleType": "PX4Multirotor",
"UseSerial": false,
"LockStep": true,
"UseTcp": true,
"TcpPort": 4560,
"ControlIp": "192.16.123.122",
"ControlPortLocal": 14540,
"ControlPortRemote": 14580,
"LocalHostIp": "192.16.118.1",
"Sensors": {
"Barometer": {
"SensorType": 1,
"Enabled": true,
"PressureFactorSigma": 0.0001825
}
},
"Parameters": {
"NAV\_RCL\_ACT": 0,
"NAV\_DLL\_ACT": 0,
"COM\_OBL\_ACT": 1,
"LPE\_LAT": 47.641468,
"LPE\_LON": -122.140165
}
}
},
"OriginGeopoint": {
"Latitude": 47.641468,
"Longitude": -122.140165,
"Altitude": 122
}
}
```

>**NOTE:** The *LocalHostIp* and the *ControlIp* are the ones from step 5 and 7, respectively. I

9. Open TCP port 4560 and UDP port 14540 in the firewall of the Windows system. This will allow the PX4 controller to send data to AirSim. A short video on how to open a TCP port can be found here [https://www.youtube.com/watch?v=xMGPyZtdP00&ab\_channel=RobertMcMillen](https://www.youtube.com/watch?v=xMGPyZtdP00&ab_channel=RobertMcMillen)

10. Start the simulator through the Unreal Editor and execute the PX4 autopilot in Linux with the command `make px4\_sitl\_default none\_iris`


## Troubleshooting if AirSim and PX4 won't connect
>**NOTE:** AirSim and PX4 should be able to communicate with your antivirus software activated. If your antivirus software due to some reasons does not allow a proper communication between both parts, switch it of temporarely. 

- The connection between PX4 and AirSim was succesfull when PX4 writes the output below in the terminal.
- The IP-address of the Windows host `PX4 SIM HOST: 192.16.118.1` must be equal to the one from step 5. If not or if `local host` is written, reboot Ubuntu and try again.

```
PX4 SIM HOST: 192.16.118.1
INFO [simulator] Simulator using TCP on remote host 192.16.118.1 port 4560
WARN [simulator] Please ensure port 4560 is not blocked by a firewall.
INFO [simulator] Waiting for simulator to accept connection on TCP port 4560
INFO [simulator] Simulator connected on TCP port 4560.

```


- If AirSim still does not connect to PX4 SITL firmware check if the firewall blocks Unreal Launcher/Unreal Editior. Open the same settings as in step 9 (*Windows Defender Firewall with Advanced Security*). All the incoming rules in Windows Defender Firewall should be green (see image below). If not allow them. 

![Windows Defender Firewall necessary Inbound Rules](./pictures/firewall_inbound_rules.png)


- If the PX4 controller still does not connect to AirSim, add the following code to the file located under `PX4-Autopilot/ROMFS/px4fmu\_common/init.d-posix/rcS`. However, it was no longer necessary for the PX4 version v1.13.0 used in the underlying project.

```
#If PX4_SIM_HOST_ADDR environment variable is empty use localhost.
if [ -z "${PX4_SIM_HOST_ADDR}" ]; then
    echo "PX4 SIM HOST: localhost"
    simulator start -c $simulator_tcp_port
else
    echo "PX4 SIM HOST: $PX4_SIM_HOST_ADDR"
    simulator start -t $PX4_SIM_HOST_ADDR $simulator_tcp_port
```

>**NOTE**: If no GPS position can be found, use the command `ip address show` in Linux to double check the IP-address of the virtual machine and compare it again with the AirSim setup file (*settings.json*) in Windows. 

- If you are not sure if the GPS position is set through AirSim open the command terminal *DroneShell* under `AirSim\DroneShell\build\x64\Release` and enter the command `pos`. If *lat*, *lon* and *alt* are 0 the GPS fix did not work.
- If the latest PX4 version does not connect to AirSim or no GPS fix is found after successful connection, downgrade to the older PX4 version (v1.12.0). Therefore change the director in Linux to `/PX4/PX4-Autopilot` and enter the command `git checkout v1.12.0`.


## Some usful additional information

### PX4 Log File Storage Folder

Under Linux go to `/PX4/PX4-Autopilot/build/px4\_sitl\_default/tmp/rootfs/log`

### Helpful Linux Code:

If you have to delete PX4 it may be writte-protected. To delete the folder an reinstall use `sudo rm -rf /my/locked/directory`