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
app = FastAPI()
uri = f"mongodb+srv://cloud:{db_password}@cluster0.ihveqly.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["Cluster0"]
#mongo va a crear tales colecciones si no existen
alarma_collection = db["alarma"]

#creamos modelos
class Alarma(BaseModel):
    id: int
    lugar: str
    contenido: Any
    
def getData(sensor_id: int):
    url = f"http://127.0.0.1:8001/sensores/{sensor_id}/latest"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error getting sensor: {response.status_code}")

TEMPERATURE_THRESHOLD = 69.0

def processData():
    print("🔍 Checking sensor data for alarms...")
    response = requests.get(f"http://127.0.0.1:8001/sensores/")
    response.raise_for_status()
    sensores = response.json()
    for sensor_id in sensores:  # Check up to 100 sensors
        try:
            data = getData(sensor_id)
            value = data.get("value")
            unit = data.get("unit", "C")
            timestamp = data.get("timestamp")

            if value is None:
                continue

            # Only check temperature values
            if unit.upper() == "C" and value > TEMPERATURE_THRESHOLD:
                print(f"🚨 Alarm condition met for sensor {sensor_id}: {value}°C")

                payload = {
                    "id": sensor_id,  # same ID ensures one alarm per sensor
                    "lugar": f"Sensor {sensor_id}",
                    "contenido": {
                        "mensaje": "Temperatura crítica",
                        "valor": value,
                        "unidad": unit,
                        "timestamp": timestamp
                    }
                }

                response = alarma_collection.insert_one(payload)

                if response.status_code == 200:
                    print(f"✅ Alarm created for sensor {sensor_id}")
                elif response.status_code == 400 and "Alarma ya existe" in response.text:
                    print(f"⚠️ Alarm already exists for sensor {sensor_id}")
                else:
                    print(f"❌ Unexpected error: {response.status_code} - {response.text}")

        except Exception as e:
            continue

try:
    print("pingeando")
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

def schedule_processing():
    while True:
        try:
            processData()
        except Exception as e:
            print(f"Error in processing loop: {e}")
        time.sleep(10)

# Start in background
threading.Thread(target=schedule_processing, daemon=True).start()