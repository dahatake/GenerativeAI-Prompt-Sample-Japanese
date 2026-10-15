import * as THREE from "three";

// 絵文字をドット絵にして立体化し、等角ジオラマ風の浮島に乗せる「3Dピクセルアイコン」
const px = new Map();
const box = new THREE.BoxGeometry(1, 1, 1);
const mats = new Map();

function sample(emoji, res) {
  const key = emoji + res;
  if (px.has(key)) return px.get(key);
  const K = 6, S = res * K, c = document.createElement("canvas");
  c.width = c.height = S;
  const g = c.getContext("2d", { willReadFrequently: true });
  g.textAlign = "center"; g.textBaseline = "middle";
  g.font = `${Math.floor(S * .82)}px "Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif`;
  g.fillText(emoji, S / 2, S / 2 + S * .04);
  const d = g.getImageData(0, 0, S, S).data, out = [];
  for (let y = 0; y < res; y++) for (let x = 0; x < res; x++) {
    let r = 0, gg = 0, b = 0, a = 0;
    for (let j = 0; j < K; j++) for (let i = 0; i < K; i++) {
      const o = ((y * K + j) * S + x * K + i) * 4, al = d[o + 3];
      r += d[o] * al; gg += d[o + 1] * al; b += d[o + 2] * al; a += al;
    }
    if (a / (K * K) < 110) continue;
    r /= a; gg /= a; b /= a;
    const l = .3 * r + .6 * gg + .1 * b, q = v => Math.max(0, Math.min(255, Math.round((l + (v - l) * 1.25) / 28) * 28));
    out.push({ x, y, c: new THREE.Color(q(r) / 255, q(gg) / 255, q(b) / 255) });
  }
  px.set(key, out);
  return out;
}

function material() {
  if (!mats.has("v")) mats.set("v", new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: .65, metalness: .05, emissive: 0x2a2a3a, emissiveIntensity: 1.1 }));
  return mats.get("v");
}

function inst(list, mat, k) {
  const m = new THREE.InstancedMesh(box, mat, list.length), M = new THREE.Matrix4(), q = new THREE.Quaternion();
  list.forEach((v, i) => {
    M.compose(new THREE.Vector3(...v.p), q, new THREE.Vector3(v.s[0] * k, v.s[1] * k, v.s[2] * k));
    m.setMatrixAt(i, M); m.setColorAt(i, v.c);
  });
  m.instanceMatrix.needsUpdate = true;
  if (m.instanceColor) m.instanceColor.needsUpdate = true;
  return m;
}

export function makeVoxelIcon(emoji, { unit = .16, res = 16, depth = 3, tint = "#7f85f5", base = true, seed = 1 } = {}) {
  const u = unit, list = [];
  const pts = sample(emoji, res);
  const rnd = (() => { let s = seed * 9301 + 49297; return () => ((s = (s * 9301 + 49297) % 233280) / 233280); })();
  const baseH = base ? 4 * 2 * u : 0, iconBottom = base ? baseH + u * .2 : 0;
  for (const p of pts) for (let z = 0; z < depth; z++) {
    const k = z === depth - 1 ? 1.06 : z === 0 ? .7 : .88, c = p.c.clone().multiplyScalar(k);
    list.push({ p: [(p.x - res / 2 + .5) * u, iconBottom + (res - p.y - .5) * u, (z - (depth - 1) / 2) * u], s: [u, u, u], c });
  }
  if (base) {
    const grass = new THREE.Color(tint).lerp(new THREE.Color("#5fd36b"), .55), dirt = new THREE.Color("#8a5a35"), stone = new THREE.Color("#6e7388");
    const N = 9, cell = 2 * u, layers = [{ r: 4.6, c: grass }, { r: 4.2, c: dirt }, { r: 3.2, c: dirt.clone().multiplyScalar(.8) }, { r: 1.9, c: stone }];
    layers.forEach((L, li) => {
      for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
        const dx = i - (N - 1) / 2, dz = j - (N - 1) / 2;
        if (Math.hypot(dx, dz) > L.r) continue;
        const shade = li === 0 && (i + j) % 2 ? .93 : 1;
        list.push({ p: [dx * cell, baseH - (li + .5) * cell, dz * cell], s: [cell, cell, cell], c: L.c.clone().multiplyScalar(shade) });
      }
    });
    const acc = new THREE.Color(tint);
    for (let n = 0; n < 4; n++) {
      const a = rnd() * 6.28, r = 3.2 + rnd() * 1.1, x = Math.cos(a) * r * cell, z = Math.sin(a) * r * cell;
      if (Math.abs(z) < depth * u) continue;
      list.push({ p: [x, baseH + u * .5, z], s: [u, u, u], c: n % 2 ? acc.clone().offsetHSL(0, 0, .15) : new THREE.Color("#3da35a") });
      if (n % 2 === 0) list.push({ p: [x, baseH + u * 1.5, z], s: [u * .8, u, u * .8], c: new THREE.Color("#4fc96d") });
    }
  }
  if (!list.length) list.push({ p: [0, u, 0], s: [u * 4, u * 4, u * 4], c: new THREE.Color(tint) });
  const mat = material();
  const mesh = inst(list, mat, .985);
  const top = iconBottom + res * u, bottom = base ? baseH - 4 * 2 * u : 0;
  mesh.position.y = -(top + bottom) / 2;
  const group = new THREE.Group();
  group.add(mesh);
  return { group, mat, height: top - bottom };
}
