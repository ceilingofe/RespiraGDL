from fastapi import APIRouter

router = APIRouter(prefix="/salones", tags=["salones"])

@router.get("/{salon_id}/proteccion")
def proteccion(salon_id: str):
    # TODO(Juan): % de PM2.5 que no entra = 1 - dentro/fuera (promedio de la última hora)
    return {"salon_id": salon_id, "proteccion_pct": None}
