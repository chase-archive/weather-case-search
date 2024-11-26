import json
import os
from fastapi import APIRouter, HTTPException

from weather_cases.soundings.models import Profile


router = APIRouter(prefix="/soundings", tags=["soundings"])


@router.get("/{case_id}")
def get_sounding(case_id: str) -> Profile:
    current_dir = os.path.dirname(os.path.abspath(__name__))
    data_loc = os.path.join(current_dir, "data", "soundings", f"{case_id}.json")
    if not os.path.exists(data_loc):
        raise HTTPException(status_code=404, detail="Sounding not found")

    with open(data_loc, "r") as f:
        data = json.load(f)
        return Profile(**data)
