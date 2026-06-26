// 逆仙录·天道残卷 - 用户认证
const Auth = {
  async init() {
    const me = await API.me();
    if (me.ok) {
      this.startGame();
    } else {
      document.getElementById('loading').style.display = 'none';
      document.getElementById('login-screen').style.display = 'flex';
    }
  },

  switchTab(tab) {
    document.querySelectorAll('.tabs .tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('login-form').style.display = tab === 'login' ? 'block' : 'none';
    document.getElementById('register-form').style.display = tab === 'register' ? 'block' : 'none';
    document.getElementById('auth-msg').textContent = '';
  },

  async doLogin() {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    if (!username || !password) {
      document.getElementById('auth-msg').textContent = '请输入用户名和密码';
      return;
    }
    const r = await API.login(username, password);
    if (r.ok) {
      this.startGame();
    } else {
      document.getElementById('auth-msg').textContent = r.msg;
    }
  },

  async doRegister() {
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value;
    if (!username || !password) {
      document.getElementById('auth-msg').textContent = '请输入用户名和密码';
      return;
    }
    if (username.length < 3) {
      document.getElementById('auth-msg').textContent = '用户名至少3个字符';
      return;
    }
    if (password.length < 4) {
      document.getElementById('auth-msg').textContent = '密码至少4个字符';
      return;
    }
    const r = await API.register(username, password);
    if (r.ok) {
      this.startGame();
    } else {
      document.getElementById('auth-msg').textContent = r.msg;
    }
  },

  async startGame() {
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('loading').textContent = '正在踏入修仙之路...';
    await UI.init();
    document.getElementById('loading').style.display = 'none';
    document.getElementById('game-container').style.display = 'flex';
    document.getElementById('game-container').style.flexDirection = 'column';
    document.getElementById('game-container').style.height = '100vh';
  },

  async logout() {
    await API.logout();
    location.reload();
  }
};
