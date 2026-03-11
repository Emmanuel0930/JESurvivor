// ============================================================
// pages/subscriptionPage.js — Página de Suscripciones
//
// Flujo:
//   1. showLoader()
//   2. getSubscriptions() ← mock → futuro: fetch("GET /api/store/subscriptions")
//   3. renderSubscription(plans)
//   4. renderPage(html)
//   5. Registrar eventos de suscripción
// ============================================================

import { getSubscriptions } from "../api/api.js";
import { renderSubscription } from "../components/subscription.js";
import { renderPage, showError } from "../utils/render.js";
import { showSkeletonSubscription } from "../components/skeleton.js";

/**
 * Carga y renderiza la página de suscripciones.
 * getSubscriptions() pasará a hacer fetch a
 * GET /api/store/subscriptions cuando el backend esté listo.
 */
export async function subscriptionPage() {
  // Muestra skeleton con la forma exacta de la página de suscripciones
  // (cabecera + stats bar + 3 plan cards + 2 badge chips)
  showSkeletonSubscription(3);

  try {
    // ── Obtener planes ─────────────────────────────────────
    // TODO (backend): descomentar en api/api.js:
    //   const res = await fetch("/api/store/subscriptions");
    const res = await getSubscriptions();

    if (!res.ok) {
      showError("No se pudieron cargar los planes.");
      return;
    }

    const plans       = res.data;
    const paidPlans   = plans.filter((p) => p.price > 0);
    const minPrice    = Math.min(...paidPlans.map((p) => p.price));
    const badgeCount  = plans.filter((p) => p.badge).length;

    const html = `
      <section class="page-enter" aria-label="Suscripciones premium">

        <!-- Cabecera -->
        <div class="page-header">
          <p class="page-eyebrow">Membresía</p>
          <h1 class="page-title"><em>Suscripción</em> Premium</h1>
          <p class="page-desc">
            Accede a contenido exclusivo, obtén tu badge en el foro
            y únete a la comunidad de élite de supervivientes.
          </p>
        </div>

        <!-- Stats bar -->
        <div class="stats-bar">
          <div class="stat-item">
            <span class="stat-value">${paidPlans.length}</span>
            <span class="stat-label">Planes de pago</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">$${minPrice}</span>
            <span class="stat-label">Desde / mes</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">${badgeCount}</span>
            <span class="stat-label">Badges exclusivos</span>
          </div>
        </div>

        <!-- Planes + badges showcase (componente) -->
        ${renderSubscription(plans)}

      </section>
    `;

    renderPage(html);

    // ── Registrar eventos de suscripción ───────────────────
    setTimeout(() => registerSubEvents(), 200);

  } catch (err) {
    console.error("[subscriptionPage]", err);
    showError("Error de conexión al cargar los planes.");
  }
}

// ── Eventos de suscripción ────────────────────────────────────
function registerSubEvents() {
  document.querySelectorAll(".btn[data-plan-id]").forEach((btn) => {
    if (btn.disabled) return;

    btn.addEventListener("click", () => {
      const planId = btn.dataset.planId;

      // TODO: Redirigir a pasarela de pago (Stripe / PayPal):
      //   POST /api/store/subscriptions/checkout
      //   body: { planId, successUrl, cancelUrl }
      // Requiere autenticación JWT del usuario

      // Feedback visual mientras no hay checkout real
      const original = btn.innerHTML;
      btn.innerHTML  = "Redirigiendo...";
      btn.disabled   = true;

      setTimeout(() => {
        btn.innerHTML = original;
        btn.disabled  = false;
        alert(`[Mock] Checkout para plan ${planId}.\nConectar con POST /api/store/subscriptions/checkout`);
      }, 1200);
    });
  });
}
