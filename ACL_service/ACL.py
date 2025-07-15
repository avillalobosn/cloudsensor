from fastapi import FastAPI, HTTPException
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SENSOR_SERVICE_URL = os.getenv("SENSOR_SERVICE_URL", "http://sensor-service:8000")

app = FastAPI()

def transform_reading(sensor_id: int, raw: dict) -> dict:
    contenido = raw.get("datos", {})
    timestamp = raw.get("timestamp")

    # Attempt to extract temperature
    value = None
    unit = contenido.get("unidad", "C")

    if "temperature" in contenido:
        value = contenido["temperature"]
    elif "temperatura" in contenido:
        value = contenido["temperatura"]
    elif "valor" in contenido:
        value = contenido["valor"]
        unit = contenido.get("unidad", unit)  # Use provided or previous default
    elif "value" in contenido:
        value = contenido["value"]
        unit = contenido.get("unit", unit)

    # Normalize Fahrenheit to Celsius
    if value is not None and isinstance(value, (int, float)):
        if unit.upper() == "F":
            value = (value - 32) * 5 / 9
            unit = "C"

        value = round(value, 2)

    return {
        "device_id": sensor_id,
        "value": value,
        "unit": unit,
        "timestamp": timestamp,
        "metadata": contenido
    }

@app.get("/readings/latest")
def get_latest_reading():
    try:
        response = requests.get(f"{SENSOR_SERVICE_URL}/sensores/")
        response.raise_for_status()
        sensores = response.json()["sensores"]
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to fetch sensors")
    latest_reading = None

    for s in sensores:
        sid = s["id"]
        try:
            r = requests.get(f"{SENSOR_SERVICE_URL}/datos/{sid}").json()
            if not r["datos"]:
                continue
            sensor_latest = sorted(r["datos"], key=lambda d: d["timestamp"], reverse=True)[0]
            if not latest_reading or sensor_latest["timestamp"] > latest_reading["timestamp"]:
                latest_reading = {**sensor_latest, "sensor": sid}
        except:
            continue

    if not latest_reading:
        raise HTTPException(status_code=404, detail="No readings available")

    return transform_reading(latest_reading["sensor"], latest_reading)


@app.get("/sensores/{sensor_id}/latest")
def get_latest_for_sensor(sensor_id: int):
    try:
        response = requests.get(f"{SENSOR_SERVICE_URL}/datos/{sensor_id}")
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail="Failed to fetch sensor data")

    if not data["datos"]:
        raise HTTPException(status_code=404, detail="No readings found for sensor")

    latest = sorted(data["datos"], key=lambda d: d["timestamp"], reverse=True)[0]
    transformed = transform_reading(sensor_id, latest)
    return transformed

@app.get("/sensores/")
def get_sensores():
    try:
        response = requests.get(f"{SENSOR_SERVICE_URL}/sensores/")
        response.raise_for_status()
        sensores = response.json().get("sensores", [])
        return [s["id"] for s in sensores if "id" in s]
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to fetch sensor IDs")
    
