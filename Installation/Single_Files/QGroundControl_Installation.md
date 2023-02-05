# QGroundControl Installation

For the following documentation, AirSim must be installed and successfully embedded in an Unreal environment. Furthermore, PX4-Autopilot must be installed and tested successfully. 

1. Download and install QGroundControl from their [website](http://qgroundcontrol.com/).

>**NOTE:** QGroundControl should be automatically connect with PX4 when both use default settings. If QGroundControl will not automatically connect with PX4 continue with step 2. 

2. In Linux open a new terminal and check the IP-address of the VM with the command `ip address show`. It gives you the output below from which you have to copy the IP-address `inet 192.16.123.122`. 

```
6: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:15:5d:05:cc:3c brd ff:ff:ff:ff:ff:ff
    inet 192.16.123.122/20 brd 192.16.126.255 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fe80::215:5dff:fe05:cc3c/64 scope link
       valid_lft forever preferred_lft forever
```


3. Open QGroundControll and go to Application Settings --> Comm Links
4. Create a new Comm Link via *Add* and enter the information from the picture below

![](./pictures/qgroundcontrol_setup.png)

>**NOTE:** The *Listening Port 18570* is the local port on the linux side to which PX4 broadcasts the MAVLink messages. The *target host* contains the IP-address of the VM, which was copied in step 2.

5. Confirm with *OK* and activate the connection with *Connect*. The PX4 controller and the Unreal simulation can then be started and the QGroundControll should connect to the PX4.
