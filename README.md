# SmarterSecurityCamera-MVSense
A program for filtering person detection from MV smart cameras based on if you are home or not. 

By remembering a few network / bluetooth devices that you usually take with you when you leave the house, the program can check if you are likely home or not when it sees a 'person'

## Setup
The program will guide you through setup, but you need to do a few things first:
1. Enable Meraki API access, store your api key somewhere safe.  https://documentation.meraki.com/zGeneral_Administration/Other_Topics/The_Cisco_Meraki_Dashboard_API
2. Enable MVSense for the target camera. Record the cameras serial. (If your camera supports MVSense, you should have 10 free licenses.)
3. Run monitorMV.py


## Future plans
* Thread client detail parsing to improve speed. 
* Implement Webhooks to allow processing of motion events. 
* Implement email notifications. 
* Actual GUI. 
