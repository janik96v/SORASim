######
#Date: 21.12.2022
##Version Log:
#
#
#
######

###Import Libraries

import numpy as np
import pandas as pd
import copy
import pymap3d as map
import time
import matplotlib.pyplot as plt
from matplotlib.pyplot import axis, plot, show

###-----------------------------------------------------------------------------------------------------------------------------------------------------------------

###----------------------------------------------------------------------------------------------------------------------------------------------------------------


##2D Plot Longitude vs Latitude
def cv_flightpath(gps1,cv_gps,grb_gps,flight,location):
    '''This function visualizes the flight path on a 2D graph (longitude vs latitude) with the corresponding section of the map.
    Every wind scenario exists in a new plot. The first plot also contains the reference scenario.'''
        
    #Figure Settings
    fig, ((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2)
    fig.set_figheight(8)
    fig.set_figwidth(14)

    #Colors for different runs
    col = ['#ADADAD','#ADADAD','#ADADAD','#EC7063','#EC7063','#EC7063','#CB4335','#CB4335','#CB4335','#641E16','#641E16','#641E16',
        '#82E0AA','#82E0AA','#82E0AA','#28B463','#28B463','#28B463','#186A3B','#186A3B','#186A3B','#5DADE2','#5DADE2','#5DADE2','#2E86C1',
        '#2E86C1','#2E86C1','#1B4F72','#1B4F72','#1B4F72','#BB8FCE','#BB8FCE','#BB8FCE','#7D3C98','#7D3C98','#7D3C98','#4A235A','#4A235A','#4A235A']
    col_idx = 0 #Color Index needed for interation trough color as the iteration through data set isn't following the same step size


    #Settings OpenStreetMap Background
    karte = {'Location1': [47.13052,47.13114,7.23963,7.24081]}
    karte1 = karte[location]
    flight_map = plt.imread('./OpenStreetMap_Images/'+location+'.png')


    longitude_min = karte1[2]
    longitude_max = karte1[3]
    latitude_min = karte1[0]
    latitude_max = karte1[1]
    BBox = ((longitude_min,longitude_max,latitude_min,latitude_max))


    #Plottting Geofence Areas
    ax1.fill(cv_gps.iloc[:,1],cv_gps.iloc[:,0],'gold',linewidth=2,alpha=0.4)
    ax1.plot(cv_gps.iloc[:,1],cv_gps.iloc[:,0],'gold',linewidth=2,alpha=0.6) #Contigency Volume
    ax1.fill(grb_gps.iloc[:,1],grb_gps.iloc[:,0],'r',linewidth=2,alpha=0.2)
    ax1.plot(grb_gps.iloc[:,1],grb_gps.iloc[:,0],'r',linewidth=2,alpha=0.4) #Ground Risk Buffer

    ax2.fill(cv_gps.iloc[:,1],cv_gps.iloc[:,0],'gold',linewidth=2,alpha=0.4)
    ax2.plot(cv_gps.iloc[:,1],cv_gps.iloc[:,0],'gold',linewidth=2,alpha=0.6) #Contigency Volume
    ax2.fill(grb_gps.iloc[:,1],grb_gps.iloc[:,0],'r',linewidth=2,alpha=0.2)
    ax2.plot(grb_gps.iloc[:,1],grb_gps.iloc[:,0],'r',linewidth=2,alpha=0.4) #Ground Risk Buffer

    ax3.fill(cv_gps.iloc[:,1],cv_gps.iloc[:,0],'gold',linewidth=2,alpha=0.4)
    ax3.plot(cv_gps.iloc[:,1],cv_gps.iloc[:,0],'gold',linewidth=2,alpha=0.6) #Contigency Volume
    ax3.fill(grb_gps.iloc[:,1],grb_gps.iloc[:,0],'r',linewidth=2,alpha=0.2)
    ax3.plot(grb_gps.iloc[:,1],grb_gps.iloc[:,0],'r',linewidth=2,alpha=0.4) #Ground Risk Buffer

    ax4.fill(cv_gps.iloc[:,1],cv_gps.iloc[:,0],'gold',linewidth=2,alpha=0.4)
    ax4.plot(cv_gps.iloc[:,1],cv_gps.iloc[:,0],'gold',linewidth=2,alpha=0.6) #Contigency Volume
    ax4.fill(grb_gps.iloc[:,1],grb_gps.iloc[:,0],'r',linewidth=2,alpha=0.2)
    ax4.plot(grb_gps.iloc[:,1],grb_gps.iloc[:,0],'r',linewidth=2,alpha=0.4) #Ground Risk Buffer

    #Plotting Flight Path
    ax1.plot(flight.iloc[:,2],flight.iloc[:,1],'black',linewidth=2)
    ax2.plot(flight.iloc[:,2],flight.iloc[:,1],'black',linewidth=2)
    ax3.plot(flight.iloc[:,2],flight.iloc[:,1],'black',linewidth=2)
    ax4.plot(flight.iloc[:,2],flight.iloc[:,1],'black',linewidth=2)

    #Setting
    ax1.set_xlim(longitude_min,longitude_max)
    ax1.set_ylim(latitude_min,latitude_max)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.imshow(flight_map, zorder=0, extent = BBox, aspect= 'auto')
    ax1.grid()

    ax2.set_xlim(longitude_min,longitude_max)
    ax2.set_ylim(latitude_min,latitude_max)
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    ax2.imshow(flight_map, zorder=0, extent = BBox, aspect= 'auto')
    ax2.grid()

    ax3.set_xlim(longitude_min,longitude_max)
    ax3.set_ylim(latitude_min,latitude_max)
    ax3.set_xlabel('Longitude')
    ax3.set_ylabel('Latitude')
    ax3.imshow(flight_map, zorder=0, extent = BBox, aspect= 'auto')
    ax3.grid()

    ax4.set_xlim(longitude_min,longitude_max)
    ax4.set_ylim(latitude_min,latitude_max)
    ax4.set_xlabel('Longitude')
    ax4.set_ylabel('Latitude')
    ax4.imshow(flight_map, zorder=0, extent = BBox, aspect= 'auto')
    ax4.grid()


    #Creating the labels for the legend
    names = gps1.columns
    names = names[range(0,len(names),3)]
    names = pd.DataFrame(names)
    names = names.replace(regex=['biel_'],value='')
    names = names.replace(regex=['_lat'],value='')

    names.iloc[range(1,len(names),3),0] = '_nolegend_'
    names.iloc[range(2,len(names),3),0] = '_nolegend_'
    names = names.replace(regex=['_Run_1'],value='')
    names = names.replace(regex=['Run_1'],value='NoWind')

    #Loop through data north wind scenarios
    for i in range(0,36,3):
        
        #North vs East Plot
        ax1.plot(gps1.iloc[:,i+1],gps1.iloc[:,i],linestyle='dashed',color=col[col_idx],label=names.iloc[col_idx,0])
        col_idx += 1 #Increase color index
        ax1.legend(loc='upper right')

    #Loop through data south wind scenarios
    for i in range(36,63,3):
        
        #North vs East Plot
        ax2.plot(gps1.iloc[:,i+1],gps1.iloc[:,i],linestyle='dashed',color=col[col_idx],label=names.iloc[col_idx,0])
        col_idx += 1 #Increase color index
        ax2.legend(loc='upper right')

    #Loop through data south east wind scenarios
    for i in range(63,90,3):
        
        #North vs East Plot
        ax3.plot(gps1.iloc[:,i+1],gps1.iloc[:,i],linestyle='dashed',color=col[col_idx],label=names.iloc[col_idx,0])
        col_idx += 1 #Increase color index
        ax3.legend(loc='upper right')


    #Loop through data north west wind scenarios
    for i in range(90,117,3):
        
        #North vs East Plot
        ax4.plot(gps1.iloc[:,i+1],gps1.iloc[:,i],linestyle='dashed',color=col[col_idx],label=names.iloc[col_idx,0])
        col_idx += 1 #Increase color index
        ax4.legend(loc='upper right')

    plt.savefig('./Plots/cv_flightpath_'+location+'.png')
    plt.show()
#---------------------------------------------------------------------------------------------------------------------------




##Distance vs Time
def reaction_distance(loc1,data_time,loc1_3s,data_time_3s,flight_ENU,geof_dist1,location):
    '''This function visualizes the distance with regard to time. The distance is measured from the initial waypoint until stable hover is reached.
    The distance is projected on to the intended flight path in order to correct for wind deviations.'''
        
    #Figure Settings
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
    fig.set_figheight(6.5)
    fig.set_figwidth(10)

    #Colors for different runs
    col = ['#ADADAD','#ADADAD','#ADADAD','#EC7063','#EC7063','#EC7063','#CB4335','#CB4335','#CB4335','#641E16','#641E16','#641E16',
        '#82E0AA','#82E0AA','#82E0AA','#28B463','#28B463','#28B463','#186A3B','#186A3B','#186A3B','#5DADE2','#5DADE2','#5DADE2','#2E86C1',
        '#2E86C1','#2E86C1','#1B4F72','#1B4F72','#1B4F72','#BB8FCE','#BB8FCE','#BB8FCE','#7D3C98','#7D3C98','#7D3C98','#4A235A','#4A235A','#4A235A']
    col_idx = 0 #Color Index needed for interation trough color as the iteration through data set isn't following the same step size

    #Plottting Geofence Areas
    ax1.axhline(y=geof_dist1[0],color = 'gold') #Contigency Volume
    ax1.axhline(y=geof_dist1[1],color = 'r') #Ground Risk Buffer
    ax2.axhline(y=geof_dist1[0],color = 'gold') #Contigency Volume
    ax2.axhline(y=geof_dist1[1],color = 'r') #Ground Risk Buffer
    ax3.axhline(y=geof_dist1[0],color = 'gold') #Contigency Volume
    ax3.axhline(y=geof_dist1[1],color = 'r') #Ground Risk Buffer
    ax4.axhline(y=geof_dist1[0],color = 'gold') #Contigency Volume
    ax4.axhline(y=geof_dist1[1],color = 'r') #Ground Risk Buffer

    #Setting
    ax1.set_ylim([0,100])
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Distance [m]')
    ax1.grid()

    ax2.set_ylim([0,100])
    ax2.set_xlabel('Time [s]')
    ax2.set_ylabel('Distance [m]')
    ax2.grid()

    ax3.set_ylim([0,100])
    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel('Distance [m]')
    ax3.grid()

    ax4.set_ylim([0,100])
    ax4.set_xlabel('Time [s]')
    ax4.set_ylabel('Distance [m]')
    ax4.grid()

    #Creating the labels for the legend
    names = loc1.columns
    names = names[range(0,len(names),3)]
    names = pd.DataFrame(names)
    names = names.replace(regex=['biel_'],value='')
    names = names.replace(regex=['_north'],value='')
    names.iloc[range(1,len(names),3),0] = '_nolegend_'
    names.iloc[range(2,len(names),3),0] = '_nolegend_'
    names = names.replace(regex=['_Run_1'],value='')
    names = names.replace(regex=['Run_1'],value='NoWind')

    #Loop through data north wind scenarios
    for i in range(0,36,3):
        
        #Calculating Distance projected on Flight Path
        vec_2d = np.array([loc1.iloc[:,i],loc1.iloc[:,i+1]]) #North,East Vector
        vec_2d = vec_2d.transpose()

        #North,East Vector of Fligth Plan
        fp_2d = np.array(flight_ENU.iloc[1,:])[1:3]

        #Calculate angle between the two vectors
        dot = np.dot(vec_2d,fp_2d)
        vec_2d_len = np.sqrt(np.sum(vec_2d*vec_2d,axis=1))
        fp_2d_len = np.sqrt((fp_2d*fp_2d).sum())
        cos_angle = dot/(vec_2d_len*fp_2d_len)
        angle = np.arccos(cos_angle)

        #Projected Distance on Flight Path
        dist = vec_2d_len*np.cos(angle)

        ax1.plot(data_time.iloc[:,col_idx],dist,linestyle='dashed',color=col[col_idx],label=names.iloc[col_idx,0])
        ax1.legend(loc='upper right')

        #Calculating Distance projected on Flight Path for 3s Pilot Reaction
        vec_2d = np.array([loc1_3s.iloc[:,i],loc1_3s.iloc[:,i+1]]) #North,East Vector
        vec_2d = vec_2d.transpose()

        #Calculate angle between the two vectors
        dot = np.dot(vec_2d,fp_2d)
        vec_2d_len = np.sqrt(np.sum(vec_2d*vec_2d,axis=1))
        cos_angle = dot/(vec_2d_len*fp_2d_len)
        angle = np.arccos(cos_angle)

        #Projected Distance on Flight Path
        dist = vec_2d_len*np.cos(angle)

        ax1.plot(data_time_3s.iloc[:,col_idx],dist,color=col[col_idx])

        col_idx += 1 #Increase color index

    #Loop through data south wind scenarios
    for i in range(36,63,3):
        
        #Calculating Distance projected on Flight Path
        vec_2d = np.array([loc1.iloc[:,i],loc1.iloc[:,i+1]]) #North,East Vector
        vec_2d = vec_2d.transpose()

        #North,East Vector of Fligth Plan
        fp_2d = np.array(flight_ENU.iloc[1,:])[1:3]

        #Calculate angle between the two vectors
        dot = np.dot(vec_2d,fp_2d)
        vec_2d_len = np.sqrt(np.sum(vec_2d*vec_2d,axis=1))
        fp_2d_len = np.sqrt((fp_2d*fp_2d).sum())
        cos_angle = dot/(vec_2d_len*fp_2d_len)
        angle = np.arccos(cos_angle)

        #Projected Distance on Flight Path
        dist = vec_2d_len*np.cos(angle)

        ax2.plot(data_time.iloc[:,col_idx],dist,linestyle='dashed',color=col[col_idx],label=names.iloc[col_idx,0])
        ax2.legend(loc='upper right')

        #Calculating Distance projected on Flight Path for 3s Pilot Reaction
        vec_2d = np.array([loc1_3s.iloc[:,i],loc1_3s.iloc[:,i+1]]) #North,East Vector
        vec_2d = vec_2d.transpose()

        #Calculate angle between the two vectors
        dot = np.dot(vec_2d,fp_2d)
        vec_2d_len = np.sqrt(np.sum(vec_2d*vec_2d,axis=1))
        cos_angle = dot/(vec_2d_len*fp_2d_len)
        angle = np.arccos(cos_angle)

        #Projected Distance on Flight Path
        dist = vec_2d_len*np.cos(angle)

        ax2.plot(data_time_3s.iloc[:,col_idx],dist,color=col[col_idx])

        col_idx += 1 #Increase color index


    #Loop through data south east wind scenarios
    for i in range(63,90,3):
        
        #Calculating Distance projected on Flight Path
        vec_2d = np.array([loc1.iloc[:,i],loc1.iloc[:,i+1]]) #North,East Vector
        vec_2d = vec_2d.transpose()

        #North,East Vector of Fligth Plan
        fp_2d = np.array(flight_ENU.iloc[1,:])[1:3]

        #Calculate angle between the two vectors
        dot = np.dot(vec_2d,fp_2d)
        vec_2d_len = np.sqrt(np.sum(vec_2d*vec_2d,axis=1))
        fp_2d_len = np.sqrt((fp_2d*fp_2d).sum())
        cos_angle = dot/(vec_2d_len*fp_2d_len)
        angle = np.arccos(cos_angle)

        #Projected Distance on Flight Path
        dist = vec_2d_len*np.cos(angle)

        ax3.plot(data_time.iloc[:,col_idx],dist,linestyle='dashed',color=col[col_idx],label=names.iloc[col_idx,0])
        ax3.legend(loc='upper right')

        #Calculating Distance projected on Flight Path for 3s Pilot Reaction
        vec_2d = np.array([loc1_3s.iloc[:,i],loc1_3s.iloc[:,i+1]]) #North,East Vector
        vec_2d = vec_2d.transpose()

        #Calculate angle between the two vectors
        dot = np.dot(vec_2d,fp_2d)
        vec_2d_len = np.sqrt(np.sum(vec_2d*vec_2d,axis=1))
        cos_angle = dot/(vec_2d_len*fp_2d_len)
        angle = np.arccos(cos_angle)

        #Projected Distance on Flight Path
        dist = vec_2d_len*np.cos(angle)

        ax3.plot(data_time_3s.iloc[:,col_idx],dist,color=col[col_idx])

        col_idx += 1 #Increase color index

    #Loop through data north west wind scenarios
    for i in range(90,117,3):
        
        #Calculating Distance projected on Flight Path
        vec_2d = np.array([loc1.iloc[:,i],loc1.iloc[:,i+1]]) #North,East Vector
        vec_2d = vec_2d.transpose()

        #North,East Vector of Fligth Plan
        fp_2d = np.array(flight_ENU.iloc[1,:])[1:3]

        #Calculate angle between the two vectors
        dot = np.dot(vec_2d,fp_2d)
        vec_2d_len = np.sqrt(np.sum(vec_2d*vec_2d,axis=1))
        fp_2d_len = np.sqrt((fp_2d*fp_2d).sum())
        cos_angle = dot/(vec_2d_len*fp_2d_len)
        angle = np.arccos(cos_angle)

        #Projected Distance on Flight Path
        dist = vec_2d_len*np.cos(angle)

        #Height vs Projected Distance from initial Waypoint
        ax4.plot(data_time.iloc[:,col_idx],dist,linestyle='dashed',color=col[col_idx],label=names.iloc[col_idx,0])
        ax4.legend(loc='upper right')

        #Calculating Distance projected on Flight Path for 3s Pilot Reaction
        vec_2d = np.array([loc1_3s.iloc[:,i],loc1_3s.iloc[:,i+1]]) #North,East Vector
        vec_2d = vec_2d.transpose()

        #Calculate angle between the two vectors
        dot = np.dot(vec_2d,fp_2d)
        vec_2d_len = np.sqrt(np.sum(vec_2d*vec_2d,axis=1))
        cos_angle = dot/(vec_2d_len*fp_2d_len)
        angle = np.arccos(cos_angle)

        #Projected Distance on Flight Path
        dist = vec_2d_len*np.cos(angle)

        ax4.plot(data_time_3s.iloc[:,col_idx],dist,color=col[col_idx])

        col_idx += 1 #Increase color index

    plt.savefig('./Plots/reaction_time_'+location+'.png')
    plt.show()





###----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print('hello')