######
#Date: 19.12.2022
##Version Log:
#-Builds on v5 Mission Script but is adapted for the Contigency Test according to experimental design
#-Geofence upload is deactivated 
#-Geofence Termination Coroutine is deactivated, Hovering after 2s pilot reaction time (and following kill switch procedure) is enabled --> Killer coroutine
#
#
#
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

# Used for storage of logged parameters 
pos_time = []; alt = []; longitude = []; lat = []
att_time = []; pitch = []; roll = []; yaw = []

# Import Operational Volumes
groundriskbuffer = pd.read_csv('../Flight_Plans/ground_risk_buffer_coordinates.csv',sep=";")
groundriskbuffer = pd.DataFrame.to_numpy(groundriskbuffer)
contigencyvolume = pd.read_csv('../Flight_Plans/contigency_volume_coordinates.csv',sep=";")
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

async def run(flight_plan,log_file):
    """Main Function"""
    
    ## Global Variables 
    global polygon

    ## Import Flight Plan from Excel
    fp = pd.read_excel('../Flight_Plans/'+flight_plan)
    print(fp)
    fp = pd.DataFrame.to_numpy(fp)
    tour_length = list(range(0,fp.shape[0]))
    speed = 23 #flight speed [m/s]

    ## Input for name of logfile
    filename = log_file
    print('Log will be saved to: ../Flight_Logs/'+filename+'.csv')
    

    ## Connection to PX4 via MAVSDK Server for Offboard Control 
    drone = System()
    await drone.connect(system_address="udp://:14540")

    ## Calls coroutine to wait until Drone<->PX4 Connection is succesful
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    ## Increasing allowed MAVLINK Timeout Time to avoid timeout error
    await drone.core.set_mavlink_timeout(2.0)
    
    ## Clears Geofence Areas on the Drone
    await drone.geofence.clear_geofence()
    await drone.mission.clear_mission()
    print("Old Geofence cleared.")

    ## Setting PX4 Parameters        
    await drone.param.set_param_int("GF_ACTION", 4) #Geofence Violation Behavior; 4 = Kill
    await drone.param.set_param_int("GF_COUNT", 1) #Geofence Activation after x Position Counts
    await drone.param.set_param_int("GF_PREDICT", 0) #Geofence Tractectory Prediction to stop before Violation; 0 = Disabled
    print("PX4 Parameters set.")

    ## Parallel coroutine/task defined as a function 
    ## to continously print mission progress.
    print_mission_progress_task = asyncio.ensure_future(print_mission_progress(drone))

    ## Parallel coroutine to log position and attitude. Further explanations below!!
    position_log_task = asyncio.ensure_future(position_logging(drone))
    attitude_log_task = asyncio.ensure_future(attitude_logging(drone))

    ## Parallel coroutine to shutdown the drone after geofence violation
    ## and resulting flight termination!
    pilot_termination = asyncio.ensure_future(killer(drone,flight_plan))

    ## Lists all parallel coroutines to pass it as an 
    ## input to the observe_is_in_air function
    running_tasks = [print_mission_progress_task,position_log_task,attitude_log_task,pilot_termination]

    ## Parallel coroutine to enable data logging until drone
    ## is landed. Further explanations below!!
    termination_task = asyncio.ensure_future(observe_is_in_air(drone, running_tasks))

   
    ## Iterates through the flight plan to store the Excel data into the
    ## mission items which are readable by the MAVSDK MissionPlan function.
    mission_items = []
    for i in tour_length:
        mission_items.append(MissionItem(fp[i,1],
                                        fp[i,2],
                                        fp[i,3],
                                        speed,
                                        True,
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
    
    # Uploads the mission_plan as an offboard controll to PX4.
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
    filename = '../Flight_Logs/'+filename+'.csv'
    log.to_csv(filename,sep=';')
    print('Log File saved as',filename)
    print('PX4 will be switched off')
    await drone.action.shutdown()
    
  

async def print_mission_progress(drone):
    """ This coroutine function is used to plot the mission progress
     and is called in the main function run() """

    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")


# async def observe_termination(drone):
#     """This coroutine function is used to shutdown the drone after Geofence Flight
#     Termination. Shutdown is set to 10s after termination
#     """
#     async for status_text in drone.telemetry.status_text():
#         print("--",status_text.text)
#         if status_text.text.strip() == "Geofence violation! Flight terminated":
#             await asyncio.sleep(10)
#             await drone.action.kill()
#             break


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
    del lat[:],longitude[:],alt[:],pos_time[:]
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

    global pitch,roll,yaw,att_time
    del pitch[:], roll[:], yaw[:],att_time[:]
    async for attitude_euler in drone.telemetry.attitude_euler():
        # print(attitude_euler)
        att_time.append(time.time())
        pitch.append(attitude_euler.pitch_deg)
        roll.append(attitude_euler.roll_deg)
        yaw.append(attitude_euler.yaw_deg)
        # await position_logging(drone)


async def killer(drone,flight_plan):
    """As soon as the required location is reached (first waypoint after take-off).
     The drone will change its heading into the direction of the flight path (315°),
     waits for 5 seconds and then continues the mission for 2 seconds (pilot reaction time).
      Afterwards, it will transition to hover and kills the whole simulation after 5 seconds of hovering."""

    #Import of flight plan for changing the heading after mission is paused
    fp = pd.read_excel('../Flight_Plans/'+flight_plan)
    fp = pd.DataFrame.to_numpy(fp)
    heading = 315 
    map_altitude = 458 #altitude according to PX4 world file

    async for mission_progress in drone.mission.mission_progress():
        #Initializes experiment according to DoE after take off is finished and journey to final waypoint will start.
        if mission_progress.current == 1:
            await drone.mission.pause_mission() #Pauses Mission
            await drone.action.goto_location(fp[0,1],fp[0,2],map_altitude+fp[0,3],heading) #Turn the UAV into required heading in order to start experiment
            # await drone.mission.start_mission()
            # await drone.mission.pause_mission()
            await asyncio.sleep(5)
            await drone.mission.start_mission() #Starting Experiment and continue mission for 2seconds
            print("Waiting for hover in 2s.....")
            await asyncio.sleep(2)
            await drone.mission.pause_mission() #Stops afer pilot reaction
            print('Hovering initated through pilot reaction')
            await asyncio.sleep(5)
            print('Kill switch activated to finish run ')
            await drone.action.terminate() #Shutdown drone after 5 second to finish experiment
            print('Wait for drone shutdown')
            await asyncio.sleep(10)
            await drone.action.kill()
   

if __name__ == "__main__":

    flight_plan = 'Flight_Plan_Location1.xlsx' 
    log_file = 'test'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(flight_plan,log_file))

