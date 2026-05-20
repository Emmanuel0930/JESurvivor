// ============================================================
// app.js — Punto de entrada y enrutador principal de JESurvivor
// Entregable 2: Agrega ruta "integration" para el panel de integraciones.
// ============================================================

import { initCart } from "./components/cart.js";
import { initNavbar } from "./components/navbar.js";
import { initModalRoot } from "./utils/modal.js";
import { forumPage } from "./pages/forumPage.js";
import { storePage } from "./pages/storePage.js";
import { coursesPage } from "./pages/coursesPage.js";
import { subscriptionPage } from "./pages/subscriptionPage.js";
import { integrationPage } from "./pages/integrationPage.js";
import { setActiveNav } from "./utils/render.js";

const ROUTES = {
  forum: forumPage,
  store: storePage,
  courses: coursesPage,
  subscription: subscriptionPage,
  integration: integrationPage,   // ← nuevo
};

const DEFAULT_PAGE = "forum";

async function navigate(pageId) {
  const page = ROUTES[pageId];
  if (!page) {
    console.warn(`[router] Página desconocida: "${pageId}". Redirigiendo a inicio.`);
    navigate(DEFAULT_PAGE);
    return;
  }
  setActiveNav(pageId);
  await page();
}

async function init() {
  initModalRoot();
  initCart();
  await initNavbar(navigate);
  navigate(DEFAULT_PAGE);
}

document.addEventListener("DOMContentLoaded", init);