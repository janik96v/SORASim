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

def pre_process(flight_plan,start_long,start_lat,start_height,scenario_ID):
    """Function imports the dataset and removes the logged data before reaching the waypoint,
     where the logging should actually start and after the drone crashed on ground."""

    ##Import data using the path of the file given as argument
    data = pd.read_csv(flight_plan, sep=';')
    ##Estimating coordinates closest to start waypoint
    lat = data.loc[:,'latitude']-start_lat
    long = data.loc[:,'longitude']-start_long
    height = data.loc[:,'altitude']-start_height

    if start_height>50:
        idx_best = np.sqrt(lat**2+long**2)
    else:
        idx_best = np.sqrt(lat**2+long**2+height**2)
        
    idx_start = idx_best.idxmin(axis=0) #Row index with distance closest to waypoint

    for i in range(150,len(data)-1):
        if data.loc[i,'altitude'] < 1.5:
            idx_stop = i #Row index of crash
            break
        else:
            continue

    ##Pruning the data set to start/stop index and renaming columns to unique run name.
    pre_data = data.loc[idx_start:idx_stop,'latitude':'altitude']
    pre_data = copy.deepcopy(pre_data.rename(columns={"latitude":scenario_ID+"_lat", "longitude":scenario_ID+"_long","altitude":scenario_ID+"_height"}))

    return(pre_data)


###----------------------------------------------------------------------------------------------------------------------------------------------------------------
def import_data(scenario,run_nr,location,coordinates):
    """This function iterates through the different scenarios while using the pre_process function for importing and pre-processing the data.
    The pre-processed data is saved into a dictionary. One entry exists for each location (see experimental design).
     Each entry contains a data frame with the logged data for every wind setup and run number."""

    ##Dictionary to save the data frames
    imported = {}
    
    ##Iteration through different locations
    for j in location:

        DATA = pd.DataFrame() #Data frame to save the data from one location

        ##Iteration through wind setups
        for i in range(0,len(scenario),1):
            ##Iteration through runs per wind setup
            for k in range(1,run_nr+1,1):

                ##Creating input arguments for pre-processing function
                scenario_ID = scenario[i]+'_'+'Run_'+str(k) #Unique scenario name consists of wind setup + run number
                flight_plan = copy.deepcopy('../Flight_Logs/'+j+'/'+scenario_ID+'.csv') #Path to log file
                start_long = coordinates[j][1]
                start_lat = coordinates[j][0]
                start_height = coordinates[j][2]

                ##Call of pre_process function and merging existing data frame with new one. Adding new log data
                DATA= pd.concat([DATA,pre_process(flight_plan,start_long,start_lat,start_height,scenario_ID)],axis=1,ignore_index = False)
                DATA= DATA.sort_index(ascending=True)

        ##Add data frame from location to dictionary    
        imported.update({j:DATA})

    return(imported)


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