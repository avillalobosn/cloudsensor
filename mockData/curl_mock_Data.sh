#!/bin/bash

echo "Sending sensor creation request..."
curl -X POST http://127.0.0.1:8000/sensores/ \
  -H "Content-Type: application/json" \
  -d @sensor.json

echo -e "\nSending sensor data request..."
curl -X POST http://127.0.0.1:8000/datos/ \
  -H "Content-Type: application/json" \
  -d @datos.json

echo -e "\nRequests complete."

