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

### Calulating the mean of consequetive runs (runs in same scenario)

def enu_mean(DATA_ENU,world,location,run_nr):
    '''This function caluclates the means of the ENU coordinates for the runs of the same scenario and outputs an array in a dictionary for every location'''

    crash_dict = {}
    
    ##Iteration through the different location
    for j in location:

        data = DATA_ENU[j] 
        runs = len(world)*run_nr #Number of runs per location

        ##Finding the last valid entry (location of crash) for every column (ENU coordinate)
        crash_idx = [data.loc[:,i].last_valid_index() for i in data.columns]
        crash_idx = np.array(crash_idx)
        crash_idx = crash_idx.reshape(crash_idx.shape[0],1)
        cols = np.array(data.columns)
        cols = cols.reshape(cols.shape[0],1)
        crash_idx2 = np.append(crash_idx,cols,axis=1)

        ##Iterates through these entrys to bring the data set into usable numpy array
        crash_loc = []
        for row,col in crash_idx2:
            val = data.loc[row,col]
            crash_loc = np.append(crash_loc,val)

        crash_loc = crash_loc.reshape(runs,3)

        ##Calculates the mean values of the three consecutive runs
        mean_crash = []
        for i in range(0,crash_loc.shape[0],3):
            val = np.mean(crash_loc[i:i+3,:],axis=0)
            mean_crash = np.append(mean_crash,val)

        mean_crash = mean_crash.reshape(len(world),3)

        ##Add the entry of the mean values below the three consecutive runs and outputs a new array
        crash_final = []
        for i in range(0,mean_crash.shape[0],1):
            val2 = np.append(crash_loc[(i*3):(i*3+3),:],mean_crash[i,:])
            crash_final = np.append(crash_final,val2)

        ##Reshapes this array [cols (north,est,up) / rows three runs plus mean --> total row number: 4*scenario number]
        crash_final = crash_final.reshape(len(world)*(run_nr+1),3)
        crash_dict.update({j:crash_final})

    return crash_dict

#----------------------------------------------------------------------------------------------------------------------------------

def projected_distance(crash_dict,fp_ENU,location,world):
    '''This function calculates the projected distance from the crash location on to the intended flight path.
     It returns the projected distances of each scenario mean and for ever location in a data frame'''

    ###Projected Distance 

    ##Data Frame Creation
    summary = pd.DataFrame(index=np.arange(len(location)),columns = np.arange(len(world)))
    summary = pd.DataFrame(index = location,columns = world)

    ##Iterates through the different locations
    for i in location:
        means = range(3,crash_dict[i].shape[0],4)
        ##Select mean north&east coordinates of each szenario
        vec_3d = crash_dict[i][means]
        vec_2d = vec_3d[:,0:2]
        ##Select north&east coordinates of flight plan
        fp_2d = np.array(fp_ENU[i].iloc[1,:])[1:3]

        ##Calculate angle between the two vectors
        dot = np.dot(vec_2d,fp_2d)
        vec_2d_len = np.sqrt(np.sum(vec_2d*vec_2d,axis=1))
        fp_2d_len = np.sqrt((fp_2d*fp_2d).sum())
        cos_angle = dot/(vec_2d_len*fp_2d_len)
        angle = np.arccos(cos_angle)
        angle_deg = (angle*180)/np.pi

        ##Projected Distance on Flight Path
        proj_dist = vec_2d_len*np.cos(angle)
        summary.loc[i] = proj_dist

    return summary

#---------------------------------------------------------------------------------------------------------------------

##Scenario Variation: Descriptive Statistics of distance to crash site between the runs of one scenario
def run_statistics(location,world,crash_dict):
    '''Function to save a .csv file with metrics from the descriptive statistics for each scenario. A file is saved for each location.'''
    for i in location:
        means = range(3,crash_dict[i].shape[0],4)
        ##Select mean north&east coordinates of each szenario
        vec_3d_nomean = np.delete(crash_dict[i], means, 0)
        vec_2d_nomean = vec_3d_nomean[:,0:2]
        dist_2d_nomean = np.sqrt(vec_2d_nomean[:,0]**2+vec_2d_nomean[:,1]**2)
        dist_2d_nomean = dist_2d_nomean.reshape(13,3)
        minimum = np.min(dist_2d_nomean,1)
        maximum = np.max(dist_2d_nomean,1)
        variation = maximum-minimum
        mittelwert = np.mean(dist_2d_nomean,1)
        standardabw = np.sqrt(np.var(dist_2d_nomean,1))
        median = np.median(dist_2d_nomean,1)
        DATA_VAR = pd.DataFrame({'Scenario':world,
                                'Minimum':minimum,
                                'Maximum':maximum,
                                'Variation':variation,
                                'Mean':mittelwert,
                                'Median':median,
                                'SD':standardabw})
        pd.DataFrame.to_csv(DATA_VAR,'./Plots/distance_statistics_'+i+'_.csv',sep=';')


#-------------------------------------------------------------------------------------------------------------------------