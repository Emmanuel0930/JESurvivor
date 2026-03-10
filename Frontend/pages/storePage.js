// ============================================================
// pages/storePage.js — Página de la Tienda
//
// Flujo:
//   1. showLoader()
//   2. getKits()  ← mock → futuro: fetch("GET /api/store/kits")
//   3. renderStore(kits)
//   4. renderPage(html)
//   5. Registrar evento de compra
// ============================================================

import { getKits } from "../api/api.js";
import { renderStore } from "../components/store.js";
import { renderPage, showError } from "../utils/render.js";
import { showSkeletonStore } from "../components/skeleton.js";

/**
 * Carga y renderiza la página de la tienda.
 * getKits() pasará a hacer fetch a GET /api/store/kits
 * en cuanto el backend esté disponible.
 */
export async function storePage() {
  // Muestra skeleton con la forma exacta de la tienda
  // (cabecera + stats bar + banner + 4 tarjetas de kit)
  showSkeletonStore(4);

  try {
    // ── Obtener kits ───────────────────────────────────────
    // TODO (backend): descomentar en api/api.js:
    //   const res = await fetch("/api/store/kits");
    const res = await getKits();

    if (!res.ok) {
      showError("No se pudo cargar la tienda.");
      return;
    }

    const kits      = res.data;
    const minPrice  = Math.min(...kits.map((k) => k.price));
    const maxPrice  = Math.max(...kits.map((k) => k.price));
    const totalStock = kits.reduce((acc, k) => acc + k.stock, 0);

    const html = `
      <section class="page-enter" aria-label="Tienda de supervivencia">

        <!-- Cabecera -->
        <div class="page-header">
          <p class="page-eyebrow">Equipamiento</p>
          <h1 class="page-title">Tienda de <em>Supervivencia</em></h1>
          <p class="page-desc">
            Kits seleccionados por expertos en emergencias reales.
            Tu preparación empieza aquí.
          </p>
        </div>

        <!-- Stats bar -->
        <div class="stats-bar">
          <div class="stat-item">
            <span class="stat-value">${kits.length}</span>
            <span class="stat-label">Kits disponibles</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">$${minPrice}</span>
            <span class="stat-label">Desde</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">${totalStock}</span>
            <span class="stat-label">Unidades en stock</span>
          </div>
        </div>

        <!-- Banner descuento premium -->
        <div class="store-alert" role="note">
          <span class="store-alert-icon" aria-hidden="true">⚡</span>
          <span>
            Suscriptores <strong>SURVIVOR PRO</strong> obtienen 15% de descuento ·
            Suscriptores <strong>ELITE GHOST</strong> obtienen 30%
          </span>
        </div>

        <!-- Grid de kits (componente) -->
        ${renderStore(kits)}

      </section>
    `;

    renderPage(html);

    // ── Registrar evento de compra ──────────────────────────
    setTimeout(() => registerBuyEvents(), 200);

  } catch (err) {
    console.error("[storePage]", err);
    showError("Error de conexión al cargar la tienda.");
  }
}

// ── Eventos de compra ────────────────────────────────────────
function registerBuyEvents() {
  document.querySelectorAll(".btn[data-kit-id]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const kitId = btn.dataset.kitId;

      // TODO: Llamar a POST /api/store/cart con { kitId, qty: 1 }
      // o redirigir a /checkout?kit=${kitId}
      // Requiere autenticación JWT

      // Feedback visual temporal
      const original = btn.textContent;
      btn.textContent = "✓ Agregado";
      btn.disabled    = true;
      btn.style.background = "var(--green-bright)";
      btn.style.borderColor = "var(--green-bright)";
      btn.style.color = "#000";

      setTimeout(() => {
        btn.textContent  = original;
        btn.disabled     = false;
        btn.style.cssText = "";
      }, 2000);
    });
  });
}
