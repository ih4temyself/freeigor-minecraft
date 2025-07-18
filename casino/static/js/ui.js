import { SPIN_COST } from './config.js';
import { apiLogin, apiSpin, apiMe, setSessionToken, clearSessionToken } from './api.js';
import { buildWheel, animateWheelTo, labelFor } from './wheel.js';

const loginView      = document.getElementById('loginView');
const loginCodeInput = document.getElementById('loginCodeInput');
const loginBtn       = document.getElementById('loginBtn');
const loginError     = document.getElementById('loginError');

const spinView       = document.getElementById('spinView');
const playerNickname = document.getElementById('playerNickname');
const playerBalance  = document.getElementById('playerBalance');
const spinBtn        = document.getElementById('spinBtn');
const spinMessage    = document.getElementById('spinMessage');
const logoutBtn      = document.getElementById('logoutBtn');
const wheelEl        = document.getElementById('wheel');

/* Expose a small init() that main.js can call */
export function initUI() {
  buildWheel(wheelEl);

  const ip = document.getElementById('ip');
  const copyBtn = document.getElementById('copyBtn');
  const copyText = document.getElementById('copyText');
  copyBtn.addEventListener('click', () =>
    navigator.clipboard.writeText(ip.textContent.trim())
      .then(() => {
        copyText.textContent = 'Copied!';
        setTimeout(() => copyText.textContent = 'Copy', 2000);
      })
      .catch(() => alert('Clipboard error 😢'))
  );

  loginBtn.addEventListener('click', doLogin);
  loginCodeInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') doLogin();
  });

  spinBtn.addEventListener('click', doSpin);

  logoutBtn.addEventListener('click', () => {
    clearSessionToken();
    showLogin();
  });

  tryResumeSession();
}

function showLogin() {
  loginView.classList.remove('hidden');
  spinView.classList.add('hidden');
  spinMessage.textContent = '';
  loginError.classList.add('hidden');
}

function showSpin(info) {
  loginView.classList.add('hidden');
  spinView.classList.remove('hidden');
  playerNickname.textContent = info?.mc_nickname || '';
  playerBalance.textContent  = info?.coin_balance ?? 0;
  spinBtn.textContent = `SPIN (-${SPIN_COST} coins)`;
  spinMessage.textContent = '';
}

async function doLogin() {
  loginError.classList.add('hidden');
  const code = loginCodeInput.value.trim();
  if (!code) {
    loginError.textContent = 'Введите код.';
    loginError.classList.remove('hidden');
    return;
  }
  loginBtn.disabled = true;
  loginBtn.textContent = 'Logging in...';
  try {
    const data = await apiLogin(code);
    setSessionToken(data.session_token);
    showSpin(data);
  } catch (err) {
    loginError.textContent = err.message || 'Login error';
    loginError.classList.remove('hidden');
  } finally {
    loginBtn.disabled = false;
    loginBtn.textContent = 'Login';
  }
}

async function doSpin() {
  spinBtn.disabled = true;
  spinBtn.textContent = 'Spinning...';
  spinMessage.textContent = '';
  try {
    const data = await apiSpin();
    animateWheelTo(wheelEl, data.result, () => {
      playerBalance.textContent = data.coin_balance;
      spinMessage.textContent = `You won: ${labelFor(data.result)}!`;
      spinBtn.disabled = false;
      spinBtn.textContent = `SPIN (-${SPIN_COST} coins)`;
    });
  } catch (err) {
    spinMessage.textContent = err.message || 'Spin error';
    spinBtn.disabled = false;
    spinBtn.textContent = `SPIN (-${SPIN_COST} coins)`;
  }
}

async function tryResumeSession() {
  try {
    const me = await apiMe();
    showSpin(me);
  } catch {
    showLogin();
  }
}