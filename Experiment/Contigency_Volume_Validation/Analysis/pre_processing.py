######
#Date: 21.12.2022
##Version Log:
#
#
#
######

###Import

import numpy as np
import pandas as pd
import copy
import pymap3d as map
import time

#####---------------------------------------------------------------------------------------------------------------------------------------------------------------

###DATA Import & Pre-Processing Functions

####-----------------------------------------------------------------------------------------------------------------------------------------------------------------

def pre_process(fp_import,flight_plan,start_long,start_lat,start_height,scenario_ID):
    """Function imports the dataset and removes the logged data before reaching the waypoint,
     where the logging should actually start and after the drone crashed on ground."""

    ##Import data using the path of the file given as argument
    data = pd.read_csv(flight_plan, sep=';')

    ##Calculating Distance projected on Flight Path usind ENU coordiantes

    #GPS to ENU conversion
    enu = map.geodetic2enu(data['latitude'],data['longitude'],data['altitude'],start_lat,start_long,start_height)
    data_enu = pd.DataFrame({'north':enu[1], 'east':enu[0],'up':enu[2]})
    
    #If altitude < 45m (absolute not ENU) then latitude & longitued = 1 in order to avoid that max distance is after crash
    data_enu['north']=data_enu['north'].where(data_enu['up']>-5,1) 
    data_enu['east']=data_enu['east'].where(data_enu['up']>-5,1)

    #North, east vector of log data
    vec_2d = np.array([data_enu['north'],data_enu['east']]) #North,East Vector
    vec_2d = vec_2d.transpose()

    #North,East Vector of Fligth Plan
    fp_2d = np.array(fp_import.iloc[1,:])[1:3]
    fp_2d = fp_2d.transpose()

    #Calculate angle between the two vectors
    dot = np.dot(vec_2d,fp_2d)
    vec_2d_len = np.sqrt(np.sum(vec_2d*vec_2d,axis=1))
    fp_2d_len = np.sqrt((fp_2d*fp_2d).sum())
    cos_angle = dot/(vec_2d_len*fp_2d_len)
    angle = np.arccos(cos_angle)
    angle_deg = (angle*180)/np.pi

    #Projected Distance on Flight Path
    dist = vec_2d_len*np.cos(angle)
    dist = dist.reshape(dist.shape[0],1)

    #Index of Max Distance allows to start the iteration to find idx_stop which marks kill-switch (end of the experiment)
    idx_max = np.argmax(np.max(dist, axis=1))

    #Calculating Min Index, which allows to find start index (index when experiment begins)
    distance_3d = np.sqrt(data_enu['north']**2+data_enu['east']**2+data_enu['up']**2)
    idx_min = distance_3d.idxmin(axis=0)


    ##Calculating Start Index

    #Calculating speed through integral of position (slope of position --> speed)
    slope_num = dist[1:dist.shape[0]]-dist[0:(dist.shape[0]-1)]
    slope_num = slope_num.reshape(slope_num.shape[0],1)
    log_time = np.array(data.loc[:,'pos_time'])
    slope_denum = log_time[1:log_time.shape[0]]-log_time[0:(log_time.shape[0]-1)]
    slope_denum = slope_denum.reshape(slope_denum.shape[0],1)
    slope = np.divide(slope_num,slope_denum)
    #If slope > 1 speed above 1 m/s --> experiment has started
    slope = np.where(slope>1,1,0)
    idx_start = np.argmax(np.min(slope, axis=1)) #Start index


    ##Calculating Stop Index
    for i in range(idx_max,len(data)-1):
        if np.abs(data.loc[i,'altitude']-start_height) > 2.0:
            idx_stop = i-2 #Row index of crash
            break
        else:
            continue

    ##Pruning the data set to start/stop index and renaming columns to unique run name.
    pre_data = data.loc[idx_start:idx_stop,'latitude':'altitude']
    pre_data = copy.deepcopy(pre_data.rename(columns={"latitude":scenario_ID+"_lat", "longitude":scenario_ID+"_long","altitude":scenario_ID+"_height"}))

    pre_data_time = data.loc[idx_start:idx_stop,'pos_time']

    return pre_data, pre_data_time



###----------------------------------------------------------------------------------------------------------------------------------------------------------------
def import_data(scenario,run_nr,location,flight_mode,coordinates,fp_ENU,reaction):
    """This function iterates through the different scenarios while using the pre_process function for importing and pre-processing the data.
    The pre-processed data is saved into a dictionary. One entry exists for each location (see experimental design).
     Each entry contains a data frame with the logged data for every wind setup and run number."""

    ##Dictionary to save the data frames
    imported = {}
    imported_time = {}
    
    ##Iteration through different locations
    for j in location:

        DATA = pd.DataFrame() #Data frame to save the data from one location
        DATA_TIME= pd.DataFrame()
        fp_import = fp_ENU[j]

        ##Iteration through wind setups
        for i in range(0,len(scenario),1):
            ##Iteration through runs per wind setup
            for k in range(1,run_nr+1,1):

                ##Creating input arguments for pre-processing function
                scenario_ID = scenario[i]+'_'+'Run_'+str(k) #Unique scenario name consists of wind setup + run number
                flight_plan = copy.deepcopy('../Flight_Logs/'+flight_mode+'/'+j+'_'+reaction+'/'+scenario_ID+'.csv') #Path to log file
                start_long = coordinates[j][1]
                start_lat = coordinates[j][0]
                start_height = coordinates[j][2]

                ##Call of pre_process function and merging existing data frame with new one. Adding new log data
                DATA_NEW, DATA_NEW_TIME = pre_process(fp_import,flight_plan,start_long,start_lat,start_height,scenario_ID)
                DATA_NEW_TIME = pd.DataFrame(DATA_NEW_TIME)
                DATA_NEW_TIME.rename(columns={'pos_time':scenario_ID},inplace=True)
                DATA_NEW_TIME = DATA_NEW_TIME-DATA_NEW_TIME.min()
                DATA=pd.concat([DATA,DATA_NEW],axis=1,ignore_index = False)
                DATA_TIME=pd.concat([DATA_TIME,DATA_NEW_TIME],axis=1,ignore_index = False)
                DATA= DATA.sort_index(ascending=True)
                DATA_TIME= DATA_TIME.sort_index(ascending=True)

        ##Add data frame from location to dictionary    
        imported.update({j:DATA})
        imported_time.update({j:DATA_TIME})

    return imported,imported_time


###----------------------------------------------------------------------------------------------------------------------------------------------------------------
def gps2enu(DATA,coordinates):
    '''Turn GPS Coordinates in ENU coordinates. The function uses the gps coordinates as input
     and calulates the ENU coordinates for the three different locations according to experimental desing'''

    enu_coord={}

    for i in coordinates.keys():
        ##Start Coordinates
        gps_home_lat = coordinates[i][0]
        gps_home_long = coordinates[i][1]
        gps_home_alt = coordinates[i][2]-coordinates[i][2]
        
        j = copy.deepcopy(pd.DataFrame(DATA[i]))
        for k in range(0,len(j.columns),3):
            enu = map.geodetic2enu(j.iloc[:,k],j.iloc[:,k+1],j.iloc[:,k+2],gps_home_lat,gps_home_long,gps_home_alt)
            j.iloc[:,k] =  enu[1]  #north
            j.iloc[:,k+1] = enu[0] #east
            j.iloc[:,k+2] = enu[2] #up

        colnames = list(j.columns.values)
        for l in range(0,len(colnames)):
            colnames[l] = colnames[l].replace('lat','north')
            colnames[l] = colnames[l].replace('long','east')
            colnames[l] = colnames[l].replace('height','up')

        j.columns = colnames
        enu_coord.update({i:j})

    return enu_coord

###----------------------------------------------------------------------------------------------------------------------------------------------------------------
def flightplan2enu(DATA,coordinates):
    '''Turn GPS Coordinates in ENU coordinates. The function uses the gps coordinates as input
     and calulates the ENU coordinates for the three different locations according to experimental desing'''

    enu_coord={}

    for i in coordinates.keys():
        ##Start Coordinates
        gps_home_lat = coordinates[i][0]
        gps_home_long = coordinates[i][1]
        gps_home_alt = coordinates[i][2]-coordinates[i][2]
        
        j = copy.deepcopy(pd.DataFrame(DATA[i]))
        j.iloc[:,3]=0
        # for k in range(0,len(j),1):
        #     enu = map.geodetic2enu(j.iloc[k,1],j.iloc[k,2],j.iloc[k,3],gps_home_lat,gps_home_long,gps_home_alt)
        #     j.iloc[:,k] =  enu[1]  #north
        #     j.iloc[:,k+1] = enu[0] #east
        #     j.iloc[:,k+2] = enu[2] #up
        enu = map.geodetic2enu(j.iloc[:,1],j.iloc[:,2],j.iloc[:,3],gps_home_lat,gps_home_long,gps_home_alt)
        j.iloc[:,1] =  enu[1]  #north
        j.iloc[:,2] = enu[0] #east
        j.iloc[:,3] = enu[2] #up

        colnames = list(j.columns.values)
        for l in range(0,len(colnames)):
            colnames[l] = colnames[l].replace('lat','north')
            colnames[l] = colnames[l].replace('long','east')
            colnames[l] = colnames[l].replace('alt','up')

        j.columns = colnames
        enu_coord.update({i:j})

    return enu_coord

###----------------------------------------------------------------------------------------------------------------------------------------------------------------
def geofence2enu(geofence,coordinates):
    '''Turn GPS Coordinates of the geofence are into ENU coordinates'''

    geofence.iloc[:,3] = 0 #Adding 0 to altitude to avoid later errors
    geofence = geofence.iloc[:,1:4] #Removing ID column

    geofence_enu = {}

    for i in coordinates.keys():
        # ##Start Coordinates
        gps_home_lat = coordinates[i][0]
        gps_home_long = coordinates[i][1]
        gps_home_alt = coordinates[i][2]-coordinates[i][2]
        
        j = copy.deepcopy(geofence)
        enu = map.geodetic2enu(geofence.iloc[:,0],geofence.iloc[:,1],geofence.iloc[:,2],gps_home_lat,gps_home_long,gps_home_alt)
        j.iloc[:,0] =  enu[1]  #north
        j.iloc[:,1] = enu[0] #east
        j.iloc[:,2] = enu[2] #up

        colnames = list(j.columns.values)
        for l in range(0,len(colnames)):
            colnames[l] = colnames[l].replace('lat','north')
            colnames[l] = colnames[l].replace('long','east')
            colnames[l] = colnames[l].replace('alt','up')

        j.columns = colnames
        geofence_enu.update({i:j})
    
    return geofence_enu


###----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print('hello')