# Reglas del repo Respira GDL

- **Diseño:** cualquier cambio de UI (frontend, bot con imágenes, infografía, pitch, capturas) sigue `docs/diseno/README.md` y usa los tokens de `frontend/src/styles/tokens.css`. No inventar colores, radios ni fuentes nuevas.
- **Commits y PRs:** sin líneas `Co-Authored-By`, `Claude-Session` ni "Generated with Claude Code". Autor: la persona del equipo. Mensajes cortos en español con prefijo de área (`frontend: agrega tarjeta de salón`).
- **Ramas:** `feat/<área>-<tema>`, PR a `main` con la plantilla; no push directo a `main`.
- **Datos:** nunca subir `.env`, `config.h` ni datos de alumnos. No presentar el sistema como herramienta de diagnóstico.
