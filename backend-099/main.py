from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import get_pool, close_pool
from routers import fasilitas
from routers import auth 

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀Starting server...🚀")
    
    await get_pool()
    print("✅Database connected✅")

    yield

    await close_pool()
    print("❌Database disconnected❌")


app = FastAPI(
    title="WebGIS API",
    description="API untuk data spasial + auth JWT",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fasilitas.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "🚀API WebGIS jalan🚀"}

@app.get("/detections")
async def get_detections():

    try:

        with open(
            "outputs/detections.geojson",
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        return JSONResponse(
            content=data
        )

    except FileNotFoundError:

        return JSONResponse(

            status_code=404,

            content={
                "message":
                "detections.geojson belum dibuat"
            }

        )