// ============================================================
// api.js — Capa de API simulada (Mock API Layer)
//
// IMPORTANTE PARA EL FUTURO:
// Cuando el backend esté listo, reemplaza cada función con
// un fetch() real al endpoint correspondiente.
// Las funciones mantienen la misma firma (Promise<data>)
// para que el resto del código no necesite cambios.
// ============================================================

import { MOCK_POSTS, MOCK_SUBSCRIPTIONS } from "./mockData.js";

const API_BASE = "/api";

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

// Simula latencia de red para que el mock se comporte
// como una API real (entre 300ms y 700ms)
const fakeDelay = (ms = 500) =>
  new Promise((resolve) => setTimeout(resolve, ms));

// Simula una respuesta de fetch exitosa envolviendo datos en
// un objeto tipo { ok: true, data: [...] }
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

  const res = await fetch(`${API_BASE}${path}`, {
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
  if (currentUserCache) {
    return currentUserCache;
  }

  const user = await apiRequest("/usuario/actual/");
  currentUserCache = mapCurrentUser(user);
  return currentUserCache;
}

async function getUserHeaders() {
  const user = await ensureCurrentUser();
  return {
    "X-User-Id": String(user.backendId),
  };
}

// ─────────────────────────────────────────────
// POSTS DEL FORO
// Endpoint futuro: GET /api/posts
// ─────────────────────────────────────────────
export async function getPosts() {
  await fakeDelay(400);

  // TODO: Reemplazar con fetch real:
  // const res = await fetch("/api/posts");
  // if (!res.ok) throw new Error("Error al cargar posts");
  // return res.json();

  return mockResponse(MOCK_POSTS);
}

// ─────────────────────────────────────────────
// POST INDIVIDUAL
// Endpoint futuro: GET /api/posts/:id
// ─────────────────────────────────────────────
export async function getPostById(id) {
  await fakeDelay(300);

  // TODO: Reemplazar con:
  // const res = await fetch(`/api/posts/${id}`);
  // return res.json();

  const post = MOCK_POSTS.find((p) => p.id === id);
  if (!post) return { ok: false, error: "Post no encontrado" };
  return mockResponse(post);
}

// ─────────────────────────────────────────────
// KITS DE LA TIENDA
// Endpoint futuro: GET /api/store/kits
// ─────────────────────────────────────────────
export async function getKits() {
  try {
    const kits = await apiRequest("/kit/");
    return mockResponse(kits.map(mapKit));
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

// ─────────────────────────────────────────────
// CURSOS
// Endpoint futuro: GET /api/store/courses
// ─────────────────────────────────────────────
export async function getCourses() {
  try {
    const courses = await apiRequest("/curso/");
    return mockResponse(courses.map(mapCourse));
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

// ─────────────────────────────────────────────
// SUSCRIPCIONES
// Endpoint futuro: GET /api/store/subscriptions
// ─────────────────────────────────────────────
export async function getSubscriptions() {
  await fakeDelay(350);

  // TODO: Reemplazar con:
  // const res = await fetch("/api/store/subscriptions");
  // return res.json();

  return mockResponse(MOCK_SUBSCRIPTIONS);
}

// ─────────────────────────────────────────────
// USUARIO ACTUAL (simulado)
// Endpoint futuro: GET /api/users/me
// ─────────────────────────────────────────────
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
      body: {
        kit_id: Number(kitId),
        inicio,
        fin,
      },
    });

    return mockResponse(data);
  } catch (error) {
    return { ok: false, error: error.message };
  }
}
