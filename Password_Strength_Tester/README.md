# Password Strength Checker Script

A lightweight, secure Bash script designed to evaluate the strength and complexity of a user-provided password against standard security policy requirements and dictionary checks.

---

## Key Features

- **Secure Masked Input**: Uses `read -sp` to prompt for the password without echoing characters to the terminal screen.
- **Whitespace Sanitization**: Trims all spaces using `tr -d '[:space:]'` to prevent accidental spacing issues during evaluation.
- **Complexity Validations**:
  - **Minimum Length**: Enforces a minimum length of at least 8 characters (`${#password} >= 8`).
  - **Uppercase Letter**: Checks for at least one uppercase character (`[A-Z]`).
  - **Lowercase Letter**: Checks for at least one lowercase character (`[a-z]`).
  - **Numeric Digit**: Checks for at least one number (`[0-9]`).
  - **Special Character**: Checks for at least one symbol (`[!@#$%^&*()_+-]`).
- **Dictionary Word Lookup**: Cross-references the input password against the system dictionary (`/usr/share/dict/words`) to block standard dictionary words.
- **Instant Visual Feedback**: Uses clear emoji indicators (❌ for failure, ✅ for success) with distinct exit codes (`1` for invalid passwords, `0` for valid passwords).

---

## Prerequisites

- **Operating System**: Linux / Unix-like environment (Ubuntu, Debian, Fedora, RHEL, macOS with Bash).
- **Optional Dependency**: Standard dictionary word list at `/usr/share/dict/words` (typically provided by packages like `wamerican`, `wbritish`, or `words`).

---

## Installation & Setup

1. **Save the Script**: Save the script file as `check_password.sh`:
   ```bash
   nano check_password.sh
   ```

2. **Make the Script Executable**:
   ```bash
   chmod +x check_password.sh
   ```

---

## Usage Instructions

Run the script from your terminal:

```bash
./check_password.sh
```

### Execution Flow:

1. **Prompt**: Asks the user to enter a password silently.
2. **Sanitize**: Strips whitespace characters from the string.
3. **Sequential Rule Evaluation**:
   - Length $\ge 8$
   - Uppercase present
   - Lowercase present
   - Digit present
   - Special symbol present
4. **Dictionary Check**: If `/usr/share/dict/words` exists, runs `grep` to verify the password is not an exact dictionary word match.
5. **Output Verdict**: Prints `✅ Password passed all strength checks!` upon satisfying all rules, or prints a specific `❌` error message and exits (`exit 1`) on the first failed check.

---

## Code Breakdown

```bash
#!/bin/bash
# This is a bash script that checks the strength of a given password

read -sp "Enter a password to check: " password # Prompting the user to input a password
echo

# Removing any whitespace
password=$(echo "$password" | tr -d '[:space:]')

# This if statement is checking if it meets the minimum length of 8 characters
if [ "${#password}" -lt 8 ]; then
    echo "❌ Password is too short. Must be at least 8 characters."
    exit 1
fi

# Checking to see if the password contains at least one capital letter
if ! [[ "$password" =~ [A-Z] ]]; then
    echo "❌ Password must contain at least one uppercase letter."
    exit 1
fi

# Checking to see if there is at least one lowercase letter
if ! [[ "$password" =~ [a-z] ]]; then
    echo "❌ Password must contain at least one lowercase letter."
    exit 1
fi

# Checking to see if the password contains at least one number
if ! [[ "$password" =~ [0-9] ]]; then
    echo "❌ Password must contain at least one number."
    exit 1
fi

# Checking to see if the password contains at least one special character
if ! [[ "$password" =~ [\!\@\#\$\%\^\&\*\(\)\_\+\-] ]]; then
    echo "❌ Password must contain at least one special character."
    exit 1
fi

# Checking the password that the user gave against a given list of words
# This line will only work if you have the correct dictionary on your system
if [ -f /usr/share/dict/words ]; then
    if grep -i -w -x "$password" /usr/share/dict/words > /dev/null; then
        echo "❌ Password is a dictionary word. Choose something more unique."
        exit 1
    fi
fi

echo "✅ Password passed all strength checks!"
```

---

## Security & Operational Notes

- **Masked Input Handling**: The `read -sp` command prevents shoulder surfing during interactive execution.
- **Customizing Requirements**: You can easily increase minimum length requirements (e.g., to 12 or 16 characters) by modifying `[ "${#password}" -lt 8 ]` to `12` or `16`.
- **Securing Word Lists**: To test against known breached passwords (e.g., SecLists / RockYou), update the dictionary file path in the `grep` statement to point to your custom wordlist file.

---

## License

MIT License. Free to use, modify, and distribute for security awareness training, internal policy enforcement, and scripting toolkits.
