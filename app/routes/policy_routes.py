# app/routes/policy_routes.py

from fastapi import APIRouter, Header, HTTPException, Depends
from typing import List
from datetime import datetime
from bson import ObjectId

from ..models import Policy, AvailablePolicy
from ..db import db
from ..auth import decode_token
from ..services.payment_stub import process_payment

router = APIRouter(prefix="/policies", tags=["policies"])


# --------------------------------------------------
# AUTH - Extract user from JWT token
# --------------------------------------------------
async def get_current_user_id(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.split(" ", 1)[1]

    try:
        payload = decode_token(token)
        return payload["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# --------------------------------------------------
# CREATE AVAILABLE POLICY (Admin use)
# --------------------------------------------------
@router.post("/create", response_model=dict)
async def create_available_policy(payload: AvailablePolicy):
    data = payload.dict(exclude_unset=True)
    res = await db.available_policies.insert_one(data)

    return {
        "message": "Available policy added",
        "id": str(res.inserted_id)
    }


# --------------------------------------------------
# LIST AVAILABLE POLICIES (Farmers choose from this)
# --------------------------------------------------
@router.get("/available", response_model=list)
async def get_available_policies():
    cursor = db.available_policies.find({})

    policies = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        policies.append(doc)

    return policies


# --------------------------------------------------
# BUY POLICY (Farmer purchases a policy)
# --------------------------------------------------
@router.post("/buy", response_model=dict)
async def buy_policy(policy_id: str, user_id: str = Depends(get_current_user_id)):

    # Find the selected available policy
    template = await db.available_policies.find_one({"_id": ObjectId(policy_id)})

    if not template:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Process mock payment
    payment = process_payment(
        amount=template["premium"],
        user_id=user_id,
        policy_name=template["name"]
    )

    # Prepare policy to save in "policies" collection
    policy_doc = {
        "owner_id": ObjectId(user_id),
        "name": template["name"],
        "crop_type": template["crop_type"],
        "premium": template["premium"],
        "status": "active",
        "created_at": datetime.utcnow(),
        "start_date": datetime.utcnow(),
        "end_date": datetime.utcnow(),
        "payment": payment
    }

    res = await db.policies.insert_one(policy_doc)

    return {
        "message": "Policy purchased successfully",
        "policy_id": str(res.inserted_id),
        "payment": payment
    }


# --------------------------------------------------
# LIST USER'S PURCHASED POLICIES
# --------------------------------------------------
@router.get("/", response_model=List[Policy])
async def list_policies(user_id: str = Depends(get_current_user_id)):
    cursor = db.policies.find({"owner_id": ObjectId(user_id)})

    policies = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["owner_id"] = str(doc["owner_id"])
        policies.append(doc)

    return policies
