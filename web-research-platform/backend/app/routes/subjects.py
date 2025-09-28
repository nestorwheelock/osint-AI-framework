from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
import uuid

router = APIRouter()

# In-memory store for MVP tests
_SUBJECTS: Dict[str, Dict] = {}

class SubjectIn(BaseModel):
    name: str
    aliases: List[str] = Field(default_factory=list)

class SubjectOut(SubjectIn):
    id: str

@router.post("", response_model=SubjectOut, status_code=201)
def create_subject(payload: SubjectIn):
    key = payload.name.strip().lower()
    if key in (s['key'] for s in _SUBJECTS.values()):
        raise HTTPException(status_code=409, detail="duplicate subject")
    sid = str(uuid.uuid4())
    data = {"id": sid, "name": payload.name, "aliases": payload.aliases, "key": key}
    _SUBJECTS[sid] = data
    return SubjectOut(id=sid, name=payload.name, aliases=payload.aliases)

@router.get("/{sid}", response_model=SubjectOut)
def get_subject(sid: str):
    if sid not in _SUBJECTS:
        raise HTTPException(status_code=404, detail="not found")
    s = _SUBJECTS[sid]
    return SubjectOut(id=s["id"], name=s["name"], aliases=s["aliases"])
