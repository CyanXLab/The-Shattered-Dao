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
  reset: () => API.post('/reset', {})
};
