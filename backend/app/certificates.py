import base64, io, json, secrets
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from .config import settings


def canonical(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def signing_key():
    value = settings.certificate_private_key.replace("\\n", "\n").strip()
    pem = value.encode() if value.startswith("-----BEGIN") else base64.b64decode(value, validate=True)
    key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(key, rsa.RSAPrivateKey) or key.key_size < 2048:
        raise RuntimeError("Certificate key must be RSA with at least 2048 bits")
    if settings.public_verification_key:
        expected = settings.public_verification_key.replace("\\n", "\n").encode()
        configured = serialization.load_pem_public_key(expected)
        actual_der = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
        expected_der = configured.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
        if actual_der != expected_der:
            raise RuntimeError("Configured public and private certificate keys do not match")
    return key


def create(job_id: str, policy: str, classification: dict, size: int, digest: str) -> tuple[str, dict, bytes]:
    if not settings.certificate_private_key:
        raise RuntimeError("Certificate signing key is not configured")
    key = signing_key()
    cert_id = "SW-" + datetime.now(timezone.utc).strftime("%Y%m%d") + "-" + secrets.token_hex(5).upper()
    payload = {"certificate_id": cert_id, "issued_at": datetime.now(timezone.utc).isoformat(), "job_id": job_id,
        "method": "private object deletion", "policy": policy, "classification": classification,
        "input_size_bytes": size, "input_sha256": digest,
        "verification_url": f"{settings.verify_base_url.rstrip('/')}/verify/{cert_id}",
        "result": "object deletion requested and absence verified", "limitation": "Cloud object deletion does not prove physical media overwrite or immediate erasure from provider backups, replicas, or retained versions."}
    sig = key.sign(canonical(payload), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32), hashes.SHA256())
    pub = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    cert = {**payload, "signature_algorithm": "RSA-PSS-SHA256", "signature": base64.b64encode(sig).decode(), "public_key": pub}
    out = io.BytesIO()
    pdf = canvas.Canvas(out, pagesize=letter)
    pdf.setTitle("SecureWipe Certificate " + cert_id)
    pdf.setFont("Helvetica-Bold", 18); pdf.drawString(48, 740, "SecureWipe Sanitization Record")
    pdf.setFont("Helvetica", 10)
    y = 700
    for line in [f"Certificate: {cert_id}", f"Issued: {payload['issued_at']}", "Method: Private object deletion", f"Policy: {policy}", f"Input size: {size} bytes", f"SHA-256: {digest}", f"Verification: {payload['verification_url']}", "Result: Object absence verified after deletion request.", "Physical overwrite is not claimed. See JSON for limitations."]:
        for segment in simpleSplit(line, "Helvetica", 9, 515):
            pdf.drawString(48, y, segment); y -= 16
    pdf.save()
    return cert_id, cert, out.getvalue()


def verify(cert: dict) -> bool:
    try:
        data = {k: v for k, v in cert.items() if k not in ("signature", "public_key", "signature_algorithm")}
        public = serialization.load_pem_public_key(cert["public_key"].encode())
        public.verify(base64.b64decode(cert["signature"], validate=True), canonical(data), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32), hashes.SHA256())
        return True
    except Exception:
        return False
