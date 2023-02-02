######
#Date: 27.12.2022
##Version Log:
#
#
#
######


###Import Libraries

import numpy as np
import pandas as pd

###-----------------------------------------------------------------------------------------------------------------------------------


### Calculates the maximum distance from the first waypoint and the time of the first deceleration of each run


def cv_breakdistance(loc1,data_time,flight_ENU,runs,reaction,flight_mode):
    '''This function is used to post-process the imported data to find maximum distance from initial waypoint and the time stamp of fist negativ accelartion. Moment when UAV starts to break.
    Therefore, it uses the imported data in ENU format and the corresponding data frame which contains the time stamp of when the data logging happend.'''

    #Prepare Column Names from Scenario Names
    names = loc1.columns
    names = names[range(0,len(names),3)]
    names = pd.DataFrame(names)
    names = names.replace(regex=['biel_'],value='')
    names = names.replace(regex=['_north'],value='')
    names.iloc[range(1,len(names),3),0] = '_nolegend_'
    names.iloc[range(2,len(names),3),0] = '_nolegend_'
    names = names.replace(regex=['_Run_1'],value='')
    names = names.replace(regex=['Run_1'],value='NoWind')
    names = list(names.iloc[range(0,39,3),0])

    #Turns 'reaction' input into integer
    pilot_reaction = reaction
    pilot_reaction = pilot_reaction.replace('s','')
    pilot_reaction = int(pilot_reaction)

    brk_vec = []
    dist_vec = []
    max_dist_vec = []
    time_itr = 0
    for i in range(0,loc1.shape[1],3):

        #North, east vector of log data
        vec_2d = np.array([loc1.iloc[:,i],loc1.iloc[:,i+1]]) #North,East Vector
        vec_2d = vec_2d.transpose()

        #North,East Vector of Fligth Plan
        fp_2d = np.array(flight_ENU.iloc[1,:])[1:3]
        fp_2d = fp_2d.transpose()

        #Calculate angle between the two vectors
        dot = np.dot(vec_2d,fp_2d)
        vec_2d_len = np.sqrt(np.sum(vec_2d*vec_2d,axis=1))
        fp_2d_len = np.sqrt((fp_2d*fp_2d).sum())
        cos_angle = dot/(vec_2d_len*fp_2d_len)
        angle = np.arccos(cos_angle)

        #Projected Distance on Flight Path
        dist = vec_2d_len*np.cos(angle)
        dist = dist.reshape(dist.shape[0],1)

        #Save maximum distance to vector with maximum distances of every run
        max_dist_vec = np.append(max_dist_vec,np.nanmax(dist))

        #Calculating speed through integral of position (slope of position --> speed)
        slope_num = dist[1:dist.shape[0]]-dist[0:(dist.shape[0]-1)]
        slope_num = slope_num.reshape(slope_num.shape[0],1)
        log_time = np.array(data_time.iloc[:,time_itr])
        slope_denum = log_time[1:log_time.shape[0]]-log_time[0:(log_time.shape[0]-1)]
        slope_denum = slope_denum.reshape(slope_denum.shape[0],1)
        slope = np.divide(slope_num,slope_denum)
        slope = np.append(slope,np.array(np.nan)) #adding 'nan' to keep array size
        slope = slope.reshape(slope.shape[0],1)

        #Calculating acceleration through integral of speed (slope of speed --> acceleration)
        slope2_num = slope[1:slope.shape[0]]-slope[0:(slope.shape[0]-1)]
        slope2_num = slope2_num.reshape(slope2_num.shape[0],1)
        slope2 = np.divide(slope2_num,slope_denum)
        slope2 = np.append(slope2,np.array(np.nan)) #adding 'nan' to keep array size
        slope2 = slope2.reshape(slope2.shape[0],1)

        #Time of first negativ acceleration after pilot intervention
        time_array = pd.Series.to_numpy(data_time.iloc[:,time_itr])
        time_array = time_array.reshape(slope2.shape[0],1)
        acc = np.append(time_array,slope2,axis=1) 
        acc = acc.reshape(slope2.shape[0],2)

        acc[:,1] = np.where(acc[:,0] < pilot_reaction,0,acc[:,1]) #Setting any acceleration below pilot reaction time to zero
        acc_neg = np.argmax(acc[:,1]<0) #Searching for first index with negativ accelartion
        dist_vec = np.append(dist_vec,dist[acc_neg,0]) #Distance in [m] of first negative acceleration after pilot reaction time saved to vector to store distance for every run
        brk_time = acc[acc_neg,0]-pilot_reaction #Time in [s] of first negative acceleration after pilot reaction time

        #Save time stamp of first negative accelartion to vector with corresponding time stamp of every run
        brk_vec = np.append(brk_vec,brk_time)

        #Iterates through data frame with time of logged data points, as it has a different format
        time_itr += 1

    #Combines both vectors in one vector with the format (runs x scenarios)
    dist_vec = dist_vec.reshape(runs,int(dist_vec.shape[0]/3),order='F')   
    brk_vec = brk_vec.reshape(runs,int(brk_vec.shape[0]/3),order='F')
    max_dist_vec = max_dist_vec.reshape(runs,int(max_dist_vec.shape[0]/3),order='F')

    brk_vec = np.append(brk_vec,dist_vec,axis=0)
    brk_vec = pd.DataFrame(brk_vec)
    max_dist_vec = pd.DataFrame(max_dist_vec)
    brk_vec = brk_vec.set_axis(names,axis=1)
    max_dist_vec = max_dist_vec.set_axis(names,axis=1)

    #Creates and sets row names
    names = []
    for i in range(1,runs+1,1):
        row_name = 'Run_'+str(i)+'_'+reaction
        names = np.append(names,row_name)

    max_dist_vec = max_dist_vec.set_axis(names,axis=0)
    names = np.append(names,names)
    names = list(names)
    brk_vec = brk_vec.set_axis(names,axis=0)

    #Saves Data Frame as .csv
    pd.DataFrame.to_csv(brk_vec,'./Plots/breakdistance_'+flight_mode+'_'+reaction+'.csv',sep=';')

    return brk_vec, max_dist_vec


##Descriptive Statistics of max distance from initial waypoint between the runs of one scenario
def cv_distance_statistics(breakdist_dict,flight_mode):
    '''Function to save a .csv file with metrics from the descriptive statistics for each scenario. A file is saved for each location.'''

    STATS_DATA = pd.DataFrame()
    for i in breakdist_dict.keys():
        
        stat_data = breakdist_dict[i]

        mittelwert = np.mean(stat_data,0)
        minimum = np.min(stat_data,0)
        maximum = np.max(stat_data,0)
        variation = maximum-minimum
        standardabw = np.sqrt(np.var(stat_data,0))
        median = stat_data.median()

        DATA_VAR = pd.DataFrame({'Minimum_'+i:minimum,
                            'Maximum_'+i:maximum,
                            'Variation_'+i:variation,
                            'Mean_'+i:mittelwert,
                            'Median_'+i:median,
                            'SD_'+i:standardabw})

        DATA_VAR = DATA_VAR.transpose()

        stat_data = pd.concat([stat_data,DATA_VAR])
    
        STATS_DATA = pd.concat([STATS_DATA,stat_data])


    pd.DataFrame.to_csv(STATS_DATA,'./Plots/distance_statistics_'+flight_mode+'.csv',sep=';')

    return STATS_DATA



###----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print('hello')