# Lab 9: Troubleshooting
## Lab Outline
In this lab, you will set up an intentionally broken environment. You will then have to identify and correct a series of issues to get the network completely up and running as intended. This lab will require good troubleshooting skills. 

## Lab Objective
The objective of this lab is to help you learn how to troubleshoot a network. This is most like what you will experience as most networks you will work with have already been initially configured. This lab will give you an opportunity to put in to practice the skills you have accumulated over the semester.

**Estimated Time:** ~3-4 hours, you have 2 weeks

### Associated Learning Outcomes
 - Computer Networks: Design and implement networks suitable for the flow of information in line with organizational needs
 - Diagnose and Solve Network Problems: Troubleshoot and diagnose common network problems and identify solutions.

---

<div style="page-break-after: always;"></div>

## Instructions
### Create Initial Topology
Your first step is to create this topology in a new GNS3 project. The configurations we want you to paste into each of these devices will be listed below, so don't configure anything yet. 

![topology](lab9-brokenpic.png)

### Copy and Paste PC Configuration
Set the PC IP addresses and default gateways as shown on the diagram with the following commands. You can simply copy and paste the commands into each device. 

>[!note] Copy and Pasting Isn't Working!
>The most common problem is whitespace. Try `Ctrl + Shift + V` to paste just the text.


##### PC1
```
ip 192.168.110.11/24 192.168.110.1
save
```

##### PC2
```
ip 192.168.140.11/24 192.168.140.1
save
```

##### PC3
```
ip 192.168.140.22/24 192.168.140.1
save
```

##### PC4
```
ip 192.168.110.22/24 192.168.110.1
save
```

##### PC5
```
ip 192.168.120.11/24 192.168.120.1
save
```

##### PC6
```
ip 192.168.120.22/24 192.168.120.1
save
```

##### PC7
```
ip 192.168.130.11/24 192.168.130.1
save
```

##### PC8
```
ip 192.168.130.22/24 192.168.130.1
save
```


<div style="page-break-after: always;"></div>

### Copy and Paste Device Configuration
Copy each device's configuration and paste it into the corresponding device's console. You should be able to paste the whole thing at once, and it will run each line like you typed the command.

>[!warning] Paste is normal mode NOT config mode
>Be sure to paste this in the "normal" console mode, not the "config" mode. It will enter the configuration terminal automatically.

These configurations are intentionally broken, but there shouldn't be any immediate error messages. Try again or ask a TA for help if it looks like the configuration didn't work.

>[!bug] COPY RUN START
>Remember to press enter at the end until the save prompt is finished.
#### Switches
##### CTB-ACCESS1
```
vlan database
vlan 110 name Labs
vlan 140 name Students
vlan 999 name PARKING
exit
configure terminal
interface f1/0
switchport mode access
switchport access vlan 110
no shutdown
exit
interface f1/1
switchport mode access
switchport access vlan 140
no shutdown
exit
interface f1/15
switchport mode access
switchport access vlan 110
no shutdown
exit
interface f1/7
switchport mode trunk
switchport trunk allowed vlan 1-2,1002-1005
no shutdown
exit
interface range f1/2 - 6 , f1/8 - 14
switchport mode access
switchport access vlan 999
shutdown
end
copy running-config startup-config
```

##### CTB-ACCESS2
```
vlan database
vlan 110 name Labs
vlan 140 name Students
vlan 999 name PARKING
exit
configure terminal
interface f1/0
switchport mode access
switchport access vlan 140
no shutdown
exit
interface f1/1
switchport mode access
switchport access vlan 110
shutdown
exit
interface f1/15
switchport mode access
switchport access vlan 140
no shutdown
exit
interface f1/7
switchport mode trunk
switchport trunk allowed vlan 1-2,1002-1005
switchport trunk allowed vlan add 110,140
switchport trunk native vlan 999
no shutdown
exit
interface range f1/2 - 6 , f1/8 - 14
switchport mode access
switchport access vlan 999
shutdown
end
copy running-config startup-config
```

##### EB-ACCESS
```
vlan database
vlan 120 name Students
vlan 999 name PARKING
exit
configure terminal
interface range f1/0
switchport mode access
switchport access vlan 120
no shutdown
exit
interface f1/15
switchport mode trunk
switchport trunk allowed vlan 1-2,1002-1005
switchport trunk allowed vlan add 120
switchport trunk native vlan 999
no shutdown
exit
interface range f1/2 - 14
switchport mode access
switchport access vlan 999
shutdown
end
copy running-config startup-config
```

##### MARB-ACCESS
```
vlan database
vlan 130 name Students
vlan 999 name PARKING
exit
configure terminal
interface range f1/0 , f1/1 , f1/15
switchport mode access
switchport access vlan 130
no shutdown
exit
no vlan 130
interface range f1/2 - 14
switchport mode access
switchport access vlan 999
shutdown
end
copy running-config startup-config
```


#### Routers
##### CTB-CORE
```
configure terminal
interface f2/0
ip address 192.168.110.1 255.255.255.0
no shutdown
exit
interface f1/0
ip address 192.168.140.1 255.255.255.0
no shutdown
exit
interface f0/0
no shutdown
exit
interface f0/1
ip address 192.168.100.2 255.255.255.252
no shutdown
exit
interface loopback 1
ip address 1.1.1.1 255.255.255.255
no shutdown
exit
interface range f0/0 - 1
ip ospf authentication message-digest
ip ospf message-digest-key 1 md5 NoTypos!
exit
router ospf 1
network 192.168.100.4 255.255.255.252 area 0
network 192.168.100.0 255.255.255.252 area 0
network 192.168.110.0 255.255.255.0 area 1
network 192.168.140.0 255.255.255.0 area 1
end
copy running-config startup-config
```

##### EB-CORE
```
configure terminal
interface f2/0
ip address 192.168.120.1 255.255.255.0
exit
interface f0/0
ip address 192.168.100.9 255.255.255.252
no shutdown
exit
interface f0/1
ip address 192.168.100.5 255.255.255.252
no shutdown
exit
interface loopback 1
ip address 2.2.2.2 255.255.255.255
no shutdown
exit
interface range f0/0 - 1
ip ospf authentication message-digest
ip ospf message-digest-key 1 md5 NoTypos!
exit
router ospf 1
network 192.168.100.8 255.255.255.252 area 7
network 192.168.100.4 255.255.255.252 area 7
network 192.168.120.0 255.255.255.0 area 1
end
copy running-config startup-config
```

##### MARB-CORE
```
configure terminal
interface f2/0
ip address 192.168.130.1 255.255.255.224
no shutdown
exit
interface f0/0
ip address 192.168.100.1 255.255.255.252
no shutdown
exit
interface f0/1
ip address 192.168.100.10 255.255.255.252
no shutdown
exit
interface loopback 1
ip address 3.3.3.3 255.255.255.255
no shutdown
exit
interface range f0/0 - 1
ip ospf authentication message-digest
ip ospf message-digest-key 1 md5 NoTypos
exit
router ospf 1
network 192.168.100.0 255.255.255.252 area 0
network 192.168.100.8 255.255.255.252 area 0
network 192.168.130.0 255.255.255.0 area 1
end
copy running-config startup-config
```

<div style="page-break-after: always;"></div>

### Fix the Network!
This network is very broken! Almost no PCs will be able to ping each other. Your goal is to fix the network until the PCs can ping each other again. Good luck!

#### Hints
- We tried creating four problems in Layers 1, 2, and 3 for this network, so there are about 12 problems total.
- This network uses OSPF, where the network links in the core comprise area 0, and the outer networks are in area 1.



## Deliverables
Submit a ***PDF*** with the following *screenshots* **and** *answers* on the Learning Suite quiz question 1

### Screenshots (30 points)
- Screenshots of PC1 successfully pinging every other PC (PC1 -> PC2, PC3, PC4, PC5, PC6, PC7, PC8)
- Screenshots of the OSPF neighbors of each core router
- A screenshot of your final topology with all appropriate labels

### Questions (10 points)
- What commands did you run most frequently? How did they help you troubleshoot your network?