// 逆仙录·天道残卷 - 天劫系统
const Tribulation = {
  active: false, busy: false,
  tribData: null, currentRound: 0, rounds: 0,

  start(trib) {
    this.active = true;
    this.busy = false;
    this.tribData = trib;
    this.currentRound = 1;
    this.rounds = trib.rounds;
    document.getElementById('tribulation-overlay').style.display = 'flex';
    document.getElementById('trib-title').textContent = trib.name;
    document.getElementById('trib-desc').textContent = trib.desc;
    document.getElementById('trib-log').innerHTML = '';
    this.updateUI();
    this.log(`★ ${trib.name}降临！共${trib.rounds}道天劫，每道造成${trib.damage}点伤害！`);
    this.log('选择硬抗、闪避或使用护身符应对！');
  },

  updateUI() {
    const p = UI.state.player;
    if (!p) return;
    const hpPct = (p.hp / p.max_hp * 100);
    document.getElementById('trib-hp-bar').style.width = hpPct + '%';
    document.getElementById('trib-hp-text').textContent = `${p.hp}/${p.max_hp}`;
    document.getElementById('trib-round-info').innerHTML = `<div style="color:#d4af37;font-size:16px;text-align:center">第 ${this.currentRound} / ${this.rounds} 道天劫</div>`;
  },

  log(msg) {
    const el = document.getElementById('trib-log');
    const div = document.createElement('div');
    div.style.cssText = 'padding:4px 0;border-bottom:1px solid #333;';
    div.textContent = msg;
    el.appendChild(div);
    el.scrollTop = el.scrollHeight;
  },

  async round(action) {
    if (this.busy) return;
    this.busy = true;
    const r = await API.tribulationRound(action, null);
    this.busy = false;
    if (!r) return;
    if (r.msg) this.log(r.msg);
    if (r.action === 'tribulation') {
      this.currentRound = r.current_round;
      await UI.refresh();
      this.updateUI();
    } else if (r.breakthrough) {
      this.log('★ ' + r.msg);
      UI.toast(r.msg, 'success');
      setTimeout(() => this.end(), 2000);
    } else if (r.action === 'death') {
      this.log('★ ' + r.msg);
      setTimeout(() => { this.end(); Death.show(r); }, 1500);
    }
  },

  async useItem() {
    if (this.busy) return;
    // 简化：使用护身符
    const p = UI.state.player;
    const shield = p.inventory.find(i => i.item_id === 'talisman_shield');
    if (!shield) {
      this.log('无护身符可用！');
      return;
    }
    this.busy = true;
    const r = await API.tribulationRound('item', 'talisman_shield');
    this.busy = false;
    if (r && r.msg) this.log(r.msg);
    if (r && r.action === 'tribulation') {
      this.currentRound = r.current_round;
      await UI.refresh();
      this.updateUI();
    }
  },

  end() {
    this.active = false;
    this.busy = false;
    document.getElementById('tribulation-overlay').style.display = 'none';
    UI.refresh();
  }
};

// 死亡转世系统
const Death = {
  show(data) {
    document.getElementById('death-overlay').style.display = 'flex';
    const optionsHtml = data.options.map(o => `
      <div class="detail-box" style="cursor:pointer;margin:8px 0" onclick="Death.choose('${o.id}')">
        <div style="color:#d4af37;font-weight:bold;font-size:15px">${o.name}</div>
        <div style="color:#a8a8c8;font-size:12px;margin-top:4px">${o.desc}</div>
        <div style="color:${o.risk === 'high' ? '#ff6b6b' : (o.risk === 'medium' ? '#ffaa6b' : '#6bc832')};font-size:11px;margin-top:4px">风险等级：${o.risk === 'high' ? '高' : (o.risk === 'medium' ? '中' : '低')}</div>
      </div>
    `).join('');
    document.getElementById('death-options').innerHTML = optionsHtml;
  },

  async choose(choice) {
    const r = await API.chooseReincarnation(choice);
    if (r.ok) {
      UI.toast(r.msg, 'success');
      document.getElementById('death-overlay').style.display = 'none';
      await UI.refresh();
    } else {
      UI.toast(r.msg, 'error');
      if (r.game_over) {
        document.getElementById('death-overlay').style.display = 'none';
        setTimeout(() => { if (confirm('游戏结束，是否重置？')) UI.doReset(); }, 500);
      }
    }
  }
};
