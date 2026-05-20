// ============================================================
// api.js — Capa de API de JESurvivor (llamadas reales al backend)
// ============================================================

import { SUBSCRIPTION_PLANS } from "./subscriptionPlans.js";

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

const POST_AVATARS = {
  basico: "🧭",
  intermedio: "🔥",
  avanzado: "⚔️",
};

let currentUserCache = null;

const ok = (data) => ({ ok: true, data });
const fail = (error, status = null) => ({ ok: false, error, status });

async function parseJsonSafely(res) {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function extractErrorMessage(data, status) {
  if (!data) return `Error del servidor (${status})`;
  if (typeof data.error === "string") return data.error;
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.non_field_errors)) return data.non_field_errors.join(" ");

  const parts = [];
  for (const [key, value] of Object.entries(data)) {
    if (Array.isArray(value)) parts.push(`${key}: ${value.join(", ")}`);
    else if (typeof value === "string") parts.push(value);
  }
  return parts.length ? parts.join(" ") : `Error del servidor (${status})`;
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
    const message = extractErrorMessage(data, res.status);
    const err = new Error(message);
    err.status = res.status;
    err.data = data;
    throw err;
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

function mapPost(post) {
  const level = post.autor_nivel || "basico";
  const created = post.creado_en || "";
  const dateStr = typeof created === "string" ? created.split("T")[0] : created;

  return {
    id: post.id,
    title: post.titulo,
    author: post.autor_nombre,
    avatar: POST_AVATARS[level] || "🧭",
    content: post.contenido,
    tags: Array.isArray(post.tags) ? post.tags : [],
    likes: post.likes ?? 0,
    comments: post.comentarios_count ?? 0,
    date: dateStr,
    isPremium: Boolean(post.es_premium),
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

// ─── Foro ─────────────────────────────────────────────────────

export async function getPosts() {
  try {
    const posts = await apiRequest("/posts/");
    return ok(posts.map(mapPost));
  } catch (error) {
    return fail(error.message, error.status);
  }
}

export async function getPostById(id) {
  try {
    const posts = await apiRequest("/posts/");
    const post = posts.map(mapPost).find((p) => p.id === Number(id));
    if (!post) return fail("Post no encontrado", 404);
    return ok(post);
  } catch (error) {
    return fail(error.message, error.status);
  }
}

export async function createPost({ title, content, tags = [] }) {
  try {
    const headers = await getUserHeaders();
    const data = await apiRequest("/posts/crear/", {
      method: "POST",
      headers,
      body: {
        titulo: title,
        contenido: content,
        tags,
      },
    });
    return ok(data);
  } catch (error) {
    return fail(error.message, error.status);
  }
}

// ─── Tienda y cursos ──────────────────────────────────────────

export async function getKits() {
  try {
    const kits = await apiRequest("/kit/");
    return ok(kits.map(mapKit));
  } catch (error) {
    return fail(error.message, error.status);
  }
}

export async function getCourses() {
  try {
    const courses = await apiRequest("/curso/");
    return ok(courses.map(mapCourse));
  } catch (error) {
    return fail(error.message, error.status);
  }
}

export async function getSubscriptions() {
  return ok(SUBSCRIPTION_PLANS);
}

export async function getCurrentUser() {
  try {
    const user = await ensureCurrentUser();
    return ok(user);
  } catch (error) {
    return fail(error.message, error.status);
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
    return ok(data);
  } catch (error) {
    return fail(error.message, error.status);
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
    return ok(data);
  } catch (error) {
    return fail(error.message, error.status);
  }
}

// ─── Integraciones (Entregable 2) ─────────────────────────────

export async function getSistemaInfo() {
  try {
    const data = await apiRequest("/sistema/info/");
    return ok(data);
  } catch (error) {
    return fail(error.message, error.status);
  }
}

export async function getClima(entorno = "urbano") {
  try {
    const data = await apiRequest(`/clima/?entorno=${entorno}`);
    return ok(data);
  } catch (error) {
    return fail(error.message, error.status);
  }
}

export async function getAliado() {
  try {
    const data = await apiRequest("/aliado/");
    return ok(data);
  } catch (error) {
    return fail(error.message, error.status);
  }
}

export async function dispararReporte() {
  try {
    const data = await apiRequest("/tareas/reporte/", { method: "POST" });
    return ok(data);
  } catch (error) {
    return fail(error.message, error.status);
  }
}

export async function getEstadoTarea(taskId) {
  try {
    const data = await apiRequest(`/tareas/estado/${taskId}/`);
    return ok(data);
  } catch (error) {
    return fail(error.message, error.status);
  }
}

export async function getFlaskHealth() {
  try {
    const base = resolveApiBase().replace("/api", "");
    const res = await fetch(`${base}/api/v2/reservas/health`);
    const data = await parseJsonSafely(res);
    if (!res.ok) throw new Error("Flask no disponible");
    return ok(data);
  } catch (error) {
    return fail(error.message);
  }
}

export async function getBiblioteca(tema = "supervivencia") {
  try {
    const data = await apiRequest(`/biblioteca/?tema=${tema}`);
    return ok(data);
  } catch (error) {
    return fail(error.message, error.status);
  }
}
