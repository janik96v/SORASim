######
#Date: 19.12.2022
##Version Log:
#
#
#
######

###Import Libraries

import numpy as np
import pandas as pd
import math
import copy
import pymap3d as map
import time
import matplotlib.pyplot as plt
from matplotlib.pyplot import axis, plot, show
import re
import visualization as vis
import pre_processing as prep
import post_processing as post

#####---------------------------------------------------------------------------------------------------------------------------------------------------------------

###DATA Import & Pre-Processing

####-----------------------------------------------------------------------------------------------------------------------------------------------------------------


##Defining arguments for data import & data pre-processing functions
world = ['biel','biel_NL','biel_NM','biel_NH','biel_SL','biel_SM','biel_SH','biel_SEL','biel_SEM','biel_SEH','biel_NWL','biel_NWM','biel_NWH']
location = ['Location1']
coordinates = {'Location1':[47.13063365,7.240606723,50]}
flight_mode = 'SMode' #Only used for folder location of the flight logs as argument of the import_function (reference to flight velocity)
runs = 3

##Flight Plan Import
fp1 = pd.read_csv('../Flight_Plans/flight_plan_location1.csv', sep=';')
fp = {'Location1':fp1}

##Truning GPS coordinates of flight plan into ENU
fp_ENU = prep.flightplan2enu(fp,coordinates)

##Importing and Preprocessing the data with the corresponding functions (2s Pilot Reaction)

reaction = '2s'  #Only used for folder location of the flight logs as argument of the import_function (reference to human reaction time)
DATA, DATA_TIME = prep.import_data(world,runs,location,flight_mode,coordinates,fp_ENU,reaction)
DATA_ENU = prep.gps2enu(DATA,coordinates)

##Importing and Preprocessing the data with the corresponding functions (3s Pilot Reaction)

reaction3 = '3s' #Only used for folder location of the flight logs as argument of the import_function (reference to human reaction time)
DATA_3s, DATA_TIME_3s = prep.import_data(world,runs,location,flight_mode,coordinates,fp_ENU,reaction3)
DATA_ENU_3s = prep.gps2enu(DATA_3s,coordinates)

##Geofence Import
cv =  pd.read_csv('../Flight_Plans/contigency_volume_coordinates.csv',sep=';') #Contigency Volume
cv.loc[len(cv.index)] = cv.iloc[0,:] #Closing geofence are by adding first point to the end
grb = pd.read_csv('../Flight_Plans/ground_risk_buffer_coordinates.csv',sep=';') #Ground Risk Buffer
grb.loc[len(grb.index)] = grb.iloc[0,:] #Closing geofence are by adding first point to the end

##Turning GPS coordinates into ENU coordinates for the geofencencing areas
cv_enu = prep.geofence2enu(cv,coordinates)
grb_enu = prep.geofence2enu(grb,coordinates)

# #Distance of cv and grb from inital waypoint at location 1,2 and 3
geof_dist = {'Location1':[50,75]}



# #####---------------------------------------------------------------------------------------------------------------------------------------------------------------

# ###Plottings

# ####-----------------------------------------------------------------------------------------------------------------------------------------------------------------

##Selcet the Location for the plots

location = 'Location1'

##Takes the data of the chosen from the corresponding dictionaries (2s Pilot Reaction Time). 
loc1 = DATA_ENU[location]
data_time = DATA_TIME[location]
gps1 = DATA[location]
cv1 = cv_enu[location]
cv_gps = cv.iloc[:,1:]
grb1 = grb_enu[location]
grb_gps = grb.iloc[:,1:]
geof_dist1 = geof_dist[location]
flight = fp[location]
flight_ENU = fp_ENU[location]
limits = {'Location1':[[-100, 10],[-10, 100]]}
limits1 = limits[location]

##Takes the data of the chosen from the corresponding dictionaries (3s Pilot Reaction Time). 
loc1_3s = DATA_ENU_3s[location]
data_time_3s = DATA_TIME_3s[location]
gps1_3s = DATA_3s[location]

## Plots the 2D flight path on the Open Street Map section
vis.cv_flightpath(gps1,cv_gps,grb_gps,flight,location)

## Plots the time vs. distance to initial waypoint
vis.reaction_distance(loc1,data_time,loc1_3s,data_time_3s,flight_ENU,geof_dist1,location)


# #####---------------------------------------------------------------------------------------------------------------------------------------------------------------

# ###Post Processing

# ####-----------------------------------------------------------------------------------------------------------------------------------------------------------------

# location = ['Location1','Location2','Location3']
# run_nr = 3

# #Calculates the mean values for each scenario
# crash_dict = post.enu_mean(DATA_ENU,world,location,run_nr)

# #Outputs the projected mean distances for every scenario and location in one data frame
# proj_dist = post.projected_distance(crash_dict,fp_ENU,location,world)

# # pd.DataFrame.to_csv(proj_dist,'./Plots/distance_to_crash.csv',sep=';')

# #Runs the function for the descriptive statistics on the crash_dict data set
# post.run_statistics(location,world,crash_dict)

breakdist, max_dist = post.cv_breakdistance(loc1,data_time,flight_ENU,runs,reaction,flight_mode)
breakdist_3s, max_dist_3s = post.cv_breakdistance(loc1_3s,data_time_3s,flight_ENU,runs,reaction3,flight_mode)

breakdist_dict = {reaction:max_dist, reaction3:max_dist_3s}

STATS_DATA = post.cv_distance_statistics(breakdist_dict,flight_mode)



