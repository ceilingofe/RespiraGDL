// Registro único de rutas. Cada página nueva se agrega aquí (y nada más),
// así los equipos de Aula Limpia y Plan de asma no chocan en App.jsx.
import Landing from "./pages/Landing.jsx";
import Tablero from "./pages/Tablero.jsx";
import Maestro from "./pages/Maestro.jsx";
import AulaLimpia from "./pages/AulaLimpia.jsx";
import PlanAsma from "./pages/PlanAsma.jsx";
import Red from "./pages/Red.jsx";
import NoEncontrada from "./pages/NoEncontrada.jsx";

// nav: texto en el menú (null = no aparece)
export const ROUTES = [
  { path: "/", page: Landing, nav: "Inicio" },
  { path: "/aula", page: AulaLimpia, nav: "Aula Limpia" },
  { path: "/tablero", page: Tablero, nav: "Tablero" },
  { path: "/maestro", page: Maestro, nav: "Plan de asma" },
  { path: "/plan", page: PlanAsma, nav: null },
  { path: "/red", page: Red, nav: "Red de escuelas" },
];

export function pageFor(path) {
  return ROUTES.find((r) => r.path === path)?.page ?? NoEncontrada;
}
