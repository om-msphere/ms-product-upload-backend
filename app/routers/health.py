import logging

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.storage import internal_client

log = logging.getLogger("upload-api")

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> JSONResponse:
    try:
        internal_client().head_bucket(Bucket=get_settings().s3_bucket)
    except (BotoCoreError, ClientError):
        log.exception("Health check: storage unreachable")
        return JSONResponse(status_code=503, content={"status": "error", "storage": "unavailable"})
    return JSONResponse(content={"status": "ok", "storage": "ok"})
