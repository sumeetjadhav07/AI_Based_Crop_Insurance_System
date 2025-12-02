import uvicorn
from fastapi import FastAPI
from .routes import auth_routes, policy_routes, claim_routes
from .db import create_indexes
from .config import settings

app = FastAPI(title="Crop Insurance Backend")

app.include_router(auth_routes.router)
app.include_router(policy_routes.router)
app.include_router(claim_routes.router)

@app.on_event("startup")
async def startup():
    await create_indexes()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
