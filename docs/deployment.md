# Deployment

## Local containers

1. Copy `.env.example` to `.env` and provide a long random `JWT_SECRET`, strong database password, generated RSA key (base64 PEM in `CERTIFICATE_PRIVATE_KEY`), private bucket endpoint/name/credentials and correct origins.
2. Ensure the bucket has public access blocked and server-side encryption enabled. Configure bucket CORS to permit browser POST from the local frontend origin. This build uses presigned POST policies to enforce the upload size limit; Cloudflare R2's documented presigned URL support does not include HTML form POST.
3. Run `docker compose up --build`. Open `http://localhost:3000`; the API health check is `http://localhost:8000/health`.
4. Register an account, upload UTF-8 text/CSV/JSON (up to 25 MiB), and watch the job. This requires live AWS S3 credentials; compose does not include a mock object store.

## Production services

- PostgreSQL: managed, private network, backups and TLS. API currently bootstraps tables with SQLAlchemy `create_all`; add versioned migrations before schema evolution/production release.
- Redis: managed/private and persistent enough for queue requirements. Restrict network access.
- Object storage: private Amazon S3 bucket, encryption at rest, least-privilege credentials, short-lived presigned POST policy support, provider lifecycle/version retention review.
- API: build `backend/Dockerfile`; run FastAPI on port 8000 behind TLS. Set health check `/health`.
- Worker: build `worker/Dockerfile`; run one or more long-lived RQ consumers with `REDIS_URL`, DB, storage, OpenAI (optional), and certificate key. Do not host it as a Vercel function.
- Cleanup: run the same worker image with command `python -m app.cleanup`, separately from the queue consumer.
- Frontend: deploy `web/` to Vercel. Set Root Directory `web`, and define `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_APP_URL` as public URLs. Set backend `ALLOWED_ORIGINS` to the deployed frontend origin.

The API and worker must share private secrets/configuration, including certificate signing key. Store secrets in the hosting provider's secret manager and never in frontend variables. Protect API, PostgreSQL, Redis and object storage with network policies. Review proxy address handling for rate limits and configure strict TLS/CORS.

## GitHub Actions

`.github/workflows/cloud-ci.yml` runs frontend typecheck/build/npm audit, Python tests/Ruff/pip-audit, and builds API/worker/frontend Docker images. It does not deploy. The existing `build-windows.yml` handles tagged desktop executable releases. No deployment credentials are committed.
