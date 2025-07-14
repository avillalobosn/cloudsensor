# Cosas que hacer
- [] Agregar integrantes
- [] Agregar codigos mockup de microservicios a implementar
- [] Chantar GitHub Actions en microservicios
- [] Dockerizar y hacer Kubernetes
# Como correrlo
## sensores
cd sensor_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn sensores:app --reload --port 8000

## anti corruption layer
cd ACL_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn ACL:app reload --port 8001

# Microservicios implementados
