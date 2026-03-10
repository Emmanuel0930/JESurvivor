// ============================================================
// components/navbar.js — Barra de navegación principal
// Renderiza el logo, links de navegación y datos del usuario.
// El usuario viene de getCurrentUser() (mock → /api/users/me)
// ============================================================

import { getCurrentUser } from "../api/api.js";

/**
 * Inicializa la navbar con datos de usuario y eventos de
 * navegación. Llama a navigate(pageId) en cada clic.
 *
 * @param {Function} navigate — Función de enrutamiento de app.js
 */
export async function initNavbar(navigate) {
  const navbar = document.getElementById("navbar");
  if (!navbar) return;

  // ── Obtener usuario actual ──────────────────────────────
  // TODO: Cuando el backend esté listo, getCurrentUser() hará
  // fetch a GET /api/users/me con el token JWT en el header.
  let user = null;
  try {
    const res = await getCurrentUser();
    if (res.ok) user = res.data;
  } catch (_) {
    // Si falla silenciosamente, mostrar navbar sin usuario
  }

  navbar.innerHTML = buildNavbar(user);

  // ── Eventos de navegación ───────────────────────────────
  navbar.querySelectorAll("[data-page]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      const page = el.dataset.page;
      if (page) navigate(page);
    });
  });
}

// ── Construcción del HTML ─────────────────────────────────
function buildNavbar(user) {
  return `
    <div class="nav-inner">

      <!-- Logo -->
      <div class="nav-logo" data-page="forum" role="button" tabindex="0" aria-label="Ir al inicio">
        <div class="logo-skull" aria-hidden="true">☠</div>
        <div class="logo-wordmark">
          <span class="logo-top">JE<span>Survivor</span></span>
          <span class="logo-sub">Survival Platform</span>
        </div>
      </div>

      <!-- Links de navegación -->
      <nav class="nav-links" role="navigation" aria-label="Navegación principal">
        <button class="nav-btn" data-page="forum" aria-label="Foro">
          <span class="nb-icon" aria-hidden="true">📡</span>
          <span class="nb-label">Foro</span>
        </button>
        <button class="nav-btn" data-page="store" aria-label="Tienda">
          <span class="nb-icon" aria-hidden="true">🏪</span>
          <span class="nb-label">Tienda</span>
        </button>
        <button class="nav-btn" data-page="courses" aria-label="Cursos">
          <span class="nb-icon" aria-hidden="true">📚</span>
          <span class="nb-label">Cursos</span>
        </button>
        <button class="nav-btn" data-page="subscription" aria-label="Suscripción">
          <span class="nb-icon" aria-hidden="true">⚡</span>
          <span class="nb-label">Suscripción</span>
        </button>
      </nav>

      <!-- Usuario / CTA -->
      <div class="nav-user">
        ${user ? buildUserChip(user) : buildGuestCTA()}
      </div>

    </div>
  `;
}

function buildUserChip(user) {
  return `
    <div class="nav-user-avatar" aria-hidden="true">${user.avatar}</div>
    <div class="nav-user-info">
      <span class="nav-user-name">${user.username}</span>
      ${user.isPremium
        ? `<span class="nav-user-badge">${user.badge}</span>`
        : `<span class="nav-user-badge" style="color:var(--txt-dim)">FREE</span>`
      }
    </div>
  `;
}

function buildGuestCTA() {
  // TODO: Conectar con POST /api/users/login o redirigir al formulario
  return `
    <button class="nav-cta-btn" data-page="subscription">
      Únete ahora
    </button>
  `;
}
