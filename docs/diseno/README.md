# Guía de diseño de Respira GDL

Esta es la **máxima de diseño** del proyecto. Todo lo que se vea (tablero, vista del maestro, landing, infografía, pitch y capturas del manual) sigue esta guía. Si un PR toca UI y no la sigue, no se aprueba.

Referencia visual: [`referencia.png`](referencia.png) (página completa) y [`referencia-hero-animado.png`](referencia-hero-animado.png) (cuadros del hero animado). Los valores de abajo se midieron de esa referencia.

Los tokens ya están listos en [`frontend/src/styles/tokens.css`](../../frontend/src/styles/tokens.css). **No escriban colores, radios ni sombras a mano**: usen las variables.

---

## 1. La idea en una frase

Naturaleza luminosa y tranquila: mucho blanco, fotos grandes con esquinas muy redondeadas, tarjetas de color pastel casi blanco, títulos verde-petróleo oscuros y botones en forma de píldora. Nada se siente "de gobierno" ni técnico; se siente como un lugar seguro para una maestra o una mamá.

## 2. Color

### Marca

| Token | Hex | Uso |
| --- | --- | --- |
| `--rg-ink` | `#0B4143` | Títulos de sección, barra inferior del footer, texto fuerte |
| `--rg-forest` | `#1C4623` | Título del hero en tema verde |
| `--rg-leaf` | `#1C702B` | Logo, enlace activo del menú |
| `--rg-teal` | `#0B585B` | Botón principal (Donar / Enviar aviso) |
| `--rg-text` | `#1E1E1E` | Texto de párrafo |
| `--rg-muted` | `#59735F` | Menú, texto secundario |
| `--rg-sage` | `#CEDDD1` | Fondo del footer |

### Superficies pastel (fondos de tarjetas)

Siempre muy claras. Una tarjeta nunca tiene fondo blanco puro sobre blanco: usa una de estas.

| Token | Hex | Tono |
| --- | --- | --- |
| `--rg-mint` | `#EEFFEC` | Verde (tarjeta activa, "Green Living") |
| `--rg-mint-2` | `#F4FFF2` | Verde muy claro (tarjeta "Achieve More") |
| `--rg-aqua` | `#E7FFF7` | Agua (botones de monto, iniciativa 2) |
| `--rg-sky` | `#F3FBFF` | Azul cielo (tarjeta "Coastal Care") |
| `--rg-ice` | `#EBFDFF` | Celeste (tarjeta "One Vision") |
| `--rg-lilac` | `#EFF3FF` | Azul lavanda (selector de moneda, iniciativas 1 y 3) |
| `--rg-mist` | `#F1F6F7` | Gris verdoso (contenedor de "Spotlight") |

### Píldoras de botón

| Token | Hex | Uso |
| --- | --- | --- |
| `--rg-pill-olive` | `#D0DC9F` | CTA del hero en tema verde ("Our Approach") |
| `--rg-pill-green` | `#DEFED4` | Botón secundario verde ("Donate" del menú) |
| `--rg-pill-blue` | `#D4EFFF` | Botón secundario azul ("Join Us", "Learn More") |

### Semáforo de calidad del aire (solo para datos)

Los colores de marca **nunca** se usan para decir si el aire es bueno o malo. Para eso hay tokens aparte, con fondo pastel y texto oscuro para que se lean bien:

| Nivel | Fondo | Texto/punto |
| --- | --- | --- |
| Bueno | `--rg-aq-good-bg` `#E6F8E8` | `--rg-aq-good` `#1E7B34` |
| Aceptable | `--rg-aq-ok-bg` `#FFF7DA` | `--rg-aq-ok` `#8A6400` |
| Mala | `--rg-aq-bad-bg` `#FFE9DE` | `--rg-aq-bad` `#B23C0A` |
| Muy mala | `--rg-aq-vbad-bg` `#FDE7EC` | `--rg-aq-vbad` `#A3123A` |
| Extremadamente mala | `--rg-aq-ext-bg` `#F1E8FB` | `--rg-aq-ext` `#5B2A8C` |

Siempre acompañen el color con la palabra ("Mala") y el número; nunca color solo.

## 3. Tipografía

- **Fuente:** [Poppins](https://fonts.google.com/specimen/Poppins) (400, 500, 600, 700). Una sola familia.
- **Títulos:** peso 600, interlineado 1.1, `letter-spacing: -0.02em`, color `--rg-ink`, centrados en secciones.
- **Hero:** peso 600 a 700, de 56 a 80 px en escritorio, dos líneas cortas ("Aire limpio, / niños tranquilos").
- **Párrafos:** 14 a 16 px, peso 400, color `--rg-text`, máximo ~60 caracteres por línea, centrados bajo el título de sección.
- **Botones y menú:** 12 a 14 px, peso 500 a 600.

| Token | Valor |
| --- | --- |
| `--rg-fs-hero` | `clamp(2.75rem, 6vw, 5rem)` |
| `--rg-fs-h2` | `clamp(1.75rem, 3.2vw, 2.5rem)` |
| `--rg-fs-h3` | `1.25rem` |
| `--rg-fs-body` | `1rem` |
| `--rg-fs-small` | `0.8125rem` |

## 4. Forma, espacio y sombra

- **Radios grandes:** fotos y tarjetas `--rg-r-xl` (32 px), tarjetas pequeñas `--rg-r-lg` (24 px), botones `--rg-r-pill` (999 px).
- **Formas asimétricas:** las imágenes destacadas pueden tener una esquina muy grande y otra pequeña (como el mar y el bosque de "Leading the Way"). Usen `--rg-r-blob`.
- **Aire generoso:** secciones separadas por `--rg-space-section` (96 a 128 px). Contenedor máximo 1200 px.
- **Sombra:** casi invisible (`--rg-shadow-soft`). La profundidad viene del color pastel, no de sombras duras. Sin bordes visibles.

## 5. Componentes

| Componente | Cómo se ve | En Respira GDL |
| --- | --- | --- |
| **Navbar** | Logo verde a la izquierda, menú en gris en el centro, dos píldoras a la derecha (verde y azul). Fondo transparente sobre el hero. | Inicio · Cómo funciona · Escuelas · Datos · Contacto; píldoras "Ver tablero" y "Unir mi escuela" |
| **Hero** | Título enorme de dos líneas a la izquierda, párrafo corto, una píldora; imagen grande a la derecha que se funde con el blanco. Debajo, 3 tarjetas pastel con foto redonda y título. | 3 temas: Aula Limpia (verde), Plan de asma (agua), Pronóstico (azul) |
| **Tarjeta de pilar** | Fondo pastel, foto de 80 px con radio 20 px, título 600, subtítulo pequeño. La activa tiene color pleno; las otras al 60 % de opacidad. | Los 3 pilares del proyecto |
| **Rejilla de fotos** | 3 columnas, foto cuadrada con radio 32 px y etiqueta centrada abajo. | Problemas: PM2.5, asma infantil, salones sin ventilar, días fuera de norma |
| **Bloque foto + tarjeta** | Foto grande y una tarjeta pastel que se le monta encima en una esquina, alternando izquierda y derecha. | "Medimos dentro y fuera" y "Un plan para cada salón" |
| **Tarjeta de iniciativa** | Tarjeta pastel con foto arriba, título, subtítulo y botón píldora blanco. | Escuelas piloto (Miravalle, Las Pintas, Santa Fe) |
| **Historias** | Contenedor gris claro con 4 fotos oscuras, título blanco sobre la foto, fecha y botón circular con flecha. | Avisos del día, pronóstico, historias de la demo |
| **Selector de montos** | Fila de píldoras pastel y una principal oscura centrada. | Selector de salón o de día en el tablero |
| **Footer** | Fondo salvia `--rg-sage`, logo grande, 3 columnas de enlaces y contacto; barra inferior `--rg-ink` con iconos blancos. | Créditos, datasets usados, aviso "no es herramienta de diagnóstico" |

### Tablero y vista del maestro

El tablero no es una landing, pero usa el mismo lenguaje:

- Fondo blanco, cada bloque es una tarjeta pastel con radio 24 a 32 px.
- Números grandes en `--rg-ink` (peso 600), etiqueta pequeña en `--rg-muted`.
- Gráficas: línea "fuera" en `--rg-aq-bad`, línea "dentro" en `--rg-teal`, línea de norma punteada en `--rg-muted`. Sin cuadrícula pesada.
- La vista del maestro es de celular: una tarjeta grande con el semáforo arriba, botones píldora de ancho completo abajo.

## 6. Movimiento

Tomado del video de referencia:

- **Hero rotativo:** cada 5 s cambia de tema. La imagen hace *crossfade* (600 ms), el título entra deslizándose desde la izquierda con fade, y el color del título y de la píldora cambia al del tema. La tarjeta del tema activo pasa a opacidad 100 % y las otras quedan en 60 %. Al hacer clic en una tarjeta se va a ese tema.
- **Entrada al hacer scroll:** cada sección sube 24 px con fade (400 ms, `--rg-ease`).
- **Hover:** tarjetas suben 4 px; fotos hacen zoom de 1.03 dentro de su marco.
- Respeten `prefers-reduced-motion`: sin rotación automática y sin desplazamientos.

| Token | Valor |
| --- | --- |
| `--rg-ease` | `cubic-bezier(.22, .61, .36, 1)` |
| `--rg-dur-fast` | `200ms` |
| `--rg-dur` | `400ms` |
| `--rg-dur-slow` | `600ms` |

## 7. Fotos e ilustración

- Fotos naturales, luminosas y con cielo: árboles, agua, niños en el patio, salones con luz. Nada de humo dramático en primer plano; el humo solo aparece en la sección del problema.
- Para niños: fotos de banco con licencia libre (Unsplash/Pexels) o ilustración; nunca fotos reales de alumnos de las escuelas piloto.
- Iconos de línea redondeada (Lucide o Phosphor), 1.5 px de grosor.

## 8. Accesibilidad

- Contraste AA: texto oscuro sobre pastel siempre. Nunca texto blanco sobre un pastel.
- Tamaño táctil mínimo de 44 px en botones de la vista del maestro.
- El semáforo siempre lleva palabra y número, no solo color.

## 9. Checklist antes de abrir un PR con UI

- [ ] Uso tokens de `tokens.css`, sin hex sueltos.
- [ ] Tarjetas con fondo pastel, radio grande y sin borde.
- [ ] Títulos en Poppins 600 color `--rg-ink`, botones en píldora.
- [ ] Colores del semáforo solo para calidad del aire, con palabra y número.
- [ ] Se ve bien en celular (360 px) y respeta `prefers-reduced-motion`.
- [ ] Adjunté captura en el PR.
