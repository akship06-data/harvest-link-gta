from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    org_type = Column(String, nullable=False)  # donor | pantry
    neighborhood = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    dinesafe_verified = Column(Boolean, default=True)
    has_refrigeration = Column(Boolean, default=True)
    accepted_dietary = Column(String, default="vegetarian,halal,nut_free,shelf_stable")

    donations = relationship("SurplusBatch", back_populates="donor", foreign_keys="SurplusBatch.donor_id")


class SurplusBatch(Base):
    __tablename__ = "surplus_batches"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    matched_pantry_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    title = Column(String, nullable=False)
    meal_count = Column(Integer, nullable=False)
    storage_type = Column(String, nullable=False)  # refrigerated | shelf_stable | hot_held
    dietary_tags = Column(String, nullable=False)  # comma-separated tags
    expires_at = Column(DateTime(timezone=True), nullable=False)

    status = Column(String, default="AVAILABLE")  # AVAILABLE -> CLAIMED -> PICKED_UP -> DELIVERED
    volunteer_name = Column(String, nullable=True)
    safety_checked = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    picked_up_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    donor = relationship("Organization", back_populates="donations", foreign_keys=[donor_id])
    matched_pantry = relationship("Organization", foreign_keys=[matched_pantry_id])
