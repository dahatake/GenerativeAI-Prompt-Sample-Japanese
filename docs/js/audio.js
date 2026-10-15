// BGM / SE はすべて Web Audio API でその場で合成する「オリジナル」です。
// 音声ファイル・サンプル・外部素材は一切使用していないため、第三者の著作権・ライセンスの問題はありません。
const KEY = "copilot-playground-audio";
const pref = (() => { try { return { bgm: true, se: true, vol: .6, ...JSON.parse(localStorage.getItem(KEY) || "{}") }; } catch { return { bgm: true, se: true, vol: .6 }; } })();
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(pref)); } catch { /* ignore */ } };

let ctx = null, master, bgmBus, seBus, reverb, noiseBuf;
let started = false, mood = "calm", timer = null, nextT = 0, step = 0;

const N = m => 440 * Math.pow(2, (m - 69) / 12);
// C メジャーのやさしい進行（Cmaj7 - Am7 - Fmaj7 - G6）
const CHORDS = [[48, 55, 59, 64], [45, 52, 57, 60], [41, 48, 57, 64], [43, 50, 55, 59]];
const PENTA = [0, 2, 4, 7, 9];
const MOODS = {
  calm: { bpm: 76, arp: .55, pad: 1400, shimmer: 0, bass: 0, root: 72 },
  space: { bpm: 64, arp: .4, pad: 900, shimmer: .5, bass: 1, root: 76 },
  galaxy: { bpm: 70, arp: .65, pad: 1200, shimmer: .8, bass: 1, root: 79 }
};

function build() {
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return false;
  ctx = new AC();
  master = ctx.createGain(); master.gain.value = pref.vol;
  const comp = ctx.createDynamicsCompressor();
  master.connect(comp); comp.connect(ctx.destination);
  bgmBus = ctx.createGain(); bgmBus.gain.value = pref.bgm ? .5 : 0;
  seBus = ctx.createGain(); seBus.gain.value = pref.se ? 1 : 0;
  bgmBus.connect(master); seBus.connect(master);
  const len = ctx.sampleRate * 2.2, ir = ctx.createBuffer(2, len, ctx.sampleRate);
  for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.6); }
  reverb = ctx.createConvolver(); reverb.buffer = ir;
  const rg = ctx.createGain(); rg.gain.value = .35;
  reverb.connect(rg); rg.connect(master);
  noiseBuf = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
  const nd = noiseBuf.getChannelData(0); for (let i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1;
  return true;
}

function tone(t, f, dur, { type = "sine", vol = .2, a = .01, bus = bgmBus, wet = .4, cutoff = 0, glide = 0, det = 0 } = {}) {
  const o = ctx.createOscillator(), g = ctx.createGain();
  o.type = type; o.frequency.setValueAtTime(f, t);
  if (glide) o.frequency.exponentialRampToValueAtTime(Math.max(20, f * glide), t + dur);
  if (det) o.detune.value = det;
  g.gain.setValueAtTime(0, t);
  g.gain.linearRampToValueAtTime(vol, t + a);
  g.gain.exponentialRampToValueAtTime(.0001, t + dur);
  let out = g;
  o.connect(g);
  if (cutoff) { const lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = cutoff; g.connect(lp); out = lp; }
  out.connect(bus);
  if (wet) { const w = ctx.createGain(); w.gain.value = wet; out.connect(w); w.connect(reverb); }
  o.start(t); o.stop(t + dur + .05);
}
function noise(t, dur, { vol = .15, f0 = 800, f1 = 800, q = 1, type = "bandpass", bus = seBus } = {}) {
  const s = ctx.createBufferSource(); s.buffer = noiseBuf; s.loop = true;
  const fl = ctx.createBiquadFilter(); fl.type = type; fl.Q.value = q;
  fl.frequency.setValueAtTime(f0, t); fl.frequency.exponentialRampToValueAtTime(f1, t + dur);
  const g = ctx.createGain();
  g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(vol, t + Math.min(.05, dur / 3)); g.gain.exponentialRampToValueAtTime(.0001, t + dur);
  s.connect(fl); fl.connect(g); g.connect(bus); g.connect(reverb);
  s.start(t); s.stop(t + dur + .05);
}

/* ---------- BGM（ジェネレーティブ・アンビエント） ---------- */
function schedule() {
  if (!ctx || ctx.state !== "running") return;
  const M = MOODS[mood], beat = 60 / M.bpm, sub = beat / 2;
  if (nextT < ctx.currentTime) nextT = ctx.currentTime + .05;
  while (nextT < ctx.currentTime + .6) {
    const bar = Math.floor(step / 8) % CHORDS.length, pos = step % 8, ch = CHORDS[bar];
    if (pos === 0) {
      ch.forEach((m, i) => {
        tone(nextT, N(m), beat * 8.2, { type: "triangle", vol: .05, a: 1.2, cutoff: M.pad, wet: .5, det: i * 3 - 4 });
        tone(nextT, N(m + 12), beat * 8.2, { type: "sine", vol: .028, a: 1.8, wet: .6, det: 5 - i * 2 });
      });
      if (M.bass) tone(nextT, N(ch[0] - 12), beat * 4, { type: "sine", vol: .09, a: .08, wet: .1 });
    }
    if (M.bass && pos === 4) tone(nextT, N(ch[0] - 12), beat * 2.5, { type: "sine", vol: .06, a: .06, wet: .1 });
    if (Math.random() < M.arp * (pos % 2 === 0 ? 1 : .6)) {
      const base = M.root + [0, 0, 5, 7][bar] - (bar === 1 ? 3 : 0);
      const note = base + PENTA[Math.floor(Math.random() * 5)] + (Math.random() < .25 ? 12 : 0);
      tone(nextT + Math.random() * .02, N(note), 1.4, { type: "sine", vol: .07, a: .005, wet: .6 });
    }
    if (M.shimmer && pos === 0 && Math.random() < M.shimmer) tone(nextT, N(ch[3] + 24), 3.2, { type: "sine", vol: .018, a: 1, wet: .9, det: 8 });
    nextT += sub; step++;
  }
}
function startBgm() {
  if (timer) return;
  nextT = ctx.currentTime + .1;
  timer = setInterval(schedule, 150);
  schedule();
}
function stopBgm() { clearInterval(timer); timer = null; }

/* ---------- SE ---------- */
const T = (t, f, d, o = {}) => tone(t, f, d, { bus: seBus, ...o });
const SE = {
  click: t => T(t, 880, .09, { type: "triangle", vol: .12, wet: .15, glide: 1.4 }),
  tab: t => { T(t, 660, .08, { type: "triangle", vol: .1 }); T(t + .05, 990, .1, { type: "triangle", vol: .1 }); },
  next: t => { T(t, 523, .12, { type: "triangle", vol: .12 }); T(t + .07, 784, .18, { type: "triangle", vol: .12 }); },
  back: t => { T(t, 784, .12, { type: "triangle", vol: .1 }); T(t + .07, 523, .18, { type: "triangle", vol: .1 }); },
  pop: t => T(t, 400, .12, { vol: .2, glide: 2.2, wet: .2 }),
  copy: t => [784, 988, 1175, 1568].forEach((f, i) => T(t + i * .06, f, .35, { vol: .14, wet: .5 })),
  stamp: t => { T(t, 140, .25, { vol: .4, glide: .4, wet: .1 }); noise(t, .12, { vol: .2, f0: 2000, f1: 300 }); },
  open: t => noise(t, .22, { vol: .12, f0: 600, f1: 3000, q: .8 }),
  close: t => noise(t, .2, { vol: .1, f0: 3000, f1: 500, q: .8 }),
  ok: t => [523, 659, 784, 1047].forEach((f, i) => T(t + i * .07, f, .3, { type: "triangle", vol: .13 })),
  ng: t => { T(t, 220, .28, { type: "sawtooth", vol: .08, cutoff: 700, glide: .7, wet: .1 }); T(t + .1, 165, .35, { type: "sawtooth", vol: .08, cutoff: 600, glide: .7, wet: .1 }); },
  combo: t => [659, 880, 1109, 1319, 1760].forEach((f, i) => T(t + i * .05, f, .3, { vol: .1, wet: .5 })),
  level: t => { [523, 659, 784, 1047, 784, 1047, 1319].forEach((f, i) => T(t + i * .09, f, .45, { type: "triangle", vol: .13, wet: .5 })); T(t + .6, 262, 1, { vol: .15, wet: .3 }); },
  badge: t => { [880, 1175, 1568].forEach((f, i) => T(t + i * .1, f, .6, { vol: .14, wet: .7 })); noise(t, .6, { vol: .05, f0: 4000, f1: 9000, type: "highpass" }); },
  whoosh: t => noise(t, .8, { vol: .22, f0: 300, f1: 4500, q: 1.2 }),
  whooshBack: t => noise(t, .8, { vol: .2, f0: 4500, f1: 250, q: 1.2 }),
  zoom: t => { noise(t, .55, { vol: .12, f0: 400, f1: 2400, q: 2 }); T(t, 330, .5, { vol: .08, glide: 2, wet: .5 }); },
  orb: t => [1047, 1319, 1568, 2093].forEach((f, i) => T(t + i * .045, f, .3, { vol: .1, wet: .7 })),
  star: t => { T(t, 587, .6, { vol: .14, wet: .7 }); T(t + .08, 880, .7, { vol: .1, wet: .7 }); },
  fanfare: t => { [392, 523, 659, 784].forEach((f, i) => T(t + i * .1, f, .5, { type: "triangle", vol: .12, wet: .5 })); [523, 659, 784, 1047].forEach(f => T(t + .45, f, 1, { type: "triangle", vol: .08, a: .03, wet: .6 })); },
  toggle: t => T(t, 740, .1, { type: "square", vol: .05, cutoff: 2000 })
};
export function sfx(name) {
  if (!ctx || !pref.se || ctx.state !== "running" || !SE[name]) return;
  SE[name](ctx.currentTime + .005);
}

/* ---------- 公開 API ---------- */
export function setMood(m) {
  if (!MOODS[m] || m === mood) return;
  mood = m;
  if (ctx && pref.bgm) { bgmBus.gain.cancelScheduledValues(ctx.currentTime); bgmBus.gain.setTargetAtTime(.2, ctx.currentTime, .15); bgmBus.gain.setTargetAtTime(.5, ctx.currentTime + .6, .6); }
}
async function ensure() {
  if (!ctx && !build()) return false;
  if (ctx.state === "suspended") { try { await ctx.resume(); } catch { return false; } }
  started = true;
  if (pref.bgm) startBgm();
  return true;
}
function apply() {
  if (!ctx) return;
  master.gain.setTargetAtTime(pref.vol, ctx.currentTime, .05);
  bgmBus.gain.setTargetAtTime(pref.bgm ? .5 : 0, ctx.currentTime, .3);
  seBus.gain.value = pref.se ? 1 : 0;
  if (pref.bgm) startBgm(); else setTimeout(() => { if (!pref.bgm) stopBgm(); }, 1200);
}

export function initAudio() {
  const btn = document.getElementById("soundBtn"), pop = document.getElementById("soundPop");
  const sync = () => {
    btn.textContent = pref.bgm || pref.se ? "🔊" : "🔇";
    pop.querySelector("#sBgm").checked = pref.bgm;
    pop.querySelector("#sSe").checked = pref.se;
    pop.querySelector("#sVol").value = Math.round(pref.vol * 100);
  };
  sync();
  const first = async () => { if (await ensure()) { removeEventListener("pointerdown", first, true); removeEventListener("keydown", first, true); } };
  addEventListener("pointerdown", first, true);
  addEventListener("keydown", first, true);

  btn.onclick = async e => {
    e.stopPropagation();
    await ensure();
    pop.hidden = !pop.hidden;
    btn.setAttribute("aria-expanded", String(!pop.hidden));
  };
  document.addEventListener("pointerdown", e => { if (!e.target.closest(".soundwrap")) pop.hidden = true; });
  pop.addEventListener("input", async e => {
    await ensure();
    if (e.target.id === "sBgm") pref.bgm = e.target.checked;
    if (e.target.id === "sSe") pref.se = e.target.checked;
    if (e.target.id === "sVol") pref.vol = e.target.value / 100;
    save(); apply(); sync();
    if (e.target.id !== "sVol") sfx("toggle");
  });
  pop.addEventListener("change", e => { if (e.target.id === "sVol") sfx("pop"); });
  document.addEventListener("visibilitychange", () => {
    if (!ctx) return;
    if (document.hidden) ctx.suspend(); else if (started) ctx.resume();
  });

  const SPECIAL = ".copy,[data-copy],#wCopy,.opt,#wNext,#wBack,.w-dot,[role=tab],.d-tabs button,.tabs button,.note-x,#mClose,#wX,.dock button,.seg button";
  document.addEventListener("pointerdown", e => {
    if (e.target.closest(".soundwrap")) return;
    if (e.target.closest("#wNext,.w-dot")) return sfx("next");
    if (e.target.closest("#wBack")) return sfx("back");
    if (e.target.closest("[role=tab],.d-tabs button,.tabs button,.dock button,.seg button")) return sfx("tab");
    if (e.target.closest(".note-x,#mClose,#wX")) return sfx("close");
    const t = e.target.closest("button,a,.card,.cat,.w-card,.style-card,.opt-card,.qi,.part");
    if (t && !t.matches(SPECIAL)) sfx("click");
  }, true);
  window.addEventListener("note-copied", () => sfx("copy"));
  window.addEventListener("guide-copied", () => sfx("copy"));
}
