"""
Backend API tests. Run with:  pytest  (from backend/, with .env configured for INFERENCE_MODE=mock)
"""
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _make_image_bytes(fmt="JPEG", color=(60, 140, 60), size=(200, 200)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf.read()


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_diseases_list_returns_known_entries():
    resp = client.get("/api/v1/diseases")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 10
    crops = {item["crop"] for item in data}
    assert "Tomato" in crops


def test_analyze_valid_image_english():
    img_bytes = _make_image_bytes()
    resp = client.post(
        "/api/v1/analyze",
        files={"image": ("leaf.jpg", img_bytes, "image/jpeg")},
        data={"text": "brown spots", "language": "en"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["language"] == "en"
    assert body["is_mock"] is True
    assert 0.0 <= body["confidence"] <= 1.0
    assert isinstance(body["symptoms"], list)


def test_analyze_valid_image_hindi():
    img_bytes = _make_image_bytes(color=(140, 70, 30))
    resp = client.post(
        "/api/v1/analyze",
        files={"image": ("leaf.jpg", img_bytes, "image/jpeg")},
        data={"language": "hi"},
    )
    assert resp.status_code == 200
    assert resp.json()["language"] == "hi"


def test_analyze_missing_image_returns_400_family_error():
    resp = client.post("/api/v1/analyze", data={"language": "en"})
    assert resp.status_code == 422  # FastAPI request validation (missing required field)
    assert "traceback" not in resp.text.lower()


def test_analyze_unsupported_language():
    img_bytes = _make_image_bytes()
    resp = client.post(
        "/api/v1/analyze",
        files={"image": ("leaf.jpg", img_bytes, "image/jpeg")},
        data={"language": "fr"},
    )
    assert resp.status_code == 400
    assert "unsupported language" in resp.json()["detail"].lower()


def test_analyze_non_image_file_rejected():
    resp = client.post(
        "/api/v1/analyze",
        files={"image": ("not_an_image.txt", b"hello world", "text/plain")},
        data={"language": "en"},
    )
    assert resp.status_code == 400


def test_analyze_corrupted_image_rejected():
    resp = client.post(
        "/api/v1/analyze",
        files={"image": ("broken.jpg", b"\xff\xd8\xff\x00not-a-real-jpeg", "image/jpeg")},
        data={"language": "en"},
    )
    assert resp.status_code == 400


def test_feedback_endpoint():
    resp = client.post(
        "/api/v1/feedback",
        json={"crop": "Tomato", "disease": "Early Blight", "helpful": True, "comment": "Useful"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "received"
