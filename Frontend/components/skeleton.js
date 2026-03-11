// ============================================================
// components/skeleton.js — Skeleton Loader reutilizable
//
// Exporta una función por cada tipo de página:
//   showSkeletonForum()        → para forumPage.js
//   showSkeletonStore()        → para storePage.js
//   showSkeletonCourses()      → para coursesPage.js
//   showSkeletonSubscription() → para subscriptionPage.js
//
// Cada función monta directamente en #app-root el HTML del
// skeleton correspondiente. Las páginas llaman a estas
// funciones en lugar de showLoader() de render.js.
// ============================================================

// ── Referencia al contenedor principal ──────────────────────
const getRoot = () => document.getElementById("app-root");

// ── Helper: bloque de cabecera de página (común a todas) ────
function headerSkeleton() {
  return `
    <div class="sk-page-header">
      <div class="sk-block sk-eyebrow"></div>
      <div class="sk-block sk-title"></div>
      <div class="sk-block sk-title sk-title--short"></div>
      <div class="sk-block sk-desc"></div>
      <div class="sk-block sk-desc sk-desc--short"></div>
    </div>
  `;
}

// ── Helper: stats bar esqueleto (común a todas) ──────────────
function statsBarSkeleton(cols = 3) {
  const items = Array.from({ length: cols }, () => `
    <div class="sk-stat-item">
      <div class="sk-block sk-stat-value"></div>
      <div class="sk-block sk-stat-label"></div>
    </div>
  `).join("");

  return `<div class="sk-stats-bar">${items}</div>`;
}

// ============================================================
// FORO — lista de posts
// Muestra la cabecera + stats bar + N tarjetas de post
// ============================================================
export function showSkeletonForum(count = 5) {
  const root = getRoot();
  if (!root) return;

  const cards = Array.from({ length: count }, (_, i) => `
    <div class="sk-post-card" style="animation-delay: ${i * 0.06}s">
      <!-- Avatar + autor -->
      <div class="sk-post-head">
        <div class="sk-block sk-avatar"></div>
        <div class="sk-post-who">
          <div class="sk-block sk-author"></div>
          <div class="sk-block sk-date"></div>
        </div>
      </div>
      <!-- Título -->
      <div class="sk-block sk-post-title"></div>
      <!-- Extracto (2 líneas) -->
      <div class="sk-block sk-line"></div>
      <div class="sk-block sk-line sk-line--short"></div>
      <!-- Footer: tags + reacciones -->
      <div class="sk-post-foot">
        <div class="sk-tags">
          <div class="sk-block sk-tag"></div>
          <div class="sk-block sk-tag"></div>
          <div class="sk-block sk-tag"></div>
        </div>
        <div class="sk-reactions">
          <div class="sk-block sk-react"></div>
          <div class="sk-block sk-react"></div>
        </div>
      </div>
    </div>
  `).join("");

  root.innerHTML = `
    <div class="sk-page" aria-busy="true" aria-label="Cargando foro...">
      ${headerSkeleton()}
      ${statsBarSkeleton(3)}
      <!-- Toolbar: botón + filtros -->
      <div class="sk-toolbar">
        <div class="sk-block sk-btn"></div>
        <div class="sk-filter-group">
          <div class="sk-block sk-pill"></div>
          <div class="sk-block sk-pill"></div>
          <div class="sk-block sk-pill"></div>
        </div>
      </div>
      <!-- Lista de posts -->
      <div class="sk-post-list">${cards}</div>
    </div>
  `;
}

// ============================================================
// TIENDA — grid de kits
// Muestra la cabecera + stats bar + N tarjetas de kit
// ============================================================
export function showSkeletonStore(count = 4) {
  const root = getRoot();
  if (!root) return;

  const cards = Array.from({ length: count }, (_, i) => `
    <div class="sk-kit-card" style="animation-delay: ${i * 0.07}s">
      <!-- Área de imagen -->
      <div class="sk-kit-visual"></div>
      <div class="sk-kit-body">
        <!-- Nombre -->
        <div class="sk-block sk-kit-name"></div>
        <!-- Descripción (2 líneas) -->
        <div class="sk-block sk-line"></div>
        <div class="sk-block sk-line sk-line--short"></div>
        <!-- Items incluidos (3 líneas) -->
        <div class="sk-kit-items">
          <div class="sk-block sk-item-row"></div>
          <div class="sk-block sk-item-row"></div>
          <div class="sk-block sk-item-row"></div>
        </div>
        <!-- Footer: stock + precio + botón -->
        <div class="sk-kit-footer">
          <div class="sk-block sk-stock"></div>
          <div class="sk-kit-purchase">
            <div class="sk-block sk-price"></div>
            <div class="sk-block sk-btn sk-btn--sm"></div>
          </div>
        </div>
      </div>
    </div>
  `).join("");

  root.innerHTML = `
    <div class="sk-page" aria-busy="true" aria-label="Cargando tienda...">
      ${headerSkeleton()}
      ${statsBarSkeleton(3)}
      <!-- Banner de descuento -->
      <div class="sk-block sk-banner"></div>
      <!-- Grid de kits -->
      <div class="sk-kits-grid">${cards}</div>
    </div>
  `;
}

// ============================================================
// CURSOS — lista de cursos
// Muestra la cabecera + stats bar + N tarjetas de curso
// ============================================================
export function showSkeletonCourses(count = 5) {
  const root = getRoot();
  if (!root) return;

  const cards = Array.from({ length: count }, (_, i) => `
    <div class="sk-course-card" style="animation-delay: ${i * 0.06}s">
      <!-- Miniatura lateral -->
      <div class="sk-course-thumb"></div>
      <div class="sk-course-body">
        <!-- Meta: nivel + duración -->
        <div class="sk-course-meta">
          <div class="sk-block sk-pill sk-pill--level"></div>
          <div class="sk-block sk-pill sk-pill--duration"></div>
        </div>
        <!-- Título -->
        <div class="sk-block sk-course-title"></div>
        <!-- Instructor -->
        <div class="sk-block sk-instructor"></div>
        <!-- Descripción -->
        <div class="sk-block sk-line"></div>
        <div class="sk-block sk-line sk-line--short"></div>
        <!-- Footer: rating + precio + botón -->
        <div class="sk-course-footer">
          <div class="sk-course-stats">
            <div class="sk-block sk-rating"></div>
            <div class="sk-block sk-students"></div>
          </div>
          <div class="sk-course-actions">
            <div class="sk-block sk-price"></div>
            <div class="sk-block sk-btn sk-btn--sm"></div>
          </div>
        </div>
      </div>
    </div>
  `).join("");

  root.innerHTML = `
    <div class="sk-page" aria-busy="true" aria-label="Cargando cursos...">
      ${headerSkeleton()}
      ${statsBarSkeleton(4)}
      <!-- Lista de cursos -->
      <div class="sk-courses-list">${cards}</div>
    </div>
  `;
}

// ============================================================
// SUSCRIPCIÓN — planes + badges
// Muestra la cabecera + stats bar + N plan cards + badges
// ============================================================
export function showSkeletonSubscription(count = 3) {
  const root = getRoot();
  if (!root) return;

  const plans = Array.from({ length: count }, (_, i) => `
    <div class="sk-plan-card" style="animation-delay: ${i * 0.08}s">
      <!-- Nombre del plan -->
      <div class="sk-block sk-plan-name"></div>
      <!-- Badge -->
      <div class="sk-block sk-plan-badge"></div>
      <!-- Precio -->
      <div class="sk-block sk-plan-price"></div>
      <!-- Features (5 ítems) -->
      <div class="sk-plan-features">
        ${Array.from({ length: 5 }, () => `
          <div class="sk-feat-row">
            <div class="sk-block sk-feat-check"></div>
            <div class="sk-block sk-feat-text"></div>
          </div>
        `).join("")}
      </div>
      <!-- Botón CTA -->
      <div class="sk-block sk-btn sk-btn--full"></div>
    </div>
  `).join("");

  // Badges showcase skeleton
  const badges = Array.from({ length: 2 }, (_, i) => `
    <div class="sk-badge-chip" style="animation-delay: ${(count + i) * 0.08}s">
      <div class="sk-block sk-badge-icon"></div>
      <div class="sk-badge-info">
        <div class="sk-block sk-badge-name"></div>
        <div class="sk-block sk-badge-plan"></div>
      </div>
    </div>
  `).join("");

  root.innerHTML = `
    <div class="sk-page" aria-busy="true" aria-label="Cargando suscripciones...">
      ${headerSkeleton()}
      ${statsBarSkeleton(3)}
      <!-- Sub hero text -->
      <div class="sk-sub-hero">
        <div class="sk-block sk-sub-title"></div>
        <div class="sk-block sk-line"></div>
        <div class="sk-block sk-line sk-line--short"></div>
      </div>
      <!-- Grid de planes -->
      <div class="sk-plans-grid">${plans}</div>
      <!-- Badges showcase -->
      <div class="sk-badges-section">
        <div class="sk-block sk-badges-title"></div>
        <div class="sk-badges-row">${badges}</div>
      </div>
    </div>
  `;
}
