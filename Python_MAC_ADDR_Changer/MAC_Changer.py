#!/usr/bin/env python

#this is a simple MAC address changer for linux

import subprocess
import optparse

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Interface to change its MAC address")
    parser.add_option("-m", "--mac", dest="new_mac", help="New MAC address") #these two lines are adding arguments to be preformed in the linux termenal
    (options, arguments) = parser.parse_args()
    if not options.interface:
        parser.error("[-] Plese specify a interface, use --help for more info") #error checking
    elif not options.new_mac:
        parser.error("[-] Plese specify a new MAC, use --help for more info") #error checking
    return options

def change_mac(interface, new_mac): #this function is running the commands nesscary in the termnal to change the MAC address
    print("[+] Changing MAC address for " + interface + " to: " + new_mac)
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
    subprocess.call(["ifconfig", interface, "up"])

options = get_arguments()
change_mac(options.interface, options.new_mac)

