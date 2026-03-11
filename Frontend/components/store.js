// ============================================================
// components/store.js — Grid de kits de supervivencia
// Recibe kits desde getKits() y genera el HTML del catálogo.
// ============================================================

/**
 * Renderiza el grid de kits de la tienda.
 * @param {Array} kits — Kits desde getKits()
 * @returns {string} HTML listo para insertar
 */
export function renderStore(kits) {
  if (!kits || kits.length === 0) {
    return `
      <div class="error-wrap">
        <span class="error-icon">📦</span>
        <p class="error-msg">La tienda está vacía por el momento.</p>
      </div>
    `;
  }

  return `
    <div class="kits-grid stagger" role="list">
      ${kits.map(buildKitCard).join("")}
    </div>
  `;
}

// ── Tarjeta individual de kit ───────────────────────────────
function buildKitCard(kit) {
  const { startDate, endDate, minDate } = getDefaultReservationDates();

  // Nivel de stock
  const stockClass  = kit.stock <= 5 ? "low" : "";
  const stockLabel  = kit.stock <= 5
    ? `⚠ Solo ${kit.stock} restantes`
    : `✓ En stock (${kit.stock})`;

  // Badge de esquina (BESTSELLER / PREMIUM)
  const cornerBadge = kit.badge
    ? `<span class="kit-corner-badge ${kit.badge.toLowerCase()}">${kit.badge}</span>`
    : "";

  // Lista de items incluidos
  const itemsHTML = kit.items
    .map((item) => `<li class="kit-item">${item}</li>`)
    .join("");

  return `
    <div class="kit-card" role="listitem" data-kit-id="${kit.id}">
      ${cornerBadge}

      <!-- Área visual / ícono -->
      <div class="kit-visual" aria-hidden="true">
        <span style="position:relative;z-index:1">${kit.image}</span>
      </div>

      <!-- Cuerpo -->
      <div class="kit-body">
        <h3 class="kit-name">${kit.name}</h3>
        <p class="kit-desc">${kit.description}</p>

        <!-- Contenido incluido -->
        <ul class="kit-items-list" aria-label="Incluye">
          ${itemsHTML}
        </ul>

        <div class="reservation-panel">
          <div class="reservation-field">
            <label class="reservation-label" for="kit-start-${kit.id}">Inicio</label>
            <input
              id="kit-start-${kit.id}"
              class="reservation-input"
              type="date"
              min="${minDate}"
              value="${startDate}"
              data-kit-start
            />
          </div>
          <div class="reservation-field">
            <label class="reservation-label" for="kit-end-${kit.id}">Fin</label>
            <input
              id="kit-end-${kit.id}"
              class="reservation-input"
              type="date"
              min="${startDate}"
              value="${endDate}"
              data-kit-end
            />
          </div>
        </div>

        <!-- Footer: stock + precio + reservar -->
        <div class="kit-footer">
          <span class="kit-stock ${stockClass}">${stockLabel}</span>
          <div class="kit-price-buy">
            <span class="kit-price" aria-label="Precio: $${kit.price.toFixed(2)}">
              $${kit.price.toFixed(2)}
            </span>
            <button
              class="btn btn-primary"
              data-kit-id="${kit.id}"
              aria-label="Reservar ${kit.name}"
            >
              Reservar
            </button>
          </div>
        </div>
        <p class="action-feedback" data-kit-feedback></p>
      </div>
    </div>
  `;
}

function getDefaultReservationDates() {
  const minDate = toDateInputValue(new Date());
  const startDate = toDateInputValue(addDays(new Date(), 1));
  const endDate = toDateInputValue(addDays(new Date(), 3));

  return { minDate, startDate, endDate };
}

function addDays(baseDate, days) {
  const date = new Date(baseDate);
  date.setDate(date.getDate() + days);
  return date;
}

function toDateInputValue(date) {
  return date.toISOString().split("T")[0];
}
