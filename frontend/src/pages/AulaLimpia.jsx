// Aula Limpia: sensor + filtro casero por salón. Página base para que el
// equipo de Aula Limpia la complete (estado del nodo, filtro, lecturas).
import { SALONES } from "../data/demo.js";
import { Semaforo } from "./Tablero.jsx";

export default function AulaLimpia() {
  return (
    <main className="rg-app">
      <div className="rg-demo-note">Demo con datos simulados.</div>
      <div className="rg-app__head">
        <div>
          <p className="rg-eyebrow">Aula Limpia</p>
          <h1>Aire limpio dentro del salón</h1>
        </div>
        <a className="rg-pill rg-pill--blue" href="#/tablero">Ver tablero</a>
      </div>
      <div className="rg-grid3">
        {SALONES.map((s) => (
          <div key={s.id} className="rg-panel rg-surface-mint">
            <div className="rg-panel__head">
              <h2>Salón {s.id}</h2>
              <Semaforo pm={s.dentro} />
            </div>
            <p className="rg-muted">{s.filtro ? `Filtro activo · ${s.proteccion} % protegido frente al aire de fuera.` : "Sin filtro todavía."}</p>
          </div>
        ))}
      </div>
    </main>
  );
}
