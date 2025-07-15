from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests
from datetime import datetime
from typing import Any
import threading
import time

load_dotenv()

db_password = os.getenv("db_password")
ACL_SERVICE_URL = os.getenv("ACL_SERVICE_URL")
ALARMAS_SERVICE_URL = os.getenv("ALARMAS_SERVICE_URL")

app = FastAPI()

#creamos modelos
class Alarma(BaseModel):
    id: int
    lugar: str
    contenido: Any
    
def getData(sensor_id: int):
    url = f"{ACL_SERVICE_URL}/sensores/{sensor_id}/latest"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error getting sensor: {response.status_code}")

TEMPERATURE_THRESHOLD = 69.0

def processData():
    print("🔍 Checking sensor data for alarms...")
    response = requests.get(f"{ACL_SERVICE_URL}/sensores/")
    response.raise_for_status()
    sensores = response.json()
    for sensor_id in sensores:  # Check up to 100 sensors
        try:
            data = getData(sensor_id)
            value = data.get("value")
            unit = data.get("unit", "C")
            timestamp = data.get("timestamp")
            metadata = data.get("metadata", {})

            if value is None:
                continue

            # Check for critical temperature
            is_temp_alarm = unit.upper() == "C" and value > TEMPERATURE_THRESHOLD

            # Check for alien detection
            is_alien_detected = metadata.get("Alien") is True

            if is_temp_alarm or is_alien_detected:
                print(f"🚨 Alarm triggered for sensor {sensor_id}")

                contenido = {
                    "mensaje": "Temperatura crítica" if is_temp_alarm else "ALIEN DETECTADO EN EL AREA CODE RED",
                    "valor": value,
                    "unidad": unit,
                    "timestamp": timestamp,
                    "metadata": metadata
                }

                payload = {
                    "id": sensor_id,
                    "lugar": f"Sensor {sensor_id}",
                    "contenido": contenido
                }

                alarm_response = requests.post(f"{ALARMAS_SERVICE_URL}/alarmas/", json=payload)

                if alarm_response.status_code == 200:
                    print(f"✅ Alarm created for sensor {sensor_id}")
                elif alarm_response.status_code == 400 and "Alarma ya existe" in alarm_response.text:
                    print(f"⚠️ Alarm already exists for sensor {sensor_id}")
                else:
                    print(f"❌ Error {alarm_response.status_code}: {alarm_response.text}")

                # You likely need to remove this response.status_code logic
                # because insert_one returns an InsertOneResult, not a response object.
                print(f"✅ Alarm created for sensor {sensor_id}")

        except Exception as e:
            print(f"❌ Error processing sensor {sensor_id}: {e}")
            continue

def schedule_processing():
    while True:
        try:
            processData()
        except Exception as e:
            print(f"Error in processing loop: {e}")
        time.sleep(10)

# Start in background
threading.Thread(target=schedule_processing, daemon=True).start()