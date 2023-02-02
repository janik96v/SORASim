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

##Crash Side on Map


def crash_plot(location,cv,grb,flight,gps1):
    '''Visualizes where the UAV crashed on a 2D map, which comes from OpenStreeMap.
    Link: https://www.openstreetmap.org/export#map=18/47.12981/7.23097. 
    The location argument gives the location according to the experimental design of where the map should be plotted'''

    #Colors for different runs
    col = ['#ADADAD','#ADADAD','#ADADAD','#EC7063','#EC7063','#EC7063','#CB4335','#CB4335','#CB4335','#641E16','#641E16','#641E16',
        '#82E0AA','#82E0AA','#82E0AA','#28B463','#28B463','#28B463','#186A3B','#186A3B','#186A3B','#5DADE2','#5DADE2','#5DADE2','#2E86C1',
        '#2E86C1','#2E86C1','#1B4F72','#1B4F72','#1B4F72','#BB8FCE','#BB8FCE','#BB8FCE','#7D3C98','#7D3C98','#7D3C98','#4A235A','#4A235A','#4A235A']
    col_idx = 0

    karte = {'Location1': [47.12976,47.13162,7.23866,7.24174],'Location2':[47.1279,47.1295,7.2360,7.2389],'Location3':[47.12847,47.13048,7.22993,7.23325]}
    karte1 = karte[location]

    longitude_min = karte1[2]
    longitude_max = karte1[3]
    latitude_min = karte1[0]
    latitude_max = karte1[1]
    BBox = ((longitude_min,longitude_max,latitude_min,latitude_max))

    #Figure Settings
    fig, ax1 = plt.subplots(figsize = (8,5))
    flight_map = plt.imread('./OpenStreetMap_Images/'+location+'.png')
    
    #Plot Geofence Areas
    ax1.fill(cv.iloc[:,2],cv.iloc[:,1],'gold',linewidth=2,alpha=0.4)
    ax1.plot(cv.iloc[:,2],cv.iloc[:,1],'gold',linewidth=2,alpha=0.6) #Contigency Volume
    ax1.fill(grb.iloc[:,2],grb.iloc[:,1],'r',linewidth=2,alpha=0.2)
    ax1.plot(grb.iloc[:,2],grb.iloc[:,1],'r',linewidth=2,alpha=0.4)  #Ground Risk Buffer

    #Plot intended flight direction
    idx_start = len(flight.index)-2
    idx_end = len(flight.index)
    ax1.plot(flight.iloc[idx_start:idx_end,2],flight.iloc[idx_start:idx_end,1],'black',linewidth=2,alpha=0.4)

    #Axis Limits & Titles
    ax1.set_xlim(longitude_min,longitude_max)
    ax1.set_ylim(latitude_min,latitude_max)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.imshow(flight_map, zorder=0, extent = BBox, aspect= 'equal')
    ax1.grid()
    
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
       
    for i in range(0,len(gps1.columns),3):

        last_idx = gps1.iloc[:,i].last_valid_index()
        ax1.scatter(gps1.loc[last_idx][i+1],gps1.loc[last_idx][i],color=col[col_idx],s=20,marker="x",label=names.iloc[col_idx,0])
        ax1.legend(loc='upper right')
        col_idx += 1

    plt.savefig('./Plots/crash_location_'+location+'.png')
    plt.show()



###----------------------------------------------------------------------------------------------------------------------------------------------------------------
##2D Plot North vs East & Height vs Distance

def crash_curve(loc1,cv1,grb1,flight_ENU,limits1,geof_dist1,location):
    '''This function visualizes the flight path on a 2D graph (north vs east) and the curve of the crash
     on a graph showing the distance to the inital waypoint vs the height above ground'''
    
    #Figure Settings
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.set_figheight(5)
    fig.set_figwidth(10)

    #Colors for different runs
    col = ['#ADADAD','#ADADAD','#ADADAD','#EC7063','#EC7063','#EC7063','#CB4335','#CB4335','#CB4335','#641E16','#641E16','#641E16',
        '#82E0AA','#82E0AA','#82E0AA','#28B463','#28B463','#28B463','#186A3B','#186A3B','#186A3B','#5DADE2','#5DADE2','#5DADE2','#2E86C1',
        '#2E86C1','#2E86C1','#1B4F72','#1B4F72','#1B4F72','#BB8FCE','#BB8FCE','#BB8FCE','#7D3C98','#7D3C98','#7D3C98','#4A235A','#4A235A','#4A235A']
    col_idx = 0 #Color Index needed for interation trough color as the iteration through data set isn't following the same step size

    #Plottting Geofence Areas
    ax1.fill(cv1.iloc[:,1],cv1.iloc[:,0],'gold',linewidth=2,alpha=0.4)
    ax1.plot(cv1.iloc[:,1],cv1.iloc[:,0],'gold',linewidth=2,alpha=0.6) #Contigency Volume
    ax1.fill(grb1.iloc[:,1],grb1.iloc[:,0],'r',linewidth=2,alpha=0.2)
    ax1.plot(grb1.iloc[:,1],grb1.iloc[:,0],'r',linewidth=2,alpha=0.4) #Ground Risk Buffer

    ax2.axvline(x=geof_dist1[0],color = 'gold') #Contigency Volume
    ax2.axvline(x=geof_dist1[1],color = 'r') #Ground Risk Buffer

    #Plotting Flight Path
    ax1.plot(flight_ENU.iloc[:,2],flight_ENU.iloc[:,1],'black',linewidth=2)

    #Setting
    ax1.set_xlim(limits1[0])
    ax1.set_ylim(limits1[1])
    ax1.set_xlabel('East [m]')
    ax1.set_ylabel('North [m]')
    ax1.grid()

    ax2.set_ylabel('Altitude [m]')
    ax2.set_xlim([0,160])
    ax2.set_ylim([0,125])
    ax2.set_xlabel('Distance from Waypoint [m]')
    ax2.grid()

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

    #Loop through data columns to plot different runs
    for i in range(0,len(loc1.columns),3):
        
        #North vs East Plot
        ax1.plot(loc1.iloc[:,i+1],loc1.iloc[:,i],linestyle='dashed',color=col[col_idx],alpha=1.0)

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
        angle_deg = (angle*180)/np.pi

        #Projected Distance on Flight Path
        dist = vec_2d_len*np.cos(angle)

        #Height vs Projected Distance from initial Waypoint
        ax2.plot(dist,loc1.iloc[:,i+2],linestyle='dashed',color=col[col_idx],label=names.iloc[col_idx,0])
        ax2.legend(loc='upper right')

        col_idx += 1 #Increase color index

    plt.savefig('./Plots/crash_curve_'+location+'.png')
    plt.show()
    


###----------------------------------------------------------------------------------------------------------------------------------------------------------------
##2D Plot North vs East & Height vs Distance (same as before but continous line adding)

def crash_curve_cont(loc1,cv1,grb1,flight_ENU,limits1,geof_dist1):
    '''This function does the same as the function crash_curve,
     but it plots the runs after each other with a certain sleep time in between'''

    #Figure Settings
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.set_figheight(5)
    fig.set_figwidth(10)
    plt.ion()

    #Colors for different runs
    col = ['#ADADAD','#ADADAD','#ADADAD','#EC7063','#EC7063','#EC7063','#CB4335','#CB4335','#CB4335','#641E16','#641E16','#641E16',
        '#82E0AA','#82E0AA','#82E0AA','#28B463','#28B463','#28B463','#186A3B','#186A3B','#186A3B','#5DADE2','#5DADE2','#5DADE2','#2E86C1',
        '#2E86C1','#2E86C1','#1B4F72','#1B4F72','#1B4F72','#BB8FCE','#BB8FCE','#BB8FCE','#7D3C98','#7D3C98','#7D3C98','#4A235A','#4A235A','#4A235A']
    col_idx = 0

    #Plottting Geofence Areas
    ax1.fill(cv1.iloc[:,1],cv1.iloc[:,0],'gold',linewidth=2,alpha=0.4)
    ax1.plot(cv1.iloc[:,1],cv1.iloc[:,0],'gold',linewidth=2,alpha=0.6) #Contigency Volume
    ax1.fill(grb1.iloc[:,1],grb1.iloc[:,0],'r',linewidth=2,alpha=0.2)
    ax1.plot(grb1.iloc[:,1],grb1.iloc[:,0],'r',linewidth=2,alpha=0.4) #Ground Risk Buffer

    ax2.axvline(x=geof_dist1[0],color = 'gold') #Contigency Volume
    ax2.axvline(x=geof_dist1[1],color = 'r') #Ground Risk Buffer

    #Plotting Flight Path
    ax1.plot(flight_ENU.iloc[:,2],flight_ENU.iloc[:,1],'black',linewidth=2)

    #Setting
    ax1.set_xlim(limits1[0])
    ax1.set_ylim(limits1[1])
    ax1.set_xlabel('East [m]')
    ax1.set_ylabel('North [m]')
    ax1.grid()

    ax2.set_ylabel('Altitude [m]')
    ax2.set_xlabel('Distance from Waypoint [m]')
    ax2.grid()

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

    #Loop through data columns to plot different runs
    for i in range(0,len(loc1.columns),3):
        
        #North vs East Plot
        ax1.plot(loc1.iloc[:,i+1],loc1.iloc[:,i],linestyle='dashed',color=col[col_idx])
       

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
        angle_deg = (angle*180)/np.pi

        #Projected Distance on Flight Path
        dist = vec_2d_len*np.cos(angle)

        #Height vs Projected Distance from initial Waypoint
        ax2.plot(dist,loc1.iloc[:,i+2],linestyle='dashed',color=col[col_idx],label=names.iloc[col_idx,0])
        ax2.legend(loc='lower left')

        #Increase color index
        col_idx += 1

        #Drawing updated values
        fig.canvas.draw()   

        # #This will run the GUI event
        # #loop until all UI events
        # #currently waiting have been processed
        fig.canvas.flush_events()

        time.sleep(0.5) #Time between update graph      
    





###----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print('hello')