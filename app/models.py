from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId

# -----------------------------------------
# CUSTOM OBJECT ID HANDLER
# -----------------------------------------
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# -----------------------------------------
# AUTH MODELS
# -----------------------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -----------------------------------------
# POLICY MODELS
# -----------------------------------------
class Policy(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    owner_id: PyObjectId
    name: str
    crop_type: str
    start_date: datetime
    end_date: datetime
    premium: float
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
        orm_mode = True


# -----------------------------------------
# AVAILABLE POLICIES (Admin Created Policies)
# -----------------------------------------
class AvailablePolicy(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    crop_type: str
    premium: float
    description: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True


# -----------------------------------------
# CLAIM MODELS
# -----------------------------------------
class ClaimCreate(BaseModel):
    policy_id: str
    description: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


class Claim(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    policy_id: PyObjectId
    image_path: str
    description: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    model_result: Optional[dict] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
