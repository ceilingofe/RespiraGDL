# Backend Respira GDL (Juan)

API FastAPI + SQLite. Recibe las lecturas de los ESP32, calcula el % de protección de cada salón, genera alertas y da el pronóstico de PM2.5 de mañana.

> Orienta y alerta; **no es una herramienta de diagnóstico**. Solo guarda el *número* de alumnos con asma por grupo, nunca nombres.

## Correrlo

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env            # opcional; sin .env usa los valores por defecto
python -m scripts.cargar_demo      # crea los salones 1A–6B de la escuela "miravalle"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Documentación interactiva: http://localhost:8000/docs
- `--host 0.0.0.0` es para que los ESP32 de la misma red WiFi lleguen a la laptop. En `config.h` pongan `API_URL "http://<IP-de-la-laptop>:8000/lecturas"` (la IP sale con `ipconfig` en Windows o `ip a` en Linux).
- Pruebas: `pytest backend/tests -q` desde la raíz (es lo que corre el CI).

### Sin sensores (plan B)

```bash
python -m scripts.cargar_demo --lecturas          # 8 h de lecturas SIMULADAS para los 6 salones
python -m scripts.simular_nodos --salon 3A        # finge ser los dos ESP32 en vivo
python -m scripts.simular_nodos --csv grabadas.csv  # reproduce lecturas reales grabadas (nodo_id,pm25)
python -m scripts.cargar_demo --borrar-simuladas  # limpiar antes de medir con los sensores reales
```

Todo lo simulado queda con `simulada = 1` en la base, para decir en la demo qué parte es simulada (regla 5 del kit).

## Convención de `nodo_id` (Sergio)

El firmware solo manda `nodo_id`, `pm25` y `pm10`. El backend saca la escuela, el salón y si está dentro o fuera del nombre:

| `nodo_id` | Qué es |
| --- | --- |
| `esc-miravalle-salon-3A-dentro` | sensor dentro del salón 3A |
| `esc-miravalle-salon-3A-fuera` | sensor afuera del salón 3A |
| `esc-miravalle-fuera` | sensor de afuera compartido por toda la escuela |

Para el % de protección, la API usa primero el sensor de afuera del salón. Si ese no existe, usa el de la escuela. Si el nombre no sigue la convención, la API responde 422.

Si en `.env` ponen `NODO_TOKEN=algo`, el ESP32 debe mandar el header `X-Nodo-Token: algo` (`http.addHeader("X-Nodo-Token", NODO_TOKEN);`). Si está vacío, no se pide token (modo demo).

## Endpoints (Carlos)

| Método y ruta | Para qué | Respuesta |
| --- | --- | --- |
| `POST /lecturas` | lo llama el ESP32 | `{"recibida", "id", "escuela", "salon_id", "ubicacion"}` |
| `GET /salones` | tabla del tablero | lista con la forma de `SALONES` de `demo.js`: `id, grupo, fuera, dentro, asma, filtro, proteccion` + `estado` (`ok`, `baja`, `aire_limpio`, `sin_datos`) y `nivel_dentro` |
| `POST /salones` | dar de alta un grupo | body `{"id":"3B","escuela":"miravalle","grupo":"3° B","alumnos_asma":5,"filtro":true}` |
| `GET /salones/{id}/proteccion` | tarjeta de un salón | `{"salon_id","proteccion_pct","estado","fuera","dentro","fuente_fuera","ventana_min"}` |
| `GET /lecturas/serie?salon_id=3A` | gráfica del día | forma de `SERIE`: `[{"h":"7:00","fuera":48,"dentro":40}, …]` |
| `GET /lecturas?salon_id=3A&horas=24` | lecturas crudas | lista, la más reciente primero |
| `GET /lecturas/nodos` | ¿están vivos los sensores? | última lectura de cada nodo |
| `GET /pronostico` | tarjeta de pronóstico | `{"fuente", "fecha_base", "dias":[{"dia":"Hoy","pm":62,"semaforo":"amarillo","nivel":"bad","nombre","consejo"}, {"dia":"Mañana",…}], "metricas_modelo", "desactualizado"}` |
| `GET /alertas/hoy` | semáforo del día (tablero, maestro, bot) | `{"nivel":"amarillo","pm":62,"categoria":"bad","nombre","recomendacion","manana":{…},"fuente","alertas":[…]}` |
| `GET /alertas` | lista de alertas | `[{"tipo","prioridad","salon_id","mensaje"}]` ordenadas urgente → aviso → info |
| `GET /salud` | prueba de vida | `{"ok": true}` |

`nivel` / `categoria` usan los mismos ids que `NIVELES` del frontend (`good`, `ok`, `bad`, `vbad`, `ext`), así que se pueden poner directo en `rg-aq--{id}`. El semáforo de la escuela agrupa así: verde = Buena o Aceptable, amarillo = Mala (recreo adentro para niños con asma), rojo = Muy mala o peor.

Tipos de alerta:

| Tipo | Cuándo se dispara |
| --- | --- |
| `proteccion_baja` | salón con filtro y protección < `PROTECCION_MINIMA` (40 %) |
| `dentro_alto` | PM2.5 dentro > `ALERTA_UMBRAL_PM25`; es urgente si el grupo tiene alumnos con asma |
| `sensor_desconectado` | un nodo real sin datos por más de `MINUTOS_SIN_DATOS` (10 min) |
| `pronostico` | mañana amarillo o rojo; trae `familias` = alumnos con asma a los que hay que avisar (lo usa el bot) |

## Cómo se calcula

- **% de protección** = `1 − dentro / fuera`, con el promedio de los últimos `VENTANA_PROTECCION_MIN` minutos (60) de cada sensor. Se limita a 0–100 %. Si afuera hay menos de 10 µg/m³, no se calcula (`aire_limpio`) porque el % no significaría nada.
- **Pronóstico**: ver `ml/README.md` y `docs/metodo-y-datos.md`. Orden de respaldo: modelo entrenado → persistencia con la serie del SIMAJ → persistencia con el sensor de afuera de hoy.

## Archivos

```
app/main.py            arranque, CORS y /salud
app/config.py          variables del .env
app/db.py              SQLite (solo librería estándar)
app/api/               endpoints
app/core/              lógica sin FastAPI: nodos, protección, semáforo, estado/alertas, pronóstico
app/services/sinaica.py descarga del SIMAJ/SINAICA (dataset 39)
scripts/               cargar_demo.py, simular_nodos.py
tests/                 pytest
```
