# MAC Address Changer for Linux

A Python tool for Linux systems designed to safely modify and verify Network Interface Card (NIC) MAC addresses using standard system utilities (`ifconfig`).
---

## Features

- **Command-Line Interface:** Easy-to-use CLI options via `optparse`.
- **Validation & Verification:** Automatically reads the MAC address before and after execution to verify successful changes.
- **Secure Execution:** Utilizes list-based `subprocess` calls to prevent shell injection vulnerabilities.
- **Regex Parsing:** Uses regular expressions to extract MAC addresses from system output reliably.

---
## Prerequisites & Requirements

- **Operating System:** Linux (Debian, Kali, Ubuntu, Arch, etc.)
- **Python Version:** Python 2.7 (or Python 3 with minor syntax adjustments)
- **Required System Tools:** `net-tools` (provides the `ifconfig` command)
- **Privileges:** Root / Superuser privileges (`sudo`) required to alter network interface configurations.

---

## Installation & Setup

1. **Clone or Download the Script:**
   Save the Python script as `mac_changer.py`.

2. **Make the Script Executable:**
   ```bash
   chmod +x mac_changer.py
   ```

3. **Install Dependencies (if needed):**
   Ensure `ifconfig` is installed on your Linux system. On Debian/Ubuntu based systems:
   ```bash
   sudo apt-get install net-tools
   ```

---

## Usage

Run the script with superuser permissions, specifying the target interface (`-i` / `--interface`) and the desired MAC address (`-m` / `--mac`).

### Basic Command Syntax

```bash
sudo ./mac_changer.py -i <interface> -m <new_mac_address>
```

### Example

To change the MAC address of interface `eth0` to `00:11:22:33:44:55`:

```bash
sudo ./mac_changer.py -i eth0 -m 00:11:22:33:44:55
```

### Display Help Options

```bash
./mac_changer.py --help
```

---

## How It Works

1. **Argument Parsing (`get_arguments`):** Captures user inputs for the interface and MAC address. Validates that both required arguments are provided.
2. **Current MAC Retrieval (`get_current_mac`):** Executes `ifconfig <interface>` and uses regular expressions (`\w\w:\w\w:\w\w:\w\w:\w\w:\w\w`) to extract the active MAC address.
3. **MAC Address Modification (`change_mac`):**
   - Brings the network interface down: `ifconfig <interface> down`
   - Modifies the hardware address: `ifconfig <interface> hw ether <new_mac>`
   - Brings the network interface back up: `ifconfig <interface> up`
4. **Verification:** Reads the MAC address again and compares it against the requested MAC address to confirm the change succeeded.
---

## Code Overview

```python
#!/usr/bin/env python

import subprocess
import optparse
import re

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Interface to change its MAC address")
    parser.add_option("-m", "--mac", dest="new_mac", help="New MAC address")
    (options, arguments) = parser.parse_args()
    if not options.interface:
        parser.error("[-] Please specify an interface, use --help for more info")
    elif not options.new_mac:
        parser.error("[-] Please specify a new MAC, use --help for more info")
    return options

def change_mac(interface, new_mac):
    print("[+] Changing MAC address for " + interface + " to: " + new_mac)
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
    subprocess.call(["ifconfig", interface, "up"])

def get_current_mac(interface):
    ifconfig_result = subprocess.check_output(["ifconfig", interface])
    mac_address_search_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", ifconfig_result)

    if mac_address_search_result:
        return mac_address_search_result.group(0)
    else:
        print("[-] Could not read MAC address.")

options = get_arguments()

current_mac = get_current_mac(options.interface)
print("Current MAC = " + str(current_mac))

change_mac(options.interface, options.new_mac)

current_mac = get_current_mac(options.interface)
if current_mac == options.new_mac:
    print("[+] MAC address was successfully changed to " + current_mac)
else:
    print("[-] MAC address did not get changed.")
```

---

## Disclaimer

This tool is intended strictly for educational, security research, and authorized testing purposes. Always obtain proper authorization before altering network configurations on production or shared systems.
