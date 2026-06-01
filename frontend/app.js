// CONFIG — FastAPI deployment. Override at runtime with ?api=https://...
const API_BASE =
  new URLSearchParams(location.search).get("api") ||
  "https://scam-classifier-api.onrender.com";

const CATS = {
  phishing:           { name: "Phishing",           color: "#ff5c5c", note: "Credential / link harvesting" },
  advance_fee_fraud:  { name: "Advance-Fee Fraud",  color: "#f5a623", note: "Prize · 419 · inheritance lure" },
  mobile_money_fraud: { name: "Mobile-Money Fraud", color: "#9b8cff", note: "Wallet · PIN · agent / OTP" },
  not_a_scam:         { name: "Not a Scam",         color: "#22c55e", note: "Benign message" },
};

const EXAMPLES = [
  { label: "Phishing link", cat: "phishing",
    text: "Dear customer, your bank account is suspended. Click here to verify immediately: http://bit.ly/secure-acct" },
  { label: "M-Pesa (PT)", cat: "mobile_money_fraud",
    text: "Caro cliente, a sua conta M-Pesa foi bloqueada. Envie o seu codigo PIN para reactivar a conta agora." },
  { label: "Prize / 419", cat: "advance_fee_fraud",
    text: "URGENT! Your mobile number won a 2000 prize GUARANTEED. Call 09061790121 to claim before it expires." },
  { label: "Benign", cat: "not_a_scam",
    text: "Hey, are we still meeting for lunch at 1pm tomorrow? Let me know if the time still works." },
];

const $ = (id) => document.getElementById(id);
const msg = $("message"), output = $("output"), runBtn = $("classify");

// examples
const chips = $("chips");
EXAMPLES.forEach((ex) => {
  const c = document.createElement("button");
  c.type = "button";
  c.className = "chip";
  c.style.setProperty("--chip", CATS[ex.cat].color);
  c.innerHTML = `<span class="tag" aria-hidden="true"></span>${ex.label}`;
  c.addEventListener("click", () => { msg.value = ex.text; msg.focus(); });
  chips.appendChild(c);
});

// api readout + health
$("apiReadout").textContent = API_BASE.replace(/^https?:\/\//, "");
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

async function classify() {
  const text = msg.value.trim();
  if (!text) { msg.focus(); return; }

  runBtn.disabled = true;
  runBtn.classList.add("loading");
  runBtn.querySelector(".btn-text").textContent = "Analysing";
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
    runBtn.disabled = false;
    runBtn.classList.remove("loading");
    runBtn.querySelector(".btn-text").textContent = "Classify";
  }
}
runBtn.addEventListener("click", classify);
msg.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === "Enter") classify();
});

function render(data) {
  const top = data.predicted_category;
  const meta = CATS[top] || { name: top, color: "#22c55e", note: "" };

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
    const m = CATS[cat] || { name: cat, color: "#8a97a6" };
    const row = document.createElement("div");
    row.className = "bar-row" + (cat === top ? " win" : "");
    row.style.setProperty("--bc", m.color);
    row.innerHTML = `
      <div class="bar-head"><span class="tag" aria-hidden="true"></span>${m.name}</div>
      <div class="bar-pct">${(score * 100).toFixed(1)}%</div>
      <div class="bar-track"><div class="bar-fill"></div></div>`;
    bars.appendChild(row);
    requestAnimationFrame(() =>
      setTimeout(() => { row.querySelector(".bar-fill").style.width = (score * 100) + "%"; }, 60 + i * 80)
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
    `<div class="err"><strong>Could not reach the classifier.</strong><br>${message}.<br><br>
     Check the API at <code>${API_BASE}</code>, or pass <code>?api=&lt;url&gt;</code>. On the free
     tier the first request can take 30 to 50 seconds to wake up.</div>`;
}
