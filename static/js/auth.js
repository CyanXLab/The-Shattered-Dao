// 逆仙录·天道残卷 - 用户认证
const Auth = {
  selectedRoot: 'pseudo',
  selectedTechnique: 'wood_basic',

  async init() {
    const me = await API.me();
    if (me.ok) {
      if (me.is_admin) {
        // 管理员进入管理后台
        this.startAdmin();
      } else {
        // 普通玩家检查是否已创建角色
        const cs = await API.get('/character_status');
        if (cs.ok && cs.created) {
          this.startGame();
        } else {
          this.showCharCreate();
        }
      }
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
      location.reload();
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
      // 注册成功后跳转角色创建
      document.getElementById('login-screen').style.display = 'none';
      this.showCharCreate();
    } else {
      document.getElementById('auth-msg').textContent = r.msg;
    }
  },

  showCharCreate() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('char-create-screen').style.display = 'flex';
    this.renderRootOptions();
    this.renderTechniqueOptions();
  },

  renderRootOptions() {
    const roots = [
      {id: 'pseudo', name: '伪灵根', desc: '资质平庸，修炼效率60%，但故事感最强', hp: 80, qi: 200},
      {id: 'false', name: '假灵根', desc: '资质一般，修炼效率80%', hp: 90, qi: 250},
      {id: 'true', name: '真灵根', desc: '资质优秀，修炼效率100%', hp: 100, qi: 300},
      {id: 'heavenly', name: '天灵根', desc: '资质绝顶，修炼效率120%（难度低）', hp: 120, qi: 400}
    ];
    const html = roots.map(r => `
      <div class="detail-box" style="cursor:pointer;margin:6px 0;border-color:${this.selectedRoot===r.id?'#d4af37':'#2a2438'}" onclick="Auth.selectRoot('${r.id}')">
        <div style="color:${this.selectedRoot===r.id?'#d4af37':'#e8e0c8'};font-weight:bold">${this.selectedRoot===r.id?'●':'○'} ${r.name}</div>
        <div style="color:#8a7a9a;font-size:11px;margin-top:2px">${r.desc}</div>
        <div style="color:#8a7a9a;font-size:11px">初始 HP:${r.hp} 灵气:${r.qi}</div>
      </div>
    `).join('');
    document.getElementById('root-options').innerHTML = html;
  },

  selectRoot(id) {
    this.selectedRoot = id;
    this.renderRootOptions();
  },

  renderTechniqueOptions() {
    const techs = [
      {id: 'wood_basic', name: '青木诀', element: '木', desc: '温和平稳，生生不息'},
      {id: 'fire_basic', name: '焚天诀', element: '火', desc: '霸道凌厉，攻伐无双'},
      {id: 'ice_basic', name: '冰魄诀', element: '冰', desc: '阴寒凝练，攻守兼备'},
      {id: 'metal_basic', name: '庚金诀', element: '金', desc: '锋锐凌厉，攻伐刚猛'},
      {id: 'earth_basic', name: '厚土诀', element: '土', desc: '厚重绵长，防御无双'}
    ];
    const html = techs.map(t => `
      <div class="detail-box" style="cursor:pointer;margin:6px 0;border-color:${this.selectedTechnique===t.id?'#d4af37':'#2a2438'}" onclick="Auth.selectTechnique('${t.id}')">
        <div style="color:${this.selectedTechnique===t.id?'#d4af37':'#e8e0c8'};font-weight:bold">${this.selectedTechnique===t.id?'●':'○'} ${t.name} <span style="color:#8a7a9a;font-weight:normal;font-size:11px">${t.element}属性</span></div>
        <div style="color:#8a7a9a;font-size:11px;margin-top:2px">${t.desc}</div>
      </div>
    `).join('');
    document.getElementById('technique-options').innerHTML = html;
  },

  selectTechnique(id) {
    this.selectedTechnique = id;
    this.renderTechniqueOptions();
  },

  async doCreateCharacter() {
    const name = document.getElementById('char-name').value.trim();
    if (!name) {
      document.getElementById('char-msg').textContent = '请输入道号';
      return;
    }
    const r = await API.post('/create_character', {
      name: name,
      spiritual_root: this.selectedRoot,
      start_technique: this.selectedTechnique
    });
    if (r.ok) {
      document.getElementById('char-create-screen').style.display = 'none';
      this.startGame();
    } else {
      document.getElementById('char-msg').textContent = r.msg;
    }
  },

  async startGame() {
    document.getElementById('char-create-screen').style.display = 'none';
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('loading').textContent = '正在踏入修仙之路...';
    await UI.init();
    document.getElementById('loading').style.display = 'none';
    document.getElementById('game-container').style.display = 'flex';
    document.getElementById('game-container').style.flexDirection = 'column';
    document.getElementById('game-container').style.height = '100vh';
  },

  startAdmin() {
    // 管理员进入管理后台
    document.getElementById('loading').style.display = 'none';
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('char-create-screen').style.display = 'none';
    document.getElementById('game-container').style.display = 'none';
    AdminPanel.show();
  },

  async logout() {
    await API.logout();
    location.reload();
  }
};
