import httpx
from app.config import settings


# This expects the CNN FastAPI to accept multipart/form-data file upload with field 'file'
async def call_model_predict(file_path: str):
    async with httpx.AsyncClient(timeout=30) as client:
        files = {'file': open(file_path, 'rb')}
        try:
            r = await client.post(settings.MODEL_SERVICE_URL, files=files)
        finally:
            files['file'].close()
        r.raise_for_status()
        return r.json()
