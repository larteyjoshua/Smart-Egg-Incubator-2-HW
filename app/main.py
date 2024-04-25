from fastapi import FastAPI, HTTPException
from loguru import logger
from fastapi_utilities import repeat_every
from app.camera_service import capture_image
from loguru import logger
from app.sensor_reading import read_sensor
from app.transfer_service import(send_sensor_data,
                                 send_image_to_server,
                                 request_hatching_status, 
                                 request_device_settings)
from app.parameter_store import(store_hatching_status,
                                store_device_settings,
                                read_hatching_status, 
                                read_device_settings,
                                get_last_run_time,
                                save_last_run_time)
from app.security import decrypt_device_id
import RPi.GPIO as GPIO
import time
import threading
from contextlib import asynccontextmanager

device_id=1
heatingLampPin = 26
humidityFanPin = 28
roatingMotorPin = 25
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(heatingLampPin, GPIO.OUT)
GPIO.setup(humidityFanPin, GPIO.OUT)
GPIO.setup(roatingMotorPin, GPIO.OUT)

def rotating_egg_tray():
    logger.info('Tray Rotation Process Started')
    GPIO.setup(roatingMotorPin, GPIO.HIGH)
    time.sleep(120)
    GPIO.setup(roatingMotorPin, GPIO.LOW)
    logger.info('Tray Rotation Process Ended')

async def config_parameters():
    status=request_hatching_status(device_id)
    logger.info(status)
    if status:
        store_hatching_status(status)
        
    settings=request_device_settings(device_id)
    logger.info(settings)
    if settings:
        store_device_settings(settings)
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    await config_parameters()
    await capturing_image()
    await process_controls()
    await roating_tray()
    # await send_sensor_reading()
    yield
    # --- shutdown ---
           
app = FastAPI(lifespan=lifespan)

@repeat_every(seconds=60 * 60) 
async def capturing_image() -> None:
    status_data = read_hatching_status()
    operating_status =status_data.get('operating')
    if operating_status == False:
        logger.info('Hatching Process is not Started by User')
        return
    
    GPIO.setup(heatingLampPin, GPIO.HIGH)
    image_path = capture_image()
    logger.info(image_path)
    send_image_to_server(image_path)
    GPIO.setup(heatingLampPin, GPIO.LOW)


@repeat_every(seconds=10) 
async def process_controls() -> None:
    status_data = read_hatching_status()
    operating_status =status_data.get('operating')
    if operating_status == False:
        logger.info('Hatching Process is not Started by User')
        return
    
    settings_data = read_device_settings()
    minTemp = settings_data.get('min_temperature')
    maxTemp = settings_data.get('max_temperature')
    minHumid = settings_data.get('min_humidity')
    maxHumid = settings_data.get('max_humidity')
    
    temperature, humidity = read_sensor()
    if temperature > maxTemp:
        GPIO.setup(heatingLampPin, GPIO.LOW)
        logger.info('Heating Process Off')
    elif temperature < minTemp:
        GPIO.setup(heatingLampPin, GPIO.HIGH)
        logger.info('Heating Process On')
        
        
    if humidity > maxHumid:
        GPIO.setup(humidityFanPin, GPIO.HIGH)
        logger.info('Humidity Reduction Process on')
    elif humidity < minHumid:
        GPIO.setup(humidityFanPin, GPIO.LOW)
        logger.info('Humidity Reduction Process Off')
    

@repeat_every(seconds=60) 
async def roating_tray() -> None:
    status_data = read_hatching_status()
    operating_status =status_data.get('operating')
    if  operating_status == False:
        logger.info('Hatching Process is not Started by User')
        return
    
    settings_data = read_device_settings()
    rotation = settings_data.get('rotation')
    rotating_hours = settings_data.get('rotating_hours')
    hours_in_seconds = 60*60*rotating_hours
    last_run_time = get_last_run_time()
    logger.info(last_run_time)
    if last_run_time is None or time.time() - last_run_time >= hours_in_seconds and rotation:
            save_last_run_time()
            thread = threading.Thread(target=rotating_egg_tray)
            thread.start()
       
    
    
@repeat_every(seconds=60*60) 
async def send_sensor_reading() -> None:
    temperature, humidity = read_sensor()
    logger.info(temperature)
    logger.info(humidity)
    
    status_data = read_hatching_status()
    operating_status =status_data.get('operating')
    if  operating_status == False:
        logger.info('Hatching Process is not Started by User')
        return
    
    send_sensor_data(temperature, humidity)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.post("/settings")
async def receive_settings(data: dict):
    logger.info(data)
    encrpyted_id = data.get('encrypted_device_id')
    settings = data.get('data')
    decrpyted_id=int(decrypt_device_id(encrpyted_id))
    
    if decrpyted_id == device_id and settings:
        store_device_settings(settings)
        return {"msg: Devices Settings Updated!"}
    else:
         raise HTTPException(status_code=404, detail="Device id Mismatch")
        
    

@app.post("/hatching/status")
async def receive_status(data: dict):
        logger.info(data)
        encrpyted_id = data.get('encrypted_device_id')
        status = data.get('data')
        decrpyted_id=int(decrypt_device_id(encrpyted_id))
    
        if decrpyted_id == device_id and status:
            store_hatching_status(status)
            return {"msg: Devices Hatching Status Updated!"}
        else:
            raise HTTPException(status_code=404, detail="Device id Mismatch")
    
    

@app.post("/control")
async def receive_command(data: dict):
    logger.info(data)
    encrpyted_id = data.get('encrypted_device_id')
    command_data = data.get('data')
    device_type=command_data.get('device_type')
    command=command_data.get('command')  
    
    decrpyted_id=int(decrypt_device_id(encrpyted_id))
    logger.info(decrpyted_id)
    if decrpyted_id != device_id:
         raise HTTPException(status_code=404, detail="Device id Mismatch")
   
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
