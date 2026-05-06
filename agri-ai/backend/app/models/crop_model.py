"""
Crop disease model — PyTorch-ready with mock predictions for demo deployments.
"""
import io
import logging
from typing import Any, Dict, Optional

from PIL import Image

logger = logging.getLogger(__name__)

_model_loaded = False
_device: Optional[str] = None


def load_model() -> None:
    """
    Load weights when available. For the conference build we register readiness
    without shipping large checkpoints.
    """
    global _model_loaded, _device
    try:
        import torch

        _device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("PyTorch available on %s; using mock classifier for demo.", _device)
    except ImportError:
        _device = None
        logger.warning("PyTorch not installed; mock classifier only.")
    _model_loaded = True


def predict(image_bytes: bytes) -> Dict[str, Any]:
    """
    Run inference. Currently returns a fixed mock result after validating the image.
    Replace with a real `torch.nn.Module` forward pass when weights are added.
    """
    if not _model_loaded:
        load_model()

    try:
        buf = io.BytesIO(image_bytes)
        with Image.open(buf) as img:
            img = img.convert("RGB")
            size = img.size
    except Exception as e:  # noqa: BLE001
        raise ValueError(f"Invalid image: {e}") from e

    # Mock output (user-specified shape)
    return {
        "disease": "Leaf Blight",
        "confidence": 0.87,
        "treatment": "Use fungicide and remove infected leaves",
        "image_size": f"{size[0]}x{size[1]}",
    }
