**AirSim Installationsanleitung:**

Die Installationnsanleitung soll als Ergänzung zur Anleitung auf [https://microsoft.github.io/AirSim/build\_windows/](https://microsoft.github.io/AirSim/build_windows/) und zum Video auf [https://www.youtube.com/watch?v=1oY8Qu5maQQ&ab\_channel=ChrisLovett](https://www.youtube.com/watch?v=1oY8Qu5maQQ&ab_channel=ChrisLovett) sie enthält gewisse Details, welche in keinem der beiden anderen Anleitungen enthalten waren.

- Download Unreal Launcher und Installation von Unreal Engine \>= 4.25
- Installation Microsoft Visual Studio 2022 und 2019. Installation der folgenden Pakete:
  - Desktop Development with C++
  - Windows 10 SDK 10.0.18362
  - neuste .NET Framework SDK

HINWEIS: Visual Studio 2019 wird nur für die Installation von AirSim verwendet, das Unreal Projekt kann nur mit Visual Studio 2022 geöffnet werden.

- Erstellen eines Unreal Projekts und download einer passenden Unreal World (e.g Landscape Mountains). Für die Erstellung eines korrekt Projekts muss aus der New Project Categories Games ausgewählt werden. Danach muss ein Blank Project gewählt werden und die Option von Blueprint auf C++ geändert werden. Den Rest der Einstellungen muss beibehalten werden. Der Speicherort und der Projektname kann vor der Erstellung geändert werden.
- Die heruntergeladene Welt und das erstellte Projekt müssen nun gemerged werden.
  - Kopieren des Ordners Maps und Assets im Content Ordner des Landscape Mountains Projekts in den Content Ordner des neuen Unreal Projekts
  - Kopieren des Ordners DerivedDataCache vom Landscape Mountain Projekts in den Content Ordner des neuen Unreal Projekts
  - Inhalt der DefaultEngine.ini Datei im Config Ordner des Landscape Mountains Projekts muss dem gleichnamigen File im neuen Unreal Projekt angefügt werden. Neuer Inhalt nur ergänzen und nicht den bestehenden Inhalt im neuen Unreal Projekt überschreiben
- Installation von AirSim durch öffnen der Developer Command Prompt for Visual Studio 2022
- Wechsel des Directory auf einen Ordner nicht welcher nicht im Directory C: liegt, sonst fehlen die Berechtigungen die AirSim Dateien herunterzuladen und Visual Studio muss mit Admin Rechten ausgeführt werden
- Ausführen des Befehls git clone https://github.com/Microsoft/AirSim.git.

WICHTIG: Falls der Befehl git nicht gefunden werden kann, muss git zuerst über den folgenden Link installiert werden [http://git-scm.com/download/win](http://git-scm.com/download/win)

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