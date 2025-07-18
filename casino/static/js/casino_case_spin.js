import { apiMe, apiSpin, clearSessionToken } from './casino_api.js';

const cfg = {
  fillerBefore: 30,
  fillerAfter: 15,
  fastExtraPx: 1600,
  durationMs: 9000,
  easing: 'cubic-bezier(.06,.95,.17,1)',
  idleBeforeFactor: 0.4,
  idleAfterFactor: 0.25
};

function loadItemsFromScript() {
  const el = document.getElementById('casinoItems');
  if (!el) return [];
  try { return JSON.parse(el.textContent.trim()); }
  catch { return []; }
}
const ITEM_META = loadItemsFromScript();

const nickEl  = document.getElementById('playerNickname');
const balEl   = document.getElementById('playerBalance');
const spinBtn = document.getElementById('spinBtn');
const msgEl   = document.getElementById('spinMessage');
const logout  = document.getElementById('logoutBtn');
const stripEl = document.getElementById('caseStrip');

let lastIdleKey = null;
let lastWinKey = null;

document.addEventListener('DOMContentLoaded', () => {
  logout.addEventListener('click', () => {
    clearSessionToken();
    window.location.href = '/casino/login';
  });
  window.addEventListener('resize', () => {
    if (lastWinKey) buildIdleStrip(lastWinKey);
    else buildIdleStrip();
  });
  warmup();
  loadMe();
});

async function loadMe() {
  try {
    const me = await apiMe();
    nickEl.textContent = me.mc_nickname || '';
    balEl.textContent  = me.coin_balance ?? 0;
    buildIdleStrip();
  } catch {
    window.location.href = '/casino/login';
  }
}

spinBtn.addEventListener('click', async () => {
  const original = spinBtn.textContent;
  spinBtn.disabled = true;
  spinBtn.textContent = 'Opening...';
  msgEl.textContent = '';
  try {
    const data = await apiSpin();
    balEl.textContent = data.coin_balance;
    runCaseAnimation(data.result, () => {
      msgEl.textContent = `You got: ${labelFor(data.result)}!`;
      spinBtn.disabled = false;
      spinBtn.textContent = original;
      lastWinKey = data.result;
      buildIdleStrip(lastWinKey);
    });
  } catch (err) {
    msgEl.textContent = err.message || 'Spin error';
    spinBtn.disabled = false;
    spinBtn.textContent = original;
  }
});

function buildIdleStrip(centerKey) {
  stripEl.innerHTML = '';
  const beforeCount = Math.max(1, Math.round(cfg.fillerBefore * cfg.idleBeforeFactor));
  const afterCount  = Math.max(1, Math.round(cfg.fillerAfter  * cfg.idleAfterFactor));
  const before = randomItems(beforeCount);
  const after  = randomItems(afterCount);
  const key = centerKey || randomItems(1)[0];
  lastIdleKey = key;
  const all = [...before, key, ...after];
  all.forEach(k => {
    const meta = ITEM_META.find(i => i.key === k) || {label:k,color:'#666'};
    const el = document.createElement('div');
    el.className = 'case-item-lg';
    el.style.background = meta.color;
    el.textContent = meta.label;
    stripEl.appendChild(el);
  });
  forceSync();
  centerStripOnIndex(before.length);
}

function runCaseAnimation(winningKey, onDone) {
  stripEl.innerHTML = '';
  const before = randomItems(cfg.fillerBefore);
  const after  = randomItems(cfg.fillerAfter);
  const all = [...before, winningKey, ...after];
  all.forEach(k => {
    const meta = ITEM_META.find(i => i.key === k) || {label:k,color:'#666'};
    const el = document.createElement('div');
    el.className = 'case-item-lg';
    el.style.background = meta.color;
    el.textContent = meta.label;
    stripEl.appendChild(el);
  });
  forceSync();
  const g = measureGeom();
  const winIndex = before.length;
  const winOffsetCenter = g.stripPadLeft + winIndex * g.cellW + g.tileWHalf;
  const translateXFinal = g.viewportCenter - winOffsetCenter;
  const startX = translateXFinal + cfg.fastExtraPx + g.viewportWidth;
  stripEl.style.transition = 'none';
  stripEl.style.transform  = `translateX(${startX}px)`;
  forceSync();
  requestAnimationFrame(() => {
    stripEl.style.transition = `transform ${cfg.durationMs}ms ${cfg.easing}`;
    stripEl.style.transform  = `translateX(${translateXFinal}px)`;
    if (onDone) setTimeout(onDone, cfg.durationMs + 100);
  });
}

function centerStripOnIndex(idx) {
  const g = measureGeom();
  const offsetCenter = g.stripPadLeft + idx * g.cellW + g.tileWHalf;
  const tx = g.viewportCenter - offsetCenter;
  stripEl.style.transition = 'none';
  stripEl.style.transform  = `translateX(${tx}px)`;
}

function measureGeom() {
  const viewportRect = stripEl.parentElement.getBoundingClientRect();
  const viewportWidth = viewportRect.width;
  const viewportCenter = viewportWidth / 2;
  const children = stripEl.children;
  let tileW = 0;
  let gap = 0;
  if (children.length > 0) {
    tileW = children[0].getBoundingClientRect().width;
    if (children.length > 1) {
      const r0 = children[0].getBoundingClientRect();
      const r1 = children[1].getBoundingClientRect();
      gap = Math.max(0, r1.left - r0.right);
    }
  }
  const style = getComputedStyle(stripEl);
  const padLeft = parseFloat(style.paddingLeft) || 0;
  return {
    viewportWidth,
    viewportCenter,
    tileW,
    tileWHalf: tileW / 2,
    gap,
    cellW: tileW + gap,
    stripPadLeft: padLeft
  };
}

function forceSync() {
  stripEl.getBoundingClientRect();
}

function warmup() {
  stripEl.style.transform = 'translateZ(0)';
  forceSync();
}

function randomItems(n) {
  const arr = [];
  for (let i=0; i<n; i++) {
    const r = Math.floor(Math.random() * ITEM_META.length);
    arr.push(ITEM_META[r].key);
  }
  return arr;
}

function labelFor(key) {
  const meta = ITEM_META.find(i => i.key === key);
  return meta ? meta.label : key;
}