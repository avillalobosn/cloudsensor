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
        "timestamp": datetime.utcnow()
    }

    sensor_collection.insert_one(doc)
    return {"datos":f"datos creados"}

# Send a ping to confirm a successful connection
try:
    print("pingeando")
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
