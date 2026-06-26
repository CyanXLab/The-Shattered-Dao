// 逆仙录·天道残卷 - 地图渲染器（支持拖拽、缩放、大地图）
const Renderer = {
  canvas: null, ctx: null,
  TILE_SIZE: 16, SCALE: 1.5, state: null,
  // 视口偏移（拖拽）
  offsetX: 0, offsetY: 0,
  isDragging: false, dragStartX: 0, dragStartY: 0, dragOffsetX: 0, dragOffsetY: 0,
  // 缩放级别
  zoom: 1.5,

  init() {
    this.canvas = document.getElementById('game-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.ctx.imageSmoothingEnabled = false;
    this.bindDragZoom();
  },

  bindDragZoom() {
    // 鼠标拖拽
    this.canvas.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return;
      this.isDragging = true;
      this.dragStartX = e.clientX;
      this.dragStartY = e.clientY;
      this.dragOffsetX = this.offsetX;
      this.dragOffsetY = this.offsetY;
      this.canvas.style.cursor = 'grabbing';
    });
    window.addEventListener('mousemove', (e) => {
      if (!this.isDragging) return;
      this.offsetX = this.dragOffsetX + (e.clientX - this.dragStartX);
      this.offsetY = this.dragOffsetY + (e.clientY - this.dragStartY);
      this.render(this.state);
    });
    window.addEventListener('mouseup', () => {
      if (this.isDragging) {
        this.isDragging = false;
        this.canvas.style.cursor = 'crosshair';
      }
    });
    // 滚轮缩放
    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.2 : 0.2;
      this.zoom = Math.max(0.8, Math.min(4, this.zoom + delta));
      this.render(this.state);
    }, { passive: false });
    // 触摸支持
    let touchStartDist = 0, touchStartZoom = 1;
    this.canvas.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        this.isDragging = true;
        this.dragStartX = e.touches[0].clientX;
        this.dragStartY = e.touches[0].clientY;
        this.dragOffsetX = this.offsetX;
        this.dragOffsetY = this.offsetY;
      } else if (e.touches.length === 2) {
        this.isDragging = false;
        touchStartDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        touchStartZoom = this.zoom;
      }
    });
    this.canvas.addEventListener('touchmove', (e) => {
      e.preventDefault();
      if (e.touches.length === 1 && this.isDragging) {
        this.offsetX = this.dragOffsetX + (e.touches[0].clientX - this.dragStartX);
        this.offsetY = this.dragOffsetY + (e.touches[0].clientY - this.dragStartY);
        this.render(this.state);
      } else if (e.touches.length === 2) {
        const dist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        this.zoom = Math.max(0.8, Math.min(4, touchStartZoom * dist / touchStartDist));
        this.render(this.state);
      }
    }, { passive: false });
    this.canvas.addEventListener('touchend', () => { this.isDragging = false; });
  },

  centerOnPlayer() {
    if (!this.state) return;
    const p = this.state.player;
    const cw = this.canvas.width, ch = this.canvas.height;
    const ts = this.TILE_SIZE * this.zoom;
    this.offsetX = cw / 2 - p.x * ts - ts / 2;
    this.offsetY = ch / 2 - p.y * ts - ts / 2;
  },

  render(state) {
    if (!this.canvas || !state) return;
    this.state = state;
    const region = state.region;
    const p = state.player;
    // canvas固定大小
    this.canvas.width = 832;
    this.canvas.height = 624;
    this.ctx.imageSmoothingEnabled = false;
    const ts = this.TILE_SIZE * this.zoom;
    // 清屏
    this.ctx.fillStyle = '#050510';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.save();
    this.ctx.translate(this.offsetX, this.offsetY);
    // 绘制地面
    this.drawGround(region, ts);
    // 出口
    this.drawExits(region, ts);
    // 资源
    for (const r of state.visible_resources) this.drawResource(r, ts);
    // 建筑
    for (const b of region.buildings) this.drawBuilding(b, ts);
    // NPC
    for (const npc of state.visible_npcs) this.drawNPC(npc, ts);
    // 妖兽
    for (const b of state.visible_beasts) this.drawBeast(b, ts);
    // 玩家
    this.drawPlayer(p, ts);
    // 视野指示
    this.drawVisionIndicator(p, ts);
    this.ctx.restore();
    // UI信息
    this.drawMinimap(state);
  },

  drawGround(region, ts) {
    let baseColor = '#1a3a1a', accentColor = '#0a2a0a';
    if (region.type === 'market') { baseColor = '#3a3a3a'; accentColor = '#2a2a2a'; }
    else if (region.type === 'beast_mountain') { baseColor = '#1a2a1a'; accentColor = '#0a1a0a'; }
    else if (region.type === 'forbidden') { baseColor = '#2a0a1a'; accentColor = '#1a050a'; }
    else if (region.type === 'mortal_kingdom') { baseColor = '#3a2a1a'; accentColor = '#2a1a0a'; }
    else if (region.type === 'void_rift') { baseColor = '#1a0a2a'; accentColor = '#0a051a'; }
    else if (region.type === 'spirit_realm') { baseColor = '#1a2a3a'; accentColor = '#0a1a2a'; }
    else if (region.type === 'demon_realm') { baseColor = '#2a0a0a'; accentColor = '#1a0505'; }
    else if (region.type === 'dragon_palace') { baseColor = '#0a1a2a'; accentColor = '#050a1a'; }
    else if (region.type === 'heaven_realm') { baseColor = '#3a3a1a'; accentColor = '#2a2a0a'; }
    // 只绘制可见范围内的格子
    const startX = Math.max(0, Math.floor(-this.offsetX / ts));
    const startY = Math.max(0, Math.floor(-this.offsetY / ts));
    const endX = Math.min(region.width, Math.ceil((this.canvas.width - this.offsetX) / ts));
    const endY = Math.min(region.height, Math.ceil((this.canvas.height - this.offsetY) / ts));
    for (let y = startY; y < endY; y++) {
      for (let x = startX; x < endX; x++) {
        this.ctx.fillStyle = (x + y) % 2 === 0 ? baseColor : accentColor;
        this.ctx.fillRect(x * ts, y * ts, ts, ts);
      }
    }
    // 区域边界
    this.ctx.strokeStyle = 'rgba(212,175,55,0.3)';
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(0, 0, region.width * ts, region.height * ts);
  },

  drawBuilding(b, ts) {
    const x = b.x * ts, y = b.y * ts, w = b.w * ts, h = b.h * ts;
    // 视口裁剪
    if (x + w < -this.offsetX || x > this.canvas.width - this.offsetX ||
        y + h < -this.offsetY || y > this.canvas.height - this.offsetY) return;
    this.ctx.fillStyle = 'rgba(0,0,0,0.4)';
    this.ctx.fillRect(x + 3, y + 3, w, h);
    this.ctx.fillStyle = '#3a2a1a';
    this.ctx.fillRect(x, y, w, h);
    this.ctx.fillStyle = '#5a3a1a';
    this.ctx.fillRect(x, y, w, Math.max(ts, h * 0.3));
    this.ctx.strokeStyle = '#d4af37';
    this.ctx.lineWidth = 1;
    this.ctx.strokeRect(x, y, w, h);
    this.ctx.fillStyle = '#1a0a0a';
    this.ctx.fillRect(x + w / 2 - ts * 0.3, y + h - ts * 0.8, ts * 0.6, ts * 0.8);
    if (ts >= 10) {
      this.ctx.fillStyle = '#d4af37';
      this.ctx.font = `${Math.floor(ts * 0.55)}px "Noto Sans SC", sans-serif`;
      this.ctx.textAlign = 'center';
      this.ctx.textBaseline = 'middle';
      this.ctx.fillText(b.name, x + w / 2, y + h / 2);
    }
  },

  drawExits(region, ts) {
    if (!region.exits) return;
    for (const ex of region.exits) {
      const x = ex.x * ts, y = ex.y * ts;
      const t = Date.now() / 500;
      this.ctx.fillStyle = `rgba(212, 175, 55, ${0.5 + 0.3 * Math.sin(t)})`;
      this.ctx.fillRect(x, y, ts, ts);
      this.ctx.strokeStyle = '#ffd700';
      this.ctx.lineWidth = 2;
      this.ctx.strokeRect(x + 1, y + 1, ts - 2, ts - 2);
    }
  },

  drawResource(r, ts) {
    const x = r.x * ts, y = r.y * ts;
    const t = Date.now() / 800;
    let color = '#6bc832';
    if (r.type === 'ore') color = '#a8a8c8';
    this.ctx.fillStyle = `rgba(${this.hexToRgb(color)}, ${0.6 + 0.3 * Math.sin(t)})`;
    this.ctx.beginPath();
    this.ctx.arc(x + ts / 2, y + ts / 2, ts * 0.35, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.fillStyle = color;
    this.ctx.beginPath();
    this.ctx.arc(x + ts / 2, y + ts / 2, ts * 0.2, 0, Math.PI * 2);
    this.ctx.fill();
    if (ts >= 12) {
      this.ctx.fillStyle = '#9ad96b';
      this.ctx.font = `${Math.max(8, Math.floor(ts * 0.4))}px sans-serif`;
      this.ctx.textAlign = 'center';
      this.ctx.fillText(r.name, x + ts / 2, y - 2);
    }
  },

  drawNPC(npc, ts) {
    const x = npc.x * ts, y = npc.y * ts;
    this.ctx.fillStyle = 'rgba(0,0,0,0.4)';
    this.ctx.beginPath();
    this.ctx.ellipse(x + ts / 2, y + ts - 1, ts * 0.3, ts * 0.15, 0, 0, Math.PI * 2);
    this.ctx.fill();
    let bodyColor = '#5a7a9a';
    if (npc.relationship < 0) bodyColor = '#9a3a3a';
    else if (npc.relationship >= 50) bodyColor = '#d4af37';
    this.ctx.fillStyle = bodyColor;
    this.ctx.fillRect(x + ts * 0.25, y + ts * 0.3, ts * 0.5, ts * 0.55);
    this.ctx.fillStyle = '#e8d4b8';
    this.ctx.beginPath();
    this.ctx.arc(x + ts / 2, y + ts * 0.25, ts * 0.2, 0, Math.PI * 2);
    this.ctx.fill();
    if (ts >= 10) {
      this.ctx.fillStyle = npc.relationship >= 50 ? '#d4af37' : '#e8e0c8';
      this.ctx.font = `${Math.max(8, Math.floor(ts * 0.5))}px "Noto Sans SC", sans-serif`;
      this.ctx.textAlign = 'center';
      this.ctx.fillText(npc.name, x + ts / 2, y - 2);
    }
  },

  drawBeast(b, ts) {
    const x = b.x * ts, y = b.y * ts;
    this.ctx.fillStyle = 'rgba(0,0,0,0.4)';
    this.ctx.beginPath();
    this.ctx.ellipse(x + ts / 2, y + ts - 1, ts * 0.35, ts * 0.18, 0, 0, Math.PI * 2);
    this.ctx.fill();
    let bodyColor = '#9a3a3a';
    if (b.tier >= 7) bodyColor = '#ffd700';
    else if (b.tier >= 5) bodyColor = '#c832c8';
    else if (b.tier >= 4) bodyColor = '#c83232';
    this.ctx.fillStyle = bodyColor;
    this.ctx.fillRect(x + ts * 0.15, y + ts * 0.3, ts * 0.7, ts * 0.55);
    this.ctx.fillStyle = '#ff0000';
    this.ctx.fillRect(x + ts * 0.3, y + ts * 0.35, ts * 0.1, ts * 0.1);
    this.ctx.fillRect(x + ts * 0.6, y + ts * 0.35, ts * 0.1, ts * 0.1);
    if (ts >= 10) {
      this.ctx.fillStyle = '#ff6b6b';
      this.ctx.font = `${Math.max(8, Math.floor(ts * 0.45))}px sans-serif`;
      this.ctx.textAlign = 'center';
      this.ctx.fillText(b.name, x + ts / 2, y - 2);
    }
    const t = Date.now() / 400;
    if (Math.sin(t) > 0.7) {
      this.ctx.strokeStyle = '#ff0000';
      this.ctx.lineWidth = 1;
      this.ctx.strokeRect(x + 1, y + 1, ts - 2, ts - 2);
    }
  },

  drawPlayer(p, ts) {
    const x = p.x * ts, y = p.y * ts;
    this.ctx.fillStyle = 'rgba(0,0,0,0.4)';
    this.ctx.beginPath();
    this.ctx.ellipse(x + ts / 2, y + ts - 1, ts * 0.3, ts * 0.15, 0, 0, Math.PI * 2);
    this.ctx.fill();
    const t = Date.now() / 600;
    if (p.in_combat) {
      this.ctx.strokeStyle = `rgba(255, 0, 0, ${0.5 + 0.4 * Math.sin(t)})`;
      this.ctx.lineWidth = 2;
      this.ctx.beginPath();
      this.ctx.arc(x + ts / 2, y + ts / 2, ts * 0.6, 0, Math.PI * 2);
      this.ctx.stroke();
    }
    this.ctx.fillStyle = '#d4af37';
    this.ctx.fillRect(x + ts * 0.25, y + ts * 0.3, ts * 0.5, ts * 0.55);
    this.ctx.fillStyle = '#e8d4b8';
    this.ctx.beginPath();
    this.ctx.arc(x + ts / 2, y + ts * 0.25, ts * 0.2, 0, Math.PI * 2);
    this.ctx.fill();
    const t2 = Date.now() / 500;
    this.ctx.fillStyle = `rgba(255, 215, 0, ${0.7 + 0.3 * Math.sin(t2)})`;
    this.ctx.beginPath();
    this.ctx.moveTo(x + ts / 2, y - ts * 0.4);
    this.ctx.lineTo(x + ts * 0.35, y - ts * 0.2);
    this.ctx.lineTo(x + ts * 0.65, y - ts * 0.2);
    this.ctx.closePath();
    this.ctx.fill();
  },

  drawVisionIndicator(p, ts) {
    const x = p.x * ts, y = p.y * ts;
    const gradient = this.ctx.createRadialGradient(x + ts / 2, y + ts / 2, 0, x + ts / 2, y + ts / 2, ts * 5);
    gradient.addColorStop(0, 'rgba(212, 175, 55, 0.08)');
    gradient.addColorStop(1, 'rgba(212, 175, 55, 0)');
    this.ctx.fillStyle = gradient;
    this.ctx.fillRect(x - ts * 5, y - ts * 5, ts * 10, ts * 10);
  },

  drawMinimap(state) {
    // 右下角小地图
    const mw = 120, mh = 90;
    const mx = this.canvas.width - mw - 10, my = this.canvas.height - mh - 10;
    const region = state.region;
    const p = state.player;
    const sx = mw / region.width, sy = mh / region.height;
    this.ctx.fillStyle = 'rgba(0,0,0,0.7)';
    this.ctx.fillRect(mx, my, mw, mh);
    this.ctx.strokeStyle = '#d4af37';
    this.ctx.lineWidth = 1;
    this.ctx.strokeRect(mx, my, mw, mh);
    // 建筑
    for (const b of region.buildings) {
      this.ctx.fillStyle = '#5a3a1a';
      this.ctx.fillRect(mx + b.x * sx, my + b.y * sy, b.w * sx, b.h * sy);
    }
    // 资源
    for (const r of state.visible_resources) {
      this.ctx.fillStyle = '#6bc832';
      this.ctx.fillRect(mx + r.x * sx - 1, my + r.y * sy - 1, 2, 2);
    }
    // 妖兽
    for (const b of state.visible_beasts) {
      this.ctx.fillStyle = '#ff6b6b';
      this.ctx.fillRect(mx + b.x * sx - 1, my + b.y * sy - 1, 2, 2);
    }
    // 玩家
    this.ctx.fillStyle = '#ffd700';
    this.ctx.fillRect(mx + p.x * sx - 2, my + p.y * sy - 2, 4, 4);
    // 缩放指示
    this.ctx.fillStyle = '#8a7a9a';
    this.ctx.font = '10px monospace';
    this.ctx.textAlign = 'left';
    this.ctx.fillText(`缩放${this.zoom.toFixed(1)}x`, mx, my - 4);
  },

  hexToRgb(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `${r},${g},${b}`;
  },

  pixelToTile(px, py) {
    const rect = this.canvas.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const scaleY = this.canvas.height / rect.height;
    const canvasX = (px - rect.left) * scaleX - this.offsetX;
    const canvasY = (py - rect.top) * scaleY - this.offsetY;
    const ts = this.TILE_SIZE * this.zoom;
    const x = Math.floor(canvasX / ts);
    const y = Math.floor(canvasY / ts);
    return { x, y };
  }
};
