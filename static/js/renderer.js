// 逆仙录·天道残卷 - 地图渲染器
const Renderer = {
  canvas: null, ctx: null,
  TILE_SIZE: 16, SCALE: 1, state: null,

  init() {
    this.canvas = document.getElementById('game-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.ctx.imageSmoothingEnabled = false;
  },

  render(state) {
    if (!this.canvas || !state) return;
    this.state = state;
    const region = state.region;
    const p = state.player;
    const containerW = this.canvas.parentElement.clientWidth - 20;
    const containerH = this.canvas.parentElement.clientHeight - 20;
    const scaleX = containerW / (region.width * this.TILE_SIZE);
    const scaleY = containerH / (region.height * this.TILE_SIZE);
    this.SCALE = Math.max(1, Math.min(scaleX, scaleY, 1.5));
    this.canvas.width = region.width * this.TILE_SIZE * this.SCALE;
    this.canvas.height = region.height * this.TILE_SIZE * this.SCALE;
    this.ctx.imageSmoothingEnabled = false;
    const ts = this.TILE_SIZE * this.SCALE;
    this.drawGround(region, ts);
    this.drawExits(region, ts);
    for (const r of state.visible_resources) this.drawResource(r, ts);
    for (const b of region.buildings) this.drawBuilding(b, ts);
    for (const npc of state.visible_npcs) this.drawNPC(npc, ts);
    for (const b of state.visible_beasts) this.drawBeast(b, ts);
    this.drawPlayer(p, ts);
    this.drawVisionIndicator(p, ts);
  },

  drawGround(region, ts) {
    const ground = 'grass';
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
    for (let y = 0; y < region.height; y++) {
      for (let x = 0; x < region.width; x++) {
        this.ctx.fillStyle = (x + y) % 2 === 0 ? baseColor : accentColor;
        this.ctx.fillRect(x * ts, y * ts, ts, ts);
      }
    }
  },

  drawBuilding(b, ts) {
    const x = b.x * ts, y = b.y * ts, w = b.w * ts, h = b.h * ts;
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
    if (ts >= 8) {
      this.ctx.fillStyle = '#d4af37';
      this.ctx.font = `${Math.floor(ts * 0.6)}px "Noto Sans SC", sans-serif`;
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
    if (ts >= 10) {
      this.ctx.fillStyle = '#9ad96b';
      this.ctx.font = `${Math.max(8, Math.floor(ts * 0.45))}px sans-serif`;
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
    if (ts >= 8) {
      this.ctx.fillStyle = npc.relationship >= 50 ? '#d4af37' : '#e8e0c8';
      this.ctx.font = `${Math.max(8, Math.floor(ts * 0.55))}px "Noto Sans SC", sans-serif`;
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
    if (ts >= 8) {
      this.ctx.fillStyle = '#ff6b6b';
      this.ctx.font = `${Math.max(8, Math.floor(ts * 0.5))}px sans-serif`;
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
    const x = Math.floor((px - rect.left) * scaleX / (this.TILE_SIZE * this.SCALE));
    const y = Math.floor((py - rect.top) * scaleY / (this.TILE_SIZE * this.SCALE));
    return { x, y };
  }
};
