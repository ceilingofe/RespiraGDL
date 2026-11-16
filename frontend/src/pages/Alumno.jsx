import { useState } from "react";
import {
  DETONANTES, AVISAR_A, GRUPOS, guardarPlan, borrarPlan, nuevoId, nombres, usePlanesLocales,
} from "../data/planes.js";
import { salir } from "../data/sesion.js";

const VACIO = { salonId: "", inhalador: null, detonantes: [], avisar: "" };

// Resumen de un plan sin nada que identifique al alumno. Lo usa también la vista de la maestra.
export function ResumenPlan({ plan }) {
  return (
    <>
      <span><strong>{plan.inhalador ? "Usa inhalador de rescate" : "Sin inhalador de rescate"}</strong></span>
      <span>Le detona: {nombres(plan.detonantes, DETONANTES) || "no indicado"}</span>
      <span>Avisar a: {nombres([plan.avisar], AVISAR_A)}</span>
    </>
  );
}

export default function Alumno() {
  const planes = usePlanesLocales();
  const [form, setForm] = useState(null); // null = lista; objeto = formulario abierto
  const [guardado, setGuardado] = useState(false);

  const abrir = (plan) => { setGuardado(false); setForm(plan ? { ...plan } : { ...VACIO, id: nuevoId() }); };
  const cambiar = (campo, valor) => setForm((f) => ({ ...f, [campo]: valor }));
  const alternar = (id) => cambiar("detonantes",
    form.detonantes.includes(id) ? form.detonantes.filter((x) => x !== id) : [...form.detonantes, id]);

  const completo = form && form.salonId && form.inhalador !== null && form.avisar;
  const enviar = (e) => {
    e.preventDefault();
    if (!completo) return;
    // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
    // POST /planes (nuevo) o PUT /planes/{id} (edición). Hoy se guarda solo en este navegador.
    guardarPlan({ ...form, actualizado: new Date().toISOString() });
    setForm(null);
    setGuardado(true);
  };
  const borrar = (id) => {
    if (!window.confirm("¿Borrar este plan? No se puede deshacer.")) return;
    // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
    // DELETE /planes/{id}
    borrarPlan(id);
    setGuardado(false);
  };
  const grupo = (id) => GRUPOS.find((g) => g.id === id)?.nombre ?? id;

  return (
    <main className="rg-app rg-app--phone">
      <div className="rg-demo-note">Demo: usa datos ficticios. El plan se guarda solo en este navegador y no se comparte automáticamente con la maestra. No es un diagnóstico.</div>
      <div className="rg-phone-bar">
        <span className="rg-muted">Vista de la familia</span>
        <button type="button" className="rg-pill rg-pill--blue rg-tap" onClick={salir}>Salir</button>
      </div>
      <div className="rg-phone">
        {!form ? (
          <>
            <p className="rg-eyebrow">Alumno</p>
            <h1>Plan de asma en la escuela</h1>
            <p>
              Cuéntale a la maestra qué hacer si su hijo o hija tiene una crisis. No pedimos su nombre: la maestra
              solo ve el plan, sin datos que lo identifiquen.
            </p>

            <div aria-live="polite">
              {guardado && <p className="rg-sent">Plan guardado. La maestra del grupo ya lo puede ver.</p>}
            </div>

            {planes.length > 0 && (
              <>
                <h2 className="rg-phone__h2">Sus planes</h2>
                <ul className="rg-plans">
                  {planes.map((p) => (
                    <li key={p.id} className="rg-plan rg-surface-ice">
                      <span className="rg-plan__tag">{grupo(p.salonId)}</span>
                      <ResumenPlan plan={p} />
                      <div className="rg-plan__acts">
                        <button type="button" className="rg-pill rg-pill--white rg-tap" onClick={() => abrir(p)}>Editar</button>
                        <button type="button" className="rg-pill rg-pill--white rg-tap" onClick={() => borrar(p.id)}>Borrar</button>
                      </div>
                    </li>
                  ))}
                </ul>
              </>
            )}

            <button type="button" className="rg-pill rg-pill--primary rg-full rg-tap" onClick={() => abrir()}>
              {planes.length ? "Agregar otro plan (hermano o hermana)" : "Llenar el plan"}
            </button>
            <p className="rg-muted">
              Este plan no sustituye la indicación de su médico. Siga siempre el plan de acción que le dio.
            </p>
          </>
        ) : (
          <form className="rg-plan-form" onSubmit={enviar}>
            <button type="button" className="rg-pill rg-pill--blue rg-tap" onClick={() => setForm(null)}>← Volver</button>
            <h1>Plan de asma</h1>

            <div className="rg-field">
              <label htmlFor="rg-grupo">Grupo</label>
              <select id="rg-grupo" className="rg-input" value={form.salonId}
                onChange={(e) => cambiar("salonId", e.target.value)} required>
                <option value="" disabled>Elija el grupo</option>
                {GRUPOS.map((g) => <option key={g.id} value={g.id}>{g.nombre}</option>)}
              </select>
            </div>

            <fieldset className="rg-fieldset">
              <legend>¿Usa inhalador de rescate?</legend>
              <ul className="rg-checks">
                {[[true, "Sí"], [false, "No"]].map(([v, t]) => (
                  <li key={t}>
                    <label className={form.inhalador === v ? "is-on" : ""}>
                      <input type="radio" name="inhalador" checked={form.inhalador === v}
                        onChange={() => cambiar("inhalador", v)} required />
                      {t}
                    </label>
                  </li>
                ))}
              </ul>
            </fieldset>

            <fieldset className="rg-fieldset">
              <legend>¿Qué le detona una crisis? <span className="rg-muted">(puede elegir varias)</span></legend>
              <ul className="rg-checks">
                {DETONANTES.map((d) => (
                  <li key={d.id}>
                    <label className={form.detonantes.includes(d.id) ? "is-on" : ""}>
                      <input type="checkbox" checked={form.detonantes.includes(d.id)} onChange={() => alternar(d.id)} />
                      {d.nombre}
                    </label>
                  </li>
                ))}
              </ul>
            </fieldset>

            <fieldset className="rg-fieldset">
              <legend>Si tiene una crisis, avisar a</legend>
              <ul className="rg-checks">
                {AVISAR_A.map((a) => (
                  <li key={a.id}>
                    <label className={form.avisar === a.id ? "is-on" : ""}>
                      <input type="radio" name="avisar" checked={form.avisar === a.id}
                        onChange={() => cambiar("avisar", a.id)} required />
                      {a.nombre}
                    </label>
                  </li>
                ))}
              </ul>
              <p className="rg-muted">El teléfono no se pide aquí: la escuela ya lo tiene en su expediente.</p>
            </fieldset>

            <button type="submit" className="rg-pill rg-pill--primary rg-full rg-tap" disabled={!completo}>
              Guardar plan
            </button>
          </form>
        )}
      </div>
    </main>
  );
}
