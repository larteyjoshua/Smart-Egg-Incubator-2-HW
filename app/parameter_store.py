import json
import time

def store_hatching_status(status):
    with open("hatching_status.json", "w") as file:
        json.dump(status, file, indent=4)
        

def read_hatching_status():
    try:
        with open("hatching_status.json", "r") as file:
            status = json.load(file)
    except FileNotFoundError:
        status = {"operating": False}

    return status


def store_device_settings(settings):
    with open("device_settings.json", "w") as file:
        json.dump(settings, file, indent=4)
        

def read_device_settings():
    try:
        with open("device_settings.json", "r") as file:
            settings = json.load(file)
    except FileNotFoundError:
        settings = {
    "min_temperature": 37.0,
    "max_temperature": 39.0,
    "min_humidity": 50.0,
    "max_humidity": 55.0,
    "rotating_hours": 8.0,
    "device_id": 1,
    "timestamp": "2024-03-19T01:55:39.063755",
    "rotation": True
                }
    return settings

def get_last_run_time():
  filename = "last_run.json"
  try:
    with open(filename, "r") as f:
      data = json.load(f)
      return data["last_run_time"]
  except (FileNotFoundError, json.JSONDecodeError):
    return None

def save_last_run_time():
  filename = "last_run.json"
  data = {"last_run_time": time.time()}
  with open(filename, "w") as f:
    json.dump(data, f, indent=4) 