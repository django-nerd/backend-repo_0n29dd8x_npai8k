import os
import hashlib
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db

app = FastAPI(title="DeepTrace API", description="Deepfake-Driven Cyber Deception")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeResponse(BaseModel):
    job_id: str
    filename: str
    accuracy: float
    deepfake_likelihood: float
    frame_scores: List[dict]
    analyzed_at: datetime
    verification: Optional[dict] = None

@app.get("/")
def root():
    return {"name": "DeepTrace Backend", "status": "ok"}

@app.get("/test")
def test():
    resp = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
    }
    try:
        if db is not None:
            resp["database"] = "✅ Connected"
            resp["collections"] = db.list_collection_names()
        else:
            resp["database"] = "❌ Not Configured"
    except Exception as e:
        resp["database"] = f"⚠️ {str(e)[:80]}"
    return resp

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_media(file: UploadFile = File(...)):
    # Basic validation
    if not file.filename.lower().endswith((".mp4", ".avi")):
        raise HTTPException(status_code=400, detail="Only MP4 or AVI files are supported")

    content = await file.read()
    filehash = hashlib.sha256(content).hexdigest()
    filesize = len(content)

    # Simulate model outputs with deterministic pseudo-randomness from hash
    seed = int(filehash[:8], 16)
    def pseudo_rand(i):
        return ((seed * (i + 73)) % 1000) / 1000.0

    frame_scores = []
    total_frames = 60
    for i in range(total_frames):
        # create wave-like confidence around 0.5-1.0
        conf = 0.5 + 0.5 * ((pseudo_rand(i) + pseudo_rand(i//3)) / 2)
        conf = max(0.0, min(1.0, conf))
        frame_scores.append({"frame_index": i, "confidence": conf})

    deepfake_likelihood = sum(s["confidence"] for s in frame_scores) / total_frames
    accuracy = 0.95  # pretend our model has 95% accuracy on benchmark

    analyzed_at = datetime.now(timezone.utc)

    job_doc = {
        "filename": file.filename,
        "filesize": filesize,
        "filehash": filehash,
        "status": "completed",
        "accuracy": accuracy,
        "deepfake_likelihood": deepfake_likelihood,
        "model": "CNN+LSTM v1",
        "frame_scores": frame_scores,
        "analyzed_at": analyzed_at,
    }

    try:
        job_id = create_document("analysisjob", job_doc)
    except Exception:
        # If DB not available, still return results without persistence
        job_id = "temporary"

    # Fake a blockchain verification lookup
    verification = {
        "contract_address": "0xDeePTrAce00000000000000000000000000000001",
        "tx_hash": "0x" + filehash[:64],
        "network": "ethereum",
        "verified": True if int(filehash, 16) % 2 == 0 else False,
        "timestamp": analyzed_at.isoformat(),
    }

    return AnalyzeResponse(
        job_id=job_id,
        filename=file.filename,
        accuracy=accuracy,
        deepfake_likelihood=deepfake_likelihood,
        frame_scores=frame_scores,
        analyzed_at=analyzed_at,
        verification=verification,
    )

class VerifyRequest(BaseModel):
    filehash: str

@app.post("/api/verify")
def verify_media(payload: VerifyRequest):
    # Simulate chain proof lookup
    fh = payload.filehash.lower()
    verified = True if int(fh, 16) % 2 == 0 else False
    return {
        "filehash": fh,
        "contract_address": "0xDeePTrAce00000000000000000000000000000001",
        "tx_hash": "0x" + fh[:64],
        "network": "ethereum",
        "verified": verified,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/api/stats")
def stats():
    # Pull last few analysis jobs if DB available
    recent = []
    try:
        docs = get_documents("analysisjob", limit=10)
        for d in docs:
            d.pop("_id", None)
            recent.append(d)
    except Exception:
        pass

    return {
        "accuracy_benchmark": 0.95,
        "realtime_threats": int(datetime.now().timestamp()) % 100,  # playful changing number
        "analyses": len(recent),
        "recent": recent,
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
