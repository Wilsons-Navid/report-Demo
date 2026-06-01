// ─────────────────────────────────────────────────────────────
// CONFIG — point this at your FastAPI deployment.
//   local:  http://127.0.0.1:8000
//   render: https://your-service.onrender.com
// You can also override at runtime with ?api=https://...
// ─────────────────────────────────────────────────────────────
const API_BASE =
  new URLSearchParams(location.search).get("api") ||
  "http://127.0.0.1:8000";

const CATS = {
  phishing:           { name: "Phishing",            color: "#ff5a4d", note: "Credential / link harvesting" },
  advance_fee_fraud:  { name: "Advance-Fee Fraud",   color: "#f4a72c", note: "Prize · 419 · inheritance lure" },
  mobile_money_fraud: { name: "Mobile-Money Fraud",  color: "#b98cff", note: "Wallet · PIN · agent / OTP" },
  not_a_scam:         { name: "Not a Scam",          color: "#43d39a", note: "Benign message" },
};

const EXAMPLES = [
  { label: "Phishing link",   cat: "phishing",
    text: "Dear customer, your bank account is suspended. Click here to verify immediately: http://bit.ly/secure-acct" },
  { label: "M-Pesa (PT)",     cat: "mobile_money_fraud",
    text: "Caro cliente, a sua conta M-Pesa foi bloqueada. Envie o seu codigo PIN para reactivar a conta agora." },
  { label: "Prize / 419",     cat: "advance_fee_fraud",
    text: "URGENT! Your mobile number won a £2000 prize GUARANTEED. Call 09061790121 to claim before it expires." },
  { label: "Benign",          cat: "not_a_scam",
    text: "Hey, are we still meeting for lunch at 1pm tomorrow? Let me know if the time still works." },
];

const $ = (id) => document.getElementById(id);
const msg = $("message"), output = $("output"), runBtn = $("classify");

// ---- examples ----
const chips = $("chips");
EXAMPLES.forEach((ex) => {
  const c = document.createElement("button");
  c.className = "chip";
  c.style.setProperty("--chip-c", CATS[ex.cat].color);
  c.innerHTML = `<b></b>${ex.label}`;
  c.onclick = () => { msg.value = ex.text; msg.focus(); };
  chips.appendChild(c);
});

// ---- api readout + health ----
$("apiReadout").textContent = API_BASE;
async function ping() {
  const el = $("apiStatus"), txt = $("apiStatusText");
  try {
    const r = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    if (!r.ok) throw 0;
    el.className = "status up"; txt.textContent = "model online";
  } catch {
    el.className = "status down"; txt.textContent = "API offline";
  }
}
ping();

// ---- classify ----
async function classify() {
  const text = msg.value.trim();
  if (!text) { msg.focus(); return; }

  runBtn.disabled = true; runBtn.classList.add("loading");
  runBtn.querySelector(".run-label").textContent = "Analysing";

  try {
    const r = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!r.ok) throw new Error(`API returned ${r.status}`);
    render(await r.json());
    $("apiStatus").className = "status up"; $("apiStatusText").textContent = "model online";
  } catch (e) {
    showError(e.message);
  } finally {
    runBtn.disabled = false; runBtn.classList.remove("loading");
    runBtn.querySelector(".run-label").textContent = "Classify";
  }
}
runBtn.onclick = classify;
msg.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === "Enter") classify();
});

// ---- render ----
function render(data) {
  const top = data.predicted_category;
  const meta = CATS[top] || { name: top, color: "#f4a72c", note: "" };

  const verdict = $("verdict");
  verdict.style.setProperty("--vc", meta.color);
  $("confPct").textContent = Math.round((data.confidence ?? 0) * 100) + "%";
  $("verdictName").textContent = meta.name;
  $("verdictNote").textContent = meta.note;
  verdict.hidden = false;

  const bars = $("bars");
  bars.hidden = false;
  bars.innerHTML = "";
  const entries = Object.entries(data.scores || {}).sort((a, b) => b[1] - a[1]);
  entries.forEach(([cat, score], i) => {
    const m = CATS[cat] || { name: cat, color: "#8c8674" };
    const row = document.createElement("div");
    row.className = "bar-row" + (cat === top ? " win" : "");
    row.style.setProperty("--bc", m.color);
    row.innerHTML = `
      <div class="bar-head"><b></b>${m.name}</div>
      <div class="bar-pct">${(score * 100).toFixed(1)}%</div>
      <div class="bar-track"><div class="bar-fill"></div></div>`;
    bars.appendChild(row);
    requestAnimationFrame(() =>
      setTimeout(() => { row.querySelector(".bar-fill").style.width = (score * 100) + "%"; }, 60 + i * 90)
    );
  });

  output.dataset.state = "result";
}

function showError(message) {
  output.dataset.state = "result";
  $("verdict").hidden = true;
  const bars = $("bars");
  bars.hidden = false;
  bars.innerHTML =
    `<div class="err"><b>Could not reach the classifier.</b><br/>${message}.<br/><br/>
     Is the API running at <code>${API_BASE}</code>? Start it with
     <code>uvicorn ml.serve.app:app --port 8000</code>, or pass <code>?api=&lt;url&gt;</code>.</div>`;
}
