import os
import subprocess
import time
from loguru import logger


def capture_image():
    folder_path = "captured_images"
    os.makedirs(folder_path, exist_ok=True)
    image_path = os.path.join(folder_path, f"image_{int(time.time())}.jpg")
    command = f"fswebcam -r {320}x{240} --no-banner {image_path}"
    subprocess.run(command, shell=True, check=True)
    logger.info("Capturing Completed: " + image_path)
    return image_path
