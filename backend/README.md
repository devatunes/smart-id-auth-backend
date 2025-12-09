<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="readmeai/assets/logos/purple.svg" width="30%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>

# <code>❯ Smart ID Authentication</code>

<em>AI-powered document + selfie identity verification using FastAPI</em>

<!-- BADGES -->
<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=default&logo=FastAPI&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/OpenCV-5C3EE8.svg?style=default&logo=OpenCV&logoColor=white" alt="OpenCV">
<img src="https://img.shields.io/badge/PyTorch-EE4C2C.svg?style=default&logo=PyTorch&logoColor=white" alt="PyTorch">
<img src="https://img.shields.io/badge/NumPy-013243.svg?style=default&logo=NumPy&logoColor=white" alt="NumPy">
<img src="https://img.shields.io/badge/Pydantic-E92063.svg?style=default&logo=Pydantic&logoColor=white" alt="Pydantic">

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

Smart-ID Authentication es un sistema de validación de identidad que combina:

- OCR de documentos (CC – Colombia).
- Liveness facial mediante heurísticas de calidad.
- Face match usando redes neuronales (FaceNet).
- Decisión final basada en reglas configurables.

Todo expuesto por una API REST desarrollada en **FastAPI**.

---

## Features

- 📄 **Análisis de documento**: OCR + validación básica.
- 🤳 **Liveness**: heurístico + anti-spoof stub.
- 🧠 **Face Match**: embeddings FaceNet (512D).
- 🔐 **Sesiones de autenticación** in-memory.
- 🚀 **API moderna** con FastAPI + Pydantic v2.
- 🪶 Código modular y extensible.

---

## Project Structure

```sh
└── /
    ├── app
    │   ├── __init__.py
    │   ├── helpers
    │   ├── main.py
    │   ├── models
    │   ├── repositories
    │   ├── routes
    │   └── services
    └── requirements.txt
```

---

### Project Index

<details open>
	<summary><b><code>/</code></b></summary>

	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<table>
				<tr>
					<td><b><a href="/requirements.txt">requirements.txt</a></b></td>
					<td>Dependencias del proyecto</td>
				</tr>
			</table>
		</blockquote>
	</details>

	<details>
		<summary><b>app</b></summary>
		<blockquote>

			<table>
				<tr>
					<td><b><a href="/app/main.py">main.py</a></b></td>
					<td>Inicialización de FastAPI y carga de rutas</td>
				</tr>
			</table>

			<details>
				<summary><b>repositories</b></summary>
				<blockquote>
					<table>
						<tr>
							<td><b><a href="/app/repositories/document_repository.py">document_repository.py</a></b></td>
							<td>Manejo de OCR / resultados del documento</td>
						</tr>
					</table>
				</blockquote>
			</details>

			<details>
				<summary><b>models</b></summary>
				<blockquote>
					<table>
						<tr>
							<td><b><a href="/app/models/schemas.py">schemas.py</a></b></td>
							<td>Modelos Pydantic v2</td>
						</tr>
					</table>
				</blockquote>
			</details>

			<details>
				<summary><b>routes</b></summary>
				<blockquote>
					<table>
						<tr>
							<td><b><a href="/app/routes/auth.py">auth.py</a></b></td>
							<td>Endpoints document / selfie / decision</td>
						</tr>
					</table>
				</blockquote>
			</details>

			<details>
				<summary><b>helpers</b></summary>
				<blockquote>
					<table>
						<tr>
							<td><b><a href="/app/helpers/session_helper.py">session_helper.py</a></b></td>
							<td>Validación de sesiones</td>
						</tr>
						<tr>
							<td><b><a href="/app/helpers/image_helper.py">image_helper.py</a></b></td>
							<td>Func utilities de imagen</td>
						</tr>
					</table>
				</blockquote>
			</details>

			<details>
				<summary><b>services</b></summary>
				<blockquote>
					<table>
						<tr>
							<td><b><a href="/app/services/document_service.py">document_service.py</a></b></td>
							<td>OCR + validación de documento</td>
						</tr>
						<tr>
							<td><b><a href="/app/services/decision_service.py">decision_service.py</a></b></td>
							<td>Motor decisorio</td>
						</tr>
						<tr>
							<td><b><a href="/app/services/liveness_service.py">liveness_service.py</a></b></td>
							<td>Liveness heurístico + anti-spoof stub</td>
						</tr>
						<tr>
							<td><b><a href="/app/services/session_service.py">session_service.py</a></b></td>
							<td>Manejo de sesiones</td>
						</tr>
						<tr>
							<td><b><a href="/app/services/ocr_service.py">ocr_service.py</a></b></td>
							<td>OCR con EasyOCR</td>
						</tr>
						<tr>
							<td><b><a href="/app/services/selfie_service.py">selfie_service.py</a></b></td>
							<td>Procesamiento de selfie</td>
						</tr>
						<tr>
							<td><b><a href="/app/services/face_service.py">face_service.py</a></b></td>
							<td>FaceNet / embeddings / comparación</td>
						</tr>
					</table>
				</blockquote>
			</details>

		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

- Python 3.12+
- pip
- Virtualenv recomendado

### Installation

```sh
git clone <repo-url>
cd smart-id-auth/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Usage

Ejecutar la API:

```sh
uvicorn app.main:app --reload
```

La API correrá en:

```
http://localhost:8000
```

Documentación automática:

- Swagger → `http://localhost:8000/docs`
- Redoc → `http://localhost:8000/redoc`

---

## Testing

Si agregas test con PyTest:

```sh
pytest
```

---

## Roadmap

- [X] Integración OCR
- [X] Liveness heurístico
- [X] Face Match con FaceNet
- [X] Motor decisorio completo
- [ ] Agregar anti-spoof CNN real
- [ ] Persistencia en Redis
- [ ] Contenerización con Docker

---

## Contributing

1. Fork del repo  
2. Crear rama nueva  
3. Commit + PR  
4. Revisiones y merge

---

## License

Este proyecto usa licencia MIT (o la que prefieras).

---

## Acknowledgments

- EasyOCR  
- FaceNet-PyTorch  
- OpenCV  
- FastAPI  

<div align="right">

[![][back-to-top]](#top)

</div>