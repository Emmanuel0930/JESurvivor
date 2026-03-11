// ============================================================
// components/courses.js — Lista de cursos disponibles
// Recibe cursos desde getCourses() y genera el HTML.
// ============================================================

// Mapeo de nivel a clase CSS y etiqueta en español
const LEVEL_MAP = {
  Principiante: { cls: "level-beginner",     label: "Principiante" },
  Intermedio:   { cls: "level-intermediate", label: "Intermedio"   },
  Avanzado:     { cls: "level-advanced",     label: "Avanzado"     },
};

/**
 * Renderiza la lista de cursos.
 * @param {Array} courses — Cursos desde getCourses()
 * @returns {string} HTML listo para insertar
 */
export function renderCourses(courses) {
  if (!courses || courses.length === 0) {
    return `
      <div class="error-wrap">
        <span class="error-icon">📭</span>
        <p class="error-msg">No hay cursos disponibles todavía.</p>
      </div>
    `;
  }

  return `
    <div class="courses-grid stagger" role="list">
      ${courses.map(buildCourseCard).join("")}
    </div>
  `;
}

// ── Tarjeta individual de curso ─────────────────────────────
function buildCourseCard(course) {
  const lvl        = LEVEL_MAP[course.level] || { cls: "level-beginner", label: course.level };
  const stars      = buildStars(course.rating);
  const isPremium  = course.isPremium;

  // Precio / etiqueta de acceso
  let priceHTML;
  if (isPremium) {
    priceHTML = `<span class="course-price premium-only">🔒 Solo Premium</span>`;
  } else if (course.price === 0) {
    priceHTML = `<span class="course-price free">GRATIS</span>`;
  } else {
    priceHTML = `<span class="course-price">$${course.price.toFixed(2)}</span>`;
  }

  // Botón CTA
  let ctaHTML;
  if (isPremium) {
    // TODO: Al tener backend, verificar token y redirigir a /cursos/:id si es premium
    ctaHTML = `<button class="btn btn-locked" disabled aria-label="Requiere suscripción">🔒 Suscríbete</button>`;
  } else {
    // TODO: Conectar con GET /api/store/courses/:id para cargar el curso
    ctaHTML = `
      <button class="btn btn-primary" data-course-id="${course.id}" aria-label="Ver curso ${course.title}">
        Ver curso →
      </button>
    `;
  }

  return `
    <article
      class="course-card ${isPremium ? "is-premium" : ""}"
      role="listitem"
      data-course-id="${course.id}"
    >
      <!-- Miniatura -->
      <div class="course-thumb" aria-hidden="true">${course.image}</div>

      <!-- Cuerpo -->
      <div class="course-body">

        <!-- Meta: nivel, duración, badge premium -->
        <div class="course-top-meta">
          <span class="course-level ${lvl.cls}">${lvl.label}</span>
          <span class="course-duration">⏱ ${course.duration}</span>
          ${isPremium ? `<span class="course-premium-tag">⚡ PREMIUM</span>` : ""}
        </div>

        <!-- Título e instructor -->
        <h3 class="course-title">${course.title}</h3>
        <p class="course-instructor">por <span>${course.instructor}</span></p>

        <!-- Descripción -->
        <p class="course-desc">${course.description}</p>

        <!-- Footer: stats + precio + CTA -->
        <div class="course-bottom">
          <div class="course-stats">
            <span class="course-rating" aria-label="Rating ${course.rating}">${stars} ${course.rating}</span>
            <span class="course-students">👥 ${course.students.toLocaleString("es-ES")}</span>
          </div>
          <div class="course-price-area">
            ${priceHTML}
            ${ctaHTML}
          </div>
        </div>

      </div>
    </article>
  `;
}

// ── Helpers ─────────────────────────────────────────────────
function buildStars(rating) {
  const full  = Math.floor(rating);
  const empty = 5 - Math.ceil(rating);
  return "★".repeat(full) + (rating % 1 >= 0.5 ? "½" : "") + "☆".repeat(empty);
}
