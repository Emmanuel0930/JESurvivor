// ============================================================
// render.js — Utilidades de renderizado
// Funciones helper para montar y desmontar vistas en el DOM
// ============================================================

// Referencia al contenedor principal de la app
const getRoot = () => document.getElementById("app-root");

/**
 * Limpia el contenedor principal y renderiza nuevo contenido.
 * @param {string|HTMLElement} content — HTML string o nodo DOM
 */
export function renderPage(content) {
  const root = getRoot();
  if (!root) return;

  // Animación de salida suave antes de cambiar página
  root.style.opacity = "0";
  root.style.transform = "translateY(8px)";

  setTimeout(() => {
    if (typeof content === "string") {
      root.innerHTML = content;
    } else {
      root.innerHTML = "";
      root.appendChild(content);
    }

    // Animación de entrada
    root.style.transition = "opacity 0.3s ease, transform 0.3s ease";
    root.style.opacity = "1";
    root.style.transform = "translateY(0)";
  }, 150);
}

/**
 * Muestra un spinner de carga en el contenedor principal.
 * NOTA: Las páginas ya no llaman a esta función directamente.
 * Cada página usa su skeleton específico desde skeleton.js:
 *   showSkeletonForum()        → forumPage.js
 *   showSkeletonStore()        → storePage.js
 *   showSkeletonCourses()      → coursesPage.js
 *   showSkeletonSubscription() → subscriptionPage.js
 * Esta función se mantiene como fallback para usos genéricos.
 */
export function showLoader() {
  const root = getRoot();
  if (!root) return;
  root.innerHTML = `
    <div class="loader-wrap">
      <div class="loader-ring"></div>
      <p class="loader-label">Cargando datos...</p>
    </div>
  `;
}

/**
 * Muestra un mensaje de error genérico.
 * @param {string} message — Mensaje de error opcional
 */
export function showError(message = "Algo salió mal. Intenta de nuevo.") {
  const root = getRoot();
  if (!root) return;
  root.innerHTML = `
    <div class="error-wrap">
      <span class="error-icon">⚠️</span>
      <p class="error-msg">${message}</p>
    </div>
  `;
}

/**
 * Marca el botón de navegación activo en la navbar.
 * @param {string} pageId — ID de la página activa
 */
export function setActiveNav(pageId) {
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.page === pageId);
  });
}
