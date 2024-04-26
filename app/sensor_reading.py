import Adafruit_DHT
import time
from app.logger import logging
sensor = Adafruit_DHT.DHT22
pin = 4  
def read_sensor():
    try:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity is not None and temperature is not None:
            logging(f"Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
            return temperature, humidity
        else:
           logging("Failed to retrieve data from the sensor")

    except Exception as e:
        logging(f"Error: {e}")