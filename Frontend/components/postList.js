// ============================================================
// components/postList.js — Lista de posts del foro
// Recibe un array de posts y devuelve HTML string.
// No hace fetch — los datos llegan desde forumPage.js
// ============================================================

/**
 * Renderiza la lista completa de posts.
 * @param {Array} posts — Posts desde getPosts()
 * @returns {string} HTML listo para insertar
 */
export function renderPostList(posts) {
  if (!posts || posts.length === 0) {
    return `
      <div class="error-wrap">
        <span class="error-icon">📭</span>
        <p class="error-msg">No hay posts disponibles todavía.</p>
      </div>
    `;
  }

  return `
    <div class="post-list stagger" role="list">
      ${posts.map(buildPostCard).join("")}
    </div>
  `;
}

// ── Tarjeta individual de post ──────────────────────────────
function buildPostCard(post) {
  const isPremium = post.isPremium;

  // Contenido visible vs bloqueado
  const excerpt = isPremium
    ? `${post.content.slice(0, 72)}… <span class="locked-hint">[ 🔒 Requiere suscripción premium ]</span>`
    : post.content;

  // Tags
  const tagsHTML = post.tags
    .map((t) => `<span class="post-tag">${t}</span>`)
    .join("");

  return `
    <article
      class="post-card ${isPremium ? "is-premium" : ""}"
      role="listitem"
      data-post-id="${post.id}"
      tabindex="0"
      aria-label="Post: ${post.title}"
    >
      <!-- Cabecera: autor + badge premium -->
      <div class="post-head">
        <div class="post-meta">
          <div class="post-ava" aria-hidden="true">${post.avatar}</div>
          <div class="post-who">
            <span class="post-author">${post.author}</span>
            <span class="post-date">${formatDate(post.date)}</span>
          </div>
        </div>
        ${isPremium ? `<span class="post-badge-premium">⚡ Premium</span>` : ""}
      </div>

      <!-- Título -->
      <h3 class="post-title">${post.title}</h3>

      <!-- Extracto -->
      <p class="post-excerpt">${excerpt}</p>

      <!-- Footer: tags + reacciones -->
      <div class="post-foot">
        <div class="post-tags" aria-label="Tags">${tagsHTML}</div>
        <div class="post-reactions" aria-label="Reacciones">
          <button class="post-react" aria-label="${post.likes} me gusta">
            <span class="r-icon" aria-hidden="true">♥</span>
            <span>${post.likes}</span>
          </button>
          <button class="post-react" aria-label="${post.comments} comentarios">
            <span class="r-icon" aria-hidden="true">◎</span>
            <span>${post.comments}</span>
          </button>
        </div>
      </div>
    </article>
  `;
}

// ── Helpers ─────────────────────────────────────────────────
function formatDate(dateStr) {
  try {
    return new Date(dateStr).toLocaleDateString("es-ES", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}
