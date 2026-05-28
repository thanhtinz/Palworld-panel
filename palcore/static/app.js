const formatNumber = new Intl.NumberFormat("en-US");
const compactNumber = new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 });

const $ = (selector) => document.querySelector(selector);

function setText(selector, text) {
  const element = $(selector);
  if (element) element.textContent = text;
}

function statusClass(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9-]/g, "-");
}

function renderMetricCards(totals) {
  setText("#online-players", formatNumber.format(totals.online_players));
  setText("#player-capacity", `${formatNumber.format(totals.player_capacity)} capacity`);
  setText("#average-health", `${totals.average_health}%`);
  setText("#tracked-pals", formatNumber.format(totals.tracked_pals));
  setText("#active-dungeons", formatNumber.format(totals.active_dungeons));
  setText("#pal-system-features", formatNumber.format(totals.pal_system_features));
}

function renderServers(servers) {
  $("#server-list").innerHTML = servers.map((server) => {
    const ramPercent = Math.min(100, Math.round((server.ram_mb / 32768) * 100));
    const diskPercent = Math.min(100, Math.round((server.disk_gb / 200) * 100));
    const tpsPercent = Math.min(100, Math.round((server.tps / 30) * 100));
    return `
      <article class="server-card">
        <div class="server-top">
          <div><div class="server-name">${server.name}</div><div class="server-region">${server.region} · ${server.online_players}/${server.max_players} players</div></div>
          <span class="status ${statusClass(server.status)}">${server.status}</span>
        </div>
        <div class="bars">
          ${bar("CPU", server.cpu_percent)}
          ${bar("RAM", ramPercent)}
          ${bar("DISK", diskPercent)}
          ${bar("TPS", tpsPercent, `${server.tps}`)}
        </div>
      </article>`;
  }).join("");
}

function bar(label, percent, display = `${Math.round(percent)}%`) {
  return `<div><div class="bar"><span style="width:${Math.min(100, percent)}%"></span></div><div class="bar-label">${label} ${display}</div></div>`;
}

function renderMap(markers, pals = []) {
  const palMarkers = pals.map((pal) => ({
    marker_type: "pal",
    label: `${pal.pal_id} ${pal.species}`,
    x: Math.max(5, Math.min(95, (pal.location.x / 2000) * 100)),
    y: Math.max(5, Math.min(95, (pal.location.y / 1000) * 100)),
    severity: pal.ai_state === "combat" ? "critical" : "pal",
  }));
  $("#live-map").innerHTML = [...markers, ...palMarkers].map((marker) => `
    <div class="marker ${marker.severity}" style="left:${marker.x}%; top:${marker.y}%" title="${marker.marker_type}">
      <span>${marker.label}</span>
    </div>
  `).join("");
}

function renderPlayers(players) {
  $("#player-list").innerHTML = players.map((player) => `
    <div class="list-row">
      <div class="row-top"><span class="row-title">${player.name}</span><span>Lv ${player.level}</span></div>
      <div class="row-subtitle">${player.guild} · ${player.playtime_hours}h · ${player.ping_ms}ms ping · ${player.warnings} warnings</div>
    </div>
  `).join("");
}

function renderPals(pals) {
  $("#pal-list").innerHTML = pals.map((pal) => {
    const traits = pal.passives ?? pal.passive_traits ?? [];
    const location = pal.location ? `@ ${pal.location.x}, ${pal.location.y}, ${pal.location.z}` : "location pending";
    return `
      <div class="list-row">
        <div class="row-top"><span class="row-title">${pal.pal_id} · ${pal.species}</span><span>${compactNumber.format(pal.market_value)} coins</span></div>
        <div class="row-subtitle">${pal.owner} · ${pal.guild} · Lv ${pal.level} · ${pal.element}/${pal.rarity} · ${location}</div>
        <div class="row-subtitle">HP ${pal.hp}% · STA ${pal.stamina}% · ${pal.mood} · AI ${pal.ai_state} · Target ${pal.current_target ?? "none"}</div>
        <div class="chip-row">${traits.map((trait) => `<span>${trait}</span>`).join("")}</div>
      </div>`;
  }).join("");
}

function renderPalSystem(system) {
  setText("#pal-system-goal", system.goal);
  const cards = [
    ["Registry", system.registry_features, system.registry_filters],
    ["Live Viewer", system.viewer_actions, system.realtime_actions],
    ["Spawn", system.spawn_features, system.spawn_controls],
    ["Breeding", system.breeding_features, system.gene_flow],
    ["AI Control", system.ai_states, system.ai_controls],
    ["Jobs", system.job_system?.features ?? [], system.job_system?.jobs ?? []],
    ["Marketplace", system.marketplace?.features ?? [], system.marketplace?.filters ?? []],
    ["Creator/API", system.creator_tools, system.public_api],
  ];
  $("#pal-system-grid").innerHTML = cards.map(([title, primary, secondary]) => `
    <article class="feature-card">
      <h3>${title}</h3>
      <p>${[...(primary ?? [])].slice(0, 3).join(" · ")}</p>
      <div class="chip-row">${[...(secondary ?? [])].slice(0, 5).map((item) => `<span>${item}</span>`).join("")}</div>
    </article>
  `).join("");
}

function renderDungeons(dungeons) {
  $("#dungeon-list").innerHTML = dungeons.map((dungeon) => `
    <div class="list-row">
      <div class="row-top"><span class="row-title">${dungeon.name}</span><span class="status ${statusClass(dungeon.status)}">${dungeon.status}</span></div>
      <div class="row-subtitle">${dungeon.difficulty} · Boss ${dungeon.boss} · ${dungeon.completion_rate}% clear · ${dungeon.death_count} deaths</div>
    </div>
  `).join("");
}

function renderEconomy(metrics) {
  $("#economy-list").innerHTML = metrics.map((metric) => `
    <div class="economy-card">
      <span>${metric.label}</span>
      <strong>${formatNumber.format(metric.value)} ${metric.unit}</strong>
      <span class="change ${metric.change_percent >= 0 ? "positive" : "negative"}">${metric.change_percent >= 0 ? "+" : ""}${metric.change_percent}%</span>
    </div>
  `).join("");
}

function renderModules(modules) {
  $("#module-list").innerHTML = modules.map((module) => `
    <div class="module-card">
      <div class="row-top"><span class="row-title">${module.name}</span><span>Phase ${module.phase}</span></div>
      <div class="row-subtitle">${module.summary}</div>
    </div>
  `).join("");
}

function renderAudit(logs) {
  $("#audit-log").innerHTML = logs.map((log) => `
    <div class="audit-row severity-${log.severity}">
      <div><strong>${log.action}</strong><div class="audit-meta">${log.actor} → ${log.target}</div></div>
      <time class="audit-meta">${new Date(log.occurred_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</time>
    </div>
  `).join("");
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2200);
}

async function loadDashboard() {
  const response = await fetch("/api/v1/dashboard");
  if (!response.ok) throw new Error(`Dashboard API returned ${response.status}`);
  const { totals, state } = await response.json();
  renderMetricCards(totals);
  renderServers(state.servers);
  renderMap(state.map_markers, state.pals);
  renderPlayers(state.players);
  renderPals(state.pals);
  renderPalSystem(state.pal_system);
  renderDungeons(state.dungeons);
  renderEconomy(state.economy);
  renderModules(state.modules);
  renderAudit(state.audit_logs);
  setText("#topic-count", `${state.event_topics.length} topics`);
}

document.addEventListener("click", (event) => {
  const action = event.target?.dataset?.action;
  if (action === "restart") showToast("Cluster restart queued for maintenance window");
  if (action === "backup") showToast("Manual backup started across active servers");
});

loadDashboard().catch((error) => {
  console.error(error);
  showToast("Unable to load PALCORE dashboard API");
});
