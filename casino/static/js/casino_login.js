import { apiLogin, setSessionToken } from './casino_api.js';

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('loginCodeInput');
  const btn   = document.getElementById('loginBtn');
  const errEl = document.getElementById('loginError');

  function showError(msg) {
    errEl.textContent = msg;
    errEl.classList.remove('hidden');
  }
  function clearError() {
    errEl.classList.add('hidden');
  }

  async function doLogin() {
    clearError();
    const code = input.value.trim();
    if (!code) {
      showError('Введите код.');
      return;
    }
    btn.disabled = true;
    btn.textContent = 'Logging in...';
    try {
      const data = await apiLogin(code);
      setSessionToken(data.session_token);
      // go to spin page
      window.location.href = '/casino/spin';
    } catch (err) {
      showError(err.message || 'Login error');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Login';
    }
  }

  btn.addEventListener('click', doLogin);
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') doLogin();
  });
});