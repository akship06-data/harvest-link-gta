import math
from typing import List
from .models import Organization, SurplusBatch


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return round(2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


def rank_pantry_matches(batch: SurplusBatch, donor: Organization, pantries: List[Organization]) -> list[dict]:
    batch_tags = {t.strip().lower() for t in batch.dietary_tags.split(",") if t.strip()}
    requires_cold_chain = batch.storage_type in {"refrigerated", "hot_held"}
    ranked = []

    for pantry in pantries:
        if pantry.org_type != "pantry":
            continue
        if requires_cold_chain and not pantry.has_refrigeration:
            continue

        dist_km = haversine_km(donor.latitude, donor.longitude, pantry.latitude, pantry.longitude)
        if dist_km > 6.0:
            continue

        accepted = {t.strip().lower() for t in pantry.accepted_dietary.split(",") if t.strip()}
        overlap = sorted(batch_tags.intersection(accepted))
        if not overlap and batch_tags:
            continue

        proximity_score = max(0, int(60 - dist_km * 10))
        dietary_score = min(40, len(overlap) * 15)
        score = min(100, proximity_score + dietary_score)

        ranked.append(
            {
                "pantry_id": pantry.id,
                "pantry_name": pantry.name,
                "neighborhood": pantry.neighborhood,
                "address": pantry.address,
                "distance_km": dist_km,
                "compatibility_score": score,
                "refrigeration_ok": pantry.has_refrigeration,
                "matched_tags": overlap,
            }
        )

    ranked.sort(key=lambda x: (-x["compatibility_score"], x["distance_km"]))
    return ranked
