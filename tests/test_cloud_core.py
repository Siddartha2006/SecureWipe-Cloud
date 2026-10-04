from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from backend.app import certificates
from backend.app.classification import classify
from backend.app.security import hash_password, verify_password


def test_classifier_is_advisory_and_detects_rules():
    result = classify(b"contact me at someone@example.org; password=not-real", "notes.txt")
    assert result["classification"] in {"MEDIUM", "HIGH", "CRITICAL"}
    assert "credential_keyword" in result["categories"]
    assert result["ai_assisted"] is False


def test_password_hash_is_salted_and_verified():
    first, second = hash_password("this is a secure passphrase"), hash_password("this is a secure passphrase")
    assert first != second
    assert verify_password("this is a secure passphrase", first)
    assert not verify_password("incorrect", first)


def test_certificate_signature_and_tamper_detection(monkeypatch):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    monkeypatch.setattr(certificates.settings, "certificate_private_key", pem)
    _, cert, pdf = certificates.create("job", "retention_1h", {"classification":"LOW"}, 12, "a" * 64)
    assert pdf.startswith(b"%PDF-")
    assert certificates.verify(cert)
    altered = dict(cert, input_size_bytes=13)
    assert not certificates.verify(altered)

