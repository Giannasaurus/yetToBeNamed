import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from cv_tracker import analyze_video


app = FastAPI(title="PhysiVision CV API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/analyze")
def analyze(file: UploadFile = File(...)):
    suffix = Path(file.filename or "upload.mp4").suffix or ".mp4"

    with tempfile.TemporaryDirectory(prefix="physivision-") as temp_dir:
        temp_path = Path(temp_dir)
        video_path = temp_path / f"upload{suffix}"

        with video_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            result = analyze_video(video_path, output_dir=temp_path)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        return {
            "samples": result["samples"],
            "fps": result["fps"],
            "dt": result["dt"],
            "centers": result["centers"],
        }
