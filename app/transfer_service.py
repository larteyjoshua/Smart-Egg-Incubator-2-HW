import os
import requests
from app.security import encrypt_device_id
import json
import base64
from app.config import settings
from app.logger import logging

device_id=1



def send_image_to_server(image_path):
    logging("Image Sending Function")
    encrypted_device_id = encrypt_device_id(str(device_id))
    url =  f"{settings.SERVER_URL}sensors/captured_image"

    if not os.path.isfile(image_path):
        logging(f"Error: Image file '{image_path}' not found.") 
        return 'File Path Not Found!'

    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read())
    data = {
        'device_id': encrypted_device_id,
        'image': image_data.decode()  
    }
    json_data= json.dumps(data)

    # Define headers
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, data=json_data, headers=headers)
        response.raise_for_status() 
        if (response.status_code == 200): 
            logging("Image sent successfully.")
            os.remove(image_path)
        return response.status_code
    except requests.exceptions.RequestException as e:
        logging(f"Error sending image: {e}") 
        return response.status_code if response else 500 



def send_sensor_data(temperature:float, humidity:float):
        encrypted_device_id = encrypt_device_id(str(device_id))
        data_to_send = {"device_id": encrypted_device_id, "temperature": temperature, "humidity": humidity}
        url = f"{settings.SERVER_URL}sensors/create"
        json_data = json.dumps(data_to_send)
        logging(json_data)
        logging(url)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json_data, headers=headers)
        logging(response)
        if response.status_code == 200:
            logging("Data sent successfully!")
        else:
            logging("Failed to send data. Server returned status code:" + str(response.status_code))
            

def request_hatching_status(device_id):
    encrypted_id = encrypt_device_id(str(device_id))
    payload = {"device_id": encrypted_id}
    backend_url: str = f"{settings.SERVER_URL}devices/hatching/status"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(backend_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        hatching_status = response.json()
        return hatching_status
    except requests.exceptions.RequestException as e:
        logging(f"Error: {e}")
        return  {"operating": True}
    
    
def request_device_settings(device_id):
    encrypted_id = encrypt_device_id(str(device_id))
    payload = {"device_id": encrypted_id}
    backend_url: str = f"{settings.SERVER_URL}devices/settings/params"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(backend_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        hatching_status = response.json()
        return hatching_status
    except requests.exceptions.RequestException as e:
        logging(f"Error: {e}")
        return  {}

      