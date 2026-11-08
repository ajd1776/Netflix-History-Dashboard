"""HTTP API. Uploaded files are analysed in memory and never written to disk."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, UploadFile
from fastapi.staticfiles import StaticFiles

from .parsing import DateOrder, HistoryError, read_history
from .sample import sample_csv
from .stats import analyse

MAX_UPLOAD = 20 * 1024 * 1024
# Inside the Mac app (PyInstaller) the built web files sit next to the code.
WEB_DIST = (
    Path(getattr(sys, "_MEIPASS", "")) / "web"
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parents[3] / "web" / "dist"
)

app = FastAPI(title="Netflix History API")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/sample")
def sample() -> dict:
    return _sample_analysis()


@lru_cache(maxsize=1)
def _sample_analysis() -> dict:
    return analyse(read_history(sample_csv()))


@app.post("/api/analyze")
async def analyze(file: UploadFile, date_order: Annotated[DateOrder, Query()] = "auto") -> dict:
    raw = await file.read(MAX_UPLOAD + 1)
    if len(raw) > MAX_UPLOAD:
        raise HTTPException(413, "That file is over 20 MB.")
    try:
        return analyse(read_history(raw, date_order))
    except HistoryError as exc:
        raise HTTPException(422, str(exc)) from exc


# When built, the API also serves the React app, so one local server does everything.
if WEB_DIST.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIST, html=True), name="web")
