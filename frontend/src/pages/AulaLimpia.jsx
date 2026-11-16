// Aula Limpia: sensor + filtro casero por salón. Con API usa los mismos salones que el tablero
// (GET /salones, cada minuto); sin API, los simulados de demo.js. Página base para que el equipo
// de Aula Limpia la complete (estado del nodo, filtro, lecturas).
import NotaDatos from "../components/NotaDatos.jsx";
import { apiAvisos, useConexionApi } from "../data/useAvisos.js";
import { useTableroDatos } from "../data/useDatos.js";
import { Semaforo, semaforoDe } from "./Tablero.jsx";

export default function AulaLimpia() {
  const modoApi = useConexionApi(apiAvisos);
  // Sin salón seleccionado: solo escuela, salones y pronóstico (no pide series).
  const { salones, origen } = useTableroDatos(modoApi, null);

  return (
    <main className="rg-app">
      <NotaDatos origen={origen} />
      <div className="rg-app__head">
        <div>
          <p className="rg-eyebrow">Aula Limpia</p>
          <h1>Aire limpio dentro del salón</h1>
        </div>
        <a className="rg-pill rg-pill--blue" href="#/tablero">Ver tablero</a>
      </div>
      <div className="rg-grid3">
        {/* Fondo con el color del semáforo del aire de adentro: el mismo que la píldora.
            Sin lecturas recientes no hay semáforo: fondo neutro y "Sin lecturas". */}
        {salones.map((s) => {
          const conDato = s.dentro != null;
          return (
            <div key={s.id} className={`rg-panel ${conDato ? `rg-aq-bg--${semaforoDe({ pm: s.dentro }).id}` : "rg-surface-mist"}`}>
              <div className="rg-panel__head">
                <h2>Salón {s.id}</h2>
                {conDato ? <Semaforo pm={s.dentro} /> : <span className="rg-muted">Sin lecturas</span>}
              </div>
              <p className="rg-muted">
                {!s.filtro ? "Sin filtro todavía."
                  : s.proteccion != null ? `Filtro registrado · diferencia dentro/fuera: ${s.proteccion} %. No confirma que el equipo esté encendido.`
                    : "Filtro registrado · sin lecturas en la última hora."}
              </p>
            </div>
          );
        })}
      </div>
    </main>
  );
}
