// Contenido del plan de asma escolar.
// BORRADOR: lo revisa Damaris y lo debe validar un médico antes de usarse con alumnos (issues #13 y #14).
// La app orienta y recuerda; no diagnostica ni sustituye el plan de acción que firma el médico de cada alumno.

// Qué hace cada quien según el semáforo del día. La clave es el id de nivel de demo.js.
export const PROTOCOLO = {
  good: {
    titulo: "Día normal",
    escuela: ["Recreo y educación física al aire libre.", "Filtro encendido en horario de clases."],
    maestro: ["Recreo normal.", "Revisar que el filtro esté encendido al llegar."],
    familias: [],
  },
  ok: {
    titulo: "Día normal con atención",
    escuela: ["Recreo al aire libre.", "Filtro encendido en horario de clases."],
    maestro: ["Recreo normal; observar a los alumnos con asma.", "Filtro encendido y puerta cerrada."],
    familias: ["Recordar el inhalador de rescate en la mochila."],
  },
  bad: {
    titulo: "Aire malo: proteger a quienes tienen asma",
    escuela: [
      "Recreo adentro para alumnos con asma.",
      "Educación física de baja intensidad o adentro.",
      "Enviar aviso a familias a las 7:00.",
    ],
    maestro: [
      "Recreo adentro para alumnos con asma.",
      "Filtro encendido y puerta cerrada.",
      "Preguntar quién trae su inhalador de rescate.",
    ],
    familias: ["Que lleve su inhalador de rescate.", "Si usa medicamento de control, no lo suspenda."],
  },
  vbad: {
    titulo: "Aire muy malo: recreo adentro para todos",
    escuela: [
      "Recreo y educación física adentro para todo el grupo.",
      "Ventanas cerradas y filtro al máximo.",
      "Enviar aviso a familias un día antes y a las 7:00.",
    ],
    maestro: [
      "Recreo adentro para todos.",
      "Ventanas cerradas y filtro al máximo.",
      "Preguntar quién trae su inhalador de rescate.",
      "Tener a la mano la guía de crisis.",
    ],
    familias: [
      "Que lleve su inhalador de rescate.",
      "Si usa medicamento de control, no lo suspenda.",
      "Evitar ejercicio al aire libre por la tarde.",
    ],
  },
  ext: {
    titulo: "Contingencia: seguir a Protección Civil",
    escuela: ["Seguir indicaciones de Protección Civil y de la SEJ.", "Todas las actividades adentro."],
    maestro: ["Todas las actividades adentro.", "Ventanas cerradas y filtro al máximo.", "Tener a la mano la guía de crisis."],
    familias: ["Seguir avisos oficiales.", "Que lleve su inhalador de rescate."],
  },
};

// Guía de crisis paso a paso. Basada en planes de acción de asma publicados; validar con un médico.
export const PASOS_CRISIS = [
  { texto: "Mantén la calma y quédate con el alumno. Siéntalo derecho, un poco inclinado hacia adelante, lejos de humo o polvo." },
  { texto: "Ayúdalo a usar su inhalador de rescate como indica su plan firmado por su médico." },
  { texto: "Observa si mejora en el tiempo que marca su plan. Si no mejora, repite como indica el plan y avisa a la dirección.", espera: true },
  { texto: "Si le cuesta hablar, tiene los labios o uñas morados, o no mejora: llama al 911.", urgente: true },
  { texto: "Avisa a la familia y registra la hora. El registro es anónimo: solo grupo y hora." },
];

export const SENALES_ALARMA = [
  "Le cuesta hablar o caminar",
  "Labios o uñas morados o grises",
  "Se le hunden las costillas al respirar",
  "El inhalador de rescate no le ayuda",
];

// Lo que el plan guarda y lo que no (ética de datos).
export const DATOS_SI = [
  "Cuántos alumnos con asma hay por grupo (solo el número).",
  "Hora y grupo de cada crisis atendida, y si se avisó a la familia.",
  "Respuestas anónimas de familias sobre síntomas del día.",
];
export const DATOS_NO = [
  "Nombres, CURP, fotos o diagnósticos de alumnos.",
  "Medicamentos o dosis de cada alumno: eso vive en su plan firmado, en papel.",
  "Teléfonos de familias dentro del tablero.",
];

export const ROLES = [
  {
    quien: "Dirección",
    hace: ["Ve el tablero y el pronóstico.", "Envía el aviso a familias.", "Revisa salones con protección baja."],
  },
  {
    quien: "Maestra o maestro",
    hace: ["Ve el semáforo y qué hacer hoy.", "Abre la guía de crisis si un alumno la necesita.", "Registra la crisis sin nombres."],
  },
  {
    quien: "Familia",
    hace: ["Recibe el aviso a las 7:00.", "Manda el inhalador y el plan firmado por su médico.", "Responde 1 si su hijo tuvo síntomas (anónimo)."],
  },
];
