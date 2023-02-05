# Simulator Automation Requirements (SSH Setup)

The following documentation describes the requirements, which are necessary to use the [mavsdk_automation_script.py](../Scripts/mavsdk_mission_automation.py).

1. Installing SSH-Client on Ubuntu virtual machine with command `sudo apt-get install openssh-client`

2. Install SSH-Server on Windows host machine and set up *ssh public key authentification* for Windows where the Windows host has admin right (see [video](https://www.youtube.com/watch?v=Wx7WPDnwcDg&list=PLbSx61FnjmwrobiaKpInjFYFvuqsyuGEa&index=23&ab_channel=WilliamCampbell))

3. Installing SSH also the other way to reach the virtual Linux machine from the Windows host. Install SSH-client on the Windows host through activating the optional feature. However, SSH-Client should be enables per default on Windows host. On the linux virtual maschine install SSH-Server with `sudo apt install openssh-server`.

4. To enable *public key authentification* enter `ssh-keygen` into Windows command prompt and accept the defaults by pressing enter.

5. As 'ssh-copy-id' command does not exist on Windows, open a PowerShell and type in the following command. In bold please add the name and IP-address of your virtual maschine

```
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh username@ip_address_VM "cat >> .ssh/authorized_keys"
```

6. Set up the command prompt to be able to activate conda virtual environment right from the command prompt
    - Go to the directory `C:\Users\janik\anaconda3\Scripts` inside a command prompt
    - Run `activate.bat`
    - Execute `conda init cmd.exe` to run conda interaction with prompt command. For other terminals (powershell, bash etc.) see help function
    - Close and open the command prompt again
    - Conda virtual environments can now be activated using the same command `conda activate <venv-name>` as in Anaconda command prompt

