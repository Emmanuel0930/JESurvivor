// ============================================================
// modal.js — Modales y toasts (reemplazo de alert/confirm)
// ============================================================

let modalRoot = null;
let toastRoot = null;
let lastFocused = null;

export function initModalRoot() {
  modalRoot = document.getElementById("modal-root");
  if (!modalRoot) {
    modalRoot = document.createElement("div");
    modalRoot.id = "modal-root";
    document.body.appendChild(modalRoot);
  }

  toastRoot = document.getElementById("toast-root");
  if (!toastRoot) {
    toastRoot = document.createElement("div");
    toastRoot.id = "toast-root";
    document.body.appendChild(toastRoot);
  }
}

function getModalRoot() {
  return modalRoot || document.getElementById("modal-root");
}

export function closeModal() {
  const root = getModalRoot();
  if (!root) return;
  root.innerHTML = "";
  root.classList.remove("is-open");
  document.body.classList.remove("modal-open");
  if (lastFocused && typeof lastFocused.focus === "function") {
    lastFocused.focus();
  }
}

function trapEscape(handler) {
  const onKey = (e) => {
    if (e.key === "Escape") {
      document.removeEventListener("keydown", onKey);
      handler();
    }
  };
  document.addEventListener("keydown", onKey);
}

function buildFooter(buttons) {
  const wrap = document.createDocumentFragment();
  buttons.forEach((b) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `btn btn-${b.variant || "ghost"}`;
    btn.textContent = b.label;
    btn.addEventListener("click", b.onClick);
    wrap.appendChild(btn);
  });
  return wrap;
}

/**
 * @param {{ title: string, body: string|HTMLElement, footer?: HTMLElement, size?: 'sm'|'md'|'lg', onClose?: () => void }} opts
 */
export function showModal(opts) {
  const root = getModalRoot();
  if (!root) return;

  lastFocused = document.activeElement;
  const size = opts.size || "md";

  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";

  const dialog = document.createElement("div");
  dialog.className = `modal-dialog modal-${size}`;
  dialog.setAttribute("role", "dialog");
  dialog.setAttribute("aria-modal", "true");
  dialog.setAttribute("aria-labelledby", "modal-title");

  const header = document.createElement("div");
  header.className = "modal-header";
  header.innerHTML = `
    <h2 id="modal-title" class="modal-title">${opts.title}</h2>
    <button type="button" class="modal-close" aria-label="Cerrar">✕</button>
  `;

  const bodyEl = document.createElement("div");
  bodyEl.className = "modal-body";
  if (typeof opts.body === "string") {
    bodyEl.innerHTML = opts.body;
  } else if (opts.body) {
    bodyEl.appendChild(opts.body);
  }

  dialog.append(header, bodyEl);

  if (opts.footer) {
    const footer = document.createElement("div");
    footer.className = "modal-footer";
    footer.appendChild(opts.footer);
    dialog.appendChild(footer);
  }

  overlay.appendChild(dialog);
  root.appendChild(overlay);
  root.classList.add("is-open");
  document.body.classList.add("modal-open");

  const close = () => {
    opts.onClose?.();
    closeModal();
  };

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });
  header.querySelector(".modal-close").addEventListener("click", close);
  trapEscape(close);

  const focusable = dialog.querySelector("button, input, textarea, select");
  if (focusable) focusable.focus();
}

export function showAlert({ title = "Aviso", message, type = "info" }) {
  const icon = type === "success" ? "✓" : type === "error" ? "!" : "i";
  showModal({
    title,
    size: "sm",
    body: `
      <div class="modal-alert modal-alert--${type}">
        <span class="modal-alert-icon" aria-hidden="true">${icon}</span>
        <p class="modal-alert-text">${message}</p>
      </div>
    `,
    footer: buildFooter([
      { label: "Entendido", variant: "primary", onClick: () => closeModal() },
    ]),
  });
}

export function showConfirm({
  title = "Confirmar",
  message,
  confirmText = "Confirmar",
  cancelText = "Cancelar",
  variant = "primary",
}) {
  return new Promise((resolve) => {
    showModal({
      title,
      size: "sm",
      body: `<p class="modal-text">${message}</p>`,
      footer: buildFooter([
        {
          label: cancelText,
          variant: "ghost",
          onClick: () => {
            resolve(false);
            closeModal();
          },
        },
        {
          label: confirmText,
          variant,
          onClick: () => {
            resolve(true);
            closeModal();
          },
        },
      ]),
    });
  });
}

export function showToast(message, type = "info", duration = 3800) {
  const root = toastRoot || document.getElementById("toast-root");
  if (!root) return;

  const toast = document.createElement("div");
  toast.className = `toast toast--${type}`;
  toast.setAttribute("role", "status");
  toast.innerHTML = `<span class="toast-msg">${message}</span>`;
  root.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add("is-visible"));

  setTimeout(() => {
    toast.classList.remove("is-visible");
    setTimeout(() => toast.remove(), 300);
  }, duration);
}
