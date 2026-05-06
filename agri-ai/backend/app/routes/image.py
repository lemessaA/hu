"""Image analysis endpoint (crop disease mock / future PyTorch weights)."""
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.middleware.auth import verify_api_key
from app.models import crop_model
from app.schemas.image import ImageAnalysisResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["image"])

ALLOWED = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_BYTES = 5 * 1024 * 1024


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    _auth: None = Depends(verify_api_key),
):
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=400, detail="Unsupported image type")
    raw = await file.read()
    if not raw or len(raw) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="Invalid or too large image")
    try:
        result = crop_model.predict(raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001
        logger.exception("analyze-image failed")
        raise HTTPException(status_code=500, detail="Analysis failed") from e

    return ImageAnalysisResponse(
        disease=str(result.get("disease", "unknown")),
        confidence=float(result.get("confidence", 0.0)),
        treatment=str(result.get("treatment", "")),
        notes=str(result.get("note", "")) if result.get("note") else None,
        raw=result,
    )
