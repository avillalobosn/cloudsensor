from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests

load_dotenv()

db_password = os.getenv("db_password")

app = FastAPI()
uri = f"mongodb+srv://cloud:{db_password}@cluster0.ihveqly.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# In-memory alarm store to avoid duplicates
alarm_store: Dict[int, Dict[str, Any]] = {}

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["Cluster0"]
#mongo va a crear tales colecciones si no existen
alarma_collection = db["alarma"]


class Contenido(BaseModel):
    mensaje: str
    valor: float
    unidad: str
    timestamp: str
    metadata: Dict[str, Any] = {}


class Alarma(BaseModel):
    id: int  # Sensor ID
    lugar: str
    contenido: Contenido


@app.post("/alarmas/")
def crear_alarma(alarma: Alarma):
    sensor_id = alarma.id

    if sensor_id in alarm_store:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Alarma ya existe para el sensor {sensor_id}"}
        )

    alarm_store[sensor_id] = alarma.dict()
    print(f"🔔 Nueva alarma recibida: {alarma}")
    # - Save to a database
    #alarma_collection.insert_one(alarma)
    # Optional: Trigger additional actions like:
    # - Send email/SMS
    # - Open a browser tab
    # - Notify another service
    

    return {"message": "Alarma creada con éxito", "id": sensor_id}


@app.get("/alarmas/")
def obtener_alarmas():
    return {"alarmas": list(alarm_store.values())}


@app.get("/")
def root():
    return {"message": "Servicio de alarmas activo"}
