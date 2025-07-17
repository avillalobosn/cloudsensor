from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests
from enviar_correo import send_email
import webbrowser
import json

load_dotenv()

db_password = os.getenv("db_password")
EMAIL_ADDRESS = os.getenv("email_address")
EMAIL_PASSWORD = os.getenv("email_password")

app = FastAPI()
uri = f"mongodb+srv://cloud:{db_password}@cluster0.ihveqly.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# In-memory alarm store to avoid duplicates
alarm_store: Dict[int, Dict[str, Any]] = {}
ALARM_STORE_FILE = "alarm_store.json"

def load_alarm_store():
    if os.path.exists(ALARM_STORE_FILE):
        with open(ALARM_STORE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_alarm_store(store):
    with open(ALARM_STORE_FILE, "w") as f:
        json.dump(store, f)

# Load alarm store from file
alarm_store = load_alarm_store()

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
    sensor_id = str(alarma.id)

    if sensor_id in alarm_store:
        return JSONResponse(
            status_code=400,
            content={"detail": f"Alarma ya existe para el sensor {sensor_id}"}
        )

    alarm_store[sensor_id] = alarma.dict()
    save_alarm_store(alarm_store)  # Persist to file

    print(f"🔔 Nueva alarma recibida: {alarma}")

    subject = f"ALIEN DETECTADO POR SENSOR {sensor_id}"
    body = (
        "Hola!\n\n"
        "AYUDA VIENEN LOS ALIENS AAAAAAAAAAAAAAA ACTIVEN LAS ALARMAS "
        "LOS ESCUDOS NO DEJEN QUE VENGAN POR MI KILO DE VRAM\n\nSaludos!"
    )
    to_email = "ivan.caasrrasco@estudiantes.uv.cl"
    send_email(subject, body, to_email, EMAIL_ADDRESS, EMAIL_PASSWORD)

    url = "https://www.youtube.com/watch?v=p_khWy7GAcQ"
    webbrowser.open_new_tab(url)

    return {"message": "Alarma creada con éxito", "id": sensor_id}

@app.get("/alarmas/")
def obtener_alarmas():
    return {"alarmas": list(alarm_store.values())}


@app.get("/")
def root():
    return {"message": "Servicio de alarmas activo"}
