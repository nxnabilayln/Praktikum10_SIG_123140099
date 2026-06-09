from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from database import get_pool
from utils.auth import create_access_token

router = APIRouter(tags=["auth"])

@router.post("/register")
async def register(email: str, password: str):
    pool = await get_pool()

    async with pool.acquire() as conn:

        existing = await conn.fetchrow(
            "SELECT * FROM users WHERE email=$1",
            email
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email sudah terdaftar"
            )

        await conn.execute(
            """
            INSERT INTO users (email, password)
            VALUES ($1, $2)
            """,
            email,
            password
        )

    return {
        "message": "Register berhasil"
    }

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    pool = await get_pool()

    async with pool.acquire() as conn:

        user = await conn.fetchrow(
            """
            SELECT * FROM users
            WHERE email = $1
            """,
            form.username
        )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="User tidak ditemukan"
        )

    if form.password != user["password"]:
        raise HTTPException(
            status_code=400,
            detail="Password salah"
        )

    token = create_access_token({
        "sub": user["email"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }