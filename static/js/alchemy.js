// 逆仙录·天道残卷 - 炼丹系统（含温度控制小游戏）
const Alchemy = {
  selectedRecipe: null, selectedMain: null, selectedAux: [], selectedCatalyst: null,
  canvas: null, ctx: null,
  temp: 200, targetTemp: 500, tempMin: 0, tempMax: 1000,
  duration: 0, targetDuration: 200, stirring: 0, targetStirring: 3,
  running: false, timer: null, startTime: 0, firePower: 50, stirAnim: 0,

  async open() {
    const recipes = await API.alchemyRecipes();
    let html = `
      <div class="detail-box">
        <div style="color:#d4af37;margin-bottom:6px">炼丹房</div>
        <div style="color:#8a7a9a;font-size:12px">炼丹之道在于火候。控制温度、时间、搅拌，炼出极品丹药。</div>
        <div style="color:#8a7a9a;font-size:12px;margin-top:4px">品质：废丹 → 下品 → 中品 → 上品 → 极品 → 完美</div>
      </div>
      <div class="section-title">第一步：选择丹方</div>
    `;
    for (const r of recipes) {
      html += `<div class="item-row" style="cursor:pointer" onclick="Alchemy.selectRecipe('${r.id}')">
        <div>
          <span class="item-name">${r.name}</span>
          <span class="item-tier tier-${r.tier}">${r.tier}阶</span>
        </div>
        <div><button class="btn gold">选择</button></div>
      </div>`;
    }
    UI.openModal('炼丹房', html);
  },

  async selectRecipe(rid) {
    const recipes = await API.alchemyRecipes();
    this.selectedRecipe = recipes.find(r => r.id === rid);
    if (!this.selectedRecipe) return;
    this.selectedMain = null;
    this.selectedAux = [];
    this.selectedCatalyst = null;
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
          温度：${proc.temperature.min}-${proc.temperature.max}（最佳${proc.temperature.optimal}） |
          时长：${proc.duration.min}-${proc.duration.max}（最佳${proc.duration.optimal}） |
          搅拌：${proc.stirring.min}-${proc.stirring.max}（最佳${proc.stirring.optimal}）
        </div>
      </div>
    `;
    html += '<div class="section-title">主药</div>';
    const mainInv = p.inventory.filter(inv => inv.type === r.inputs.main.type && inv.tier >= (r.inputs.main.min_tier || 1));
    if (mainInv.length === 0) html += '<div class="detail-box" style="color:#ff6b6b">无符合条件的主药</div>';
    for (const inv of mainInv) {
      const sel = this.selectedMain === inv.item_id;
      html += `<div class="item-row" style="cursor:pointer;border-color:${sel ? '#d4af37' : ''}" onclick="Alchemy.selectMain('${inv.item_id}')">
        <div><span class="item-name">${inv.name}</span><span class="item-tier tier-${inv.tier}">${inv.tier}阶</span><span class="item-qty">×${inv.qty}</span></div>
        <div>${sel ? '<span style="color:#d4af37">✓</span>' : '<button class="btn">选择</button>'}</div>
      </div>`;
    }
    if (r.inputs.auxiliary) {
      html += '<div class="section-title">辅药（可多选）</div>';
      const auxReq = r.inputs.auxiliary;
      const auxInv = p.inventory.filter(inv => inv.type === auxReq.type && inv.tier >= (auxReq.min_tier || 1));
      for (const inv of auxInv) {
        const sel = this.selectedAux.includes(inv.item_id);
        html += `<div class="item-row" style="cursor:pointer;border-color:${sel ? '#d4af37' : ''}" onclick="Alchemy.toggleAux('${inv.item_id}')">
          <div><span class="item-name">${inv.name}</span><span class="item-tier tier-${inv.tier}">${inv.tier}阶</span><span class="item-qty">×${inv.qty}</span></div>
          <div>${sel ? '<span style="color:#d4af37">✓</span>' : '<button class="btn">添加</button>'}</div>
        </div>`;
      }
    }
    if (r.inputs.catalyst) {
      html += '<div class="section-title">催化剂（妖丹）</div>';
      const catReq = r.inputs.catalyst;
      const catInv = p.inventory.filter(inv => inv.type === catReq.type && inv.tier >= (catReq.min_tier || 1));
      if (catInv.length === 0) html += '<div class="detail-box" style="color:#ff6b6b">无符合条件的催化剂</div>';
      for (const inv of catInv) {
        const sel = this.selectedCatalyst === inv.item_id;
        html += `<div class="item-row" style="cursor:pointer;border-color:${sel ? '#d4af37' : ''}" onclick="Alchemy.selectCatalyst('${inv.item_id}')">
          <div><span class="item-name">${inv.name}</span><span class="item-tier tier-${inv.tier}">${inv.tier}阶</span><span class="item-qty">×${inv.qty}</span></div>
          <div>${sel ? '<span style="color:#d4af37">✓</span>' : '<button class="btn">选择</button>'}</div>
        </div>`;
      }
    }
    const canStart = this.selectedMain && (!r.inputs.auxiliary || this.selectedAux.length >= (r.inputs.auxiliary.count || 0)) && (!r.inputs.catalyst || this.selectedCatalyst);
    html += `<div style="text-align:center;margin-top:12px">
      <button class="btn gold" ${canStart ? '' : 'disabled'} onclick="Alchemy.startMinigame()">开始炼丹</button>
    </div>`;
    UI.setModalBody(html);
  },

  selectMain(id) { this.selectedMain = id; this.renderMaterialSelect(); },
  toggleAux(id) {
    const idx = this.selectedAux.indexOf(id);
    if (idx >= 0) this.selectedAux.splice(idx, 1);
    else this.selectedAux.push(id);
    this.renderMaterialSelect();
  },
  selectCatalyst(id) { this.selectedCatalyst = id; this.renderMaterialSelect(); },

  startMinigame() {
    const r = this.selectedRecipe;
    const proc = r.process;
    this.temp = 200; this.targetTemp = proc.temperature.optimal;
    this.tempMin = proc.temperature.min; this.tempMax = proc.temperature.max;
    this.duration = 0; this.targetDuration = proc.duration.optimal;
    this.stirring = 0; this.targetStirring = proc.stirring.optimal;
    this.firePower = 50; this.running = false;
    const html = `
      <div class="alchemy-layout">
        <div class="alchemy-section">
          <div style="color:#d4af37;font-size:13px;margin-bottom:6px">丹炉</div>
          <div class="alchemy-canvas-wrap">
            <canvas id="alchemy-canvas" width="280" height="280"></canvas>
          </div>
          <div style="font-size:11px;color:#8a7a9a;text-align:center">点击丹炉搅拌（最佳${this.targetStirring}次）</div>
        </div>
        <div class="alchemy-section">
          <div style="color:#d4af37;font-size:13px;margin-bottom:6px">控制</div>
          <div class="alchemy-controls">
            <div class="alchemy-slider-wrap">
              <span style="width:60px;color:#8a7a9a">火力</span>
              <input type="range" id="fire-slider" min="0" max="100" value="50">
              <span id="fire-val" style="width:40px;color:#ff6b6b">50</span>
            </div>
            <div class="detail-box" style="font-size:12px;padding:8px">
              <div class="attr-row"><span class="attr-name">温度</span><span class="attr-value" id="temp-val">200</span></div>
              <div class="attr-row"><span class="attr-name">目标</span><span class="attr-value">${this.targetTemp}</span></div>
              <div class="attr-row"><span class="attr-name">范围</span><span class="attr-value">${this.tempMin}-${this.tempMax}</span></div>
              <div class="attr-row"><span class="attr-name">时长</span><span class="attr-value" id="dur-val">0/${this.targetDuration}</span></div>
              <div class="attr-row"><span class="attr-name">搅拌</span><span class="attr-value" id="stir-val">0/${this.targetStirring}</span></div>
            </div>
            <button class="btn gold" id="start-btn" onclick="Alchemy.toggleRun()">${this.running ? '暂停' : '开始'}</button>
            <button class="btn gold" onclick="Alchemy.finishCraft()">收丹</button>
          </div>
        </div>
      </div>
    `;
    UI.setModalBody(html);
    this.canvas = document.getElementById('alchemy-canvas');
    this.ctx = this.canvas.getContext('2d');
    document.getElementById('fire-slider').oninput = (e) => {
      this.firePower = parseInt(e.target.value);
      document.getElementById('fire-val').textContent = this.firePower;
    };
    this.canvas.onclick = () => {
      this.stirring++;
      document.getElementById('stir-val').textContent = `${this.stirring}/${this.targetStirring}`;
      this.stirAnim = 1.0;
    };
    this.renderMinigame();
  },

  toggleRun() {
    this.running = !this.running;
    document.getElementById('start-btn').textContent = this.running ? '暂停' : '开始';
    if (this.running) {
      this.startTime = Date.now();
      this.loop();
    }
  },

  loop() {
    if (!this.running) return;
    const targetFromFire = this.firePower * 10;
    this.temp += (targetFromFire - this.temp) * 0.05;
    this.duration += 0.1;
    document.getElementById('temp-val').textContent = Math.round(this.temp);
    document.getElementById('dur-val').textContent = `${Math.round(this.duration)}/${this.targetDuration}`;
    this.renderMinigame();
    if (this.stirAnim) {
      this.stirAnim *= 0.9;
      if (this.stirAnim < 0.05) this.stirAnim = 0;
    }
    if (this.duration >= this.targetDuration * 1.5) {
      this.running = false;
      this.finishCraft();
      return;
    }
    this.timer = setTimeout(() => this.loop(), 100);
  },

  renderMinigame() {
    if (!this.ctx) return;
    const w = this.canvas.width, h = this.canvas.height;
    this.ctx.clearRect(0, 0, w, h);
    this.ctx.fillStyle = '#0a0505';
    this.ctx.fillRect(0, 0, w, h);
    const cx = w / 2, cy = h / 2 + 10;
    const r = 80;
    const fireColor = this.temp > this.tempMax ? '#ff0000' : (this.temp > this.targetTemp * 0.8 ? '#ff6b00' : '#ffaa00');
    this.ctx.fillStyle = fireColor;
    for (let i = 0; i < 5; i++) {
      const fx = cx - 30 + i * 15;
      const fy = cy + r + 5;
      const flameH = 20 + Math.sin(Date.now() / 100 + i) * 10 + (this.firePower / 100) * 30;
      this.ctx.beginPath();
      this.ctx.moveTo(fx, fy);
      this.ctx.quadraticCurveTo(fx - 5, fy - flameH / 2, fx, fy - flameH);
      this.ctx.quadraticCurveTo(fx + 5, fy - flameH / 2, fx, fy);
      this.ctx.fill();
    }
    this.ctx.fillStyle = '#3a2a1a';
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.strokeStyle = '#5a3a1a';
    this.ctx.lineWidth = 4;
    this.ctx.stroke();
    const tempClose = 1 - Math.abs(this.temp - this.targetTemp) / (this.tempMax - this.tempMin);
    let liquidColor;
    if (tempClose > 0.8) liquidColor = '#ffd700';
    else if (tempClose > 0.5) liquidColor = '#d4af37';
    else if (tempClose > 0.2) liquidColor = '#a87a3a';
    else liquidColor = '#3a2a1a';
    if (this.temp > this.tempMax) liquidColor = '#1a0a0a';
    this.ctx.fillStyle = liquidColor;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, r - 8, 0, Math.PI * 2);
    this.ctx.fill();
    if (this.temp > 100) {
      const t = Date.now() / 200;
      for (let i = 0; i < 5; i++) {
        const bx = cx + Math.cos(t + i) * 40;
        const by = cy + Math.sin(t * 1.3 + i) * 40;
        this.ctx.fillStyle = 'rgba(255,255,255,0.3)';
        this.ctx.beginPath();
        this.ctx.arc(bx, by, 3 + Math.sin(t * 2 + i) * 2, 0, Math.PI * 2);
        this.ctx.fill();
      }
    }
    if (this.stirAnim) {
      this.ctx.strokeStyle = `rgba(255,255,255,${this.stirAnim})`;
      this.ctx.lineWidth = 3;
      this.ctx.beginPath();
      const stirAngle = Date.now() / 100;
      this.ctx.arc(cx, cy, 40, stirAngle, stirAngle + Math.PI * 1.5);
      this.ctx.stroke();
    }
    // 温度计
    const tx = 20, ty = 20, tw = 16, th = 240;
    this.ctx.fillStyle = '#1a1525';
    this.ctx.fillRect(tx, ty, tw, th);
    const tempPct = Math.max(0, Math.min(1, this.temp / 1000));
    this.ctx.fillStyle = fireColor;
    this.ctx.fillRect(tx, ty + th - th * tempPct, tw, th * tempPct);
    const tgtY = ty + th - th * (this.targetTemp / 1000);
    this.ctx.strokeStyle = '#d4af37';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.moveTo(tx - 4, tgtY);
    this.ctx.lineTo(tx + tw + 4, tgtY);
    this.ctx.stroke();
  },

  async finishCraft() {
    if (this.running) {
      this.running = false;
      if (this.timer) clearTimeout(this.timer);
    }
    const process = {
      temperature: Math.round(this.temp),
      duration: Math.round(this.duration),
      stirring: this.stirring
    };
    const materials = {
      main: this.selectedMain,
      auxiliary: this.selectedAux,
      catalyst: this.selectedCatalyst
    };
    const r = await API.alchemyCraft(this.selectedRecipe.id, materials, process);
    await UI.refresh();
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
        <button class="btn gold" onclick="Alchemy.open()">再次炼丹</button>
        <button class="btn" onclick="UI.closeModal()">关闭</button>
      </div>
    `;
    UI.setModalBody(html);
    UI.toast(r.msg, r.ok ? 'success' : 'error');
  }
};
