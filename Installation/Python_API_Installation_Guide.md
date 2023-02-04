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


