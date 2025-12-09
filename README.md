
<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="readmeai/assets/logos/purple.svg" width="30%" alt="Project Logo"/>

# <code>❯ Smart ID Authentication – OCR + Liveness + FaceMatch</code>

<em>Sistema completo de autenticación basado en documento + selfie usando OCR, FaceNet y anti-spoof heurístico.</em>

<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat&logo=FastAPI&logoColor=white">
<img src="https://img.shields.io/badge/EasyOCR-FFC107.svg?style=flat">
<img src="https://img.shields.io/badge/FaceNet-4B7BEC.svg?style=flat">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white">
<img src="https://img.shields.io/badge/OpenCV-5C3EE8.svg?style=flat&logo=opencv&logoColor=white">
<img src="https://img.shields.io/badge/Pydantic-E92063.svg?style=flat&logo=Pydantic&logoColor=white">

</div>

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Endpoints](#endpoints)
- [Getting Started](#getting-started)
- [Technical Details](#technical-details)
- [Examples](#examples)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview
Este proyecto implementa autenticación por documento + selfie mediante:
- OCR con EasyOCR
- Liveness heurístico + anti-spoof
- Match facial con FaceNet (embeddings 512D)
- Motor de decisión configurable

---

## Features
- ✔ OCR
- ✔ Liveness + anti-spoof
- ✔ Face embeddings (FaceNet)
- ✔ Cosine similarity normalizado
- ✔ Validación completa del flujo

---

## Architecture
```
User
 ├── POST /auth/start
 ├── POST /auth/document
 ├── POST /auth/selfie
 └── POST /auth/decision
```

---

## Project Structure
```
app/
 ├── routes/
 ├── services/
 ├── helpers/
 ├── models/
 ├── repositories/
 └── main.py
requirements.txt
README.md
```

---

## Endpoints
### **POST /auth/start**
Crea una sesión de autenticación.

### **POST /auth/document**
Procesa documento, OCR, validación, extracción de rostro.

### **POST /auth/selfie**
Liveness + anti-spoof + embeddings.

### **POST /auth/decision**
Evalúa reglas:
- liveness ≥ 0.75  
- faceMatch ≥ 0.70  
- OCR ≥ 0.60  
- documento válido  

---

## Getting Started
### Install
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run
```
uvicorn app.main:app --reload
```

---

## Technical Details

### OCR
EasyOCR extrae documento, nombres, apellidos, expiración.

### Liveness
Se utilizan:
- nitidez (Laplacian)
- brillo
- tamaño del rostro

### FaceMatch
- MTCNN detecta rostro
- FaceNet genera embedding 512D
- Similitud de coseno normalizada a 0–1

---

## Examples

### Aprobado
```json
{
  "status": "APPROVED",
  "faceMatchScore": 0.82
}
```

### Rechazado
```json
{
  "status": "REJECTED",
  "reason": "Face match score too low"
}
```

---

## Roadmap
- [x] OCR
- [x] Liveness
- [x] FaceMatch
- [ ] Anti-spoof CNN real
- [ ] Docker
- [ ] Tests

---

## License
MIT

</div>
