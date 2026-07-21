#This Python Code Can be used to send a text about the local weather at a certan time of the day
#Twilio is being used to send the SMS texts
#With a few alterations of the code that will be labled at the corosponding line you can have this code work for you!

import requests, schedule, logging, os
from twilio.rest import Client  

logging.basicConfig(FileName="WeatherLog.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s") #Setting up the logging required

#Input your Twilio Credentials Here
#NOTE that these variables are left blank so you can input your own credentials and so I do not expose my own 
AccountSid = ""         # Twilio Account SID
AuthToken = ""          # Twilio Auth Token
TwilioPhoneNumber = ""  # Twilio phone number
YourPhoneNumber = ""    # Your phone number

#Input your OpenWeatherMap Information
#Again this area is left blank for the same reasons listed above
ApiKey = ""    #OpenWeatherMap API key
CityName = ""  #City name for your weather information

#This Function will get the weather for your area and send a SMS text
def get_weather_and_send_sms():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CityName}&appid={ApiKey}&units=metric"  #API endpoint URL for weather data
        response = requests.get(url)  #Sending GET request to OpenWeatherMap API
        data = response.json()  #Parsing the JSON response
        
        if data['cod'] == 200:  #Checking if API response is successful
            WeatherDescription = data["weather"][0]["description"]  #Extracting your weather description
            Temperature = data["main"]["temp"]  #Extracting the temperature
            Message = f"The weather in {CityName} is {WeatherDescription} with a temperature of {Temperature}°F."  #Composing SMS message
            send_sms(Message)  #Sending  a SMS with your weather information
            logging.info("Weather message sent successfully.")  #Logging the success message
        else:
            logging.error(f"Error fetching weather data: {data["message"]}")  #Logging error message if API response is not successful
    except Exception as e:
        logging.exception("An error occurred while getting weather data and sending SMS.")  #Logging exception if an error occurs

#This function will send your SMS message using Twilio
def send_sms(message):
    try:
        client = Client(AccountSid, AuthToken)  #Creating  the twilio client instance
        client.messages.create(
            to=YourPhoneNumber,  #The receiver's phone number
            from_=TwilioPhoneNumber,  #Twilio phone number
            body=message  #The SMS message body
        )
    except Exception as e:
        logging.exception("An error occurred while sending SMS.")  #Logging exception if an error occurs while sending a SMS

#Schedule the task to run daily at a specific time
schedule.every().day.at("08:00").do(get_weather_and_send_sms) 

#Keep the script running to execute scheduled tasks
while True:
    schedule.run_pending()  #Running pending scheduled tasks
