# Scheduled Weather SMS Alert System

A Python automation script that fetches live local weather updates from the OpenWeatherMap API and sends daily SMS notifications to a specified phone number using the Twilio REST API. 

---

## Features

- **Automated Daily Scheduling**: Leverages Python's `schedule` library to run automatically at a specific time every day (default set to 08:00 AM).
- **Live Weather Integration**: Connects to OpenWeatherMap's REST API to retrieve real-time weather conditions and temperature.
- **SMS Alerts via Twilio**: Sends customized text messages directly to your mobile device using Twilio's messaging service.
- **Activity Logging**: Records all successful transmissions, API errors, and runtime exceptions into a local `WeatherLog.txt` log file for debugging and monitoring.

---

## Prerequisites

- **Python Version**: Python 3.7 or higher.
- **Third-Party Libraries**: Install required packages via `pip`:
  ```bash
  pip install requests schedule twilio
  ```
- **API Accounts & Credentials**:
  - **OpenWeatherMap Account**: An active API key from [OpenWeatherMap](https://openweathermap.org/api).
  - **Twilio Account**: Account SID, Auth Token, and an active Twilio Phone Number from [Twilio](https://www.twilio.com/).

---

## Configuration & Setup

1. **Save the Script**: Save the code as `weather_sms_notifier.py`.
2. **Set Up Credentials**: Open `weather_sms_notifier.py` and input your API credentials and phone numbers in the placeholder variables:

   ```python
   # Twilio Configuration
   AccountSid = "YOUR_TWILIO_ACCOUNT_SID"
   AuthToken = "YOUR_TWILIO_AUTH_TOKEN"
   TwilioPhoneNumber = "+1234567890"  # Your Twilio virtual number
   YourPhoneNumber = "+1987654321"    # Destination mobile number

   # OpenWeatherMap Configuration
   ApiKey = "YOUR_OPENWEATHERMAP_API_KEY"
   CityName = "Denver"                # Target city name
   ```

> **Note on Units**: The script queries OpenWeatherMap with `units=metric` but formats the output text with `°F`. If you prefer imperial units (Fahrenheit), change `units=metric` to `units=imperial` in the request URL:
> ```python
> url = f"http://api.openweathermap.org/data/2.5/weather?q={CityName}&appid={ApiKey}&units=imperial"
> ```

---

## Usage Instructions

Run the script from your terminal:

```bash
python weather_sms_notifier.py
```

The script enters a persistent loop (`while True: schedule.run_pending()`) and remains active in the background. At **08:00 AM** daily, it executes the check, logs the status, and dispatches the SMS notification.

To run the process in the background on Linux/macOS servers, use `nohup` or `systemd`:
```bash
nohup python weather_sms_notifier.py &
```

---

## Code Breakdown

```python
# This Python Code Can be used to send a text about the local weather at a certain time of the day
# Twilio is being used to send the SMS texts

import requests, schedule, logging, os
from twilio.rest import Client  

# Setting up logging configuration
logging.basicConfig(filename="WeatherLog.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Twilio Credentials
AccountSid = ""         # Twilio Account SID
AuthToken = ""          # Twilio Auth Token
TwilioPhoneNumber = ""  # Twilio phone number
YourPhoneNumber = ""    # Your phone number

# OpenWeatherMap Information
ApiKey = ""    # OpenWeatherMap API key
CityName = ""  # City name for your weather information

def get_weather_and_send_sms():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CityName}&appid={ApiKey}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if data['cod'] == 200:
            WeatherDescription = data["weather"][0]["description"]
            Temperature = data["main"]["temp"]
            Message = f"The weather in {CityName} is {WeatherDescription} with a temperature of {Temperature}°F."
            send_sms(Message)
            logging.info("Weather message sent successfully.")
        else:
            logging.error(f"Error fetching weather data: {data['message']}")
    except Exception as e:
        logging.exception("An error occurred while getting weather data and sending SMS.")

def send_sms(message):
    try:
        client = Client(AccountSid, AuthToken)
        client.messages.create(
            to=YourPhoneNumber,
            from_=TwilioPhoneNumber,
            body=message
        )
    except Exception as e:
        logging.exception("An error occurred while sending SMS.")

# Schedule the task to run daily at a specific time
schedule.every().day.at("08:00").do(get_weather_and_send_sms) 

# Keep the script running to execute scheduled tasks
while True:
    schedule.run_pending()
```

---

## Security & Best Practices

- **Avoid Hardcoding Secrets**: Consider storing sensitive values like `AccountSid`, `AuthToken`, and `ApiKey` in environment variables rather than hardcoding them into source files:
  ```python
  import os
  AccountSid = os.getenv("TWILIO_ACCOUNT_SID")
  AuthToken = os.getenv("TWILIO_AUTH_TOKEN")
  ApiKey = os.getenv("OWM_API_KEY")
  ```
- **Source Control**: Ensure credentials are removed before committing this code to public repositories. Add configuration or log files (`WeatherLog.txt`) to your `.gitignore`.

---

## License

MIT License. Free to use, modify, and integrate into custom automation routines.
