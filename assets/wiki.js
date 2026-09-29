(function () {
  var body = document.body;

  // Mobile navigation
  var menu = document.querySelector(".menu-btn");
  menu.addEventListener("click", function () {
    var open = body.classList.toggle("nav-open");
    menu.setAttribute("aria-expanded", open);
  });
  document.addEventListener("click", function (e) {
    if (body.classList.contains("nav-open") && !e.target.closest(".sidebar, .menu-btn")) {
      body.classList.remove("nav-open");
      menu.setAttribute("aria-expanded", false);
    }
  });

  // Keep the current page visible in the sidebar
  var active = document.querySelector(".sidebar a.active");
  if (active) active.scrollIntoView({ block: "center" });

  // Wrap tables so they scroll sideways on phones
  document.querySelectorAll("article table").forEach(function (t) {
    if (t.parentElement.classList.contains("table-wrap")) return;
    var w = document.createElement("div");
    w.className = "table-wrap";
    t.parentNode.insertBefore(w, t);
    w.appendChild(t);
  });

  // Contents box, before the first section heading
  var heads = document.querySelectorAll("article h2[id]");
  if (heads.length > 2 && !document.body.classList.contains("page-home")) {
    var box = document.createElement("nav");
    box.className = "contents";
    box.setAttribute("aria-label", "Contents");
    var html = '<div class="c-h">Contents</div><ol>';
    heads.forEach(function (el) { html += '<li><a href="#' + el.id + '">' + el.textContent + "</a></li>"; });
    box.innerHTML = html + "</ol>";
    var anchor = heads[0];
    while (anchor.parentNode.tagName !== "ARTICLE") anchor = anchor.parentNode;
    anchor.parentNode.insertBefore(box, anchor);
  }

  // Search
  var input = document.getElementById("search");
  var box = document.getElementById("results");
  var index = null, sel = -1;

  function load(cb) {
    if (index) return cb();
    fetch("search-index.json").then(function (r) { return r.json(); })
      .then(function (d) { index = d; cb(); })
      .catch(function () { index = []; cb(); });
  }
  function esc(s) {
    return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }
  function snippet(text, terms) {
    var low = text.toLowerCase(), at = -1;
    for (var i = 0; i < terms.length && at < 0; i++) at = low.indexOf(terms[i]);
    if (at < 0) return "";
    var start = Math.max(0, at - 50), s = text.slice(start, at + 110);
    s = (start ? "…" : "") + esc(s) + "…";
    terms.forEach(function (t) {
      s = s.replace(new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>");
    });
    return s;
  }
  function run() {
    var q = input.value.trim().toLowerCase();
    if (!q) { box.hidden = true; return; }
    var terms = q.split(/\s+/);
    var hits = index.map(function (p) {
      var score = 0, t = p.t.toLowerCase(), hd = p.h.join(" ").toLowerCase(), x = p.x.toLowerCase();
      for (var i = 0; i < terms.length; i++) {
        var w = terms[i], s = 0;
        if (t.indexOf(w) >= 0) s += 10;
        if (hd.indexOf(w) >= 0) s += 4;
        if (x.indexOf(w) >= 0) s += 1 + Math.min(3, x.split(w).length - 2);
        if (!s) return null;
        score += s;
      }
      return { p: p, score: score };
    }).filter(Boolean).sort(function (a, b) { return b.score - a.score; }).slice(0, 8);
    sel = -1;
    box.innerHTML = hits.length ? hits.map(function (h) {
      return '<a href="' + h.p.u + '"><span class="r-t">' + esc(h.p.t) + '</span><span class="r-g">' + esc(h.p.g) +
        '</span><span class="r-x">' + (snippet(h.p.x, terms) || esc(h.p.s)) + "</span></a>";
    }).join("") : '<div class="empty">Nothing found for “' + esc(q) + '”.</div>';
    box.hidden = false;
  }
  input.addEventListener("input", function () { load(run); });
  input.addEventListener("focus", function () { load(function () {}); if (input.value) load(run); });
  input.addEventListener("keydown", function (e) {
    var items = box.querySelectorAll("a");
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!items.length) return;
      sel = (sel + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
      items.forEach(function (a, i) { a.classList.toggle("sel", i === sel); });
    } else if (e.key === "Enter" && items.length) {
      location.href = items[Math.max(sel, 0)].getAttribute("href");
    } else if (e.key === "Escape") {
      box.hidden = true; input.blur();
    }
  });
  document.addEventListener("click", function (e) { if (!e.target.closest(".search")) box.hidden = true; });
  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && document.activeElement !== input && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
      e.preventDefault(); input.focus();
    }
  });
})();
