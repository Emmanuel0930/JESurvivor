// ============================================================
// pages/forumPage.js — Página principal del Foro
//
// Flujo:
//   1. showLoader()
//   2. getPosts()  ← mock → futuro: fetch("GET /api/posts")
//   3. renderPostList(posts)
//   4. renderPage(html)
//   5. Registrar eventos del DOM (filtros, botones)
// ============================================================

import { getPosts } from "../api/api.js";
import { renderPostList } from "../components/postList.js";
import { renderPage, showError } from "../utils/render.js";
import { showSkeletonForum } from "../components/skeleton.js";

/**
 * Carga y renderiza la página del foro.
 * Llama a getPosts() — cuando el backend esté listo esa
 * función hará fetch a GET /api/posts automáticamente.
 */
export async function forumPage() {
  // Muestra skeleton con la forma exacta de la página del foro
  // (cabecera + stats bar + toolbar + 5 tarjetas de post)
  showSkeletonForum(5);

  try {
    // ── Obtener posts ──────────────────────────────────────
    // TODO (backend): getPosts() ya tiene el fetch comentado.
    //   Solo hay que descomentar la línea en api/api.js:
    //   const res = await fetch("/api/posts");
    const res = await getPosts();

    if (!res.ok) {
      showError("No se pudieron cargar los posts del foro.");
      return;
    }

    const posts       = res.data;
    const totalPosts  = posts.length;
    const totalAuthors = new Set(posts.map((p) => p.author)).size;
    const premiumCount = posts.filter((p) => p.isPremium).length;

    const html = `
      <section class="page-enter" aria-label="Foro de supervivencia">

        <!-- Cabecera de página -->
        <div class="page-header">
          <p class="page-eyebrow">Comunidad</p>
          <h1 class="page-title">Foro de <em>Supervivencia</em></h1>
          <p class="page-desc">
            Consejos reales de supervivientes reales. Comparte lo que sabes.
            Aprende lo que no.
          </p>
        </div>

        <!-- Stats bar -->
        <div class="stats-bar" role="status" aria-label="Estadísticas del foro">
          <div class="stat-item">
            <span class="stat-value">${totalPosts}</span>
            <span class="stat-label">Posts</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">${totalAuthors}</span>
            <span class="stat-label">Autores</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">${premiumCount}</span>
            <span class="stat-label">Exclusivos</span>
          </div>
        </div>

        <!-- Toolbar: nuevo post + filtros -->
        <div class="forum-toolbar">
          <!--
            TODO: Botón "Nuevo Post" → conectar con
            POST /api/posts (requiere autenticación JWT)
          -->
          <button class="btn btn-primary" id="btn-new-post">
            + Nuevo Post
          </button>

          <div class="filter-group" role="group" aria-label="Filtrar posts">
            <button class="filter-pill active" data-filter="all">Todos</button>
            <button class="filter-pill" data-filter="free">Gratuitos</button>
            <button class="filter-pill" data-filter="premium">Premium</button>
          </div>
        </div>

        <!-- Lista de posts (componente) -->
        <div id="post-list-container">
          ${renderPostList(posts)}
        </div>

      </section>
    `;

    renderPage(html);

    // ── Registrar eventos del DOM ───────────────────────────
    // Hay que esperar al re-render antes de seleccionar elementos
    setTimeout(() => {
      registerFilterEvents(posts);
      registerNewPostButton();
    }, 200);

  } catch (err) {
    console.error("[forumPage]", err);
    showError("Error de conexión. Verifica tu red e intenta de nuevo.");
  }
}

// ── Filtros ─────────────────────────────────────────────────
function registerFilterEvents(allPosts) {
  const pills     = document.querySelectorAll(".filter-pill");
  const container = document.getElementById("post-list-container");
  if (!pills.length || !container) return;

  pills.forEach((pill) => {
    pill.addEventListener("click", () => {
      // Actualizar pill activo
      pills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");

      const filter = pill.dataset.filter;
      let filtered = allPosts;

      if (filter === "free")    filtered = allPosts.filter((p) => !p.isPremium);
      if (filter === "premium") filtered = allPosts.filter((p) => p.isPremium);

      container.innerHTML = renderPostList(filtered);
    });
  });
}

// ── Botón nuevo post ─────────────────────────────────────────
function registerNewPostButton() {
  const btn = document.getElementById("btn-new-post");
  if (!btn) return;

  btn.addEventListener("click", () => {
    // TODO: Abrir modal/formulario de nuevo post
    // Se conectará con POST /api/posts (requiere token JWT)
    alert("[Mock] Formulario de nuevo post.\nConectar con POST /api/posts cuando el backend esté listo.");
  });
}
