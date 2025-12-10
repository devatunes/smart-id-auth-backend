# Smart ID Authentication – OCR + Liveness + FaceMatch  

<div align="center">
<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat&logo=FastAPI&logoColor=white">
<img src="https://img.shields.io/badge/EasyOCR-FFC107.svg?style=flat">
<img src="https://img.shields.io/badge/FaceNet-4B7BEC.svg?style=flat">
<img src="https://img.shields.io/badge/OpenCV-5C3EE8.svg?style=flat&logo=opencv&logoColor=white">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white">
<img src="https://img.shields.io/badge/Pydantic-E92063.svg?style=flat&logo=Pydantic&logoColor=white">
</div>

---

## 📌 Enlaces importantes

| Recurso | Link |
|--------|------|
| **Repositorio GitHub** | https://github.com/devatunes/smart-id-auth-backend |
| **Documentación OAS (GitHub Pages)** | https://devatunes.github.io/smart-id-auth-backend/ |
| **Colección de Postman** | https://documenter.getpostman.com/view/21541927/2sB3dQwAPQ |
| **Demo funcional (video)** | https://drive.google.com/drive/folders/1TS9JKFt8h1AW9ZXBz8_BjH7PElMTSsG9 |

---

# 📖 Tabla de contenido
- [Overview](#overview)
- [Features](#features)
- [Arquitectura](#arquitectura)
- [Flujo de Autenticación](#flujo-de-autenticación)
- [Dependencias Principales](#dependencias-principales)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Endpoints](#endpoints)
- [Getting Started](#getting-started)
- [Detalles Técnicos](#detalles-técnicos)
- [Dataset Usado o Referencia](#dataset-usado-o-referencia)
- [Evidencias de Pruebas](#evidencias-de-pruebas)
- [Demo Funcional](#demo-funcional)
- [Roadmap](#roadmap)
- [Licencia](#licencia)

---

# 🧐 Overview

**Smart ID Authentication** es un sistema completo de verificación de identidad compuesto por:

- OCR de documento (EasyOCR)
- Extracción y comparación de rostro (FaceNet 512D)
- Detección de rostro con MTCNN
- Liveness heurístico + anti‑spoofing básico
- Motor de decisión basado en umbrales configurables
- API modular construida en FastAPI

Simula un flujo real como los usados en entidades financieras.

---

# ✨ Features

### 🔍 OCR Inteligente
- Extrae nombres, apellidos, documento, expiración  
- Calcula confianza del OCR  

### 🧠 Liveness + Anti‑Spoofing
Evalúa:
- Nitidez  
- Brillo  
- Área del rostro  
- Señales anti‑spoof  

### 🧬 FaceMatch (FaceNet)
- Embeddings de 512D  
- Similaridad de coseno 0–1  
- Tolerancia configurable  

### 🔐 Motor de decisión
Reglas:
- Liveness ≥ 0.75  
- FaceMatch ≥ 0.70  
- OCR ≥ 0.60  
- Documento válido  

### ⚙ Arquitectura limpia
- Servicios independientes  
- Manejo de sesiones en memoria  
- Estructura escalable  

---

# 🏛 Arquitectura

```
                   +-------------------------------+
                   |           FastAPI             |
                   |          (Backend)            |
                   +-------------------------------+
                     |       |           |       
                     v       v           v
               Document   Selfie     Decision Engine
                Service   Service        Service
                   |         |              |
                   v         v              v
         +------------+  +----------+  +----------------+
         |   OCR      |  | Liveness |  | FaceNet Match |
         | EasyOCR     | | AntiSpoof | | CosineSim      |
         +------------+  +----------+  +----------------+
```

---

# 🔄 Flujo de Autenticación

```
Usuario
  |
  |-- POST /v1/auth/session ------> crea sesión
  |
  |-- POST /v1/auth/document -----> OCR + validación + rostro documento
  |
  |-- POST /v1/auth/selfie --------> liveness + rostro selfie
  |
  |-- POST /v1/auth/decision ------> motor de decisión
  |
Resultado: APPROVED o REJECTED
```

---

# 📦 Dependencias Principales

| Componente | Tecnologías |
|-----------|-------------|
| OCR | EasyOCR, PyTorch |
| Face Detection | MTCNN |
| Embeddings | FaceNet |
| Liveness | OpenCV |
| API | FastAPI |
| Modelado | Pydantic |

---

# 🗂 Estructura del Proyecto

```
smart-id-auth-backend/
 ├── app/
 │   ├── routes/
 │   ├── services/
 │   ├── helpers/
 │   ├── models/
 │   ├── repositories/
 │   └── main.py
 ├── docs/
 │   └── openapi.json
 ├── README.md
 └── requirements.txt
```

---

# 🌐 Endpoints

### POST `/v1/auth/session`
Crea nueva sesión.

### POST `/v1/auth/document`
Procesa:
- OCR  
- Validación  
- Extracción de rostro  

### POST `/v1/auth/selfie`
Procesa:
- Liveness  
- Anti-spoof  
- Embedding facial  

### POST `/v1/auth/decision`
Evalúa el flujo y decide.

---

# 🚀 Getting Started

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger:
```
http://localhost:8000/docs
```

---

# 🧬 Detalles Técnicos

### OCR – EasyOCR
Extrae texto y calcula confianza del reconocimiento.

### FaceNet – Embeddings
- 512 dimensiones  
- Normalización L2  
- Similaridad → (coseno + 1)/2  

### Liveness
Heurísticas:
- Varianza Laplaciana → nitidez  
- Intensidad → brillo  
- Proporción facial  

### Motor de Decisión
```
if doc_valid and ocr>=0.60 and live>=0.75 and match>=0.70:
    APPROVED
else:
    REJECTED
```

---

# 📚 Dataset Usado o Referencia

No se usa dataset real por privacidad.

Referencias:
- EasyOCR datasets  
- VGGFace2 embeddings  
- Imágenes locales controladas  

---

# 🧪 Evidencias de Pruebas

✔ Colección Postman  
✔ Pruebas de flujo completo  
✔ Pruebas negativas  
✔ Validación manual de excepciones  
✔ Logs y resultados del motor de decisión  

---

# 🎥 Demo Funcional

Video demostrativo:  
https://drive.google.com/drive/folders/1TS9JKFt8h1AW9ZXBz8_BjH7PElMTSsG9

---

# 🗺 Roadmap

- [x] OCR  
- [x] Liveness  
- [x] FaceMatch  
- [x] Tests unitarios  
- [x] Docker  

---

# 📄 Licencia

Proyecto académico de libre uso.

---

<div align="right">
<a href="#top">⬆ Volver arriba</a>
</div>
