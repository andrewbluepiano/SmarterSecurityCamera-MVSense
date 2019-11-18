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

def main():
    trusted = []
#    pp = pprint.PrettyPrinter(indent=4)
    LOG_FILENAME = 'motionData.log'
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(filename=LOG_FILENAME, format=FORMAT)
    
    if not os.path.isfile('trusted.txt'):
        print("You should have a file named trusted.txt that lists your on-person devices MAC addresses, one per line.")
        sys.exit(0)
    else:
        trustfile = open('trusted.txt', 'r')
        trustedAll = trustfile.read().splitlines()
        trustfile.close()
    print("Trusted devices MAC addresses:")
    for x in trustedAll:
        trusted.append(x.lower())
        print(x.lower())
    print("")
    
    if not os.path.isfile('apikey.txt'):
        print("You should have a file named apikey.txt that contains your api key.")
        sys.exit(0)
    else:
        apifile = open('apikey.txt', 'r')
        apikey = apifile.read().splitlines()
        apikey = apikey[0]
        apifile.close()
        
    if not os.path.isfile('camera.txt'):
        print("You should have a file named camera.txt that contains your cameras serial.")
        sys.exit(0)
    else:
        camerafile = open('camera.txt', 'r')
        cameraSerial = camerafile.read().splitlines()
        cameraSerial = cameraSerial[0]
        camerafile.close()
        
    if not os.path.isfile('networkid.txt'):
        print("You should have a file named networkid.txt that contains the target networks id.")
        sys.exit(0)
    else:
        networkfile = open('networkid.txt', 'r')
        networkID = networkfile.read().splitlines()
        networkID = networkID[0]
        networkfile.close()
    
    while 1==1:
        try:
            zones = requests.get( 'https://api.meraki.com/api/v0/devices/' + cameraSerial + '/camera/analytics/live',
                headers={'x-cisco-meraki-api-key': apikey, 'Accept': 'application/json'}
            )
            
            people = json.loads(zones.text)
            
#            print(zones.url)
#            pp.pprint(people)

            for values in people["zones"]:
                #If a person is detected
                if int(people["zones"][values]["person"]) > 0:
                    wificlientsget = requests.get(
                        'https://api.meraki.com/api/v0/networks/' + networkID + '/clients',
                        headers={'x-cisco-meraki-api-key': apikey, 'Accept': 'application/json'},
                        params={'timespan' : '1800'}
                    )
                    bluetoothclientsget = requests.get(
                        'https://api.meraki.com/api/v0/networks/' + networkID + '/bluetoothClients',
                        headers={'x-cisco-meraki-api-key': apikey, 'Accept': 'application/json'},
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
#                        print(client["mac"])
                        if client["status"] != "Offline" and client["mac"] in trusted:
#                            pp.pprint(client)
                            notify = 0
                    
                    for client in bluetoothClients:
#                        print(client["mac"])
                        if client["mac"] in trusted:
#                            pp.pprint(client)
                            notify = 0
                    
                    if notify == 1:
                        logging.warning('Warnable Person Detected')
                        print("Warnable Person Detected")
        except KeyError as e:
            print("Oops, but not really (KeyError): " + str(e))

if __name__ == "__main__":
    main()
