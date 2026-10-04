# Security notes

## Data flow

Uploaded files go to the configured private Amazon S3 bucket over a presigned POST policy. The policy expires after five minutes, uses a random object key, requires the declared MIME type and server-side encryption, and enforces a 25 MiB maximum before accepting the upload. Current accepted MIME types are plain text, CSV and JSON; UTF-8 content is validated before classification. The API and worker need narrowly scoped credentials for the configured bucket.

If `OPENAI_API_KEY` is configured, the API sends up to 12 KiB of the text sample to OpenAI for advisory classification. Leave the key unset to use only regex checks. Never expose this key to browser code. Classification is not a guarantee that all sensitive content was found.

## Identity and authorization

Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes (310,000 iterations). Signed bearer tokens expire after 12 hours. Database lookups for jobs, upload completion, and certificate downloads are scoped to the authenticated account; the public verify endpoint exposes signed certificate metadata by ID. Redis-backed IP rate limiting is 120 requests/minute by default. Restrict CORS to known frontend origins and deploy only behind HTTPS.

This initial auth implementation lacks email verification, MFA, password reset, account lockout and administrator tooling. Tokens use session storage, so same-origin script injection could read them; apply CSP/XSS review and consider a BFF with HttpOnly cookies before broad production use.

## Certificate keys

Set `CERTIFICATE_PRIVATE_KEY` to the base64 encoding of a PEM RSA private key in a deployment secret store. Use 3072-bit or larger RSA keys, restrict access to API/worker, back up securely, rotate with an explicit key ID/pinning strategy, and never store it in source control. `PUBLIC_VERIFICATION_KEY` can be set to check the configured pair. Certificates embed the public key; self-contained verification proves only signature consistency, not an independently trusted organizational identity.

## Retention and cloud deletion

Successful jobs request object deletion and check that the key is no longer visible through `HEAD`. Failed or abandoned uploads are deleted by the cleanup service after 1, 6 or 24 hours. Certificate metadata and audit records remain in PostgreSQL. Configure provider lifecycle/versioning/backup retention separately. A missing key response does not prove replicas, provider backups or physical storage blocks are erased.

Audit metadata excludes file content, passwords and secrets. Public certificate verification makes certificate fields available to anyone with the certificate ID. Avoid sensitive personal information in filenames and certificate metadata.

## Threat model and gaps

The service reduces casual object exposure, cross-account record access and signature tampering. It does not scan for malware, offer DLP, encrypt each file with a per-user key, guarantee availability, resist compromise of the cloud operator/provider, or meet a named compliance standard. Database migrations, CSP, malware scanning, email identity, key revocation, incident response and storage-provider lifecycle controls remain operational requirements. The desktop `src/wipe_engine.py` cannot guarantee overwrites on all SSD, virtual, copy-on-write or remote storage.
