#!/bin/bash

#Checking to see that the script is being run as the root user
if [[ $EUID -ne 0 ]]; then
    echo "Please run this script as root or using sudo."
    exit 1
fi

#Checking to see if ufw is installed on the system
if ! command -v ufw &> /dev/null; then
    echo "UFW firewall is not installed. Please install it first."
    exit 1
fi

#Showing the current firewall status
echo "Checking current firewall status..."
ufw status verbose

#Asking the user for conformation
read -p "Do you want to apply hardened firewall rules? (y/n): " choice
if [[ ! $choice =~ ^[Yy]$ ]]; then
    echo "Audit complete. No changes made."
    exit 0
fi

#Resetting the firewall rules
echo "Resetting existing firewall rules..."
ufw --force reset

#Setting secure default policies
echo "Setting default firewall policies..."
ufw default deny incoming
ufw default allow outgoing

#Allowing the essential services
echo "Allowing essential services..."
ufw allow ssh
ufw allow http
ufw allow https

#Enabling Logging
echo "Enabling firewall logging..."
ufw logging on

#Enabling the new firewall rules
echo "Enabling the firewall..."
ufw --force enable

#Confirming the firewall rules were applied correctly if not it will show a error message
if ufw status | grep -q "Status: active"; then
    echo "Hardened firewall rules applied successfully:"
    ufw status verbose
else
    echo "Something went wrong. Firewall is not active."
fi
