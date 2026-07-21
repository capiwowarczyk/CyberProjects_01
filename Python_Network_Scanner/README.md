# ARP Network Scanner

An ARP-based network scanner written in Python using the **Scapy** library. This tool allows users to discover active devices on a local network (LAN) by sending ARP (Address Resolution Protocol) requests and parsing the corresponding responses to map IP addresses to MAC addresses.

---

## Table of Contents
- [Overview](#overview)
- [How It Works](#how-it-works)
- [Prerequisites & Requirements](#prerequisites--requirements)
- [Usage](#usage)
- [Code Breakdown](#code-breakdown)
- [Python 2 vs Python 3 Compatibility](#python-2-vs-python-3-compatibility)
- [Security & Ethical Considerations](#security--ethical-considerations)

---

## Overview

The script is a lightweight command-line utility designed to perform network reconnaissance on a local subnet. By broadcasting ARP requests across a target IP range (or single IP address), it identifies live hosts and retrieves their hardware (MAC) addresses.

### Key Features
- **Target Selection:** Supports single IP addresses (e.g., `192.168.1.1`) or CIDR IP ranges (e.g., `192.168.1.1/24`).
- **Layer 2 Discovery:** Utilizes custom Ethernet frames combined with ARP requests to discover connected devices quickly.
- **Formatted Output:** Displays results in a clean table mapping IP addresses to MAC addresses.

---

## How It Works

1. **Argument Parsing:** The user passes a target IP address or network range via command-line flags (`-t` or `--target`).
2. **Packet Construction:** 
   - Creates an ARP request packet specifying the target IP (`scapy.ARP(pdst=target)`).
   - Creates an Ethernet frame with the broadcast MAC address (`ff:ff:ff:ff:ff:ff`).
   - Combines both into an `Ether / ARP` broadcast packet stack (`broadcast / arp_request`).
3. **Packet Transmission:** Sends the stacked packet at Layer 2 (`scapy.srp()`) with a 1-second timeout and captures responses from active devices on the subnet.
4. **Data Extraction:** Iterates through the received responses, extracting each host's IP (`psrc`) and hardware/MAC address (`hwsrc`).
5. **Output Display:** Prints the gathered results in an aligned tab-separated table.

---

## Prerequisites & Requirements

### Dependencies
- **Python:** Python 2.7 (or Python 3 with slight modifications).
- **Scapy:** Scapy packet manipulation tool/library.

### Installation
Install Scapy via `pip`:

```bash
pip install scapy
```

> **Note:** Root or Administrator privileges (e.g., `sudo`) are required to send raw sockets/Layer 2 packets on most operating systems.

---

## Usage

### Command Syntax

```bash
sudo python network_scanner.py -t <TARGET_IP_OR_RANGE>
```

### Examples

**Scan a single host:**
```bash
sudo python network_scanner.py -t 192.168.1.1
```

**Scan an entire subnet (CIDR notation):**
```bash
sudo python network_scanner.py -t 192.168.1.1/24
```

**Display Help Message:**
```bash
python network_scanner.py --help
```

#### Sample Output

```text
IP			MAC Address 
----------------------------------------------
192.168.1.1		00:11:22:33:44:55
192.168.1.15		aa:bb:cc:dd:ee:ff
192.168.1.42		12:34:56:78:9a:bc
```

---

## Code Breakdown

### 1. Command-Line Argument Parser (`get_arguments`)
```python
def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--target", dest="target", help="Target IP / IP range.")
    options, arguments = parser.parse_args()
    if not options.target:
        parser.error("[-] Please specify an IP target, use --help for more info.")
    return options
```
- Uses `optparse` to define the `-t` / `--target` flag.
- Validates that a target parameter was provided, displaying an error message if missing.

### 2. Network Scanner Core (`scan`)
```python
def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    clients_list = []
    for element in answered_list:
        client_dict = {"IP": element[1].psrc, "MAC": element[1].hwsrc}
        clients_list.append(client_dict)
    return clients_list
```
- **`scapy.ARP(pdst=ip)`**: Prepares an ARP request for the specified IP or range.
- **`scapy.Ether(dst="ff:ff:ff:ff:ff:ff")`**: Prepares an Ethernet broadcast frame.
- **`broadcast / arp_request`**: Combines Ethernet and ARP layers using Scapy's `/` operator.
- **`scapy.srp(...)`**: Sends packet and receives responses at Layer 2. `[0]` extracts the list of answered packets.
- **`element[1].psrc` / `element[1].hwsrc`**: Extracts the source IP and MAC address from the received ARP response packet.

### 3. Output Formatter (`print_result`)
```python
def print_result(results_list):
    print("IP\t\t\tMAC Address \n----------------------------------------------")
    for client in results_list:
        print(client["IP"] + "\t\t" + client["MAC"])
```
- Prints formatted headers and iterates through the list of dictionary results to print each host's IP and MAC address.

---

## Python 2 vs Python 3 Compatibility

The provided script contains a shebang error (`#!/usr/bin/env pyhon` — missing 't') and uses `optparse` (deprecated in modern Python).

To upgrade the script to modern Python 3 standards:
1. Fix shebang to `#!/usr/bin/env python3`.
2. Upgrade `optparse` to `argparse`.
3. Wrap `print` calls in parentheses (`print(...)`).

---

## Security & Ethical Considerations

- **Authorized Use Only:** Network scanning should only be performed on networks you own or have explicit written permission to test.
- **Local Subnet Scope:** ARP requests are non-routable layer 2 packets and will only scan devices within your immediate broadcast domain / local subnet.
