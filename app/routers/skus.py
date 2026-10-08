from fastapi import APIRouter, Query

from app.config import get_settings
from app.schemas import ImageItem, ImageList, SkuInfo, SkuList, SkuPath, SkuSummary
from app.storage import internal_client, public_client, sku_prefix

router = APIRouter(prefix="/api/v1/skus", tags=["skus"])


def _list_objects(prefix: str) -> list[dict]:
    paginator = internal_client().get_paginator("list_objects_v2")
    objects: list[dict] = []
    for page in paginator.paginate(Bucket=get_settings().s3_bucket, Prefix=prefix):
        objects.extend(page.get("Contents", []))
    return objects


def _view_url(key: str) -> str:
    s = get_settings()
    return public_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": s.s3_bucket, "Key": key},
        ExpiresIn=s.view_url_expires,
    )


@router.get("", response_model=SkuList)
def list_skus(
    limit: int = Query(100, ge=1, le=500, description="SKUs per page"),
    offset: int = Query(0, ge=0, description="SKUs to skip"),
) -> SkuList:
    """SKUs that have images, newest upload first. `total` is the count across all pages."""
    root = f"{get_settings().upload_prefix}/"
    latest: dict[str, dict] = {}
    counts: dict[str, int] = {}
    for obj in _list_objects(root):
        parts = obj["Key"][len(root):].split("/", 1)
        if len(parts) != 2 or not parts[1]:
            continue
        sku = parts[0]
        counts[sku] = counts.get(sku, 0) + 1
        if sku not in latest or obj["LastModified"] > latest[sku]["LastModified"]:
            latest[sku] = obj

    # Sort and slice first so only the returned page gets signed URLs.
    ordered = sorted(latest.items(), key=lambda kv: kv[1]["LastModified"], reverse=True)
    page = [
        SkuSummary(
            sku=sku,
            image_count=counts[sku],
            last_uploaded=obj["LastModified"],
            cover_url=_view_url(obj["Key"]),
        )
        for sku, obj in ordered[offset : offset + limit]
    ]
    return SkuList(total=len(ordered), skus=page)


@router.get("/{sku}", response_model=SkuInfo)
def get_sku(sku: SkuPath) -> SkuInfo:
    sku = sku.upper()
    count = len(_list_objects(sku_prefix(sku)))
    return SkuInfo(sku=sku, exists=count > 0, image_count=count)


@router.get("/{sku}/images", response_model=ImageList)
def list_images(sku: SkuPath) -> ImageList:
    """All images of one SKU, newest first."""
    sku = sku.upper()
    objects = sorted(_list_objects(sku_prefix(sku)), key=lambda o: o["LastModified"], reverse=True)
    images = [
        ImageItem(
            key=o["Key"],
            filename=o["Key"].rsplit("/", 1)[-1],
            size=o["Size"],
            last_modified=o["LastModified"],
            url=_view_url(o["Key"]),
        )
        for o in objects
    ]
    return ImageList(sku=sku, images=images)
