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

        <!-- Footer: stock + precio + comprar -->
        <div class="kit-footer">
          <span class="kit-stock ${stockClass}">${stockLabel}</span>
          <div class="kit-price-buy">
            <span class="kit-price" aria-label="Precio: $${kit.price.toFixed(2)}">
              $${kit.price.toFixed(2)}
            </span>
            <!--
              TODO: onClick conectar con POST /api/store/cart
              o redirigir a pasarela de pago con kit.id
            -->
            <button
              class="btn btn-primary"
              data-kit-id="${kit.id}"
              aria-label="Comprar ${kit.name}"
            >
              Comprar
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}
