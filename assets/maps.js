/* Pan-and-zoom world maps. Any <div class="map" data-map="world|mining|forestry|crops"> becomes one. */
(function () {
  var nodes = document.querySelectorAll(".map[data-map]");
  if (!nodes.length) return;

  var SVGNS = "http://www.w3.org/2000/svg";

  // Resource icons, drawn on a 24x24 grid.
  var ICONS = {
    diamond: '<path d="M6 4h12l4 6-10 11L2 10z" fill="#74d7e2" stroke="#1f6f7a"/><path d="M2 10h20M8 4l4 17M16 4l-4 17" stroke="#1f6f7a" stroke-width=".8" fill="none"/>',
    emerald: '<path d="M8 3h8l5 6v6l-5 6H8l-5-6V9z" fill="#3cc46d" stroke="#16603a"/><path d="M9 7h6l2 3v4l-2 3H9l-2-3v-4z" fill="#7be29f"/>',
    lapis: '<path d="M4 8l8-5 8 5v8l-8 5-8-5z" fill="#3f5fcf" stroke="#1d2f77"/><circle cx="10" cy="10" r="1.3" fill="#e6c24c"/><circle cx="14" cy="14" r="1" fill="#e6c24c"/>',
    coal: '<path d="M5 14l2-7 6-3 6 4 1 7-5 5-7-1z" fill="#3b3b3b" stroke="#111"/><path d="M9 9l3-1 2 2" stroke="#777" fill="none"/>',
    iron: '<path d="M3 16l3-7h12l3 7z" fill="#d8b49a" stroke="#7a5a44"/><path d="M6 9l1.5-3h9L18 9" fill="#ead3c2" stroke="#7a5a44"/>',
    gold: '<path d="M3 16l3-7h12l3 7z" fill="#f0cc50" stroke="#8a6a12"/><path d="M6 9l1.5-3h9L18 9" fill="#fbe58f" stroke="#8a6a12"/>',
    copper: '<path d="M3 16l3-7h12l3 7z" fill="#d07a4a" stroke="#6e3517"/><path d="M6 9l1.5-3h9L18 9" fill="#e9a57c" stroke="#6e3517"/>',
    redstone: '<circle cx="8" cy="9" r="3" fill="#c8453c"/><circle cx="15" cy="7" r="2.3" fill="#e0574c"/><circle cx="14" cy="15" r="3.3" fill="#b0342c"/><circle cx="7" cy="17" r="2" fill="#e0574c"/>',
    quartz: '<path d="M8 21V9l3-6 3 6v12z" fill="#f4f1ea" stroke="#8a8474"/><path d="M14 21v-9l3-4 3 4v9z" fill="#e8e4dc" stroke="#8a8474"/>',
    amethyst: '<path d="M7 21l-2-9 4-8 3 9z" fill="#b07ada" stroke="#5a2d7a"/><path d="M12 21l-1-11 4-7 3 8-2 10z" fill="#9a5cc6" stroke="#5a2d7a"/>',
    lava: '<path d="M12 2c4 6 7 9 7 13a7 7 0 0 1-14 0c0-4 3-7 7-13z" fill="#e8602c" stroke="#8a2a0c"/><path d="M12 10c2 3 3 4 3 6a3 3 0 0 1-6 0c0-2 1-3 3-6z" fill="#fbc04a"/>',
    wheat: '<path d="M12 22V6" stroke="#8a6a22" stroke-width="1.5"/><g fill="#e6c65a" stroke="#8a6a22" stroke-width=".7"><ellipse cx="9.5" cy="8" rx="1.8" ry="3" transform="rotate(-25 9.5 8)"/><ellipse cx="14.5" cy="8" rx="1.8" ry="3" transform="rotate(25 14.5 8)"/><ellipse cx="9.5" cy="13" rx="1.8" ry="3" transform="rotate(-25 9.5 13)"/><ellipse cx="14.5" cy="13" rx="1.8" ry="3" transform="rotate(25 14.5 13)"/><ellipse cx="12" cy="4" rx="1.6" ry="2.6"/></g>',
    potato: '<ellipse cx="12" cy="13" rx="8" ry="6" fill="#c39a5e" stroke="#6e4f24"/><circle cx="9" cy="12" r=".9" fill="#6e4f24"/><circle cx="14" cy="15" r=".9" fill="#6e4f24"/><circle cx="15" cy="10.5" r=".8" fill="#6e4f24"/>',
    beetroot: '<path d="M12 21c-5-3-6-7-4-10h8c2 3 1 7-4 10z" fill="#b8324f" stroke="#5e1426"/><path d="M12 11V4M12 8l-4-4M12 8l4-4" stroke="#3f8a3a" stroke-width="1.6" fill="none"/>',
    carrot: '<path d="M6 7l12 3-11 12z" fill="#f08a2a" stroke="#8a4410"/><path d="M17 9l3-5M17 9l5-1" stroke="#3f8a3a" stroke-width="1.6"/>',
    melon: '<circle cx="12" cy="12" r="8.5" fill="#7cc45a" stroke="#2f6a20"/><path d="M12 3.5v17M5 7c4 3 4 7 0 10M19 7c-4 3-4 7 0 10" stroke="#2f6a20" fill="none"/>',
    danger: '<path d="M12 2l10 19H2z" fill="#f5c02e" stroke="#7a4a00"/><path d="M12 8v6" stroke="#222" stroke-width="2.2"/><circle cx="12" cy="17.5" r="1.3" fill="#222"/>'
  };
  var ICON_NAMES = {
    diamond: "Diamond", emerald: "Emerald", lapis: "Lapis lazuli", coal: "Coal", iron: "Iron", gold: "Gold",
    copper: "Copper", redstone: "Redstone", quartz: "Quartz", amethyst: "Amethyst, sulfur & cinnabar", lava: "Lava",
    wheat: "Wheat", potato: "Potato", beetroot: "Beetroot", carrot: "Carrot, pumpkin & more", melon: "Melon & sugar cane",
    danger: "Danger"
  };
  // What each region is known for (its land's rich resources).
  var REGION_ICONS = {
    outer: ["diamond", "redstone", "gold", "potato", "beetroot"],
    north: ["coal", "quartz", "amethyst", "lava", "potato", "beetroot"],
    spider: ["lapis", "potato", "beetroot"],
    bread: ["emerald", "copper", "wheat", "carrot", "melon"],
    rain: ["iron", "wheat"],
    ardcarran: ["coal", "lapis", "emerald", "potato"],
    hell: ["lava", "danger"]
  };
  var NUDGE = { 6: [26, 14], 8: [-18, -14] };
  var LAND_NAMES = { outer: "Outer Isles", north: "Northlands", spider: "Spiderholme Isles", bread: "Breadbasket", rain: "Rainlands", hell: "The Burning Isle" };

  var metaPromise = fetch("maps/maps.json").then(function (r) { return r.json(); });

  function el(tag, attrs, parent) {
    var e = document.createElementNS(SVGNS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function h(tag, cls, parent, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    if (parent) parent.appendChild(e);
    return e;
  }

  nodes.forEach(function (node) {
    metaPromise.then(function (meta) { build(node, meta); });
  });

  function build(node, meta) {
    var kind = node.dataset.map;
    var W = meta.width, H = meta.height;
    var thematic = kind !== "world";

    var wrap = h("div", "map-wrap", node);
    var view = h("div", "map-view", wrap);
    view.style.height = node.dataset.height || "";
    if (thematic) view.style.background = "#dbe9f1";
    var stage = h("div", "map-stage", view);
    stage.style.width = W + "px";
    stage.style.height = H + "px";
    var img = h("img", "map-base", stage);
    img.src = thematic ? "maps/base.jpg" : "maps/world.jpg";
    img.alt = thematic ? "" : "Map of the Caeldun Isles";
    img.draggable = false;

    var group = { mining: ["ores", "minerals"], forestry: ["trees"], crops: ["crops"] }[kind] || [];
    var layers = meta.layers.filter(function (l) { return group.indexOf(l.group) >= 0; });
    var overlayEls = {};
    layers.forEach(function (l) {
      var o = h("img", "map-overlay", stage);
      o.src = "maps/layers/" + l.id + ".png";
      o.alt = "";
      o.draggable = false;
      overlayEls[l.id] = o;
    });

    var svg = el("svg", { class: "map-svg", viewBox: "0 0 " + W + " " + H, width: W, height: H }, stage);
    var markers = [];

    meta.labels.forEach(function (lab) {
      var g = el("g", { class: "map-marker" }, svg);
      var nd = NUDGE[lab.id] || [0, 0];
      var inner = el("g", { transform: "translate(" + nd[0] + " " + nd[1] + ")" }, g);
      var name = lab.name;
      var landKey = lab.id === 14 ? "ardcarran" : lab.land;
      var t = el("text", { class: "map-label" + (lab.land === "hell" ? " hell" : ""), x: 0, y: 0, "text-anchor": "middle" }, inner);
      t.textContent = name;
      if (!thematic) {
        var icons = REGION_ICONS[landKey] || [];
        var size = 17, gap = 2, total = icons.length * size + (icons.length - 1) * gap;
        icons.forEach(function (ic, i) {
          var x = -total / 2 + i * (size + gap);
          var bg = el("rect", { x: x - 1.5, y: 5, width: size + 3, height: size + 3, rx: 3, class: "map-icon-bg" }, inner);
          var ig = el("g", { transform: "translate(" + x + " 6.5) scale(" + (size / 24) + ")" }, inner);
          ig.innerHTML = ICONS[ic];
          var title = el("title", {}, ig);
          title.textContent = ICON_NAMES[ic];
          bg.appendChild(title.cloneNode(true));
        });
      }
      markers.push({ g: g, x: lab.x * W, y: lab.y * H });
    });

    // Controls
    var ctl = h("div", "map-ctl", view);
    var zin = h("button", "", ctl, "+"); zin.setAttribute("aria-label", "Zoom in");
    var zout = h("button", "", ctl, "−"); zout.setAttribute("aria-label", "Zoom out");
    var zfit = h("button", "", ctl, "◎"); zfit.setAttribute("aria-label", "Show whole map"); zfit.title = "Show whole map";
    var zfull = h("button", "", ctl, "⛶"); zfull.setAttribute("aria-label", "Full screen"); zfull.title = "Full screen";
    var coords = h("div", "map-coords", view, "Drag to move · + and − to zoom");
    var hint = h("div", "map-hint", view, "");
    var gate = h("button", "map-gate", view, "Tap to explore the map");
    var touchy = matchMedia("(pointer: coarse)").matches;
    var active = !touchy;
    function setActive(on) {
      active = on;
      view.classList.toggle("active", on);
      gate.hidden = on || !touchy;
    }
    setActive(active);
    gate.addEventListener("click", function () { setActive(true); });
    var hintTimer;
    function showHint(t) {
      hint.textContent = t;
      hint.classList.add("on");
      clearTimeout(hintTimer);
      hintTimer = setTimeout(function () { hint.classList.remove("on"); }, 1400);
    }
    function toggleFull(on) {
      wrap.classList.toggle("map-full", on);
      document.body.classList.toggle("map-open", on);
      zfull.textContent = on ? "✕" : "⛶";
      zfull.title = on ? "Close full screen" : "Full screen";
      if (on) setActive(true); else if (touchy) setActive(false);
      setTimeout(fit, 30);
    }
    zfull.onclick = function () { toggleFull(!wrap.classList.contains("map-full")); };
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && wrap.classList.contains("map-full")) toggleFull(false);
    });

    // Legend / layer panel
    if (!thematic) {
      var leg = h("div", "map-legend", wrap);
      var lands = Object.keys(LAND_NAMES).map(function (k) {
        var c = k === "hell" ? "#5a2a22" : meta.lands[k];
        return '<span><i class="sw" style="background:' + c + '"></i>' + LAND_NAMES[k] + "</span>";
      }).join("");
      var icons = Object.keys(ICON_NAMES).map(function (k) {
        return '<span><svg viewBox="0 0 24 24" width="16" height="16">' + ICONS[k] + "</svg>" + ICON_NAMES[k] + "</span>";
      }).join("");
      leg.innerHTML = '<div class="lg-row"><b>Lands</b>' + lands + '</div><div class="lg-row"><b>Resources</b>' + icons + "</div>";
    } else {
      var panel = h("div", "map-layers", wrap);
      var groups = meta.groups.filter(function (g) { return group.indexOf(g.id) >= 0; });
      var on = (node.dataset.on || "").split(",");
      groups.forEach(function (g) {
        var box = h("div", "ml-group", panel);
        h("div", "ml-h", box, g.label + ' <a href="#" class="ml-all">all</a> · <a href="#" class="ml-none">none</a>');
        h("div", "ml-about", box, g.about);
        var list = h("div", "ml-list", box);
        layers.filter(function (l) { return l.group === g.id; }).forEach(function (l) {
          var lab = h("label", "", list);
          var cb = h("input", "", lab);
          cb.type = "checkbox";
          cb.checked = on.indexOf(l.id) >= 0 || node.dataset.on === "all";
          lab.insertAdjacentHTML("beforeend", '<i class="sw" style="background:' + l.colour + '"></i>' + l.name);
          var set = function () { overlayEls[l.id].style.display = cb.checked ? "" : "none"; };
          cb.addEventListener("change", set);
          set();
        });
        box.querySelector(".ml-all").addEventListener("click", function (e) {
          e.preventDefault();
          list.querySelectorAll("input").forEach(function (c) { c.checked = true; c.dispatchEvent(new Event("change")); });
        });
        box.querySelector(".ml-none").addEventListener("click", function (e) {
          e.preventDefault();
          list.querySelectorAll("input").forEach(function (c) { c.checked = false; c.dispatchEvent(new Event("change")); });
        });
      });
    }

    // Pan / zoom
    var s = 1, tx = 0, ty = 0, minS = 0.1, maxS = 4;
    function fit() {
      var vw = view.clientWidth, vh = view.clientHeight, pad = 36;
      s = Math.min((vw - pad) / W, (vh - pad * 1.5) / H);
      minS = s * 0.8;
      tx = (vw - W * s) / 2;
      ty = (vh - H * s) / 2;
      apply();
    }
    function apply() {
      stage.style.transform = "translate(" + tx + "px," + ty + "px) scale(" + s + ")";
      var k = Math.max(0.62, Math.min(1, view.clientWidth / 820)) / s;
      markers.forEach(function (m) {
        m.g.setAttribute("transform", "translate(" + m.x + " " + m.y + ") scale(" + k + ")");
      });
    }
    function zoomAt(f, cx, cy) {
      var ns = Math.max(minS, Math.min(maxS, s * f));
      f = ns / s;
      tx = cx - (cx - tx) * f;
      ty = cy - (cy - ty) * f;
      s = ns;
      apply();
    }
    function centre() { return [view.clientWidth / 2, view.clientHeight / 2]; }
    zin.onclick = function () { var c = centre(); zoomAt(1.6, c[0], c[1]); };
    zout.onclick = function () { var c = centre(); zoomAt(1 / 1.6, c[0], c[1]); };
    zfit.onclick = fit;

    view.addEventListener("wheel", function (e) {
      var full = wrap.classList.contains("map-full");
      if (!full && !e.ctrlKey && !e.metaKey) {
        showHint("Hold Ctrl (or ⌘) and scroll to zoom, or use + and −");
        return;
      }
      e.preventDefault();
      var r = view.getBoundingClientRect();
      zoomAt(Math.exp(-e.deltaY * 0.0022), e.clientX - r.left, e.clientY - r.top);
    }, { passive: false });

    var pts = {}, last = null;
    view.addEventListener("pointerdown", function (e) {
      if (e.target.closest(".map-ctl, .map-gate")) return;
      if (e.pointerType !== "mouse" && !active) return;
      view.setPointerCapture(e.pointerId);
      pts[e.pointerId] = [e.clientX, e.clientY];
      last = null;
      view.classList.add("dragging");
    });
    view.addEventListener("pointermove", function (e) {
      var r = view.getBoundingClientRect();
      var mx = (e.clientX - r.left - tx) / s, my = (e.clientY - r.top - ty) / s;
      if (mx >= 0 && my >= 0 && mx <= W && my <= H) {
        var bx = Math.round(-meta.blocks[0] / 2 + mx / W * meta.blocks[0]);
        var bz = Math.round(-meta.blocks[1] / 2 + my / H * meta.blocks[1]);
        coords.textContent = "x " + bx + "   z " + bz;
      }
      if (!pts[e.pointerId]) return;
      var prev = pts[e.pointerId];
      pts[e.pointerId] = [e.clientX, e.clientY];
      var ids = Object.keys(pts);
      if (ids.length === 1) {
        tx += e.clientX - prev[0];
        ty += e.clientY - prev[1];
        apply();
      } else if (ids.length === 2) {
        var a = pts[ids[0]], b = pts[ids[1]];
        var d = Math.hypot(a[0] - b[0], a[1] - b[1]);
        var cx = (a[0] + b[0]) / 2 - r.left, cy = (a[1] + b[1]) / 2 - r.top;
        if (last) {
          tx += cx - last.cx;
          ty += cy - last.cy;
          zoomAt(d / last.d, cx, cy);
        }
        last = { d: d, cx: cx, cy: cy };
      }
    });
    function up(e) {
      delete pts[e.pointerId];
      last = null;
      if (!Object.keys(pts).length) view.classList.remove("dragging");
    }
    view.addEventListener("pointerup", up);
    view.addEventListener("pointercancel", up);
    addEventListener("resize", fit);
    if (img.complete) fit(); else img.addEventListener("load", fit);
    fit();
  }
})();
