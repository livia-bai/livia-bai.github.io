/* 2026-10-29《实物大小》：一只直径 3.6 厘米的青花小药盒（从正上方往下看），字写在釉上。
   舞台就是放大镜的镜头：先按实物大小摆着，点一下飞到第一段，一段一段往下看，最后挪开，缩回实物大小。
   中英两版共用这个文件；没有 JS 时，页面上就是普通的几段字。 */
(function () {
  var root = document.querySelector(".ds-tc");
  if (!root || root.classList.contains("ds-tc-on")) return;
  var stage = root.querySelector(".ds-tc-stage");
  var world = root.querySelector(".ds-tc-world");
  var ps = [].slice.call(root.querySelectorAll(".ds-tc-p"));
  if (!stage || !world || !ps.length) return;

  var NS = "http://www.w3.org/2000/svg";
  var W = 2000, C = 1000;                  // 世界坐标：整只盒子 2000 宽，1 毫米约 56
  var D = { x: 170, y: 1000, r: 80 };      // 盒沿那道放盖子的沟里，一汪水
  var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function el(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function grad(defs, id, stops, attrs) {
    var g = el("radialGradient", attrs || {}, defs);
    g.setAttribute("id", id);
    stops.forEach(function (s) {
      el("stop", { offset: s[0], "stop-color": s[1], "stop-opacity": s[2] == null ? 1 : s[2] }, g);
    });
  }
  function pt(r, a) {
    return (C + r * Math.cos(a)).toFixed(1) + "," + (C + r * Math.sin(a)).toFixed(1);
  }

  // ---- 画盒子：口沿、放盖子的沟、内壁、盒底，釉面叫海啃出来的小坑 ----
  var svg = el("svg", { "class": "ds-tc-box", viewBox: "0 0 2000 2000", "aria-hidden": "true", focusable: "false" });
  var defs = el("defs", {}, svg);
  grad(defs, "ds-tc-shadow", [["0.84", "#000", 0.42], ["1", "#000", 0]]);
  grad(defs, "ds-tc-lip", [["0.93", "#d8ddd0"], ["0.985", "#c8cfc1"], ["1", "#aab3a4"]]);
  grad(defs, "ds-tc-wall", [["0.79", "#e1e5da"], ["1", "#b7bfb1"]]);
  grad(defs, "ds-tc-floor", [["0", "#eef0e8"], ["1", "#dce0d5"]], { cx: "0.46", cy: "0.42" });
  grad(defs, "ds-tc-water", [["0", "#eef6f7", 0.15], ["0.75", "#bcd6de", 0.3], ["1", "#9cbfca", 0.6]], { cx: "0.42", cy: "0.4" });

  el("circle", { cx: 1045, cy: 1055, r: 1090, fill: "url(#ds-tc-shadow)" }, svg);
  el("circle", { cx: C, cy: C, r: 1000, fill: "url(#ds-tc-lip)" }, svg);
  // 外壁上的青花，从口沿边上透出一点
  el("circle", { cx: C, cy: C, r: 992, fill: "none", stroke: "#46659a", "stroke-width": 14, opacity: 0.3,
    "stroke-dasharray": "300 110 160 70 420 140 90 60" }, svg);
  el("circle", { cx: C, cy: C, r: 930, fill: "#d4d9cd", stroke: "rgba(80,90,80,.3)", "stroke-width": 6 }, svg);
  el("circle", { cx: C, cy: C, r: 740, fill: "url(#ds-tc-wall)", stroke: "rgba(70,80,70,.35)", "stroke-width": 6 }, svg);
  el("circle", { cx: C, cy: C, r: 590, fill: "url(#ds-tc-floor)" }, svg);
  // 盒里那两小块奶白的三角
  [40, 140].forEach(function (deg) {
    var a = deg * Math.PI / 180, b = 5.5 * Math.PI / 180;
    el("polygon", { points: pt(600, a) + " " + pt(735, a - b) + " " + pt(735, a + b),
      fill: "#efe3c3", stroke: "#d6c79c", "stroke-width": 4, "stroke-linejoin": "round" }, svg);
  });
  var seed = 1752;
  function rnd() { seed = seed * 16807 % 2147483647; return seed / 2147483647; }
  var pits = el("g", {}, svg);
  for (var i = 0; i < 460; i++) {
    var a = rnd() * Math.PI * 2, r = 990 * Math.sqrt(rnd()), s = 3 + rnd() * rnd() * 16;
    el("ellipse", {
      cx: (C + r * Math.cos(a)).toFixed(1), cy: (C + r * Math.sin(a)).toFixed(1),
      rx: s.toFixed(1), ry: (s * (0.5 + rnd() * 0.5)).toFixed(1),
      fill: rnd() < 0.55 ? "rgba(255,255,255,.38)" : "rgba(96,108,94,.16)"
    }, pits);
  }

  // ---- 水滴、弹一下洒出去的几滴、水熊 ----
  var at = el("g", { transform: "translate(" + D.x + " " + D.y + ")" }, svg);
  var drop = el("g", { "class": "ds-tc-drop" }, at);
  el("circle", { r: D.r, fill: "url(#ds-tc-water)", stroke: "rgba(255,255,255,.6)", "stroke-width": 3 }, drop);
  el("ellipse", { cx: -26, cy: -30, rx: 22, ry: 10, fill: "rgba(255,255,255,.6)", transform: "rotate(-35 -26 -30)" }, drop);
  var splash = el("g", { "class": "ds-tc-splash" }, at);
  [[30, -150, 14], [-20, 160, 10], [62, 118, 7], [-55, -112, 8]].forEach(function (d) {
    el("circle", { cx: d[0], cy: d[1], r: d[2], fill: "rgba(200,225,232,.35)", stroke: "rgba(255,255,255,.55)", "stroke-width": 2 }, splash);
  });
  var bear = el("g", { "class": "ds-tc-bear" }, at);
  [-13, -4.5, 4.5, 13].forEach(function (x, k) {
    el("rect", { x: x - 2.2, y: 7, width: 4.4, height: 9, rx: 2.2, fill: "#d9c6a4",
      "class": "ds-tc-leg" + (k % 2 ? " ds-tc-alt" : "") }, bear);
    el("rect", { x: x - 2.2, y: -16, width: 4.4, height: 9, rx: 2.2, fill: "#d9c6a4",
      "class": "ds-tc-leg ds-tc-up" + (k % 2 ? "" : " ds-tc-alt") }, bear);
  });
  el("rect", { x: -19, y: -10, width: 38, height: 20, rx: 10, fill: "#eadcc2", stroke: "#b49c78", "stroke-width": 1.5 }, bear);
  el("ellipse", { cx: -3, cy: 0, rx: 9, ry: 5, fill: "rgba(150,170,110,.45)" }, bear);
  el("circle", { cx: 14, cy: -3.5, r: 1.6, fill: "#3a2f2a" }, bear);
  el("circle", { cx: 14, cy: 3.5, r: 1.6, fill: "#3a2f2a" }, bear);

  world.insertBefore(svg, world.firstChild);

  // ---- 字摆到釉上 ----
  ps.forEach(function (p) {
    var d = p.dataset;
    p.style.left = (+d.x || 0) + "px";
    p.style.top = (+d.y || 0) + "px";
    if (d.w) p.style.width = d.w + "px";
  });
  var runAt = -1, flickAt = -1;
  ps.forEach(function (p, k) {
    if (p.dataset.run && runAt < 0) runAt = k;
    if (p.dataset.flick && flickAt < 0) flickAt = k;
  });

  // ---- 按钮 ----
  var L = { start: root.dataset.start, next: root.dataset.next, last: root.dataset.last };
  function button(text, cls) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = cls;
    b.textContent = text;
    return b;
  }
  var ctrl = document.createElement("div");
  ctrl.className = "ds-tc-ctrl";
  var back = button(root.dataset.back, "ds-tc-btn");
  var next = button(L.start, "ds-tc-btn ds-tc-go");
  back.hidden = true;
  ctrl.appendChild(back);
  ctrl.appendChild(next);
  root.appendChild(ctrl);

  // 3.6 厘米在这块屏幕上有多宽
  var ruler = document.createElement("div");
  ruler.style.cssText = "position:absolute;visibility:hidden;width:3.6cm;height:1px";
  root.appendChild(ruler);
  var actual = (ruler.getBoundingClientRect().width || 136) / W;
  root.removeChild(ruler);

  root.classList.add("ds-tc-on");

  // ---- 镜头 ----
  var step = -1, cam = null, raf = 0, flickTimer = 0;
  function home() { return { x: C, y: C, s: actual }; }
  function target(k) {
    if (k < 0 || k >= ps.length) return home();
    var p = ps[k];
    var b = { l: p.offsetLeft, t: p.offsetTop, r: p.offsetLeft + p.offsetWidth, b: p.offsetTop + p.offsetHeight };
    if (p.dataset.see === "drop") {
      b.l = Math.min(b.l, D.x - D.r); b.r = Math.max(b.r, D.x + D.r);
      b.t = Math.min(b.t, D.y - D.r); b.b = Math.max(b.b, D.y + D.r);
    }
    var sw = stage.clientWidth, sh = stage.clientHeight, pad = 18;
    var s = Math.min(0.85 * (+p.dataset.z || 1), (sw - 2 * pad) / (b.r - b.l), (sh - 2 * pad) / (b.b - b.t));
    return { x: (b.l + b.r) / 2, y: (b.t + b.b) / 2, s: s };
  }
  function apply(c) {
    cam = c;
    world.style.transform = "translate(" + (stage.clientWidth / 2 - c.x * c.s).toFixed(2) + "px," +
      (stage.clientHeight / 2 - c.y * c.s).toFixed(2) + "px) scale(" + c.s.toFixed(5) + ")";
  }
  function fly(to, ms, done) {
    cancelAnimationFrame(raf);
    if (still || !cam) { apply(to); if (done) done(); return; }
    var from = cam, t0 = 0, ls = Math.log(from.s), le = Math.log(to.s);
    function frame(now) {
      if (!t0) t0 = now;
      var t = Math.min(1, (now - t0) / ms);
      var e = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
      apply({ x: from.x + (to.x - from.x) * e, y: from.y + (to.y - from.y) * e, s: Math.exp(ls + (le - ls) * e) });
      if (t < 1) raf = requestAnimationFrame(frame);
      else if (done) done();
    }
    raf = requestAnimationFrame(frame);
  }
  function setDrop(k) { drop.style.transform = "scale(" + k + ")"; }

  function go(k) {
    if (k < 0 || k > ps.length || k === step) return;
    var from = step;
    step = k;
    var reading = k < ps.length;
    root.classList.toggle("ds-tc-reading", reading);
    root.classList.toggle("ds-tc-done", !reading);
    ps.forEach(function (p, j) {
      p.classList.toggle("is-on", j === k);
      p.classList.toggle("is-past", j < k);
    });
    root.classList.toggle("ds-tc-run", reading && runAt >= 0 && k >= runAt);
    var cur = ps[Math.min(k, ps.length - 1)];
    var after = null;
    if (reading && k === flickAt && k > from) {
      // 「叮」：镜头到了再弹，整个国晃一下，湖洒出去一半
      after = function () {
        root.classList.remove("ds-tc-flick");
        void root.offsetWidth;
        root.classList.add("ds-tc-flick");
        clearTimeout(flickTimer);
        flickTimer = setTimeout(function () { root.classList.remove("ds-tc-flick"); }, 600);
        setDrop(+cur.dataset.drop || 1);
        root.classList.add("ds-tc-splashed");
      };
    } else {
      setDrop(+cur.dataset.drop || 1);
      root.classList.toggle("ds-tc-splashed", flickAt >= 0 && k >= flickAt);
    }
    next.textContent = k === ps.length - 1 ? L.last : L.next;
    next.hidden = !reading;
    back.hidden = !(reading && k >= 1);
    fly(target(k), !reading ? 1900 : from < 0 ? 1700 : 1150, after);
  }

  next.addEventListener("click", function () { go(step + 1); });
  back.addEventListener("click", function () { go(step - 1); });
  stage.addEventListener("click", function () { if (step < ps.length) go(step + 1); });
  var rt = 0;
  window.addEventListener("resize", function () {
    clearTimeout(rt);
    rt = setTimeout(function () { cancelAnimationFrame(raf); apply(target(step)); }, 120);
  });

  apply(home());
})();
