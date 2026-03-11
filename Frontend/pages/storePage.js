// ============================================================
// pages/storePage.js — Página de la Tienda
//
// Flujo:
//   1. showSkeletonStore()
//   2. getKits()  ← API real → GET /api/kit/
//   3. renderStore(kits)
//   4. renderPage(html)
//   5. Registrar evento de reserva
// ============================================================

import { getKits, reserveKit } from "../api/api.js";
import { renderStore } from "../components/store.js";
import { renderPage, showError } from "../utils/render.js";
import { showSkeletonStore } from "../components/skeleton.js";

/**
 * Carga y renderiza la página de la tienda con reserva real.
 */
export async function storePage() {
  showSkeletonStore(4);

  try {
    const res = await getKits();

    if (!res.ok) {
      showError(res.error || "No se pudo cargar la tienda.");
      return;
    }

    const kits = res.data;
    const minPrice = kits.length ? Math.min(...kits.map((kit) => kit.price)) : 0;
    const totalStock = kits.reduce((acc, kit) => acc + kit.stock, 0);

    const html = `
      <section class="page-enter" aria-label="Tienda de supervivencia">

        <div class="page-header">
          <p class="page-eyebrow">Equipamiento</p>
          <h1 class="page-title">Tienda de <em>Supervivencia</em></h1>
          <p class="page-desc">
            Kits seleccionados por expertos en emergencias reales.
            Tu preparación empieza aquí.
          </p>
        </div>

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

        <div class="store-alert" role="note">
          <span class="store-alert-icon" aria-hidden="true">⚡</span>
          <span>
            Reserva el kit que necesitas, elige tus fechas
            y registra la solicitud directamente contra la service layer.
          </span>
        </div>

        ${renderStore(kits)}

      </section>
    `;

    renderPage(html);
    setTimeout(() => registerReservationEvents(), 200);
  } catch (err) {
    console.error("[storePage]", err);
    showError("Error de conexión al cargar la tienda.");
  }
}

function registerReservationEvents() {
  document.querySelectorAll(".btn[data-kit-id]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const kitId = btn.dataset.kitId;
      const card = btn.closest(".kit-card");
      const startInput = card?.querySelector("[data-kit-start]");
      const endInput = card?.querySelector("[data-kit-end]");
      const feedback = card?.querySelector("[data-kit-feedback]");
      const inicio = startInput?.value;
      const fin = endInput?.value;

      if (!inicio || !fin) {
        setFeedback(feedback, "Selecciona un rango de fechas válido.", "error");
        return;
      }

      if (inicio >= fin) {
        setFeedback(feedback, "La fecha final debe ser posterior a la inicial.", "error");
        return;
      }

      const original = btn.textContent;
      btn.textContent = "Reservando...";
      btn.disabled = true;
      setFeedback(feedback, "Enviando reserva...", "pending");

      const res = await reserveKit(kitId, inicio, fin);

      if (!res.ok) {
        btn.textContent = original;
        btn.disabled = false;
        setFeedback(feedback, res.error || "No se pudo registrar la reserva.", "error");
        return;
      }

      btn.textContent = "Reservado";
      setFeedback(feedback, `Reserva creada. ID ${res.data.reserva_id}.`, "success");
    });
  });
}

function setFeedback(target, message, state) {
  if (!target) return;

  target.textContent = message;
  target.dataset.state = state;
}
