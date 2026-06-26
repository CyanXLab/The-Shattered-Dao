// 逆仙录·天道残卷 - 战斗系统
const Combat = {
  active: false, beastHp: 0, beastMaxHp: 0, beastName: '',
  playerHp: 0, playerMaxHp: 0, playerQi: 0, playerMaxQi: 0, busy: false,

  startFromState(state) {
    if (!state.player.in_combat) return;
    this.active = true;
    document.getElementById('combat-overlay').style.display = 'flex';
    document.getElementById('combat-log').innerHTML = '';
    this.playerHp = state.player.hp;
    this.playerMaxHp = state.player.max_hp;
    this.playerQi = state.player.qi;
    this.playerMaxQi = state.player.max_qi;
    this.updateBars();
    document.getElementById('combat-options').style.display = 'block';
    document.getElementById('combat-qi-allocation').oninput = (e) => {
      document.getElementById('combat-qi-val').textContent = e.target.value + '%';
    };
    this.log('战斗开始！');
  },

  updateBars() {
    document.getElementById('combat-player-hp').style.width = (this.playerHp / this.playerMaxHp * 100) + '%';
    document.getElementById('combat-player-hp-text').textContent = `${this.playerHp}/${this.playerMaxHp}`;
    document.getElementById('combat-player-qi').style.width = (this.playerMaxQi > 0 ? this.playerQi / this.playerMaxQi * 100 : 0) + '%';
    document.getElementById('combat-player-qi-text').textContent = `${this.playerQi}/${this.playerMaxQi}`;
    if (this.beastMaxHp > 0) {
      document.getElementById('combat-beast-hp').style.width = (this.beastHp / this.beastMaxHp * 100) + '%';
      document.getElementById('combat-beast-hp-text').textContent = `${this.beastHp}/${this.beastMaxHp}`;
    }
  },

  log(msg) {
    const el = document.getElementById('combat-log');
    const div = document.createElement('div');
    div.style.cssText = 'padding:4px 0;border-bottom:1px solid #2a1a1a;';
    div.textContent = msg;
    el.appendChild(div);
    el.scrollTop = el.scrollHeight;
  },

  getCombatOptions() {
    return {
      target_part: document.getElementById('combat-target-part').value,
      qi_allocation: parseInt(document.getElementById('combat-qi-allocation').value) / 100
    };
  },

  async attack() {
    if (this.busy) return;
    this.busy = true;
    const opts = this.getCombatOptions();
    const r = await API.combatAction('attack', 0, opts.target_part, opts.qi_allocation);
    this.handleResult(r);
  },

  async openSkills() {
    const state = UI.state;
    if (!state || !state.player.active_technique) {
      this.log('未激活功法，无法施展神通！');
      this.busy = false;
      return;
    }
    const tech = state.player.techniques.find(t => t.id === state.player.active_technique);
    if (!tech) { this.busy = false; return; }
    const skillsDiv = document.getElementById('combat-skills');
    const itemsDiv = document.getElementById('combat-items');
    itemsDiv.style.display = 'none';
    if (skillsDiv.style.display === 'none') {
      skillsDiv.style.display = 'grid';
      skillsDiv.innerHTML = '';
      for (let i = 0; i < tech.combat_skills.length; i++) {
        const sk = tech.combat_skills[i];
        const canUse = REALM_ORDER.indexOf(state.player.realm) >= REALM_ORDER.indexOf(sk.unlock);
        const enoughQi = state.player.qi >= sk.cost;
        const btn = document.createElement('button');
        btn.className = 'skill-btn';
        btn.disabled = !canUse || !enoughQi;
        const label = sk.label || sk.name;
        btn.innerHTML = `${label}<span class="skill-cost">${sk.cost}气</span><div style="font-size:10px;color:#8a7a9a">${canUse ? '' : '需' + (REALM_NAMES[sk.unlock] || sk.unlock)}</div>`;
        btn.onclick = () => this.useSkill(i);
        skillsDiv.appendChild(btn);
      }
    } else {
      skillsDiv.style.display = 'none';
    }
    this.busy = false;
  },

  async useSkill(idx) {
    if (this.busy) return;
    this.busy = true;
    document.getElementById('combat-skills').style.display = 'none';
    const opts = this.getCombatOptions();
    const r = await API.combatAction('skill', idx, opts.target_part, opts.qi_allocation);
    this.handleResult(r);
  },

  async openItems() {
    const state = UI.state;
    const skillsDiv = document.getElementById('combat-skills');
    const itemsDiv = document.getElementById('combat-items');
    skillsDiv.style.display = 'none';
    if (itemsDiv.style.display === 'none') {
      itemsDiv.style.display = 'grid';
      itemsDiv.innerHTML = '';
      const usable = state.player.inventory.filter(inv => ['pill', 'talisman'].includes(inv.type));
      if (usable.length === 0) {
        itemsDiv.innerHTML = '<div style="grid-column:1/3;color:#8a7a9a;text-align:center;padding:8px">无可使用物品</div>';
      }
      for (const inv of usable) {
        const btn = document.createElement('button');
        btn.className = 'item-btn';
        btn.innerHTML = `${inv.name} ×${inv.qty}`;
        btn.onclick = () => this.useItem(inv.item_id);
        itemsDiv.appendChild(btn);
      }
    } else {
      itemsDiv.style.display = 'none';
    }
    this.busy = false;
  },

  async useItem(itemId) {
    if (this.busy) return;
    this.busy = true;
    document.getElementById('combat-items').style.display = 'none';
    const r = await API.useItemCombat(itemId);
    this.handleResult(r);
  },

  async flee() {
    if (this.busy) return;
    this.busy = true;
    const r = await API.combatAction('flee', 0, 'body', 0.5);
    this.handleResult(r);
  },

  async handleResult(r) {
    this.busy = false;
    if (!r) return;
    if (r.msg) {
      const lines = r.msg.split('\n');
      for (const line of lines) if (line.trim()) this.log(line);
    }
    if (r.action === 'combat' && r.player) {
      this.playerHp = r.player.hp;
      this.playerMaxHp = r.player.max_hp;
      this.playerQi = r.player.qi;
      this.playerMaxQi = r.player.max_qi;
      this.beastHp = r.beast.hp;
      this.beastMaxHp = r.beast.max_hp;
      this.beastName = r.beast.name;
      document.getElementById('combat-beast-name').textContent = r.beast.name;
      this.updateBars();
    } else if (r.action === 'victory') {
      this.log('★ ' + r.msg);
      setTimeout(() => this.end(), 1500);
    } else if (r.action === 'flee') {
      this.log('成功逃脱！');
      setTimeout(() => this.end(), 1000);
    } else if (!r.ok && r.msg && r.msg.includes('战败')) {
      this.log('💀 ' + r.msg);
      setTimeout(() => this.end(), 2000);
    }
    await UI.refresh();
  },

  end() {
    this.active = false;
    this.busy = false;
    document.getElementById('combat-overlay').style.display = 'none';
    document.getElementById('combat-skills').style.display = 'none';
    document.getElementById('combat-items').style.display = 'none';
    document.getElementById('combat-options').style.display = 'none';
    this.beastHp = 0;
    this.beastMaxHp = 0;
  }
};

const REALM_ORDER = [
  'qi_refining_1','qi_refining_2','qi_refining_3','qi_refining_4','qi_refining_5','qi_refining_6','qi_refining_7','qi_refining_8','qi_refining_9',
  'foundation_1','foundation_3','foundation_5','foundation_7',
  'golden_core_1','golden_core_3','golden_core_5','golden_core_9',
  'nascent_soul_1','nascent_soul_3','nascent_soul_5',
  'divine_transformation_1','divine_transformation_3','divine_transformation_5',
  'void_refining_1','void_refining_3','void_refining_5',
  'body_integration_1','body_integration_3','body_integration_5',
  'mahayana_1','mahayana_3','mahayana_5',
  'tribulation_1','tribulation_3','tribulation_5'
];
const REALM_NAMES = {
  'qi_refining_1': '练气一层','qi_refining_2': '练气二层','qi_refining_3': '练气三层','qi_refining_4': '练气四层',
  'qi_refining_5': '练气五层','qi_refining_6': '练气六层','qi_refining_7': '练气七层','qi_refining_8': '练气八层','qi_refining_9': '练气九层',
  'foundation_1': '筑基初期','foundation_3': '筑基中期','foundation_5': '筑基后期','foundation_7': '筑基大圆满',
  'golden_core_1': '金丹初期','golden_core_3': '金丹中期','golden_core_5': '金丹后期','golden_core_9': '金丹大圆满',
  'nascent_soul_1': '元婴初期','nascent_soul_3': '元婴中期','nascent_soul_5': '元婴后期',
  'divine_transformation_1': '化神初期','divine_transformation_3': '化神中期','divine_transformation_5': '化神后期',
  'void_refining_1': '炼虚初期','void_refining_3': '炼虚中期','void_refining_5': '炼虚后期',
  'body_integration_1': '合体初期','body_integration_3': '合体中期','body_integration_5': '合体后期',
  'mahayana_1': '大乘初期','mahayana_3': '大乘中期','mahayana_5': '大乘后期',
  'tribulation_1': '渡劫初期','tribulation_3': '渡劫中期','tribulation_5': '渡劫后期'
};
