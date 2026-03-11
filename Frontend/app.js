// ============================================================
// app.js — Punto de entrada y enrutador principal de JESurvivor
// ============================================================

import { initNavbar } from "./components/navbar.js";
import { forumPage } from "./pages/forumPage.js";
import { storePage } from "./pages/storePage.js";
import { coursesPage } from "./pages/coursesPage.js";
import { subscriptionPage } from "./pages/subscriptionPage.js";
import { setActiveNav } from "./utils/render.js";

// ─────────────────────────────────────────────
// MAPA DE RUTAS
// Conecta el ID de página con su función de renderizado.
// TODO: En el futuro, estas rutas pueden sincronizarse con
// el historial del navegador usando History API / hash routing.
// ─────────────────────────────────────────────
const ROUTES = {
  forum: forumPage,
  store: storePage,
  courses: coursesPage,
  subscription: subscriptionPage,
};

// Página inicial al cargar la app
const DEFAULT_PAGE = "forum";

/**
 * Navega a una página por su ID.
 * @param {string} pageId — Clave en ROUTES
 */
async function navigate(pageId) {
  const page = ROUTES[pageId];

  if (!page) {
    console.warn(`[router] Página desconocida: "${pageId}". Redirigiendo a inicio.`);
    navigate(DEFAULT_PAGE);
    return;
  }

  // Marcar botón activo en la navbar
  setActiveNav(pageId);

  // Renderizar la página
  await page();
}

// ─────────────────────────────────────────────
// INICIALIZACIÓN
// ─────────────────────────────────────────────
async function init() {
  // Inicializar navbar pasándole la función de navegación
  await initNavbar(navigate);

  // Cargar página inicial
  navigate(DEFAULT_PAGE);
}

// Arrancar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", init);
