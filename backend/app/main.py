from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import lecturas, salones, alertas, plan_asma, escuelas

app = FastAPI(title="Respira GDL API")
app.include_router(lecturas.router)
app.include_router(salones.router)
app.include_router(alertas.router)
app.include_router(plan_asma.router)
app.include_router(escuelas.router)

# El tablero vive en GitHub Pages o en localhost:5173 y llama a esta API desde el navegador.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

@app.get("/salud")
def salud():
    return {"ok": True}
