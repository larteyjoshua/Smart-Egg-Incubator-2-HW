import os
import subprocess
import time
from app.logger import logging



def capture_image():
    folder_path = "captured_images"
    os.makedirs(folder_path, exist_ok=True)
    image_path = os.path.join(folder_path, f"image_{int(time.time())}.jpg")
    command = f"/usr/bin/fswebcam -r {320}x{240} --no-banner {image_path}"
    subprocess.run(command, shell=True, check=True)
    logging("Capturing Completed: " + image_path)
    return image_path
