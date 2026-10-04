# Cloud architecture

The repository has two separate execution paths. `main.py` and `src/` are the existing Windows desktop application. The browser workflow lives in `web/`, the FastAPI API in `backend/app/`, and the queue consumer in `worker/`. The API does not import or invoke Tkinter or the local `WipeEngine`.

## Browser workflow

1. Next.js serves the account and workflow UI (Vercel-compatible).
2. The browser authenticates with a bearer token. The API associates all private uploads/jobs/certificates with the authenticated user.
3. FastAPI validates name/size/MIME metadata, creates a random storage key, and returns a five-minute presigned S3 POST policy with a content-length ceiling. The browser sends bytes directly to private S3.
4. Upload completion checks object size/type. Job creation reads bounded-size UTF-8 text and runs pattern detection plus optional backend-only OpenAI classification.
5. FastAPI enqueues a job in Redis/RQ. The independent worker downloads bytes, computes SHA-256, calls object deletion, verifies that `HEAD` returns missing, and signs certificate metadata.
6. PostgreSQL stores accounts, job/certificate metadata, PDF bytes (base64), and audit events. Public verification returns only the signed certificate metadata.
7. A separate cleanup process deletes pending/failed objects after their configured expiry.

## Guarantees and limits

The cloud result is **object-deletion requested and object absence observed**. S3-compatible deletion is not evidence of provider replica, backup, snapshot, or physical-media erasure. `standard`/multi-pass filesystem overwrite is not attempted in the cloud. The legacy local wipe code has platform/filesystem limitations and is not part of this workflow.

All certificate JSON fields other than `signature`, `public_key`, and `signature_algorithm` are canonically serialized (sorted keys, compact separators, UTF-8) and signed with RSA-PSS-SHA256. Verification uses the public key embedded in the certificate, proving integrity and key possession, not the truth of external claims. The key must be pinned/trusted out-of-band if signer identity matters.

Deployment needs API, worker and cleanup containers, PostgreSQL, Redis, private encrypted S3-compatible storage and secrets. The API and worker must use the same `DATABASE_URL`, storage settings and signing key. Vercel hosts only the frontend.
