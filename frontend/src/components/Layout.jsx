import { useEffect, useState } from "react";
import { ROUTES } from "../routes.js";

export function Logo({ big }) {
  return (
    <a href="#/" className={`rg-logo${big ? " rg-logo--big" : ""}`} aria-label="Respira GDL, inicio">
      <svg viewBox="0 0 32 32" aria-hidden="true">
        <rect x="2" y="2" width="28" height="28" rx="9" fill="none" stroke="currentColor" strokeWidth="3.2" />
        <path d="M9 21c0-6 5-10 14-11-1 8-5 13-11 13-1 0-2-1-3-2z" fill="currentColor" />
      </svg>
      <span>Respira GDL</span>
    </a>
  );
}

export function Navbar({ route }) {
  const [open, setOpen] = useState(false);
  useEffect(() => setOpen(false), [route]);
  const pages = ROUTES.filter((r) => r.nav).map((r) => [`#${r.path}`, r.nav]);
  const links = [pages[0], ["#/#como", "Cómo funciona"], ...pages.slice(1)];
  return (
    <header className="rg-nav">
      <Logo />
      <button className="rg-nav__toggle" aria-label="Abrir menú" aria-expanded={open} onClick={() => setOpen(!open)}>
        <span /><span />
      </button>
      <nav className={`rg-nav__links${open ? " is-open" : ""}`}>
        {links.map(([href, label]) => {
          const active = href === "#/" ? route === "/" : href.startsWith(`#${route}`) && route !== "/";
          return (
            <a key={href} href={href} className={active ? "is-active" : ""}>{label}</a>
          );
        })}
        <div className="rg-nav__ctas">
          <a className="rg-pill" href="#/tablero">Ver tablero</a>
          <a className="rg-pill rg-pill--blue" href="#/#unete">Unir mi escuela</a>
        </div>
      </nav>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="rg-footer">
      <div className="rg-footer__inner">
        <div>
          <Logo big />
          <p className="rg-footer__note">
            Respira GDL orienta, recuerda y alerta. No es una herramienta de diagnóstico. Solo usa datos agregados y anónimos.
          </p>
        </div>
        <div>
          <h4>Proyecto</h4>
          <a href="#/#como">Cómo funciona</a>
          <a href="#/#escuelas">Escuelas piloto</a>
          <a href="https://github.com/ceilingofe/respiragdl">Código en GitHub</a>
        </div>
        <div>
          <h4>Datos del catálogo</h4>
          <span>39 · Calidad del aire</span>
          <span>11 · Anuario de morbilidad</span>
          <span>28 · Estadísticas educativas</span>
          <span>12 · Mortalidad</span>
        </div>
        <div>
          <h4>Hackathon</h4>
          <span>Jalisco Internacional 2026</span>
          <span>Reto 02 · Salud y Bienestar</span>
          <span>Guadalajara, Jalisco</span>
        </div>
      </div>
      <div className="rg-footer__bar">
        <span>© 2026 Equipo Respira GDL · Sergio, Juan, Carlos y Damaris</span>
        <span>Datos de la demo simulados</span>
      </div>
    </footer>
  );
}

// Aparece al hacer scroll
export function useReveal(dep) {
  useEffect(() => {
    const els = document.querySelectorAll(".rg-reveal");
    if (!("IntersectionObserver" in window)) {
      els.forEach((e) => e.classList.add("is-visible"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && (e.target.classList.add("is-visible"), io.unobserve(e.target))),
      { threshold: 0.12 }
    );
    els.forEach((e) => io.observe(e));
    return () => io.disconnect();
  }, [dep]);
}
