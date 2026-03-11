// ============================================================
// pages/coursesPage.js — Página de Cursos
//
// Flujo:
//   1. showSkeletonCourses()
//   2. getCourses()  ← API real → GET /api/curso/
//   3. renderCourses(courses)
//   4. renderPage(html)
//   5. Registrar evento de compra
// ============================================================

import { buyCourse, getCourses } from "../api/api.js";
import { renderCourses } from "../components/courses.js";
import { renderPage, showError } from "../utils/render.js";
import { showSkeletonCourses } from "../components/skeleton.js";

/**
 * Carga y renderiza la página de cursos con compra real.
 */
export async function coursesPage() {
  showSkeletonCourses(5);

  try {
    const res = await getCourses();

    if (!res.ok) {
      showError(res.error || "No se pudieron cargar los cursos.");
      return;
    }

    const courses = res.data;
    const freeCourses = courses.filter((course) => !course.isPremium && course.price === 0);
    const paidCourses = courses.filter((course) => !course.isPremium && course.price > 0);
    const premiumCount = courses.filter((course) => course.isPremium).length;
    const ratedCourses = courses.filter((course) => Number.isFinite(course.rating));
    const avgRating = ratedCourses.length
      ? (ratedCourses.reduce((acc, course) => acc + course.rating, 0) / ratedCourses.length).toFixed(1)
      : "N/D";

    const html = `
      <section class="page-enter" aria-label="Cursos de supervivencia">

        <div class="page-header">
          <p class="page-eyebrow">Formación</p>
          <h1 class="page-title">Cursos de <em>Supervivencia</em></h1>
          <p class="page-desc">
            Conocimiento que salva vidas. Aprende de los mejores instructores
            con experiencia en situaciones reales de emergencia.
          </p>
        </div>

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
            <span class="stat-value">${avgRating === "N/D" ? avgRating : `★ ${avgRating}`}</span>
            <span class="stat-label">Rating promedio</span>
          </div>
        </div>

        ${renderCourses(courses)}

      </section>
    `;

    renderPage(html);
    setTimeout(() => registerCourseEvents(), 200);
  } catch (err) {
    console.error("[coursesPage]", err);
    showError("Error de conexión al cargar los cursos.");
  }
}

function registerCourseEvents() {
  document.querySelectorAll(".btn[data-course-id]").forEach((btn) => {
    if (btn.disabled) return;

    btn.addEventListener("click", async () => {
      const courseId = btn.dataset.courseId;
      const card = btn.closest(".course-card");
      const feedback = card?.querySelector("[data-course-feedback]");
      const original = btn.innerHTML;

      btn.disabled = true;
      btn.innerHTML = "Procesando...";
      setFeedback(feedback, "Registrando compra...", "pending");

      const res = await buyCourse(courseId);

      if (!res.ok) {
        btn.disabled = false;
        btn.innerHTML = original;
        setFeedback(feedback, res.error || "No se pudo completar la compra.", "error");
        return;
      }

      btn.innerHTML = "Comprado";
      setFeedback(feedback, `Compra registrada. ID ${res.data.compra_id}.`, "success");
    });
  });
}

function setFeedback(target, message, state) {
  if (!target) return;

  target.textContent = message;
  target.dataset.state = state;
}
