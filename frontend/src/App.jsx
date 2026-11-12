import { useEffect, useState } from "react";
import { Navbar, Footer, useReveal } from "./components/Layout.jsx";
import Landing from "./pages/Landing.jsx";
import Tablero from "./pages/Tablero.jsx";
import Maestro from "./pages/Maestro.jsx";

// Rutas con hash para que funcione en GitHub Pages sin servidor: #/, #/tablero, #/maestro, #/#seccion
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

  const Page = path === "/tablero" ? Tablero : path === "/maestro" ? Maestro : Landing;
  return (
    <>
      <Navbar route={path} />
      <Page />
      <Footer />
    </>
  );
}
