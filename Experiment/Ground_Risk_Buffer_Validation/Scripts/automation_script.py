######
#Date: 19.12.2022
##Version Log:
#-2 Nested For-Loop (iterating through scenarios & multiple runs)
#-Linux Bash script no longer used to boot PX4
#-World Files on VM used to set up Wind Scenarios
#-World Files addressed through SSH commands from this script
#-Log Files saved with unique file name
#-PX4 shutdown is controlled by the mission script, no longer by this script
######

import os
import time
from paramiko import SSHClient, AutoAddPolicy
import mission_script_GRB_validation as mission
import asyncio

world = ['biel','biel_NL','biel_NM','biel_NH','biel_SL','biel_SM','biel_SH',
        'biel_SEL','biel_SEM','biel_SEH','biel_NWL','biel_NWM','biel_NWH']


runs = 3

for i in range(0,len(world),1):

    print('---------------RUN Scenario '+world[i]+'----------------------------')

    for j in range(1,runs+1,1):

        print('---------------RUN '+str(j)+' Starts----------------------------')

        ## Connect to VM
        client = SSHClient()

        #Load Authentification Keys
        client.load_system_host_keys()

        #Known_host policy
        client.set_missing_host_key_policy(AutoAddPolicy())

        ### ADD YOUR USERNAME AND IP ADDRESS OF YOUR MACHINE CONTAINING THE SIMULATOR (PX4 AND GAZEBO)
        #Connecting
        client.connect('YOUR_IP_ADDRESS', username='USERNAME') #Add your the IP address of the machine you want to SSH and the username
        print("Connected to VM")

        #Start PX4 
        print("PX4 is booting....")
        stdin, stdout, stderr = client.exec_command('cd ./PX4/PX4-Autopilot; make px4_sitl gazebo_matrice_300__'+world[i])
        time.sleep(20)
        print("PX4 booted")

        #---------------------------------------------------------------------------------------------------------------------

        ## Run Mission Script

        flight_plan = 'Flight_Plan_Location1.xlsx'
        log_file = world[i]+'_Run_'+str(j)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(mission.run(flight_plan,log_file))
        
        print("Offboard Script has finished")

        #---------------------------------------------------------------------------------------------------------------------

        ## Close VM

        stdin.close()
        stdout.close()
        stderr.close()
        client.close()
        print("VM deconnected")

        print('---------------RUN '+str(j)+' Finished----------------------------')

print('---------------All scenarios were successfully executed----------------------------')






