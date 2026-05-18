// ============================================================
// pages/integrationPage.js — Panel de Integraciones (E2)
// FIX: waitFor() espera a que el DOM esté listo antes de pintar.
// ============================================================

import { getSistemaInfo, getClima, getAliado, dispararReporte, getFlaskHealth } from "../api/api.js";
import { renderPage } from "../utils/render.js";

const ENTORNOS = [
  { id: "urbano",   label: "Urbano",   icon: "🏙️" },
  { id: "montana",  label: "Montaña",  icon: "🏔️" },
  { id: "selva",    label: "Selva",    icon: "🌿" },
  { id: "desierto", label: "Desierto", icon: "🏜️" },
  { id: "nieve",    label: "Nieve",    icon: "❄️" },
];

// Espera hasta 3s a que un elemento exista en el DOM
function waitFor(id) {
  return new Promise((resolve) => {
    const start = Date.now();
    const tick = () => {
      const el = document.getElementById(id);
      if (el) return resolve(el);
      if (Date.now() - start > 3000) return resolve(null);
      requestAnimationFrame(tick);
    };
    tick();
  });
}

export async function integrationPage() {
  renderPage(buildShell());

  // CRÍTICO: esperar a que renderPage monte el HTML (tiene setTimeout 150ms)
  await waitFor("panel-sistema");

  const [sistemaRes, aliadoRes, flaskRes] = await Promise.all([
    getSistemaInfo(),
    getAliado(),
    getFlaskHealth(),
  ]);

  renderSistema(sistemaRes);
  renderAliado(aliadoRes);
  renderFlask(flaskRes);

  await loadClima("urbano");
  registerClimaEvents();
  registerReporteEvent();
}

function buildShell() {
  return `
    <section class="page-enter integ-page" aria-label="Panel de integraciones">
      <div class="page-header">
        <p class="page-eyebrow">Entregable 2</p>
        <h1 class="page-title">Panel de <em>Integraciones</em></h1>
        <p class="page-desc">Monitoreo en tiempo real de todos los servicios del ecosistema JESurvivor. Microservicios, APIs externas, comunicación asíncrona y servicios aliados.</p>
      </div>

      <div class="integ-row integ-row--2col">
        <div class="integ-card" id="panel-sistema">
          <div class="integ-card-header">
            <div class="integ-card-icon amber">⚙️</div>
            <div><div class="integ-card-title">Estado del Sistema</div><div class="integ-card-subtitle">GET /api/sistema/info/</div></div>
            <div class="integ-badge integ-badge--loading" id="badge-sistema"><span class="badge-dot"></span>CARGANDO</div>
          </div>
          <div class="integ-card-body" id="body-sistema">${buildPulse(4)}</div>
        </div>
        <div class="integ-card" id="panel-flask">
          <div class="integ-card-header">
            <div class="integ-card-icon green">🐍</div>
            <div><div class="integ-card-title">Microservicio Flask</div><div class="integ-card-subtitle">GET /api/v2/reservas/health</div></div>
            <div class="integ-badge integ-badge--loading" id="badge-flask"><span class="badge-dot"></span>CARGANDO</div>
          </div>
          <div class="integ-card-body" id="body-flask">${buildPulse(3)}</div>
        </div>
      </div>

      <div class="integ-card integ-card--full" id="panel-clima">
        <div class="integ-card-header">
          <div class="integ-card-icon amber">🌤️</div>
          <div><div class="integ-card-title">Clima para Supervivencia</div><div class="integ-card-subtitle">GET /api/clima/?entorno=X · Adapter Pattern → Open-Meteo</div></div>
          <div class="integ-badge integ-badge--ok" id="badge-clima"><span class="badge-dot"></span>LIVE</div>
        </div>
        <div class="clima-tabs" id="clima-tabs">
          ${ENTORNOS.map((e) => `<button class="clima-tab ${e.id === "urbano" ? "active" : ""}" data-entorno="${e.id}"><span>${e.icon}</span><span>${e.label}</span></button>`).join("")}
        </div>
        <div class="integ-card-body" id="body-clima">${buildPulse(3)}</div>
      </div>

      <div class="integ-row integ-row--2col">
        <div class="integ-card" id="panel-aliado">
          <div class="integ-card-header">
            <div class="integ-card-icon amber">🤝</div>
            <div><div class="integ-card-title">Servicio Aliado</div><div class="integ-card-subtitle">GET /api/aliado/</div></div>
            <div class="integ-badge integ-badge--loading" id="badge-aliado"><span class="badge-dot"></span>CARGANDO</div>
          </div>
          <div class="integ-card-body" id="body-aliado">${buildPulse(3)}</div>
        </div>
        <div class="integ-card" id="panel-celery">
          <div class="integ-card-header">
            <div class="integ-card-icon red">⚡</div>
            <div><div class="integ-card-title">Tarea Asíncrona</div><div class="integ-card-subtitle">POST /api/tareas/reporte/ · Redis + Celery</div></div>
            <div class="integ-badge integ-badge--idle" id="badge-celery"><span class="badge-dot"></span>LISTO</div>
          </div>
          <div class="integ-card-body" id="body-celery">
            <p class="integ-desc">Dispara un reporte del sistema en <strong>background</strong> usando Celery + Redis. La respuesta es inmediata — la tarea se ejecuta sin bloquear el servidor.</p>
            <div class="celery-arch">
              <span class="arch-step">Django</span>
              <span class="arch-arrow">→</span>
              <span class="arch-step arch-step--amber">Redis</span>
              <span class="arch-arrow">→</span>
              <span class="arch-step">Worker</span>
            </div>
            <button class="btn btn-primary integ-btn" id="btn-reporte">⚡ Disparar Reporte</button>
            <div class="celery-result" id="celery-result" style="display:none"></div>
          </div>
        </div>
      </div>
    </section>
  `;
}

function renderSistema(res) {
  const badge = document.getElementById("badge-sistema");
  const body  = document.getElementById("body-sistema");
  if (!badge || !body) return;
  if (!res.ok) {
    badge.className = "integ-badge integ-badge--error";
    badge.innerHTML = `<span class="badge-dot"></span>ERROR`;
    body.innerHTML  = buildError(res.error);
    return;
  }
  const d = res.data, s = d.estadisticas || {};
  badge.className = "integ-badge integ-badge--ok";
  badge.innerHTML = `<span class="badge-dot"></span>ONLINE`;
  body.innerHTML = `
    <div class="sistema-stats">
      ${buildStat("👤", s.usuarios_registrados ?? "—", "Usuarios")}
      ${buildStat("🎒", s.kits_disponibles     ?? "—", "Kits")}
      ${buildStat("📅", s.reservas_activas     ?? "—", "Reservas activas")}
      ${buildStat("📚", s.cursos_activos       ?? "—", "Cursos")}
    </div>
    <div class="integ-meta-row">
      ${buildMeta("Versión", d.version || "—", true)}
      ${buildMeta("Gateway", d.arquitectura?.gateway || "Nginx", false)}
      ${buildMeta("Broker",  d.arquitectura?.broker_asincrono || "Redis+Celery", false)}
      ${buildMeta("Infra",   d.arquitectura?.infra || "Docker+EC2", false)}
    </div>`;
}

async function loadClima(entorno) {
  const body = document.getElementById("body-clima");
  if (!body) return;
  body.innerHTML = buildPulse(3);
  const res = await getClima(entorno);
  if (!res.ok) { body.innerHTML = buildError(res.error); return; }
  const d = res.data, c = d.clima || {};
  const icons = { sunny:"☀️", cloudy:"⛅", rainy:"🌧️", stormy:"⛈️", snowy:"❄️", foggy:"🌫️" };
  const condIcon = icons[c.condicion] || "🌡️";
  const alertHtml = d.alerta_supervivencia
    ? `<div class="clima-alert"><span>⚠️</span>${d.alerta_supervivencia}</div>` : "";
  body.innerHTML = `
    <div class="clima-main">
      <div class="clima-weather">
        <div class="clima-icon">${condIcon}</div>
        <div class="clima-temp">${c.temperatura_c != null ? c.temperatura_c + "°C" : "—"}</div>
        <div class="clima-desc">${c.descripcion || "Sin datos"}</div>
        <div class="clima-lugar">${d.lugar_referencia || ""}</div>
      </div>
      <div class="clima-stats">
        ${buildClimaRow("💧","Humedad",   c.humedad_pct         != null ? c.humedad_pct         + "%" : "—")}
        ${buildClimaRow("💨","Viento",    c.viento_kmh          != null ? c.viento_kmh          + " km/h" : "—")}
        ${buildClimaRow("🌡️","Sensación", c.sensacion_termica_c != null ? c.sensacion_termica_c + "°C" : "—")}
        ${buildClimaRow("🌧️","Precipit.", c.precipitacion_mm    != null ? c.precipitacion_mm    + " mm" : "—")}
      </div>
    </div>
    ${alertHtml}
    <div class="clima-kit-rec">
      <span class="klimeta-label">// KIT RECOMENDADO</span>
      <span class="klimeta-value">${d.recomendacion_kit || "—"}</span>
    </div>
    <div class="integ-source">Fuente: ${c.fuente || "Open-Meteo"} · Adapter Pattern (DIP)</div>`;
}

function registerClimaEvents() {
  const tabs = document.getElementById("clima-tabs");
  if (!tabs) return;
  tabs.addEventListener("click", async (e) => {
    const btn = e.target.closest(".clima-tab");
    if (!btn) return;
    tabs.querySelectorAll(".clima-tab").forEach((t) => t.classList.remove("active"));
    btn.classList.add("active");
    await loadClima(btn.dataset.entorno);
  });
}

function renderAliado(res) {
  const badge = document.getElementById("badge-aliado");
  const body  = document.getElementById("body-aliado");
  if (!badge || !body) return;
  if (!res.ok) {
    badge.className = "integ-badge integ-badge--error";
    badge.innerHTML = `<span class="badge-dot"></span>ERROR`;
    body.innerHTML  = buildError(res.error);
    return;
  }
  const d = res.data;
  if (d.estado === "pendiente_configuracion") {
    badge.className = "integ-badge integ-badge--idle";
    badge.innerHTML = `<span class="badge-dot"></span>PENDIENTE`;
    body.innerHTML = `
      <div class="aliado-pending">
        <div class="aliado-pending-icon">🔗</div>
        <p class="aliado-pending-title">URL del aliado por configurar</p>
        <p class="aliado-pending-desc">Cuando el equipo aliado te pase su IP de EC2, actualiza <code>ALIADO_API_URL</code> en <code>docker-compose.yml</code> y reinicia Django.</p>
        <div class="aliado-code"><span class="code-label">Variable a cambiar:</span><code>ALIADO_API_URL: "http://IP_ALIADO/api/info/"</code></div>
      </div>`;
    return;
  }
  if (d.estado === "conectado") {
    badge.className = "integ-badge integ-badge--ok";
    badge.innerHTML = `<span class="badge-dot"></span>CONECTADO`;
    const datos = d.datos || {};
    const statsHtml = datos.estadisticas ? `<div class="aliado-stats">${Object.entries(datos.estadisticas).map(([k,v]) => `<div class="aliado-stat"><span class="meta-value c-amber">${v}</span><span class="meta-label">${k.replace(/_/g," ")}</span></div>`).join("")}</div>` : "";
    body.innerHTML = `<div class="aliado-connected">
      <div class="aliado-info-row"><span class="meta-label">Sistema</span><span class="meta-value c-amber">${datos.sistema||"—"}</span></div>
      <div class="aliado-info-row"><span class="meta-label">Versión</span><span class="meta-value">${datos.version||"—"}</span></div>
      <div class="aliado-info-row"><span class="meta-label">Descripción</span><span class="meta-value">${datos.descripcion||"—"}</span></div>
      ${statsHtml}
      <div class="integ-source">URL: ${d.url_consultada||"—"}</div>
    </div>`;
    return;
  }
  badge.className = "integ-badge integ-badge--error";
  badge.innerHTML = `<span class="badge-dot"></span>${(d.estado||"ERROR").toUpperCase()}`;
  body.innerHTML  = buildError(d.mensaje || "Servicio aliado no disponible");
}

function renderFlask(res) {
  const badge = document.getElementById("badge-flask");
  const body  = document.getElementById("body-flask");
  if (!badge || !body) return;
  if (!res.ok) {
    badge.className = "integ-badge integ-badge--error";
    badge.innerHTML = `<span class="badge-dot"></span>OFFLINE`;
    body.innerHTML  = buildError(res.error || "Flask no responde");
    return;
  }
  const d = res.data;
  badge.className = "integ-badge integ-badge--ok";
  badge.innerHTML = `<span class="badge-dot"></span>RUNNING`;
  body.innerHTML = `
    <div class="flask-grid">
      ${buildFlaskRow("Estado",  d.status  || "ok",             true)}
      ${buildFlaskRow("Servicio",d.service || "Flask Reservas", false)}
      ${buildFlaskRow("Versión", d.version || "—",              false)}
      ${buildFlaskRow("Ruta",    "/api/v2/reservas/",           false)}
      ${buildFlaskRow("Patrón",  "Strangler Fig Pattern",       false)}
      ${buildFlaskRow("DB",      "PostgreSQL compartida",       false)}
    </div>
    <div class="integ-source">Microservicio independiente · Nginx rutea /api/v2/reservas/*</div>`;
}

function registerReporteEvent() {
  const btn    = document.getElementById("btn-reporte");
  const result = document.getElementById("celery-result");
  const badge  = document.getElementById("badge-celery");
  if (!btn || !result || !badge) return;
  btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.textContent = "Encolando tarea...";
    badge.className = "integ-badge integ-badge--loading";
    badge.innerHTML = `<span class="badge-dot"></span>PROCESANDO`;
    result.style.display = "none";
    const res = await dispararReporte();
    btn.disabled = false;
    btn.textContent = "⚡ Disparar Reporte";
    if (res.ok) {
      const d = res.data;
      badge.className = "integ-badge integ-badge--ok";
      badge.innerHTML = `<span class="badge-dot"></span>ENCOLADO`;
      result.style.display = "block";
      result.className = "celery-result celery-result--ok";
      result.innerHTML = `
        <div class="celery-row"><span class="celery-key">Estado</span><span class="celery-val c-amber">${d.estado||"encolado"}</span></div>
        <div class="celery-row"><span class="celery-key">Task ID</span><span class="celery-val" style="font-family:var(--font-mono);font-size:11px">${d.task_id||"—"}</span></div>
        <div class="celery-row"><span class="celery-key">Broker</span><span class="celery-val">${d.broker||"Redis + Celery"}</span></div>
        <p class="celery-note">✅ Tarea ejecutándose en background. Verifica con: docker compose logs celery_worker</p>`;
    } else {
      badge.className = "integ-badge integ-badge--error";
      badge.innerHTML = `<span class="badge-dot"></span>ERROR`;
      result.style.display = "block";
      result.className = "celery-result celery-result--error";
      result.innerHTML = `<p>⚠️ ${res.error}</p><p class="celery-note">Verifica con: docker compose ps</p>`;
    }
  });
}

function buildPulse(n) { return Array.from({length:n},(_,i)=>`<div class="integ-pulse" style="width:${70-i*10}%;animation-delay:${i*0.12}s"></div>`).join(""); }
function buildError(msg) { return `<div class="integ-error"><span>⚠️</span><p>${msg||"Error de conexión"}</p></div>`; }
function buildStat(icon,value,label) { return `<div class="sistema-stat"><span class="sstat-icon">${icon}</span><span class="sstat-value">${value}</span><span class="sstat-label">${label}</span></div>`; }
function buildMeta(label,value,amber) { return `<div class="integ-meta-item"><span class="meta-label">${label}</span><span class="meta-value ${amber?"c-amber":""}">${value}</span></div>`; }
function buildClimaRow(icon,label,value) { return `<div class="clima-row"><span class="clima-row-icon">${icon}</span><span class="clima-row-label">${label}</span><span class="clima-row-value">${value}</span></div>`; }
function buildFlaskRow(label,value,highlight) { return `<div class="flask-row"><span class="meta-label">${label}</span><span class="meta-value ${highlight?"c-amber":""}">${value}</span></div>`; }