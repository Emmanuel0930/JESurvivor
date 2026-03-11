// ============================================================
// pages/coursesPage.js — Página de Cursos
//
// Flujo:
//   1. showLoader()
//   2. getCourses()  ← mock → futuro: fetch("GET /api/store/courses")
//   3. renderCourses(courses)
//   4. renderPage(html)
//   5. Registrar evento "Ver curso"
// ============================================================

import { getCourses } from "../api/api.js";
import { renderCourses } from "../components/courses.js";
import { renderPage, showError } from "../utils/render.js";
import { showSkeletonCourses } from "../components/skeleton.js";

/**
 * Carga y renderiza la página de cursos.
 * getCourses() pasará a hacer fetch a GET /api/store/courses
 * cuando el backend esté disponible.
 */
export async function coursesPage() {
  // Muestra skeleton con la forma exacta de la página de cursos
  // (cabecera + stats bar + 5 tarjetas de curso)
  showSkeletonCourses(5);

  try {
    // ── Obtener cursos ─────────────────────────────────────
    // TODO (backend): descomentar en api/api.js:
    //   const res = await fetch("/api/store/courses");
    const res = await getCourses();

    if (!res.ok) {
      showError("No se pudieron cargar los cursos.");
      return;
    }

    const courses      = res.data;
    const freeCourses  = courses.filter((c) => !c.isPremium && c.price === 0);
    const paidCourses  = courses.filter((c) => !c.isPremium && c.price > 0);
    const premiumCount = courses.filter((c) => c.isPremium).length;
    const avgRating    = (
      courses.reduce((acc, c) => acc + c.rating, 0) / courses.length
    ).toFixed(1);

    const html = `
      <section class="page-enter" aria-label="Cursos de supervivencia">

        <!-- Cabecera -->
        <div class="page-header">
          <p class="page-eyebrow">Formación</p>
          <h1 class="page-title">Cursos de <em>Supervivencia</em></h1>
          <p class="page-desc">
            Conocimiento que salva vidas. Aprende de los mejores instructores
            con experiencia en situaciones reales de emergencia.
          </p>
        </div>

        <!-- Stats bar -->
        <div class="stats-bar">
          <div class="stat-item">
            <span class="stat-value">${freeCourses.length}</span>
            <span class="stat-label">Cursos gratis</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">${paidCourses.length}</span>
            <span class="stat-label">De pago</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">${premiumCount}</span>
            <span class="stat-label">Exclusivos Premium</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">★ ${avgRating}</span>
            <span class="stat-label">Rating promedio</span>
          </div>
        </div>

        <!-- Lista de cursos (componente) -->
        ${renderCourses(courses)}

      </section>
    `;

    renderPage(html);

    // ── Registrar evento "Ver curso" ────────────────────────
    setTimeout(() => registerCourseEvents(), 200);

  } catch (err) {
    console.error("[coursesPage]", err);
    showError("Error de conexión al cargar los cursos.");
  }
}

// ── Eventos de curso ─────────────────────────────────────────
function registerCourseEvents() {
  document.querySelectorAll(".btn[data-course-id]").forEach((btn) => {
    if (btn.disabled) return;

    btn.addEventListener("click", () => {
      const courseId = btn.dataset.courseId;

      // TODO: Redirigir a la vista de curso:
      // GET /api/store/courses/:id → renderizar contenido del curso
      // Si requiere premium, verificar token antes de cargar
      alert(`[Mock] Abriendo curso ${courseId}.\nConectar con GET /api/store/courses/${courseId}`);
    });
  });
}
