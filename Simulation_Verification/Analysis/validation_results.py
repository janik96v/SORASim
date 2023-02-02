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
val_data1 = pd.read_csv('../Flight_Logs/Flight_Test/DJIFlightRecord_2022-08-25_[10-38-43].csv', sep=',')
val_data2 = pd.read_csv('../Flight_Logs/Flight_Test/DJIFlightRecord_2022-08-25_[10-42-05].csv', sep=',')
val_data3 = pd.read_csv('../Flight_Logs/Flight_Test/DJIFlightRecord_2022-08-25_[10-45-30].csv', sep=',')
val_flights = [val_data1,val_data2,val_data3]

##Simulation Data
sim_data1 = pd.read_csv('../Flight_Logs/Simulation/verification_final1.csv', sep=';')
sim_data2 = pd.read_csv('../Flight_Logs/Simulation/verification_final2.csv', sep=';')
sim_data3 = pd.read_csv('../Flight_Logs/Simulation/verification_final3.csv', sep=';')

# sim_datatest = pd.read_csv('Validation/validation_test.csv', sep=';') #Only for test flight data
# sim_datatest= sim_datatest.iloc[:,1:] #Only for test flight data

#Removing first line (Time)
sim_data1 = sim_data1.iloc[:,1:]
sim_data2 = sim_data2.iloc[:,1:]
sim_data3 = sim_data3.iloc[:,1:]
sim_flights = [sim_data1,sim_data2,sim_data3]

# sim_flights = [sim_datatest,sim_datatest,sim_datatest] #Only for test flight data

##Simulation Data before Model Tuning
sim_data_comparison = pd.read_csv('../Flight_Logs/Simulation/verification_no_adjustments.csv', sep=';')
sim_data_comparison2 = pd.read_csv('../Flight_Logs/Simulation/verification_no_adjustments2.csv', sep=';')
sim_data_comparison3 = pd.read_csv('../Flight_Logs/Simulation/verification_no_adjustments3.csv', sep=';')
sim_data_comparison = sim_data_comparison.iloc[:,1:]
sim_data_comparison2 = sim_data_comparison2.iloc[:,1:]
sim_data_comparison3 = sim_data_comparison3.iloc[:,1:]
sim_compare = [sim_data_comparison,sim_data_comparison2,sim_data_comparison3]

##Waypoints
waypoints = pd.read_excel('../Script/Flight_Plans/Flight_Plan.xlsx')
waypoints = waypoints.iloc[0:waypoints.shape[0]-1,:]
waypoints = waypoints.rename(columns={waypoints.columns[1]:'latitude',waypoints.columns[2]:'longitude',waypoints.columns[3]:'height'})

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


####RESULT: FLIGHT PAHT PLOTTINGS


###########################################################################


###Plottings

##North vs. East (2D Plot)

fig = plt.figure()
ax = plt.axes()
ax.plot(avg_real_enu['north'],avg_real_enu['east'],'r--',label = 'Flight Test')
ax.plot(avg_sim_enu['north'],avg_sim_enu['east'],'g',label= 'Simulation')
ax.scatter(waypoints_enu['north'],waypoints_enu['east'],marker='o',color='black')
ax.set_title('Coordinates relative to Waypoint 1')
ax.set_ylabel('East [m]')
ax.set_xlabel('North [m]')
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

fig.suptitle('ENU coordinates with respect to time')

ax2.plot(north['real'],'r--',label = 'Flight Test')
ax2.plot(north['sim'],'g',label = 'Simulation')
ax2.plot(north['comp'],'b',alpha = 0.2 ,label = 'Unadjusted')
ax2.set_xlabel('Time [s]')
ax2.set_ylabel('North [m]')
ax2.legend()
ax2.grid()

ax3.plot(east['real'],'r--',label = 'Flight Test')
ax3.plot(east['sim'],'g',label = 'Simulation')
ax3.plot(east['comp'],'b',alpha = 0.2 ,label = 'Unadjusted')
ax3.set_xlabel('Time [s]')
ax3.set_ylabel('East [m]')
ax3.grid()

ax1.plot(up['real'],'r--',label = 'Flight Test')
ax1.plot(up['sim'],'g',label = 'Simulation')
ax1.plot(up['comp'],'b',alpha = 0.2 ,label = 'Unadjusted')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Height [m]')
ax1.grid()

plt.show()



###########################################################################


####RESULTS: RUN VARIATION INCLUDING PLOTS AND ERROR EVALUATION


###########################################################################


###Run Variation

# Analysis the amount of variation between the 3 runs. Performs post processing of the data and plottings.
# Some Data must be post processed as the post processing before mainly focuses on the averaged data where
# here each run must be post processed as well.

##Turn each run from GPS to ENU coordinates
gps_home_lat = 46.9765208 
gps_home_long = 7.179124
gps_home_alt = 59

enu_real1= map.geodetic2enu(real_flights.loc[:,1],real_flights.loc[:,2],real_flights.loc[:,3],gps_home_lat,gps_home_long,gps_home_alt)
enu_real2= map.geodetic2enu(real_flights.loc[:,6],real_flights.loc[:,7],real_flights.loc[:,8],gps_home_lat,gps_home_long,gps_home_alt)
enu_real3= map.geodetic2enu(real_flights.loc[:,11],real_flights.loc[:,12],real_flights.loc[:,13],gps_home_lat,gps_home_long,gps_home_alt)

enu_sim1= map.geodetic2enu(sim_flights.loc[:,2],sim_flights.loc[:,3],sim_flights.loc[:,4],gps_home_lat,gps_home_long,gps_home_alt)
enu_sim2= map.geodetic2enu(sim_flights.loc[:,10],sim_flights.loc[:,11],sim_flights.loc[:,12],gps_home_lat,gps_home_long,gps_home_alt)
enu_sim3= map.geodetic2enu(sim_flights.loc[:,18],sim_flights.loc[:,19],sim_flights.loc[:,20],gps_home_lat,gps_home_long,gps_home_alt)

enu_comp1= map.geodetic2enu(compare_flights.loc[:,2],compare_flights.loc[:,3],compare_flights.loc[:,4],gps_home_lat,gps_home_long,gps_home_alt)
enu_comp2= map.geodetic2enu(compare_flights.loc[:,10],compare_flights.loc[:,11],compare_flights.loc[:,12],gps_home_lat,gps_home_long,gps_home_alt)
enu_comp3= map.geodetic2enu(compare_flights.loc[:,18],compare_flights.loc[:,19],compare_flights.loc[:,20],gps_home_lat,gps_home_long,gps_home_alt)


##Interpolation and Creation of North, East, Up data sets

#North Interpolation
north_sens =pd.DataFrame({'real':pd.Series.to_numpy(avg_real_enu.loc[:,'north'])},index=avg_real_enu.loc[:,'time'])
north1 = pd.DataFrame({'north1':pd.Series.to_numpy(enu_real1[1])},index=real_flights.loc[:,0])
north2 = pd.DataFrame({'north2':pd.Series.to_numpy(enu_real2[1])},index=real_flights.loc[:,0])
north3 = pd.DataFrame({'north3':pd.Series.to_numpy(enu_real3[1])},index=real_flights.loc[:,0])
north_avg_sim = pd.DataFrame({'sim':pd.Series.to_numpy(avg_sim_enu.loc[:,'north'])},index=avg_sim_enu.loc[:,'time'])
north1_sim = pd.DataFrame({'north1_sim':pd.Series.to_numpy(enu_sim1[1])},index=sim_flights.loc[:,0])
north2_sim = pd.DataFrame({'north2_sim':pd.Series.to_numpy(enu_sim2[1])},index=sim_flights.loc[:,0])
north3_sim = pd.DataFrame({'north3_sim':pd.Series.to_numpy(enu_sim3[1])},index=sim_flights.loc[:,0])
north_avg_comp = pd.DataFrame({'comp':pd.Series.to_numpy(avg_compare_enu.loc[:,'north'])},index=avg_compare_enu.loc[:,'time'])
north1_comp = pd.DataFrame({'north1_comp':pd.Series.to_numpy(enu_comp1[1])},index=compare_flights.loc[:,0])
north2_comp = pd.DataFrame({'north2_comp':pd.Series.to_numpy(enu_comp2[1])},index=compare_flights.loc[:,0])
north3_comp = pd.DataFrame({'north3_comp':pd.Series.to_numpy(enu_comp3[1])},index=compare_flights.loc[:,0])
north_sens = pd.concat([north_sens,north1,north2,north3,north_avg_sim,north1_sim,north2_sim,north3_sim,north_avg_comp,north1_comp,north2_comp,north3_comp],axis=1)

north_sens['real'] = north_sens['real'].interpolate()
north_sens['sim'] = north_sens['sim'].interpolate()
north_sens['comp'] = north_sens['comp'].interpolate()
north_sens['north1_sim'] = north_sens['north1_sim'].interpolate()
north_sens['north2_sim'] = north_sens['north2_sim'].interpolate()
north_sens['north3_sim'] = north_sens['north3_sim'].interpolate()
north_sens['north1'] = north_sens['north1'].interpolate()
north_sens['north2'] = north_sens['north2'].interpolate()
north_sens['north3'] = north_sens['north3'].interpolate()
north_sens['north1_comp'] = north_sens['north1_comp'].interpolate()
north_sens['north2_comp'] = north_sens['north2_comp'].interpolate()
north_sens['north3_comp'] = north_sens['north3_comp'].interpolate()

#East Interpolation
east_sens =pd.DataFrame({'real':pd.Series.to_numpy(avg_real_enu.loc[:,'east'])},index=avg_real_enu.loc[:,'time'])
east1 = pd.DataFrame({'east1':pd.Series.to_numpy(enu_real1[0])},index=real_flights.loc[:,0])
east2 = pd.DataFrame({'east2':pd.Series.to_numpy(enu_real2[0])},index=real_flights.loc[:,0])
east3 = pd.DataFrame({'east3':pd.Series.to_numpy(enu_real3[0])},index=real_flights.loc[:,0])
east_avg_sim = pd.DataFrame({'sim':pd.Series.to_numpy(avg_sim_enu.loc[:,'east'])},index=avg_sim_enu.loc[:,'time'])
east1_sim = pd.DataFrame({'east1_sim':pd.Series.to_numpy(enu_sim1[0])},index=sim_flights.loc[:,0])
east2_sim = pd.DataFrame({'east2_sim':pd.Series.to_numpy(enu_sim2[0])},index=sim_flights.loc[:,0])
east3_sim = pd.DataFrame({'east3_sim':pd.Series.to_numpy(enu_sim3[0])},index=sim_flights.loc[:,0])
east_avg_comp = pd.DataFrame({'comp':pd.Series.to_numpy(avg_compare_enu.loc[:,'east'])},index=avg_compare_enu.loc[:,'time'])
east1_comp = pd.DataFrame({'east1_comp':pd.Series.to_numpy(enu_comp1[0])},index=compare_flights.loc[:,0])
east2_comp = pd.DataFrame({'east2_comp':pd.Series.to_numpy(enu_comp2[0])},index=compare_flights.loc[:,0])
east3_comp = pd.DataFrame({'east3_comp':pd.Series.to_numpy(enu_comp3[0])},index=compare_flights.loc[:,0])
east_sens = pd.concat([east_sens,east1,east2,east3,east_avg_sim,east1_sim,east2_sim,east3_sim,east_avg_comp,east1_comp,east2_comp,east3_comp],axis=1)

east_sens['real'] = east_sens['real'].interpolate()
east_sens['sim'] = east_sens['sim'].interpolate()
east_sens['comp'] = east_sens['comp'].interpolate()
east_sens['east1_sim'] = east_sens['east1_sim'].interpolate()
east_sens['east2_sim'] = east_sens['east2_sim'].interpolate()
east_sens['east3_sim'] = east_sens['east3_sim'].interpolate()
east_sens['east1'] = east_sens['east1'].interpolate()
east_sens['east2'] = east_sens['east2'].interpolate()
east_sens['east3'] = east_sens['east3'].interpolate()
east_sens['east1_comp'] = east_sens['east1_comp'].interpolate()
east_sens['east2_comp'] = east_sens['east2_comp'].interpolate()
east_sens['east3_comp'] = east_sens['east3_comp'].interpolate()

#Up Interpolation
up_sens =pd.DataFrame({'real':pd.Series.to_numpy(avg_real_enu.loc[:,'up'])},index=avg_real_enu.loc[:,'time'])
up1 = pd.DataFrame({'up1':pd.Series.to_numpy(enu_real1[2])},index=real_flights.loc[:,0])
up2 = pd.DataFrame({'up2':pd.Series.to_numpy(enu_real2[2])},index=real_flights.loc[:,0])
up3 = pd.DataFrame({'up3':pd.Series.to_numpy(enu_real3[2])},index=real_flights.loc[:,0])
up_avg_sim = pd.DataFrame({'sim':pd.Series.to_numpy(avg_sim_enu.loc[:,'up'])},index=avg_sim_enu.loc[:,'time'])
up1_sim = pd.DataFrame({'up1_sim':pd.Series.to_numpy(enu_sim1[2])},index=sim_flights.loc[:,0])
up2_sim = pd.DataFrame({'up2_sim':pd.Series.to_numpy(enu_sim2[2])},index=sim_flights.loc[:,0])
up3_sim = pd.DataFrame({'up3_sim':pd.Series.to_numpy(enu_sim3[2])},index=sim_flights.loc[:,0])
up_avg_comp = pd.DataFrame({'comp':pd.Series.to_numpy(avg_compare_enu.loc[:,'up'])},index=avg_compare_enu.loc[:,'time'])
up1_comp = pd.DataFrame({'up1_comp':pd.Series.to_numpy(enu_comp1[2])},index=compare_flights.loc[:,0])
up2_comp = pd.DataFrame({'up2_comp':pd.Series.to_numpy(enu_comp2[2])},index=compare_flights.loc[:,0])
up3_comp = pd.DataFrame({'up3_comp':pd.Series.to_numpy(enu_comp3[2])},index=compare_flights.loc[:,0])
up_sens = pd.concat([up_sens,up1,up2,up3,up_avg_sim,up1_sim,up2_sim,up3_sim,up_avg_comp,up1_comp,up2_comp,up3_comp],axis=1)


up_sens['real'] = up_sens['real'].interpolate()
up_sens['sim'] = up_sens['sim'].interpolate()
up_sens['comp'] = up_sens['comp'].interpolate()
up_sens['up1_sim'] = up_sens['up1_sim'].interpolate()
up_sens['up2_sim'] = up_sens['up2_sim'].interpolate()
up_sens['up3_sim'] = up_sens['up3_sim'].interpolate()
up_sens['up1'] = up_sens['up1'].interpolate()
up_sens['up2'] = up_sens['up2'].interpolate()
up_sens['up3'] = up_sens['up3'].interpolate()
up_sens['up1_comp'] = up_sens['up1_comp'].interpolate()
up_sens['up2_comp'] = up_sens['up2_comp'].interpolate()
up_sens['up3_comp'] = up_sens['up3_comp'].interpolate()


##Distance Analysis between Mean and Run (3D Distance Deviation from Mean)

sd1 = np.std(((north_sens['real']-north_sens['north1'])**2+(east_sens['real']-east_sens['east1'])**2+(up_sens['real']-up_sens['up1'])**2)**0.5)
sd2 = np.std(((north_sens['real']-north_sens['north2'])**2+(east_sens['real']-east_sens['east2'])**2+(up_sens['real']-up_sens['up2'])**2)**0.5)
sd3 = np.std(((north_sens['real']-north_sens['north3'])**2+(east_sens['real']-east_sens['east3'])**2+(up_sens['real']-up_sens['up3'])**2)**0.5)
sd_real = (sd1+sd2+sd3)/3

mean1 = np.mean(((north_sens['real']-north_sens['north1'])**2+(east_sens['real']-east_sens['east1'])**2+(up_sens['real']-up_sens['up1'])**2)**0.5)
mean2 = np.mean(((north_sens['real']-north_sens['north2'])**2+(east_sens['real']-east_sens['east2'])**2+(up_sens['real']-up_sens['up2'])**2)**0.5)
mean3 = np.mean(((north_sens['real']-north_sens['north3'])**2+(east_sens['real']-east_sens['east3'])**2+(up_sens['real']-up_sens['up3'])**2)**0.5)


sd1_sim = np.std(((north_sens['sim']-north_sens['north1_sim'])**2+(east_sens['sim']-east_sens['east1_sim'])**2+(up_sens['sim']-up_sens['up1_sim'])**2)**0.5)
sd2_sim = np.std(((north_sens['sim']-north_sens['north2_sim'])**2+(east_sens['sim']-east_sens['east2_sim'])**2+(up_sens['sim']-up_sens['up2_sim'])**2)**0.5)
sd3_sim = np.std(((north_sens['sim']-north_sens['north3_sim'])**2+(east_sens['sim']-east_sens['east3_sim'])**2+(up_sens['sim']-up_sens['up3_sim'])**2)**0.5)
sd_sim = (sd1_sim+sd2_sim+sd3_sim)/3

mean1_sim = np.mean(((north_sens['sim']-north_sens['north1_sim'])**2+(east_sens['sim']-east_sens['east1_sim'])**2+(up_sens['sim']-up_sens['up1_sim'])**2)**0.5)
mean2_sim = np.mean(((north_sens['sim']-north_sens['north2_sim'])**2+(east_sens['sim']-east_sens['east2_sim'])**2+(up_sens['sim']-up_sens['up2_sim'])**2)**0.5)
mean3_sim = np.mean(((north_sens['sim']-north_sens['north3_sim'])**2+(east_sens['sim']-east_sens['east3_sim'])**2+(up_sens['sim']-up_sens['up3_sim'])**2)**0.5)


sd1_comp = np.std(((north_sens['comp']-north_sens['north1_comp'])**2+(east_sens['comp']-east_sens['east1_comp'])**2+(up_sens['comp']-up_sens['up1_comp'])**2)**0.5)
sd2_comp = np.std(((north_sens['comp']-north_sens['north2_comp'])**2+(east_sens['comp']-east_sens['east2_comp'])**2+(up_sens['comp']-up_sens['up2_comp'])**2)**0.5)
sd3_comp = np.std(((north_sens['comp']-north_sens['north3_comp'])**2+(east_sens['comp']-east_sens['east3_comp'])**2+(up_sens['comp']-up_sens['up3_comp'])**2)**0.5)

mean1_comp = np.mean(((north_sens['comp']-north_sens['north1_comp'])**2+(east_sens['comp']-east_sens['east1_comp'])**2+(up_sens['comp']-up_sens['up1_comp'])**2)**0.5)
mean2_comp = np.mean(((north_sens['comp']-north_sens['north2_comp'])**2+(east_sens['comp']-east_sens['east2_comp'])**2+(up_sens['comp']-up_sens['up2_comp'])**2)**0.5)
mean3_comp = np.mean(((north_sens['comp']-north_sens['north3_comp'])**2+(east_sens['comp']-east_sens['east3_comp'])**2+(up_sens['comp']-up_sens['up3_comp'])**2)**0.5)

run_dev = pd.DataFrame(
  {
    'mean_real':    [mean1,mean2,mean3],
    'sd_real':      [sd1,sd2,sd3],
    'mean_sim':     [mean1_sim,mean2_sim,mean3_sim],
    'sd_sim':       [sd1_sim,sd2_sim,sd3_sim],
    'mean_comp':    [mean1_comp,mean2_comp,mean3_comp],
    'sd_comp':      [sd1_comp, sd2_comp, sd3_comp]

  }, 
  index=['run1','run2','run3']
)

## Plotting of the Standard Deviation
fig, ax1 = plt.subplots()

barwidth = 0.25

r1 = [1,2,3]
r2 = [x + barwidth for x in r1]
r3 = [x - 2*barwidth for x in r2]

ax1.bar(r1, run_dev['sd_real'], width=barwidth, alpha=0.5, color='r',label = 'Flight Test')
ax1.bar(r2, run_dev['sd_sim'], width=barwidth, alpha=0.5, color='g',label = 'Simulation')
ax1.bar(r3, run_dev['sd_comp'], width=barwidth, alpha=0.5, color='b',label = 'Unadjusted')

ax1.set_ylabel('Standard Deviation [m]')
ax1.set_title('3D distance deviation between runs and run mean')
ax1.legend(loc = 'upper right')
ax1.axes.set_xticks(r1, ['Run 1','Run 2','Run 3'])
plt.show()

## Plotting Run Deviation from the mean including the 95% confidence interval over all runs

#Standard Deviation over all 3 runs for ENU coordinates (Sim & Real)
error_sd_east = (np.std(east_sens['real']-east_sens['east1'])+np.std(east_sens['real']-east_sens['east2'])+np.std(east_sens['real']-east_sens['east3']))/3
error_sd_east_sim = (np.std(east_sens['sim']-east_sens['east1_sim'])+np.std(east_sens['sim']-east_sens['east2_sim'])+np.std(east_sens['sim']-east_sens['east3_sim']))/3
error_sd_north = (np.std(north_sens['real']-north_sens['north1'])+np.std(north_sens['real']-north_sens['north2'])+np.std(north_sens['real']-north_sens['north3']))/3
error_sd_north_sim = (np.std(north_sens['sim']-north_sens['north1_sim'])+np.std(north_sens['sim']-north_sens['north2_sim'])+np.std(north_sens['sim']-north_sens['north3_sim']))/3
error_sd_up = (np.std(up_sens['real']-up_sens['up1'])+np.std(up_sens['real']-up_sens['up2'])+np.std(up_sens['real']-up_sens['up3']))/3
error_sd_up_sim = (np.std(up_sens['sim']-up_sens['up1_sim'])+np.std(up_sens['sim']-up_sens['up2_sim'])+np.std(up_sens['sim']-up_sens['up3_sim']))/3

#Plot
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

fig.suptitle('Deviations from mean, including 95% confidence intervall')

ax2.plot(north_sens['real']-north_sens['north1'],'r',alpha = 0.5, label = 'Flight Test')
ax2.plot(north_sens['real']-north_sens['north2'],'r',alpha = 0.3)
ax2.plot(north_sens['real']-north_sens['north3'],'r',alpha = 0.1)
ax2.fill_between(north_sens.index,(north_sens['real']-north_sens['real']+2*error_sd_north),(north_sens['real']-north_sens['real']-2*error_sd_north),color='r',alpha=0.1)
ax2.plot(north_sens['sim']-north_sens['north1_sim'],'g',alpha = 0.5, label = 'Simulation')
ax2.plot(north_sens['sim']-north_sens['north2_sim'],'g',alpha = 0.3)
ax2.plot(north_sens['sim']-north_sens['north3_sim'],'g',alpha = 0.1)
ax2.fill_between(north_sens.index,(north_sens['sim']-north_sens['sim']+2*error_sd_north_sim),(north_sens['sim']-north_sens['sim']-2*error_sd_north_sim),color='g',alpha=0.2)
ax2.set_xlabel('Time [s]')
ax2.set_ylabel('North [m]')
ax2.set_ylim([-3,3])
ax2.grid()

ax3.plot(east_sens['real']-east_sens['east1'],'r',alpha = 0.5, label = 'Flight Test')
ax3.plot(east_sens['real']-east_sens['east2'],'r',alpha = 0.3)
ax3.plot(east_sens['real']-east_sens['east3'],'r',alpha = 0.1)
ax3.fill_between(east_sens.index,(east_sens['real']-east_sens['real']+2*error_sd_east),(east_sens['real']-east_sens['real']-2*error_sd_east),color='r',alpha=0.1)
ax3.plot(east_sens['sim']-east_sens['east1_sim'],'g',alpha = 0.5, label = 'Simulation')
ax3.plot(east_sens['sim']-east_sens['east2_sim'],'g',alpha = 0.3)
ax3.plot(east_sens['sim']-east_sens['east3_sim'],'g',alpha = 0.1)
ax3.fill_between(east_sens.index,(east_sens['sim']-east_sens['sim']+2*error_sd_east_sim),(east_sens['sim']-east_sens['sim']-2*error_sd_east_sim),color='g',alpha=0.2)
ax3.set_xlabel('Time [s]')
ax3.set_ylabel('East [m]')
ax3.set_ylim([-3,3])
ax3.grid()

ax1.plot(up_sens['real']-up_sens['up1'],'r',alpha = 0.5, label = 'Flight Test')
ax1.plot(up_sens['real']-up_sens['up2'],'r',alpha = 0.3)
ax1.plot(up_sens['real']-up_sens['up3'],'r',alpha = 0.1)
ax1.fill_between(up_sens.index,(up_sens['real']-up_sens['real']+2*error_sd_up),(up_sens['real']-up_sens['real']-2*error_sd_up),color='r',alpha=0.1)
ax1.plot(up_sens['sim']-up_sens['up1_sim'],'g',alpha = 0.5, label = 'Simulation')
ax1.plot(up_sens['sim']-up_sens['up2_sim'],'g',alpha = 0.3)
ax1.plot(up_sens['sim']-up_sens['up3_sim'],'g',alpha = 0.1)
ax1.fill_between(up_sens.index,(up_sens['sim']-up_sens['sim']+2*error_sd_up_sim),(up_sens['sim']-up_sens['sim']-2*error_sd_up_sim),color='g',alpha=0.2)
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Height [m]')
ax1.legend()
ax1.grid()

plt.show()


##3D Distance Deviation (real vs sim) incl. 95% confidence intervall

err = ((north['real']-north['sim'])**2+(east['real']-east['sim'])**2+(up['real']-up['sim'])**2)**0.5
sd_err = np.sqrt(sd_real**2+(-sd_sim)**2)

#North vs. Time / East vs. Time / Up vs. Tim / Distance Error (1D Plots)

fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1)

fig.suptitle('ENU coordinates and spatial difference')

ax2.plot(north['real'],'r--',label = 'Flight Test')
ax2.plot(north['sim'],'g',label = 'Simulation')
ax2.set_xlabel('Time [s]')
ax2.set_ylabel('North [m]')
ax2.grid()

ax3.plot(east['real'],'r--',label = 'Flight Test')
ax3.plot(east['sim'],'g',label = 'Simulation')
ax3.set_xlabel('Time [s]')
ax3.set_ylabel('East [m]')
ax3.grid()

ax1.plot(up['real'],'r--',label = 'Flight Test')
ax1.plot(up['sim'],'g',label = 'Simulation')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Height [m]')
ax1.legend()
ax1.grid()

ax4.plot(err.index,err,'r')
ax4.plot(err.index,np.zeros(np.shape(err.index)[0]),color='black')
ax4.fill_between(err.index,(err+2*(sd_err)),(err-2*(sd_err)),color='r',alpha = 0.2)
ax4.set_xlabel('Time [s]')
ax4.set_ylabel('Difference [m]')
ax4.grid()

plt.show()


##Distance Errors

#Mean Error Spacial Distance (MAE)

actual = ((north['real'])**2+(east['real'])**2+(up['real'])**2)**0.5
simulated = ((north['sim'])**2+(east['sim'])**2+(up['sim'])**2)**0.5

mae = np.mean(np.abs(actual-simulated))
print(mae)

#MAPE 
per_err = (pd.Series.to_numpy(actual)-pd.Series.to_numpy(simulated))/pd.Series.to_numpy(actual)
mape = (sum(abs(per_err))/len(per_err))*100
print(mape)

#SDMAE

sdmae = (mae/np.std(actual))*100
print(sdmae)

#MSE 
sqr_err = (pd.Series.to_numpy(actual)-pd.Series.to_numpy(simulated))**2
mse = sum(sqr_err)/len(sqr_err)
print(mse)

#Summary
print('MAE:',mae, 'MAPE:',mape, 'MSE:',mse, 'SDMAE', sdmae)

sd_literature = np.std(np.array([99.46,99.03,98.78,98.69,99.72,100.25,100.17,98.61,99.84,99.3])/3.33)


