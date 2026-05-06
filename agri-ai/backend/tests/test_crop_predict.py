"""Crop model mock path."""
from app.models import crop_model


def test_crop_predict_returns_mock_shape():
    # 1x1 PNG (minimal valid PNG bytes)
    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
        b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    crop_model.load_model()
    r = crop_model.predict(png)
    assert r["disease"] == "Leaf Blight"
    assert r["confidence"] == 0.87
    assert "treatment" in r
