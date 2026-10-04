import uuid, time, json, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from .db import Base, engine
from .api import router
from .certificates import signing_key
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

@asynccontextmanager
async def lifespan(_app):
    startup()
    yield


app = FastAPI(title="SecureWipe API", version="1.0.0", docs_url=None, redoc_url=None, lifespan=lifespan)
app.state.limiter = Limiter(key_func=get_remote_address, storage_uri=settings.redis_url, default_limits=["120/minute"])
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
origins = [x.strip() for x in settings.allowed_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET","POST"], allow_headers=["Authorization","Content-Type","X-Request-ID"])

def startup():
    if settings.jwt_secret == "change-me-before-deployment" or len(settings.jwt_secret) < 32 or "replace" in settings.jwt_secret.lower():
        raise RuntimeError("Set JWT_SECRET to at least 32 random characters")
    if not settings.certificate_private_key:
        raise RuntimeError("CERTIFICATE_PRIVATE_KEY is required")
    signing_key()
    Base.metadata.create_all(bind=engine)

@app.middleware("http")
async def security(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))[:80]
    start = time.monotonic()
    try: response = await call_next(request)
    except Exception:
        response = JSONResponse({"error":"internal_error", "request_id":request_id}, status_code=500)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    logging.info(json.dumps({"request_id":request_id,"method":request.method,"status":response.status_code,"duration_ms":round((time.monotonic()-start)*1000,2)}))
    return response

@app.get("/health")
def health(): return {"status":"ok"}

app.include_router(router, prefix="/api")
