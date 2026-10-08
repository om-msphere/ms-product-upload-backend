# Image Upload API

FastAPI service the mobile app uploads product images to. Storage keys stay on the server.

## Run locally

```bash
cd img-upload-backend
cp .env.example .env   
docker compose up -d --build
```

- API: http://localhost:8000 (interactive docs at `/docs`)
- Storage console (RustFS): http://localhost:9002

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | API + storage status |
| GET | `/api/v1/skus` | All SKUs with image count, last upload and a cover image |
| GET | `/api/v1/skus/{sku}` | `{exists, image_count}` for a SKU |
| GET | `/api/v1/skus/{sku}/images` | List images with temporary view URLs |
| POST | `/api/v1/skus/{sku}/images` | Upload one image as `multipart/form-data`, field `file` (JPEG/PNG, ≤ 10 MB) |
| DELETE | `/api/v1/skus/{sku}/images/{filename}` | Remove an image |

## Upload an image

```bash
curl -F file=@photo.jpg http://localhost:8000/api/v1/skus/ABC123/images
```

In Postman: `POST` the same URL, Body → form-data, key `file` (type File), pick an image.
The real type is checked from the file contents; anything other than JPEG/PNG gets `415`, over 10 MB gets `413`.

## Production notes

- `S3_PUBLIC_ENDPOINT` is the address clients use to open image links (`url` in responses); links are signed for that host.
- Phones only talk to the API, so storage can stay on a private network.
- Set `CREATE_BUCKET=false` and `CORS_ORIGINS` as needed; use strong storage keys.
- There is no auth in this service; put it behind the internal gateway.
