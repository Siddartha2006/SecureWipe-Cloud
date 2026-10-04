from datetime import datetime, timedelta, timezone

import pytest
from botocore.exceptions import ClientError
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from backend.app.db import Base, get_db
from backend.app.main import app
from backend.app.models import User, Upload, Job, Certificate, AuditEvent
from backend.app.config import settings
from backend.app.certificates import verify


@pytest.fixture
def system(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(engine)
    monkeypatch.setattr("backend.app.main.engine", engine)
    monkeypatch.setattr(settings, "jwt_secret", "test-secret-with-more-than-32-characters")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    monkeypatch.setattr(settings, "certificate_private_key", private)
    monkeypatch.setattr(settings, "public_verification_key", "")
    monkeypatch.setattr(app.state.limiter, "enabled", False)

    def override_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as client:
        yield client, TestingSession, private
    app.dependency_overrides.clear()
    engine.dispose()


def register(client, email="owner@example.com"):
    response = client.post("/api/auth/register", json={"email":email,"password":"correct horse battery staple"})
    assert response.status_code == 201
    return response.json()["access_token"]


def test_upload_job_authorization_and_validation(system, monkeypatch):
    client, Session, _ = system
    import backend.app.api as api
    monkeypatch.setattr(api.storage, "presign_upload", lambda *args:{"url":"https://storage.invalid","fields":{"policy":"signed"}})
    monkeypatch.setattr(api.storage, "head", lambda key:{"ContentLength":26,"ContentType":"text/plain","ETag":"\"etag-1\""})
    monkeypatch.setattr(api.storage, "get_with_etag", lambda key:(b"contact owner@example.test","etag-1"))
    class FakeQueue:
        def __init__(self,*args,**kwargs): pass
        def enqueue(self,*args,**kwargs): return None
    monkeypatch.setattr(api, "Queue", FakeQueue)

    token = register(client)
    auth = {"Authorization":f"Bearer {token}"}
    rejected = client.post("/api/upload/init", headers=auth, json={"filename":"bad.exe","size":26,"content_type":"text/plain"})
    assert rejected.status_code == 415
    oversized = client.post("/api/upload/init", headers=auth, json={"filename":"big.txt","size":26*1024*1024,"content_type":"text/plain"})
    assert oversized.status_code == 413
    init = client.post("/api/upload/init", headers=auth, json={"filename":"..\\private.txt","size":26,"content_type":"text/plain"})
    assert init.status_code == 200
    assert ".." not in init.json()["upload_id"]
    upload_id = init.json()["upload_id"]
    complete = client.post("/api/upload/complete", headers=auth, json={"upload_id":upload_id})
    assert complete.status_code == 200
    invalid_retention = client.post("/api/jobs", headers=auth, json={"upload_id":upload_id,"retention_hours":3})
    assert invalid_retention.status_code == 422
    queued = client.post("/api/jobs", headers=auth, json={"upload_id":upload_id,"retention_hours":1})
    assert queued.status_code == 202
    job_id = queued.json()["id"]
    assert queued.json()["classification"]["classification"] in {"LOW","MEDIUM","HIGH","CRITICAL"}
    assert client.get(f"/api/jobs/{job_id}", headers=auth).status_code == 200
    other = {"Authorization":f"Bearer {register(client, 'other@example.org')}"}
    assert client.get(f"/api/jobs/{job_id}", headers=other).status_code == 404
    assert client.post(f"/api/jobs/{job_id}/cancel", headers=other).status_code == 404
    assert client.post(f"/api/jobs/{job_id}/cancel", headers=auth).json()["status"] == "cancelled"
    assert client.post(f"/api/jobs/{job_id}/cancel", headers=auth).status_code == 409
    db = Session()
    assert db.query(AuditEvent).filter_by(event="AI_CLASSIFICATION_COMPLETED").count() == 1
    stored_upload=db.query(Upload).filter_by(id=upload_id).one()
    assert stored_upload.filename == "private.txt"
    assert len(stored_upload.sha256) == 64
    expiry=stored_upload.expires_at
    if expiry.tzinfo is None: expiry=expiry.replace(tzinfo=timezone.utc)
    assert 3500 <= (expiry-datetime.now(timezone.utc)).total_seconds() <= 3600
    db.close()


def test_worker_generates_signed_certificate_and_audit(system, monkeypatch):
    client, Session, _ = system
    import backend.app.worker as worker
    user = User(id="user-1", email="worker@example.net", password_hash="x")
    import hashlib
    upload = Upload(id="upload-1", user_id=user.id, object_key="uploads/user-1/random", filename="file.txt", size=4, content_type="text/plain", status="ready", etag="expected", sha256=hashlib.sha256(b"test").hexdigest(), expires_at=datetime.now(timezone.utc)+timedelta(hours=1))
    job = Job(id="job-1", user_id=user.id, upload_id=upload.id, status="queued", policy="retention_1h", classification={"classification":"LOW"})
    db = Session(); db.add_all([user,upload,job]); db.commit(); db.close()
    monkeypatch.setattr(worker, "SessionLocal", Session)
    monkeypatch.setattr(worker, "get_with_etag", lambda key:(b"test","expected"))
    monkeypatch.setattr(worker, "delete", lambda *args,**kwargs:None)
    def missing(key):
        raise ClientError({"Error":{"Code":"NoSuchKey"},"ResponseMetadata":{"HTTPStatusCode":404}},"HeadObject")
    monkeypatch.setattr(worker, "head", missing)
    worker.process_job(job.id)
    db=Session()
    stored_job=db.get(Job,job.id); cert=db.query(Certificate).one()
    assert stored_job.status == "completed"
    assert stored_job.certificate_id == cert.id
    assert verify(cert.payload)
    assert cert.payload["result"] == "object deletion requested and absence verified"
    assert {x.event for x in db.query(AuditEvent).all()} >= {"SANITIZATION_STARTED","FILE_DELETED","VERIFICATION_COMPLETED","CERTIFICATE_GENERATED"}
    db.close()


def test_public_verification_returns_invalid_for_tampered_stored_certificate(system):
    client, Session, _ = system
    owner=User(id="cert-user",email="cert@example.org",password_hash="x")
    job=Job(id="cert-job",user_id=owner.id,upload_id="upload-unused",status="completed",policy="retention_1h",classification={})
    # Public verification depends on certificate signature, not on an authenticated account.
    payload={"certificate_id":"SW-test","public_key":"bad","signature":"bad","signature_algorithm":"RSA-PSS-SHA256","input_size_bytes":1}
    db=Session(); db.add(owner); db.flush()
    # The job upload FK is required, so create a minimal upload first.
    upload=Upload(id="upload-unused",user_id=owner.id,object_key="key",filename="file.txt",size=1,content_type="text/plain",status="deleted",expires_at=datetime.now(timezone.utc))
    db.add(upload); db.flush(); db.add(job); db.add(Certificate(id="SW-test",user_id=owner.id,job_id=job.id,payload=payload,pdf="")); db.commit(); db.close()
    result=client.get("/api/verify/SW-test")
    assert result.status_code == 200
    assert result.json()["valid"] is False


def test_expired_upload_cleanup_logs_expiration(system, monkeypatch):
    _, Session, _ = system
    import backend.app.worker as worker
    user=User(id="cleanup-user",email="cleanup@example.com",password_hash="x")
    expired=Upload(id="expired",user_id=user.id,object_key="uploads/expired",filename="gone.txt",size=1,content_type="text/plain",status="ready",expires_at=datetime.now(timezone.utc)-timedelta(minutes=2))
    live=Upload(id="live",user_id=user.id,object_key="uploads/live",filename="live.txt",size=1,content_type="text/plain",status="pending",expires_at=datetime.now(timezone.utc)+timedelta(hours=1))
    db=Session();db.add_all([user,expired,live]);db.commit();db.close()
    removed=[]
    monkeypatch.setattr(worker,"SessionLocal",Session)
    monkeypatch.setattr(worker,"delete",lambda key:removed.append(key))
    worker.cleanup_expired()
    db=Session()
    assert removed == ["uploads/expired"]
    assert db.get(Upload,"expired").status == "expired"
    assert db.get(Upload,"live").status == "pending"
    assert db.query(AuditEvent).filter_by(event="FILE_EXPIRED").count() == 1
    db.close()

