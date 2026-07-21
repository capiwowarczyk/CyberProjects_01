# UFW Firewall Hardening Script

A lightweight, robust Bash script designed to automate the configuration and hardening of the Uncomplicated Firewall (UFW) on Linux systems. This script enforces a secure baseline policy ("deny incoming, allow outgoing"), resets legacy rules, explicitly enables essential network services (SSH, HTTP, HTTPS), and turns on system firewall logging.

---

## Key Features

- **Root Privilege Enforcement**: Checks for root or `sudo` execution privileges prior to making system modifications.
- **Dependency Checking**: Verifies that `ufw` is installed on the host before attempting configuration.
- **Interactive Dry-Run / Confirmation**: Displays current UFW status and prompts for explicit user confirmation before applying changes.
- **Default Hardening Policy**:
  - `deny incoming`: Blocks all unsolicited incoming traffic by default.
  - `allow outgoing`: Permits all outbound system traffic.
- **Essential Service Rules**:
  - `SSH` (Port 22/tcp)
  - `HTTP` (Port 80/tcp)
  - `HTTPS` (Port 443/tcp)
- **Logging & Verification**: Enables system logging (`ufw logging on`) and performs a post-configuration health check to verify that the firewall is active and rules are applied.

---

## Prerequisites

- Operating System: Ubuntu/Debian or any Linux distribution supporting `ufw`.
- Required Packages: `ufw`
- Permissions: Root privileges (`sudo` or root user).

---

## Installation & Setup

1. **Save the Script**: Save the script file as `harden_ufw.sh` (or a preferred script name):
   ```bash
   nano harden_ufw.sh
   ```

2. **Make the Script Executable**:
   ```bash
   chmod +x harden_ufw.sh
   ```

---

## Usage

Run the script using `sudo`:

```bash
sudo ./harden_ufw.sh
```

### Execution Flow:

1. **Privilege Check**: Verifies `EUID == 0`. Exits with code `1` if executed as a non-root user.
2. **UFW Check**: Runs `command -v ufw`. Exits with code `1` if UFW is missing.
3. **Status Audit**: Displays `ufw status verbose`.
4. **User Prompt**: Asks `Do you want to apply hardened firewall rules? (y/n):`.
   - If **n** or any non-`y` input: Prints `Audit complete. No changes made.` and exits cleanly (`0`).
   - If **y**: Proceed to configuration.
5. **Rule Reset**: Runs `ufw --force reset` to clean existing configurations.
6. **Apply Hardening Baseline**:
   - `ufw default deny incoming`
   - `ufw default allow outgoing`
7. **Rule Additions**:
   - `ufw allow ssh`
   - `ufw allow http`
   - `ufw allow https`
8. **Logging Activation**: `ufw logging on`
9. **Firewall Enable**: `ufw --force enable`
10. **Validation Check**: Confirms UFW status is active and prints the updated rule matrix.

---

## Code Breakdown

```bash
#!/bin/bash

# Checking to see that the script is being run as the root user
if [[ $EUID -ne 0 ]]; then
    echo "Please run this script as root or using sudo."
    exit 1
fi

# Checking to see if ufw is installed on the system
if ! command -v ufw &> /dev/null; then
    echo "UFW firewall is not installed. Please install it first."
    exit 1
fi

# Showing the current firewall status
echo "Checking current firewall status..."
ufw status verbose

# Asking the user for confirmation
read -p "Do you want to apply hardened firewall rules? (y/n): " choice
if [[ ! $choice =~ ^[Yy]$ ]]; then
    echo "Audit complete. No changes made."
    exit 0
fi

# Resetting the firewall rules
echo "Resetting existing firewall rules..."
ufw --force reset

# Setting secure default policies
echo "Setting default firewall policies..."
ufw default deny incoming
ufw default allow outgoing

# Allowing the essential services
echo "Allowing essential services..."
ufw allow ssh
ufw allow http
ufw allow https

# Enabling Logging
echo "Enabling firewall logging..."
ufw logging on

# Enabling the new firewall rules
echo "Enabling the firewall..."
ufw --force enable

# Confirming the firewall rules were applied correctly
if ufw status | grep -q "Status: active"; then
    echo "Hardened firewall rules applied successfully:"
    ufw status verbose
else
    echo "Something went wrong. Firewall is not active."
fi
```

---

## Security Considerations

- **SSH Port Access**: If your server uses a non-standard SSH port (e.g., `2222`), update `ufw allow ssh` to `ufw allow 2222/tcp` prior to running the script to avoid being locked out.
- **Custom Application Ports**: If running custom network services (databases, API endpoints, internal tools), append the necessary `ufw allow <port>` statements to the script body.
- **Automated Deployments**: For unattended deployments (e.g., CI/CD or cloud-init), remove or bypass the interactive `read -p` prompt.

---

## License

MIT License. Free to use, modify, and distribute for personal and commercial infrastructure security baseline enforcement.
