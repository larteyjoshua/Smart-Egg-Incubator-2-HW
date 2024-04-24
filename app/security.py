from cryptography.fernet import Fernet
import base64
from app.config import settings

key = settings.DEVICE_ID_ENCRYPTION_KEY
fernet = Fernet(key)

def decrypt_device_id(encrypted_device_id_str):
    encrypted_device_id_bytes = base64.b64decode(encrypted_device_id_str.encode())
    decrypted_device_id_bytes = fernet.decrypt(encrypted_device_id_bytes)
    decrypted_device_id = decrypted_device_id_bytes.decode()
    return decrypted_device_id


def encrypt_device_id(device_id: str):
    device_id_bytes = device_id.encode()
    encrypted_device_id = fernet.encrypt(device_id_bytes)
    encrypted_device_id_str = base64.b64encode(encrypted_device_id).decode()
    return encrypted_device_id_str
