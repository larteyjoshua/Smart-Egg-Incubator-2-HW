from fastapi import FastAPI, HTTPException
from loguru import logger
from fastapi_utils.tasks import repeat_every
from app.camera_service import capture_image
from loguru import logger
from app.sensor_reading import read_sensor
from app.transfer_service import send_sensor_data, send_image_to_server
import RPi.GPIO as GPIO
import time

heatingLampPin = 26
humidityFanPin = 28
roatingMotorPin = 25
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(heatingLampPin, GPIO.OUT)
GPIO.setup(humidityFanPin, GPIO.OUT)
GPIO.setup(roatingMotorPin, GPIO.OUT)

app = FastAPI()
@app.on_event("startup")
@repeat_every(seconds=60 * 60)  # 1 hour
def captuturing_image() -> None:
    image_path = capture_image()
    logger.info(image_path)
    send_image_to_server(image_path)

@app.on_event("startup")
@repeat_every(seconds=10) 
def sensor_readings() -> None:
    temperature, humidity = read_sensor()
    if temperature > 37.7:
        GPIO.setup(heatingLampPin, GPIO.LOW)
    elif temperature < 37:
        GPIO.setup(heatingLampPin, GPIO.HIGH)
        
        
    if humidity > 55:
        GPIO.setup(humidityFanPin, GPIO.HIGH)
    elif humidity < 50:
         GPIO.setup(humidityFanPin, GPIO.LOW)
    
@app.on_event("startup")
@repeat_every(seconds=60*60*8) 
def roating_tray() -> None:
    GPIO.setup(roatingMotorPin, GPIO.HIGH)
    logger.info("Rotaing Motor")
    time.sleep(120)
    GPIO.setup(roatingMotorPin, GPIO.LOW)
    
    
@app.on_event("startup")
@repeat_every(seconds=60*20) 
async def send_sensor_reading() -> None:
    temperature, humidity = read_sensor()
    logger.info(temperature)
    logger.info(humidity)
    send_sensor_data(temperature, humidity)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.post("/control")
async def receive_command(data: dict):
    device_id = data.get('device_id')
    device_type = data.get('device_type')
    command = data.get('command')
    if not all([device_id, device_type, command]):
        raise HTTPException(status_code=400, detail="Invalid data received")
    if device_type == "light" and command == "on":
        GPIO.setup(heatingLampPin, GPIO.HIGH)
        logger.info("Light ON")
    elif device_type == "light" and command == "off":
         GPIO.setup(heatingLampPin, GPIO.LOW)
         logger.info("Light OFF")
    elif device_type == "fan" and command == "on":
         GPIO.setup(humidityFanPin, GPIO.HIGH)
         logger.info("Fan ON")
    elif device_type == "fan" and command == "off":
         GPIO.setup(humidityFanPin, GPIO.LOW)
         logger.info("Fan OFF")
    elif device_type == "motor" and command == "on":
         GPIO.setup(roatingMotorPin, GPIO.HIGH)
         logger.info("Motor ON")
    elif device_type == "motor" and command == "off":
         GPIO.setup(roatingMotorPin, GPIO.LOW)
         logger.info("Motor OFF")
    logger.info("Command Excuted")
    return {"message": "Command received successfully"}
