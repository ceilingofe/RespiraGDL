from fastapi import APIRouter

router = APIRouter(prefix="/alertas", tags=["alertas"])

@router.get("/hoy")
def hoy():
    # TODO(Juan): usar ml/pronostico para decidir verde / amarillo / rojo por escuela
    return {"nivel": "amarillo", "recomendacion": "Recreo adentro; revisar inhaladores"}
