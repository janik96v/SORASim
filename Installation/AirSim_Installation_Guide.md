# AirSim Installation Guide

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


> **NOTE:** If the comman can not found Git, it must be installed first with the following link: [http://git-scm.com/download/win](http://git-scm.com/download/win)





- Nach erfolgreichem Download der AirSim Dateien wechsel in den AirSim Ordner (cd AirSim)
- Installation durch build.cmd. Dadurch wird ein Plugin Ordner erstellt, welcher danach ins bestehende Unreal Projekt eingefügt werden kann.
- Der erstellte Ordner unter AirSim\Unreal\Plugins in das Hauptverzeichnis des neu erstellten Unreal Projekts kopieren
- Neustar von Visual Studio 2022 und öffnen der Datei xxxx.uproject im Ordner des neu erstellten Unreal Projekt.
- Kopieren des folgenden Codes an das Ende der soeben geöffneten Datei: Der ganze Code kann unter [https://microsoft.github.io/AirSim/unreal\_custenv/](https://microsoft.github.io/AirSim/unreal_custenv/) gefunden werden.

,

"AdditionalDependencies": [

"AirSim"

]

}

],

"TargetPlatforms": [

"MacNoEditor",

"WindowsNoEditor"

],

"Plugins": [

{

"Name": "AirSim",

"Enabled": true

}

]

}

- Öffnen des Unreal Editors und des erstellten Projekts im Editor und File\Refresh Visual Studio Projects wählen um danach Visual Studio mit den gemachten Änderungen zu öffnen.
- Öffnen der Einstellungen unter Window\World Settings umso den Game Mode auf AirSimGameMode zu wechseln
- Suchen im World Outliner Suchfeld nach Player Startposition, um alle Startpositionen bis auf eine zu löschen.
- Die Startposition nahe an den Boden bringen und die Simulation mit Play starten. Falls die Drohne erscheint, hat die Installation funktioniert.
- Im Unreal Editor unter «Edit  Editor Preferences" öffnen und "CPU" im der Suche eingeben. Den Hacken bei «Use Less CPU when in Background» entfernen.

**WICHTIG:**

- Falls AirSim in Linux (Ubuntu 18.04) installiert wird, werden dabei die folgenden Befehle benötigt. Zu finden sind diese unter der AirSim Github Page.

git clone https://github.com/Microsoft/AirSim.git

cd AirSim
 ./setup.sh
 ./build.sh

Falls der ./build.sh Befehl einen Fehler auswirft, muss versucht werden mit folgendem Befehl nötige Dependencies/Packages zu installieren. Dies sollte eigentlich bereits durch ./setup.sh geschehen, passierte da aber nicht. Der zusätzlich auszuführende Befehl ist der folgende:

sudo apt-get install libstdc++-8-dev

- Falls AirSim für GazeboDrone installiert wird, müssen gemäss Github Page die folgenden Befehle ausgeführt werden:

sudo apt-get install libgazebo9-dev.
 ./ **clean**.sh
./ **setup**.sh

./ **build**.sh **–gcc**

Wenn der ./build.sh Befehl aufgrund des fehlenden Compilers abgebrochen wird mit dem nachfolgenden Befehl den nötigen Compiler installieren:

sudo apt-get install gcc-8 g++-8