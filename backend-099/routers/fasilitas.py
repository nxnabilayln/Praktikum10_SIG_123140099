from fastapi import APIRouter, HTTPException, Depends
from database import get_pool
from models import FasilitasCreate
from utils.auth import get_current_user
import json

router = APIRouter(
    prefix="/api/fasilitas",
    tags=["fasilitas"]
)

@router.get("/")
async def get_all(
    user=Depends(get_current_user)
):
    pool = await get_pool()

    async with pool.acquire() as conn:

        rows = await conn.fetch("""
            SELECT
                id,
                nama,
                jenis,
                alamat,
                ST_AsGeoJSON(geom) as geom
            FROM fasilitas_publik
        """)

    return [dict(row) for row in rows]

@router.post("/", status_code=201)
async def create_fasilitas(
    data: FasilitasCreate,
    user=Depends(get_current_user)
):
    pool = await get_pool()

    async with pool.acquire() as conn:

        row = await conn.fetchrow("""
            INSERT INTO fasilitas_publik
            (
                nama,
                jenis,
                alamat,
                geom
            )

            VALUES
            (
                $1,
                $2,
                $3,
                ST_SetSRID(
                    ST_Point($4,$5),
                    4326
                )
            )

            RETURNING
                id,
                nama,
                jenis,
                alamat,
                ST_X(geom) as longitude,
                ST_Y(geom) as latitude
        """,
        data.nama,
        data.jenis,
        data.alamat,
        data.longitude,
        data.latitude)

    return dict(row)

@router.get("/geojson")
async def geojson(
    user=Depends(get_current_user)
):
    pool = await get_pool()

    async with pool.acquire() as conn:

        rows = await conn.fetch("""
            SELECT
                id,
                nama,
                jenis,
                alamat,
                ST_AsGeoJSON(geom) as geom
            FROM fasilitas_publik
        """)

    features = []

    for row in rows:

        features.append({
            "type": "Feature",
            "geometry": json.loads(row["geom"]),
            "properties": {
                "id": row["id"],
                "nama": row["nama"],
                "jenis": row["jenis"],
                "alamat": row["alamat"]
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/nearby")
async def nearby(
    lat: float,
    lon: float,
    radius: int = 1000,
    user=Depends(get_current_user)
):
    pool = await get_pool()

    async with pool.acquire() as conn:

        rows = await conn.fetch("""
            SELECT
                id,
                nama,
                jenis,

                ROUND(
                    ST_Distance(
                        geom::geography,
                        ST_Point($1,$2)::geography
                    )
                ) as jarak

            FROM fasilitas_publik

            WHERE ST_DWithin(
                geom::geography,
                ST_Point($1,$2)::geography,
                $3
            )
        """,
        lon,
        lat,
        radius)

    return [dict(row) for row in rows]

@router.get("/{id}")
async def get_by_id(
    id: int,
    user=Depends(get_current_user)
):
    pool = await get_pool()

    async with pool.acquire() as conn:

        row = await conn.fetchrow("""
            SELECT
                id,
                nama,
                jenis,
                alamat,
                ST_X(geom) as longitude,
                ST_Y(geom) as latitude

            FROM fasilitas_publik

            WHERE id = $1
        """, id)

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Data tidak ditemukan"
        )

    return dict(row)

@router.put("/{id}")
async def update_fasilitas(
    id: int,
    data: FasilitasCreate,
    user=Depends(get_current_user)
):
    pool = await get_pool()

    async with pool.acquire() as conn:

        row = await conn.fetchrow("""
            UPDATE fasilitas_publik

            SET
                nama = $2,
                jenis = $3,
                alamat = $4,

                geom = ST_SetSRID(
                    ST_Point($5,$6),
                    4326
                )

            WHERE id = $1

            RETURNING
                id,
                nama,
                jenis,
                alamat
        """,
        id,
        data.nama,
        data.jenis,
        data.alamat,
        data.longitude,
        data.latitude)

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Data tidak ditemukan"
        )

    return dict(row)

@router.delete("/{id}")
async def delete_fasilitas(
    id: int,
    user=Depends(get_current_user)
):
    pool = await get_pool()

    async with pool.acquire() as conn:

        result = await conn.execute("""
            DELETE FROM fasilitas_publik
            WHERE id = $1
        """, id)

    if result == "DELETE 0":
        raise HTTPException(
            status_code=404,
            detail="Data tidak ditemukan"
        )

    return {
        "message": "Data berhasil dihapus"
    }