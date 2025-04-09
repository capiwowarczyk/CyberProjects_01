#!/bin/bash
#This is a bash script that checks the strength of a given password

read -sp "Enter a password to check: " password #Prompting the user to input a password
echo

#Removing any whitespace
password=$(echo "$password" | tr -d '[:space:]')

#This if statement is checking if it meets the minimum legenth of 8 characters
if [ "${#password}" -lt 8 ]; then
    echo "❌ Password is too short. Must be at least 8 characters."
    exit 1
fi

#Checking to see if the password contains at least one capital letter
if ! [[ "$password" =~ [A-Z] ]]; then
    echo "❌ Password must contain at least one uppercase letter."
    exit 1
fi

#Checking to see if there is at least one lowercase letter
if ! [[ "$password" =~ [a-z] ]]; then
    echo "❌ Password must contain at least one lowercase letter."
    exit 1
fi

#Checking to see if the passowrd contains at least one number
if ! [[ "$password" =~ [0-9] ]]; then
    echo "❌ Password must contain at least one number."
    exit 1
fi

#Checking to see if the password contains at least one special character
if ! [[ "$password" =~ [\!\@\#\$\%\^\&\*\(\)\_\+\-] ]]; then
    echo "❌ Password must contain at least one special character."
    exit 1
fi

#Checking the passowrd that the user gave aginst a given list of words
#This line will only work if you have the correct diconary on your system
if [ -f /usr/share/dict/words ]; then
    if grep -i -w -x "$password" /usr/share/dict/words > /dev/null; then
        echo "❌ Password is a dictionary word. Choose something more unique."
        exit 1
    fi
fi

echo "✅ Password passed all strength checks!"
