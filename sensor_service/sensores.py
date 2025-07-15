from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from typing import Any

load_dotenv()
db_password = os.getenv("db_password")
app = FastAPI()
uri = f"mongodb+srv://cloud:{db_password}@cluster0.ihveqly.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["Cluster0"]
#mongo va a crear tales colecciones si no existen
sensor_collection = db["sensores"]
datos_collection = db["datos"]

#creamos modelos
class Sensor(BaseModel):
    id: int
    nombre: str
    estado: str

class Datos(BaseModel):
    sensor: int
    contenido: Any

@app.post("/sensores/")
def createSensor(sensor: Sensor):
    if sensor_collection.find_one({"id": sensor.id}):
        raise HTTPException(status_code = 400, detail="Sensor existe")
    sensor_collection.insert_one({"id":sensor.id, "nombre":sensor.nombre,"estado":sensor.estado})
    return {"mensaje":f"Sensor {sensor.nombre} fue creado"}

@app.post("/datos/")
def createDatoSensor(datos: Datos):
    if not sensor_collection.find_one({"id": datos.sensor}):
        raise HTTPException(status_code = 400, detail="Sensor no existe")
    doc = {
        "sensor": datos.sensor,
        "datos": datos.contenido,
        "timestamp": datetime.now()
    }

    datos_collection.insert_one(doc)
    return {"datos":f"datos creados"}

@app.get("/sensores/")
def get_all_sensors():
    sensores = list(sensor_collection.find({}, {"_id": 0}))
    return {"sensores": sensores}

@app.get("/sensores/{sensor_id}")
def get_sensor(sensor_id: int):
    sensor = sensor_collection.find_one({"id": sensor_id}, {"_id": 0})
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    return sensor

@app.get("/datos/{sensor_id}")
def get_sensor_data(sensor_id: int):
    if not sensor_collection.find_one({"id": sensor_id}):
        raise HTTPException(status_code=404, detail="Sensor no encontrado")
    
    datos = list(datos_collection.find({"sensor": sensor_id}, {"_id": 0}))
    return {"sensor_id": sensor_id, "datos": datos}

@app.delete("/sensores/{sensor_id}")
def delete_sensor(sensor_id: int):
    result = sensor_collection.delete_one({"id": sensor_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sensor no encontrado")

# Send a ping to confirm a successful connection
try:
    print("pingeando")
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
