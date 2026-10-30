"use strict";

const STATUS_URL = "status.json";
const FETCH_TIMEOUT_MS = 5000;
const REFRESH_MS = 60_000;
const MAX_FUTURE_SKEW_MS = 5 * 60_000;

const CHECK_META = {
  "public-web": {
    title: "Публичная витрина",
    role: "HTTPS и контрольный маркер опубликованной страницы",
    source: "HTTPS readback",
    fallbackScope: "Проверяется выдача страницы, не весь интернет-маршрут каждого посетителя."
  },
  coordination: {
    title: "Контур координации",
    role: "Доступность внешнего API, через который фиксируются задачи",
    source: "Внешний API",
    fallbackScope: "Доступность API не означает выполнение конкретной приватной задачи."
  },
  workspace: {
    title: "ИИ-рабочая среда",
    role: "HTTPS-вход и обязательная граница авторизации",
    source: "HTTPS + auth boundary",
    fallbackScope: "Проверяется публичная поверхность входа, без доступа к пользовательским данным."
  },
  verification: {
    title: "Проверка snapshot",
    role: "Схема, allowlist и свежесть публичного среза",
    source: "Локальная проверка публикации",
    fallbackScope: "Это проверка публичного среза, не содержательная приёмка всех проектов LexTeam."
  }
};

const STATE_LABELS = {
  ok: "работает",
  degraded: "сбой",
  unknown: "неизвестно",
  stale: "устарело"
};

const orderedIds = Object.keys(CHECK_META);
let currentSnapshot = null;
let currentChecks = new Map();
let activeNode = null;

const statusList = document.getElementById("status-list");
const summary = document.getElementById("scene-summary");
const snapshotTime = document.getElementById("snapshot-time");
const detailPanel = document.getElementById("detail-panel");
const detailClose = detailPanel.querySelector(".detail-close");

function safeDate(value) {
  if (typeof value !== "string" || !value.trim()) return null;
  const date = new Date(value);
  return Number.isFinite(date.getTime()) ? date : null;
}

function derivedState(check, snapshot, now = new Date()) {
  const checked = safeDate(check?.checked_at);
  const snapshotDate = safeDate(snapshot?.generated_at);
  if (!checked || !snapshotDate) return "unknown";
  if (checked.getTime() - now.getTime() > MAX_FUTURE_SKEW_MS) return "unknown";
  if (snapshotDate.getTime() - now.getTime() > MAX_FUTURE_SKEW_MS) return "unknown";

  const freshFor = Number(check?.fresh_for_seconds ?? snapshot?.fresh_for_seconds);
  if (!Number.isFinite(freshFor) || freshFor <= 0) return "unknown";
  if (now.getTime() - checked.getTime() > freshFor * 1000) return "stale";

  if (check.state === "ok") return "ok";
  if (check.state === "degraded" || check.state === "fail") return "degraded";
  return "unknown";
}

function relativeAge(value, now = new Date()) {
  const date = safeDate(value);
  if (!date) return "время неизвестно";
  const seconds = Math.max(0, Math.round((now.getTime() - date.getTime()) / 1000));
  if (seconds < 10) return "только что";
  if (seconds < 60) return `${seconds} сек. назад`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} мин. назад`;
  const hours = Math.floor(minutes / 60);
  return `${hours} ч. назад`;
}

function formatDate(value) {
  const date = safeDate(value);
  if (!date) return "—";
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    timeZone: "Europe/Moscow"
  }).format(date) + " МСК";
}

function unknownCheck(id) {
  const meta = CHECK_META[id];
  return {
    id,
    state: "unknown",
    checked_at: null,
    summary: "Источник публичного статуса сейчас недоступен.",
    source: meta.source,
    scope: meta.fallbackScope,
    fresh_for_seconds: 180
  };
}

function normalizeSnapshot(payload) {
  if (!payload || typeof payload !== "object" || !Array.isArray(payload.checks)) {
    throw new Error("invalid snapshot");
  }
  const allowed = new Map();
  for (const raw of payload.checks) {
    if (!raw || !orderedIds.includes(raw.id) || allowed.has(raw.id)) continue;
    allowed.set(raw.id, {
      id: raw.id,
      state: ["ok", "degraded", "fail", "unknown"].includes(raw.state) ? raw.state : "unknown",
      checked_at: typeof raw.checked_at === "string" ? raw.checked_at : null,
      summary: typeof raw.summary === "string" ? raw.summary.slice(0, 180) : "Нет публичного описания.",
      source: typeof raw.source === "string" ? raw.source.slice(0, 80) : CHECK_META[raw.id].source,
      scope: typeof raw.scope === "string" ? raw.scope.slice(0, 220) : CHECK_META[raw.id].fallbackScope,
      fresh_for_seconds: Number(raw.fresh_for_seconds)
    });
  }
  return {
    schema_version: String(payload.schema_version || ""),
    generated_at: typeof payload.generated_at === "string" ? payload.generated_at : null,
    fresh_for_seconds: Number(payload.fresh_for_seconds) || 180,
    checks: orderedIds.map((id) => allowed.get(id) || unknownCheck(id))
  };
}

async function fetchSnapshot() {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const response = await fetch(`${STATUS_URL}?t=${Date.now()}`, {
      cache: "no-store",
      credentials: "omit",
      signal: controller.signal
    });
    if (!response.ok) throw new Error(`status ${response.status}`);
    return normalizeSnapshot(await response.json());
  } finally {
    clearTimeout(timeout);
  }
}

function updateEdges() {
  document.querySelectorAll("[data-edge]").forEach((edge) => {
    const ids = edge.dataset.edge.split(",");
    const isHealthy = ids.every((id) => {
      const check = currentChecks.get(id) || unknownCheck(id);
      return derivedState(check, currentSnapshot) === "ok";
    });
    edge.classList.toggle("is-muted", !isHealthy);
  });
}

function renderNodes() {
  document.querySelectorAll(".system-node[data-check-id]").forEach((node) => {
    const id = node.dataset.checkId;
    const check = currentChecks.get(id) || unknownCheck(id);
    const state = derivedState(check, currentSnapshot);
    node.dataset.state = state;
    node.querySelector(".node-state").textContent = STATE_LABELS[state];
    node.setAttribute("aria-label", `${CHECK_META[id].title}: ${STATE_LABELS[state]}`);
  });
  updateEdges();
}

function makeStatusRow(id) {
  const meta = CHECK_META[id];
  const check = currentChecks.get(id) || unknownCheck(id);
  const state = derivedState(check, currentSnapshot);
  const row = document.createElement("article");
  row.className = "status-row";
  row.dataset.checkId = id;

  const identity = document.createElement("div");
  const title = document.createElement("h3");
  title.textContent = meta.title;
  const role = document.createElement("p");
  role.textContent = meta.role;
  identity.append(title, role);

  const chip = document.createElement("span");
  chip.className = `status-chip is-${state}`;
  chip.textContent = STATE_LABELS[state];

  const age = document.createElement("span");
  age.className = "status-age";
  age.textContent = relativeAge(check.checked_at);
  age.title = formatDate(check.checked_at);

  row.append(identity, chip, age);
  return row;
}

function renderStatusList() {
  statusList.replaceChildren(...orderedIds.map(makeStatusRow));
}

function renderHeader() {
  const states = orderedIds.map((id) => derivedState(currentChecks.get(id) || unknownCheck(id), currentSnapshot));
  const ok = states.filter((state) => state === "ok").length;
  const stale = states.filter((state) => state === "stale").length;
  const degraded = states.filter((state) => state === "degraded").length;
  if (degraded) summary.textContent = `Наблюдается сбой: ${degraded} из ${states.length} проверок.`;
  else if (stale) summary.textContent = `Часть данных устарела: ${stale} из ${states.length} проверок.`;
  else if (ok === states.length) summary.textContent = `Все ${states.length} публичные проверки свежие.`;
  else summary.textContent = `Свежих проверок: ${ok} из ${states.length}; остальное неизвестно.`;

  const date = safeDate(currentSnapshot?.generated_at);
  snapshotTime.textContent = date ? formatDate(date) : "источник недоступен";
  snapshotTime.dateTime = date ? date.toISOString() : "";
}

function renderAll() {
  renderNodes();
  renderStatusList();
  renderHeader();
  if (activeNode) showDetail(activeNode, false);
}

function closeDetail({ restoreFocus = true } = {}) {
  detailPanel.hidden = true;
  document.querySelectorAll(".system-node").forEach((node) => {
    node.classList.remove("is-dimmed");
    node.setAttribute("aria-expanded", "false");
  });
  const previous = activeNode;
  activeNode = null;
  if (restoreFocus && previous) previous.focus();
}

function showDetail(node, moveFocus = true) {
  const id = node.dataset.checkId;
  const meta = CHECK_META[id];
  const check = currentChecks.get(id) || unknownCheck(id);
  const state = derivedState(check, currentSnapshot);
  activeNode = node;

  document.querySelectorAll(".system-node").forEach((item) => {
    const active = item === node;
    item.classList.toggle("is-dimmed", !active);
    item.setAttribute("aria-expanded", String(active));
  });
  document.getElementById("detail-source").textContent = check.source || meta.source;
  document.getElementById("detail-title").textContent = meta.title;
  document.getElementById("detail-summary").textContent = check.summary;
  document.getElementById("detail-state").textContent = STATE_LABELS[state];
  document.getElementById("detail-checked").textContent = check.checked_at ? formatDate(check.checked_at) : "нет надёжного времени";
  document.getElementById("detail-scope").textContent = check.scope || meta.fallbackScope;
  detailPanel.hidden = false;
  if (moveFocus) detailPanel.focus({ preventScroll: true });
}

document.querySelectorAll(".system-node").forEach((node) => {
  node.addEventListener("click", () => {
    if (activeNode === node && !detailPanel.hidden) closeDetail();
    else showDetail(node);
  });
});
detailClose.addEventListener("click", () => closeDetail());
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !detailPanel.hidden) closeDetail();
});

function fallbackSnapshot() {
  return {
    schema_version: "1",
    generated_at: null,
    fresh_for_seconds: 180,
    checks: orderedIds.map(unknownCheck)
  };
}

async function refresh() {
  try {
    currentSnapshot = await fetchSnapshot();
  } catch {
    currentSnapshot = fallbackSnapshot();
  }
  currentChecks = new Map(currentSnapshot.checks.map((check) => [check.id, check]));
  renderAll();
}

function startReveal() {
  const targets = document.querySelectorAll("[data-reveal]");
  if (!("IntersectionObserver" in window)) {
    targets.forEach((target) => target.classList.add("is-visible"));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, { rootMargin: "0px 0px -8%", threshold: 0.08 });
  targets.forEach((target) => observer.observe(target));
}

startReveal();
refresh();
setInterval(() => {
  if (!document.hidden) refresh();
}, REFRESH_MS);
setInterval(() => {
  if (currentSnapshot) renderAll();
}, 15_000);
