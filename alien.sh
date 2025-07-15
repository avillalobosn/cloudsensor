#!/bin/bash

curl -X POST http://localhost:8000/datos/ \
  -H "Content-Type: application/json" \
  -d '{
    "sensor": 1,
    "contenido": {
      "tipo": "temperature",
      "unidad": "C",
      "valor": 37.5,
      "Alien": true,
      "timestamp": "'$(date -Iseconds)'"
    }
  }'

