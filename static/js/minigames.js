// 逆仙录·天道残卷 - 小游戏（采药/突破）
const Minigames = {};

// ==================== 采药小游戏（觅长生风格） ====================
Minigames.gatherHerb = async function(resourceId, herbName, herbTier) {
  // 显示采药小游戏界面
  const overlay = document.getElementById('modal-overlay');
  const html = `
    <div style="text-align:center">
      <h2 style="color:#6bc832;margin-bottom:8px">采药·${herbName}</h2>
      <div style="color:#8a7a9a;font-size:12px;margin-bottom:12px">${herbTier}阶灵药，时机精准方可完美采集</div>
      <canvas id="herb-canvas" width="400" height="200" style="border:1px solid #3a3450;background:#0a0a14;border-radius:4px"></canvas>
      <div id="herb-status" style="margin-top:8px;color:#d4af37;font-size:14px">等待开始...</div>
      <div style="margin-top:12px">
        <button class="btn gold" id="herb-collect-btn" onclick="Minigames.herbCollect()" disabled>采集！</button>
        <button class="btn" onclick="Minigames.herbCancel()">放弃</button>
      </div>
      <div style="color:#8a7a9a;font-size:11px;margin-top:8px">规则：药力条在最佳区域(金色)时点击采集，完美区获得双倍</div>
    </div>
  `;
  document.getElementById('modal-title').textContent = '采药';
  document.getElementById('modal-body').innerHTML = html;
  overlay.style.display = 'flex';
  // 初始化小游戏
  Minigames.herbData = {
    resourceId: resourceId,
    canvas: document.getElementById('herb-canvas'),
    ctx: document.getElementById('herb-canvas').getContext('2d'),
    pos: 0, dir: 1, speed: 0.8 + herbTier * 0.3,
    running: true, bestZone: [60, 80], goodZone: [40, 100],
    score: 0, attempts: 0
  };
  Minigames.herbLoop();
  document.getElementById('herb-collect-btn').disabled = false;
};

Minigames.herbLoop = function() {
  const d = Minigames.herbData;
  if (!d || !d.running) return;
  d.pos += d.dir * d.speed;
  if (d.pos >= 100) { d.pos = 100; d.dir = -1; }
  if (d.pos <= 0) { d.pos = 0; d.dir = 1; }
  const ctx = d.ctx;
  const w = d.canvas.width, h = d.canvas.height;
  ctx.clearRect(0, 0, w, h);
  // 背景
  ctx.fillStyle = '#0a0a14';
  ctx.fillRect(0, 0, w, h);
  // 良好区
  ctx.fillStyle = 'rgba(155,200,50,0.2)';
  ctx.fillRect(d.goodZone[0] * w / 100, 40, (d.goodZone[1] - d.goodZone[0]) * w / 100, h - 60);
  // 最佳区
  ctx.fillStyle = 'rgba(255,215,0,0.4)';
  ctx.fillRect(d.bestZone[0] * w / 100, 40, (d.bestZone[1] - d.bestZone[0]) * w / 100, h - 60);
  // 药力条
  const barX = d.pos * w / 100;
  ctx.fillStyle = '#d4af37';
  ctx.fillRect(barX - 3, 30, 6, h - 40);
  // 文字
  ctx.fillStyle = '#8a7a9a';
  ctx.font = '12px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('药力波动', w / 2, 20);
  // 刻度
  for (let i = 0; i <= 100; i += 20) {
    ctx.fillStyle = '#3a3450';
    ctx.fillRect(i * w / 100, h - 20, 1, 5);
    ctx.fillStyle = '#5a4a6a';
    ctx.font = '9px monospace';
    ctx.fillText(i, i * w / 100, h - 8);
  }
  requestAnimationFrame(Minigames.herbLoop);
};

Minigames.herbCollect = async function() {
  const d = Minigames.herbData;
  if (!d) return;
  d.running = false;
  const pos = d.pos;
  let score = 0;
  if (pos >= d.bestZone[0] && pos <= d.bestZone[1]) {
    score = 80 + (100 - Math.abs(pos - 70) * 3);
    document.getElementById('herb-status').textContent = '完美时机！';
    document.getElementById('herb-status').style.color = '#ffd700';
  } else if (pos >= d.goodZone[0] && pos <= d.goodZone[1]) {
    score = 50 + (100 - Math.abs(pos - 70) * 1.5);
    document.getElementById('herb-status').textContent = '良好时机';
    document.getElementById('herb-status').style.color = '#6bc832';
  } else {
    score = Math.max(10, 50 - Math.abs(pos - 70));
    document.getElementById('herb-status').textContent = '时机不佳';
    document.getElementById('herb-status').style.color = '#ff6b6b';
  }
  const r = await API.gatherHerbComplete(d.resourceId, score);
  setTimeout(() => {
    UI.closeModal();
    UI.toast(r.msg, r.ok ? 'success' : 'error');
    UI.refresh();
  }, 800);
};

Minigames.herbCancel = function() {
  if (Minigames.herbData) Minigames.herbData.running = false;
  UI.closeModal();
};

// ==================== 突破小游戏 ====================
Minigames.breakthrough = async function(method) {
  const startR = await API.breakthroughMinigameStart(method);
  if (!startR.ok) {
    UI.toast(startR.msg, 'error');
    return;
  }
  const html = `
    <div style="text-align:center">
      <h2 style="color:#d4af37;margin-bottom:8px">突破·${startR.next_realm}</h2>
      <div style="color:#8a7a9a;font-size:12px;margin-bottom:12px">${startR.is_minor ? '小境界突破' : '★ 大境界突破 ★'} | 共${startR.rounds}回合</div>
      <canvas id="bt-canvas" width="400" height="250" style="border:1px solid #3a3450;background:#0a0a14;border-radius:4px"></canvas>
      <div id="bt-status" style="margin-top:8px;color:#d4af37;font-size:14px">第 1 / ${startR.rounds} 回合</div>
      <div style="margin-top:12px">
        <button class="btn gold" id="bt-collect-btn" onclick="Minigames.btCollect()" disabled>引导灵气！</button>
      </div>
      <div style="color:#8a7a9a;font-size:11px;margin-top:8px">灵气运行至中心金圈时点击，越准得分越高</div>
    </div>
  `;
  document.getElementById('modal-title').textContent = '突破';
  document.getElementById('modal-body').innerHTML = html;
  Minigames.btData = {
    method: method,
    rounds: startR.rounds,
    currentRound: 0,
    scores: [],
    canvas: document.getElementById('bt-canvas'),
    ctx: document.getElementById('bt-canvas').getContext('2d'),
    angle: 0, speed: 0.04 + startR.difficulty * 0.001,
    running: true, targetAngle: 0
  };
  Minigames.btNewRound();
  document.getElementById('bt-collect-btn').disabled = false;
};

Minigames.btNewRound = function() {
  const d = Minigames.btData;
  d.targetAngle = Math.random() * Math.PI * 2;
  d.angle = Math.random() * Math.PI * 2;
  Minigames.btLoop();
};

Minigames.btLoop = function() {
  const d = Minigames.btData;
  if (!d || !d.running) return;
  d.angle += d.speed;
  if (d.angle > Math.PI * 2) d.angle -= Math.PI * 2;
  const ctx = d.ctx;
  const w = d.canvas.width, h = d.canvas.height;
  const cx = w / 2, cy = h / 2;
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = '#0a0a14';
  ctx.fillRect(0, 0, w, h);
  // 外圈
  ctx.strokeStyle = '#3a3450';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(cx, cy, 80, 0, Math.PI * 2);
  ctx.stroke();
  // 目标区（金色弧）
  ctx.strokeStyle = '#ffd700';
  ctx.lineWidth = 8;
  ctx.beginPath();
  ctx.arc(cx, cy, 80, d.targetAngle - 0.3, d.targetAngle + 0.3);
  ctx.stroke();
  // 灵气点
  const px = cx + Math.cos(d.angle) * 80;
  const py = cy + Math.sin(d.angle) * 80;
  ctx.fillStyle = '#d4af37';
  ctx.beginPath();
  ctx.arc(px, py, 8, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 10;
  ctx.shadowColor = '#d4af37';
  ctx.fill();
  ctx.shadowBlur = 0;
  // 中心
  ctx.fillStyle = '#8a7a9a';
  ctx.font = '12px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('丹田', cx, cy + 4);
  requestAnimationFrame(Minigames.btLoop);
};

Minigames.btCollect = async function() {
  const d = Minigames.btData;
  if (!d) return;
  // 计算角度差
  let diff = Math.abs(d.angle - d.targetAngle);
  if (diff > Math.PI) diff = Math.PI * 2 - diff;
  const score = Math.max(0, 100 - diff * 100);
  d.scores.push(score);
  d.currentRound++;
  document.getElementById('bt-status').textContent = `第 ${d.currentRound} / ${d.rounds} 回合 — 上次得分 ${score.toFixed(0)}`;
  if (d.currentRound >= d.rounds) {
    d.running = false;
    document.getElementById('bt-collect-btn').disabled = true;
    const r = await API.breakthroughMinigameComplete(d.method, d.scores);
    const success = r.ok && r.breakthrough;
    setTimeout(() => {
      UI.closeModal();
      UI.toast(r.msg, r.ok ? 'success' : 'error');
      UI.refresh();
      // 大境界突破成功后触发天劫
      if (success && Minigames._pendingTribulation) {
        API.triggerTribulation().then(tr => {
          if (tr.action === 'tribulation') Tribulation.start(tr.tribulation);
        });
      }
      Minigames._pendingTribulation = false;
    }, 800);
  } else {
    Minigames.btNewRound();
  }
};
