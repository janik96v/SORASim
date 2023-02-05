# Table of Content

- [AirSim-Installation-Guide-(Windows)](#-AirSim-Installation-Guide-(Windows))
  * [Sub-heading](#sub-heading)
    + [Sub-sub-heading](#sub-sub-heading)
- [Heading](#heading-1)
  * [Sub-heading](#sub-heading-1)
    + [Sub-sub-heading](#sub-sub-heading-1)
- [Heading](#heading-2)
  * [Sub-heading](#sub-heading-2)
    + [Sub-sub-heading](#sub-sub-heading-2)


# AirSim Installation Guide (Windows)

The installation guide is intended to add information to AirSim's [official documenetation](https://microsoft.github.io/AirSim/build_windows/) and the [installation video](https://www.youtube.com/watch?v=1oY8Qu5maQQ&ab_channel=ChrisLovett) of Chris Lovett. This file contains certain details that were not included in either of the other two sources. 

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


## AirSim under Linux
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


