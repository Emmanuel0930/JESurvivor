// ============================================================
// components/subscription.js — Planes de suscripción
// Renderiza cards de plan y showcase de badges tipo Twitch.
// ============================================================

/**
 * Renderiza la sección completa de suscripciones.
 * @param {Array} plans — Planes desde getSubscriptions()
 * @returns {string} HTML listo para insertar
 */
export function renderSubscription(plans) {
  if (!plans || plans.length === 0) {
    return `
      <div class="error-wrap">
        <span class="error-icon">⚡</span>
        <p class="error-msg">No hay planes disponibles.</p>
      </div>
    `;
  }

  return `
    <!-- Intro hero -->
    <div class="sub-hero">
      <h2 class="sub-hero-title">Elige tu nivel de supervivencia</h2>
      <p class="sub-hero-desc">
        Desbloquea contenido exclusivo, obtén un badge reconocible en el foro
        y accede a la comunidad de supervivientes élite.
      </p>
    </div>

    <!-- Grid de planes -->
    <div class="plans-grid stagger" role="list">
      ${plans.map(buildPlanCard).join("")}
    </div>

    <!-- Showcase de badges -->
    ${buildBadgesShowcase(plans)}
  `;
}

// ── Card de plan ────────────────────────────────────────────
function buildPlanCard(plan) {
  // Clases visuales según el plan
  const isPopular = plan.popular;
  const isGhost   = plan.name === "ELITE GHOST";

  const cardClass = [
    "plan-card",
    isPopular ? "plan-popular" : "",
    isGhost   ? "plan-ghost"   : "",
  ].filter(Boolean).join(" ");

  // Cinta "más popular"
  const ribbon = isPopular
    ? `<div class="plan-popular-ribbon">⚡ Más popular</div>`
    : "";

  // Precio
  const priceBlock = buildPriceBlock(plan);

  // Badge del plan
  const badgeBlock = plan.badge
    ? `<span class="plan-badge-display ${isGhost ? "badge-red" : "badge-amber"}">${plan.badge}</span>`
    : "";

  // Features
  const featClass  = isGhost ? "c-red" : plan.price === 0 ? "c-grey" : "c-amber";
  const featuresHTML = plan.features
    .map((f) => `
      <li class="plan-feat">
        <span class="feat-check ${featClass}" aria-hidden="true">✓</span>
        <span>${f}</span>
      </li>
    `)
    .join("");

  // Botón CTA
  const ctaHTML = buildPlanCTA(plan, isGhost);

  return `
    <div class="${cardClass}" role="listitem" data-plan-id="${plan.id}">
      ${ribbon}

      <div class="plan-header" style="${isPopular ? "margin-top:18px" : ""}">
        <h3 class="plan-name">${plan.name}</h3>
        ${badgeBlock}
        ${priceBlock}
      </div>

      <ul class="plan-features">
        ${featuresHTML}
      </ul>

      <div class="plan-cta">
        ${ctaHTML}
      </div>
    </div>
  `;
}

function buildPriceBlock(plan) {
  if (plan.price === 0) {
    return `
      <div class="plan-price-row">
        <span class="plan-price c-grey">Gratis</span>
      </div>
    `;
  }

  const isGhost    = plan.name === "ELITE GHOST";
  const priceColor = isGhost ? "c-red" : "c-amber";

  return `
    <div class="plan-price-row">
      <span class="plan-price ${priceColor}">$${plan.price.toFixed(2)}</span>
      <span class="plan-period">/ ${plan.period}</span>
    </div>
  `;
}

function buildPlanCTA(plan, isGhost) {
  if (plan.price === 0) {
    return `<button class="btn btn-locked" disabled>Plan actual</button>`;
  }

  // TODO: Conectar con POST /api/store/subscriptions y Stripe / PayPal
  // Pasar plan.id al checkout para identificar el tier
  const btnClass = isGhost ? "btn btn-red-solid" : "btn btn-primary";
  const icon     = plan.badgeIcon || "→";

  return `
    <button
      class="${btnClass}"
      data-plan-id="${plan.id}"
      aria-label="Suscribirse al plan ${plan.name}"
    >
      Suscribirse ${icon}
    </button>
  `;
}

// ── Showcase de badges ──────────────────────────────────────
function buildBadgesShowcase(plans) {
  const badgePlans = plans.filter((p) => p.badge);
  if (!badgePlans.length) return "";

  const chipsHTML = badgePlans.map((p) => {
    const isGhost   = p.name === "ELITE GHOST";
    const chipClass = isGhost ? "chip-red" : "chip-amber";
    const nameClass = isGhost ? "c-red"    : "c-amber";

    return `
      <div class="badge-chip ${chipClass}" role="img" aria-label="Badge ${p.badge}">
        <span class="badge-chip-icon" aria-hidden="true">${p.badgeIcon}</span>
        <div class="badge-chip-info">
          <span class="badge-chip-name ${nameClass}">${p.badge}</span>
          <span class="badge-chip-plan">Plan ${p.name}</span>
        </div>
      </div>
    `;
  }).join("");

  return `
    <div class="badges-showcase">
      <p class="badges-title">// Badges exclusivos del foro</p>
      <div class="badges-row">${chipsHTML}</div>
    </div>
  `;
}
