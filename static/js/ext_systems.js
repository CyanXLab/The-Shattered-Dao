// 逆仙录·天道残卷 - 扩展系统UI（阵法/道侣/剧情/拍卖/PVP/宗门战）
const ExtSystems = {};

// ==================== 阵法系统 ====================
UI.openFormations = async function() {
  const forms = await API.formations();
  let html = '<div class="detail-box"><div style="color:#d4af37;margin-bottom:6px">阵法</div><div style="color:#8a7a9a;font-size:12px">布阵需消耗阵旗和灵石，阵法提供各种增益。破阵需神识。</div></div>';
  html += '<div class="section-title">阵法列表</div>';
  for (const f of forms) {
    const matNames = f.materials.map(m => `${ITEM_NAMES[m.item] || m.item}×${m.count}`).join(', ');
    html += `<div class="detail-box">
      <div style="color:#d4af37;font-weight:bold">${f.name} <span style="color:#8a7a9a;font-weight:normal;font-size:11px">${f.tier}阶·${f.type}</span></div>
      <div style="color:#a8a8c8;font-size:12px;margin:4px 0">${f.desc}</div>
      <div style="color:#8a7a9a;font-size:11px">材料：${matNames} | 灵石：${f.spirit_stone_cost}</div>
      <div style="margin-top:6px"><button class="btn gold" onclick="UI.setFormation('${f.id}')">布阵</button>
      <button class="btn" onclick="UI.breakFormation('${f.id}')">破阵</button></div>
    </div>`;
  }
  this.openModal('阵法', html);
};

UI.setFormation = async function(fid) {
  const r = await API.setFormation(fid);
  this.toast(r.msg, r.ok ? 'success' : 'error');
  await this.refresh();
};

UI.breakFormation = async function(fid) {
  const r = await API.breakFormation(fid);
  this.toast(r.msg, r.ok ? 'success' : 'error');
  await this.refresh();
};

// ==================== 道侣系统 ====================
UI.openCompanion = function() {
  const p = this.state.player;
  let html = '<div class="detail-box"><div style="color:#d4af37;margin-bottom:6px">道侣</div><div style="color:#8a7a9a;font-size:12px">道侣是大道同行之人，可双修共进。但背叛将招致大因果。</div></div>';
  if (p.dao_companion) {
    const npc = this.state.visible_npcs.find(n => n.id === p.dao_companion);
    const name = npc ? npc.name : p.dao_companion;
    html += `<div class="detail-box" style="border-color:#c832c8">
      <div style="color:#ff6bff;font-weight:bold">★ 你的道侣：${name}</div>
      <div style="color:#a8a8c8;font-size:12px;margin-top:4px">大道同行，可双修共进。</div>
    </div>
    <div class="section-title">双修</div>
    <div class="cultivate-options">
      <button class="cultivate-btn" onclick="UI.dualCultivate(1)"><span class="hours">1小时</span><span class="desc">双修</span></button>
      <button class="cultivate-btn" onclick="UI.dualCultivate(4)"><span class="hours">4小时</span><span class="desc">双修</span></button>
      <button class="cultivate-btn" onclick="UI.dualCultivate(8)"><span class="hours">8小时</span><span class="desc">双修</span></button>
    </div>
    <div class="section-title">危险操作</div>
    <button class="btn danger" onclick="UI.betrayCompanion()">背叛道侣（业力-200）</button>`;
  } else {
    html += '<div class="detail-box" style="color:#8a7a9a">尚无道侣</div>';
    html += '<div class="section-title">可求婚对象</div>';
    for (const npc of this.state.visible_npcs) {
      if (npc.relationship >= 80) {
        html += `<div class="detail-box">
          <div style="color:#d4af37">${npc.name} <span style="color:#8a7a9a;font-size:11px">关系${npc.relationship}</span></div>
          <button class="btn gold" style="margin-top:6px" onclick="UI.proposeCompanion('${npc.id}')">求婚</button>
        </div>`;
      }
    }
    if (!this.state.visible_npcs.some(n => n.relationship >= 80)) {
      html += '<div class="detail-box" style="color:#8a7a9a">需与NPC关系达到80以上方可求婚。多送礼提升关系。</div>';
    }
  }
  this.openModal('道侣', html);
};

UI.proposeCompanion = async function(npcId) {
  const r = await API.proposeCompanion(npcId);
  this.toast(r.msg, r.ok ? 'success' : 'error');
  await this.refresh();
  this.openCompanion();
};

UI.dualCultivate = async function(hours) {
  this.closeModal();
  const r = await API.dualCultivate(hours);
  this.toast(r.msg, r.ok ? 'success' : 'error');
  await this.refresh();
};

UI.betrayCompanion = async function() {
  if (!confirm('确定背叛道侣？这将损失200业力，且对方会仇视你。')) return;
  const r = await API.betrayCompanion();
  this.toast(r.msg, r.ok ? 'success' : 'error');
  await this.refresh();
  this.openCompanion();
};

// ==================== 剧情任务 ====================
UI.openStory = async function() {
  const r = await API.storyProgress();
  if (!r.ok) return;
  let html = '<div class="detail-box"><div style="color:#d4af37;margin-bottom:6px">剧情任务</div><div style="color:#8a7a9a;font-size:12px">5条主线故事，揭开修仙世界的真相。</div></div>';
  for (const story of r.storylines) {
    const progress = r.progress[story.id] || 0;
    const completed = progress >= story.chapters.length;
    html += `<div class="detail-box" style="border-color:${completed ? '#6bc832' : '#d4af37'}">
      <div style="color:${completed ? '#6bc832' : '#d4af37'};font-weight:bold">${completed ? '✓' : '○'} ${story.name} <span style="color:#8a7a9a;font-weight:normal;font-size:11px">${story.type === 'main' ? '主线' : '支线'} ${progress}/${story.chapters.length}</span></div>
      <div style="color:#a8a8c8;font-size:12px;margin:4px 0">${story.desc}</div>`;
    if (!completed) {
      const curCh = story.chapters[progress];
      html += `<div style="color:#d4af37;font-size:13px;margin-top:6px">当前：${curCh.name}</div>
      <div style="color:#e8e0c8;font-size:12px;margin-top:2px">${curCh.desc}</div>
      <div style="color:#8a7a9a;font-size:11px;margin-top:2px">目标：${curCh.objective}</div>`;
    }
    html += '</div>';
  }
  this.openModal('剧情', html);
};

// ==================== 拍卖系统 ====================
UI.openAuction = async function() {
  const items = await API.auctionList();
  let html = `<div class="detail-box"><div style="color:#d4af37;margin-bottom:6px">拍卖行</div><div style="color:#8a7a9a;font-size:12px">当前灵石：${this.state.player.spirit_stones_value}</div></div>`;
  html += '<button class="btn gold" onclick="UI.refreshAuction()" style="margin-bottom:10px">刷新拍卖物品（50灵石）</button>';
  html += '<div class="section-title">拍卖物品</div>';
  if (items.length === 0) {
    html += '<div class="detail-box" style="color:#8a7a9a">暂无拍卖物品</div>';
  }
  for (const it of items) {
    const rarityClass = `rarity-${it.rarity}`;
    html += `<div class="item-row">
      <div>
        <span class="item-name ${rarityClass}">${it.name}</span>
        <span class="item-tier tier-${it.tier}">${it.tier}阶</span>
        <div style="font-size:10px;color:#8a7a9a;margin-top:2px">${it.desc}</div>
        <div style="font-size:11px;color:#6bc832">底价：${it.base_price} | 当前：${it.current_price}</div>
      </div>
      <div>
        <input type="number" id="bid-${it.id}" placeholder="出价" value="${it.current_price + 10}" style="width:80px;padding:4px;background:#1a1525;border:1px solid #3a3450;color:#e8e0c8;border-radius:3px;">
        <button class="btn gold" onclick="UI.auctionBid('${it.id}')">竞拍</button>
      </div>
    </div>`;
  }
  this.openModal('拍卖行', html);
};

UI.refreshAuction = async function() {
  const r = await API.refreshAuction();
  this.toast(r.msg, r.ok ? 'success' : 'error');
  await this.refresh();
  this.openAuction();
};

UI.auctionBid = async function(aucId) {
  const bid = parseInt(document.getElementById('bid-' + aucId).value);
  if (!bid || bid <= 0) { this.toast('请输入有效出价', 'error'); return; }
  const r = await API.auctionBid(aucId, bid);
  this.toast(r.msg, r.ok ? 'success' : 'error');
  await this.refresh();
  if (r.ok) this.closeModal();
};

// ==================== PVP切磋 ====================
UI.openPVP = async function() {
  const opps = await API.pvpList();
  let html = '<div class="detail-box"><div style="color:#d4af37;margin-bottom:6px">切磋</div><div style="color:#8a7a9a;font-size:12px">与其他修士切磋，胜者获得灵石和经验，但杀孽损业力。</div></div>';
  if (opps.length === 0) {
    html += '<div class="detail-box" style="color:#8a7a9a">当前无可挑战对手。提升境界后会有更多对手出现。</div>';
  } else {
    html += '<div class="section-title">可挑战对手</div>';
    for (const opp of opps) {
      html += `<div class="item-row">
        <div>
          <span class="item-name">${opp.name}</span>
          <span style="color:#8a7a9a;font-size:11px;margin-left:6px">${opp.realm}</span>
          <div style="font-size:10px;color:#8a7a9a;margin-top:2px">${opp.desc}</div>
          <div style="font-size:11px;color:#d4af37">奖励：${opp.reward_stones}灵石 +${opp.reward_exp}经验</div>
        </div>
        <button class="btn danger" onclick="UI.startPvp('${opp.id}')">挑战</button>
      </div>`;
    }
  }
  this.openModal('切磋', html);
};

UI.startPvp = async function(oppId) {
  this.closeModal();
  const r = await API.startPvp(oppId);
  if (r.action === 'combat') {
    await this.refresh();
  } else {
    this.toast(r.msg, r.ok ? 'info' : 'error');
  }
};

// ==================== 宗门战 ====================
UI.openSectWar = function() {
  const p = this.state.player;
  let html = '<div class="detail-box"><div style="color:#d4af37;margin-bottom:6px">宗门战</div><div style="color:#8a7a9a;font-size:12px">正魔大战，影响天下格局。</div></div>';
  if (!p.sect) {
    html += '<div class="detail-box" style="color:#ff6b6b">未加入宗门，无法参与宗门战。</div>';
  } else {
    html += `<div class="detail-box">当前宗门：${p.sect}</div>`;
    html += '<button class="btn danger" onclick="UI.startSectWar()">发起宗门战（1000灵石）</button>';
    html += '<button class="btn gold" onclick="UI.joinSectWar()">加入宗门战</button>';
  }
  this.openModal('宗门战', html);
};

UI.startSectWar = async function() {
  const r = await API.startSectWar();
  this.toast(r.msg, r.ok ? 'success' : 'error');
  this.closeModal();
};

UI.joinSectWar = async function() {
  const r = await API.joinSectWar();
  this.toast(r.msg, r.ok ? 'success' : 'error');
  this.closeModal();
};

// ==================== 炼器入口 ====================
UI.openForge = function() { Forge.open(); };

// 物品名映射
const ITEM_NAMES = {
  spirit_gather_flag: '聚灵阵旗', spirit_gather_disk: '聚灵阵盘',
  defense_flag: '护身阵旗', defense_disk: '护身阵盘',
  kill_flag: '杀阵阵旗', kill_disk: '杀阵阵盘',
  illusion_flag: '幻阵阵旗', time_disk: '时间阵盘',
  wood_block: '木材', leather: '兽皮', yang_soul_wood: '养魂木',
  han_iron: '寒铁矿', chi_copper: '赤铜矿', xuan_iron: '玄铁矿',
  ling_crystal: '灵晶石', purple_gold: '紫金', star_iron: '陨星铁',
  huo_jing: '火晶', bing_jing: '冰晶', lei_jing: '雷晶', feng_jing: '风晶',
  an_jing: '暗晶', guang_jing: '光晶', xu_kong_jing: '虚空晶', chen_jing_shi: '辰精石',
  xian_tie: '仙铁', mo_tie: '魔铁', tian_yuan_iron: '天元铁', xian_yin_shi: '仙银石'
};
