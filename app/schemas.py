from datetime import datetime
from typing import Annotated

from fastapi import Path
from pydantic import BaseModel

SkuPath = Annotated[
    str,
    Path(pattern=r"^[A-Za-z0-9_-]{1,64}$", description="Product SKU (letters, digits, - and _)"),
]


class SkuInfo(BaseModel):
    sku: str
    exists: bool
    image_count: int


class ImageItem(BaseModel):
    key: str
    filename: str
    size: int
    last_modified: datetime
    url: str


class ImageList(BaseModel):
    sku: str
    images: list[ImageItem]


class SkuSummary(BaseModel):
    sku: str
    image_count: int
    last_uploaded: datetime
    cover_url: str


class SkuList(BaseModel):
    total: int
    skus: list[SkuSummary]
