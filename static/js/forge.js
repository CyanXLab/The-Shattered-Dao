// 逆仙录·天道残卷 - 炼器系统（锻造小游戏）
const Forge = {
  selectedRecipe: null, selectedMaterials: {},
  canvas: null, ctx: null,
  smeltingTemp: 200, targetSmelting: 600,
  hammering: 0, targetHammering: 18,
  quenchingTime: 0, targetQuenching: 10,
  running: false, timer: null,
  hammerAnim: 0, firePower: 50,

  async open() {
    const recipes = await API.forgeRecipes();
    let html = `
      <div class="detail-box">
        <div style="color:#d4af37;margin-bottom:6px">炼器房</div>
        <div style="color:#8a7a9a;font-size:12px">锻造之法，在于熔炼、锤击、淬火三步。控制火候与力度，方能铸就神兵。</div>
      </div>
      <div class="section-title">选择器方</div>
    `;
    for (const r of recipes) {
      const m = MATERIAL_NAMES[r.output];
      html += `<div class="item-row" style="cursor:pointer" onclick="Forge.selectRecipe('${r.id}')">
        <div><span class="item-name">${m || r.name}</span><span class="item-tier tier-${r.tier}">${r.tier}阶</span></div>
        <div><button class="btn gold">选择</button></div>
      </div>`;
    }
    UI.openModal('炼器房', html);
  },

  async selectRecipe(fid) {
    const recipes = await API.forgeRecipes();
    this.selectedRecipe = recipes.find(r => r.id === fid);
    if (!this.selectedRecipe) return;
    this.selectedMaterials = {};
    this.renderMaterialSelect();
  },

  renderMaterialSelect() {
    const r = this.selectedRecipe;
    const p = UI.state.player;
    const proc = r.process;
    let html = `
      <div class="detail-box">
        <div style="color:#d4af37">${r.name}（${r.tier}阶）</div>
        <div style="color:#8a7a9a;font-size:11px;margin-top:4px">
          熔炼：${proc.smelting.min}-${proc.smelting.max}（最佳${proc.smelting.optimal}） |
          锤击：${proc.hammering.min}-${proc.hammering.max}（最佳${proc.hammering.optimal}） |
          淬火：${proc.quenching.duration.min}-${proc.quenching.duration.max}（最佳${proc.quenching.duration.optimal}）
        </div>
        <div style="color:#8a7a9a;font-size:11px;margin-top:4px">${r.desc}</div>
      </div>
    `;
    for (const [slot, req] of Object.entries(r.inputs)) {
      const slotNames = {core:'核心材料', edge:'刃材', handle:'柄材', inscription:'铭文材', lining:'内衬', poison:'毒材'};
      html += `<div class="section-title">${slotNames[slot] || slot}</div>`;
      const inv = p.inventory.filter(i => {
        if (i.item_id === 'reverse_jade') return false;
        const m = MATERIAL_DATA[i.item_id];
        if (!m) return false;
        if (req.type && m.type !== req.type) return false;
        if (req.min_tier && m.tier < req.min_tier) return false;
        if (req.id && m.id !== req.id) return false;
        return true;
      });
      if (inv.length === 0) html += '<div class="detail-box" style="color:#ff6b6b">无符合条件材料</div>';
      for (const i of inv) {
        const sel = this.selectedMaterials[slot] === i.item_id;
        html += `<div class="item-row" style="cursor:pointer;border-color:${sel ? '#d4af37' : ''}" onclick="Forge.selectMaterial('${slot}','${i.item_id}')">
          <div><span class="item-name">${i.name}</span><span class="item-tier tier-${i.tier}">${i.tier}阶</span><span class="item-qty">×${i.qty}</span></div>
          <div>${sel ? '<span style="color:#d4af37">✓</span>' : '<button class="btn">选择</button>'}</div>
        </div>`;
      }
    }
    const canStart = Object.keys(r.inputs).every(s => this.selectedMaterials[s]);
    html += `<div style="text-align:center;margin-top:12px"><button class="btn gold" ${canStart ? '' : 'disabled'} onclick="Forge.startMinigame()">开始锻造</button></div>`;
    UI.setModalBody(html);
  },

  selectMaterial(slot, id) { this.selectedMaterials[slot] = id; this.renderMaterialSelect(); },

  startMinigame() {
    const r = this.selectedRecipe;
    const proc = r.process;
    this.smeltingTemp = 200;
    this.targetSmelting = proc.smelting.optimal;
    this.hammering = 0;
    this.targetHammering = proc.hammering.optimal;
    this.quenchingTime = 0;
    this.targetQuenching = proc.quenching.duration.optimal;
    this.firePower = 50;
    this.running = false;
    this.phase = 'smelting';  // smelting -> hammering -> quenching
    const html = `
      <div class="alchemy-layout">
        <div class="alchemy-section">
          <div style="color:#d4af37;font-size:13px;margin-bottom:6px">锻造台</div>
          <div class="alchemy-canvas-wrap">
            <canvas id="forge-canvas" width="280" height="280"></canvas>
          </div>
          <div style="font-size:11px;color:#8a7a9a;text-align:center" id="forge-phase">阶段：熔炼中</div>
        </div>
        <div class="alchemy-section">
          <div style="color:#d4af37;font-size:13px;margin-bottom:6px">控制</div>
          <div class="alchemy-controls">
            <div class="alchemy-slider-wrap" id="fire-control">
              <span style="width:60px;color:#8a7a9a">火力</span>
              <input type="range" id="forge-fire-slider" min="0" max="100" value="50">
              <span id="forge-fire-val" style="width:40px;color:#ff6b6b">50</span>
            </div>
            <div class="detail-box" style="font-size:12px;padding:8px">
              <div class="attr-row"><span class="attr-name">温度</span><span class="attr-value" id="forge-temp-val">200</span></div>
              <div class="attr-row"><span class="attr-name">目标</span><span class="attr-value">${this.targetSmelting}</span></div>
              <div class="attr-row"><span class="attr-name">锤击</span><span class="attr-value" id="forge-hammer-val">0/${this.targetHammering}</span></div>
              <div class="attr-row"><span class="attr-name">淬火</span><span class="attr-value" id="forge-quench-val">0/${this.targetQuenching}</span></div>
            </div>
            <button class="btn gold" id="forge-start-btn" onclick="Forge.toggleRun()">${this.running ? '暂停' : '开始熔炼'}</button>
            <button class="btn" id="forge-hammer-btn" style="display:none" onclick="Forge.hammer()">锤击！</button>
            <button class="btn gold" id="forge-quench-btn" style="display:none" onclick="Forge.startQuench()">开始淬火</button>
            <button class="btn gold" onclick="Forge.finishForge()">完成锻造</button>
          </div>
        </div>
      </div>
    `;
    UI.setModalBody(html);
    this.canvas = document.getElementById('forge-canvas');
    this.ctx = this.canvas.getContext('2d');
    const slider = document.getElementById('forge-fire-slider');
    if (slider) {
      slider.oninput = (e) => {
        this.firePower = parseInt(e.target.value);
        document.getElementById('forge-fire-val').textContent = this.firePower;
      };
    }
    this.renderMinigame();
  },

  toggleRun() {
    this.running = !this.running;
    const btn = document.getElementById('forge-start-btn');
    if (btn) btn.textContent = this.running ? '暂停' : '开始熔炼';
    if (this.running) this.loop();
  },

  loop() {
    if (!this.running) return;
    if (this.phase === 'smelting') {
      const target = this.firePower * 15;
      this.smeltingTemp += (target - this.smeltingTemp) * 0.05;
      document.getElementById('forge-temp-val').textContent = Math.round(this.smeltingTemp);
    } else if (this.phase === 'quenching') {
      this.quenchingTime += 0.1;
      this.smeltingTemp = Math.max(20, this.smeltingTemp * 0.97);
      document.getElementById('forge-quench-val').textContent = `${Math.round(this.quenchingTime)}/${this.targetQuenching}`;
      document.getElementById('forge-temp-val').textContent = Math.round(this.smeltingTemp);
    }
    this.renderMinigame();
    this.timer = setTimeout(() => this.loop(), 100);
  },

  hammer() {
    if (this.phase !== 'hammering') return;
    this.hammering++;
    this.hammerAnim = 1.0;
    document.getElementById('forge-hammer-val').textContent = `${this.hammering}/${this.targetHammering}`;
    if (this.hammering >= this.targetHammering * 1.5) {
      this.phase = 'quenching';
      document.getElementById('forge-phase').textContent = '阶段：淬火中';
      document.getElementById('forge-hammer-btn').style.display = 'none';
      document.getElementById('forge-quench-btn').style.display = 'block';
      this.running = true;
      this.loop();
    }
  },

  startQuench() {
    this.running = false;
    if (this.timer) clearTimeout(this.timer);
    this.finishForge();
  },

  finishForge() {
    if (this.running) {
      this.running = false;
      if (this.timer) clearTimeout(this.timer);
    }
    const process = {
      smelting: Math.round(this.smeltingTemp),
      hammering: this.hammering,
      quenching_duration: Math.round(this.quenchingTime)
    };
    const materials = {...this.selectedMaterials};
    API.forgeCraft(this.selectedRecipe.id, materials, process).then(r => {
      UI.refresh();
      let color = '#ff6b6b';
      if (r.quality >= 4) color = '#ffd700';
      else if (r.quality >= 3) color = '#d4af37';
      else if (r.quality >= 2) color = '#a8a8c8';
      else if (r.quality >= 1) color = '#9ad96b';
      const html = `
        <div class="alchemy-result" style="color:${color}">
          <div style="font-size:24px;margin-bottom:8px">${r.quality_name}</div>
          <div style="font-size:14px;color:#e8e0c8">${r.msg}</div>
        </div>
        <div style="text-align:center;margin-top:12px">
          <button class="btn gold" onclick="Forge.open()">再次锻造</button>
          <button class="btn" onclick="UI.closeModal()">关闭</button>
        </div>
      `;
      UI.setModalBody(html);
      UI.toast(r.msg, r.ok ? 'success' : 'error');
    });
  },

  renderMinigame() {
    if (!this.ctx) return;
    const w = this.canvas.width, h = this.canvas.height;
    this.ctx.clearRect(0, 0, w, h);
    this.ctx.fillStyle = '#0a0505';
    this.ctx.fillRect(0, 0, w, h);
    const cx = w / 2, cy = h / 2 + 20;
    // 锻造台
    this.ctx.fillStyle = '#2a1a0a';
    this.ctx.fillRect(cx - 100, cy + 40, 200, 20);
    // 火焰
    if (this.smeltingTemp > 100) {
      const fireColor = this.smeltingTemp > 1000 ? '#ff0000' : (this.smeltingTemp > 600 ? '#ff6b00' : '#ffaa00');
      this.ctx.fillStyle = fireColor;
      for (let i = 0; i < 6; i++) {
        const fx = cx - 50 + i * 20;
        const fy = cy + 30;
        const flameH = 15 + Math.sin(Date.now() / 80 + i) * 8 + (this.firePower / 100) * 25;
        this.ctx.beginPath();
        this.ctx.moveTo(fx, fy);
        this.ctx.quadraticCurveTo(fx - 6, fy - flameH / 2, fx, fy - flameH);
        this.ctx.quadraticCurveTo(fx + 6, fy - flameH / 2, fx, fy);
        this.ctx.fill();
      }
    }
    // 金属块
    const metalColor = this.smeltingTemp > 800 ? '#ff6b00' : (this.smeltingTemp > 500 ? '#ffaa00' : '#5a3a1a');
    this.ctx.fillStyle = metalColor;
    this.ctx.fillRect(cx - 40, cy - 10, 80, 40);
    this.ctx.strokeStyle = '#3a2a1a';
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(cx - 40, cy - 10, 80, 40);
    // 锤击动画
    if (this.hammerAnim > 0) {
      this.ctx.fillStyle = `rgba(200,200,200,${this.hammerAnim})`;
      this.ctx.fillRect(cx - 30, cy - 60 - this.hammerAnim * 30, 60, 30);
      this.ctx.strokeStyle = '#fff';
      this.ctx.strokeRect(cx - 30, cy - 60 - this.hammerAnim * 30, 60, 30);
      this.hammerAnim *= 0.85;
      if (this.hammerAnim < 0.05) this.hammerAnim = 0;
    }
    // 温度计
    const tx = 20, ty = 20, tw = 16, th = 240;
    this.ctx.fillStyle = '#1a1525';
    this.ctx.fillRect(tx, ty, tw, th);
    const tempPct = Math.max(0, Math.min(1, this.smeltingTemp / 1500));
    this.ctx.fillStyle = this.smeltingTemp > 1000 ? '#ff0000' : (this.smeltingTemp > 600 ? '#ff6b00' : '#ffaa00');
    this.ctx.fillRect(tx, ty + th - th * tempPct, tw, th * tempPct);
    const tgtY = ty + th - th * (this.targetSmelting / 1500);
    this.ctx.strokeStyle = '#d4af37';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.moveTo(tx - 4, tgtY);
    this.ctx.lineTo(tx + tw + 4, tgtY);
    this.ctx.stroke();
    // 锤击计数
    if (this.phase === 'hammering' || this.hammering > 0) {
      this.ctx.fillStyle = '#d4af37';
      this.ctx.font = '14px sans-serif';
      this.ctx.textAlign = 'right';
      this.ctx.fillText(`锤击: ${this.hammering}/${this.targetHammering}`, w - 20, 30);
    }
  }
};

const MATERIAL_NAMES = {
  iron_sword: '铁剑', spirit_sword: '灵纹剑', fire_sword: '赤焰剑', ice_sword: '寒冰剑',
  thunder_sword: '雷霆剑', wind_sword: '风行剑', dragon_sword: '青龙剑', phoenix_sword: '朱雀剑',
  immortal_sword: '仙剑·诛仙', demon_sword: '魔剑·血煞', wood_sword: '青木剑', earth_sword: '厚土剑',
  metal_sword: '庚金剑', void_sword: '虚空剑', light_sword: '光明剑', dark_sword: '暗影剑',
  poison_sword: '碧毒剑', soul_sword: '诛魂剑', bone_sword: '白骨剑', crystal_sword: '水晶剑',
  cloth_armor: '布衣', leather_armor: '皮甲', spirit_armor: '灵纹甲', fire_armor: '赤焰甲',
  ice_armor: '寒冰甲', thunder_armor: '雷霆甲', dragon_armor: '青龙甲', phoenix_armor: '朱雀甲',
  black_turtle_armor: '玄武甲', demon_armor: '血煞甲', wood_armor: '青木甲', earth_armor: '厚土甲',
  metal_armor: '庚金甲', light_armor: '光明甲', spirit_robe: '道袍'
};

const MATERIAL_DATA = {};  // 由ui.js填充
