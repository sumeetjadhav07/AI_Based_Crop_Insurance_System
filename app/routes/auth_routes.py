from fastapi import APIRouter, HTTPException
from ..models import UserCreate, UserLogin, UserOut, Token
from ..auth import hash_password, verify_password, create_access_token
from ..db import db

router = APIRouter(prefix="/auth", tags=["auth"])


# -------------------------------------------------
# SIGNUP
# -------------------------------------------------
@router.post("/signup", response_model=UserOut)
async def signup(payload: UserCreate):
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "name": payload.name,
        "email": payload.email,
        "password": hash_password(payload.password),
        "created_at": __import__("datetime").datetime.utcnow()
    }

    res = await db.users.insert_one(user_doc)
    user_doc["_id"] = res.inserted_id
    user_doc.pop("password", None)

    return user_doc


# -------------------------------------------------
# LOGIN
# -------------------------------------------------
@router.post("/login", response_model=Token)
async def login(form: UserLogin):

    user = await db.users.find_one({"email": form.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": str(user["_id"]),
        "email": user["email"]
    })

    return {"access_token": token}
