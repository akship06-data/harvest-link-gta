from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class OrganizationCreate(BaseModel):
    name: str
    org_type: str = Field(..., pattern="^(donor|pantry)$")
    neighborhood: str
    address: str
    latitude: float
    longitude: float
    dinesafe_verified: bool = True
    has_refrigeration: bool = True
    accepted_dietary: List[str] = ["vegetarian", "halal", "nut_free", "shelf_stable"]


class OrganizationOut(BaseModel):
    id: int
    name: str
    org_type: str
    neighborhood: str
    address: str
    latitude: float
    longitude: float
    dinesafe_verified: bool
    has_refrigeration: bool
    accepted_dietary: str

    class Config:
        from_attributes = True


class SurplusBatchCreate(BaseModel):
    donor_id: int
    title: str = Field(..., min_length=3, max_length=140)
    meal_count: int = Field(..., ge=1, le=2000)
    storage_type: str = Field(..., pattern="^(refrigerated|shelf_stable|hot_held)$")
    dietary_tags: List[str] = Field(..., min_length=1)
    expires_in_hours: float = Field(..., ge=2.0, le=720.0)
    sealed_commercial_source: bool = True

    @field_validator("sealed_commercial_source")
    @classmethod
    def require_commercial_or_sealed(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "Ontario Donation of Food Act guardrail: items must be sealed shelf-stable goods or from a DineSafe-verified commercial/catering source."
            )
        return v


class ClaimRequest(BaseModel):
    pantry_id: int
    volunteer_name: str = Field(..., min_length=2, max_length=80)


class PantryMatchOut(BaseModel):
    pantry_id: int
    pantry_name: str
    neighborhood: str
    address: str
    distance_km: float
    compatibility_score: int
    refrigeration_ok: bool
    matched_tags: List[str]


class SurplusBatchOut(BaseModel):
    id: int
    donor_id: int
    matched_pantry_id: Optional[int]
    title: str
    meal_count: int
    storage_type: str
    dietary_tags: str
    expires_at: datetime
    status: str
    volunteer_name: Optional[str]
    safety_checked: bool
    created_at: datetime
    claimed_at: Optional[datetime]
    picked_up_at: Optional[datetime]
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True
