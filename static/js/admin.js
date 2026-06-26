// 逆仙录·天道残卷 - 管理员后台
const AdminPanel = {
  show() {
    // 创建管理后台UI
    document.body.innerHTML = `
      <div style="background:#0a0a14;color:#e8e0c8;font-family:'Noto Sans SC',sans-serif;min-height:100vh;padding:20px">
        <div style="max-width:1200px;margin:0 auto">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;border-bottom:2px solid #d4af37;padding-bottom:10px">
            <h1 style="color:#d4af37;letter-spacing:4px">逆仙录·管理后台</h1>
            <button onclick="Auth.logout()" style="background:#2a2438;border:1px solid #3a3450;color:#e8e0c8;padding:6px 12px;border-radius:3px;cursor:pointer">登出</button>
          </div>
          <div id="admin-content"></div>
        </div>
      </div>
    `;
    this.loadDashboard();
  },

  async loadDashboard() {
    const r = await API.get('/admin/stats');
    if (!r.ok) return;
    const s = r.stats;
    document.getElementById('admin-content').innerHTML = `
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px">
        ${this.statCard('用户数', s.users, '#6bc8ff')}
        ${this.statCard('材料', s.materials, '#9ad96b')}
        ${this.statCard('功法', s.techniques, '#c896ff')}
        ${this.statCard('丹方', s.pill_recipes, '#ffaa6b')}
        ${this.statCard('妖兽', s.beasts, '#ff6b6b')}
        ${this.statCard('区域', s.regions, '#6bc832')}
        ${this.statCard('NPC', s.npcs, '#d4af37')}
        ${this.statCard('宗门', s.sects, '#3296c8')}
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <div style="background:#1a1428;border:1px solid #2a2438;border-radius:6px;padding:12px">
          <h3 style="color:#d4af37;margin-bottom:10px">玩家管理</h3>
          <button onclick="AdminPanel.loadUsers()" style="background:#2a2438;border:1px solid #3a3450;color:#e8e0c8;padding:8px;border-radius:3px;cursor:pointer;width:100%;margin-bottom:6px">查看所有玩家</button>
          <button onclick="AdminPanel.showGiveItem()" style="background:#2a2438;border:1px solid #3a3450;color:#e8e0c8;padding:8px;border-radius:3px;cursor:pointer;width:100%;margin-bottom:6px">发放物品</button>
          <button onclick="AdminPanel.showSetRealm()" style="background:#2a2438;border:1px solid #3a3450;color:#e8e0c8;padding:8px;border-radius:3px;cursor:pointer;width:100%;margin-bottom:6px">设置境界</button>
          <button onclick="AdminPanel.showAddStones()" style="background:#2a2438;border:1px solid #3a3450;color:#e8e0c8;padding:8px;border-radius:3px;cursor:pointer;width:100%">发放灵石</button>
        </div>
        <div style="background:#1a1428;border:1px solid #2a2438;border-radius:6px;padding:12px">
          <h3 style="color:#d4af37;margin-bottom:10px">世界管理</h3>
          <button onclick="AdminPanel.showBroadcast()" style="background:#2a2438;border:1px solid #3a3450;color:#e8e0c8;padding:8px;border-radius:3px;cursor:pointer;width:100%;margin-bottom:6px">全服公告</button>
          <button onclick="AdminPanel.viewData('materials')" style="background:#2a2438;border:1px solid #3a3450;color:#e8e0c8;padding:8px;border-radius:3px;cursor:pointer;width:100%;margin-bottom:6px">查看数据</button>
          <button onclick="AdminPanel.viewData('regions')" style="background:#2a2438;border:1px solid #3a3450;color:#e8e0c8;padding:8px;border-radius:3px;cursor:pointer;width:100%;margin-bottom:6px">查看区域</button>
          <button onclick="AdminPanel.viewData('npcs')" style="background:#2a2438;border:1px solid #3a3450;color:#e8e0c8;padding:8px;border-radius:3px;cursor:pointer;width:100%">查看NPC</button>
        </div>
      </div>
      <div id="admin-detail" style="margin-top:12px;background:#1a1428;border:1px solid #2a2438;border-radius:6px;padding:12px;min-height:200px"></div>
    `;
  },

  statCard(label, value, color) {
    return `<div style="background:#1a1428;border:1px solid #2a2438;border-radius:6px;padding:12px;text-align:center">
      <div style="color:${color};font-size:28px;font-weight:bold">${value}</div>
      <div style="color:#8a7a9a;font-size:12px;margin-top:4px">${label}</div>
    </div>`;
  },

  async loadUsers() {
    const r = await API.get('/admin/users');
    if (!r.ok) return;
    const html = r.users.map(u => `
      <div style="background:#1a1525;padding:8px;border-radius:3px;margin-bottom:6px;display:flex;justify-content:space-between">
        <div>
          <span style="color:#d4af37">${u.username}</span>
          <span style="color:#8a7a9a;font-size:11px;margin-left:8px">${u.is_admin?'管理员':'玩家'}</span>
          <span style="color:#8a7a9a;font-size:11px;margin-left:8px">ID:${u.id}</span>
        </div>
        <div style="font-size:11px;color:#8a7a9a">${new Date(u.last_login*1000).toLocaleString()}</div>
      </div>
    `).join('');
    document.getElementById('admin-detail').innerHTML = `<h3 style="color:#d4af37;margin-bottom:10px">玩家列表（${r.users.length}）</h3>${html}`;
  },

  async showGiveItem() {
    const users = await API.get('/admin/users');
    const html = `
      <h3 style="color:#d4af37;margin-bottom:10px">发放物品</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <select id="gi-user" style="background:#1a1525;border:1px solid #3a3450;color:#e8e0c8;padding:6px;border-radius:3px">
          ${users.users.map(u => `<option value="${u.id}">${u.username}</option>`).join('')}
        </select>
        <input id="gi-item" placeholder="物品ID如iron_sword" style="flex:1;background:#1a1525;border:1px solid #3a3450;color:#e8e0c8;padding:6px;border-radius:3px">
        <input id="gi-qty" type="number" value="1" style="width:80px;background:#1a1525;border:1px solid #3a3450;color:#e8e0c8;padding:6px;border-radius:3px">
        <button onclick="AdminPanel.doGiveItem()" style="background:#d4af37;color:#0a0a14;border:none;padding:6px 12px;border-radius:3px;cursor:pointer">发放</button>
      </div>
      <div style="color:#8a7a9a;font-size:11px;margin-top:8px">常用: iron_sword, spirit_stone_low, foundation_pill, reverse_jade, storage_ring_low</div>
    `;
    document.getElementById('admin-detail').innerHTML = html;
  },

  async doGiveItem() {
    const r = await API.post('/admin/give_item', {
      user_id: parseInt(document.getElementById('gi-user').value),
      item_id: document.getElementById('gi-item').value,
      qty: parseInt(document.getElementById('gi-qty').value)
    });
    alert(r.msg);
  },

  async showSetRealm() {
    const users = await API.get('/admin/users');
    const realms = ['qi_refining_1','qi_refining_5','foundation_1','golden_core_1','nascent_soul_1','divine_transformation_1'];
    const html = `
      <h3 style="color:#d4af37;margin-bottom:10px">设置境界</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <select id="sr-user" style="background:#1a1525;border:1px solid #3a3450;color:#e8e0c8;padding:6px;border-radius:3px">
          ${users.users.map(u => `<option value="${u.id}">${u.username}</option>`).join('')}
        </select>
        <select id="sr-realm" style="background:#1a1525;border:1px solid #3a3450;color:#e8e0c8;padding:6px;border-radius:3px">
          ${realms.map(r => `<option value="${r}">${r}</option>`).join('')}
        </select>
        <button onclick="AdminPanel.doSetRealm()" style="background:#d4af37;color:#0a0a14;border:none;padding:6px 12px;border-radius:3px;cursor:pointer">设置</button>
      </div>
    `;
    document.getElementById('admin-detail').innerHTML = html;
  },

  async doSetRealm() {
    const r = await API.post('/admin/set_realm', {
      user_id: parseInt(document.getElementById('sr-user').value),
      realm: document.getElementById('sr-realm').value
    });
    alert(r.msg);
  },

  async showAddStones() {
    const users = await API.get('/admin/users');
    const html = `
      <h3 style="color:#d4af37;margin-bottom:10px">发放灵石</h3>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <select id="as-user" style="background:#1a1525;border:1px solid #3a3450;color:#e8e0c8;padding:6px;border-radius:3px">
          ${users.users.map(u => `<option value="${u.id}">${u.username}</option>`).join('')}
        </select>
        <input id="as-amount" type="number" value="1000" style="width:120px;background:#1a1525;border:1px solid #3a3450;color:#e8e0c8;padding:6px;border-radius:3px">
        <button onclick="AdminPanel.doAddStones()" style="background:#d4af37;color:#0a0a14;border:none;padding:6px 12px;border-radius:3px;cursor:pointer">发放</button>
      </div>
    `;
    document.getElementById('admin-detail').innerHTML = html;
  },

  async doAddStones() {
    const r = await API.post('/admin/add_spirit_stones', {
      user_id: parseInt(document.getElementById('as-user').value),
      amount: parseInt(document.getElementById('as-amount').value)
    });
    alert(r.msg);
  },

  showBroadcast() {
    document.getElementById('admin-detail').innerHTML = `
      <h3 style="color:#d4af37;margin-bottom:10px">全服公告</h3>
      <textarea id="bc-msg" placeholder="输入公告内容" style="width:100%;height:80px;background:#1a1525;border:1px solid #3a3450;color:#e8e0c8;padding:8px;border-radius:3px"></textarea>
      <button onclick="AdminPanel.doBroadcast()" style="background:#d4af37;color:#0a0a14;border:none;padding:8px 16px;border-radius:3px;cursor:pointer;margin-top:8px">发送全服公告</button>
    `;
  },

  async doBroadcast() {
    const r = await API.post('/admin/broadcast', { msg: document.getElementById('bc-msg').value });
    alert(r.msg);
  },

  async viewData(type) {
    const r = await API.get('/admin/data/' + type);
    if (!r.ok) return;
    const data = r.data;
    const key = Object.keys(data)[0];
    const list = data[key];
    const html = `<h3 style="color:#d4af37;margin-bottom:10px">${type}（${list.length}条）</h3>
      <div style="max-height:500px;overflow:auto;background:#0a0a14;padding:8px;border-radius:3px;font-size:11px;font-family:monospace;color:#a8a8c8">
        ${list.slice(0, 50).map(item => JSON.stringify(item).substring(0, 200)).join('<br>')}
      </div>`;
    document.getElementById('admin-detail').innerHTML = html;
  }
};
