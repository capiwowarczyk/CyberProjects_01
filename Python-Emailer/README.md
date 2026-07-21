# Python Automated Email Sender

A lightweight Python automation script designed to construct and securely send formatted emails via SMTP using SSL encryption. The script utilizes Python's built-in `smtplib`, `ssl`, and `email.message` modules to communicate with secure mail servers (such as Gmail's SMTP server).

---

## Features

- **Secure SSL Transmission**: Connects over port 465 using `ssl.create_default_context()` for encrypted, secure communication (`SMTP_SSL`).
- **Standardized MIME Formatting**: Uses Python's native `EmailMessage` class to cleanly build email headers (`From`, `To`, `Subject`) and body content.
- **Externalized Credential Support**: Includes support for modular credential management via an external configuration/password module (`appPass`).
- **Clean Resource Management**: Employs context managers (`with smtplib.SMTP_SSL(...)`) to automatically handle socket connections and graceful SMTP teardowns.

---

## Prerequisites

- **Python Version**: Python 3.6 or higher (uses standard library modules: `smtplib`, `ssl`, `email.message`).
- **Email Credentials**: An email account configured for SMTP access.
  - *Note for Gmail Users*: Google requires an **App Password** (2-Step Verification must be enabled) rather than your standard account password.

---

## Installation & Setup

1. **Clone or Download the Script**: Save the script file as `send_email.py`.

2. **Create the Password File**:
   Create a Python file named `appPass.py` in the same directory to securely store your App Password:
   ```python
   # appPass.py
   password = "your_generated_app_password_here"
   ```

3. **Configure Script Parameters**:
   Update `send_email.py` with your sender/receiver email addresses and desired email content:
   ```python
   emailSender = "TEST@email.com"
   emailPassword = #####  # Uses the imported password variable from appPass.py
   emailReceiver = "TEST@email.com"
   subject = "This is a test email"
   body = """
   When you check out my programs, I hope you enjoy them!
   """
   ```

---

## Usage Instructions

Run the script from your terminal or command prompt:

```bash
python send_email.py
```

---

## Code Breakdown

```python
# This is a python program of mine to Create and send Emails for me!

# importing required libraries and variables
import ssl, smtplib
from email.message import EmailMessage
from appPass import password

# define all the variables required to send the email
emailSender = "TEST@email.com"
emailPassword = password  # Assigned from the imported appPass module
emailReceiver = "TEST@email.com"  # Input who will receive the email here
subject = "This is a test email"
body = """ 
When you check out my programs, I hope you enjoy them!
"""

# formatting the email with the email.message library
em = EmailMessage()
em["From"] = emailSender
em["To"] = emailReceiver
em["subject"] = subject
em.set_content(body)

context = ssl.create_default_context()

# sending email
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
    smtp.login(emailSender, emailPassword)
    smtp.sendmail(emailSender, emailReceiver, em.as_string())
```

---

## Security Best Practices

- **Never Hardcode Passwords**: Avoid placing plain-text passwords directly into main execution scripts or committing them to source control (e.g., GitHub).
- **Git Ignore Sensitive Files**: Add `appPass.py` (and any `.env` or credential files) to your `.gitignore` file:
  ```text
  appPass.py
  __pycache__/
  ```
- **SMTP Server Configuration**:
  - **Gmail**: Host `smtp.gmail.com`, Port `465` (SSL) or `587` (STARTTLS).
  - **Outlook / Office 365**: Host `smtp.office365.com`, Port `587` (STARTTLS).
  - **Yahoo**: Host `smtp.mail.yahoo.com`, Port `465` (SSL).

---

## License

MIT License. Free to use, adapt, and integrate into larger automation and notification workflows.
