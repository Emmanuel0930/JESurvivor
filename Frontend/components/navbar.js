// ============================================================
// components/navbar.js — Barra de navegación principal
// Entregable 2: Agrega botón "Integraciones" al menú.
// ============================================================

import { getCurrentUser } from "../api/api.js";
import { openCart } from "./cart.js";

export async function initNavbar(navigate) {
  const navbar = document.getElementById("navbar");
  if (!navbar) return;

  let user = null;
  try {
    const res = await getCurrentUser();
    if (res.ok) user = res.data;
  } catch (_) {}

  navbar.innerHTML = buildNavbar(user);

  navbar.querySelectorAll("[data-page]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      const page = el.dataset.page;
      if (page) navigate(page);
    });
  });

  document.getElementById("nav-cart-btn")?.addEventListener("click", (e) => {
    e.preventDefault();
    openCart();
  });
}

function buildNavbar(user) {
  return `
    <div class="nav-inner">

      <div class="nav-logo" data-page="forum" role="button" tabindex="0" aria-label="Ir al inicio">
        <div class="logo-skull" aria-hidden="true">☠</div>
        <div class="logo-wordmark">
          <span class="logo-top">JE<span>Survivor</span></span>
          <span class="logo-sub">Survival Platform</span>
        </div>
      </div>

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
        <button class="nav-btn nav-btn--integ" data-page="integration" aria-label="Integraciones">
          <span class="nb-icon" aria-hidden="true">🔗</span>
          <span class="nb-label">Integraciones</span>
        </button>
      </nav>

      <div class="nav-actions">
        <button type="button" class="nav-cart-btn" id="nav-cart-btn" aria-label="Abrir carrito">
          <span class="nav-cart-icon" aria-hidden="true">🛒</span>
          <span class="nav-cart-badge is-hidden" id="cart-badge">0</span>
        </button>
      </div>

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
  return `
    <button class="nav-cta-btn" data-page="subscription">
      Únete ahora
    </button>
  `;
}