// 逆仙录·天道残卷 - UI管理器
const UI = {
  state: null,

  async init() {
    Renderer.init();
    this.bindEvents();
    await this.refresh();
    this.startPolling();
  },

  bindEvents() {
    const canvas = document.getElementById('game-canvas');
    canvas.addEventListener('click', (e) => {
      const { x, y } = Renderer.pixelToTile(e.clientX, e.clientY);
      this.onMapClick(x, y);
    });
  },

  async onMapClick(x, y) {
    if (!this.state) return;
    if (this.state.player.in_combat) { this.toast('战斗中无法移动', 'error'); return; }
    if (this.state.player.hp <= 0) { this.toast('你已死亡，请重置游戏', 'error'); return; }
    // NPC
    for (const npc of this.state.visible_npcs) {
      if (npc.x === x && npc.y === y) {
        const r = await API.moveTo(x, y);
        if (r.ok) { await this.refresh(); this.openNPCDialog(npc.id); }
        else this.toast(r.msg, 'error');
        return;
      }
    }
    // 妖兽
    for (const b of this.state.visible_beasts) {
      if (b.x === x && b.y === y) {
        const r = await API.moveTo(x, y);
        await this.refresh();
        if (r.action === 'combat') { /* Combat模块处理 */ }
        else if (r.msg) this.toast(r.msg, r.ok ? 'info' : 'error');
        return;
      }
    }
    // 资源
    for (const r of this.state.visible_resources) {
      if (r.x === x && r.y === y) {
        const mv = await API.moveTo(x, y);
        if (mv.action === 'gather') {
          // 草药用小游戏，其他直接采集
          if (r.type === 'herb') {
            Minigames.gatherHerb(r.id, r.name, this._getHerbTier(r.item));
          } else {
            const g = await API.gather(r.id);
            this.toast(g.msg, g.ok ? 'success' : 'error');
            await this.refresh();
          }
        } else if (mv.ok) {
          await this.refresh();
          if (mv.msg) this.toast(mv.msg, 'info');
        }
        return;
      }
    }
    // 建筑
    for (const b of this.state.region.buildings) {
      if (x >= b.x && x < b.x + b.w && y >= b.y && y < b.y + b.h) {
        const r = await API.moveTo(b.x + Math.floor(b.w / 2), b.y + Math.floor(b.h / 2));
        await this.refresh();
        if (r.action) this.handleBuildingAction(r);
        else if (r.msg) this.toast(r.msg, 'info');
        return;
      }
    }
    // 普通移动
    const r = await API.moveTo(x, y);
    await this.refresh();
    if (r.action === 'gather') {
      // 检查是否草药
      const res = this.state.visible_resources.find(rr => rr.id === r.resource_id);
      if (res && res.type === 'herb') {
        Minigames.gatherHerb(r.resource_id, res.name, this._getHerbTier(res.item));
      } else {
        const g = await API.gather(r.resource_id);
        this.toast(g.msg, g.ok ? 'success' : 'error');
        await this.refresh();
      }
    } else if (r.action === 'combat') {
      // 战斗开始
    } else if (r.action === 'talk') {
      this.openNPCDialog(r.npc_id);
    } else if (r.action) {
      this.handleBuildingAction(r);
    } else if (r.msg) {
      this.toast(r.msg, 'info');
    }
  },

  _getHerbTier(itemId) {
    const inv = this.state.player.inventory.find(i => i.item_id === itemId);
    return inv ? inv.tier : 1;
  },

  handleBuildingAction(r) {
    if (r.action === 'alchemy') this.openAlchemy();
    else if (r.action === 'forge') this.openForge();
    else if (r.action === 'learn') this.openLearnTechnique();
    else if (r.action === 'shop') this.openShop(r.shop_type);
    else if (r.action === 'tavern') this.openTavern();
    else if (r.action === 'sect_master') this.openSectMaster();
    else if (r.action === 'farm') this.openFarm();
    else if (r.action === 'auction') this.openAuction();
    else if (r.action === 'mission') this.toast('任务系统开发中', 'info');
    else if (r.msg) this.toast(r.msg, 'info');
  },

  async refresh() {
    const state = await API.getState();
    if (!state) return;
    this.state = state;
    this.renderState(state);
    Renderer.render(state);
    if (state.player.in_combat && !Combat.active) Combat.startFromState(state);
    else if (!state.player.in_combat && Combat.active) Combat.end();
  },

  renderState(state) {
    const p = state.player;
    document.getElementById('player-name').textContent = p.name;
    document.getElementById('player-realm').textContent = p.realm_name;
    document.getElementById('player-lifespan').textContent = p.lifespan.toFixed(1) + '年';
    document.getElementById('player-age').textContent = p.age.toFixed(1);
    document.getElementById('player-money').textContent = p.spirit_stones_value;
    document.getElementById('player-karma').textContent = p.karma;
    document.getElementById('hp-bar').style.width = (p.hp / p.max_hp * 100) + '%';
    document.getElementById('hp-text').textContent = `${p.hp}/${p.max_hp}`;
    document.getElementById('qi-bar').style.width = (p.qi / p.max_qi * 100) + '%';
    document.getElementById('qi-text').textContent = `${p.qi}/${p.max_qi}`;
    document.getElementById('realm-progress').style.width = (p.realm_progress * 100) + '%';
    document.getElementById('game-time').textContent = `第${state.world.day}日 ${String(state.world.hour).padStart(2,'0')}:${String(state.world.minute).padStart(2,'0')}`;
    document.getElementById('region-name').textContent = state.region.name;
    document.getElementById('region-desc').textContent = state.region.description;
    document.getElementById('coords').textContent = `(${p.x},${p.y}) 攻${p.attack} 防${p.defense} 速${p.speed} 悟${p.comprehension}`;
    this.renderLog(state.log);
  },

  renderLog(log) {
    const el = document.getElementById('event-log');
    const lastT = el.lastElementChild ? el.lastElementChild.getAttribute('data-t') : -1;
    const newLogs = log.filter(l => l.t > lastT);
    if (newLogs.length === 0 && el.children.length > 0) return;
    if (el.children.length === 0 || log.length < el.children.length) {
      el.innerHTML = '';
      for (const l of log.slice(-50)) this.appendLog(l);
    } else {
      for (const l of newLogs) this.appendLog(l);
    }
    el.scrollTop = el.scrollHeight;
  },

  appendLog(l) {
    const el = document.getElementById('event-log');
    const div = document.createElement('div');
    div.className = 'log-entry ' + (l.level || 'info');
    div.setAttribute('data-t', l.t);
    div.textContent = l.msg;
    el.appendChild(div);
    while (el.children.length > 100) el.removeChild(el.firstChild);
  },

  startPolling() {
    setInterval(() => this.refresh(), 1500);
    setInterval(() => { if (this.state) Renderer.render(this.state); }, 100);
  },

  toast(msg, type = 'info') {
    const c = document.getElementById('toast-container');
    const t = document.createElement('div');
    t.className = 'toast ' + type;
    t.textContent = msg;
    c.appendChild(t);
    setTimeout(() => {
      t.style.opacity = '0';
      t.style.transition = 'opacity 0.3s';
      setTimeout(() => t.remove(), 300);
    }, 2500);
  },

  openModal(title, bodyHtml) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = bodyHtml;
    document.getElementById('modal-overlay').style.display = 'flex';
  },
  closeModal() { document.getElementById('modal-overlay').style.display = 'none'; },
  setModalBody(html) { document.getElementById('modal-body').innerHTML = html; },

  // ==================== 行囊 ====================
  openInventory() {
    const p = this.state.player;
    let html = '<div class="tab-bar"><div class="tab active" onclick="UI.switchInvTab(\'all\')">全部</div><div class="tab" onclick="UI.switchInvTab(\'pill\')">丹药</div><div class="tab" onclick="UI.switchInvTab(\'weapon\')">武器</div><div class="tab" onclick="UI.switchInvTab(\'armor\')">防具</div><div class="tab" onclick="UI.switchInvTab(\'material\')">材料</div><div class="tab" onclick="UI.switchInvTab(\'other\')">其他</div></div>';
    html += '<div id="inv-list"></div>';
    html += '<div class="section-title">装备</div>';
    html += `<div class="detail-box">
      <div class="attr-row"><span class="attr-name">武器</span><span class="attr-value">${p.equipped.weapon ? this.getItemName(p.equipped.weapon) : '无'} ${p.equipped.weapon ? `<button class="btn" onclick="UI.unequip('weapon')">卸下</button>` : ''}</span></div>
      <div class="attr-row"><span class="attr-name">防具</span><span class="attr-value">${p.equipped.armor ? this.getItemName(p.equipped.armor) : '无'} ${p.equipped.armor ? `<button class="btn" onclick="UI.unequip('armor')">卸下</button>` : ''}</span></div>
    </div>`;
    this.openModal('行囊', html);
    this.switchInvTab('all');
  },

  switchInvTab(tab) {
    document.querySelectorAll('.tab-bar .tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    const p = this.state.player;
    const list = document.getElementById('inv-list');
    list.innerHTML = '';
    for (const inv of p.inventory) {
      let show = false;
      if (tab === 'all') show = true;
      else if (tab === 'pill') show = inv.type === 'pill';
      else if (tab === 'weapon') show = inv.type === 'weapon';
      else if (tab === 'armor') show = inv.type === 'armor';
      else if (tab === 'material') show = ['herb', 'ore', 'beast_part', 'beast_core', 'spirit_stone', 'misc', 'seed', 'formation'].includes(inv.type);
      else if (tab === 'other') show = ['jade_slip', 'talisman'].includes(inv.type);
      if (!show) continue;
      const tierClass = `tier-${inv.tier}`;
      const rarityClass = `rarity-${inv.rarity}`;
      let actions = '';
      if (inv.type === 'pill' || inv.type === 'talisman') actions = `<button class="btn gold" onclick="UI.useItem('${inv.item_id}')">使用</button>`;
      else if (inv.type === 'weapon' || inv.type === 'armor') actions = `<button class="btn gold" onclick="UI.equip('${inv.item_id}')">装备</button>`;
      else if (inv.type === 'jade_slip' && inv.teaches) actions = `<button class="btn gold" onclick="UI.learnTechnique('${inv.teaches}')">学习</button>`;
      else if (inv.type === 'seed') actions = `<button class="btn gold" onclick="UI.plantSeed('${inv.item_id}')">种植</button>`;
      const div = document.createElement('div');
      div.className = 'item-row';
      div.innerHTML = `<div><span class="item-name ${rarityClass}">${inv.name}</span><span class="item-tier ${tierClass}">${inv.tier}阶</span><span class="item-qty">×${inv.qty}</span></div><div>${actions}<button class="btn" onclick="UI.showItemDetail('${inv.item_id}')" style="margin-left:4px">详情</button></div>`;
      list.appendChild(div);
    }
  },

  getItemName(id) { for (const inv of this.state.player.inventory) if (inv.item_id === id) return inv.name; return id; },

  async useItem(id) { const r = await API.useItem(id); this.toast(r.msg, r.ok ? 'success' : 'error'); await this.refresh(); this.openInventory(); },
  async equip(id) { const r = await API.equipItem(id); this.toast(r.msg, r.ok ? 'success' : 'error'); await this.refresh(); this.openInventory(); },
  async unequip(slot) { const r = await API.unequipItem(slot); this.toast(r.msg, r.ok ? 'success' : 'error'); await this.refresh(); this.openInventory(); },
  async learnTechnique(tid) { const r = await API.learnTechnique(tid); this.toast(r.msg, r.ok ? 'success' : 'error'); await this.refresh(); this.openInventory(); },
  async plantSeed(seedId) { const r = await API.plantSeed(seedId, 0); this.toast(r.msg, r.ok ? 'success' : 'error'); await this.refresh(); this.openFarm(); },

  showItemDetail(id) {
    const inv = this.state.player.inventory.find(i => i.item_id === id);
    if (!inv) return;
    let attrsHtml = '';
    for (const [k, v] of Object.entries(inv.attrs || {})) attrsHtml += `<div class="attr-row"><span class="attr-name">${k}</span><span class="attr-value">${v}</span></div>`;
    if (inv.effect) {
      attrsHtml += '<div class="section-title">效果</div>';
      for (const [k, v] of Object.entries(inv.effect)) attrsHtml += `<div class="attr-row"><span class="attr-name">${k}</span><span class="attr-value">${v}</span></div>`;
    }
    this.openModal(inv.name, `<div class="detail-box">
      <div class="attr-row"><span class="attr-name">类型</span><span class="attr-value">${inv.type}</span></div>
      <div class="attr-row"><span class="attr-name">等阶</span><span class="attr-value tier-${inv.tier}">${inv.tier}阶</span></div>
      <div class="attr-row"><span class="attr-name">稀有度</span><span class="attr-value rarity-${inv.rarity}">${inv.rarity}</span></div>
      <div class="attr-row"><span class="attr-name">价值</span><span class="attr-value">${inv.value}灵石</span></div>
      ${inv.desc ? `<div style="margin-top:8px;color:#e8d4b8;font-style:italic;">"${inv.desc}"</div>` : ''}
    </div>${attrsHtml ? `<div class="section-title">属性</div><div class="detail-box">${attrsHtml}</div>` : ''}`);
  },

  // ==================== 功法 ====================
  openTechniques() {
    const p = this.state.player;
    let html = '';
    if (p.techniques.length === 0) html = '<div class="detail-box">尚未学习任何功法。前往藏经阁学习，或使用功法玉简。</div>';
    else {
      for (const t of p.techniques) {
        const isActive = t.id === p.active_technique;
        html += `<div class="detail-box" style="border-color:${isActive ? '#d4af37' : '#2a2438'}">`;
        html += `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><span style="color:#d4af37;font-size:15px;font-weight:bold;">${t.name}</span>${isActive ? '<span style="color:#6bc832;font-size:12px">● 修炼中</span>' : `<button class="btn gold" onclick="UI.activateTechnique('${t.id}')">激活</button>`}</div>`;
        html += `<div style="color:#8a7a9a;font-size:11px;margin-bottom:6px">属性：${t.element} | 完整度：${(t.completeness * 100).toFixed(0)}%</div>`;
        html += `<div style="color:#a8a8c8;font-size:12px;margin-bottom:8px">${t.desc}</div>`;
        html += '<div class="section-title">修炼阶段</div>';
        for (let i = 0; i < t.stages.length; i++) {
          const s = t.stages[i];
          const reversed = t.reversed_stages && t.reversed_stages[i];
          const canPractice = REALM_ORDER.indexOf(p.realm) >= REALM_ORDER.indexOf(s.realm_required);
          html += `<div style="margin:6px 0;padding:6px;background:rgba(26,21,37,0.6);border-radius:3px;border-left:3px solid ${reversed ? '#c832c8' : (canPractice ? '#d4af37' : '#3a3450')}">`;
          html += `<div style="color:${reversed ? '#c832c8' : '#d4af37'};font-size:13px">${s.name} ${reversed ? '◉ 已逆修' : ''}</div>`;
          html += `<div style="color:#8a7a9a;font-size:11px">需要境界：${REALM_NAMES[s.realm_required] || s.realm_required}</div>`;
          if (canPractice && !reversed && s.reversal) {
            html += `<div style="margin-top:4px;font-size:11px;color:#c896ff">逆修方案：${s.reversal.method}</div>`;
            html += `<div style="font-size:11px;color:#6bc832">收益：${s.reversal.benefit}</div>`;
            html += `<button class="btn gold" style="margin-top:4px" onclick="UI.reverseTechnique('${t.id}', ${i})">使用逆道玉简逆修</button>`;
          }
          html += '</div>';
        }
        html += '<div class="section-title">神通</div>';
        for (const sk of t.combat_skills) {
          const canUse = REALM_ORDER.indexOf(p.realm) >= REALM_ORDER.indexOf(sk.unlock);
          const label = sk.label || sk.name;
          html += `<div style="margin:4px 0;padding:6px;background:rgba(26,21,37,0.4);border-radius:3px;font-size:12px"><span style="color:${canUse ? '#3296c8' : '#6a5a4a'}">${label}</span><span style="color:#8a7a9a;margin-left:8px">需${REALM_NAMES[sk.unlock] || sk.unlock}</span><span style="color:#3296c8;float:right">${sk.cost}灵气</span></div>`;
        }
        html += '</div>';
      }
    }
    this.openModal('功法', html);
  },

  async activateTechnique(tid) { const r = await API.activateTechnique(tid); this.toast(r.msg, r.ok ? 'success' : 'error'); await this.refresh(); this.openTechniques(); },
  async reverseTechnique(tid, stageIdx) { const r = await API.reverseTechnique(tid, stageIdx); this.toast(r.msg, r.ok ? 'success' : 'error'); await this.refresh(); this.openTechniques(); },

  // ==================== 修炼 ====================
  openCultivate() {
    const p = this.state.player;
    if (!p.active_technique) { this.toast('请先激活功法', 'error'); return; }
    if (p.in_combat) { this.toast('战斗中无法修炼', 'error'); return; }
    const tech = p.techniques.find(t => t.id === p.active_technique);
    const html = `
      <div class="detail-box">
        <div style="color:#d4af37;margin-bottom:6px">当前功法：${tech ? tech.name : '无'}</div>
        <div style="color:#8a7a9a;font-size:12px">完整度：${tech ? (tech.completeness * 100).toFixed(0) + '%' : '-'} | 灵根：${p.spiritual_root === 'pseudo' ? '伪灵根（修炼效率60%）' : p.spiritual_root}</div>
        <div style="color:#8a7a9a;font-size:12px;margin-top:4px">区域灵气浓度：${(this.state.region.spirit_density * 100).toFixed(0)}% | 悟性：${p.comprehension}</div>
      </div>
      <div class="section-title">选择修炼时长</div>
      <div class="cultivate-options">
        <button class="cultivate-btn" onclick="UI.doCultivate(1, 3)"><span class="hours">1小时</span><span class="desc">日常修炼</span></button>
        <button class="cultivate-btn" onclick="UI.doCultivate(4, 3)"><span class="hours">4小时</span><span class="desc">沉浸修炼</span></button>
        <button class="cultivate-btn" onclick="UI.doCultivate(8, 5)"><span class="hours">8小时</span><span class="desc">一日苦修</span></button>
      </div>
      <div class="section-title">周天数（影响效率与风险）</div>
      <div class="cultivate-options">
        <button class="cultivate-btn" onclick="UI.doCultivate(4, 1)"><span class="hours">1周天</span><span class="desc">保守</span></button>
        <button class="cultivate-btn" onclick="UI.doCultivate(4, 3)"><span class="hours">3周天</span><span class="desc">正常</span></button>
        <button class="cultivate-btn" onclick="UI.doCultivate(4, 7)"><span class="hours">7周天</span><span class="desc">激进(走火风险)</span></button>
      </div>
      ${p.realm_progress >= 1.0 ? '<div class="detail-box" style="border-color:#d4af37"><div style="color:#d4af37">境界圆满！可尝试突破</div><button class="btn gold" onclick="UI.openBreakthrough()">突破</button></div>' : ''}
    `;
    this.openModal('修炼', html);
  },

  async doCultivate(hours, cycles) {
    this.closeModal();
    const r = await API.cultivate(hours, 'sect', cycles, null, null);
    this.toast(r.msg, r.ok ? 'success' : 'error');
    await this.refresh();
    if (r.can_breakthrough) this.openBreakthrough();
  },

  openBreakthrough() {
    const p = this.state.player;
    const html = `
      <div class="detail-box">
        <div style="color:#d4af37;margin-bottom:6px">突破境界</div>
        <div style="color:#8a7a9a;font-size:12px">当前：${p.realm_name} | 业力：${p.karma} ${p.karma < -500 ? '(心魔风险高!)' : ''}</div>
      </div>
      <div class="section-title">选择突破方式</div>
      <div class="cultivate-options">
        <button class="cultivate-btn" onclick="UI.doBreakthrough('water_grind')"><span class="hours">水磨工夫</span><span class="desc">1年,风险5%</span></button>
        <button class="cultivate-btn" onclick="UI.doBreakthrough('pill')"><span class="hours">破境丹</span><span class="desc">需破境丹</span></button>
        <button class="cultivate-btn" onclick="UI.doBreakthrough('life_death_battle')"><span class="hours">生死战</span><span class="desc">风险50%</span></button>
        <button class="cultivate-btn" onclick="UI.doBreakthrough('comprehension')"><span class="hours">顿悟</span><span class="desc">需悟性100+</span></button>
      </div>
    `;
    this.openModal('突破', html);
  },

  async doBreakthrough(method) {
    this.closeModal();
    // 大境界突破需先渡劫
    const p = this.state.player;
    const realmId = p.realm;
    const majorRealms = ['foundation_1', 'golden_core_1', 'nascent_soul_1', 'divine_transformation_1', 'void_refining_1'];
    const idx = REALM_ORDER.indexOf(realmId);
    const nextRealm = idx >= 0 && idx + 1 < REALM_ORDER.length ? REALM_ORDER[idx + 1] : null;
    // 启动突破小游戏
    Minigames.breakthrough(method);
    // 小游戏完成后的天劫检查在 Minigames.btCollect 中处理
    // 这里记录是否需要渡劫
    Minigames._pendingTribulation = (nextRealm && majorRealms.includes(nextRealm));
  },

  async afterBreakthroughMinigame(success, method) {
    if (success && Minigames._pendingTribulation) {
      // 大境界突破成功，触发天劫
      const r = await API.triggerTribulation();
      if (r.action === 'tribulation') {
        Tribulation.start(r.tribulation);
      }
    }
    Minigames._pendingTribulation = false;
  },

  openRest() {
    const html = `<div class="section-title">打坐恢复</div><div style="color:#8a7a9a;font-size:12px;margin-bottom:10px">打坐可恢复HP和灵气，若有激活功法则有微量修炼进度。</div>
    <div class="cultivate-options">
      <button class="cultivate-btn" onclick="UI.doRest(1)"><span class="hours">1小时</span><span class="desc">小憩</span></button>
      <button class="cultivate-btn" onclick="UI.doRest(4)"><span class="hours">4小时</span><span class="desc">打坐</span></button>
      <button class="cultivate-btn" onclick="UI.doRest(8)"><span class="hours">8小时</span><span class="desc">静修</span></button>
    </div>`;
    this.openModal('打坐', html);
  },

  async doRest(hours) { this.closeModal(); const r = await API.rest(hours); this.toast(r.msg, r.ok ? 'success' : 'error'); await this.refresh(); },

  openSeclusion() {
    const p = this.state.player;
    if (p.lifespan < 30) this.toast('寿元不足，闭关有风险！', 'error');
    const html = `<div class="detail-box"><div style="color:#d4af37">闭关修炼</div><div style="color:#8a7a9a;font-size:12px;margin-top:4px">闭关期间大幅提升修为，但时间快速流逝，寿元持续消耗。</div><div style="color:#c896ff;font-size:12px;margin-top:4px">注意：闭关期间功法缺陷会快速累积！</div></div>
    <div class="section-title">选择闭关时长</div>
    <div class="cultivate-options">
      <button class="cultivate-btn" onclick="UI.doSeclusion(7)"><span class="hours">7天</span><span class="desc">小闭关</span></button>
      <button class="cultivate-btn" onclick="UI.doSeclusion(30)"><span class="hours">30天</span><span class="desc">大闭关</span></button>
      <button class="cultivate-btn" onclick="UI.doSeclusion(90)"><span class="hours">90天</span><span class="desc">百日关</span></button>
    </div>
    <div style="color:#8a7a9a;font-size:11px;margin-top:8px">当前寿元：${p.lifespan.toFixed(1)}年</div>`;
    this.openModal('闭关', html);
  },

  async doSeclusion(days) {
    this.closeModal();
    const r = await API.seclusion(days);
    this.toast(r.msg, r.ok ? 'success' : 'error');
    await this.refresh();
    if (r.can_breakthrough) this.openBreakthrough();
    if (r.death) this.toast('闭关中坐化，游戏结束', 'error');
  },

  // ==================== 角色 ====================
  openCharacter() {
    const p = this.state.player;
    let attrsHtml = '';
    for (const [k, v] of Object.entries(p.attributes)) if (v !== 0) attrsHtml += `<div class="attr-row"><span class="attr-name">${ATTR_NAMES[k] || k}</span><span class="attr-value">${v.toFixed(2)}</span></div>`;
    const html = `<div class="detail-box">
      <div class="attr-row"><span class="attr-name">道号</span><span class="attr-value">${p.name}</span></div>
      <div class="attr-row"><span class="attr-name">境界</span><span class="attr-value">${p.realm_name}</span></div>
      <div class="attr-row"><span class="attr-name">境界进度</span><span class="attr-value">${(p.realm_progress * 100).toFixed(1)}%</span></div>
      <div class="attr-row"><span class="attr-name">年龄</span><span class="attr-value">${p.age.toFixed(1)}岁</span></div>
      <div class="attr-row"><span class="attr-name">寿元</span><span class="attr-value" style="color:${p.lifespan < 20 ? '#ff6b6b' : '#d4af37'}">${p.lifespan.toFixed(1)}年</span></div>
      <div class="attr-row"><span class="attr-name">灵根</span><span class="attr-value">${p.spiritual_root === 'pseudo' ? '伪灵根' : p.spiritual_root}</span></div>
      <div class="attr-row"><span class="attr-name">悟性</span><span class="attr-value">${p.comprehension.toFixed(1)}</span></div>
      <div class="attr-row"><span class="attr-name">业力</span><span class="attr-value" style="color:${p.karma < -500 ? '#ff6b6b' : (p.karma > 500 ? '#6bc832' : '#d4af37')}">${p.karma}</span></div>
    </div>
    <div class="section-title">战斗属性</div>
    <div class="detail-box">
      <div class="attr-row"><span class="attr-name">气血</span><span class="attr-value">${p.hp}/${p.max_hp}</span></div>
      <div class="attr-row"><span class="attr-name">灵气</span><span class="attr-value">${p.qi}/${p.max_qi}</span></div>
      <div class="attr-row"><span class="attr-name">攻击</span><span class="attr-value">${p.attack}</span></div>
      <div class="attr-row"><span class="attr-name">防御</span><span class="attr-value">${p.defense}</span></div>
      <div class="attr-row"><span class="attr-name">身法</span><span class="attr-value">${p.speed}</span></div>
    </div>
    <div class="section-title">属性亲和</div>
    <div class="detail-box">${attrsHtml || '<div style="color:#8a7a9a">无属性亲和</div>'}</div>
    <div class="section-title">修行记录</div>
    <div class="detail-box">
      <div class="attr-row"><span class="attr-name">击杀妖兽</span><span class="attr-value">${p.kills}</span></div>
      <div class="attr-row"><span class="attr-name">炼制丹药</span><span class="attr-value">${p.pills_crafted}</span></div>
      <div class="attr-row"><span class="attr-name">砍伐树木</span><span class="attr-value">${p.trees_cut}</span></div>
      <div class="attr-row"><span class="attr-name">持有逆道玉简</span><span class="attr-value">${p.has_reverse_jade ? '是' : '否'}</span></div>
    </div>`;
    this.openModal('角色', html);
  },

  // ==================== 身体系统 ====================
  openBody() {
    const p = this.state.player;
    const body = p.body;
    let meridianHtml = '<div class="meridian-list">';
    for (const [name, m] of Object.entries(body.meridians)) {
      const blocked = m.blocked ? 'blocked' : '';
      const integColor = m.integrity > 70 ? '#6bc832' : (m.integrity > 30 ? '#ffaa6b' : '#ff6b6b');
      meridianHtml += `<div class="meridian-row ${blocked}"><span>${name}${m.blocked ? '(堵)' : ''}</span><span style="color:${integColor}">${m.integrity.toFixed(0)}%</span></div>`;
    }
    meridianHtml += '</div>';
    const dantian = body.dantian;
    const dantianColor = dantian.cracks > 3 ? '#ff6b6b' : (dantian.cracks > 0 ? '#ffaa6b' : '#6bc832');
    const html = `
      <div class="section-title">丹田</div>
      <div class="detail-box">
        <div class="attr-row"><span class="attr-name">容量</span><span class="attr-value">${dantian.current}/${dantian.capacity}</span></div>
        <div class="attr-row"><span class="attr-name">品质</span><span class="attr-value">${dantian.quality}</span></div>
        <div class="attr-row"><span class="attr-name">裂纹</span><span class="attr-value" style="color:${dantianColor}">${dantian.cracks}处</span></div>
      </div>
      <div class="section-title">经脉（20条）</div>
      <div class="detail-box">${meridianHtml}</div>
      <div class="section-title">肉身强度</div>
      <div class="detail-box">
        <div class="attr-row"><span class="attr-name">皮肤韧性</span><span class="attr-value">${body.flesh.skin.toughness}</span></div>
        <div class="attr-row"><span class="attr-name">肌肉力量</span><span class="attr-value">${body.flesh.muscle.strength}</span></div>
        <div class="attr-row"><span class="attr-name">骨骼密度</span><span class="attr-value">${body.flesh.bone.density}</span></div>
        <div class="attr-row"><span class="attr-name">灵髓</span><span class="attr-value">${body.flesh.bone.spiritual_marrow ? '有' : '无'}</span></div>
      </div>
      <div class="section-title">神识</div>
      <div class="detail-box">
        <div class="attr-row"><span class="attr-name">扫描范围</span><span class="attr-value">${body.spirit.range}格</span></div>
        <div class="attr-row"><span class="attr-name">洞察力</span><span class="attr-value">${body.spirit.sharpness}</span></div>
        <div class="attr-row"><span class="attr-name">抗夺舍</span><span class="attr-value">${body.spirit.resilience}</span></div>
        <div class="attr-row"><span class="attr-name">魂魄碎片</span><span class="attr-value">${body.spirit.soul_fragments}</span></div>
      </div>
      ${body.conditions.length > 0 ? `<div class="section-title">状态</div><div class="detail-box">${body.conditions.map(c => `<div style="color:#ff6b6b">● ${c.type}: ${c.source}</div>`).join('')}</div>` : ''}
    `;
    this.openModal('身体', html);
  },

  // ==================== 学习功法（藏经阁） ====================
  openLearnTechnique() {
    const p = this.state.player;
    const html = `<div class="detail-box"><div style="color:#d4af37;margin-bottom:6px">藏经阁</div><div style="color:#8a7a9a;font-size:12px">藏书万卷，皆上古传承。可在此学习基础功法。</div></div>
    <div class="section-title">可学功法</div>
    ${['wood_basic', 'fire_basic', 'ice_basic', 'metal_basic', 'earth_basic'].map(tid => {
      const tech = TECHNIQUE_DATA[tid];
      if (!tech) return '';
      const learned = p.techniques.find(t => t.id === tid);
      return `<div class="detail-box">
        <div style="color:#d4af37;font-weight:bold">${tech.name} <span style="color:#8a7a9a;font-weight:normal;font-size:11px">${tech.element}属性</span></div>
        <div style="color:#a8a8c8;font-size:12px;margin:4px 0">${tech.desc}</div>
        <div style="color:#8a7a9a;font-size:11px">完整度：${(tech.completeness * 100).toFixed(0)}%</div>
        ${learned ? '<div style="color:#6bc832;font-size:12px;margin-top:4px">已学习</div>' : `<button class="btn gold" style="margin-top:6px" onclick="UI.learnAtLibrary('${tid}')">学习（消耗对应玉简）</button>`}
      </div>`;
    }).join('')}`;
    this.openModal('藏经阁', html);
  },

  async learnAtLibrary(tid) { const r = await API.learnTechnique(tid); this.toast(r.msg, r.ok ? 'success' : 'error'); await this.refresh(); this.openLearnTechnique(); },

  // ==================== 商店 ====================
  async openShop(shopType) {
    const items = await API.shopList(shopType);
    const shopNames = { herb: '百草堂', ore: '千锤铺', pill: '丹药阁', weapon: '兵器坊', talisman: '符箓阁' };
    let html = `<div class="detail-box"><div style="color:#d4af37">欢迎光临${shopNames[shopType] || '商店'}</div><div style="color:#8a7a9a;font-size:12px;margin-top:4px">当前灵石：${this.state.player.spirit_stones_value}</div></div>`;
    html += '<div class="section-title">购买</div>';
    for (const it of items) {
      const priceDiff = it.price - it.base_price;
      const priceColor = priceDiff > 0 ? '#ff6b6b' : (priceDiff < 0 ? '#6bc832' : '#d4af37');
      html += `<div class="item-row">
        <div>
          <span class="item-name ${it.tier >= 5 ? 'rarity-epic' : (it.tier >= 3 ? 'rarity-rare' : (it.tier >= 2 ? 'rarity-uncommon' : 'rarity-common'))}">${it.name}</span>
          <span class="item-tier tier-${it.tier}">${it.tier}阶</span>
          <div style="font-size:10px;color:#8a7a9a;margin-top:2px">${it.desc}</div>
        </div>
        <div>
          <span style="color:${priceColor};margin-right:6px">${it.price}灵石${priceDiff !== 0 ? `(${priceDiff>0?'+':''}${priceDiff})` : ''}</span>
          <button class="btn gold" onclick="UI.buyItem('${it.item_id}', 1)">购买</button>
        </div>
      </div>`;
    }
    html += '<div class="section-title">出售（半价）</div>';
    for (const inv of this.state.player.inventory) {
      if (inv.item_id === 'reverse_jade') continue;
      const sellPrice = Math.max(1, Math.floor(inv.value * 0.5));
      html += `<div class="item-row">
        <div><span class="item-name">${inv.name}</span><span class="item-qty">×${inv.qty}</span></div>
        <div><span style="color:#d4af37;margin-right:6px">${sellPrice}灵石</span><button class="btn" onclick="UI.sellItem('${inv.item_id}', 1)">出售</button></div>
      </div>`;
    }
    this.openModal(shopNames[shopType] || '商店', html);
  },

  async buyItem(id, qty) {
    const r = await API.shopBuy(id, qty);
    this.toast(r.msg, r.ok ? 'success' : 'error');
    await this.refresh();
    const title = document.getElementById('modal-title').textContent;
    const shopType = { '百草堂': 'herb', '千锤铺': 'ore', '丹药阁': 'pill', '兵器坊': 'weapon', '符箓阁': 'talisman' }[title];
    if (shopType) this.openShop(shopType);
  },

  async sellItem(id, qty) {
    const r = await API.shopSell(id, qty);
    this.toast(r.msg, r.ok ? 'success' : 'error');
    await this.refresh();
    const title = document.getElementById('modal-title').textContent;
    const shopType = { '百草堂': 'herb', '千锤铺': 'ore', '丹药阁': 'pill', '兵器坊': 'weapon', '符箓阁': 'talisman' }[title];
    if (shopType) this.openShop(shopType);
  },

  // ==================== 醉仙楼 ====================
  openTavern() {
    const html = `<div class="npc-dialog"><div class="npc-name">醉仙楼掌柜</div><div>客官住店还是用饭？本楼消息灵通，价格公道。</div></div>
    <div class="detail-box">
      <div class="attr-row"><span class="attr-name">住宿（恢复HP/QI）</span><button class="btn gold" onclick="UI.tavernRest()">5灵石</button></div>
      <div class="attr-row" style="margin-top:6px"><span class="attr-name">打听情报</span><button class="btn" onclick="UI.tavernInfo()">20灵石</button></div>
    </div>`;
    this.openModal('醉仙楼', html);
  },

  async tavernRest() {
    if (this.state.player.spirit_stones_value < 5) { this.toast('灵石不足', 'error'); return; }
    await API.shopBuy('qi_pill', 0);
    await API.rest(8);
    await API.shopSell('spirit_stone_low', 5);
    this.toast('休息8小时，HP/QI已恢复', 'success');
    this.closeModal();
    await this.refresh();
  },

  async tavernInfo() {
    if (this.state.player.spirit_stones_value < 20) { this.toast('灵石不足', 'error'); return; }
    await API.shopSell('spirit_stone_low', 20);
    const infos = ['听说万妖山脉深处最近有大能遗迹现世，但已有金丹期修士前往，恐有凶险。', '坊市拍卖行下月将有上品法器拍卖。', '青云宗掌门最近在物色传承弟子。', '魔门近日动作频繁，听闻有人在追踪一位持玉简的少年。', '万妖山脉的赤焰虎最近躁动异常。'];
    this.toast('掌柜低声说：' + infos[Math.floor(Math.random() * infos.length)], 'info');
    this.closeModal();
    await this.refresh();
  },

  openSectMaster() {
    const npc = this.state.visible_npcs.find(n => n.id === 'npc_master_qingyun');
    if (npc) this.openNPCDialog('npc_master_qingyun');
    else this.toast('掌门不在主殿', 'info');
  },

  // ==================== NPC对话 ====================
  async openNPCDialog(npcId) {
    const r = await API.talkNpc(npcId);
    if (!r.ok) { this.toast(r.msg, 'error'); return; }
    const npc = this.state.visible_npcs.find(n => n.id === npcId);
    let html = `<div class="npc-dialog"><div class="npc-name">${npc.name}</div><div>${npc.title}</div><div style="margin-top:8px">${r.msg}</div></div>`;
    html += `<div class="detail-box"><div class="attr-row"><span class="attr-name">关系</span><span class="attr-value" style="color:${npc.relationship >= 50 ? '#6bc832' : (npc.relationship < 0 ? '#ff6b6b' : '#d4af37')}">${npc.relationship}</span></div></div>`;
    html += '<div class="section-title">行动</div><div class="npc-actions">';
    html += `<button class="btn" onclick="UI.openGift('${npcId}')">赠送礼物</button>`;
    if (r.action === 'shop') html += `<button class="btn gold" onclick="UI.openShop('${r.shop_type}')">交易</button>`;
    if (r.action === 'services') for (const s of r.services) html += `<button class="btn gold" onclick="UI.npcService('${npcId}', '${s.name}')">${s.name}（${s.cost}灵石）</button>`;
    if (r.action === 'quest' && r.quests) for (const q of r.quests) html += `<button class="btn gold" onclick="UI.acceptQuest('${q.id}')">${q.name}</button>`;
    html += '</div>';
    if (r.quests && r.quests.length) {
      html += '<div class="section-title">可接任务</div>';
      for (const q of r.quests) html += `<div class="detail-box"><div style="color:#d4af37">${q.name}</div><div style="color:#a8a8c8;font-size:12px;margin:4px 0">${q.desc}</div></div>`;
    }
    this.openModal(npc.name, html);
  },

  openGift(npcId) {
    const p = this.state.player;
    let html = '<div class="section-title">选择礼物</div>';
    for (const inv of p.inventory) {
      if (inv.item_id === 'reverse_jade') continue;
      html += `<div class="item-row"><div><span class="item-name">${inv.name}</span><span class="item-qty">×${inv.qty}</span></div><button class="btn gold" onclick="UI.doGift('${npcId}', '${inv.item_id}')">赠送</button></div>`;
    }
    this.setModalBody(html);
  },

  async doGift(npcId, itemId) {
    const r = await API.giftNpc(npcId, itemId, 1);
    this.toast(r.msg, r.ok ? 'success' : 'error');
    await this.refresh();
    this.openNPCDialog(npcId);
  },

  async npcService(npcId, serviceName) { this.toast('服务：' + serviceName, 'info'); this.closeModal(); },
  async acceptQuest(qid) { this.toast('已接受任务', 'info'); this.closeModal(); },

  // ==================== 药园（种田） ====================
  openFarm() {
    const p = this.state.player;
    let plotsHtml = '';
    for (let i = 0; i < 4; i++) {
      const plot = p.farm_plots[i];
      if (plot) {
        const remaining = (plot.harvest_time - this.state.world.game_time) / (24 * 60);
        const ready = remaining <= 0;
        plotsHtml += `<div class="detail-box">
          <div style="color:${ready ? '#6bc832' : '#d4af37'}">第${i+1}块地: ${plot.plant_id}</div>
          <div style="color:#8a7a9a;font-size:11px">${ready ? '已成熟！' : `还需${remaining.toFixed(1)}日`}</div>
          ${ready ? `<button class="btn gold" onclick="UI.harvestCrop(${i})">收获</button>` : ''}
        </div>`;
      } else {
        plotsHtml += `<div class="detail-box"><div style="color:#8a7a9a">第${i+1}块地: 空闲</div></div>`;
      }
    }
    const html = `<div class="detail-box"><div style="color:#d4af37;margin-bottom:6px">药园</div><div style="color:#8a7a9a;font-size:12px">种植灵药种子，等待成熟后收获。在行囊中点击种子可种植。</div></div>
    <div class="section-title">农田（4块）</div>
    ${plotsHtml}`;
    this.openModal('药园', html);
  },

  async harvestCrop(plotIdx) {
    const r = await API.harvest(plotIdx);
    this.toast(r.msg, r.ok ? 'success' : 'error');
    await this.refresh();
    this.openFarm();
  },

  // ==================== 灵兽 ====================
  openPets() {
    const p = this.state.player;
    let html = '<div class="detail-box"><div style="color:#d4af37;margin-bottom:6px">灵兽</div><div style="color:#8a7a9a;font-size:12px">已驯服的妖兽可成为伙伴。需要契约符驯服。</div></div>';
    if (p.pets.length === 0) html += '<div class="detail-box" style="color:#8a7a9a">尚无灵兽</div>';
    else {
      for (const pet of p.pets) {
        html += `<div class="detail-box">
          <div style="color:#d4af37;font-weight:bold">${pet.name} <span style="color:#8a7a9a;font-weight:normal;font-size:11px">${pet.tier}阶</span></div>
          <div class="attr-row"><span class="attr-name">气血</span><span class="attr-value">${pet.hp}</span></div>
          <div class="attr-row"><span class="attr-name">攻击</span><span class="attr-value">${pet.attack}</span></div>
          <div class="attr-row"><span class="attr-name">忠诚</span><span class="attr-value">${pet.loyalty}</span></div>
        </div>`;
      }
    }
    this.openModal('灵兽', html);
  },

  // ==================== 宗门 ====================
  openSects() {
    const p = this.state.player;
    let html = `<div class="detail-box"><div style="color:#d4af37;margin-bottom:6px">宗门</div><div style="color:#8a7a9a;font-size:12px">${p.sect ? '当前宗门：' + p.sect : '尚未加入宗门'}</div></div>`;
    html += '<div class="section-title">已知宗门</div>';
    const sects = ['qingyun_sect_info', 'dan_dao_zong', 'qi_zong', 'wan_yao_men', 'jian_ge', 'fu_zong', 'zhen_fa_men'];
    for (const sid of sects) {
      const s = SECT_DATA[sid];
      if (s) {
        html += `<div class="detail-box">
          <div style="color:#d4af37;font-weight:bold">${s.name} <span style="color:#8a7a9a;font-weight:normal;font-size:11px">${s.type}</span></div>
          <div style="color:#a8a8c8;font-size:12px;margin:4px 0">${s.description}</div>
        </div>`;
      }
    }
    this.openModal('宗门', html);
  },

  // ==================== 重置 ====================
  confirmReset() {
    const html = `<div class="detail-box" style="border-color:#c83232"><div style="color:#ff6b6b;font-size:14px;margin-bottom:8px">⚠ 警告</div><div style="color:#a8a8c8;font-size:13px">这将清除所有游戏进度，重新开始。此操作不可撤销！</div></div>
    <div style="text-align:center;margin-top:12px"><button class="btn danger" onclick="UI.doReset()">确认重置</button><button class="btn" onclick="UI.closeModal()">取消</button></div>`;
    this.openModal('重置游戏', html);
  },

  async doReset() {
    const r = await API.reset();
    this.closeModal();
    this.toast(r.msg, 'success');
    await this.refresh();
  }
};

const ATTR_NAMES = {
  'wood_affinity': '木属性亲和', 'fire_affinity': '火属性亲和', 'ice_affinity': '冰属性亲和',
  'metal_affinity': '金属性亲和', 'earth_affinity': '土属性亲和', 'wind_affinity': '风属性亲和',
  'thunder_affinity': '雷属性亲和', 'light_affinity': '光属性亲和', 'dark_affinity': '暗属性亲和',
  'void_affinity': '虚空属性亲和', 'water_affinity': '水属性亲和', 'soul_affinity': '神魂属性亲和',
  'spiritual_energy': '灵气', 'meridian_strain': '经脉损伤', 'fire_poison': '火毒', 'cold_damage': '寒气'
};

const TECHNIQUE_DATA = {
  "wood_basic": {"name": "青木诀", "element": "木", "completeness": 0.7, "desc": "木属性基础功法，温和平稳。"},
  "fire_basic": {"name": "焚天诀", "element": "火", "completeness": 0.65, "desc": "火属性功法，霸道凌厉。"},
  "ice_basic": {"name": "冰魄诀", "element": "冰", "completeness": 0.75, "desc": "冰属性功法，阴寒凝练。"},
  "metal_basic": {"name": "庚金诀", "element": "金", "completeness": 0.72, "desc": "金属性功法，锋锐凌厉。"},
  "earth_basic": {"name": "厚土诀", "element": "土", "completeness": 0.78, "desc": "土属性功法，厚重绵长。"}
};

const SECT_DATA = {
  "qingyun_sect_info": {"name": "青云宗", "type": "正道", "description": "正道大宗，传承千年。"},
  "dan_dao_zong": {"name": "丹道宗", "type": "正道", "description": "专精炼丹的宗门。"},
  "qi_zong": {"name": "器宗", "type": "正道", "description": "专精炼器的宗门。"},
  "wan_yao_men": {"name": "万兽门", "type": "中立", "description": "专精御兽的宗门。"},
  "jian_ge": {"name": "剑阁", "type": "正道", "description": "剑修圣地。"},
  "fu_zong": {"name": "符箓宗", "type": "正道", "description": "专精符箓。"},
  "zhen_fa_men": {"name": "阵法门", "type": "正道", "description": "专精阵法。"}
};
