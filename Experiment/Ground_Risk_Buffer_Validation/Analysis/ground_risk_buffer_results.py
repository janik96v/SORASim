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
location = ['Location1','Location2','Location3']
coordinates = {'Location1':[47.13063365,7.240606723,50],'Location2':[47.128575,7.237782,73],'Location3':[47.128694,7.230861,120]}
runs = 3

##Importing and Preprocessing the data with the corresponding functions
DATA = prep.import_data(world,runs,location,coordinates)
DATA_ENU = prep.gps2enu(DATA,coordinates)

##Geofence Import
cv =  pd.read_csv('../Flight_Plans/contigency_volume_coordinates.csv',sep=';') #Contigency Volume
cv.loc[len(cv.index)] = cv.iloc[0,:] #Closing geofence are by adding first point to the end
grb = pd.read_csv('../Flight_Plans/ground_risk_buffer_coordinates.csv',sep=';') #Ground Risk Buffer
grb.loc[len(grb.index)] = grb.iloc[0,:] #Closing geofence are by adding first point to the end

##Turning GPS coordinates into ENU coordinates for the geofencencing areas
cv_enu = prep.geofence2enu(cv,coordinates)
grb_enu = prep.geofence2enu(grb,coordinates)

#Distance of cv and grb from inital waypoint at location 1,2 and 3
geof_dist = {'Location1':[50,75], 'Location2':[50,89], 'Location3':[50,120]}

##Flight Plan Import
fp1 = pd.read_csv('../Flight_Plans/flight_plan_location1.csv', sep=';')
fp2 = pd.read_csv('../Flight_Plans/flight_plan_location2.csv', sep=';')
fp3 = pd.read_csv('../Flight_Plans/flight_plan_location3.csv', sep=';')
fp = {'Location1':fp1, 'Location2':fp2, 'Location3':fp3}

##Truning GPS coordinates of flight plan into ENU

fp_ENU = prep.flightplan2enu(fp,coordinates)


#####---------------------------------------------------------------------------------------------------------------------------------------------------------------

###Post Processing

####-----------------------------------------------------------------------------------------------------------------------------------------------------------------

location = ['Location1','Location2','Location3']
run_nr = 3

#Calculates the mean values for each scenario
crash_dict = post.enu_mean(DATA_ENU,world,location,run_nr)

#Outputs the projected mean distances for every scenario and location in one data frame
proj_dist = post.projected_distance(crash_dict,fp_ENU,location,world)

pd.DataFrame.to_csv(proj_dist,'./Plots/distance_to_crash.csv',sep=';')

#Runs the function for the descriptive statistics on the crash_dict data set
post.run_statistics(location,world,crash_dict)








#####---------------------------------------------------------------------------------------------------------------------------------------------------------------

###Plottings

####-----------------------------------------------------------------------------------------------------------------------------------------------------------------

##Box Plot: Run variation

bp_data = {}
boxplot_label = [s.replace('biel_','') for s in world]
boxplot_label = [s.replace('biel','NoWind') for s in boxplot_label]

#Iterating through the 3 locations
for j in location:

    box_data = crash_dict[j]
    #Calculating 2D distance and reshape matrix
    dist = np.sqrt(box_data[:,0]**2+box_data[:,1]**2)
    dist = dist.reshape(13,4)
    dist = dist[:,0:3]

    #Create Data Frame of the distance and the labels 
    data_dist = {}
    for i in range(0,len(boxplot_label),1):
        data_dist.update({boxplot_label[i]:dist[i,:]})

    data_dist = pd.DataFrame(data_dist)

    #Add the data frame to a dict for every location
    bp_data.update({j:data_dist})

#Function to plot boxplot and fill the boxplots with a different color for every location
def box_plot(data, fill_color):
    bp = ax1.boxplot(data, patch_artist=True)
    
    for patch in bp['boxes']:
        patch.set(facecolor=fill_color)       
        
    return bp

#Initializing the plot
fig, ax1 = plt.subplots(figsize=(8, 12))
ax1.set_ylabel('Distance from initial waypoint [m]')
ax1.grid()
bplot1 = box_plot(bp_data['Location1'],'lightgreen')
bplot2 = box_plot(bp_data['Location2'],'lightblue')
bplot3 = box_plot(bp_data['Location3'],'pink')
ax1.set_xticks(range(1,14,1),boxplot_label)
ax1.legend([bplot1["boxes"][0],bplot2["boxes"][0],bplot3["boxes"][0]], ['Location 1','Location 2','Location 3'])
plt.savefig('./Plots/sensitivity_boxplot.png')
plt.show() 

####----------------------------------------------------------
##Selcet the Location for the plots

location = 'Location3'

##Takes the data of the chosen from the corresponding dictionaries. 
loc1 = DATA_ENU[location]
gps1 = DATA[location]
cv1 = cv_enu[location]
grb1 = grb_enu[location]
geof_dist1 = geof_dist[location]
flight = fp[location]
flight_ENU = fp_ENU[location]
limits = {'Location1':[[-100, 10],[-10, 100]],'Location2':[[-100, 10],[-10, 100]],'Location3':[[-10, 100],[-10, 150]]}
limits1 = limits[location]

## Plots the crash on the Open Street Map cut out
vis.crash_plot(location,cv,grb,flight,gps1)

## Plots the flight path and the crash curve
vis.crash_curve(loc1,cv1,grb1,flight_ENU,limits1,geof_dist1,location)


# vis.crash_curve_cont(loc1,cv1,grb1,flight_ENU,limits1,geof_dist1)
# plt.show() 








