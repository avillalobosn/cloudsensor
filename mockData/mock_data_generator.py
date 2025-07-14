import os
import time
import random
import requests


BASE_URL = "http://localhost:8000"

# Sensor types & configurations
SENSOR_TYPES = [
    {"tipo": "temperature", "unidad": "C", "rango": (0, 40)},
    {"tipo": "temperature", "unidad": "F", "rango": (32, 104)}
]

SENSORS = []
NEXT_SENSOR_ID = 1
SENSOR_SPAWN_INTERVAL = 30  # Seconds
DATA_SEND_INTERVAL = 1      # Seconds per sensor

def create_sensor():
    global NEXT_SENSOR_ID

    config = random.choice(SENSOR_TYPES)
    sensor = {
        "id": NEXT_SENSOR_ID,
        "nombre": f"{config['tipo'].capitalize()}Sensor_{NEXT_SENSOR_ID}",
        "estado": "activo",
        "tipo": config["tipo"],
        "unidad": config["unidad"],
        "rango": config["rango"]
    }

    response = requests.post(f"{BASE_URL}/sensores/", json={
        "id": sensor["id"],
        "nombre": sensor["nombre"],
        "estado": sensor["estado"]
    })

    if response.status_code == 200 and NEXT_SENSOR_ID < 9:
        print(f"🆕 Sensor created: {sensor['nombre']}")
        SENSORS.append(sensor)
        NEXT_SENSOR_ID += 1
    elif response.status_code == 400:
        print(f"⚠️ Sensor {sensor['nombre']} already exists")
        NEXT_SENSOR_ID += 1
    else:
        print(f"❌ Failed to create sensor: {response.text}")

def generate_data(sensor):
    value = round(random.uniform(*sensor["rango"]), 2)
    return {
        "tipo": sensor["tipo"],
        "unidad": sensor["unidad"],
        "valor": value
    }

def post_sensor_data(sensor):
    payload = {
        "sensor": sensor["id"],
        "contenido": generate_data(sensor)
    }
    response = requests.post(f"{BASE_URL}/datos/", json=payload)
    if response.status_code == 200:
        print(f"📤 Sent data for {sensor['nombre']}: {payload['contenido']}")
    else:
        print(f"❌ Failed to send data for {sensor['nombre']}: {response.text}")

def main():
    print("🚀 Starting mock data generator...")
    create_sensor()  # Create first sensor immediately
    last_spawn = time.time()

    try:
        while True:
            now = time.time()

            # Create new sensor every X seconds
            if now - last_spawn > SENSOR_SPAWN_INTERVAL:
                create_sensor()
                last_spawn = now

            # Send data for each sensor
            for sensor in SENSORS:
                post_sensor_data(sensor)
                time.sleep(DATA_SEND_INTERVAL)
    except KeyboardInterrupt:
        print("\n🛑 Generator stopped by user.")

if __name__ == "__main__":
    main()
