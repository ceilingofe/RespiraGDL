from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alertas, lecturas, pronostico, salones
from app.db import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Respira GDL API",
    description="Lecturas de PM2.5 de los salones, % de protección, alertas y pronóstico a 24 h. "
                "Orienta y alerta; no es una herramienta de diagnóstico.",
    version="0.1.0",
    lifespan=lifespan,
)

# Demo: el tablero (Vite, GitHub Pages) y el bot llaman desde otro origen.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(lecturas.router)
app.include_router(salones.router)
app.include_router(alertas.router)
app.include_router(pronostico.router)


@app.get("/salud", tags=["salud"])
def salud():
    return {"ok": True}
