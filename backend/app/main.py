from fastapi import FastAPI
from .routes import subjects, search, analyze

app = FastAPI(title="Web Research Platform API")

app.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
app.include_router(search.router, tags=["search"])
app.include_router(analyze.router, tags=["analyze"])

@app.get("/healthz")
def healthz():
    return {"ok": True}
