// Ein Adventskalender als Single Page App. Die Inhalte kommen aus inhalt.js (window.KALENDER),
// die Bildnachweise aus bilder/nachweise.js (window.NACHWEISE). Seiten: #/ (Übersicht), #/tuer/7, #/bildnachweise.
//
// ?preview        alle Türchen lassen sich öffnen (nur solange der Parameter in der Adresse steht)
// ?datum=2026-12-07  tut so, als wäre heute dieses Datum (zum Testen)
(() => {
  const K = window.KALENDER;
  const NACHWEISE = window.NACHWEISE || {};
  const params = new URLSearchParams(location.search);
  const VORSCHAU = params.has("preview") && params.get("preview") !== "off";

  const app = document.getElementById("app");
  const toastEl = document.getElementById("toast");

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

  const speicher = {
    get(k) { try { return localStorage.getItem(`${K.id}:${k}`); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(`${K.id}:${k}`, v); } catch { /* kein Speicher verfügbar */ } },
  };
  let geoeffnet;
  try { geoeffnet = new Set(JSON.parse(speicher.get("geoeffnet") || "[]")); } catch { geoeffnet = new Set(); }
  // In der Vorschau wird nichts gemerkt, damit die Kinder ihre Türchen später selbst öffnen.
  const merken = (n) => { if (VORSCHAU) return; geoeffnet.add(n); speicher.set("geoeffnet", JSON.stringify([...geoeffnet])); };

  // ---------- Datum ----------
  function heute() {
    const d = params.get("datum");
    const t = d ? new Date(d + "T12:00:00") : new Date();
    return isNaN(t) ? new Date() : t;
  }
  // Im Dezember öffnet jeden Tag ein Türchen, im Januar sind noch alle offen.
  function istOffen(n) {
    if (VORSCHAU) return true;
    const t = heute();
    if (t.getMonth() === 11) return t.getDate() >= n;
    return t.getMonth() === 0;
  }
  function tageBis(n) {
    const t = heute();
    const start = new Date(t.getFullYear(), t.getMonth(), t.getDate());
    const ziel = new Date(t.getFullYear(), 11, n);
    return Math.round((ziel - start) / 864e5);
  }
  const datumText = (n) => `${n}. Dezember`;

  // ---------- Türchen zufällig, aber immer gleich verteilt ----------
  function zufall(seed) {
    let a = 0;
    for (const c of seed) a = (Math.imul(a ^ c.charCodeAt(0), 2654435761) + 1) >>> 0;
    return () => {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const rnd = zufall(K.id + "-tuerchen");
  const reihenfolge = Array.from({ length: 24 }, (_, i) => i + 1);
  for (let i = reihenfolge.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [reihenfolge[i], reihenfolge[j]] = [reihenfolge[j], reihenfolge[i]];
  }
  const form = {};
  reihenfolge.forEach((n) => {
    const r = rnd();
    form[n] = n === 24 ? "gross" : r < 0.16 ? "breit" : r < 0.28 ? "hoch" : "";
  });
  const farbe = (n) => K.farben[Math.floor(zufall(K.id + n)() * K.farben.length)];
  const deko = (n) => K.deko[Math.floor(zufall(K.id + "d" + n)() * K.deko.length)];

  // ---------- Toast ----------
  function toast(text) {
    toastEl.textContent = text;
    toastEl.classList.add("show");
    clearTimeout(toast.t);
    toast.t = setTimeout(() => toastEl.classList.remove("show"), 2600);
  }

  // ---------- Seiten ----------
  const tuer = (n) => K.tueren.find((t) => t.n === n);

  function uebersicht() {
    const t = heute();
    let hinweis = "";
    if (VORSCHAU) hinweis = "Vorschau: Alle Türchen lassen sich öffnen.";
    else if (t.getMonth() < 11 && t.getMonth() > 0) {
      const d = tageBis(1);
      hinweis = d === 1 ? "Morgen geht es los!" : `Noch ${d} Tage, dann öffnet sich das erste Türchen.`;
    } else if (t.getMonth() === 11 && t.getDate() <= 24) hinweis = `Heute darfst du Türchen ${t.getDate()} öffnen!`;
    else hinweis = "Frohe Weihnachten! Alle Türchen sind offen.";

    const tueren = reihenfolge.map((n) => {
      const offen = istOffen(n);
      const schonAuf = offen && geoeffnet.has(n);
      const d = tuer(n);
      const klassen = ["tuer", form[n], offen ? "kann" : "zu", schonAuf ? "auf" : ""].filter(Boolean).join(" ");
      const label = schonAuf ? `Türchen ${n}: ${d.name}` : offen ? `Türchen ${n} öffnen` : `Türchen ${n}, öffnet am ${datumText(n)}`;
      const bild = schonAuf ? `<img src="bilder/klein/${d.bild}.jpg" alt="" loading="lazy">` : "";
      return `<button type="button" class="${klassen}" data-n="${n}" aria-label="${esc(label)}" style="--farbe:${farbe(n)}">
        <span class="innen">${bild}${schonAuf ? `<span class="name">${esc(d.name)}</span>` : ""}</span>
        <span class="klappe"><span class="deko" aria-hidden="true">${deko(n)}</span><span class="zahl">${n}</span></span>
      </button>`;
    }).join("");

    return `<header class="kopf">
        <p class="kicker">${esc(K.untertitel)}</p>
        <h1 tabindex="-1">${esc(K.titel)}</h1>
        <p class="hinweis">${esc(hinweis)}</p>
      </header>
      <div class="raster">${tueren}</div>`;
  }

  function nachweis(d) {
    const q = NACHWEISE[d.bild];
    if (!q) return "";
    return `Bild: ${esc(q.urheber)} · <a href="${esc(q.lizenzUrl)}" target="_blank" rel="noopener">${esc(q.lizenz)}</a>${q.bearbeitung ? ` · ${esc(q.bearbeitung)}` : ""} · <a href="${esc(q.quelle)}" target="_blank" rel="noopener">Quelle</a>`;
  }

  function box(klasse, titel, inhalt) {
    return inhalt ? `<section class="box ${klasse}"><h2>${titel}</h2>${inhalt}</section>` : "";
  }

  function tuerSeite(n) {
    const d = tuer(n);
    const zurueck = n > 1 ? `<a class="knopf" href="#/tuer/${n - 1}">← Türchen ${n - 1}</a>` : "<span></span>";
    const weiter = n < 24 && istOffen(n + 1) ? `<a class="knopf" href="#/tuer/${n + 1}">Türchen ${n + 1} →</a>` : "<span></span>";
    const art = d.art === "fabel" ? `<span class="badge fabel">✨ Fabelwesen</span>` : d.art === "ort" ? `<span class="badge ort">🌍 Naturwunder</span>` : `<span class="badge echt">🐾 Echtes Tier</span>`;
    const quiz = d.quiz ? `<p><strong>${esc(d.quiz.frage)}</strong></p><details><summary>Antwort anzeigen</summary><p>${esc(d.quiz.antwort)}</p></details>` : "";
    return `<article class="seite">
      <nav class="leiste"><a class="knopf" href="#/">← Alle Türchen</a><span class="datum">Türchen ${n} · ${datumText(n)}</span></nav>
      <div class="inhalt">
        <figure class="bild">
          <img src="bilder/${d.bild}.jpg" alt="${esc(d.alt)}">
          <figcaption>${nachweis(d)}</figcaption>
        </figure>
        <div class="text">
          ${art}
          <h1 tabindex="-1">${esc(d.name)}</h1>
          <p class="lead">${esc(d.text)}</p>
          ${box("rekord", d.rekordTitel || "🏆 Weltrekord", d.rekord ? `<p>${esc(d.rekord)}</p>` : "")}
          ${box("sage", "📜 Die Sage", d.sage ? `<p>${esc(d.sage)}</p>` : "")}
          ${box("mitmach", "✋ Mach mit!", d.mitmach ? `<p>${esc(d.mitmach)}</p>` : "")}
          ${box("quiz", "❓ Quizfrage", quiz)}
        </div>
      </div>
      <nav class="blaettern">${zurueck}${weiter}</nav>
    </article>`;
  }

  function zuSeite(n) {
    const tage = tageBis(n);
    const text = tage === 1 ? "Nur noch einmal schlafen!" : tage > 1 ? `Noch ${tage}-mal schlafen!` : "";
    return `<article class="seite zu-seite">
      <nav class="leiste"><a class="knopf" href="#/">← Alle Türchen</a></nav>
      <div class="geschlossen">
        <div class="schloss" aria-hidden="true">🔒</div>
        <h1 tabindex="-1">Türchen ${n} ist noch zu</h1>
        <p>Es öffnet sich am ${datumText(n)}. ${esc(text)}</p>
      </div>
    </article>`;
  }

  function bildnachweise() {
    const zeilen = K.tueren.filter((d) => istOffen(d.n)).map((d) => {
      const q = NACHWEISE[d.bild] || {};
      return `<tr>
        <td>${d.n}</td>
        <td><img src="bilder/klein/${d.bild}.jpg" alt="" loading="lazy"></td>
        <td><strong>${esc(d.name)}</strong><br><span class="klein">${esc(q.datei || "")}</span></td>
        <td>${esc(q.urheber || "")}${q.bearbeitung ? `<br><span class="klein">${esc(q.bearbeitung)}</span>` : ""}</td>
        <td><a href="${esc(q.lizenzUrl)}" target="_blank" rel="noopener">${esc(q.lizenz || "")}</a></td>
        <td><a href="${esc(q.quelle)}" target="_blank" rel="noopener">Wikimedia Commons</a></td>
      </tr>`;
    }).join("");
    const rest = 24 - K.tueren.filter((d) => istOffen(d.n)).length;
    return `<article class="seite nachweise">
      <nav class="leiste"><a class="knopf" href="#/">← Alle Türchen</a></nav>
      <h1 tabindex="-1">Bildnachweise</h1>
      <p>Alle Bilder stammen von <a href="https://commons.wikimedia.org" target="_blank" rel="noopener">Wikimedia Commons</a> und sind frei nutzbar: gemeinfrei (Public Domain, CC0) oder unter einer Creative-Commons-Lizenz, die die Nutzung mit Namensnennung erlaubt. Bilder unter CC BY-SA werden unverändert gezeigt. Die Lizenzangaben jedes Bildes stehen auf seiner Commons-Seite (Link „Wikimedia Commons“). Eine Kopie der Lizenzdaten vom Abruf liegt in <a href="bilder/lizenzen.json">bilder/lizenzen.json</a>.</p>
      ${rest > 0 ? `<p class="klein">Die Bilder hinter den noch geschlossenen Türchen (${rest}) erscheinen hier, sobald ihr Türchen offen ist.</p>` : ""}
      <div class="tabelle"><table>
        <thead><tr><th>Tür</th><th></th><th>Motiv</th><th>Urheber</th><th>Lizenz</th><th>Quelle</th></tr></thead>
        <tbody>${zeilen}</tbody>
      </table></div>
    </article>`;
  }

  // ---------- Router ----------
  function render() {
    const h = location.hash;
    const m = h.match(/^#\/tuer\/(\d{1,2})$/);
    const n = m ? Number(m[1]) : 0;
    if (n >= 1 && n <= 24) {
      if (istOffen(n)) { merken(n); app.innerHTML = tuerSeite(n); document.title = `${tuer(n).name} · ${K.titel}`; }
      else { app.innerHTML = zuSeite(n); document.title = `Türchen ${n} · ${K.titel}`; }
    } else if (h === "#/bildnachweise") {
      app.innerHTML = bildnachweise(); document.title = `Bildnachweise · ${K.titel}`;
    } else {
      app.innerHTML = uebersicht(); document.title = K.titel;
    }
    window.scrollTo({ top: 0 });
    app.querySelector("h1")?.focus({ preventScroll: true });
  }

  app.addEventListener("click", (e) => {
    const b = e.target.closest("button.tuer");
    if (!b) return;
    const n = Number(b.dataset.n);
    if (!istOffen(n)) {
      b.classList.remove("wackeln"); void b.offsetWidth; b.classList.add("wackeln");
      const tage = tageBis(n);
      toast(tage === 1 ? `Türchen ${n}: Nur noch einmal schlafen!` : tage > 1 ? `Türchen ${n}: Noch ${tage}-mal schlafen!` : `Türchen ${n} ist noch zu.`);
      return;
    }
    if (b.classList.contains("auf") || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      location.hash = `#/tuer/${n}`;
      return;
    }
    // Das Türchen geht auf, dann kommt die Seite.
    const d = tuer(n);
    b.querySelector(".innen").innerHTML = `<img src="bilder/klein/${d.bild}.jpg" alt=""><span class="name">${esc(d.name)}</span>`;
    b.classList.add("auf", "oeffnet");
    merken(n);
    setTimeout(() => { location.hash = `#/tuer/${n}`; }, 900);
  });

  document.addEventListener("keydown", (e) => {
    const m = location.hash.match(/^#\/tuer\/(\d{1,2})$/);
    if (!m || e.metaKey || e.ctrlKey || e.altKey) return;
    const n = Number(m[1]);
    if (e.key === "Escape") location.hash = "#/";
    if (e.key === "ArrowLeft" && n > 1) location.hash = `#/tuer/${n - 1}`;
    if (e.key === "ArrowRight" && n < 24 && istOffen(n + 1)) location.hash = `#/tuer/${n + 1}`;
  });

  window.addEventListener("hashchange", render);

  if (VORSCHAU) {
    const b = document.createElement("div");
    b.className = "vorschau-banner";
    b.textContent = "Vorschau: Alle Türchen lassen sich öffnen.";
    document.body.prepend(b);
  }

  render();

  // ---------- Schnee ----------
  // Aus, wenn das Gerät weniger Bewegung wünscht. Der Knopf unten schaltet ihn aus und an, die Wahl bleibt gespeichert.
  (function schnee() {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const knopf = document.getElementById("schnee-knopf");
    const c = document.createElement("canvas");
    c.className = "schnee";
    c.setAttribute("aria-hidden", "true");
    document.body.prepend(c);
    const ctx = c.getContext("2d");
    let w, h, flocken, frame = null;
    const groesse = () => {
      w = c.width = innerWidth; h = c.height = innerHeight;
      flocken = Array.from({ length: Math.min(160, Math.round(w / 9)) }, () => ({
        x: Math.random() * w, y: Math.random() * h, r: 0.8 + Math.random() * 2.6,
        s: 0.3 + Math.random() * 0.9, d: Math.random() * Math.PI * 2,
      }));
    };
    groesse();
    addEventListener("resize", groesse);
    function tick() {
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "rgba(255,255,255,.85)";
      for (const f of flocken) {
        f.y += f.s; f.d += 0.01; f.x += Math.sin(f.d) * 0.35;
        if (f.y > h + 4) { f.y = -4; f.x = Math.random() * w; }
        ctx.beginPath(); ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2); ctx.fill();
      }
      frame = requestAnimationFrame(tick);
    }
    function setzen(an) {
      if (an && frame === null) tick();
      if (!an && frame !== null) { cancelAnimationFrame(frame); frame = null; ctx.clearRect(0, 0, w, h); }
      if (knopf) knopf.textContent = an ? "❄️ Schnee aus" : "❄️ Schnee an";
      try { localStorage.setItem("kinder-advent-schnee", an ? "1" : "0"); } catch { /* kein Speicher verfügbar */ }
    }
    let gespeichert = null;
    try { gespeichert = localStorage.getItem("kinder-advent-schnee"); } catch { /* kein Speicher verfügbar */ }
    setzen(gespeichert !== "0");
    if (knopf) {
      knopf.hidden = false;
      knopf.addEventListener("click", () => setzen(frame === null));
    }
  })();
})();
