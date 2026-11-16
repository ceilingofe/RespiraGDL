import { Suspense, useEffect, useState } from "react";
import { Navbar, Footer, useReveal } from "./components/Layout.jsx";
import ErrorBoundary from "./components/ErrorBoundary.jsx";
import { pageFor } from "./routes.js";
import Alumno from "./pages/Alumno.jsx";
import Entrar from "./pages/Entrar.jsx";
import { ROLES, rolDeRuta, useSesion } from "./data/sesion.js";

// Páginas del acceso por rol que no están en routes.js. El resto sale de routes.js (pageFor).
const PAGINAS_ACCESO = { "/alumno": Alumno, "/entrar": Entrar };

// Rutas con hash para que funcione en GitHub Pages sin servidor: #/, #/aula, #/tablero, #/maestro, #/#seccion.
// Para agregar una página, regístrala en routes.js.
function parse() {
  const raw = window.location.hash.replace(/^#/, "") || "/";
  const [path, anchor] = raw.split("#");
  return { path: path || "/", anchor };
}

const Vacio = () => <main className="rg-app" />;

export default function App() {
  const [{ path, anchor }, setLoc] = useState(parse);
  const sesion = useSesion();

  // Sin sesión -> #/entrar. Con sesión de otro rol -> a su propia pantalla.
  const rol = rolDeRuta(path); // null si la página es pública
  const destino = rol && rol !== sesion?.rol
    ? (sesion ? ROLES[sesion.rol].ruta : "/entrar")
    : null;
  useEffect(() => {
    if (destino) window.location.replace(`#${destino}`);
  }, [destino]);

  useEffect(() => {
    const on = () => setLoc(parse());
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);
  useEffect(() => {
    if (anchor) document.getElementById(anchor)?.scrollIntoView({ behavior: "smooth" });
    else window.scrollTo(0, 0);
  }, [path, anchor]);
  useReveal(path);

  // Mientras redirige no se pinta la pantalla protegida ni un instante.
  const Page = destino ? Vacio : PAGINAS_ACCESO[path] ?? pageFor(path);
  return (
    <>
      <Navbar route={path} sesion={sesion} />
      <ErrorBoundary resetKey={path}>
        <Suspense fallback={<main className="rg-app" role="status">Abriendo la vista…</main>}><Page /></Suspense>
      </ErrorBoundary>
      <Footer />
    </>
  );
}
