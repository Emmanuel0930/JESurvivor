// ============================================================
// pages/forumPage.js — Página principal del Foro
//
// Flujo:
//   1. showLoader()
//   2. getPosts()  ← GET /api/posts/
//   3. renderPostList(posts)
//   4. renderPage(html)
//   5. Registrar eventos del DOM (filtros, botones)
// ============================================================

import { createPost, getPosts } from "../api/api.js";
import { renderPostList } from "../components/postList.js";
import { renderPage, showError } from "../utils/render.js";
import { showSkeletonForum } from "../components/skeleton.js";
import { closeModal, showModal, showToast } from "../utils/modal.js";

/**
 * Carga y renderiza la página del foro.
 * Carga posts desde GET /api/posts/ y permite crear con POST /api/posts/crear/.
 */
export async function forumPage() {
  // Muestra skeleton con la forma exacta de la página del foro
  // (cabecera + stats bar + toolbar + 5 tarjetas de post)
  showSkeletonForum(5);

  try {
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
    const form = document.createElement("form");
    form.className = "modal-form";
    form.innerHTML = `
      <label class="modal-label" for="post-title">Título</label>
      <input id="post-title" class="modal-input" type="text" placeholder="Ej. Kit esencial para 72h" required />
      <label class="modal-label" for="post-body">Contenido</label>
      <textarea id="post-body" class="modal-textarea" rows="5" placeholder="Comparte tu experiencia o pregunta..." required></textarea>
      <label class="modal-label" for="post-tags">Etiquetas (opcional, separadas por coma)</label>
      <input id="post-tags" class="modal-input" type="text" placeholder="refugio, agua, emergencia" />
    `;

    const footer = document.createElement("div");
    footer.className = "modal-footer-actions";
    footer.innerHTML = `
      <button type="button" class="btn btn-ghost" data-modal-cancel>Cancelar</button>
      <button type="submit" class="btn btn-primary" form="post-form">Publicar</button>
    `;
    form.id = "post-form";
    footer.querySelector("[data-modal-cancel]").addEventListener("click", () => closeModal());

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const title = document.getElementById("post-title")?.value?.trim();
      const content = document.getElementById("post-body")?.value?.trim();
      const tagsRaw = document.getElementById("post-tags")?.value?.trim();
      const tags = tagsRaw
        ? tagsRaw.split(",").map((t) => t.trim()).filter(Boolean)
        : [];

      if (!title || !content) {
        showToast("Título y contenido son obligatorios.", "error");
        return;
      }

      const submitBtn = footer.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Publicando...";
      }

      const res = await createPost({ title, content, tags });
      closeModal();

      if (!res.ok) {
        showToast(res.error || "No se pudo publicar el post.", "error");
        return;
      }

      showToast("Post publicado correctamente.", "success");
      await forumPage();
    });

    showModal({
      title: "Nuevo post",
      size: "md",
      body: form,
      footer,
    });
  });
}
