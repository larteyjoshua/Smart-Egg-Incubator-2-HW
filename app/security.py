from cryptography.fernet import Fernet
import base64
from loguru import logger


def encrypt_device_id(device_id:str):
    key = 
    fernet = Fernet(key)
    logger.info("encrpytion")
    device_id_bytes = device_id.encode()
    encrypted_device_id = fernet.encrypt(device_id_bytes)
    encrypted_device_id_str = base64.b64encode(encrypted_device_id).decode()
    return encrypted_device_id_str
