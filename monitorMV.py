# Author: Andrew Afonso
# Github: https://github.com/andrewbluepiano/SmarterSecurityCamera-MVSense
import requests
import os
import time
import logging
import json
import sys
#pprint used for debugging
#import pprint

class config:
    # Defines config information
    def __init__(self):
        self.trusted = []
        self.apikey = ""
        self.cameraSerial = ""
        self.networkID = ""
    
    # Runs user through first time setup. Stores configuration information in a file config.json.
    def setup(self):
        print("First time?\n Lets get things set up. \n")
        self.apikey = input('Enter your API Key: ')
        self.cameraSerial = input('Enter the target MV camera\'s serial: ')

        print("Lets find your network ID\n~~~\nListing your organizations:")
        
        # Queries dashboard for organizations using that API key, and lists them out to the user to select the target.
        orgs = requests.get( 'https://api.meraki.com/api/v0/organizations',
           headers={'x-cisco-meraki-api-key': self.apikey, 'Accept': 'application/json'}
        )
        if orgs.text == " ":
            # Query will return empty if the API key is incorrect.
           print("Uoho, something is wrong with the API key you entered.")
           sys.exit(0)
        else:
           organizations = json.loads(orgs.text)
           count=1
           for org in organizations:
               print(str(count) + "- Name: " + org["name"] + "  ID: " + org["id"])
               count+=1
        targetorg = organizations[int(input("\n\nEnter number for target organization: "))-1]["id"]
        
        # Queries dashboard for list of networks in the selected organization. Asks user to pick the correct one.
        networksget = requests.get( 'https://api.meraki.com/api/v0/organizations/' + targetorg + '/networks',
           headers={'x-cisco-meraki-api-key': self.apikey, 'Accept': 'application/json'}
        )
        if networksget.text == " ":
           print("Hmm, something is wrong with that organization.")
           sys.exit(0)
        else:
           print("~~~~\nHere are the networks in that organization: ")
           networks = json.loads(networksget.text)
           count=1
           for network in networks:
               print(str(count) + "- Name: " + network["name"])
               count+=1
               
        self.networkID = networks[int(input('\n\nEnter the target network\'s ID: '))-1]["id"]
        netidtest = requests.get(
           'https://api.meraki.com/api/v0/networks/' + self.networkID,
           headers={'x-cisco-meraki-api-key': self.apikey, 'Accept': 'application/json'},
        )
        if netidtest.text == " ":
           print("Uoho, something is wrong with that network.")
           sys.exit(0)
           
        # Asks the user to enter the MAC addresses of the trusted devices.
        print("~~~~\nEnter on-person device's MAC addresses, one per line. Press enter or enter \"done\" when done.\n")
        while True:
           newtrust = input('MAC: ').lower()
           if newtrust == "" or newtrust == "done":
               break
           else:
               self.trusted.append(newtrust)
        with open('config.json', 'w') as newConfig:
           json.dump(self.getList(), newConfig)
    
    # Loads information from an existing config.json file.
    def loadConfig(self):
        configFile = open('config.json', 'r')
        tempConfig = json.load(configFile)
        self.trusted = tempConfig["trusted"]
        self.apikey = tempConfig["apikey"]
        self.cameraSerial = tempConfig["cameraSerial"]
        self.networkID = tempConfig["networkID"]
        configFile.close()
        
    # Converts the config data into a single list.
    def getList(self):
        return {"trusted" : self.trusted, "apikey" : self.apikey, "cameraSerial" : self.cameraSerial, "networkID" : self.networkID}

def main():
    appConfig = config()
#    pp = pprint.PrettyPrinter(indent=4)
    LOG_FILENAME = 'motionData.log'
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(filename=LOG_FILENAME, format=FORMAT)
    if not os.path.isfile('config.json'):
        appConfig.setup()
    else:
        checkLoad = input("Existing configuration detected, continue with that? [yes/no]: ").lower()
        if checkLoad == "yes" or checkLoad == "":
            appConfig.loadConfig()
        if checkLoad == "no":
            sys.exit(0)
    
    # The main loop. Checks if the camera detects a person, if so, check if any trusted devices are on the network. If not, alert.
    while True:
        try:
            # Query camera for person count.
            zones = requests.get( 'https://api.meraki.com/api/v0/devices/' + appConfig.cameraSerial + '/camera/analytics/live',
                headers={'x-cisco-meraki-api-key': appConfig.apikey, 'Accept': 'application/json'}
            )
            
            people = json.loads(zones.text)
            
#            print(zones.url)
#            pp.pprint(people)

            for values in people["zones"]:
                if int(people["zones"][values]["person"]) > 0:
                    # If a person is detected, then check if the trusted devices are on the network.
                    wificlientsget = requests.get(
                        'https://api.meraki.com/api/v0/networks/' + appConfig.networkID + '/clients',
                        headers={'x-cisco-meraki-api-key': appConfig.apikey, 'Accept': 'application/json'},
                        params={'timespan' : '1800'}
                    )
                    bluetoothclientsget = requests.get(
                        'https://api.meraki.com/api/v0/networks/' + appConfig.networkID + '/bluetoothClients',
                        headers={'x-cisco-meraki-api-key': appConfig.apikey, 'Accept': 'application/json'},
                        params={'timespan' : '60'}
                    )
                    
                    wifiClients = json.loads(wificlientsget.text)
                    bluetoothClients = json.loads(bluetoothclientsget.text)
                    
#                    print(wificlientsget.url)
#                    print(wificlientsget.text)
#                    pp.pprint(wifiClients)
#                    pp.pprint(bluetoothClients)
                    
                    notify = 1
                    
                    for client in wifiClients:
                        if client["status"] != "Offline" and client["mac"] in appConfig.trusted:
                            notify = 0
                    
                    for client in bluetoothClients:
                        if client["mac"] in appConfig.trusted:
                            notify = 0
                    
                    # What happens if a warnable person is detected. Ideal place to start customizations.
                    if notify == 1:
                        logging.warning('Warnable Person Detected')
                        print("Warnable Person Detected")
        except KeyError as e:
            print("Oops, but not really (KeyError): " + str(e))

if __name__ == "__main__":
    main()
