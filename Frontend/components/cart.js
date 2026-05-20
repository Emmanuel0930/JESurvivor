// ============================================================
// cart.js — Carrito de compras (cursos + reservas de kits)
// ============================================================

import { buyCourse, reserveKit } from "../api/api.js";
import { closeModal, showConfirm, showModal, showToast } from "../utils/modal.js";

const STORAGE_KEY = "jesurvivor_cart_v1";
const listeners = new Set();

function loadCart() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveCart(items) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  notify();
}

function notify() {
  const count = getCartCount();
  listeners.forEach((fn) => fn(count));
  updateBadge();
  renderDrawerContent();
}

export function onCartChange(fn) {
  listeners.add(fn);
  fn(getCartCount());
  return () => listeners.delete(fn);
}

export function getCartItems() {
  return loadCart();
}

export function getCartCount() {
  return loadCart().length;
}

export function getCartTotal() {
  return loadCart().reduce((sum, item) => sum + (Number(item.price) || 0), 0);
}

function itemKey(item) {
  if (item.type === "kit") {
    return `kit-${item.id}-${item.inicio}-${item.fin}`;
  }
  return `course-${item.id}`;
}

export function addToCart(item) {
  const items = loadCart();
  const key = itemKey(item);
  if (items.some((i) => itemKey(i) === key)) {
    showToast("Este artículo ya está en el carrito.", "info");
    return false;
  }
  items.push({ ...item, key });
  saveCart(items);
  showToast("Añadido al carrito.", "success");
  return true;
}

export function removeFromCart(key) {
  saveCart(loadCart().filter((i) => i.key !== key));
  showToast("Eliminado del carrito.", "info");
}

export function clearCart() {
  saveCart([]);
}

function formatPrice(n) {
  return `$${Number(n).toFixed(2)}`;
}

function ensureCartDOM() {
  if (document.getElementById("cart-drawer")) return;

  const drawer = document.createElement("aside");
  drawer.id = "cart-drawer";
  drawer.className = "cart-drawer";
  drawer.setAttribute("aria-label", "Carrito de compras");
  drawer.innerHTML = `
    <div class="cart-backdrop" data-cart-close></div>
    <div class="cart-panel">
      <header class="cart-header">
        <div>
          <p class="cart-eyebrow">Tu equipo</p>
          <h2 class="cart-title">Carrito</h2>
        </div>
        <button type="button" class="cart-close" data-cart-close aria-label="Cerrar carrito">✕</button>
      </header>
      <div class="cart-body" id="cart-body"></div>
      <footer class="cart-footer" id="cart-footer"></footer>
    </div>
  `;

  document.body.appendChild(drawer);

  drawer.querySelectorAll("[data-cart-close]").forEach((el) => {
    el.addEventListener("click", closeCart);
  });
}

function updateBadge() {
  const badge = document.getElementById("cart-badge");
  if (!badge) return;
  const count = getCartCount();
  badge.textContent = String(count);
  badge.classList.toggle("is-hidden", count === 0);
}

export function openCart() {
  ensureCartDOM();
  renderDrawerContent();
  document.getElementById("cart-drawer")?.classList.add("is-open");
  document.body.classList.add("cart-open");
}

export function closeCart() {
  document.getElementById("cart-drawer")?.classList.remove("is-open");
  document.body.classList.remove("cart-open");
}

function modalFooterButton(label, onClick) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "btn btn-primary";
  btn.textContent = label;
  btn.addEventListener("click", onClick);
  return btn;
}

function renderDrawerContent() {
  const body = document.getElementById("cart-body");
  const footer = document.getElementById("cart-footer");
  if (!body || !footer) return;

  const items = loadCart();

  if (items.length === 0) {
    body.innerHTML = `
      <div class="cart-empty">
        <span class="cart-empty-icon" aria-hidden="true">🛒</span>
        <p>Tu carrito está vacío.</p>
        <p class="cart-empty-hint">Añade cursos o reserva kits desde la tienda.</p>
      </div>
    `;
    footer.innerHTML = "";
    return;
  }

  body.innerHTML = items
    .map(
      (item) => `
    <article class="cart-item" data-cart-key="${item.key}">
      <div class="cart-item-icon" aria-hidden="true">${item.image || "📦"}</div>
      <div class="cart-item-info">
        <span class="cart-item-type">${item.type === "kit" ? "Reserva kit" : "Curso"}</span>
        <h3 class="cart-item-name">${item.name || item.title}</h3>
        ${
          item.type === "kit"
            ? `<p class="cart-item-meta">${item.inicio} → ${item.fin}</p>`
            : ""
        }
        <p class="cart-item-price">${formatPrice(item.price)}</p>
      </div>
      <button type="button" class="cart-item-remove" data-remove="${item.key}" aria-label="Quitar">✕</button>
    </article>
  `
    )
    .join("");

  footer.innerHTML = `
    <div class="cart-total-row">
      <span>Total estimado</span>
      <strong>${formatPrice(getCartTotal())}</strong>
    </div>
    <button type="button" class="btn btn-primary cart-checkout-btn" id="cart-checkout-btn">
      Finalizar compra
    </button>
    <button type="button" class="btn btn-ghost cart-clear-btn" id="cart-clear-btn">
      Vaciar carrito
    </button>
  `;

  body.querySelectorAll("[data-remove]").forEach((btn) => {
    btn.addEventListener("click", () => removeFromCart(btn.dataset.remove));
  });

  document.getElementById("cart-checkout-btn")?.addEventListener("click", checkoutCart);
  document.getElementById("cart-clear-btn")?.addEventListener("click", async () => {
    const ok = await showConfirm({
      title: "Vaciar carrito",
      message: "¿Seguro que quieres eliminar todos los artículos?",
      confirmText: "Vaciar",
      variant: "danger",
    });
    if (ok) {
      clearCart();
      showToast("Carrito vaciado.", "info");
    }
  });
}

async function checkoutCart() {
  const items = loadCart();
  if (!items.length) return;

  const ok = await showConfirm({
    title: "Confirmar pedido",
    message: `Procesar ${items.length} artículo(s) por un total de ${formatPrice(getCartTotal())}?`,
    confirmText: "Confirmar",
  });
  if (!ok) return;

  const btn = document.getElementById("cart-checkout-btn");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "Procesando...";
  }

  const results = { ok: [], fail: [] };

  for (const item of items) {
    if (item.type === "course") {
      const res = await buyCourse(item.id);
      if (res.ok) results.ok.push(item);
      else results.fail.push({ item, error: res.error });
    } else if (item.type === "kit") {
      const res = await reserveKit(item.id, item.inicio, item.fin);
      if (res.ok) results.ok.push(item);
      else results.fail.push({ item, error: res.error });
    }
  }

  results.ok.forEach((item) => removeFromCart(item.key));

  if (btn) {
    btn.disabled = false;
    btn.textContent = "Finalizar compra";
  }

  if (results.fail.length === 0) {
    showModal({
      title: "Pedido completado",
      size: "sm",
      body: `
        <div class="modal-alert modal-alert--success">
          <span class="modal-alert-icon">✓</span>
          <p class="modal-alert-text">Se procesaron ${results.ok.length} artículo(s) correctamente.</p>
        </div>
      `,
      footer: modalFooterButton("Cerrar", () => {
        closeModal();
        closeCart();
      }),
    });
    return;
  }

  const failList = results.fail
    .map((f) => `<li><strong>${f.item.name || f.item.title}</strong>: ${f.error}</li>`)
    .join("");

  showModal({
    title: "Pedido parcial",
    size: "md",
    body: `
      <p class="modal-text">${results.ok.length} correcto(s), ${results.fail.length} con error:</p>
      <ul class="modal-list">${failList}</ul>
    `,
    footer: modalFooterButton("Entendido", () => closeModal()),
  });
}

export function initCart() {
  ensureCartDOM();
  renderDrawerContent();
  updateBadge();
}
