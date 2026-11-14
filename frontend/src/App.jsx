import { useEffect, useState } from "react";
import { Navbar, Footer, useReveal } from "./components/Layout.jsx";
import ErrorBoundary from "./components/ErrorBoundary.jsx";
import { pageFor } from "./routes.js";

// Rutas con hash para que funcione en GitHub Pages sin servidor: #/, #/aula, #/tablero, #/maestro, #/#seccion.
// Para agregar una página, regístrala en routes.js.
function parse() {
  const raw = window.location.hash.replace(/^#/, "") || "/";
  const [path, anchor] = raw.split("#");
  return { path: path || "/", anchor };
}

export default function App() {
  const [{ path, anchor }, setLoc] = useState(parse);
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

  const Page = pageFor(path);
  return (
    <>
      <Navbar route={path} />
      <ErrorBoundary resetKey={path}>
        <Page />
      </ErrorBoundary>
      <Footer />
    </>
  );
}
