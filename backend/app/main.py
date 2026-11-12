from fastapi import FastAPI
from app.api import lecturas, salones, alertas

app = FastAPI(title="Respira GDL API")
app.include_router(lecturas.router)
app.include_router(salones.router)
app.include_router(alertas.router)

@app.get("/salud")
def salud():
    return {"ok": True}
