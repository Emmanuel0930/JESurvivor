// ============================================================
// api.js — Capa de API de JESurvivor
// Entregable 2: Nuevas funciones para endpoints de integración.
// ============================================================

import { MOCK_POSTS, MOCK_SUBSCRIPTIONS } from "./mockData.js";

function resolveApiBase() {
  if (typeof window !== "undefined" && window.__API_BASE__) {
    return window.__API_BASE__;
  }
  if (typeof window !== "undefined" && window.location) {
    const hostname = window.location.hostname;
    const port = window.location.port;
    const isLocal =
      hostname === "127.0.0.1" || hostname === "localhost" || hostname === "::1";
    const DEV_STATIC_PORTS = ["5173", "5500", "5501", "3000", "4200", "8080"];
    if (isLocal && DEV_STATIC_PORTS.indexOf(port) !== -1) {
      return "http://127.0.0.1:8000/api";
    }
  }
  return "/api";
}

const COURSE_LEVEL_LABELS = {
  basico: "Principiante",
  intermedio: "Intermedio",
  avanzado: "Avanzado",
};

const KIT_ICONS = {
  montana: "🏔️",
  selva: "🌿",
  urbano: "🏙️",
  desierto: "🏜️",
  nieve: "❄️",
};

const USER_AVATARS = {
  basico: "🧭",
  intermedio: "🔥",
  avanzado: "⚔️",
};

let currentUserCache = null;

const fakeDelay = (ms = 500) => new Promise((resolve) => setTimeout(resolve, ms));
const mockResponse = (data) => ({ ok: true, data });

async function parseJsonSafely(res) {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

async function apiRequest(path, options = {}) {
  const { method = "GET", body, headers = {} } = options;
  const apiBase = resolveApiBase();
  const res = await fetch(`${apiBase}${path}`, {
    method,
    headers: {
      ...(body ? { "Content-Type": "application/json" } : {}),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await parseJsonSafely(res);
  if (!res.ok) {
    throw new Error(data?.error || "No se pudo completar la solicitud.");
  }
  return data;
}

function mapCurrentUser(user) {
  const level = user.nivel_experiencia || "basico";
  return {
    id: user.id,
    backendId: user.id,
    username: user.nombre,
    avatar: USER_AVATARS[level] || "🧭",
    subscription: "FREE",
    badge: level === "avanzado" ? "OPERADOR AVANZADO" : "FREE",
    isPremium: false,
  };
}

function mapCourse(course) {
  const level = COURSE_LEVEL_LABELS[course.nivel_recomendado] || "Principiante";
  return {
    id: course.id,
    title: course.nombre,
    instructor: "Equipo JESurvivor",
    duration: `${course.duracion_horas} horas`,
    level,
    price: Number(course.precio),
    image: level === "Avanzado" ? "⚔️" : level === "Intermedio" ? "🔥" : "🧭",
    description: course.descripcion,
    students: null,
    rating: null,
    isPremium: false,
    active: course.activo,
  };
}

function mapKit(kit) {
  return {
    id: kit.id,
    name: kit.nombre,
    price: Number(kit.precio),
    image: KIT_ICONS[kit.entorno] || "🎒",
    description: kit.descripcion,
    items: Array.isArray(kit.lista_items) ? kit.lista_items : [],
    stock: kit.stock,
    badge: kit.stock <= 2 ? "LIMITADO" : null,
    level: kit.nivel_recomendado,
    environment: kit.entorno,
  };
}

async function ensureCurrentUser() {
  if (currentUserCache) return currentUserCache;
  const user = await apiRequest("/usuario/actual/");
  currentUserCache = mapCurrentUser(user);
  return currentUserCache;
}

async function getUserHeaders() {
  const user = await ensureCurrentUser();
  return { "X-User-Id": String(user.backendId) };
}

// ─── Existentes ───────────────────────────────────────────────

export async function getPosts() {
  await fakeDelay(400);
  return mockResponse(MOCK_POSTS);
}

export async function getPostById(id) {
  await fakeDelay(300);
  const post = MOCK_POSTS.find((p) => p.id === id);
  if (!post) return { ok: false, error: "Post no encontrado" };
  return mockResponse(post);
}

export async function getKits() {
  try {
    const kits = await apiRequest("/kit/");
    return mockResponse(kits.map(mapKit));
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

export async function getCourses() {
  try {
    const courses = await apiRequest("/curso/");
    return mockResponse(courses.map(mapCourse));
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

export async function getSubscriptions() {
  await fakeDelay(350);
  return mockResponse(MOCK_SUBSCRIPTIONS);
}

export async function getCurrentUser() {
  try {
    const user = await ensureCurrentUser();
    return mockResponse(user);
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

export async function buyCourse(courseId) {
  try {
    const headers = await getUserHeaders();
    const data = await apiRequest("/curso/comprar/", {
      method: "POST",
      headers,
      body: { curso_id: Number(courseId) },
    });
    return mockResponse(data);
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

export async function reserveKit(kitId, inicio, fin) {
  try {
    const headers = await getUserHeaders();
    const data = await apiRequest("/reserva/crear/", {
      method: "POST",
      headers,
      body: { kit_id: Number(kitId), inicio, fin },
    });
    return mockResponse(data);
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

// ─── NUEVAS — Entregable 2 ────────────────────────────────────

/**
 * GET /api/sistema/info/
 * Información del sistema expuesta para el equipo aliado.
 */
export async function getSistemaInfo() {
  try {
    const data = await apiRequest("/sistema/info/");
    return mockResponse(data);
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

/**
 * GET /api/clima/?entorno=X
 * Adapter Pattern sobre Open-Meteo. Entornos: montana, selva, urbano, desierto, nieve
 */
export async function getClima(entorno = "urbano") {
  try {
    const data = await apiRequest(`/clima/?entorno=${entorno}`);
    return mockResponse(data);
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

/**
 * GET /api/aliado/
 * Consumo del servicio del equipo aliado.
 */
export async function getAliado() {
  try {
    const data = await apiRequest("/aliado/");
    return mockResponse(data);
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

/**
 * POST /api/tareas/reporte/
 * Dispara una tarea asíncrona en Celery + Redis.
 */
export async function dispararReporte() {
  try {
    const data = await apiRequest("/tareas/reporte/", { method: "POST" });
    return mockResponse(data);
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

/**
 * GET /api/tareas/estado/<task_id>/
 * Consulta el estado y resultado de una tarea Celery.
 */
export async function getEstadoTarea(taskId) {
  try {
    const data = await apiRequest(`/tareas/estado/${taskId}/`);
    return mockResponse(data);
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

/**
 * GET /api/v2/reservas/health
 * Health check del microservicio Flask (Strangler Pattern).
 */
export async function getFlaskHealth() {
  try {
    const base = resolveApiBase().replace("/api", "");
    const res = await fetch(`${base}/api/v2/reservas/health`);
    const data = await parseJsonSafely(res);
    if (!res.ok) throw new Error("Flask no disponible");
    return mockResponse(data);
  } catch (error) {
    return { ok: false, error: error.message };
  }
}