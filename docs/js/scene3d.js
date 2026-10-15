import * as THREE from "three";
import { COPILOTS, SHOTS, ANGLES, MOVES, CHARS, STYLES } from "./data.js";
import { CATALOG } from "./catalog.js";

const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function tagSprite(icon, text, color, w = 5, sub = "", depthTest = false) {
  const H = sub ? 160 : 128, c = document.createElement("canvas");
  c.width = 512; c.height = H;
  const g = c.getContext("2d");
  g.fillStyle = "rgba(10,12,24,.76)";
  g.beginPath(); g.roundRect(4, 8, 504, H - 16, 40); g.fill();
  g.strokeStyle = color; g.lineWidth = 3; g.stroke();
  g.fillStyle = "#fff"; g.textBaseline = "middle";
  g.font = "600 40px 'Segoe UI','Yu Gothic UI',sans-serif";
  g.fillText(icon, 26, sub ? 56 : H / 2);
  g.fillText(text, 86, sub ? 56 : H / 2, 400);
  if (sub) { g.fillStyle = color; g.font = "600 26px 'Segoe UI','Yu Gothic UI',sans-serif"; g.fillText(sub, 86, 112, 400); }
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false, depthTest }));
  sp.scale.set(w, w * H / 512, 1);
  sp.renderOrder = 10;
  return sp;
}

const $ = (s, r = document) => r.querySelector(s);
const rad = d => d * Math.PI / 180;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const lerp = (a, b, t) => a + (b - a) * t;
const ease = f => (f < .5 ? 4 * f * f * f : 1 - Math.pow(-2 * f + 2, 3) / 2);
const ns = (t, s) => (Math.sin(t * 1.7 + s) + Math.sin(t * 2.9 + s * 2.1) * .6 + Math.sin(t * 5.3 + s * .7) * .3) / 1.9;

const SIZE = { EWS: { d: 46, f: 60 }, WS: { d: 28, f: 55 }, FS: { d: 18, f: 52 }, MS: { d: 12, f: 50 }, MCU: { d: 8.5, f: 48 }, CU: { d: 5.5, f: 46 }, ECU: { d: 3.2, f: 42 } };
const POVFOV = { EWS: 95, WS: 80, FS: 65, MS: 55, MCU: 45, CU: 32, ECU: 18 };
const ANG = { eye: { el: 4, roll: 0 }, low: { el: -16, roll: 0 }, high: { el: 35, roll: 0 }, bird: { el: 82, roll: 0 }, worm: { el: -68, roll: 0 }, dutch: { el: 8, roll: 18 }, ots: { el: 8, roll: 0 }, pov: { el: 0, roll: 0 } };
const CHAR = {
  locked: { k: 0, d: 20, n: 0 }, gentle: { k: .45, d: 3, n: 0 }, smooth: { k: 1, d: 4, n: 0 }, floating: { k: .7, d: 2.5, n: 0, float: 1 },
  organic: { k: .9, d: 5, n: .012 }, energetic: { k: 1.6, d: 7, n: 0 }, snappy: { k: 1.4, d: 12, n: 0, snap: 1 },
  aggressive: { k: 2.2, d: 14, n: .03 }, hyper: { k: 3.6, d: 18, n: .015 }, impossible: { k: 2, d: 9, n: 0, imp: 1 }
};

function glowTexture() {
  const c = document.createElement("canvas"); c.width = c.height = 128;
  const g = c.getContext("2d"), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(.25, "rgba(255,255,255,.45)"); gr.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}

function labelSprite(cp) {
  const c = document.createElement("canvas"); c.width = 512; c.height = 128;
  const g = c.getContext("2d");
  g.fillStyle = "rgba(10,12,24,.72)";
  g.beginPath(); g.roundRect(4, 20, 504, 88, 44); g.fill();
  g.strokeStyle = cp.color; g.lineWidth = 3; g.stroke();
  g.fillStyle = "#fff"; g.textBaseline = "middle"; g.font = "600 40px 'Segoe UI','Yu Gothic UI',sans-serif";
  g.fillText(cp.emoji, 28, 66);
  g.fillText(cp.name, 90, 66, 400);
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false, depthTest: false }));
  sp.scale.set(6, 1.5, 1);
  sp.renderOrder = 10;
  return sp;
}

function geometryFor(shape) {
  switch (shape) {
    case "octahedron": return new THREE.OctahedronGeometry(1.7);
    case "dodecahedron": return new THREE.DodecahedronGeometry(1.6);
    case "torusknot": return new THREE.TorusKnotGeometry(1.1, .38, 120, 16);
    case "sphere": return new THREE.SphereGeometry(1.5, 48, 32);
    case "wire": return new THREE.IcosahedronGeometry(1.7, 1);
    default: return new THREE.IcosahedronGeometry(1.6, 0);
  }
}

export async function initScene(api) {
  const { state, save, addXP, toast, burst, openLesson, checkBadges } = api;
  const stage = $("#stage");
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  stage.append(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x05060d);
  scene.fog = new THREE.FogExp2(0x05060d, 0.0105);
  const camera = new THREE.PerspectiveCamera(55, 1, .1, 600);
  const glow = glowTexture();

  scene.add(new THREE.AmbientLight(0x8890ff, .7));
  const core = new THREE.PointLight(0xffffff, 90, 60, 1.6);
  scene.add(core);

  /* Starfield */
  {
    const n = 2600, pos = new Float32Array(n * 3), col = new Float32Array(n * 3), c = new THREE.Color();
    for (let i = 0; i < n; i++) {
      const r = 70 + Math.random() * 160, th = Math.random() * Math.PI * 2, ph = Math.acos(2 * Math.random() - 1);
      pos.set([r * Math.sin(ph) * Math.cos(th), r * Math.cos(ph), r * Math.sin(ph) * Math.sin(th)], i * 3);
      c.setHSL(.55 + Math.random() * .3, .7, .6 + Math.random() * .3); col.set([c.r, c.g, c.b], i * 3);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setAttribute("color", new THREE.BufferAttribute(col, 3));
    var stars = new THREE.Points(g, new THREE.PointsMaterial({ size: 1.3, vertexColors: true, fog: false, transparent: true, opacity: .9, sizeAttenuation: false }));
    scene.add(stars);
  }

  /* Hub */
  const hub = new THREE.Group();
  scene.add(hub);
  const coreMesh = new THREE.Mesh(new THREE.IcosahedronGeometry(1.1, 2), new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0x8aa0ff, emissiveIntensity: 1.4, roughness: .2 }));
  hub.add(coreMesh);
  const coreHalo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, color: 0x8aa0ff, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true }));
  coreHalo.scale.setScalar(9); hub.add(coreHalo);
  const rings = [2.6, 3.4, 4.3].map((r, i) => {
    const m = new THREE.Mesh(new THREE.TorusGeometry(r, .03, 8, 120), new THREE.MeshBasicMaterial({ color: [0x7f85f5, 0x00b7c3, 0xff4fa3][i] }));
    m.rotation.set(i * 1.0, i * .6, 0); hub.add(m); return m;
  });
  const grid = new THREE.GridHelper(120, 60, 0x4b55c8, 0x1b2050);
  grid.position.y = -10; grid.material.transparent = true; grid.material.opacity = .35;
  scene.add(grid);
  // orbit track
  const track = new THREE.Mesh(new THREE.RingGeometry(11.9, 12.05, 160), new THREE.MeshBasicMaterial({ color: 0x5a64ff, transparent: true, opacity: .35, side: THREE.DoubleSide }));
  track.rotation.x = Math.PI / 2; scene.add(track);

  /* Copilot nodes */
  const nodes = COPILOTS.map((cp, i) => {
    const grp = new THREE.Group();
    const a = i / COPILOTS.length * Math.PI * 2;
    grp.position.set(Math.sin(a) * 12, Math.sin(i * 1.7) * 2.5, Math.cos(a) * 12);
    const col = new THREE.Color(cp.color);
    const wire = cp.shape === "wire";
    const mat = new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: .45, metalness: .55, roughness: .25, wireframe: wire, flatShading: !wire && cp.shape !== "sphere" && cp.shape !== "torusknot" });
    const mesh = new THREE.Mesh(geometryFor(cp.shape), mat);
    grp.add(mesh);
    if (wire) grp.add(new THREE.Mesh(new THREE.SphereGeometry(.9, 24, 16), new THREE.MeshStandardMaterial({ color: new THREE.Color(cp.color2), emissive: new THREE.Color(cp.color2), emissiveIntensity: .9 })));
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, color: col, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: .8 }));
    halo.scale.setScalar(8); grp.add(halo);
    const label = labelSprite(cp); label.position.y = 3.3; grp.add(label);
    const hit = new THREE.Mesh(new THREE.SphereGeometry(2.4, 8, 8), new THREE.MeshBasicMaterial({ visible: false }));
    hit.userData.node = i; grp.add(hit);
    const light = new THREE.PointLight(col, 25, 18, 1.8); grp.add(light);
    const sats = [0, 1, 2].map(j => {
      const s = new THREE.Mesh(new THREE.SphereGeometry(.16, 12, 12), new THREE.MeshBasicMaterial({ color: new THREE.Color(cp.color2) }));
      s.userData = { r: 2.5 + j * .55, sp: .8 + j * .5, ph: j * 2.1 };
      grp.add(s); return s;
    });
    scene.add(grp);
    return { cp, grp, mesh, mat, halo, label, hit, sats, base: grp.position.clone(), ph: i * 1.3, scale: 1 };
  });
  const selRing = new THREE.Mesh(new THREE.TorusGeometry(2.7, .05, 8, 80), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0 }));
  scene.add(selRing);

  /* ---------- Prompt Galaxy (sample prompt catalog) ---------- */
  const gal = new THREE.Group();
  gal.visible = false;
  scene.add(gal);
  const galCore = new THREE.Mesh(new THREE.IcosahedronGeometry(1.8, 2), new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffd24a, emissiveIntensity: 1.2, roughness: .3 }));
  gal.add(galCore);
  const galHalo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, color: 0xffd24a, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true }));
  galHalo.scale.setScalar(14); gal.add(galHalo);
  const galTitle = tagSprite("📚", "サンプルPrompt", "#ffd24a", 7);
  galTitle.position.y = 3.8; gal.add(galTitle);
  [13, 28].forEach(r => {
    const ring = new THREE.Mesh(new THREE.RingGeometry(r - .06, r + .06, 160), new THREE.MeshBasicMaterial({ color: 0x5a64ff, transparent: true, opacity: .3, side: THREE.DoubleSide }));
    ring.rotation.x = Math.PI / 2; gal.add(ring);
  });
  const shapes = [s => new THREE.IcosahedronGeometry(s), s => new THREE.OctahedronGeometry(s * 1.1), s => new THREE.DodecahedronGeometry(s), s => new THREE.SphereGeometry(s, 32, 24), s => new THREE.TorusKnotGeometry(s * .7, s * .25, 80, 12)];
  const nPersona = CATALOG.filter(c => c.kind === "persona").length, nTopic = CATALOG.length - nPersona;
  let pi = 0, ti = 0;
  const cats = CATALOG.map((meta, i) => {
    const big = meta.kind === "persona";
    let a, r, y;
    if (big) { a = pi / nPersona * Math.PI * 2; r = 13; y = Math.sin(pi * 1.7) * 1.6; pi++; }
    else { a = (ti + .5) / nTopic * Math.PI * 2; r = 28; y = Math.sin(ti * 1.3) * 4; ti++; }
    const grp = new THREE.Group();
    grp.position.set(Math.sin(a) * r, y, Math.cos(a) * r);
    const col = new THREE.Color(meta.color), size = big ? 2.1 : 1.3;
    const mat = new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: .5, metalness: .5, roughness: .3, flatShading: true });
    const mesh = new THREE.Mesh(shapes[i % shapes.length](size), mat);
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, color: col, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: .8 }));
    halo.scale.setScalar(big ? 9 : 6);
    const label = tagSprite(meta.icon, meta.dir, meta.color, big ? 7 : 5.4, big ? "職種：" + meta.role : "");
    label.position.y = size + (big ? 2.2 : 1.7);
    const hit = new THREE.Mesh(new THREE.SphereGeometry(size * 1.5, 8, 8), new THREE.MeshBasicMaterial({ visible: false }));
    hit.userData.gcat = i;
    grp.add(mesh, halo, label, hit);
    gal.add(grp);
    return { meta, i, grp, mesh, mat, halo, label, hit, base: grp.position.clone(), ph: i * .9, k: 0, scale: 1, built: false, fileGrp: null, files: [], big };
  });
  {
    const sp = [];
    cats.forEach(c => sp.push(0, 0, 0, c.base.x, c.base.y, c.base.z));
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(sp), 3));
    gal.add(new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0x6670ff, transparent: true, opacity: .16 })));
  }
  function buildFiles(c) {
    c.built = true;
    c.fileGrp = new THREE.Group();
    c.fileGrp.visible = false; c.fileGrp.scale.setScalar(.001);
    c.grp.add(c.fileGrp);
    const files = c.meta.files, n = files.length, R = 4.5 + Math.sqrt(n) * .55;
    const groups = [...new Set(files.map(f => f.group))];
    const lines = [];
    files.forEach((f, j) => {
      const y = n === 1 ? 0 : 1 - (j / (n - 1)) * 2, rr = Math.sqrt(1 - y * y), th = j * 2.399963;
      const pos = new THREE.Vector3(Math.cos(th) * rr, y, Math.sin(th) * rr).multiplyScalar(R);
      const readme = f.path === "README.md";
      const col = new THREE.Color(c.meta.color).offsetHSL(groups.indexOf(f.group) * .08, 0, readme ? .18 : 0);
      const grp = new THREE.Group();
      grp.position.copy(pos);
      const mat = new THREE.MeshStandardMaterial({ color: col, emissive: col, emissiveIntensity: .7, metalness: .4, roughness: .3, flatShading: true });
      const mesh = new THREE.Mesh(readme ? new THREE.DodecahedronGeometry(.5) : new THREE.OctahedronGeometry(.45), mat);
      const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, color: col, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: .7 }));
      halo.scale.setScalar(2.8);
      const label = tagSprite(readme ? "📖" : "📝", f.title, "#" + col.getHexString(), 4.4, "", true);
      label.position.y = 1;
      const hit = new THREE.Mesh(new THREE.SphereGeometry(.85, 8, 8), new THREE.MeshBasicMaterial({ visible: false }));
      hit.userData.gfile = { c: c.i, f: j };
      grp.add(mesh, halo, label, hit);
      c.fileGrp.add(grp);
      c.files.push({ f, grp, mesh, mat, label, hit, sc: 1 });
      lines.push(0, 0, 0, pos.x, pos.y, pos.z);
    });
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(lines), 3));
    c.fileGrp.add(new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: new THREE.Color(c.meta.color), transparent: true, opacity: .25 })));
  }

  /* Collectible orbs */
  const orbs = [];
  const orbGeo = new THREE.SphereGeometry(.32, 16, 16);
  function spawnOrb(o) {
    const a = Math.random() * Math.PI * 2, r = 5 + Math.random() * 18;
    const col = new THREE.Color().setHSL(Math.random(), .9, .65);
    if (!o) {
      o = { mesh: new THREE.Mesh(orbGeo, new THREE.MeshBasicMaterial({ color: col })), halo: new THREE.Sprite(new THREE.SpriteMaterial({ map: glow, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true })), t: 0 };
      o.mesh.add(o.halo); o.mesh.userData.orb = o; scene.add(o.mesh); orbs.push(o);
    }
    o.mesh.material.color.copy(col); o.halo.material.color.copy(col); o.halo.scale.setScalar(4);
    o.base = new THREE.Vector3(Math.sin(a) * r, -5 + Math.random() * 13, Math.cos(a) * r);
    o.ph = Math.random() * 6; o.alive = true; o.pop = 1; o.mesh.visible = true;
    return o;
  }
  for (let i = 0; i < 16; i++) spawnOrb();
  $("#orbCount").textContent = state.orbs;

  /* 3D particle bursts */
  let bursts = [];
  function burst3(pos, color, n = 70) {
    const p = new Float32Array(n * 3), v = [];
    for (let i = 0; i < n; i++) { p.set([pos.x, pos.y, pos.z], i * 3); v.push(new THREE.Vector3().randomDirection().multiplyScalar(3 + Math.random() * 8)); }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(p, 3));
    const m = new THREE.PointsMaterial({ size: .35, color, map: glow, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true });
    const pts = new THREE.Points(g, m); scene.add(pts);
    bursts.push({ pts, v, life: 1.4 });
  }

  /* ---------------- Camera director ---------------- */
  const sel = { i: -1 };
  const target = new THREE.Vector3();
  const user = { az: 0, el: 0, zoom: 1 };
  const cur = { pos: new THREE.Vector3(0, 6, 40), look: new THREE.Vector3(), roll: 0, fov: 55 };
  const want = { pos: new THREE.Vector3(), look: new THREE.Vector3(), roll: 0, fov: 55 };
  let style = STYLES.find(s => s.id === "corporate");
  let shots = style.shots.slice(), shotIdx = 0, shotT = 0, clock = 0, tour = false, tourT = 0;
  let custom = false;

  function pose(shot, t, out) {
    const S = SIZE[shot.size], A = ANG[shot.angle], C = CHAR[shot.char];
    const locked = shot.char === "locked";
    const kt0 = locked ? 0 : t * C.k;
    const kt = C.snap ? Math.floor(kt0) + ease(kt0 - Math.floor(kt0)) : kt0;
    const pp = .5 - .5 * Math.cos(kt * .6);
    const hubTarget = sel.i < 0;
    const tg = target;
    const az0 = hubTarget ? 0 : Math.atan2(tg.x, tg.z);
    const m = { az: 0, dm: 1, lat: 0, ped: 0, roll: 0, fovm: 1, lookR: 0, lookU: 0, el: 0 };
    const mv = locked ? "static" : shot.move;
    switch (mv) {
      case "pan": m.lookR = Math.sin(kt * .5) * S.d * .45; break;
      case "tilt": m.lookU = Math.sin(kt * .5) * S.d * .35; break;
      case "dollyIn": m.dm = lerp(1.3, .55, pp); break;
      case "dollyOut": m.dm = lerp(.55, 1.3, pp); break;
      case "truck": m.lat = Math.sin(kt * .5) * S.d * .7; break;
      case "pedestal": m.ped = Math.sin(kt * .5) * S.d * .4; break;
      case "orbit": m.az = kt * .35; break;
      case "crane": m.ped = (pp - .5) * S.d * 1.2; m.dm = lerp(1.2, .8, pp); m.el = (pp - .5) * 30; break;
      case "handheld": m.lat = ns(t, 1) * S.d * .02; m.ped = ns(t, 2) * S.d * .02; m.roll = ns(t, 3) * .02; break;
      case "gimbal": m.az = Math.sin(kt * .3) * .25; m.ped = Math.sin(kt * .6) * S.d * .04; break;
      case "whip": {
        const T = kt / 3, cyc = Math.floor(T), w = T - cyc;
        m.az = (cyc + ease(clamp(w / .18, 0, 1))) * Math.PI * 2 / 3;
        m.fovm = 1 + Math.sin(clamp(w / .18, 0, 1) * Math.PI) * .25;
        break;
      }
      case "zoom": m.fovm = lerp(1.3, .55, pp); break;
      case "dollyZoom": m.dm = lerp(1.6, .5, pp); break;
      case "roll": m.roll = kt * .4; break;
      default: break;
    }
    if (!locked && C.float) { m.ped += Math.sin(t * .9) * S.d * .03; m.lat += Math.cos(t * .7) * S.d * .04; m.az += Math.sin(t * .5) * .05; }
    if (!locked && C.imp) { m.dm *= 1 + .45 * Math.sin(t * 1.7); m.roll += Math.sin(t * .9) * .8; m.az += Math.sin(t * 1.3) * .6; }

    const az = az0 + m.az + user.az;
    const el = clamp(rad(A.el + m.el) + user.el, -1.5, 1.5);
    const dist = S.d * m.dm * user.zoom;
    const dir = new THREE.Vector3(Math.sin(az), 0, Math.cos(az));
    const right = new THREE.Vector3(Math.cos(az), 0, -Math.sin(az));
    const up = new THREE.Vector3(0, 1, 0);
    let fov = S.f * m.fovm;
    if (mv === "dollyZoom") fov = 2 * Math.atan(Math.tan(rad(S.f) / 2) / m.dm) * 180 / Math.PI;

    if (mv === "fpv") {
      const R = 8 + S.d * .5, a = kt * .25, P = b => new THREE.Vector3(Math.cos(b) * R * (1 + .2 * Math.sin(3 * b)), 4 * Math.sin(2 * b) + A.el * .1, Math.sin(b) * R * (1 + .2 * Math.cos(2 * b)));
      out.pos.copy(P(a)); out.look.copy(P(a + .12)); out.roll = Math.sin(a * 3) * .3 + rad(A.roll); out.fov = S.f * (C.k > 3 ? 1.15 : 1);
      return;
    }
    if (shot.angle === "pov") {
      if (hubTarget || world === "galaxy") out.pos.copy(tg).addScaledVector(dir, 14).addScaledVector(up, .8);
      else out.pos.copy(tg).multiplyScalar(.2).addScaledVector(up, .6);
      out.pos.addScaledVector(right, m.lat);
      out.look.copy(tg).addScaledVector(right, m.lookR).addScaledVector(up, m.lookU);
      out.roll = m.roll; out.fov = POVFOV[shot.size] * m.fovm;
      return;
    }
    out.pos.copy(tg).addScaledVector(dir, Math.cos(el) * dist).addScaledVector(up, Math.sin(el) * dist).addScaledVector(right, m.lat + (shot.angle === "ots" ? dist * .3 : 0)).addScaledVector(up, m.ped);
    out.look.copy(tg).addScaledVector(right, m.lookR).addScaledVector(up, m.lookU);
    out.roll = rad(A.roll) + m.roll;
    out.fov = fov;
  }

  const fmt = s => `${SHOTS[s.size]} + ${ANGLES[s.angle]} + ${MOVES[s.move]} + ${CHARS[s.char]}`;
  function syncUI() {
    const s = shots[shotIdx];
    $("#selSize").value = s.size; $("#selAngle").value = s.angle; $("#selMove").value = s.move; $("#selChar").value = s.char;
    $("#formula").textContent = fmt(s) + (shots.length > 1 ? `   (${shotIdx + 1}/${shots.length})` : "");
  }
  function trackCam(key) {
    if (!state.cams.includes(key)) { state.cams.push(key); save(); checkBadges(); }
  }
  function setStyle(id) {
    style = STYLES.find(s => s.id === id); custom = false;
    shots = style.shots.slice(); shotIdx = 0; shotT = 0;
    user.az = user.el = 0; user.zoom = 1;
    document.querySelectorAll("#styleChips button").forEach(b => b.classList.toggle("on", b.dataset.id === id));
    $("#goal").textContent = `🎯 ${style.goal}`;
    syncUI(); trackCam("style:" + id);
    burst3(cur.look, 0x8aa0ff, 40);
  }
  function setCustom(shot) {
    custom = true; shots = [shot]; shotIdx = 0; shotT = 0;
    document.querySelectorAll("#styleChips button").forEach(b => b.classList.remove("on"));
    $("#goal").textContent = "🎯 オリジナル構成";
    syncUI(); trackCam("custom:" + Object.values(shot).join("-"));
  }

  // UI build
  $("#styleChips").innerHTML = STYLES.map(s => `<button data-id="${s.id}" title="${s.goal}">${s.icon} ${s.name.split(" / ")[0]}</button>`).join("");
  const fill = (id, obj) => { $(id).innerHTML = Object.entries(obj).map(([k, v]) => `<option value="${k}">${v}</option>`).join(""); };
  fill("#selSize", SHOTS); fill("#selAngle", ANGLES); fill("#selMove", MOVES); fill("#selChar", CHARS);
  $("#styleChips").onclick = e => { const b = e.target.closest("button"); if (b) setStyle(b.dataset.id); };
  ["#selSize", "#selAngle", "#selMove", "#selChar"].forEach(id => $(id).onchange = () => setCustom({ size: $("#selSize").value, angle: $("#selAngle").value, move: $("#selMove").value, char: $("#selChar").value }));
  const pick = o => { const k = Object.keys(o); return k[Math.floor(Math.random() * k.length)]; };
  $("#dice").onclick = () => { setCustom({ size: pick(SHOTS), angle: pick(ANGLES), move: pick(MOVES), char: pick(CHARS) }); toast("🎲 " + fmt(shots[0])); };
  $("#autoTour").onclick = () => {
    tour = !tour; tourT = 0;
    $("#autoTour").textContent = tour ? "⏹ ツアー停止" : "🎬 オートツアー";
    toast(tour ? "🎬 オートツアー開始：スタイルと対象が自動で切り替わります" : "ツアーを停止しました");
  };
  $("#camToggle").onclick = () => {
    const p = $("#camPanel"); p.classList.toggle("min");
    $("#camToggle").setAttribute("aria-expanded", !p.classList.contains("min"));
  };

  function select(i) {
    sel.i = i;
    if (i < 0) { target.set(0, 0, 0); $("#hudTitle").textContent = "Copilot Hub"; selRing.material.opacity = 0; }
    else {
      target.copy(nodes[i].base);
      $("#hudTitle").textContent = `${nodes[i].cp.emoji} ${nodes[i].cp.name}`;
      selRing.material.color.set(nodes[i].cp.color);
      burst3(nodes[i].base, new THREE.Color(nodes[i].cp.color), 90);
      addXP(1);
    }
    document.querySelectorAll("#dock button").forEach(b => b.classList.toggle("on", +b.dataset.i === i));
  }
  function buildDock() {
    $("#dock").innerHTML = world === "galaxy"
      ? `<button data-g="-1" class="on" style="--c:#fff">🌌 全体</button>` + cats.map((c, i) => `<button data-g="${i}" style="--c:${c.meta.color}">${c.meta.icon} ${esc(c.meta.dir)}</button>`).join("")
      : `<button data-i="-1" class="on" style="--c:#fff">🌌 Hub</button>` + COPILOTS.map((c, i) => `<button data-i="${i}" style="--c:${c.color}">${c.emoji} ${c.name.replace("Microsoft 365 ", "M365 ")}</button>`).join("");
  }
  $("#dock").onclick = e => {
    const b = e.target.closest("button");
    if (!b) return;
    if (b.dataset.g !== undefined) gGo(+b.dataset.g); else select(+b.dataset.i);
  };
  $("#openLesson").onclick = () => sel.i < 0 ? toast("先に Copilot を選択してください（ドックかオブジェクトをクリック）") : openLesson(nodes[sel.i].cp.id);

  /* ---------------- Galaxy logic: 全体 → カテゴリ → 個別Prompt のズーム ---------------- */
  let world = "copilot";
  const gSel = { c: -1, f: -1 };
  const openUrl = u => window.open(u, "_blank", "noopener");
  const curFile = () => (gSel.c >= 0 && gSel.f >= 0 ? cats[gSel.c].meta.files[gSel.f] : null);

  function galPreset() {
    let size = "EWS", angle = "high";
    if (gSel.f >= 0) { size = "MCU"; angle = "eye"; }
    else if (gSel.c >= 0) { const n = cats[gSel.c].meta.count; size = n >= 15 ? "WS" : n >= 3 ? "FS" : "MS"; angle = "eye"; }
    const s = shots[shotIdx];
    user.zoom = 1;
    setCustom({ size, angle, move: s.move, char: s.char });
  }
  function gGo(c, f = -1) {
    const prev = gSel.c;
    gSel.c = c; gSel.f = f;
    if (c >= 0 && !cats[c].built) buildFiles(cats[c]);
    galPreset();
    const file = curFile(), meta = c >= 0 ? cats[c].meta : null;
    $("#hudTitle").textContent = file ? `📝 ${file.title}` : meta ? `${meta.icon} ${meta.dir}` : "📚 サンプルPrompt銀河";
    document.querySelectorAll("#dock button").forEach(b => b.classList.toggle("on", b.dataset.g !== undefined && +b.dataset.g === c));
    renderCard();
    galTitle.visible = c < 0;
    cats.forEach(k => { k.label.visible = c < 0 || (k.i === c && f < 0); });
    if (c >= 0) cats[c].files.forEach((n, j) => { n.label.visible = f < 0 || j === f; });
    if (c >= 0 && c !== prev) {
      burst3(cats[c].grp.position, new THREE.Color(meta.color), 80);
      addXP(1);
      state.gcats = state.gcats || [];
      if (!state.gcats.includes(meta.dir)) { state.gcats.push(meta.dir); save(); checkBadges(); }
    }
  }
  function galUp() {
    if (gSel.f >= 0) gGo(gSel.c, -1);
    else if (gSel.c >= 0) gGo(-1);
  }
  const card = $("#galCard");
  function renderCard() {
    const f = curFile(), c = gSel.c >= 0 ? cats[gSel.c].meta : null;
    let h = `<nav class="crumbs"><button data-a="all">🌌 全体</button>`;
    if (c) h += ` › <button data-a="cat">${c.icon} ${esc(c.dir)}</button>`;
    if (f) h += ` › <span>${esc(f.title)}</span>`;
    h += "</nav>";
    if (f) {
      h += `<h4>${esc(f.title)}</h4><p class="mini">📁 ${esc(c.dir + (f.group ? " / " + f.group : ""))}</p><p class="mini">もう一度クリック（または Enter）で GitHub の全文を開きます。</p>
        <div class="row"><a class="btn small primary" target="_blank" rel="noopener" href="${f.url}">全文を読む ↗</a><button class="btn small" data-a="next">次のPrompt ›</button></div>`;
    } else if (c) {
      h += `${c.kind === "persona" ? `<span class="role">職種：${esc(c.role)}</span>` : ""}<h4>${c.icon} ${esc(c.dir)}</h4><p class="mini">${esc(c.desc)}</p>
        <p class="mini">✨ ${c.count}件のPrompt。周りの星をクリックでさらにズームイン。</p>
        <div class="row"><a class="btn small primary" target="_blank" rel="noopener" href="${c.startUrl}">まず読む ↗</a></div>`;
    } else {
      h += `<h4>📚 サンプルPrompt銀河</h4><p class="mini">内側の大きな星＝<b>職種（ペルソナ）</b>、外側の小さな星＝<b>テーマ</b>。星をクリックするとズームインして、中のPromptが現れます。</p>
        <p class="mini">ドラッグ=視点 ／ ホイール=ズーム ／ ←→=移動 ／ Esc=ズームアウト</p>`;
    }
    h += `<div class="row">${c ? '<button class="btn small" data-a="up">⤴ ズームアウト</button>' : ""}<button class="btn small" data-a="2d">🖥 2Dで見る</button></div>`;
    card.innerHTML = h;
  }
  card.onclick = e => {
    const b = e.target.closest("[data-a]");
    if (!b) return;
    const a = b.dataset.a;
    if (a === "all") gGo(-1);
    else if (a === "cat") gGo(gSel.c);
    else if (a === "up") galUp();
    else if (a === "next") gGo(gSel.c, (gSel.f + 1) % cats[gSel.c].meta.files.length);
    else if (a === "2d") api.goTo2D(gSel.c >= 0 ? cats[gSel.c].meta.dir : null);
  };

  function flyIn() {
    cur.pos.add(cur.pos.clone().sub(cur.look).multiplyScalar(1.1));
    cur.fov += 18;
  }
  function setWorld(w) {
    if (w === world) return;
    world = w;
    const g = w === "galaxy";
    nodes.forEach(n => { n.grp.visible = !g; });
    hub.visible = !g; track.visible = !g; selRing.visible = !g; gal.visible = g;
    scene.fog.density = g ? .0055 : .0105;
    $("#wCop").setAttribute("aria-selected", !g);
    $("#wGal").setAttribute("aria-selected", g);
    card.hidden = !g;
    $("#openLesson").style.display = g ? "none" : "";
    buildDock();
    sel.i = -1; selRing.material.opacity = 0;
    if (g) {
      gSel.c = -1; gSel.f = -1;
      setCustom({ size: "EWS", angle: "high", move: "orbit", char: "gentle" });
      gGo(-1);
    } else {
      setStyle("product");
      select(-1);
    }
    flyIn();
  }
  function showGalaxy(dir) {
    setWorld("galaxy");
    gGo(dir ? cats.findIndex(c => c.meta.dir === dir) : -1);
  }
  $("#wCop").onclick = () => setWorld("copilot");
  $("#wGal").onclick = () => setWorld("galaxy");
  buildDock();

  /* ---------------- Interaction ---------------- */
  const ray = new THREE.Raycaster(), ptr = new THREE.Vector2();
  let down = null, hover = null;
  const el = renderer.domElement;
  const setPtr = e => { const r = el.getBoundingClientRect(); ptr.set((e.clientX - r.left) / r.width * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1); };
  function hitTest(e) {
    setPtr(e); ray.setFromCamera(ptr, camera);
    let list;
    if (world === "galaxy") {
      list = cats.map(c => c.hit);
      if (gSel.c >= 0) cats[gSel.c].files.forEach(n => list.push(n.hit));
    } else list = nodes.map(n => n.hit);
    const hits = ray.intersectObjects([...list, ...orbs.filter(o => o.alive).map(o => o.mesh)], false);
    return hits[0] ? hits[0].object : null;
  }
  el.addEventListener("pointerdown", e => { down = { x: e.clientX, y: e.clientY, ax: user.az, ay: user.el, moved: false }; el.setPointerCapture(e.pointerId); });
  el.addEventListener("pointermove", e => {
    if (down) {
      const dx = e.clientX - down.x, dy = e.clientY - down.y;
      if (Math.abs(dx) + Math.abs(dy) > 5) down.moved = true;
      user.az = down.ax - dx * .006; user.el = clamp(down.ay + dy * .005, -1.4, 1.4);
    } else { hover = hitTest(e); el.style.cursor = hover ? "pointer" : "grab"; }
  });
  el.addEventListener("pointerup", e => {
    const d = down; down = null;
    if (!d || d.moved) return;
    const o = hitTest(e);
    if (!o) return;
    if (o.userData.orb) collect(o.userData.orb, e);
    else if (world === "galaxy") {
      const gf = o.userData.gfile;
      if (gf) {
        if (gSel.c === gf.c && gSel.f === gf.f) openUrl(cats[gf.c].meta.files[gf.f].url); else gGo(gf.c, gf.f);
      } else if (o.userData.gcat !== undefined && !(gSel.c === o.userData.gcat && gSel.f < 0)) gGo(o.userData.gcat);
    }
    else if (o.userData.node === sel.i) openLesson(nodes[sel.i].cp.id);
    else select(o.userData.node);
  });
  el.addEventListener("wheel", e => { e.preventDefault(); user.zoom = clamp(user.zoom * (1 + Math.sign(e.deltaY) * .08), .35, 2.6); }, { passive: false });
  addEventListener("keydown", e => {
    if ($("#view3d").hidden || !$("#modal").hidden || /SELECT|INPUT/.test(document.activeElement.tagName)) return;
    if (world === "galaxy") {
      const dir = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (dir) {
        if (gSel.f >= 0) { const n = cats[gSel.c].meta.files.length; gGo(gSel.c, (gSel.f + dir + n) % n); }
        else gGo((gSel.c + dir + cats.length) % cats.length);
      }
      if (e.key === "Enter") { const f = curFile(); if (f) openUrl(f.url); else if (gSel.c >= 0) openUrl(cats[gSel.c].meta.startUrl); }
      if (e.key === "Escape" || e.key === "Backspace") galUp();
      return;
    }
    if (e.key === "ArrowRight" || e.key === "ArrowLeft") select((sel.i + (e.key === "ArrowRight" ? 1 : -1) + COPILOTS.length + 1 - 0) % (COPILOTS.length) );
    if (e.key === "Enter" && sel.i >= 0) openLesson(nodes[sel.i].cp.id);
    if (e.key === "Escape") select(-1);
  });

  function collect(o, e) {
    o.alive = false; o.pop = 0; o.t = 5;
    burst3(o.mesh.position, o.mesh.material.color, 60);
    burst(e.clientX, e.clientY, 30);
    state.orbs++; $("#orbCount").textContent = state.orbs;
    const cp = COPILOTS[Math.floor(Math.random() * COPILOTS.length)];
    toast(`🔮 ${cp.emoji} ${cp.tips[Math.floor(Math.random() * cp.tips.length)]}`);
    addXP(5, e.clientX, e.clientY);
  }

  /* ---------------- Loop ---------------- */
  function resize() {
    const w = stage.clientWidth || innerWidth, h = stage.clientHeight || innerHeight;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(stage);
  addEventListener("resize", resize);

  let raf = 0, last = 0, frames = 0, fpsT = 0, running = false;
  const tmp = { pos: new THREE.Vector3(), look: new THREE.Vector3(), roll: 0, fov: 55 };
  function frame(now) {
    raf = requestAnimationFrame(frame);
    const dt = Math.min(.05, (now - last) / 1000 || .016); last = now;
    clock += dt; shotT += dt;
    frames++; fpsT += dt;
    if (fpsT > 1) { $("#fps3d").textContent = Math.round(frames / fpsT) + " fps"; frames = 0; fpsT = 0; }

    // tour & multi-shot sequencing
    if (tour) {
      tourT += dt;
      if (tourT > 7) {
        tourT = 0;
        select((sel.i + 1) % COPILOTS.length);
        setStyle(STYLES[Math.floor(Math.random() * STYLES.length)].id);
      }
    }
    if (shots.length > 1 && shotT > (style.dur || 3)) {
      shotT = 0; shotIdx = (shotIdx + 1) % shots.length; syncUI();
      if (shots[shotIdx].cut) cur.snap = true;
    }
    const shot = shots[shotIdx];
    if (world === "galaxy") {
      if (gSel.f >= 0 && cats[gSel.c].files[gSel.f]) cats[gSel.c].files[gSel.f].mesh.getWorldPosition(target);
      else if (gSel.c >= 0) cats[gSel.c].grp.getWorldPosition(target);
      else target.set(0, 0, 0);
    }
    pose(shot, custom ? clock : clock, want);
    const C = CHAR[shot.char];

    // damped following; hard cut for YouTube-style shots
    const a = cur.snap ? 1 : 1 - Math.exp(-C.d * dt);
    cur.snap = false;
    cur.pos.lerp(want.pos, a); cur.look.lerp(want.look, a);
    cur.roll = lerp(cur.roll, want.roll, a); cur.fov = lerp(cur.fov, want.fov, a);

    tmp.pos.copy(cur.pos); tmp.roll = cur.roll;
    const mvNoise = shot.move === "handheld" ? .02 : 0, nz = C.n + mvNoise;
    if (nz && shot.char !== "locked") {
      const d = SIZE[shot.size].d * nz;
      tmp.pos.x += ns(clock * 2, 4) * d; tmp.pos.y += ns(clock * 2, 5) * d; tmp.pos.z += ns(clock * 2, 6) * d;
      tmp.roll += ns(clock * 2, 7) * nz * 1.5;
    }
    camera.position.copy(tmp.pos);
    camera.up.set(0, 1, 0);
    camera.lookAt(cur.look);
    camera.rotateZ(tmp.roll);
    if (Math.abs(camera.fov - cur.fov) > .01) { camera.fov = clamp(cur.fov, 8, 120); camera.updateProjectionMatrix(); }

    // world animation
    const t = clock;
    stars.rotation.y += dt * .004;
    coreMesh.rotation.y += dt * .8; coreMesh.scale.setScalar(1 + Math.sin(t * 2) * .06);
    rings.forEach((r, i) => { r.rotation.x += dt * (.2 + i * .1); r.rotation.z += dt * (.15 - i * .05); });
    core.intensity = 80 + Math.sin(t * 3) * 15;
    nodes.forEach((n, i) => {
      const selected = i === sel.i;
      n.grp.position.y = n.base.y + Math.sin(t * .9 + n.ph) * .5;
      n.mesh.rotation.y += dt * (selected ? 1.6 : .5); n.mesh.rotation.x += dt * .25;
      const goal = selected ? 1.35 + Math.sin(t * 4) * .05 : hover && hover.userData.node === i ? 1.15 : 1;
      n.scale = lerp(n.scale, goal, 1 - Math.exp(-8 * dt)); n.mesh.scale.setScalar(n.scale);
      n.mat.emissiveIntensity = lerp(n.mat.emissiveIntensity, selected ? 1.3 : .45, .1);
      n.halo.scale.setScalar(8 + (selected ? 3 + Math.sin(t * 5) : 0));
      n.sats.forEach(s => { const u = s.userData, aa = t * u.sp + u.ph; s.position.set(Math.cos(aa) * u.r, Math.sin(aa * 1.3) * .8, Math.sin(aa) * u.r); });
    });
    if (sel.i >= 0) {
      selRing.position.copy(nodes[sel.i].grp.position); selRing.rotation.x = Math.PI / 2 + Math.sin(t) * .3; selRing.rotation.y += dt * 2;
      selRing.material.opacity = .6 + Math.sin(t * 4) * .3;
    }
    orbs.forEach(o => {
      if (!o.alive) { o.t -= dt; o.mesh.visible = false; if (o.t <= 0) spawnOrb(o); return; }
      o.pop = Math.min(1, o.pop + dt * 2);
      o.mesh.position.set(o.base.x + Math.sin(t * .7 + o.ph) * 1.2, o.base.y + Math.sin(t * 1.3 + o.ph) * .8, o.base.z + Math.cos(t * .6 + o.ph) * 1.2);
      o.mesh.scale.setScalar(o.pop * (hover === o.mesh ? 1.6 : 1) * (1 + Math.sin(t * 4 + o.ph) * .15));
    });
    if (world === "galaxy") {
      galCore.rotation.y += dt * .6;
      galHalo.scale.setScalar(14 + Math.sin(t * 2) * .8);
      cats.forEach(c => {
        const selC = c.i === gSel.c, hov = hover && hover.userData.gcat === c.i;
        c.grp.position.y = c.base.y + Math.sin(t * .8 + c.ph) * .4;
        c.mesh.rotation.y += dt * (selC ? 1.2 : .4); c.mesh.rotation.x += dt * .2;
        c.scale = lerp(c.scale, selC ? .8 : hov ? 1.25 : 1, 1 - Math.exp(-8 * dt));
        c.mesh.scale.setScalar(c.scale);
        c.mat.emissiveIntensity = lerp(c.mat.emissiveIntensity, selC ? 1.2 : hov ? .9 : .5, .1);
        c.halo.scale.setScalar((c.big ? 9 : 6) + (selC ? 2 + Math.sin(t * 4) * .5 : 0));
        if (!c.built) return;
        c.k = lerp(c.k, selC ? 1 : 0, 1 - Math.exp(-5 * dt));
        c.fileGrp.visible = c.k > .01;
        c.fileGrp.scale.setScalar(Math.max(.001, c.k));
        if (!c.fileGrp.visible) return;
        if (gSel.f < 0) c.fileGrp.rotation.y += dt * .08;
        c.files.forEach((n, j) => {
          const gf = hover && hover.userData.gfile;
          const goal = selC && gSel.f === j ? 1.9 : gf && gf.c === c.i && gf.f === j ? 1.4 : 1;
          n.sc = lerp(n.sc, goal, .15);
          n.mesh.scale.setScalar(n.sc);
          n.mesh.rotation.y += dt * 1.2;
        });
      });
    }
    bursts = bursts.filter(b => {
      b.life -= dt;
      const p = b.pts.geometry.attributes.position;
      b.v.forEach((v, i) => { v.multiplyScalar(.97); p.setXYZ(i, p.getX(i) + v.x * dt, p.getY(i) + v.y * dt, p.getZ(i) + v.z * dt); });
      p.needsUpdate = true; b.pts.material.opacity = Math.max(0, b.life / 1.4);
      if (b.life <= 0) { scene.remove(b.pts); b.pts.geometry.dispose(); b.pts.material.dispose(); return false; }
      return true;
    });
    renderer.render(scene, camera);
  }

  setStyle("product");
  select(-1);
  resize();
  cur.pos.set(0, 8, 70); cur.look.set(0, 0, 0);

  return {
    start(opts = {}) {
      if (running) { if (opts.galaxy) showGalaxy(opts.dir || null); return; }
      running = true; last = performance.now(); resize();
      if (opts.galaxy) showGalaxy(opts.dir || null);
      flyIn();
      raf = requestAnimationFrame(frame);
      setTimeout(() => toast(world === "galaxy" ? "🖱️ 星をクリックでズームイン、Esc でズームアウト" : "🖱️ ドラッグで視点、ホイールでズーム、🔮をクリックでXP"), 900);
    },
    stop() { running = false; cancelAnimationFrame(raf); },
    _debug: { select, setStyle, setCustom, camera, gGo, setWorld }
  };
}
