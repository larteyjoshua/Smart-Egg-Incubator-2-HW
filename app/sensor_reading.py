import Adafruit_DHT
import time
from app.logger import logging
sensor = Adafruit_DHT.DHT22
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

sensorPin = 16
pin = 21 
GPIO.setup(sensorPin, GPIO.OUT)
GPIO.output(sensorPin, GPIO.LOW)

def read_sensor():
    GPIO.output(sensorPin, GPIO.HIGH)
    try:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity is not None and temperature is not None:
            logging(f"Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
            return temperature, humidity
        else:
           logging("Failed to retrieve data from the sensor")

    except Exception as e:
        GPIO.output(sensorPin, GPIO.LOW)
        logging(f"Error: {e}")
    
    finally:
        time.sleep(1)
        GPIO.output(sensorPin, GPIO.LOW)
        