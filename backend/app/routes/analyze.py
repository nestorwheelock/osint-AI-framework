from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class AnalyzeRequest(BaseModel):
    subject_id: str
    pipeline: str
    page_ids: List[str] = []

class AnalyzeResponse(BaseModel):
    run_id: str
    status: str

@router.post("/analyze", response_model=AnalyzeResponse, status_code=202)
def analyze(req: AnalyzeRequest):
    # Placeholder for TDD; returns a fake run id
    return AnalyzeResponse(run_id="RUN-TEST-0001", status="running")
