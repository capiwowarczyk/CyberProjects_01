# HTTP Packet Sniffer

A lightweight Python script designed to capture and analyze unencrypted HTTP network traffic in real time. Built using the **Scapy** library, this tool intercepts network packets on a specified interface, extracts visited URLs, and scans packet payloads for sensitive cleartext information such as login credentials.

---

## Overview

This script acts as a basic passive network analyzer focusing on unencrypted HTTP request packets (`HTTPRequest`). It performs two primary functions:
1. **URL Extraction**: Parses the HTTP request headers to log the requested Host domain and Path.
2. **Credential Inspection**: Scans the raw packet load (`Raw` layer) for common keywords associated with authentication forms (e.g., `username`, `password`, `login`).

---

## Technical Specifications & Dependencies

- **Language**: Python 2.7 (Legacy)
- **Primary Library**: `scapy` (specifically `scapy.all` and `scapy.layers.http`)
- **Execution Level**: Requires administrative/root privileges to put the network interface into promiscuous mode for packet capture.

---

## How It Works

### Code Structure & Logic Flow

1. **`sniff(interface)`**
   - Calls `scapy.sniff()` on the specified network interface (e.g., `eth0`).
   - `store=False`: Ensures captured packets are processed on-the-fly and not held in system memory, preventing excessive memory consumption during extended monitoring sessions.
   - `prn=process_sinffed_packet`: Defines the callback function triggered for every captured packet.

2. **`process_sinffed_packet(packet)`**
   - Checks if the packet contains an `http.HTTPRequest` layer.
   - If present, extracts the full URL via `get_url(packet)` and outputs it to the console.
   - Passes the packet to `get_login_info(packet)` to check for authentication payloads.

3. **`get_url(packet)`**
   - Combines the HTTP request header fields: `Host` + `Path` (e.g., `example.com` + `/login.php` $\rightarrow$ `example.com/login.php`).

4. **`get_login_info(packet)`**
   - Checks if the packet contains a raw data layer (`scapy.Raw`).
   - Iterates through a defined list of authentication keywords: `["username", "login", "user", "password", "pass"]`.
   - If a keyword match is found within the payload string, the function returns the payload data containing potential credentials.

---

## Usage

### 1. Prerequisites
Ensure `scapy` is installed for Python 2.7:
```bash
pip install scapy
```

### 2. Execution
Run the script with superuser / root privileges:
```bash
sudo python sniffer.py
```

### 3. Target Interface Configuration
Modify the entry point at the bottom of the script to match your target network adapter:
```python
sniff("eth0")  # Replace 'eth0' with your target interface (e.g., wlan0, en0)
```

---

## Disclaimer & Security Context

This script relies on unencrypted HTTP protocol inspection. Traffic secured via TLS/SSL (HTTPS) will be encrypted at the transport layer and cannot be read in plain text using raw layer inspection without intermediary decryption (e.g., SSL/TLS proxying).

*Note: This tool is intended solely for educational purposes, security analysis, and authorized network troubleshooting on networks where permission has been explicitly granted.*
