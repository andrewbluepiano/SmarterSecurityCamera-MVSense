# SmarterSecurityCamera-MVSense
A program for filtering person detection from MV smart cameras based on if you are home or not. 

By remembering a few network / bluetooth devices that you usually take with you when you leave the house, the program can check if you are likely home or not when it sees a 'person'

## Setup
The program will guide you through setup, but you need to do a few things first:
1. Enable Meraki API access, store your api key somewhere safe.  https://documentation.meraki.com/zGeneral_Administration/Other_Topics/The_Cisco_Meraki_Dashboard_API
2. Enable MVSense for the target camera. Record the cameras serial. (If your camera supports MVSense, you should have 10 free licenses.)
3. Run monitorMV.py

## Output
Currently the program simply writes to a .log file, 'motionData.log', when a person is detected, and it determines you are away from home. <br>
I decided against including code for email notifications in this version, as doing so requires linking an SMTP server to the application, and if you can figure out how to do that for whatever email service you use, you can likely implement that funcionality in the program yourself. <br>
The main purpose of the program is to provide the actual filtering of alerts in such a way that allows the end user to take whatever actions they may want using the data. 


## Future plans
* Thread client detail parsing to improve speed. 
* Implement Webhooks to allow processing of motion events. 
* Implement email notifications. 
* Actual GUI. 
