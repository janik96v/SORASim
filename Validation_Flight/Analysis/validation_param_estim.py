######
#Date: 07.10.2022
##Version Log:
#
#
#
######

from cProfile import label
from math import sqrt
import re
from socket import EAI_SOCKTYPE
from turtle import color
from typing import Mapping
from cv2 import mean
from matplotlib.pyplot import axis, plot, show
from pip import main
import pymap3d as map
import numpy as np
import pandas as pd
import copy
import matplotlib.pyplot as plt

###Import 

##Real Flight Test Data
val_data1 = pd.read_csv('Validation/DJIFlightRecord_2022-08-25_[10-38-43].csv', sep=',')
val_data2 = pd.read_csv('Validation/DJIFlightRecord_2022-08-25_[10-42-05].csv', sep=',')
val_data3 = pd.read_csv('Validation/DJIFlightRecord_2022-08-25_[10-45-30].csv', sep=',')
val_flights = [val_data1,val_data2,val_data3]

##Simulation Data
sim_data1 = pd.read_csv('Validation/validation_final2.csv', sep=';')
# sim_data2 = pd.read_csv('Validation/validation_final2.csv', sep=';')
# sim_data3 = pd.read_csv('Validation/validation_final3.csv', sep=';')
#Removing first line (Time)
sim_data1 = sim_data1.iloc[:,1:]
# sim_data2 = sim_data2.iloc[:,1:]
# sim_data3 = sim_data3.iloc[:,1:]
sim_flights = [sim_data1,sim_data1,sim_data1]

##Simulation Data before Model Tuning
sim_data_comparison = pd.read_csv('Validation/validation_no_adjustments.csv', sep=';')
sim_data_comparison2 = pd.read_csv('Validation/validation_no_adjustments2.csv', sep=';')
sim_data_comparison3 = pd.read_csv('Validation/validation_no_adjustments3.csv', sep=';')
sim_data_comparison = sim_data_comparison.iloc[:,1:]
sim_data_comparison2 = sim_data_comparison2.iloc[:,1:]
sim_data_comparison3 = sim_data_comparison3.iloc[:,1:]
sim_compare = [sim_data_comparison,sim_data_comparison2,sim_data_comparison3]

##Waypoints
waypoints = pd.read_excel('Validation/Flight_Plan_Validation_angepasst.xlsx')
waypoints = waypoints.iloc[0:waypoints.shape[0]-1,:]
waypoints = waypoints.rename(columns={waypoints.columns[1]:'latitude',waypoints.columns[2]:'longitude',waypoints.columns[3]:'height'})

plt.plot(sim_data1['longitude'])
plt.show()

###Data Post Processing

def real_post_process(real_data,logsteps,start,end):
    '''Takes a data frame with 3 single flight logs from the flight testing as input. Extracts the most interesting columns.
    Turns them into correct units if needed, removes the starting and landing procedure and takes the average of the 3 logs.
    The function returns the averaged data set and the shortened flight logs of all 3 flights in one data frame'''

    ## Initial Variables
    real = pd.DataFrame()
    lat_waypoint1 = 46.9765208  #Latitude of Waypoint 1
    long_waypoint1 = 7.179124   #Longitude of Waypoint 1

    ## Post Processing Real Data
    # Iterating through Data Sets
    for i in real_data:

        #Exporting important columns
        real_single = copy.deepcopy(i.iloc[:,4])                    #Add latitude
        real_single = pd.concat([real_single,i.iloc[:,5]],axis=1)   #Add longitude
        real_single = pd.concat([real_single,i.iloc[:,6]],axis=1)   #Add height [ft]
        real_single = pd.concat([real_single,i.iloc[:,9]],axis=1)   #Add altitude [ft]
        real_single = pd.concat([real_single,i.iloc[:,10]],axis=1)  #Add speed [mph]
        real_single = real_single.rename({' OSD.latitude':'latitude',' OSD.longitude':'longitude',' OSD.height [ft]':'height',' OSD.altitude [ft]':'altitude',' OSD.hSpeed [MPH]':'speed'},axis=1)

        # Imperial Unit in SI
        real_single.loc[:,'height'] = real_single.loc[:,'height']/3.33      #ft --> m
        real_single.loc[:,'altitude'] = real_single.loc[:,'altitude']/3.33  #ft --> m
        real_single.loc[:,'speed'] = real_single.loc[:,'speed']*0.44704     #mph --> m/s

        #Removing Start Procedure
        real_start = copy.deepcopy(real_single)
        real_start.loc[:,'latitude'] = abs(real_start.loc[:,'latitude']-lat_waypoint1)
        real_start.loc[:,'longitude'] = abs(real_start.loc[:,'longitude']-long_waypoint1)
        summe = real_start.loc[:,'latitude'] + real_start.loc[:,'longitude']
        summe_start = summe.iloc[start:end]
        idx_start = summe_start.idxmin()
        summe_end = summe.iloc[end+1:] 
        idx_end = summe_end.idxmin()

        #Merging all runs in one data sate
        real_add = copy.deepcopy(real_single.iloc[idx_start:idx_end,:])
        new_idx = pd.Index(range(0,idx_end-idx_start,1))
        real_add.set_index(new_idx,inplace=True)
        real = pd.concat([real,real_add], axis=1, ignore_index=True)

    #Averaging Date of the runs
    cols = real_add.shape[1]
    lat_start = 0; long_start = 1; height_start = 2
    alt_start = 3; speed_start = 4

    lat = real[[lat_start,lat_start+cols,lat_start+2*cols]].mean(axis = 1, skipna = True) #Selecting necessary columns for mean
    long = real[[long_start,long_start+cols,long_start+2*cols]].mean(axis = 1, skipna = True) 
    height = real[[height_start,height_start+cols,height_start+2*cols]].mean(axis = 1, skipna = True) 
    alt = real[[alt_start,alt_start+cols,alt_start+2*cols]].mean(axis = 1, skipna = True) 
    speed = real[[speed_start,speed_start+cols,speed_start+2*cols]].mean(axis = 1, skipna = True) 

    #Create column with frequency of logged data
    time = pd.Series(np.arange(0,real.shape[0]/logsteps,1/logsteps))
    real = pd.concat([time,real], axis=1, ignore_index=True)     #Add them also to the data sets containing all runs

    real_avg = pd.DataFrame({
        'time': time,
        'latitude':lat,
        'longitude': long,
        'height': height,
        'altitude':alt,
        'speed':speed})

    return real_avg, real

##Post Processing Sim Data
def sim_post_process(sim,logsteps,start,end):
    '''Takes a data frame with 3 single flight logs from the simulation as input. 
    Removes the starting and landing procedure and takes the average of the 3 logs.
    The function returns the averaged data set and flight logs of all 3 flights in one data frame'''

    sim_all = pd.DataFrame()
    lat_waypoint1 = 46.9765208  #Latitude of Waypoint 1
    long_waypoint1 = 7.179124   #Longitude of Waypoint 1

    ##Iterating through Sim Runs
    for i in sim:
        #Deleting Start Procedure
        sim_start = copy.deepcopy(i)
        sim_start.loc[:,'latitude'] = abs(sim_start.loc[:,'latitude']-lat_waypoint1)
        sim_start.loc[:,'longitude'] = abs(sim_start.loc[:,'longitude']-long_waypoint1)
        summe = sim_start.loc[:,'latitude'] + sim_start.loc[:,'longitude']
        summe_start = summe.iloc[start:end]
        idx_start = summe_start.idxmin()
        summe_end = summe.iloc[end+1:]
        idx_end = summe_end.idxmin()

        #Merging all runs in one data sate
        sim_add = copy.deepcopy(i.iloc[idx_start:idx_end,:])
        new_idx = pd.Index(range(0,idx_end-idx_start,1))
        sim_add.set_index(new_idx,inplace=True)
        sim_all = pd.concat([sim_all,sim_add], axis=1, ignore_index=True)

    ##Averaging Date of the runs
    cols = sim_add.shape[1]
    lat_start = 1; long_start = 2; height_start = 3
    pitch_start = 5; roll_start = 6; yaw_start = 7

    lat = sim_all[[lat_start,lat_start+cols,lat_start+2*cols]].mean(axis = 1, skipna = True) #Selecting necessary columns for mean
    long = sim_all[[long_start,long_start+cols,long_start+2*cols]].mean(axis = 1, skipna = True) 
    height = sim_all[[height_start,height_start+cols,height_start+2*cols]].mean(axis = 1, skipna = True) 
    pitch = sim_all[[pitch_start,pitch_start+cols,pitch_start+2*cols]].mean(axis = 1, skipna = True) 
    roll = sim_all[[roll_start,roll_start+cols,roll_start+2*cols]].mean(axis = 1, skipna = True) 
    yaw = sim_all[[yaw_start,yaw_start+cols,yaw_start+2*cols]].mean(axis = 1, skipna = True) 

    #Create column with frequency of logged data
    time = pd.Series(np.arange(0,sim_all.shape[0]/logsteps,1/logsteps))
    sim_all = pd.concat([time,sim_all], axis=1, ignore_index=True)     #Add them also to the data sets containing all runs

    sim_avg = pd.DataFrame({
        'time':time,
        'latitude':lat,
        'longitude': long,
        'height': height,
        'pitch':pitch,
        'roll':roll,
        'yaw':yaw})


    return sim_avg, sim_all


def gps2enu(log):
    '''Turn GPS Coordinates in ENU coordinates'''

    enu_coord=[]
    ##Home Coordinates
    gps_home_lat = 46.9765208 
    gps_home_long = 7.179124
    gps_home_alt = 59

    for i in log:
        enu = map.geodetic2enu(i.loc[:,'latitude'],i.loc[:,'longitude'],i.loc[:,'height'],gps_home_lat,gps_home_long,gps_home_alt)
        i.loc[:,'latitude'] = enu[1]  #north
        i.loc[:,'longitude'] = enu[0] #east
        i.loc[:,'height'] = enu[2]    #up 
        mapping = {i.columns[1]:'north',i.columns[2]:'east',i.columns[3]:'up'}
        p = i.rename(columns = mapping)
        enu_coord.append(p)

    return enu_coord



###########################################################################


####DATA POSTPROCESSING


###########################################################################


###Apply Post-Process Function
avg_real, real_flights = real_post_process(val_flights,10,440,600)
avg_sim, sim_flights = sim_post_process(sim_flights,5,0,400)
avg_compare, compare_flights = sim_post_process(sim_compare,5,200,290)

###Apply GPS to ENU Function
gps_coord = copy.deepcopy([avg_real,avg_sim,waypoints,avg_compare])
enu_coord = gps2enu(gps_coord)
avg_real_enu = enu_coord[0]
avg_sim_enu = enu_coord[1]
waypoints_enu = enu_coord[2]
avg_compare_enu = enu_coord[3]

###Interpolate Coordiantes

# Creates 3 Data Sets (north, east, up) with real, sim and comparison data and
# Interpolates Coordinates as the real and sim flight logs doesn't contain same logging frequency
# Real Data 10Hz, Sim Data 5Hz

##North
north = pd.DataFrame({'real':pd.Series.to_numpy(avg_real_enu.loc[:,'north'])},index=avg_real_enu.loc[:,'time'])
north_sim = pd.DataFrame({'sim':pd.Series.to_numpy(avg_sim_enu.loc[:,'north'])},index=avg_sim_enu.loc[:,'time'])
north_comp = pd.DataFrame({'comp':pd.Series.to_numpy(avg_compare_enu.loc[:,'north'])},index=avg_compare_enu.loc[:,'time'])
north = pd.concat([north,north_sim,north_comp],axis=1)

north['sim'] = north['sim'].interpolate()
north['real'] = north['real'].interpolate()
north['comp'] = north['comp'].interpolate()

##East
east = pd.DataFrame({'real':pd.Series.to_numpy(avg_real_enu.loc[:,'east'])},index=avg_real_enu.loc[:,'time'])
east_sim = pd.DataFrame({'sim':pd.Series.to_numpy(avg_sim_enu.loc[:,'east'])},index=avg_sim_enu.loc[:,'time'])
east_comp = pd.DataFrame({'comp':pd.Series.to_numpy(avg_compare_enu.loc[:,'east'])},index=avg_compare_enu.loc[:,'time'])
east = pd.concat([east,east_sim,east_comp],axis=1)

east['sim'] = east['sim'].interpolate()
east['real'] = east['real'].interpolate()
east['comp'] = east['comp'].interpolate()

##Up
up = pd.DataFrame({'real':pd.Series.to_numpy(avg_real_enu.loc[:,'up'])},index=avg_real_enu.loc[:,'time'])
up_sim = pd.DataFrame({'sim':pd.Series.to_numpy(avg_sim_enu.loc[:,'up'])},index=avg_sim_enu.loc[:,'time'])
up_comp = pd.DataFrame({'comp':pd.Series.to_numpy(avg_compare_enu.loc[:,'up'])},index=avg_compare_enu.loc[:,'time'])
up = pd.concat([up,up_sim,up_comp],axis=1)

up['sim'] = up['sim'].interpolate()
up['real'] = up['real'].interpolate()
up['comp'] = up['comp'].interpolate()




###########################################################################


####RESULTS AND PLOTTINGS


###########################################################################


###Plottings

##North vs. East (2D Plot)

fig = plt.figure()
ax = plt.axes()
ax.plot(avg_real_enu['north'],avg_real_enu['east'],'r--',label = 'Flight Test')
ax.plot(avg_sim_enu['north'],avg_sim_enu['east'],'g',label= 'Simulation')
ax.scatter(waypoints_enu['north'],waypoints_enu['east'],marker='o',color='black')
ax.set_title('Coordinates relative to Waypoint 1')
ax.set_ylabel('Relative Coordinates to the East [m]')
ax.set_xlabel('Relative Coordinates to the North [m]')
ax.legend(loc='upper right')
annotations=["WP-1","WP-2","WP-3","WP-4"]
for i, label in enumerate(annotations):
    plt.text(waypoints_enu['north'][i], waypoints_enu['east'][i],label)
ax.grid()
plt.show()

##North vs. East vs Up (3D Plot)

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot3D(avg_real_enu['north'],avg_real_enu['east'],avg_real['height'],'r--',label='Flight Test')
ax.plot3D(avg_sim_enu['north'],avg_sim_enu['east'],avg_sim['height'],'g',label='Simulation')
ax.scatter(waypoints_enu['north'],waypoints_enu['east'],waypoints['height'],marker='o',color='black')
ax.set_title('Coordinates relative to Waypoint 1')
ax.set_xlabel('North [m]')
ax.set_ylabel('East [m]')
annotations=["WP-1","WP-2","WP-3","WP-4"]
for i, label in enumerate(annotations):
    ax.text(waypoints_enu['north'][i], waypoints_enu['east'][i],waypoints['height'][i],  label, zorder=1)
ax.legend()
plt.show()


##North vs. Time / East vs. Time (1D Plots)


fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

fig.suptitle('Distances relative to Waypoint 1')

ax2.plot(north['real'],'r--',label = 'Flight Test')
ax2.plot(north['sim'],'g',label = 'Simulation')
ax2.plot(north['comp'],'b',alpha = 0.2 ,label = 'Comparison')
ax2.set_xlabel('Time [s]')
ax2.set_ylabel('North [m]')
ax2.legend()
ax2.grid()

ax3.plot(east['real'],'r--',label = 'Flight Test')
ax3.plot(east['sim'],'g',label = 'Simulation')
ax3.plot(east['comp'],'b',alpha = 0.2 ,label = 'Comparison')
ax3.set_xlabel('Time [s]')
ax3.set_ylabel('East [m]')
ax3.grid()

ax1.plot(up['real'],'r--',label = 'Flight Test')
ax1.plot(up['sim'],'g',label = 'Simulation')
ax1.plot(up['comp'],'b',alpha = 0.2 ,label = 'Comparison')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Height [m]')
ax1.grid()

plt.show()


###Distance Errors

err_north = pd.Series.to_numpy(north['real']-north['sim'])
err_east = pd.Series.to_numpy(east['real']-east['sim'])
err_up = pd.Series.to_numpy(up['real']-up['sim'])

err_horizontal = (err_north**2+err_east**2+err_up**2)**0.5

#Plot Horizontal Distance Error
t = pd.Series.to_numpy(north.index)
plot(t,err_horizontal)
plt.show()

#Mean Error Horizontal Distance
mhe = np.mean(err_horizontal)
print(mhe)

#MAPE North 
per_err = (pd.Series.to_numpy(north['real'])-pd.Series.to_numpy(north['sim']))/pd.Series.to_numpy(north['real'])
mape = sum(abs(per_err))/len(per_err)
print(mape)

#MSE North 
sqr_err = (pd.Series.to_numpy(north['real'])-pd.Series.to_numpy(north['sim']))**2
mse = sum(sqr_err)/len(sqr_err)
print(mse)

#Summary
print('Mean horizontal Error:',mhe, 'MAPE:',mape, 'MSE:',mse)






