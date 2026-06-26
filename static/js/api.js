// 逆仙录·天道残卷 - API通信层
const API = {
  base: '/api',
  async post(endpoint, data = {}) {
    try {
      const resp = await fetch(this.base + endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(data)
      });
      return await resp.json();
    } catch (e) {
      console.error('API error:', endpoint, e);
      return { ok: false, msg: '网络错误：' + e.message };
    }
  },
  async get(endpoint) {
    try {
      const resp = await fetch(this.base + endpoint, { credentials: 'same-origin' });
      return await resp.json();
    } catch (e) {
      console.error('API error:', endpoint, e);
      return null;
    }
  },
  // 用户系统
  register: (username, password) => API.post('/register', { username, password }),
  login: (username, password) => API.post('/login', { username, password }),
  logout: () => API.post('/logout', {}),
  me: () => API.get('/me'),
  // 游戏状态
  getState: () => API.get('/state'),
  move: (direction) => API.post('/move', { direction }),
  moveTo: (x, y) => API.post('/move_to', { x, y }),
  gather: (resource_id) => API.post('/gather', { resource_id }),
  cutTree: () => API.post('/cut_tree', {}),
  cultivate: (hours, location, cycles, use_pill, use_formation) => API.post('/cultivate', { hours, location, cycles, use_pill, use_formation }),
  breakthrough: (method) => API.post('/breakthrough', { method }),
  rest: (hours) => API.post('/rest', { hours }),
  seclusion: (days) => API.post('/seclusion', { days }),
  learnTechnique: (tech_id) => API.post('/learn_technique', { tech_id }),
  activateTechnique: (tech_id) => API.post('/activate_technique', { tech_id }),
  reverseTechnique: (tech_id, stage_idx) => API.post('/reverse_technique', { tech_id, stage_idx }),
  combatAction: (action, skill_idx, target_part, qi_allocation) => API.post('/combat_action', { action, skill_idx, target_part, qi_allocation }),
  useItemCombat: (item_id) => API.post('/use_item_combat', { item_id }),
  useItem: (item_id) => API.post('/use_item', { item_id }),
  equipItem: (item_id) => API.post('/equip_item', { item_id }),
  unequipItem: (slot) => API.post('/unequip_item', { slot }),
  alchemyRecipes: () => API.get('/alchemy_recipes'),
  alchemyCraft: (recipe_id, materials, process) => API.post('/alchemy_craft', { recipe_id, materials, process }),
  shopList: (type) => API.get('/shop_list?type=' + type),
  shopBuy: (item_id, qty) => API.post('/shop_buy', { item_id, qty }),
  shopSell: (item_id, qty) => API.post('/shop_sell', { item_id, qty }),
  talkNpc: (npc_id) => API.post('/talk_npc', { npc_id }),
  giftNpc: (npc_id, item_id, qty) => API.post('/gift_npc', { npc_id, item_id, qty }),
  plantSeed: (seed_id, plot_idx) => API.post('/plant_seed', { seed_id, plot_idx }),
  harvest: (plot_idx) => API.post('/harvest', { plot_idx }),
  tameBeast: (beast_id) => API.post('/tame_beast', { beast_id }),
  reset: () => API.post('/reset', {}),
  // 扩展系统
  forgeRecipes: () => API.get('/forge_recipes'),
  forgeCraft: (recipe_id, materials, process) => API.post('/forge_craft', { recipe_id, materials, process }),
  formations: () => API.get('/formations'),
  setFormation: (formation_id) => API.post('/set_formation', { formation_id }),
  breakFormation: (formation_id) => API.post('/break_formation', { formation_id }),
  proposeCompanion: (npc_id) => API.post('/propose_companion', { npc_id }),
  dualCultivate: (hours) => API.post('/dual_cultivate', { hours }),
  betrayCompanion: () => API.post('/betray_companion', {}),
  chooseReincarnation: (choice) => API.post('/choose_reincarnation', { choice }),
  triggerTribulation: () => API.post('/trigger_tribulation', {}),
  tribulationRound: (action, use_item) => API.post('/tribulation_round', { action, use_item }),
  storyProgress: () => API.get('/story_progress'),
  auctionList: () => API.get('/auction_list'),
  auctionBid: (auc_id, bid_price) => API.post('/auction_bid', { auc_id, bid_price }),
  pvpList: () => API.get('/pvp_list'),
  startPvp: (opp_id) => API.post('/start_pvp', { opp_id }),
  startSectWar: () => API.post('/start_sect_war', {}),
  joinSectWar: () => API.post('/join_sect_war', {}),
  // 角色创建
  characterStatus: () => API.get('/character_status'),
  createCharacter: (name, spiritual_root, start_technique) => API.post('/create_character', { name, spiritual_root, start_technique }),
  // 采药小游戏
  gatherHerbStart: (resource_id) => API.post('/gather_herb_start', { resource_id }),
  gatherHerbComplete: (resource_id, timing_score) => API.post('/gather_herb_complete', { resource_id, timing_score }),
  // 突破小游戏
  breakthroughMinigameStart: (method) => API.post('/breakthrough_minigame_start', { method }),
  breakthroughMinigameComplete: (method, scores) => API.post('/breakthrough_minigame_complete', { method, scores }),
  // 拍卖刷新
  refreshAuction: () => API.post('/refresh_auction', {})
};
