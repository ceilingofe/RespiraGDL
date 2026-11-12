// Ilustraciones SVG en el lenguaje visual de la guía (cielo luminoso, verdes, formas suaves).
// Sustituyen a fotos mientras no tengamos fotos con licencia.

export function ArtAula({ className }) {
  return (
    <svg className={className} viewBox="0 0 640 520" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Salón con filtro casero y dos sensores">
      <defs>
        <linearGradient id="aSky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#d9f1ff" />
          <stop offset="1" stopColor="#f6fcff" />
        </linearGradient>
        <linearGradient id="aWall" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#f4fff2" />
          <stop offset="1" stopColor="#e3f4e2" />
        </linearGradient>
        <linearGradient id="aHill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#7cc47f" />
          <stop offset="1" stopColor="#2f7d3c" />
        </linearGradient>
        <radialGradient id="aAir" cx=".5" cy=".5" r=".5">
          <stop offset="0" stopColor="#bdf0e6" stopOpacity=".9" />
          <stop offset="1" stopColor="#bdf0e6" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect width="640" height="520" fill="url(#aWall)" />
      {/* ventana */}
      <rect x="360" y="60" width="230" height="190" rx="22" fill="url(#aSky)" stroke="#cfe3d3" strokeWidth="8" />
      <path d="M368 220 Q420 170 480 200 T584 180 V244 H368Z" fill="url(#aHill)" opacity=".85" />
      <circle cx="420" cy="110" r="22" fill="#fff6c9" />
      <g fill="#c9a98a" opacity=".55">
        <circle cx="520" cy="110" r="26" /><circle cx="548" cy="122" r="20" /><circle cx="498" cy="126" r="16" />
      </g>
      <line x1="475" y1="64" x2="475" y2="246" stroke="#cfe3d3" strokeWidth="6" />
      {/* sensor fuera */}
      <g transform="translate(540 268)">
        <rect width="62" height="44" rx="12" fill="#fff" stroke="#ffd7c2" strokeWidth="3" />
        <text x="31" y="20" textAnchor="middle" fontSize="11" fontWeight="600" fill="#b23c0a">FUERA</text>
        <text x="31" y="36" textAnchor="middle" fontSize="13" fontWeight="700" fill="#b23c0a">62</text>
      </g>
      {/* pizarrón con semáforo */}
      <rect x="44" y="70" width="270" height="150" rx="20" fill="#0b4143" />
      <text x="70" y="112" fontSize="18" fontWeight="600" fill="#e7fff7">Aire de hoy</text>
      <rect x="70" y="128" width="140" height="40" rx="20" fill="#ffe9de" />
      <circle cx="94" cy="148" r="9" fill="#b23c0a" />
      <text x="112" y="154" fontSize="16" fontWeight="600" fill="#b23c0a">Mala</text>
      <text x="70" y="198" fontSize="12" fill="#bfe3dc">Recreo adentro para niños con asma</text>
      {/* aire limpio */}
      <ellipse cx="190" cy="360" rx="190" ry="110" fill="url(#aAir)" />
      {/* filtro casero */}
      <g transform="translate(110 290)">
        <rect x="0" y="40" width="150" height="150" rx="18" fill="#f3fbff" stroke="#0b585b" strokeWidth="5" />
        <g stroke="#9cc3ec" strokeWidth="3">
          {[0, 1, 2, 3, 4, 5].map((i) => (<line key={i} x1={14 + i * 24} y1="54" x2={14 + i * 24} y2="176" />))}
        </g>
        <rect x="-6" y="18" width="162" height="34" rx="14" fill="#0b585b" />
        <circle cx="75" cy="35" r="12" fill="#e7fff7" />
        <text x="75" y="214" textAnchor="middle" fontSize="13" fontWeight="600" fill="#0b4143">Filtro casero</text>
      </g>
      {/* sensor dentro */}
      <g transform="translate(300 330)">
        <rect width="70" height="50" rx="14" fill="#fff" stroke="#bfe8c2" strokeWidth="3" />
        <text x="35" y="22" textAnchor="middle" fontSize="11" fontWeight="600" fill="#1e7b34">DENTRO</text>
        <text x="35" y="40" textAnchor="middle" fontSize="14" fontWeight="700" fill="#1e7b34">21</text>
      </g>
      {/* pupitres */}
      <g fill="#c4dccb">
        <rect x="400" y="380" width="96" height="16" rx="8" /><rect x="510" y="380" width="96" height="16" rx="8" />
        <rect x="430" y="396" width="8" height="60" rx="4" /><rect x="460" y="396" width="8" height="60" rx="4" />
        <rect x="540" y="396" width="8" height="60" rx="4" /><rect x="570" y="396" width="8" height="60" rx="4" />
      </g>
      <g fill="#7fd6d3"><circle cx="448" cy="352" r="18" /><circle cx="558" cy="352" r="18" /></g>
      <rect x="0" y="470" width="640" height="50" fill="#d6e9d8" />
      {/* tarjeta de protección */}
      <g transform="translate(380 430)">
        <rect width="220" height="64" rx="22" fill="#fff" />
        <text x="22" y="28" fontSize="12" fill="#59735f">Protección del salón</text>
        <text x="22" y="52" fontSize="22" fontWeight="700" fill="#0b4143">66 %</text>
        <rect x="104" y="40" width="96" height="10" rx="5" fill="#e6f8e8" />
        <rect x="104" y="40" width="63" height="10" rx="5" fill="#1e7b34" />
      </g>
    </svg>
  );
}

export function ArtAsma({ className }) {
  return (
    <svg className={className} viewBox="0 0 640 520" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Teléfono del maestro con plan de asma">
      <defs>
        <linearGradient id="bBg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#ebfdff" />
          <stop offset="1" stopColor="#c8f1ec" />
        </linearGradient>
        <linearGradient id="bLeaf" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#8fd9b5" />
          <stop offset="1" stopColor="#2e8f7a" />
        </linearGradient>
      </defs>
      <rect width="640" height="520" fill="url(#bBg)" />
      <g fill="url(#bLeaf)" opacity=".7">
        <path d="M40 520 C60 380 150 330 220 300 C190 380 140 460 120 520Z" />
        <path d="M600 520 C590 400 520 330 450 300 C470 390 520 460 540 520Z" />
        <path d="M560 120 C520 60 450 50 410 70 C450 100 500 130 560 120Z" />
      </g>
      <circle cx="140" cy="130" r="70" fill="#fff" opacity=".6" />
      {/* teléfono */}
      <g transform="translate(220 40)">
        <rect width="210" height="430" rx="36" fill="#0b4143" />
        <rect x="10" y="12" width="190" height="406" rx="28" fill="#fff" />
        <text x="28" y="54" fontSize="12" fill="#59735f">Grupo 3°A · hoy</text>
        <text x="28" y="80" fontSize="18" fontWeight="600" fill="#0b4143">Plan de asma</text>
        <rect x="28" y="96" width="154" height="70" rx="20" fill="#ffe9de" />
        <circle cx="52" cy="131" r="10" fill="#b23c0a" />
        <text x="70" y="126" fontSize="14" fontWeight="600" fill="#b23c0a">Aire malo</text>
        <text x="70" y="146" fontSize="11" fill="#7a3a17">PM2.5 · 62</text>
        <rect x="28" y="180" width="154" height="62" rx="20" fill="#eeffec" />
        <text x="44" y="206" fontSize="11" fill="#59735f">Alumnos con asma</text>
        <text x="44" y="230" fontSize="20" fontWeight="700" fill="#0b4143">4</text>
        <text x="66" y="230" fontSize="10" fill="#59735f">sin nombres</text>
        <rect x="28" y="256" width="154" height="62" rx="20" fill="#eff3ff" />
        <text x="44" y="282" fontSize="11" fill="#59735f">Recreo</text>
        <text x="44" y="304" fontSize="14" fontWeight="600" fill="#0b4143">Adentro</text>
        <rect x="28" y="340" width="154" height="44" rx="22" fill="#0b585b" />
        <text x="105" y="367" textAnchor="middle" fontSize="13" fontWeight="600" fill="#fff">Guía de crisis</text>
      </g>
      {/* inhalador */}
      <g transform="translate(470 250) rotate(18)">
        <rect width="54" height="110" rx="18" fill="#7fd6d3" />
        <rect x="-8" y="96" width="70" height="34" rx="14" fill="#0b585b" />
        <circle cx="27" cy="34" r="10" fill="#fff" opacity=".8" />
      </g>
    </svg>
  );
}

export function ArtPronostico({ className }) {
  return (
    <svg className={className} viewBox="0 0 640 520" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Ciudad con pronóstico de calidad del aire">
      <defs>
        <linearGradient id="cSky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#bfe2ff" />
          <stop offset=".7" stopColor="#eef7ff" />
          <stop offset="1" stopColor="#fff4e6" />
        </linearGradient>
        <linearGradient id="cHaze" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#f6d6bd" stopOpacity="0" />
          <stop offset="1" stopColor="#f6d6bd" stopOpacity=".8" />
        </linearGradient>
        <linearGradient id="cHill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#6bb37a" />
          <stop offset="1" stopColor="#2c6b3a" />
        </linearGradient>
      </defs>
      <rect width="640" height="520" fill="url(#cSky)" />
      <circle cx="520" cy="90" r="40" fill="#fff6c9" />
      <g fill="#fff" opacity=".9">
        <ellipse cx="160" cy="90" rx="70" ry="22" /><ellipse cx="200" cy="74" rx="44" ry="24" />
        <ellipse cx="420" cy="140" rx="60" ry="18" />
      </g>
      {/* ciudad */}
      <g fill="#9fb8cf">
        <rect x="60" y="300" width="50" height="140" rx="6" /><rect x="120" y="260" width="40" height="180" rx="6" />
        <rect x="170" y="320" width="60" height="120" rx="6" /><rect x="240" y="230" width="44" height="210" rx="6" />
        <rect x="294" y="290" width="70" height="150" rx="6" /><rect x="374" y="250" width="40" height="190" rx="6" />
        <rect x="424" y="310" width="64" height="130" rx="6" /><rect x="498" y="270" width="46" height="170" rx="6" />
      </g>
      <rect x="0" y="230" width="640" height="220" fill="url(#cHaze)" />
      <path d="M0 440 Q160 400 320 430 T640 420 V520 H0Z" fill="url(#cHill)" />
      {/* tarjeta pronóstico */}
      <g transform="translate(70 120)">
        <rect width="300" height="150" rx="28" fill="#fff" opacity=".96" />
        <text x="26" y="40" fontSize="13" fill="#59735f">Pronóstico 24 h · Miravalle</text>
        <polyline points="26,110 70,96 114,84 158,70 202,62 246,74 274,90" fill="none" stroke="#b23c0a" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <line x1="26" y1="92" x2="274" y2="92" stroke="#59735f" strokeDasharray="5 6" strokeWidth="1.5" />
        <text x="200" y="130" fontSize="12" fill="#59735f">norma</text>
        <rect x="26" y="118" width="110" height="22" rx="11" fill="#ffe9de" />
        <text x="81" y="133" textAnchor="middle" fontSize="11" fontWeight="600" fill="#b23c0a">Mañana: Mala</text>
      </g>
    </svg>
  );
}

// Miniaturas: escenas pequeñas para rejillas, escuelas e historias
const sky = (id, a, b) => (
  <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stopColor={a} />
    <stop offset="1" stopColor={b} />
  </linearGradient>
);

const SCENES = {
  humo: (
    <>
      <defs>{sky("t-humo", "#f7c8a4", "#fdeee2")}{sky("t-humo-h", "#e9b896", "#f5dccb")}</defs>
      <rect width="300" height="200" fill="url(#t-humo)" />
      <circle cx="220" cy="62" r="26" fill="#ffe2b8" />
      <g fill="#8c7468" opacity=".75">
        <rect x="20" y="96" width="26" height="80" rx="4" /><rect x="52" y="70" width="22" height="106" rx="4" />
        <rect x="80" y="110" width="34" height="66" rx="4" /><rect x="120" y="60" width="24" height="116" rx="4" />
        <rect x="150" y="92" width="38" height="84" rx="4" /><rect x="194" y="76" width="22" height="100" rx="4" />
        <rect x="222" y="104" width="34" height="72" rx="4" /><rect x="262" y="84" width="26" height="92" rx="4" />
      </g>
      <rect y="60" width="300" height="120" fill="url(#t-humo-h)" opacity=".55" />
      <path d="M0 176 Q150 160 300 176 V200 H0Z" fill="#6f8f6a" />
    </>
  ),
  asma: (
    <>
      <defs>{sky("t-asma", "#c8f1ec", "#ebfdff")}</defs>
      <rect width="300" height="200" fill="url(#t-asma)" />
      <path d="M0 200 C20 130 70 110 110 100 C90 150 60 180 50 200Z" fill="#5fbf9f" opacity=".7" />
      <path d="M300 200 C285 140 240 110 200 104 C215 150 245 180 255 200Z" fill="#2e8f7a" opacity=".6" />
      <g transform="translate(120 40) rotate(-12)">
        <rect width="52" height="104" rx="18" fill="#7fd6d3" />
        <rect x="-10" y="92" width="72" height="34" rx="14" fill="#0b585b" />
        <circle cx="26" cy="30" r="9" fill="#fff" opacity=".85" />
      </g>
      <g fill="#fff" opacity=".8"><circle cx="210" cy="52" r="7" /><circle cx="226" cy="40" r="4" /><circle cx="236" cy="58" r="5" /></g>
    </>
  ),
  salon: (
    <>
      <defs>{sky("t-salon", "#f3fbff", "#e2f1fb")}{sky("t-salon-s", "#bfe2ff", "#eef7ff")}</defs>
      <rect width="300" height="200" fill="url(#t-salon)" />
      <rect x="60" y="28" width="180" height="120" rx="16" fill="url(#t-salon-s)" stroke="#cfe0ec" strokeWidth="8" />
      <path d="M64 120 Q120 90 170 108 T236 100 V144 H64Z" fill="#7cc47f" />
      <line x1="150" y1="30" x2="150" y2="146" stroke="#cfe0ec" strokeWidth="6" />
      <circle cx="100" cy="62" r="13" fill="#fff6c9" />
      <rect x="30" y="160" width="240" height="12" rx="6" fill="#c4d7e4" />
      <rect x="110" y="110" width="80" height="62" rx="10" fill="#f3fbff" stroke="#0b585b" strokeWidth="4" />
      <rect x="104" y="100" width="92" height="18" rx="8" fill="#0b585b" />
    </>
  ),
  norma: (
    <>
      <defs>{sky("t-norma", "#fde7ec", "#fff6ee")}</defs>
      <rect width="300" height="200" fill="url(#t-norma)" />
      <rect x="30" y="30" width="240" height="140" rx="20" fill="#fff" opacity=".85" />
      <line x1="50" y1="100" x2="250" y2="100" stroke="#59735f" strokeDasharray="6 7" strokeWidth="2" />
      <polyline points="50,140 90,118 130,126 170,74 210,88 250,62" fill="none" stroke="#a3123a" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
      <g fill="#a3123a"><circle cx="170" cy="74" r="6" /><circle cx="250" cy="62" r="6" /></g>
      <text x="56" y="56" fontSize="15" fontWeight="600" fill="#0b4143" fontFamily="Poppins, sans-serif">PM2.5</text>
    </>
  ),
  recreo: (
    <>
      <defs>{sky("t-recreo", "#cfeaff", "#f4fff2")}</defs>
      <rect width="300" height="200" fill="url(#t-recreo)" />
      <circle cx="236" cy="48" r="22" fill="#fff6c9" />
      <path d="M0 140 Q90 100 170 132 T300 120 V200 H0Z" fill="#8fd18b" />
      <path d="M0 168 Q120 140 300 170 V200 H0Z" fill="#3f9a4c" />
      <rect x="64" y="86" width="8" height="54" rx="4" fill="#7a5a3a" />
      <circle cx="68" cy="78" r="26" fill="#2f7d3c" /><circle cx="52" cy="92" r="16" fill="#3f9a4c" /><circle cx="86" cy="90" r="18" fill="#3f9a4c" />
      <g stroke="#0b4143" strokeWidth="4" strokeLinecap="round" fill="none"><path d="M170 150 L190 96 L210 150" /><path d="M186 96 H222 L240 150" /></g>
      <rect x="196" y="122" width="22" height="6" rx="3" fill="#0b585b" />
    </>
  ),
  familia: (
    <>
      <defs>{sky("t-familia", "#e3e7ff", "#f5f7ff")}</defs>
      <rect width="300" height="200" fill="url(#t-familia)" />
      <rect x="104" y="24" width="92" height="164" rx="20" fill="#0b4143" />
      <rect x="110" y="32" width="80" height="148" rx="15" fill="#fff" />
      <rect x="118" y="52" width="60" height="36" rx="10" fill="#eff3ff" />
      <rect x="126" y="96" width="56" height="44" rx="10" fill="#e6f8e8" />
      <circle cx="136" cy="70" r="5" fill="#b23c0a" />
      <rect x="146" y="66" width="24" height="7" rx="3" fill="#b9c3e8" />
      <rect x="134" y="106" width="38" height="6" rx="3" fill="#8fc79a" /><rect x="134" y="118" width="28" height="6" rx="3" fill="#8fc79a" />
      <g fill="#7f86d6" opacity=".7"><circle cx="58" cy="92" r="18" /><path d="M30 160 q28 -56 56 0z" /><circle cx="246" cy="100" r="14" /><path d="M224 160 q22 -46 44 0z" /></g>
    </>
  ),
};

export function Tile({ kind, className }) {
  return (
    <svg className={className} viewBox="0 0 300 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      {SCENES[kind]}
    </svg>
  );
}
