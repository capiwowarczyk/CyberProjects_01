# This is a python program of mine to Create and send Emails for me!

#importing requited libaries and variables
import ssl, smtplib
from email.message import EmailMessage
from appPass import password

#define all the vairables required to send the email
emailSender = "carsonautoemail@gmail.com"
emailPassword = password 
emailReceiver = "piwowarczykca@gmail.com" #input who ill reviece the email here
subject = "This is a test email"
body = """ 
When you check out my programs, I hope you enjoy them!
"""

#formatting the email with the email.message libary
em = EmailMessage()
em["From"] = emailSender
em["To"] = emailReceiver
em["subject"] = subject
em.set_content(body)

context = ssl.create_default_context()

#sending email
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
    smtp.login(emailSender, emailPassword)
    smtp.sendmail(emailSender, emailReceiver, em.as_string())
