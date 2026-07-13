// Server-side SSD simulation visualizer.
// The Python engine runs the trace and streams grid snapshots over SSE; this
// module just renders each snapshot, so the browser never runs the simulation.

let streamCells = [];       // block index -> <div> cell
let streamGridBlocks = 0;   // current grid size
let currentSource = null;   // active EventSource
let znsCards = [];          // zone index -> {card, badge, v, s} (ZNS mode)
let znsZoneCount = -1;      // current zone-grid size

async function loadTraces() {
  try {
    const res = await fetch("/api/traces");
    const traces = await res.json();
    const sel = document.getElementById("trace_select");
    sel.innerHTML = "";
    if (!traces.length) {
      const o = document.createElement("option");
      o.textContent = "(no traces uploaded yet)";
      o.disabled = true;
      sel.appendChild(o);
      return;
    }
    traces.forEach((t) => {
      const o = document.createElement("option");
      o.value = t.name;
      o.textContent = `${t.name} — ${(t.size / 1e6).toFixed(1)} MB (${t.kind})`;
      sel.appendChild(o);
    });
  } catch (e) {
    setStatus("Could not load trace list: " + e);
  }
}

async function uploadTrace() {
  const input = document.getElementById("trace_upload");
  if (!input.files.length) {
    alert("Choose a trace file first.");
    return;
  }
  const fd = new FormData();
  fd.append("trace", input.files[0]);
  setStatus("Uploading " + input.files[0].name + " ...");
  try {
    const res = await fetch("/api/upload_trace", { method: "POST", body: fd });
    const j = await res.json();
    setStatus(j.ok ? "Uploaded: " + j.name : "Upload error: " + j.error);
    await loadTraces();
    if (j.ok) document.getElementById("trace_select").value = j.name;
  } catch (e) {
    setStatus("Upload failed: " + e);
  }
}

let streamGeoKey = "";  // signature of the geometry currently drawn

// Build the nested channel -> chip -> die -> plane -> blocks grid, exactly like
// the advance simulator. streamCells is indexed by the engine's FLAT block index
// so renderSnapshot can update in O(1). The flat index layout matches the engine:
//   plane_index = (((channel*CHIP + chip)*DIE + die)*PLANE + plane)   (channel outermost)
//   block_index = plane_index * BPP + local_block
function buildGrid(geo) {
  const grid = document.getElementById("stream_grid");
  grid.className = "";   // leave ZNS zone-grid layout if we were in that mode
  grid.innerHTML = "";
  const CH = geo.channel, CP = geo.chip, DI = geo.die, PL = geo.plane;
  const BPP = geo.blocks_per_plane;
  const total = CH * CP * DI * PL * BPP;
  streamCells = new Array(total);

  const cols = Math.min(BPP, Math.ceil(Math.sqrt(BPP)) + 2); // block grid width

  const box = (label, cls) => {
    const d = document.createElement("div");
    d.className = "grp " + cls;
    const h = document.createElement("div");
    h.className = "grp-label";
    h.textContent = label;
    d.appendChild(h);
    return d;
  };

  for (let ch = 0; ch < CH; ch++) {
    const chBox = box("Channel " + ch, "channel");
    for (let cp = 0; cp < CP; cp++) {
      const cpBox = box("Chip " + cp, "chip");
      for (let di = 0; di < DI; di++) {
        const diBox = box("Die " + di, "die");
        for (let pl = 0; pl < PL; pl++) {
          const plBox = box("P" + pl, "plane");
          const bg = document.createElement("div");
          bg.className = "block-grid";
          bg.style.gridTemplateColumns = `repeat(${cols}, 7px)`;
          const planeIdx = ((ch * CP + cp) * DI + di) * PL + pl;
          for (let b = 0; b < BPP; b++) {
            const cell = document.createElement("div");
            cell.className = "blk";
            bg.appendChild(cell);
            streamCells[planeIdx * BPP + b] = cell;
          }
          plBox.appendChild(bg);
          diBox.appendChild(plBox);
        }
        cpBox.appendChild(diBox);
      }
      chBox.appendChild(cpBox);
    }
    grid.appendChild(chBox);
  }
  streamGridBlocks = total;
  streamGeoKey = `${CH}-${CP}-${DI}-${PL}-${BPP}`;
}

// Paint one block cell using the advance-simulator color code system:
//   free (no pages)      -> white
//   partial              -> rgb(0, 255*invalidRatio, 0)  (near-black = mostly
//                           valid, bright green = mostly invalid)
//   fully valid  (inv=0) -> black bg + r.webp tick overlay
//   fully invalid(val=0) -> bright-green bg + x.webp cross overlay
const TICK_IMG = 'url("/static/src/logo/r.webp")';
const CROSS_IMG = 'url("/static/src/logo/x.webp")';

function paintCell(cell, valid, invalid) {
  const total = valid + invalid;
  if (total === 0) {
    if (cell._img !== "none") { cell.style.backgroundImage = "none"; cell._img = "none"; }
    cell.style.backgroundColor = "rgb(255,255,255)";
    return;
  }
  if (valid === 0) {                 // fully invalid
    cell.style.backgroundColor = "rgb(0,255,0)";
    if (cell._img !== "x") { cell.style.backgroundImage = CROSS_IMG; cell.style.backgroundSize = "cover"; cell._img = "x"; }
    return;
  }
  if (invalid === 0) {               // fully valid
    cell.style.backgroundColor = "rgb(0,0,0)";
    if (cell._img !== "r") { cell.style.backgroundImage = TICK_IMG; cell.style.backgroundSize = "cover"; cell._img = "r"; }
    return;
  }
  const g = Math.max(0, Math.min(255, Math.floor((255 * invalid) / total)));
  cell.style.backgroundColor = `rgb(0,${g},0)`;
  if (cell._img !== "none") { cell.style.backgroundImage = "none"; cell._img = "none"; }
}

function fmtTime(s) {
  s = Math.max(0, Math.round(s));
  if (s < 60) return s + "s";
  const m = Math.floor(s / 60);
  return m + "m " + (s % 60) + "s";
}

// ---------------------------------------------------------------------------
// Live paper-style metrics. Every snapshot carries waf + per-block erase/valid/
// invalid arrays, so all of these are computed on the client and redrawn at the
// stream's update frequency.
// ---------------------------------------------------------------------------
let charts = null;         // active Chart.js instances (keys depend on engine)
let chartsEngine = null;   // "conventional" | "zns" — which chart set is built
let lastPhase = "";        // to reset the time-series line charts at phase change

function makeChart(id, cfg) {
  const el = document.getElementById(id);
  return el ? new Chart(el.getContext("2d"), cfg) : null;
}

function lineCfg(label, color, xtitle) {
  return {
    type: "line",
    data: { labels: [], datasets: [{ label, data: [], borderColor: color,
              backgroundColor: color, pointRadius: 0, borderWidth: 2, tension: 0.15 }] },
    options: { animation: false, responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, title: { display: true, text: label } },
      scales: { x: { title: { display: true, text: xtitle }, ticks: { maxTicksLimit: 6 } },
                y: { beginAtZero: true } } },
  };
}
function barCfg(label, color, xtitle, ytitle) {
  return {
    type: "bar",
    data: { labels: [], datasets: [{ label, data: [], backgroundColor: color }] },
    options: { animation: false, responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, title: { display: true, text: label } },
      scales: { x: { title: { display: true, text: xtitle } },
                y: { beginAtZero: true, title: { display: true, text: ytitle || "" } } } },
  };
}

function destroyCharts() {
  if (!charts) return;
  for (const k in charts) if (charts[k]) charts[k].destroy();
  charts = null;
}

// (Re)build the chart set for the active engine. The four <canvas> slots are
// reused; only their meaning changes between conventional and ZNS.
function ensureCharts(engine) {
  if (chartsEngine === engine && charts) return;
  destroyCharts();
  if (typeof Chart === "undefined") return;
  if (engine === "zns") {
    charts = {
      waf: makeChart("chart_waf", lineCfg("Host write amplification vs writes", "#2ca02c", "host writes")),
      reset: makeChart("chart_cv", barCfg("Zone resets per zone", "#d62728", "zone", "resets")),
      valid: makeChart("chart_erase", barCfg("Valid (live) pages per zone", "#2ca02c", "zone", "pages")),
      state: makeChart("chart_invalid", barCfg("Zones by state", "#1f77b4", "state", "zones")),
    };
  } else {
    charts = {
      waf: makeChart("chart_waf", lineCfg("Write Amplification (WAF) vs host writes", "#2ca02c", "host writes")),
      cv: makeChart("chart_cv", lineCfg("Wear evenness — erase-count CV vs writes", "#d62728", "host writes")),
      erase: makeChart("chart_erase", barCfg("Erase-count distribution", "#1f77b4", "erases per block", "blocks")),
      invalid: makeChart("chart_invalid", barCfg("Invalid-page ratio distribution", "#ff7f0e", "invalid page ratio", "blocks")),
    };
  }
  chartsEngine = engine;
  lastPhase = "";
}

function resetLineCharts() {
  if (!charts) return;
  for (const k of ["waf", "cv"]) {
    if (!charts[k]) continue;
    charts[k].data.labels = [];
    charts[k].data.datasets[0].data = [];
    charts[k].update("none");
  }
}

function updateCharts(snap) {
  const engine = snap.engine || "conventional";
  ensureCharts(engine);
  if (!charts) return;
  if (engine === "zns") { updateZnsCharts(snap); return; }
  const erase = snap.erase, inv = snap.invalid, val = snap.valid;

  // erase-count histogram across blocks
  let maxE = 0;
  for (let i = 0; i < erase.length; i++) if (erase[i] > maxE) maxE = erase[i];
  const nb = Math.min(maxE + 1, 25);
  const ebins = new Array(nb).fill(0);
  for (let i = 0; i < erase.length; i++) ebins[Math.min(nb - 1, erase[i])]++;

  // invalid-page ratio histogram (10 buckets, non-free blocks only)
  const ibins = new Array(10).fill(0);
  for (let i = 0; i < inv.length; i++) {
    const t = inv[i] + val[i];
    if (t === 0) continue;
    ibins[Math.min(9, Math.floor((10 * inv[i]) / t))]++;
  }

  // erase-count coefficient of variation (wear evenness; lower = more even)
  let sum = 0;
  for (let i = 0; i < erase.length; i++) sum += erase[i];
  const mean = sum / erase.length;
  let vs = 0;
  for (let i = 0; i < erase.length; i++) { const d = erase[i] - mean; vs += d * d; }
  const cv = mean > 0 ? Math.sqrt(vs / erase.length) / mean : 0;

  // time-series charts: reset when we enter a new phase so each phase draws clean
  if (snap.phase !== lastPhase) { resetLineCharts(); lastPhase = snap.phase; }
  if (snap.phase !== "done" && charts.waf) {
    const x = snap.host_writes.toLocaleString();
    charts.waf.data.labels.push(x);
    charts.waf.data.datasets[0].data.push(snap.waf);
    charts.waf.update("none");
    charts.cv.data.labels.push(x);
    charts.cv.data.datasets[0].data.push(Number(cv.toFixed(4)));
    charts.cv.update("none");
  }

  if (charts.erase) {
    charts.erase.data.labels = ebins.map((_, i) => (i === nb - 1 && maxE >= nb ? nb - 1 + "+" : String(i)));
    charts.erase.data.datasets[0].data = ebins;
    charts.erase.update("none");
  }
  if (charts.invalid) {
    charts.invalid.data.labels = ibins.map((_, i) => `${i * 10}-${i * 10 + 10}%`);
    charts.invalid.data.datasets[0].data = ibins;
    charts.invalid.update("none");
  }
}

function updateZnsCharts(snap) {
  const st = snap.zone_state, valid = snap.zone_valid, reset = snap.zone_reset;
  const labels = st.map((_, i) => "Z" + i);
  // host WA time series (reset on phase change)
  if (snap.phase !== lastPhase) { resetLineCharts(); lastPhase = snap.phase; }
  if (snap.phase !== "done" && charts.waf) {
    charts.waf.data.labels.push(snap.host_writes.toLocaleString());
    charts.waf.data.datasets[0].data.push(snap.wa);
    charts.waf.update("none");
  }
  if (charts.reset) {
    charts.reset.data.labels = labels;
    charts.reset.data.datasets[0].data = reset;
    charts.reset.update("none");
  }
  if (charts.valid) {
    charts.valid.data.labels = labels;
    charts.valid.data.datasets[0].data = valid;
    charts.valid.update("none");
  }
  if (charts.state) {
    let e = 0, o = 0, f = 0;
    for (const s of st) { if (s === 0) e++; else if (s === 1) o++; else if (s === 2) f++; }
    charts.state.data.labels = ["EMPTY", "OPEN", "FULL"];
    charts.state.data.datasets[0].data = [e, o, f];
    charts.state.update("none");
  }
}

// Build one card per zone. Each card has a bar split into valid / stale / free.
function buildZoneGrid(n) {
  const grid = document.getElementById("stream_grid");
  grid.className = "zns";
  grid.innerHTML = "";
  znsCards = new Array(n);
  for (let z = 0; z < n; z++) {
    const card = document.createElement("div");
    card.className = "zone";
    const head = document.createElement("div");
    head.className = "zone-head";
    const id = document.createElement("span");
    id.textContent = "Z" + z;
    const badge = document.createElement("span");
    badge.textContent = "0";
    badge.title = "zone reset count";
    head.appendChild(id);
    head.appendChild(badge);
    const bar = document.createElement("div");
    bar.className = "zone-bar";
    const v = document.createElement("div");
    v.className = "zseg-valid";
    const s = document.createElement("div");
    s.className = "zseg-stale";
    bar.appendChild(v);
    bar.appendChild(s);   // remaining width stays white = unwritten
    card.appendChild(head);
    card.appendChild(bar);
    grid.appendChild(card);
    znsCards[z] = { card, badge, v, s };
  }
  znsZoneCount = n;
}

function renderZns(snap) {
  if (znsZoneCount !== snap.n_zones) buildZoneGrid(snap.n_zones);
  const st = snap.zone_state, valid = snap.zone_valid, wp = snap.zone_wp, reset = snap.zone_reset;
  const zp = snap.zone_pages;
  for (let z = 0; z < snap.n_zones; z++) {
    const c = znsCards[z];
    const vp = valid[z], stale = Math.max(0, wp[z] - vp);
    c.v.style.width = (100 * vp / zp) + "%";
    c.s.style.width = (100 * stale / zp) + "%";
    c.badge.textContent = reset[z];
    let cls = "zone";
    if (st[z] === 1) cls += " open"; else if (st[z] === 2) cls += " full";
    if (z === snap.open_hot) cls += " hot";
    else if (z === snap.open_cold) cls += " cold";
    c.card.className = cls;
  }
  updateCharts(snap);
  document.getElementById("stream_progress").style.width = snap.progress + "%";
  const eta = snap.phase === "done" ? "0s" : fmtTime(snap.eta_sec || 0);
  setStatus(
    `${snap.phase}  |  ${snap.progress}%  |  ZNS ${snap.hot_cold ? "hot/cold" : "single-stream"}` +
      `  |  writes: ${snap.host_writes.toLocaleString()}  |  WA: ${snap.wa}` +
      `  |  GC writes: ${snap.gc_writes.toLocaleString()}  |  zone resets: ${snap.zone_resets}` +
      `  |  ${(snap.writes_per_sec || 0).toLocaleString()} w/s  |  elapsed ${fmtTime(snap.elapsed_sec || 0)}  |  ~${eta} left`
  );
}

// FDP mode: same block grid + valid/invalid coloring as conventional, plus a
// colored border marking each block's placement handle (hot=red, cold=blue).
function renderFdp(snap) {
  const geo = snap.geo;
  const key = `${geo.channel}-${geo.chip}-${geo.die}-${geo.plane}-${geo.blocks_per_plane}`;
  if (streamGeoKey !== key) buildGrid(geo);
  const inv = snap.invalid, val = snap.valid, handle = snap.handle;
  for (let i = 0; i < inv.length; i++) {
    const cell = streamCells[i];
    paintCell(cell, val[i], inv[i]);
    const h = handle[i];
    cell.style.boxShadow =
      h === 0 ? "inset 0 0 0 1px #d62728" :          // hot handle
      h === 1 ? "inset 0 0 0 1px #1f77b4" :          // cold handle
                "inset 0 0 0 0.5px #e0e0e0";          // free
  }
  updateCharts(snap);
  document.getElementById("stream_progress").style.width = snap.progress + "%";
  const eta = snap.phase === "done" ? "0s" : fmtTime(snap.eta_sec || 0);
  setStatus(
    `${snap.phase}  |  ${snap.progress}%  |  FDP ${snap.hot_cold ? "hot/cold hints" : "single handle"}` +
      `  |  writes: ${snap.host_writes.toLocaleString()}  |  WAF: ${snap.waf}` +
      `  |  GC writes: ${snap.gc_writes.toLocaleString()}` +
      `  |  ${(snap.writes_per_sec || 0).toLocaleString()} w/s  |  elapsed ${fmtTime(snap.elapsed_sec || 0)}  |  ~${eta} left`
  );
}

function renderSnapshot(snap) {
  const engine = snap.engine || "conventional";
  if (engine === "zns") { renderZns(snap); return; }
  if (engine === "fdp") { renderFdp(snap); return; }
  const geo = snap.geo;
  const key = `${geo.channel}-${geo.chip}-${geo.die}-${geo.plane}-${geo.blocks_per_plane}`;
  if (streamGeoKey !== key) buildGrid(geo);
  const inv = snap.invalid, val = snap.valid;
  for (let i = 0; i < inv.length; i++) paintCell(streamCells[i], val[i], inv[i]);
  updateCharts(snap);
  document.getElementById("stream_progress").style.width = snap.progress + "%";
  const eta = snap.phase === "done" ? "0s" : fmtTime(snap.eta_sec || 0);
  setStatus(
    `${snap.phase}  |  ${snap.progress}%  |  writes: ${snap.host_writes.toLocaleString()}` +
      `  |  WAF: ${snap.waf}  |  ${(snap.writes_per_sec || 0).toLocaleString()} w/s` +
      `  |  elapsed ${fmtTime(snap.elapsed_sec || 0)}  |  time left ~${eta}`
  );
}

function runSimulation() {
  const trace = document.getElementById("trace_select").value;
  if (!trace) {
    alert("Select a trace to run.");
    return;
  }
  const interval = document.getElementById("stream_interval").value;
  const op = document.getElementById("stream_op").value;
  const g = (id) => document.getElementById(id).value;
  const engine = document.querySelector('input[name="engine"]:checked').value;
  if (currentSource) currentSource.close();
  streamGridBlocks = 0;
  streamGeoKey = "";
  znsZoneCount = -1;
  lastPhase = "";
  resetLineCharts();
  setStatus("Starting simulation on the server...");
  let url =
    `/api/simulate?trace=${encodeURIComponent(trace)}` +
    `&interval=${encodeURIComponent(interval)}&op=${encodeURIComponent(op)}` +
    `&channel=${g("geo_channel")}&chip=${g("geo_chip")}` +
    `&die=${g("geo_die")}&plane=${g("geo_plane")}&blocks_per_plane=${g("geo_bpp")}` +
    `&pages_per_block=${g("geo_ppb")}`;
  if (engine === "zns") {
    const hc = document.getElementById("zns_hotcold").checked ? 1 : 0;
    url += `&engine=zns&hot_cold=${hc}&blocks_per_zone=${g("zns_bpz")}`;
  } else if (engine === "fdp") {
    const hc = document.getElementById("fdp_hotcold").checked ? 1 : 0;
    url += `&engine=fdp&hot_cold=${hc}`;
  }
  const src = new EventSource(url);
  currentSource = src;
  src.onmessage = (e) => renderSnapshot(JSON.parse(e.data));
  src.addEventListener("done", () => {
    src.close();
    currentSource = null;
    setStatus(document.getElementById("stream_status").textContent + "  — done");
  });
  src.addEventListener("error", (e) => {
    src.close();
    currentSource = null;
    if (e && e.data) {
      try { setStatus("Error: " + JSON.parse(e.data).error); } catch (_) {}
    }
  });
}

function stopSimulation() {
  if (currentSource) {
    currentSource.close();
    currentSource = null;
    setStatus("Stopped.");
  }
}

function setStatus(msg) {
  const el = document.getElementById("stream_status");
  if (el) el.textContent = msg;
}

// Read the geometry currently selected in the dropdowns.
function currentGeo() {
  const g = (id) => parseInt(document.getElementById(id).value, 10);
  return { channel: g("geo_channel"), chip: g("geo_chip"), die: g("geo_die"),
           plane: g("geo_plane"), blocks_per_plane: g("geo_bpp") };
}

// Draw a single "zoomed-in" block as a grid of its pages, so the Pages/block
// dropdown has a visible effect (a block's grid is one square in the big grid).
function renderBlockDetail(ppb) {
  const el = document.getElementById("block_detail");
  const lbl = document.getElementById("block_detail_label");
  if (!el) return;
  const cols = Math.min(ppb, 32);
  el.style.gridTemplateColumns = `repeat(${cols}, 4px)`;
  el.innerHTML = "";
  for (let i = 0; i < ppb; i++) {
    const c = document.createElement("div");
    c.style.width = "4px";
    c.style.height = "4px";
    c.style.background = "#dbe6f2";
    c.style.boxShadow = "inset 0 0 0 0.5px #b9cde2";
    el.appendChild(c);
  }
  if (lbl) lbl.innerHTML = `<b>One block</b> = ${ppb} pages (each small square = one 4&nbsp;KB page):`;
}

// Draw an EMPTY SSD (all blocks free / all zones empty) for the current mode +
// geometry, so the device structure is visible before any run starts.
function renderSkeleton() {
  if (currentSource) return;   // don't clobber a live run
  const engine = document.querySelector('input[name="engine"]:checked').value;
  const geo = currentGeo();
  const ppb = parseInt(document.getElementById("geo_ppb").value, 10);
  renderBlockDetail(ppb);
  const total = geo.channel * geo.chip * geo.die * geo.plane * geo.blocks_per_plane;
  // device capacity: blocks × pages/block × 4 KB page
  const gb = (total * ppb * 4096) / (1024 * 1024 * 1024);
  const size = gb >= 1 ? gb.toFixed(2) + " GB" : (gb * 1024).toFixed(0) + " MB";
  if (engine === "zns") {
    const bpz = parseInt(document.getElementById("zns_bpz").value, 10) || geo.blocks_per_plane;
    const n = Math.max(1, Math.floor(total / bpz));
    znsZoneCount = -1;
    buildZoneGrid(n);
    setStatus(`Empty ZNS device: ${n} zones × ${bpz} blocks × ${ppb} pages ` +
      `= ${size}. Select a trace and press Run.`);
  } else {
    streamGeoKey = "";
    buildGrid(geo);
    setStatus(`Empty SSD: ${total.toLocaleString()} blocks × ${ppb} pages/block ` +
      `across ${geo.channel}×${geo.chip}×${geo.die}×${geo.plane} planes = ${size}. ` +
      `Select a trace and press Run.`);
  }
}

// Show ZNS options + swap the legend when the simulation mode changes.
function onModeChange() {
  const engine = document.querySelector('input[name="engine"]:checked').value;
  const zns = engine === "zns", fdp = engine === "fdp";
  document.getElementById("zns_opts").style.display = zns ? "" : "none";
  document.getElementById("fdp_opts").style.display = fdp ? "" : "none";
  document.getElementById("legend_conv").style.display = (zns || fdp) ? "none" : "";
  document.getElementById("legend_zns").style.display = zns ? "" : "none";
  document.getElementById("legend_fdp").style.display = fdp ? "" : "none";
  renderSkeleton();
}

window.addEventListener("load", () => {
  loadTraces();
  onModeChange();          // also draws the initial skeleton
  // redraw the empty device whenever the geometry (or zone size) changes
  ["geo_channel", "geo_chip", "geo_die", "geo_plane", "geo_bpp", "geo_ppb", "zns_bpz"]
    .forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("change", renderSkeleton);
    });
});
