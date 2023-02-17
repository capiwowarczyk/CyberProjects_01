#!/usr/bin/env pyhon

#this is a python network scanner for python 3

import scapy.all as scapy
import arcparse

def get_arguments(): #functions to get arguments from the command line
    parser = arcparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Target IP / IP range.")
    options = parser.parse_args()
    if not options.target:
        parser.error("[-] Please specify and ip target, use --help for more info.")
    return options

def scan(ip):
    arp_request = scapy.ARP(pdst=ip) #creates a ARP packet looking for ip addr
    brodcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") #creates a Ether packet looking for mac addresses
    arp_request_brodcast = brodcast/arp_request
    answered_list = scapy.srp(arp_request_brodcast, timeout=1, verbose=False)[0] #.srp sends packets with a custom Ether part
    #the [0] is assinging the data to a list in the variable answered_list
    #the 2 variabels are for the 2 things being rturned the answered and unanswered packets

    clients_list = []

    for element in answered_list:
        client_dict = {"IP": element[1].psrc, "MAC": element[1].hwsrc}
            # .psrc prints the IP addr of the source .hwsrc prints the MAC addr of the Client
        clients_list.append(client_dict) #each time a dict is mande it is added to clients_list[]
    return clients_list

def print_result(results_list):
    print("IP\t\t\tMAC Address \n----------------------------------------------")
    for client in results_list:
        print(client["IP"] + "\t\t" + client["MAC"])

options = get_arguments()
scan_result = scan(options.target)
print_result(scan_result)