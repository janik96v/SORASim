######
#Date: 06.10.2022
##Version Log:
#Validation Flight 
#PX4 make cmd: make px4_sitl gazebo_matrice_300__validation

######

#!/usr/bin/env python3

import time
import asyncio
from fileinput import filename
from typing import Text
import pandas as pd
import numpy as np
from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)
from mavsdk.geofence import Point, Polygon
import pickle
import mavsdk.telemetry 

## Global Variables 

# Used for storage of logged parameters 
pos_time = []; alt = []; longitude = []; lat = []
att_time = []; pitch = []; roll = []; yaw = []

# Import Operational Volumes
groundriskbuffer = pd.read_csv('./Flight_Plans/ground_risk_buffer_coordinates.csv',sep=";")
groundriskbuffer = pd.DataFrame.to_numpy(groundriskbuffer)
contigencyvolume = pd.read_csv('./Flight_Plans/contigency_volume_coordinates.csv',sep=";")
contigencyvolume = pd.DataFrame.to_numpy(contigencyvolume)
geofence = contigencyvolume #Defines which operational volume should be used for geofencing

# GeoFencing Points 
volume = [] 
for i in geofence[:,0]:
    i = int(i)-1
    p = Point(geofence[i,1],geofence[i,2])
    list.append(volume,p)

# Create a polygon object using your points
polygon = Polygon(volume, Polygon.FenceType.INCLUSION)

async def run():
    """Main Function"""
    global polygon

    ## Import Flight Plan from Excel
    fp = pd.read_excel('./Flight_Plans/Flight_Plan_Validation_angepasst.xlsx')
    print(fp)
    fp = pd.DataFrame.to_numpy(fp)
    tour_length = list(range(0,fp.shape[0]))
    speed = 15 #flight speed [m/s]

    ## Input for name of logfile
    print("Log will be saved to script location. Type in the file name")
    filename = input()

    ## Connection to PX4 via MAVSDK Server for Offboard Control 
    drone = System()
    await drone.connect(system_address="udp://:14540")

    ## Clears Geofence Areas on the Drone
    await drone.geofence.clear_geofence()

    ## Calls coroutine to wait until Drone<->PX4 Connection is succesful
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    ## Setting PX4 Parameters        
    await drone.param.set_param_int("GF_ACTION", 4) #Geofence Violation Behavior; 4 = Kill
    await drone.param.set_param_int("GF_COUNT", 1) #Geofence Activation after x Position Counts
    await drone.param.set_param_int("GF_PREDICT", 0) #Geofence Tractectory Prediction to stop before Violation; 0 = Disabled
    await drone.param.set_param_float("NAV_ACC_RAD",1) #Acceptance Turning Radius
    # await drone.param.set_param_float("MPC_XY_VEL_ALL",20) #Overall horizontal velocity limit
    # await drone.param.set_param_float("MPC_XY_CRUISE",20) #Maximum horizontal velocity in mission mode
    # await drone.param.set_param_float("MPC_VEL_MAX_DN",7) #Maximum descent velocity in offboard mode
    # await drone.param.set_param_float("MPC_VEL_MAX_UP",6) #Maximum ascent velocity in offboard mode
    print("PX4 Parameters set.")

    # ##PID Tune
    # #Rate Controller
    # await drone.param.set_param_float("MC_ROLLRATE_K",1.4)
    # await drone.param.set_param_float("MC_ROLLRATE_D",0.0011)
    # await drone.param.set_param_float("MC_ROLLRATE_I",0.104)
    # await drone.param.set_param_float("MC_PITCHRATE_K",1.4)
    # await drone.param.set_param_float("MC_PITCHRATE_D",0.0012)
    # await drone.param.set_param_float("MC_PITCHRATE_I",0.112)
    # await drone.param.set_param_float("MC_YAWRATE_K",2.5)
    # await drone.param.set_param_float("MC_YAWRATE_I",0.14)
    # #Attitude Controller
    # await drone.param.set_param_float("MC_ROLL_P",6.5)
    # await drone.param.set_param_float("MC_PITCH_P",3.0)
    # await drone.param.set_param_float("MC_YAW_P",5.0)
    # #Velocity Controller
    # await drone.param.set_param_float("MPC_XY_VEL_P_ACC",4.2)
    # await drone.param.set_param_float("MPC_XY_VEL_I_ACC",8.2)
    # await drone.param.set_param_float("MPC_XY_VEL_D_ACC",1.0)   
    # await drone.param.set_param_float("MPC_Z_VEL_P_ACC",12.0)
    # await drone.param.set_param_float("MPC_Z_VEL_I_ACC",2.4)
    # await drone.param.set_param_float("MPC_Z_VEL_D_ACC",0.8) 
    # #Position Controller
    # await drone.param.set_param_float("MPC_XY_P",0.95)
    # await drone.param.set_param_float("MPC_Z_P",1.0)


    ## Parallel coroutine/task defined as a function 
    ## to continously print mission progress.
    print_mission_progress_task = asyncio.ensure_future(print_mission_progress(drone))

    ## Parallel coroutine to log position and attitude. Further explanations below!!
    position_log_task = asyncio.ensure_future(position_logging(drone))
    attitude_log_task = asyncio.ensure_future(attitude_logging(drone))

    ## Lists all parallel coroutines to pass it as an 
    ## input to the observe_is_in_air function
    running_tasks = [print_mission_progress_task,position_log_task,attitude_log_task]

    ## Parallel coroutine to enable data logging until drone
    ## is landed. Further explanations below!!
    termination_task = asyncio.ensure_future(observe_is_in_air(drone, running_tasks))

    ## Parallel coroutine to shutdown the drone after geofence violation
    ## and resulting flight termination!
    geofence_termination = asyncio.ensure_future(observe_termination(drone))
    
    ## Iterates through the flight plan to store the Excel data into the
    ## mission items which are readable by the MAVSDK MissionPlan function.
    mission_items = []
    for i in tour_length:
        mission_items.append(MissionItem(fp[i,1],
                                        fp[i,2],
                                        fp[i,3],
                                        speed,
                                        False,
                                        float('nan'),
                                        float('nan'),
                                        MissionItem.CameraAction.NONE,
                                        float('nan'),
                                        float('nan'),
                                        float('nan'),
                                        float('nan'),
                                        float('nan')))

    ## Stores the mission items in the MissionPlan function of MAVSDK
    mission_plan = MissionPlan(mission_items)

    await drone.mission.set_return_to_launch_after_mission(True)

    ## Uploads the mission_plan as an offboard controll to PX4.
    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)
    
    ## Calls a coroutine until GPS Lock is successful
    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Starting mission")
    await drone.mission.start_mission()    

    # # Upload the geofence to your vehicle
    # print("Uploading geofence...")
    # await drone.geofence.upload_geofence([polygon])
    # print("Geofence uploaded!")

    ## Starts kill switch procedure as parallel coroutine
    # asyncio.ensure_future(killer(drone)) #Comment out if no kill-switch needed
    await termination_task



    ## Saves log file with collected parameters from coroutines
    ## running as parallel tasks
    log = {'pos_time':pos_time ,'latitude':lat , 'longitude':longitude ,'altitude':alt}
    log2 = {'alt_time':att_time , 'pitch':pitch ,'roll':roll ,'yaw':yaw }

    log = pd.DataFrame(log)
    log2 = pd.DataFrame(log2)
    logsync = round(np.shape(log2)[0]/np.shape(log)[0])
    log2 = log2[(logsync-1)::logsync]
    log2 = log2.reset_index(drop=True)
    log = pd.concat([log,log2],axis=1)

    drone.info.get_flight_information
    # The logged data is saved to a .csv file
    log = pd.DataFrame(log)
    #log.loc[0] # Output first row of data frame
    #log['altitude'] # Output altitude column of data frame
    filename = '../Analysis/'+filename+'.csv'
    log.to_csv(filename,sep=';')
    print('Log File saved as',filename)
    
  

async def print_mission_progress(drone):
    """ This coroutine function is used to plot the mission progress
     and is called in the main function run() """

    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")


async def observe_termination(drone):
    """This coroutine function is used to shutdown the drone after Geofence Flight
    Termination. Shutdown is set to 10s after termination
    """
    async for status_text in drone.telemetry.status_text():
        print("--",status_text.text)
        if status_text.text.strip() == "Geofence violation! Flight terminated":
            await asyncio.sleep(10)
            await drone.action.kill()
            break



async def observe_is_in_air(drone, running_tasks):
    """Monitors whether the drone is flying or not and
    returns after landing. It allows data logging until touch down
    and not only until landing process is initiated.
    At end all running parallel task are terminated"""

    was_in_air = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air            

        if was_in_air and not is_in_air:
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await asyncio.get_event_loop().shutdown_asyncgens()

            return


async def position_logging(drone):
    """ Logging of positional data (GPS). Because of attitude logging which is logging 3x as much data, 
    only the first data point of attitude logging is kept and the rest will be deleted 
    --> ensures same amount of logging points """

    global lat, longitude, alt,pos_time
    async for position in drone.telemetry.position():
        # print(position)

        #Writes GPS Telemetry to file for plotter script
        try: 
            f = open('gps_telemetry.pckl', 'wb')
            pickle.dump([longitude,lat,alt], f)
            f.close()
        except: pass

        pos_time.append(time.time())
        alt.append(position.relative_altitude_m)
        longitude.append(position.longitude_deg)
        lat.append(position.latitude_deg)
        # await attitude_logging(drone)

           
async def attitude_logging(drone):
    """ Logging of attitude telemetry (IMU) """
    global pitch,roll,yaw
    async for attitude_euler in drone.telemetry.attitude_euler():
        # print(attitude_euler)
        att_time.append(time.time())
        pitch.append(attitude_euler.pitch_deg)
        roll.append(attitude_euler.roll_deg)
        yaw.append(attitude_euler.yaw_deg)
        # await position_logging(drone)


async def killer(drone):
    """Kills the mission after certain amounts of seconds by setting motor RPM to zero
     (terminate cmd) and killing the whole simulation (kill cmd) to save log"""

    print("waiting for kill in 35s.....")
    await asyncio.sleep(35)
    print("will clear mission")
    await drone.mission.clear_mission()
    print("cleared mission")
    await drone.action.terminate()
    await asyncio.sleep(20)
    await drone.action.kill()




if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

