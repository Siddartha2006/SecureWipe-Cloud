import base64, hashlib, re, uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from redis import Redis
from rq import Queue
from sqlalchemy import update
from .db import get_db
from .models import User, Upload, Job, Certificate, AuditEvent
from .security import current_user, hash_password, verify_password, issue_token
from .config import settings
from . import storage
from .classification import classify
from .certificates import verify

router = APIRouter()
ALLOWED_TYPES = {"text/plain", "text/csv", "application/json"}
EXTENSION_TYPES = {".txt":"text/plain", ".csv":"text/csv", ".json":"application/json"}


def audit(db, event, user_id=None, job_id=None, metadata=None):
    db.add(AuditEvent(user_id=user_id, job_id=job_id, event=event, metadata_json=metadata or {}))


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class Login(BaseModel):
    email: EmailStr
    password: str


class InitUpload(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    size: int = Field(gt=0)
    content_type: str


class CompleteUpload(BaseModel):
    upload_id: str


class CreateJob(BaseModel):
    upload_id: str
    retention_hours: int = Field(ge=1, le=24)


@router.post("/auth/register", status_code=201)
def register(body: Credentials, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.query(User).filter_by(email=email).first():
        raise HTTPException(409, "An account with this email already exists")
    user = User(id=str(uuid.uuid4()), email=email, password_hash=hash_password(body.password))
    db.add(user); db.commit()
    return {"access_token": issue_token(user.id), "token_type": "bearer"}


@router.post("/auth/login")
def login(body: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=body.email.lower()).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Email or password is incorrect")
    return {"access_token": issue_token(user.id), "token_type": "bearer"}


@router.post("/upload/init")
def upload_init(body: InitUpload, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if body.size > settings.upload_max_bytes: raise HTTPException(413, "File exceeds the configured upload size limit")
    if body.content_type not in ALLOWED_TYPES: raise HTTPException(415, "Only plain text, CSV, and JSON uploads are currently accepted")
    filename = re.sub(r"[^A-Za-z0-9._-]", "_", body.filename.split("/")[-1].split("\\")[-1])[:120] or "upload.txt"
    ext = "." + filename.rsplit(".",1)[-1].lower() if "." in filename else ""
    if EXTENSION_TYPES.get(ext) != body.content_type: raise HTTPException(415, "File extension and declared content type must match (.txt, .csv, or .json)")
    uid = str(uuid.uuid4()); key = f"uploads/{user.id}/{uid}"
    row = Upload(id=uid, user_id=user.id, object_key=key, filename=filename, size=body.size, content_type=body.content_type, expires_at=datetime.now(timezone.utc)+timedelta(hours=settings.retention_hours))
    try: signed = storage.presign_upload(key, body.content_type)
    except Exception as exc: raise HTTPException(503, "Private storage is unavailable") from exc
    db.add(row); audit(db, "UPLOAD_STARTED", user.id, metadata={"upload_id": uid, "size": body.size}); db.commit()
    return {"upload_id": uid, "upload_url": signed["url"], "upload_fields": signed["fields"], "expires_in": 300}


@router.post("/upload/complete")
def upload_complete(body: CompleteUpload, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.query(Upload).filter_by(id=body.upload_id, user_id=user.id).first()
    if not row: raise HTTPException(404, "Upload not found")
    try: obj = storage.head(row.object_key)
    except Exception as exc: raise HTTPException(400, "Uploaded object could not be confirmed") from exc
    if obj.get("ContentLength") != row.size or obj.get("ContentType") != row.content_type:
        try: storage.delete(row.object_key)
        finally: row.status = "rejected"; db.commit()
        raise HTTPException(400, "Uploaded object does not match the declared size or type")
    row.etag = obj.get("ETag", "").strip('"')
    if not row.etag: raise HTTPException(502, "Storage did not return an object version fingerprint")
    row.status = "ready"; audit(db, "UPLOAD_COMPLETED", user.id, metadata={"upload_id": row.id}); db.commit()
    return {"upload_id": row.id, "status": "ready"}


@router.post("/jobs", status_code=202)
def create_job(body: CreateJob, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if body.retention_hours not in (1, 6, 24): raise HTTPException(422, "Retention must be 1, 6, or 24 hours")
    upload = db.query(Upload).filter_by(id=body.upload_id, user_id=user.id, status="ready").first()
    if not upload: raise HTTPException(404, "Ready upload not found")
    if db.query(Job).filter_by(upload_id=upload.id).first(): raise HTTPException(409, "This upload already has a job")
    audit(db, "AI_CLASSIFICATION_STARTED", user.id, metadata={"upload_id":upload.id}); db.commit()
    try:
        obj, etag = storage.get_with_etag(upload.object_key)
        if etag != upload.etag: raise HTTPException(409, "Uploaded object changed after completion; upload it again")
        if len(obj) != upload.size: raise ValueError("size mismatch")
        try: obj.decode("utf-8")
        except UnicodeDecodeError as exc: raise HTTPException(415, "File content must be valid UTF-8 text") from exc
        result = classify(obj, upload.filename)
    except HTTPException: raise
    except Exception as exc: raise HTTPException(503, "Classification could not be completed") from exc
    upload.sha256 = hashlib.sha256(obj).hexdigest()
    upload.expires_at = datetime.now(timezone.utc) + timedelta(hours=body.retention_hours)
    job = Job(id=str(uuid.uuid4()), user_id=user.id, upload_id=upload.id, status="queued", policy=f"retention_{body.retention_hours}h", classification=result)
    db.add(job); audit(db, "AI_CLASSIFICATION_COMPLETED", user.id, job.id, {"classification": result["classification"], "ai_assisted": result["ai_assisted"]}); audit(db, "SANITIZATION_QUEUED", user.id, job.id, {"retention_hours": body.retention_hours}); db.commit()
    try: Queue("securewipe", connection=Redis.from_url(settings.redis_url)).enqueue("app.worker.process_job", job.id, job_timeout=600)
    except Exception as exc:
        db.execute(update(Job).where(Job.id == job.id, Job.status == "queued").values(status="failed", error="Queue unavailable")); db.commit()
        raise HTTPException(503, "Background queue is unavailable") from exc
    return {"id": job.id, "status": job.status, "classification": result}


@router.get("/jobs/{job_id}")
def job_status(job_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter_by(id=job_id, user_id=user.id).first()
    if not job: raise HTTPException(404, "Job not found")
    return {"id": job.id, "status": job.status, "policy": job.policy, "classification": job.classification, "certificate_id": job.certificate_id, "error": job.error}


@router.get("/jobs")
def list_jobs(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Job).filter_by(user_id=user.id).order_by(Job.created_at.desc()).limit(100).all()
    return [{"id":j.id,"status":j.status,"policy":j.policy,"classification":j.classification,"certificate_id":j.certificate_id,"created_at":j.created_at.isoformat()} for j in rows]


@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter_by(id=job_id, user_id=user.id).first()
    if not job: raise HTTPException(404, "Job not found")
    changed = db.execute(update(Job).where(Job.id == job_id, Job.user_id == user.id, Job.status == "queued").values(status="cancelled")).rowcount
    if changed != 1: raise HTTPException(409, "Only queued jobs can be cancelled")
    audit(db, "JOB_CANCELLED", user.id, job.id); db.commit()
    return {"id": job_id, "status": "cancelled"}


@router.get("/certificates")
def certificates(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Certificate).filter_by(user_id=user.id).order_by(Certificate.created_at.desc()).all()
    return [{"certificate_id": c.id, "created_at": c.created_at.isoformat(), "payload": c.payload} for c in rows]


@router.get("/certificates/{certificate_id}")
def certificate(certificate_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.query(Certificate).filter_by(id=certificate_id, user_id=user.id).first()
    if not row: raise HTTPException(404, "Certificate not found")
    return {"certificate": row.payload, "signature_valid": verify(row.payload)}


@router.get("/certificates/{certificate_id}/download")
def download(certificate_id: str, format: str = "json", user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.query(Certificate).filter_by(id=certificate_id, user_id=user.id).first()
    if not row: raise HTTPException(404, "Certificate not found")
    if format == "pdf":
        content = base64.b64decode(row.pdf)
        media, ext = "application/pdf", "pdf"
    elif format == "json": content, media, ext = __import__("json").dumps(row.payload, indent=2).encode(), "application/json", "json"
    else: raise HTTPException(422, "format must be json or pdf")
    audit(db, "CERTIFICATE_DOWNLOADED", user.id, metadata={"certificate_id": row.id, "format": ext}); db.commit()
    return Response(content, media_type=media, headers={"Content-Disposition": f'attachment; filename="{row.id}.{ext}"'})


@router.get("/verify/{certificate_id}")
def public_verify(certificate_id: str, db: Session = Depends(get_db)):
    row = db.query(Certificate).filter_by(id=certificate_id).first()
    if not row: raise HTTPException(404, "Certificate not found")
    audit(db, "VERIFICATION_STARTED", job_id=row.job_id, metadata={"certificate_id":row.id})
    valid = verify(row.payload)
    audit(db, "VERIFICATION_COMPLETED", job_id=row.job_id, metadata={"certificate_id":row.id,"valid":valid})
    db.commit()
    return {"certificate": row.payload, "valid": valid}
