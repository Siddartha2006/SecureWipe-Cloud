import hashlib, base64
from sqlalchemy.orm import Session
from sqlalchemy import update
from .db import SessionLocal
from .models import Job, Upload, Certificate, AuditEvent
from .storage import get_with_etag, delete, head
from .certificates import create, signing_key


def process_job(job_id: str):
    db: Session = SessionLocal()
    try:
        changed = db.execute(update(Job).where(Job.id == job_id, Job.status == "queued").values(status="processing")).rowcount
        if changed != 1:
            db.rollback()
            return
        db.commit()
        job = db.get(Job, job_id)
        upload = db.get(Upload, job.upload_id)
        signing_key()  # Fail before deleting the source object if signing is misconfigured.
        db.add(AuditEvent(user_id=job.user_id, job_id=job.id, event="SANITIZATION_STARTED", metadata_json={"method":"object_delete"})); db.commit()
        data, current_etag = get_with_etag(upload.object_key)
        if not upload.etag or current_etag != upload.etag:
            raise RuntimeError("Uploaded object changed after upload verification")
        digest = hashlib.sha256(data).hexdigest()
        del data
        if upload.sha256 and digest != upload.sha256:
            raise RuntimeError("Uploaded object content changed after classification")
        db.add(AuditEvent(user_id=job.user_id, job_id=job.id, event="VERIFICATION_STARTED", metadata_json={"check":"object_absence"})); db.commit()
        delete(upload.object_key, upload.etag)
        try: head(upload.object_key)
        except Exception as exc:
            from .storage import is_not_found
            if not is_not_found(exc): raise RuntimeError("Could not verify object deletion") from exc
        else: raise RuntimeError("Object still exists after deletion request")
        upload.status = "deleted"
        db.add(AuditEvent(user_id=job.user_id, job_id=job.id, event="FILE_DELETED", metadata_json={"verification":"head_object_not_found"}))
        db.add(AuditEvent(user_id=job.user_id, job_id=job.id, event="VERIFICATION_COMPLETED", metadata_json={"valid":True}))
        cert_id, payload, pdf = create(job.id, job.policy, job.classification, upload.size, digest)
        db.add(Certificate(id=cert_id, user_id=job.user_id, job_id=job.id, payload=payload, pdf=base64.b64encode(pdf).decode()))
        job.status = "completed"; job.certificate_id = cert_id
        db.add(AuditEvent(user_id=job.user_id, job_id=job.id, event="SANITIZATION_COMPLETED", metadata_json={"certificate_id": cert_id}))
        db.add(AuditEvent(user_id=job.user_id, job_id=job.id, event="CERTIFICATE_GENERATED", metadata_json={"certificate_id": cert_id}))
        db.commit()
    except Exception:
        db.rollback()
        job = db.get(Job, job_id)
        if job:
            job.status = "failed"; job.error = "Processing failed; support metadata retained without file content"
            db.add(AuditEvent(user_id=job.user_id, job_id=job.id, event="JOB_FAILED", metadata_json={}))
            db.commit()
        raise
    finally: db.close()


def cleanup_expired():
    from datetime import datetime, timezone
    from .models import Upload
    db = SessionLocal()
    try:
        rows = db.query(Upload).filter(Upload.expires_at <= datetime.now(timezone.utc), Upload.status.in_(["pending", "ready"])).all()
        for row in rows:
            try: delete(row.object_key)
            except Exception: continue
            row.status = "expired"
            db.add(AuditEvent(user_id=row.user_id, event="FILE_EXPIRED", metadata_json={"upload_id":row.id}))
        db.commit()
    finally: db.close()
