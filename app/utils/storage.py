import os
from uuid import uuid4
from pathlib import Path
from app.config import settings

Path(settings.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

def save_upload_file(file) -> str:
    # file: Starlette UploadFile
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    path = os.path.join(settings.UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path
