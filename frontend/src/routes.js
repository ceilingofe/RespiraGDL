// Registro único de rutas. Cada página nueva se agrega aquí (y nada más),
// así los equipos de Aula Limpia y Plan de asma no chocan en App.jsx.
import { lazy } from "react";
import Landing from "./pages/Landing.jsx";
import NoEncontrada from "./pages/NoEncontrada.jsx";
const Tablero = lazy(() => import("./pages/Tablero.jsx"));
const Maestro = lazy(() => import("./pages/Maestro.jsx"));
const AulaLimpia = lazy(() => import("./pages/AulaLimpia.jsx"));
const Evidencia = lazy(() => import("./pages/Evidencia.jsx"));
const Simulador = lazy(() => import("./pages/Simulador.jsx"));

// nav: texto en el menú (null = no aparece)
export const ROUTES = [
  { path: "/", page: Landing, nav: "Inicio" },
  { path: "/aula", page: AulaLimpia, nav: "Aula Limpia" },
  { path: "/tablero", page: Tablero, nav: "Tablero" },
  { path: "/maestro", page: Maestro, nav: "Plan de asma" },
  { path: "/evidencia", page: Evidencia, nav: "Evidencia" },
  { path: "/simulador", page: Simulador, nav: "Escuela 3D" },
];

export function pageFor(path) {
  return ROUTES.find((r) => r.path === path)?.page ?? NoEncontrada;
}
