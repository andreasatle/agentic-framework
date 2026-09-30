// atle.dev — public site behaviour. No framework; progressive enhancement only.
(function () {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- top bar border on scroll ----------
  const topbar = document.querySelector(".topbar");
  const onScroll = () => topbar && topbar.classList.toggle("is-scrolled", window.scrollY > 8);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // ---------- reveal on scroll + animated charts ----------
  const fillCharts = (root) => {
    root.querySelectorAll("[data-fill]").forEach((el) => {
      el.style.width = el.dataset.fill + "%";
    });
  };
  if ("IntersectionObserver" in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add("is-in");
        fillCharts(e.target);
        io.unobserve(e.target);
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
    document.querySelectorAll(".reveal, .js-chart").forEach((el) => io.observe(el));
  } else {
    document.querySelectorAll(".reveal").forEach((el) => el.classList.add("is-in"));
    fillCharts(document);
  }

  // ---------- autoplay videos only while visible ----------
  if ("IntersectionObserver" in window) {
    const vio = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        const v = e.target;
        if (e.isIntersecting && !reduceMotion) { v.play().catch(() => {}); } else { v.pause(); }
      });
    }, { threshold: 0.25 });
    document.querySelectorAll("video[data-autoplay]").forEach((v) => vio.observe(v));
  }

  // ---------- helpers ----------
  function fitCanvas(canvas) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const r = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.round(r.width * dpr));
    canvas.height = Math.max(1, Math.round(r.height * dpr));
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx, w: r.width, h: r.height };
  }
  function whenVisible(el, onChange) {
    if (!("IntersectionObserver" in window)) { onChange(true); return; }
    new IntersectionObserver((es) => es.forEach((e) => onChange(e.isIntersecting))).observe(el);
  }

  // =====================================================================
  // Hero: a tree embedded in the Poincaré disk, panned by a Möbius map.
  // Geodesics are arcs orthogonal to the boundary; the Möbius transform is
  // an isometry, so the tree keeps its shape while we "move through" it.
  // =====================================================================
  function poincare(canvas) {
    const BRANCH = 3, DEPTH = 5, STEP = 0.8; // hyperbolic edge length (shorter = less crowding at the rim)
    const nodes = []; // {r, th, depth, parent}
    (function build(parent, depth, lo, hi) {
      const th = (lo + hi) / 2;
      const idx = nodes.length;
      nodes.push({ r: depth * STEP, th, depth, parent });
      if (depth === DEPTH) return;
      const span = (hi - lo) / BRANCH;
      for (let k = 0; k < BRANCH; k++) build(idx, depth + 1, lo + k * span, lo + (k + 1) * span);
    })(-1, 0, 0, Math.PI * 2);
    const base = nodes.map((n) => {
      const e = Math.tanh(n.r / 2);
      return [e * Math.cos(n.th), e * Math.sin(n.th)];
    });
    const leaves = nodes.map((n, i) => (n.depth === DEPTH ? i : -1)).filter((i) => i >= 0);

    // complex helpers
    const mul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
    const div = (a, b) => { const d = b[0] * b[0] + b[1] * b[1]; return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; };
    const mobius = (z, a) => div([z[0] - a[0], z[1] - a[1]], [1 - (a[0] * z[0] + a[1] * z[1]), -(a[0] * z[1] - a[1] * z[0])]);

    let ctx, w, h, cx, cy, R;
    const resize = () => {
      ({ ctx, w, h } = fitCanvas(canvas));
      const wide = w > 820;
      R = wide ? Math.min(h * 0.44, w * 0.3) : Math.min(w * 0.48, h * 0.4);
      cx = wide ? w * 0.7 : w * 0.5;
      cy = wide ? h * 0.5 : h * 0.36;
    };
    resize();
    window.addEventListener("resize", resize);

    function geodesic(u, v) {
      // circle through u, v and u's inversion in the unit circle
      const uu = u[0] * u[0] + u[1] * u[1];
      if (uu < 1e-6) return null;
      const s = [u[0] / uu, u[1] / uu];
      const ax = u[0], ay = u[1], bx = v[0], by = v[1], sx = s[0], sy = s[1];
      const d = 2 * (ax * (by - sy) + bx * (sy - ay) + sx * (ay - by));
      if (Math.abs(d) < 1e-9) return null;
      const a2 = ax * ax + ay * ay, b2 = bx * bx + by * by, s2 = sx * sx + sy * sy;
      const ox = (a2 * (by - sy) + b2 * (sy - ay) + s2 * (ay - by)) / d;
      const oy = (a2 * (sx - bx) + b2 * (ax - sx) + s2 * (bx - ax)) / d;
      const rr = Math.hypot(ax - ox, ay - oy);
      if (rr > 60) return null; // effectively straight
      return [ox, oy, rr];
    }
    function drawEdge(u, v) {
      const g = geodesic(u, v);
      const X = (p) => cx + p[0] * R, Y = (p) => cy + p[1] * R;
      ctx.beginPath();
      if (!g) { ctx.moveTo(X(u), Y(u)); ctx.lineTo(X(v), Y(v)); ctx.stroke(); return; }
      const [ox, oy, rr] = g;
      let a1 = Math.atan2(u[1] - oy, u[0] - ox), a2 = Math.atan2(v[1] - oy, v[0] - ox);
      let da = a2 - a1;
      while (da > Math.PI) da -= 2 * Math.PI;
      while (da < -Math.PI) da += 2 * Math.PI;
      ctx.arc(cx + ox * R, cy + oy * R, rr * R, a1, a1 + da, da < 0);
      ctx.stroke();
    }

    let t0 = performance.now(), running = true, raf = 0;
    let pathLeaf = leaves[Math.floor(Math.random() * leaves.length)], pathSince = 0;

    function frame(now) {
      const t = (now - t0) / 1000;
      ctx.clearRect(0, 0, w, h);
      // pan: move the "camera" slowly around a circle in the disk
      const rad = 0.3, om = 0.05;
      const a = [rad * Math.cos(om * t), rad * Math.sin(om * t * 1.3)];
      const rot = [Math.cos(t * 0.03), Math.sin(t * 0.03)];
      const P = base.map((z) => mul(mobius(z, a), rot));

      // boundary
      ctx.lineWidth = 1;
      ctx.strokeStyle = "rgba(79,209,197,0.28)";
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.stroke();
      const glow = ctx.createRadialGradient(cx, cy, R * 0.2, cx, cy, R * 1.05);
      glow.addColorStop(0, "rgba(79,209,197,0.05)"); glow.addColorStop(1, "rgba(79,209,197,0)");
      ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fill();

      // growth: depth revealed over the first seconds
      const grown = reduceMotion ? DEPTH + 1 : Math.min(DEPTH + 1, t * 1.4);

      // edges
      for (let i = 1; i < nodes.length; i++) {
        const n = nodes[i];
        const vis = Math.max(0, Math.min(1, grown - n.depth + 1));
        if (vis <= 0) continue;
        const u = P[n.parent], v = P[i];
        const size = 1 - (v[0] * v[0] + v[1] * v[1]); // conformal factor ~ apparent size
        ctx.strokeStyle = `rgba(160,195,215,${(0.2 + 0.6 * size) * vis})`;
        ctx.lineWidth = 0.5 + 1.6 * size;
        drawEdge(u, v);
      }
      // highlighted root→leaf path (a "plan")
      if (t - pathSince > 4.5) { pathLeaf = leaves[Math.floor(Math.random() * leaves.length)]; pathSince = t; }
      const k = Math.min(1, (t - pathSince) / 1.2);
      const chain = [];
      for (let i = pathLeaf; i >= 0; i = nodes[i].parent) chain.push(i);
      chain.reverse();
      const upto = Math.floor(k * (chain.length - 1));
      ctx.strokeStyle = "rgba(245,180,84,0.95)";
      ctx.lineWidth = 2;
      if (grown >= DEPTH) for (let j = 0; j < upto; j++) drawEdge(P[chain[j]], P[chain[j + 1]]);

      // nodes
      for (let i = 0; i < nodes.length; i++) {
        const n = nodes[i];
        const vis = Math.max(0, Math.min(1, grown - n.depth + 1));
        if (vis <= 0) continue;
        const p = P[i];
        const size = 1 - (p[0] * p[0] + p[1] * p[1]);
        const r = 0.8 + 3.6 * size;
        if (r < 0.7) continue;
        ctx.fillStyle = `rgba(79,209,197,${(0.25 + 0.75 * size) * vis})`;
        ctx.beginPath(); ctx.arc(cx + p[0] * R, cy + p[1] * R, r, 0, Math.PI * 2); ctx.fill();
      }
      if (grown >= DEPTH && upto > 0) {
        const p = P[chain[upto]];
        ctx.fillStyle = "#f5b454";
        ctx.beginPath(); ctx.arc(cx + p[0] * R, cy + p[1] * R, 3.5, 0, Math.PI * 2); ctx.fill();
      }
      if (running && !reduceMotion) raf = requestAnimationFrame(frame);
    }
    whenVisible(canvas, (vis) => {
      if (vis && !running) { running = true; raf = requestAnimationFrame(frame); }
      if (!vis) { running = false; cancelAnimationFrame(raf); }
    });
    raf = requestAnimationFrame(frame);
  }

  // =====================================================================
  // Maze card: random spanning-tree maze, BFS wavefront from a start cell.
  // =====================================================================
  function maze(canvas) {
    let ctx, w, h, cols, rows, cell, ox, oy, walls, dist, order, maxd, t0;
    function gen() {
      ({ ctx, w, h } = fitCanvas(canvas));
      cell = Math.max(14, Math.floor(Math.min(w / 22, h / 12)));
      cols = Math.floor((w - 16) / cell); rows = Math.floor((h - 16) / cell);
      ox = (w - cols * cell) / 2; oy = (h - rows * cell) / 2;
      const N = cols * rows;
      walls = Array.from({ length: N }, () => [true, true, true, true]); // N E S W
      const seen = new Uint8Array(N), stack = [0]; seen[0] = 1;
      const nb = (i) => { const x = i % cols, y = (i / cols) | 0, r = [];
        if (y > 0) r.push([i - cols, 0, 2]); if (x < cols - 1) r.push([i + 1, 1, 3]);
        if (y < rows - 1) r.push([i + cols, 2, 0]); if (x > 0) r.push([i - 1, 3, 1]); return r; };
      while (stack.length) {
        const c = stack[stack.length - 1];
        const opts = nb(c).filter(([j]) => !seen[j]);
        if (!opts.length) { stack.pop(); continue; }
        const [j, d, od] = opts[(Math.random() * opts.length) | 0];
        walls[c][d] = false; walls[j][od] = false; seen[j] = 1; stack.push(j);
      }
      const start = ((rows / 2) | 0) * cols + ((cols / 2) | 0);
      dist = new Int32Array(N).fill(-1); dist[start] = 0; order = [start];
      for (let q = 0; q < order.length; q++) {
        const c = order[q];
        nb(c).forEach(([j, d]) => { if (!walls[c][d] && dist[j] < 0) { dist[j] = dist[c] + 1; order.push(j); } });
      }
      maxd = dist[order[order.length - 1]];
      t0 = performance.now();
    }
    gen();
    let running = true, raf = 0;
    function frame(now) {
      const front = reduceMotion ? maxd : ((now - t0) / 1000) * 14;
      if (front > maxd + 30) { gen(); }
      ctx.clearRect(0, 0, w, h);
      for (let i = 0; i < walls.length; i++) {
        const x = ox + (i % cols) * cell, y = oy + ((i / cols) | 0) * cell;
        const d = dist[i];
        if (d <= front) {
          const age = front - d;
          const a = Math.max(0.12, 1 - age / 40);
          ctx.fillStyle = age < 2 ? `rgba(245,180,84,${0.9})` : `rgba(79,209,197,${0.45 * a})`;
          ctx.fillRect(x + 1, y + 1, cell - 2, cell - 2);
        }
      }
      ctx.strokeStyle = "rgba(170,180,192,0.55)"; ctx.lineWidth = 1.2; ctx.beginPath();
      for (let i = 0; i < walls.length; i++) {
        const x = ox + (i % cols) * cell, y = oy + ((i / cols) | 0) * cell, wl = walls[i];
        if (wl[0]) { ctx.moveTo(x, y); ctx.lineTo(x + cell, y); }
        if (wl[3]) { ctx.moveTo(x, y); ctx.lineTo(x, y + cell); }
        if (wl[1] && i % cols === cols - 1) { ctx.moveTo(x + cell, y); ctx.lineTo(x + cell, y + cell); }
        if (wl[2] && ((i / cols) | 0) === rows - 1) { ctx.moveTo(x, y + cell); ctx.lineTo(x + cell, y + cell); }
      }
      ctx.stroke();
      if (running && !reduceMotion) raf = requestAnimationFrame(frame);
    }
    window.addEventListener("resize", () => { gen(); if (!running || reduceMotion) requestAnimationFrame(frame); });
    whenVisible(canvas, (vis) => {
      if (vis && !running) { running = true; raf = requestAnimationFrame(frame); }
      if (!vis) { running = false; cancelAnimationFrame(raf); }
    });
    raf = requestAnimationFrame(frame);
  }

  document.querySelectorAll("canvas[data-viz='poincare']").forEach(poincare);
  document.querySelectorAll("canvas[data-viz='maze']").forEach(maze);
})();
