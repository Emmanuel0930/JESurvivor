// ============================================================
// api.js — Capa de API simulada (Mock API Layer)
//
// IMPORTANTE PARA EL FUTURO:
// Cuando el backend esté listo, reemplaza cada función con
// un fetch() real al endpoint correspondiente.
// Las funciones mantienen la misma firma (Promise<data>)
// para que el resto del código no necesite cambios.
// ============================================================

import {
  MOCK_POSTS,
  MOCK_KITS,
  MOCK_COURSES,
  MOCK_SUBSCRIPTIONS,
} from "./mockData.js";

// Simula latencia de red para que el mock se comporte
// como una API real (entre 300ms y 700ms)
const fakeDelay = (ms = 500) =>
  new Promise((resolve) => setTimeout(resolve, ms));

// Simula una respuesta de fetch exitosa envolviendo datos en
// un objeto tipo { ok: true, data: [...] }
const mockResponse = (data) => ({ ok: true, data });

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
  await fakeDelay(500);

  // TODO: Reemplazar con:
  // const res = await fetch("/api/store/kits");
  // return res.json();

  return mockResponse(MOCK_KITS);
}

// ─────────────────────────────────────────────
// CURSOS
// Endpoint futuro: GET /api/store/courses
// ─────────────────────────────────────────────
export async function getCourses() {
  await fakeDelay(450);

  // TODO: Reemplazar con:
  // const res = await fetch("/api/store/courses");
  // return res.json();

  return mockResponse(MOCK_COURSES);
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
  await fakeDelay(300);

  // TODO: Reemplazar con:
  // const res = await fetch("/api/users/me", { headers: { Authorization: `Bearer ${token}` } });
  // return res.json();

  // Usuario mock con suscripción activa para mostrar el badge
  return mockResponse({
    id: 1,
    username: "SurvivorX",
    avatar: "🔥",
    subscription: "SURVIVOR PRO",
    badge: "⚡ SURVIVOR",
    isPremium: true,
  });
}
