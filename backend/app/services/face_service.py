# app/services/face_service.py

from typing import Optional, List

import numpy as np
from PIL import Image
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1

# --------------------------------------------------------------------
# Inicialización global (se carga una sola vez por proceso)
# --------------------------------------------------------------------

# Dispositivo: usamos CPU para ser más portables (en Mac M1 también sirve).
_device = torch.device("cpu")

# Detector de rostros + alineador
_mtcnn = MTCNN(
    image_size=160,
    margin=20,
    min_face_size=60,
    thresholds=[0.6, 0.7, 0.7],
    factor=0.709,
    post_process=True,
    device=_device,
)

# Modelo FaceNet (InceptionResnetV1 entrenado en VGGFace2)
_resnet = InceptionResnetV1(
    pretrained="vggface2"
).eval().to(_device)


def _bytes_to_pil(image_bytes: bytes) -> Optional[Image.Image]:
    """
    Convierte bytes a una imagen PIL en RGB.
    Devuelve None si no se puede decodificar.
    """
    import io

    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        return img
    except Exception:
        return None


def extract_face_descriptor(image_bytes: bytes) -> Optional[List[float]]:
    """
    Extrae un embedding de FaceNet (512D) para el rostro principal:
      1. Convierte bytes → PIL Image.
      2. Usa MTCNN para detectar y alinear la cara.
      3. Pasa la cara por InceptionResnetV1.
      4. Normaliza el vector (L2) y lo devuelve como lista de floats.

    Devuelve:
      - Lista[float] de 512 dimensiones si encuentra rostro.
      - None si no se detecta rostro o algo falla.
    """
    img = _bytes_to_pil(image_bytes)
    if img is None:
        return None

    # MTCNN devuelve un tensor [3, 160, 160] o None si no hay cara
    with torch.no_grad():
        face_tensor = _mtcnn(img)

    if face_tensor is None:
        return None

    # Añadimos batch dimension [1, 3, 160, 160]
    face_tensor = face_tensor.unsqueeze(0).to(_device)

    with torch.no_grad():
        embedding = _resnet(face_tensor)  # [1, 512]

    vec = embedding[0].cpu().numpy().astype("float32")
    norm = np.linalg.norm(vec)
    if norm == 0.0:
        return None

    vec /= norm  # normalización L2
    return vec.tolist()


def compute_face_similarity(desc1: List[float], desc2: List[float]) -> float:
    """
    Calcula similitud de coseno entre dos embeddings FaceNet y la normaliza a [0,1]:
      - 0.0 → nada parecido
      - 1.0 → prácticamente idéntico

    Ambos vectores se esperan ya normalizados, pero por seguridad
    volvemos a normalizar aquí.
    """
    v1 = np.asarray(desc1, dtype="float32")
    v2 = np.asarray(desc2, dtype="float32")

    # Re-normalizar por seguridad
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 == 0.0 or n2 == 0.0:
        return 0.0

    v1 /= n1
    v2 /= n2

    cos_sim = float(np.dot(v1, v2))  # ya están normalizados → [-1, 1]
    score = (cos_sim + 1.0) / 2.0    # → [0, 1]

    # Clamp defensivo
    return max(0.0, min(1.0, score))