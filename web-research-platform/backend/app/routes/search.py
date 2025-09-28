from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from ..utils.url import canonicalize_url

router = APIRouter()

class SearchRequest(BaseModel):
    subject_id: str
    query: str
    engines: List[str] = ["google","ddg"]

class SearchResult(BaseModel):
    url: str
    canonical_url: str
    engine: str
    rank: int
    title: str = ""
    snippet: str = ""

@router.post("/search", response_model=List[SearchResult])
def meta_search(req: SearchRequest):
    # Fixture-backed stub for TDD
    # We simulate two engines returning same page with different tracking params
    results = [
        {"url":"https://example.com/post?id=123&utm_source=x#frag","engine":"google","rank":1},
        {"url":"https://EXAMPLE.com/post?utm_medium=y&id=123","engine":"ddg","rank":1},
    ]
    merged: Dict[str, Dict] = {}
    for r in results:
        c = canonicalize_url(r["url"])
        if c not in merged:
            merged[c] = {"url": r["url"], "canonical_url": c, "engine": r["engine"], "rank": r["rank"], "title":"", "snippet":""}
        else:
            # keep best rank; engines could be a list later
            merged[c]["rank"] = min(merged[c]["rank"], r["rank"])
    return [SearchResult(**v) for v in merged.values()]
