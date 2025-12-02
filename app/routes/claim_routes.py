# app/routes/claim_routes.py

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, Header
from datetime import datetime
from bson import ObjectId
import os
import shutil

from ..db import db
from ..auth import decode_token
from ..models import ClaimCreate, Claim
from ..services.model_client import call_model_predict

router = APIRouter(prefix="/claims", tags=["claims"])

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------------------------------------------------
# AUTH TOKEN → GET CURRENT USER ID
# ---------------------------------------------------------
async def get_current_user_id(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.split(" ", 1)[1]

    try:
        payload = decode_token(token)
        return payload["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ---------------------------------------------------------
# SUBMIT CLAIM (Farmer uploads image + desc + location)
# ---------------------------------------------------------
@router.post("/", response_model=dict)
async def submit_claim(
    policy_id: str = Form(...),
    description: str = Form(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    image: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """Submit a new insurance claim with image + description."""

    # Ensure policy exists and belongs to user
    policy = await db.policies.find_one({"_id": ObjectId(policy_id)})

    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if str(policy["owner_id"]) != user_id:
        raise HTTPException(status_code=403, detail="Not your policy")


    # Save uploaded image
    image_path = os.path.join(UPLOAD_DIR, f"{datetime.utcnow().timestamp()}_{image.filename}")

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Run ML model (damage detection)
    model_output = await call_model_predict(image_path)


    # Prepare claim document
    claim_doc = {
        "user_id": ObjectId(user_id),
        "policy_id": ObjectId(policy_id),
        "image_path": image_path,
        "description": description,
        "latitude": latitude,
        "longitude": longitude,
        "model_result": model_output,
        "status": "pending",  # pending / under_review / approved / rejected
        "created_at": datetime.utcnow()
    }

    res = await db.claims.insert_one(claim_doc)

    return {"message": "Claim submitted successfully", "claim_id": str(res.inserted_id)}


# ---------------------------------------------------------
# LIST CLAIMS FOR LOGGED-IN USER
# ---------------------------------------------------------
@router.get("/", response_model=list)
async def list_claims(user_id: str = Depends(get_current_user_id)):
    """Return all claims submitted by the current user."""

    cursor = db.claims.find({"user_id": ObjectId(user_id)})

    claims = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["user_id"] = str(doc["user_id"])
        doc["policy_id"] = str(doc["policy_id"])
        claims.append(doc)

    return claims


# ---------------------------------------------------------
# UPDATE CLAIM STATUS (Admin or internal use)
# ---------------------------------------------------------
@router.patch("/status/{claim_id}", response_model=dict)
async def update_claim_status(claim_id: str, status: str):
    """
    Update claim status:
        - pending
        - under_review
        - approved
        - rejected
    """

    allowed = ["pending", "under_review", "approved", "rejected"]
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed}")

    res = await db.claims.update_one(
        {"_id": ObjectId(claim_id)},
        {"$set": {"status": status}}
    )

    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Claim not found")

    return {
        "message": "Status updated",
        "claim_id": claim_id,
        "status": status
    }
