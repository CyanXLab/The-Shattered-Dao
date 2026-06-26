"""
《逆仙录·天道残卷》核心游戏引擎
- 真实身体系统（经脉/丹田/肉身/神识/状态）
- 真实修炼系统（地点/周天/丹药/阵法/瓶颈/突破）
- 策略战斗系统（情报/瞄准/灵气分配/部位伤害）
- 因果/业力系统（因果账本/心魔/天劫/转世）
- 多维社交系统（信任/尊重/感情/利益/畏惧）
- 真实经济系统（灵石分级/通货膨胀/以物易物）
- 寿命/时间系统（年龄阶段/延寿手段/世界变化）
- 种田/家园/储物空间
- 宠物/道侣/同伴
"""
import json
import os
import time
import random
import math
from data_loader import (
    get_realms, get_realm, get_realm_index, get_next_realm,
    get_realm_name, get_realm_lifespan,
    get_materials, get_material, get_techniques, get_technique,
    get_pill_recipes, get_pill_recipe, get_beasts, get_beast,
    get_regions, get_region, get_npcs_config, get_npc_config,
    get_sects, get_sect, get_storylines, get_causal_chains,
    MERIDIANS, ORGANS, ATTR_NAMES, ELEMENT_COUNTERS, LIFESPAN_STAGES
)
from user_system import save_player_state, load_player_state
from engine_ext import EngineExtension


class GameEngine(EngineExtension):
    def __init__(self, user_id=None, username=""):
        self.user_id = user_id
        self.username = username
        self.state = None
        self.last_tick = time.time()
        self.load_state()

    # ==================== 存档系统 ====================
    def load_state(self):
        if self.user_id:
            saved = load_player_state(self.user_id)
            if saved:
                self.state = json.loads(saved)
                return
        self.state = self._new_game()
        self.save_state()

    def save_state(self):
        if self.user_id:
            save_player_state(self.user_id, json.dumps(self.state, ensure_ascii=False))

    def _new_game(self):
        """新建游戏"""
        state = {
            "player": self._init_player(),
            "world": self._init_world(),
            "log": [],
            "flags": {},
            "version": 2
        }
        self._log(state, "你醒来时，手中握着一块温润的玉简——逆道玉简。它似乎在低语：天道有缺，万物皆可逆。")
        self._log(state, "你身处青云宗山门前。师尊说，从此刻起，你便是青云宗的记名弟子。寿元一百二十载，已是倒计时。")
        return state

    def _init_player(self):
        """初始化玩家 - 包含真实身体系统"""
        return {
            "name": "陈平安",
            "realm": "qi_refining_1",
            "realm_progress": 0.0,
            "comprehension": 10,  # 悟性
            "age": 16,
            "lifespan": 120,
            # 真实身体系统
            "body": {
                "meridians": {m: {"integrity": 100, "blocked": False, "qi_flow": 100} for m in MERIDIANS},
                "dantian": {"capacity": 200, "current": 50, "quality": "impure", "cracks": 0},
                "flesh": {
                    "skin": {"toughness": 10, "regeneration": 5},
                    "muscle": {"strength": 15, "endurance": 20},
                    "bone": {"density": 12, "spiritual_marrow": False},
                    "organs": {o: {"health": 100, "affinity": 5} for o in ORGANS}
                },
                "spirit": {"range": 10, "sharpness": 15, "resilience": 20, "soul_fragments": 0},
                "conditions": []
            },
            # 兼容旧系统的HP/QI
            "hp": 80, "max_hp": 80,
            "qi": 50, "max_qi": 200,
            "attack": 8, "defense": 3, "speed": 12,
            "spiritual_root": "pseudo",  # pseudo/false/true/heavenly
            "techniques": [],
            "active_technique": None,
            "attributes": {
                "wood_affinity": 5, "fire_affinity": 0, "ice_affinity": 0,
                "metal_affinity": 0, "earth_affinity": 0, "wind_affinity": 0,
                "thunder_affinity": 0, "light_affinity": 0, "dark_affinity": 0,
                "void_affinity": 0, "water_affinity": 0, "soul_affinity": 0,
                "meridian_strain": 0, "fire_poison": 0, "cold_damage": 0
            },
            # 储物空间（多级储物戒）
            "inventory": [
                {"item_id": "reverse_jade", "qty": 1},
                {"item_id": "spirit_stone_low", "qty": 100},
                {"item_id": "wood_slip", "qty": 1},
                {"item_id": "qi_pill", "qty": 3},
                {"item_id": "flesh_renew_pill", "qty": 2},
                {"item_id": "iron_sword", "qty": 1},
                {"item_id": "cloth_armor", "qty": 1}
            ],
            "equipped": {"weapon": None, "armor": None, "talisman": None},
            "x": 32, "y": 8,
            "region": "qingyun_sect",
            # 因果/业力
            "karma": 0,
            "karma_ledger": [],
            "reputation": 0,  # 声望
            # 经济
            "spirit_stones": {"low": 100, "mid": 0, "high": 0, "top": 0},
            # 社交关系
            "relationships": {},
            # 统计
            "kills": 0, "pills_crafted": 0, "trees_cut": 0, "mortal_helped": False,
            # 宠物/道侣/同伴
            "pets": [], "dao_companion": None, "companions": [],
            # 家园/种田
            "home": None, "farm_plots": [],
            # 宗门
            "sect": None, "sect_position": None,
            # 战斗
            "in_combat": False, "combat_target": None,
            "buffs": [],
            # 剧情
            "story_progress": {},
            "completed_quests": []
        }

    def _init_world(self):
        """初始化世界"""
        world = {
            "game_time": 0, "day": 1, "hour": 6, "minute": 0,
            "npcs": [], "resources": [], "beasts": [],
            "events": [], "active_chains": [], "triggered_chains": [],
            "market_prices": {},  # 动态市场价格
            "world_events": []  # 世界级事件
        }
        # 初始化NPC
        for npc_cfg in get_npcs_config():
            world["npcs"].append({
                "id": npc_cfg["id"],
                "x": npc_cfg["x"], "y": npc_cfg["y"],
                "home_x": npc_cfg["x"], "home_y": npc_cfg["y"],
                "region": npc_cfg["region"],
                "relationship": npc_cfg.get("relationship", 0),
                "emotional_state": npc_cfg.get("emotional_state", {}),
                "dimensions": {"trust": npc_cfg.get("relationship", 0), "respect": 30, "affection": 0, "interest": 50, "fear": 0},
                "alive": True, "current_action": "idle", "last_speak": ""
            })
        # 初始化资源与妖兽
        for region in get_regions():
            tiles = region.get("buildings", [])
            for res in region.get("resources", []):
                world["resources"].append({
                    "id": res["id"], "region": region["id"],
                    "x": res["x"], "y": res["y"], "type": res["type"],
                    "item": res["item"], "respawn": res["respawn"],
                    "available": True, "respawn_at": 0
                })
            for beast in region.get("beast_spawns", []):
                world["beasts"].append({
                    "id": f"beast_{region['id']}_{beast['x']}_{beast['y']}",
                    "region": region["id"],
                    "x": beast["x"], "y": beast["y"],
                    "home_x": beast["x"], "home_y": beast["y"],
                    "beast_id": beast["beast"], "respawn": beast["respawn"],
                    "alive": True, "hp": 0, "respawn_at": 0
                })
        # 初始化市场价格
        for m in get_materials():
            world["market_prices"][m["id"]] = m["value"]
        return world

    def _log(self, state, msg, level="info"):
        if state is None:
            state = self.state
        log = state["log"]
        log.append({"t": state["world"]["game_time"], "msg": msg, "level": level})
        if len(log) > 200:
            state["log"] = log[-200:]

    # ==================== 时间系统 ====================
    REAL_SEC_TO_GAME_MIN = 1.0
    TICK_INTERVAL = 1.0

    def tick(self):
        now = time.time()
        if now - self.last_tick < self.TICK_INTERVAL:
            return
        elapsed = now - self.last_tick
        self.last_tick = now
        minutes = max(1, int(elapsed * self.REAL_SEC_TO_GAME_MIN))
        self._advance_time(minutes)

    def _advance_time(self, minutes):
        w = self.state["world"]
        w["game_time"] += minutes
        total = w["game_time"]
        w["day"] = total // (24 * 60) + 1
        rem = total % (24 * 60)
        w["hour"] = rem // 60
        w["minute"] = rem % 60
        p = self.state["player"]
        days_pass = minutes / (24 * 60)
        p["age"] += days_pass / 365
        # 寿元消耗（更慢，更真实）
        p["lifespan"] -= days_pass
        # HP/QI自然恢复（根据年龄阶段）
        if not p["in_combat"]:
            stage = self._get_lifespan_stage()
            recov_bonus = 1 + stage.get("recovery_bonus", 0)
            p["hp"] = min(p["max_hp"], p["hp"] + int(minutes * 0.3 * recov_bonus))
            p["qi"] = min(p["max_qi"], p["qi"] + int(minutes * 0.5 * recov_bonus))
        # NPC行为
        self._update_npcs(minutes)
        # 资源/妖兽重生
        self._update_resources(minutes)
        self._update_beasts(minutes)
        # 因果链
        self._check_causal_chains()
        # 市场价格波动
        if random.random() < 0.01:
            self._update_market_prices()
        # 寿元检查
        if p["lifespan"] <= 0:
            self._log(None, "寿元已尽，你坐化了。游戏结束。", "death")
            p["lifespan"] = 0
            p["hp"] = 0
        if w["game_time"] % 60 == 0:
            self.save_state()
        # 剧情触发检查
        self.check_story_triggers()

    def _get_lifespan_stage(self):
        p = self.state["player"]
        age_ratio = p["age"] / max(1, p["lifespan"])
        if age_ratio < 0.25:
            return LIFESPAN_STAGES["youth"]
        elif age_ratio < 0.66:
            return LIFESPAN_STAGES["prime"]
        elif age_ratio < 0.92:
            return LIFESPAN_STAGES["decline"]
        return LIFESPAN_STAGES["desperate"]

    def _update_npcs(self, minutes):
        w = self.state["world"]
        for npc in w["npcs"]:
            if not npc["alive"]:
                continue
            cfg = get_npc_config(npc["id"])
            if not cfg:
                continue
            schedule = cfg.get("schedule", {})
            cur_hour = w["hour"]
            action = "idle"
            for t, a in sorted(schedule.items()):
                th, tm = map(int, t.split(":"))
                if cur_hour > th or (cur_hour == th and w["minute"] >= tm):
                    action = a
            npc["current_action"] = action
            self._npc_act(npc, cfg, action, minutes)

    def _npc_act(self, npc, cfg, action, minutes):
        region = get_region(npc["region"])
        if not region:
            return
        buildings = region.get("buildings", [])
        target = None
        if action in ("cultivate", "morning_cultivation", "evening_cultivation", "meditate", "rest", "wake_up", "sleep"):
            target = self._find_building(buildings, "dormitory")
        elif action in ("audience", "teach", "court"):
            target = self._find_building(buildings, "main_hall") or self._find_building(buildings, "palace")
        elif action == "alchemy":
            target = self._find_building(buildings, "alchemy_room")
        elif action in ("forge", "prepare"):
            target = self._find_building(buildings, "forge_room")
        elif action in ("library", "study"):
            target = self._find_building(buildings, "scripture_pavilion")
        elif action in ("market", "wander", "open_shop", "close_shop"):
            target = self._find_building(buildings, "gate") or self._find_building(buildings, "gate_n")
        elif action == "meal":
            target = self._find_building(buildings, "tavern") or self._find_building(buildings, "dormitory")
        elif action in ("hunt", "gather_herb", "patrol", "farm"):
            target = None
        elif action == "camp":
            target = self._find_building(buildings, "hunter_camp")
        elif action == "hide":
            target = self._find_building(buildings, "deep_cave")
        if target:
            tx = target["x"] + target["w"] // 2
            ty = target["y"] + target["h"] // 2
            self._move_npc_toward(npc, tx, ty, minutes)
        else:
            hx, hy = npc["home_x"], npc["home_y"]
            if random.random() < 0.3 * minutes:
                npc["x"] = max(1, min(region["width"]-2, hx + random.randint(-3, 3)))
                npc["y"] = max(1, min(region["height"]-2, hy + random.randint(-3, 3)))

    def _find_building(self, buildings, *keywords):
        for b in buildings:
            for kw in keywords:
                if kw in b.get("id", "") or kw in b.get("function", ""):
                    return b
        return None

    def _move_npc_toward(self, npc, tx, ty, minutes):
        speed = 2
        steps = max(1, int(speed * minutes / 5))
        for _ in range(steps):
            if abs(npc["x"] - tx) <= 1 and abs(npc["y"] - ty) <= 1:
                break
            if npc["x"] < tx: npc["x"] += 1
            elif npc["x"] > tx: npc["x"] -= 1
            if npc["y"] < ty: npc["y"] += 1
            elif npc["y"] > ty: npc["y"] -= 1

    def _update_resources(self, minutes):
        w = self.state["world"]
        for res in w["resources"]:
            if not res["available"] and w["game_time"] >= res["respawn_at"]:
                res["available"] = True

    def _update_beasts(self, minutes):
        w = self.state["world"]
        for beast in w["beasts"]:
            if not beast["alive"] and w["game_time"] >= beast["respawn_at"]:
                beast["alive"] = True
                beast["hp"] = 0
                beast["x"] = beast["home_x"]
                beast["y"] = beast["home_y"]
            elif beast["alive"] and minutes >= 5 and random.random() < 0.15:
                region = get_region(beast["region"])
                if region:
                    beast["x"] = max(1, min(region["width"]-2, beast["home_x"] + random.randint(-2, 2)))
                    beast["y"] = max(1, min(region["height"]-2, beast["home_y"] + random.randint(-2, 2)))

    def _update_market_prices(self):
        """市场价格波动（±10%）"""
        w = self.state["world"]
        for mid in list(w["market_prices"].keys()):
            m = get_material(mid)
            if m:
                base = m["value"]
                fluctuation = random.uniform(-0.1, 0.1)
                w["market_prices"][mid] = max(1, int(base * (1 + fluctuation)))

    # ==================== 因果链 ====================
    def _check_causal_chains(self):
        w = self.state["world"]
        p = self.state["player"]
        for chain in get_causal_chains():
            if chain["id"] in w["triggered_chains"]:
                continue
            if self._match_trigger(chain["trigger"]):
                w["triggered_chains"].append(chain["id"])
                self._trigger_chain_step(chain, 0)
                self._log(None, f"【事件链触发】{chain['name']}", "event")

    def _match_trigger(self, trigger):
        p = self.state["player"]
        if trigger == "player_kills_sect_member":
            return p.get("killed_sect_member", False)
        if trigger == "player_crafts_rare_pill":
            return p["pills_crafted"] >= 5
        if trigger == "player_kills_weak_npc":
            return p.get("killed_weak_npc", False)
        if trigger == "player_helps_mortal":
            return p["mortal_helped"]
        if trigger == "player_cuts_many_trees":
            return p["trees_cut"] >= 10
        if trigger == "player_crafts_100_pills":
            return p["pills_crafted"] >= 100
        if trigger == "player_kills_50_beasts":
            return p["kills"] >= 50
        if trigger == "player_has_reverse_jade_visible":
            return p["age"] > 18
        if trigger == "player_breakthrough_foundation":
            return p["realm"].startswith("foundation")
        if trigger == "player_lifespan_below_20":
            return p["lifespan"] <= 20
        return False

    def _trigger_chain_step(self, chain, idx):
        if idx >= len(chain["steps"]):
            return
        step = chain["steps"][idx]
        log_msg = step.get("log", "")
        if log_msg:
            self._log(None, log_msg, "event")
        effect = step.get("effect", "")
        for kv in effect.split(","):
            kv = kv.strip()
            if "=" in kv:
                k, v = kv.split("=", 1)
                k, v = k.strip(), v.strip()
                if k == "sect_relation":
                    self.state["flags"]["sect_relation"] = int(v)
                elif k == "bounty_posted" and v == "true":
                    self.state["flags"]["bounty_posted"] = True

    # ==================== 因果/业力系统 ====================
    def add_karma(self, weight, event, karma_type="neutral", realm="mortal"):
        """添加因果记录"""
        p = self.state["player"]
        p["karma"] += weight
        p["karma_ledger"].append({
            "event": event, "weight": weight, "type": karma_type,
            "realm": realm, "time": self.state["world"]["game_time"]
        })
        # 业力影响
        if weight < -100:
            self._log(None, f"业力大损：{event}（{weight}）", "warn")
        elif weight > 50:
            self._log(None, f"善业累积：{event}（+{weight}）", "info")

    # ==================== 库存系统 ====================
    def _add_item(self, item_id, qty=1):
        p = self.state["player"]
        for inv in p["inventory"]:
            if inv["item_id"] == item_id:
                inv["qty"] += qty
                return
        p["inventory"].append({"item_id": item_id, "qty": qty})

    def _remove_item(self, item_id, qty=1):
        p = self.state["player"]
        for inv in p["inventory"]:
            if inv["item_id"] == item_id:
                if inv["qty"] < qty:
                    return False
                inv["qty"] -= qty
                if inv["qty"] <= 0:
                    p["inventory"].remove(inv)
                return True
        return False

    def _has_item(self, item_id, qty=1):
        p = self.state["player"]
        for inv in p["inventory"]:
            if inv["item_id"] == item_id and inv["qty"] >= qty:
                return True
        return False

    def _count_item(self, item_id):
        p = self.state["player"]
        for inv in p["inventory"]:
            if inv["item_id"] == item_id:
                return inv["qty"]
        return 0

    # ==================== 灵石系统（分级） ====================
    def get_spirit_stones_value(self):
        """获取灵石总价值（以下品为单位）"""
        s = self.state["player"]["spirit_stones"]
        return s["low"] + s["mid"] * 100 + s["high"] * 10000 + s["top"] * 1000000

    def spend_spirit_stones(self, amount):
        """消耗灵石（自动从低到高）"""
        p = self.state["player"]
        s = p["spirit_stones"]
        total = self.get_spirit_stones_value()
        if total < amount:
            return False
        # 先用下品
        use_low = min(s["low"], amount)
        s["low"] -= use_low
        amount -= use_low
        # 兑换中品
        while amount > 0 and s["mid"] > 0:
            s["mid"] -= 1
            s["low"] += 100
            use_low = min(s["low"], amount)
            s["low"] -= use_low
            amount -= use_low
        # 兑换上品
        while amount > 0 and s["high"] > 0:
            s["high"] -= 1
            s["mid"] += 100
            use_low = min(s["low"], amount)
            s["low"] -= use_low
            amount -= use_low
            while amount > 0 and s["mid"] > 0:
                s["mid"] -= 1
                s["low"] += 100
                use_low = min(s["low"], amount)
                s["low"] -= use_low
                amount -= use_low
        # 极品
        while amount > 0 and s["top"] > 0:
            s["top"] -= 1
            s["high"] += 100
            # 递归处理
            return self.spend_spirit_stones(amount)
        return amount == 0

    def add_spirit_stones(self, amount):
        """增加灵石（自动归为下品）"""
        self.state["player"]["spirit_stones"]["low"] += amount

    # ==================== 真实修炼系统 ====================
    def cultivate(self, hours=1, location="sect", cycles=3, use_pill=None, use_formation=None):
        """修炼
        hours: 修炼时长
        location: 修炼地点（影响灵气浓度）
        cycles: 周天数（影响效率与风险）
        use_pill: 辅助丹药ID
        use_formation: 阵法ID
        """
        p = self.state["player"]
        if p["in_combat"]:
            return {"ok": False, "msg": "战斗中无法修炼"}
        if not p["active_technique"]:
            return {"ok": False, "msg": "未激活功法，无法修炼。请先学习功法。"}
        tech = get_technique(p["active_technique"])
        if not tech:
            return {"ok": False, "msg": "功法不存在"}
        # 找当前阶段
        realm_idx = get_realm_index(p["realm"])
        cur_stage = None
        cur_stage_idx = -1
        for i, stage in enumerate(tech["stages"]):
            stage_realm_idx = get_realm_index(stage["realm_required"])
            if realm_idx >= stage_realm_idx:
                cur_stage = stage
                cur_stage_idx = i
        if cur_stage is None:
            return {"ok": False, "msg": "境界不足"}
        # 是否逆修
        reversed_stages = p.get("reversed_stages", {})
        is_reversed = reversed_stages.get(p["active_technique"], {}).get(cur_stage_idx, False)
        # 修炼速度
        base_speed = 0.5 * tech["completeness"]
        if is_reversed:
            base_speed *= 1.2
        if p["spiritual_root"] == "pseudo":
            base_speed *= 0.6
        # 地点加成
        location_bonus = 1.0
        region = get_region(p["region"])
        if region:
            location_bonus *= region["spirit_density"]
        if location == "spirit_vein":
            location_bonus *= 1.5
        elif location == "void":
            location_bonus *= 0.5
        # 周天加成（每多一圈+10%，但风险增加）
        cycle_bonus = 1.0 + (cycles - 1) * 0.1
        # 丹药加成
        pill_bonus = 1.0
        if use_pill:
            if not self._has_item(use_pill):
                return {"ok": False, "msg": "无此丹药"}
            m = get_material(use_pill)
            if m and m.get("effect", {}).get("cultivate_bonus"):
                pill_bonus += m["effect"]["cultivate_bonus"]
                self._remove_item(use_pill, 1)
        # 阵法加成
        formation_bonus = 1.0
        if use_formation:
            formation_bonus *= 1.3
        # 年龄阶段加成
        stage_info = self._get_lifespan_stage()
        age_bonus = 1.0 + stage_info.get("cultivate_bonus", 0)
        # 计算进度
        progress_gain = base_speed * cycle_bonus * location_bonus * pill_bonus * formation_bonus * age_bonus * hours / 10.0
        p["realm_progress"] += progress_gain
        # 属性增加
        eff = cur_stage.get("effect", {})
        for k, v in eff.items():
            if k == "qi_capacity":
                p["max_qi"] += int(v * hours * 0.1)
                p["body"]["dantian"]["capacity"] += int(v * hours * 0.1)
            elif k in p["attributes"]:
                p["attributes"][k] += v * hours * 0.05
        # 经脉负担
        defect = cur_stage.get("defect", {})
        meridian_stress = cycles * 2
        if not is_reversed:
            for k, v in defect.items():
                if k == "meridian_strain":
                    p["attributes"]["meridian_strain"] += v * hours
                    # 经脉损伤累积
                    for m in p["body"]["meridians"]:
                        if random.random() < 0.1:
                            p["body"]["meridians"][m]["integrity"] = max(0, p["body"]["meridians"][m]["integrity"] - v * hours * 10)
                elif k == "fire_poison":
                    p["attributes"]["fire_poison"] += v * hours
                    p["body"]["meridians"]["督脉"]["blocked"] = "fire_toxin"
                elif k == "cold_damage":
                    p["attributes"]["cold_damage"] += v * hours
        # 走火入魔风险
        qi_deviation_risk = 0
        if meridian_stress > 50:
            qi_deviation_risk = (meridian_stress - 50) / 100
        if stage_info.get("qi_deviation_risk"):
            qi_deviation_risk *= stage_info["qi_deviation_risk"]
        # 业力影响心魔
        if p["karma"] < -500:
            qi_deviation_risk += 0.2
        if random.random() < qi_deviation_risk:
            self._log(None, "走火入魔！修为倒退，HP受损！", "warn")
            p["realm_progress"] = max(0, p["realm_progress"] - 0.2)
            p["hp"] = max(1, p["hp"] - int(p["max_hp"] * 0.3))
            for m in p["body"]["meridians"]:
                p["body"]["meridians"][m]["integrity"] = max(0, p["body"]["meridians"][m]["integrity"] - 10)
            self._advance_time(int(hours * 60))
            return {"ok": False, "msg": "走火入魔！修为倒退，HP受损"}
        # 悟性提升
        comp_gain = random.uniform(0, 2) * hours
        p["comprehension"] += comp_gain
        # QI消耗
        p["qi"] = max(0, p["qi"] - int(hours * 10))
        # 推进时间
        self._advance_time(int(hours * 60))
        msg = f"修炼{hours}小时，进度+{progress_gain*100:.1f}%，悟性+{comp_gain:.1f}"
        if is_reversed:
            msg += "（逆修加持）"
        if meridian_stress > 30:
            msg += "，经脉隐隐作痛"
            p["hp"] = max(1, p["hp"] - int(hours * 1))
        self._log(None, msg, "cultivate")
        if p["realm_progress"] >= 1.0:
            return {"ok": True, "msg": msg + "\n境界圆满，可尝试突破！", "can_breakthrough": True}
        return {"ok": True, "msg": msg, "progress": p["realm_progress"]}

    def try_breakthrough(self, method="water_grind"):
        """尝试突破
        method: water_grind(水磨工夫) / pill(破境丹) / life_death_battle(生死战) / comprehension(顿悟)
        """
        p = self.state["player"]
        next_realm = get_next_realm(p["realm"])
        if not next_realm:
            p["realm_progress"] = 1.0
            return {"ok": False, "msg": "已达境界上限"}
        # 基础成功率
        base_rate = 0.7
        if p["spiritual_root"] == "pseudo":
            base_rate = 0.4
        # 突破方式
        method_config = {
            "water_grind": {"rate_bonus": 0, "risk": 0.05, "time_cost": 365 * 24 * 60, "desc": "水磨工夫，需1年"},
            "pill": {"rate_bonus": 0.3, "risk": 0.2, "time_cost": 24 * 60, "desc": "破境丹辅助"},
            "life_death_battle": {"rate_bonus": 0.4, "risk": 0.5, "time_cost": 60, "desc": "生死战中突破"},
            "comprehension": {"rate_bonus": 0.5, "risk": 0, "time_cost": 0, "desc": "顿悟，需悟性100+"}
        }
        mc = method_config.get(method, method_config["water_grind"])
        # 顿悟需要悟性
        if method == "comprehension" and p["comprehension"] < 100:
            return {"ok": False, "msg": "悟性不足，无法顿悟"}
        # 破境丹消耗
        if method == "pill":
            pill_id = "foundation_pill" if next_realm["id"].startswith("foundation") else \
                      "golden_core_pill" if next_realm["id"].startswith("golden_core") else None
            if pill_id and not self._has_item(pill_id):
                return {"ok": False, "msg": "无破境丹"}
            if pill_id:
                self._remove_item(pill_id, 1)
        # 丹田品质要求
        if p["body"]["dantian"]["quality"] == "impure" and next_realm["id"].startswith("golden_core"):
            base_rate -= 0.3
        # 经脉损伤减成
        avg_meridian = sum(m["integrity"] for m in p["body"]["meridians"].values()) / len(p["body"]["meridians"])
        if avg_meridian < 70:
            base_rate -= 0.2
        # 业力影响心魔
        heart_devil_prob = 0
        if p["karma"] < -500:
            heart_devil_prob = 0.5
            self._log(None, "业力深重，突破时心魔入侵！", "warn")
        # 最终成功率
        final_rate = min(0.95, base_rate + mc["rate_bonus"])
        # 心魔考验
        if random.random() < heart_devil_prob:
            self._log(None, "心魔考验！回想你做过的亏心事...", "event")
            # 玩家可选择坚持道心或被心魔吞噬（简化为50%概率）
            if random.random() < 0.5:
                self._log(None, "你战胜了心魔！", "info")
            else:
                self._log(None, "心魔入侵，突破失败，修为倒退！", "warn")
                p["realm_progress"] = 0.1
                self._advance_time(mc["time_cost"])
                return {"ok": False, "msg": "心魔入侵，突破失败"}
        # 推进时间
        if mc["time_cost"] > 0:
            self._advance_time(mc["time_cost"])
        # 突破
        if random.random() < final_rate:
            old_realm = p["realm"]
            p["realm"] = next_realm["id"]
            p["realm_progress"] = 0.0
            p["max_hp"] = int(p["max_hp"] * 1.5)
            p["hp"] = p["max_hp"]
            p["max_qi"] = int(p["max_qi"] * 1.5)
            p["qi"] = p["max_qi"]
            p["body"]["dantian"]["capacity"] = int(p["body"]["dantian"]["capacity"] * 1.5)
            p["lifespan"] = max(p["lifespan"], next_realm["lifespan"])
            self._log(None, f"突破成功！现在境界：{next_realm['name']}，寿元上限：{next_realm['lifespan']}年", "breakthrough")
            # 因果：突破成功 +10 业力
            self.add_karma(10, "突破成功", "cultivation")
            return {"ok": True, "msg": f"突破成功！现在境界：{next_realm['name']}", "breakthrough": True}
        else:
            p["realm_progress"] = 0.3
            p["hp"] = max(1, p["hp"] - int(p["max_hp"] * mc["risk"]))
            if mc["risk"] > 0.3:
                # 经脉损伤
                for m in p["body"]["meridians"]:
                    p["body"]["meridians"][m]["integrity"] = max(0, p["body"]["meridians"][m]["integrity"] - 20)
                self._log(None, "突破失败！经脉受损！", "warn")
            self._log(None, "突破失败！", "warn")
            return {"ok": False, "msg": "突破失败！HP受损"}

    # ==================== 移动 ====================
    def move_player(self, direction):
        p = self.state["player"]
        if p["in_combat"]:
            return {"ok": False, "msg": "战斗中无法移动！"}
        if p["hp"] <= 0:
            return {"ok": False, "msg": "你已死亡。"}
        region = get_region(p["region"])
        if not region:
            return {"ok": False, "msg": "未知区域"}
        nx, ny = p["x"], p["y"]
        if direction == "up": ny -= 1
        elif direction == "down": ny += 1
        elif direction == "left": nx -= 1
        elif direction == "right": nx += 1
        else: return {"ok": False, "msg": "无效方向"}
        if nx < 0 or nx >= region["width"] or ny < 0 or ny >= region["height"]:
            return {"ok": False, "msg": "边界外"}
        for b in region.get("buildings", []):
            if b["x"] <= nx < b["x"]+b["w"] and b["y"] <= ny < b["y"]+b["h"]:
                return self._enter_building(b)
        p["x"], p["y"] = nx, ny
        for ex in region.get("exits", []):
            if ex["x"] == nx and ex["y"] == ny:
                return self._change_region(ex["target"], ex["tx"], ex["ty"])
        for res in self.state["world"]["resources"]:
            if res["region"] == p["region"] and res["x"] == nx and res["y"] == ny and res["available"]:
                m = get_material(res["item"])
                name = m["name"] if m else res["item"]
                return {"ok": True, "msg": f"发现{name}，可采集", "action": "gather", "resource_id": res["id"]}
        for beast in self.state["world"]["beasts"]:
            if beast["alive"] and beast["region"] == p["region"] and beast["x"] == nx and beast["y"] == ny:
                return self._start_combat(beast)
        for npc in self.state["world"]["npcs"]:
            if npc["alive"] and npc["region"] == p["region"] and npc["x"] == nx and npc["y"] == ny:
                cfg = get_npc_config(npc["id"])
                return {"ok": True, "msg": f"遇到{cfg['name']}", "action": "talk", "npc_id": npc["id"]}
        self._advance_time_for_move(1)
        return {"ok": True, "msg": ""}

    def move_player_to(self, x, y):
        p = self.state["player"]
        if p["in_combat"]:
            return {"ok": False, "msg": "战斗中无法移动！"}
        if p["hp"] <= 0:
            return {"ok": False, "msg": "你已死亡。"}
        region = get_region(p["region"])
        if not region:
            return {"ok": False, "msg": "未知区域"}
        if x < 0 or x >= region["width"] or y < 0 or y >= region["height"]:
            return {"ok": False, "msg": "边界外"}
        # 追踪妖兽
        clicked_beast = None
        for b in self.state["world"]["beasts"]:
            if b["alive"] and b["region"] == p["region"] and b["x"] == x and b["y"] == y:
                clicked_beast = b
                break
        target_x, target_y = x, y
        if clicked_beast:
            target_x, target_y = clicked_beast["x"], clicked_beast["y"]
        if p["x"] == target_x and p["y"] == target_y:
            for beast in self.state["world"]["beasts"]:
                if beast["alive"] and beast["region"] == p["region"] and beast["x"] == p["x"] and beast["y"] == p["y"]:
                    return self._start_combat(beast)
            return {"ok": True, "msg": "已在此处"}
        steps = 0
        while (p["x"] != target_x or p["y"] != target_y) and steps < 30:
            steps += 1
            if clicked_beast and clicked_beast["alive"]:
                target_x, target_y = clicked_beast["x"], clicked_beast["y"]
            if p["x"] < target_x: p["x"] += 1
            elif p["x"] > target_x: p["x"] -= 1
            elif p["y"] < target_y: p["y"] += 1
            elif p["y"] > target_y: p["y"] -= 1
            for b in region.get("buildings", []):
                if b["x"] <= p["x"] < b["x"]+b["w"] and b["y"] <= p["y"] < b["y"]+b["h"]:
                    result = self._enter_building(b)
                    if result.get("action"):
                        return result
                    break
            for ex in region.get("exits", []):
                if ex["x"] == p["x"] and ex["y"] == p["y"]:
                    return self._change_region(ex["target"], ex["tx"], ex["ty"])
            for res in self.state["world"]["resources"]:
                if res["region"] == p["region"] and res["x"] == p["x"] and res["y"] == p["y"] and res["available"]:
                    m = get_material(res["item"])
                    name = m["name"] if m else res["item"]
                    return {"ok": True, "msg": f"发现{name}，可采集", "action": "gather", "resource_id": res["id"]}
            for beast in self.state["world"]["beasts"]:
                if beast["alive"] and beast["region"] == p["region"] and beast["x"] == p["x"] and beast["y"] == p["y"]:
                    return self._start_combat(beast)
            for npc in self.state["world"]["npcs"]:
                if npc["alive"] and npc["region"] == p["region"] and npc["x"] == p["x"] and npc["y"] == p["y"]:
                    cfg = get_npc_config(npc["id"])
                    return {"ok": True, "msg": f"遇到{cfg['name']}", "action": "talk", "npc_id": npc["id"]}
            self._advance_time_for_move(1)
        for beast in self.state["world"]["beasts"]:
            if beast["alive"] and beast["region"] == p["region"] and beast["x"] == p["x"] and beast["y"] == p["y"]:
                return self._start_combat(beast)
        return {"ok": True, "msg": f"到达({p['x']},{p['y']})"}

    def _advance_time_for_move(self, minutes):
        """移动专用时间推进（不让妖兽移动）"""
        w = self.state["world"]
        w["game_time"] += minutes
        total = w["game_time"]
        w["day"] = total // (24 * 60) + 1
        rem = total % (24 * 60)
        w["hour"] = rem // 60
        w["minute"] = rem % 60
        p = self.state["player"]
        days_pass = minutes / (24 * 60)
        p["age"] += days_pass / 365
        p["lifespan"] -= days_pass
        if not p["in_combat"]:
            p["hp"] = min(p["max_hp"], p["hp"] + int(minutes * 0.3))
            p["qi"] = min(p["max_qi"], p["qi"] + int(minutes * 0.5))
        self._update_npcs(minutes)
        self._update_resources(minutes)

    def _enter_building(self, building):
        func = building.get("function", "")
        p = self.state["player"]
        self._advance_time(2)
        if func == "alchemy":
            return {"ok": True, "msg": f"进入{building['name']}，可炼丹", "action": "alchemy"}
        if func == "forge":
            return {"ok": True, "msg": f"进入{building['name']}，可炼器", "action": "forge"}
        if func == "learn":
            return {"ok": True, "msg": f"进入{building['name']}，可学习功法", "action": "learn"}
        if func == "mission":
            return {"ok": True, "msg": f"进入{building['name']}，可接取任务", "action": "mission"}
        if func == "farm":
            return {"ok": True, "msg": f"进入{building['name']}，可种植灵药", "action": "farm"}
        if func == "rest":
            p["hp"] = p["max_hp"]
            p["qi"] = p["max_qi"]
            self._advance_time(60)
            self._log(None, f"在{building['name']}休息一小时，HP/QI已恢复。", "rest")
            return {"ok": True, "msg": f"在{building['name']}休息，HP/QI已恢复"}
        if func and func.startswith("shop_"):
            return {"ok": True, "msg": f"进入{building['name']}", "action": "shop", "shop_type": func[5:]}
        if func == "tavern":
            return {"ok": True, "msg": f"进入{building['name']}", "action": "tavern"}
        if func == "sect_master":
            return {"ok": True, "msg": f"进入{building['name']}", "action": "sect_master"}
        if func == "auction":
            return {"ok": True, "msg": f"进入{building['name']}", "action": "auction"}
        if func == "guild":
            return {"ok": True, "msg": f"进入{building['name']}", "action": "guild"}
        if func and func.startswith("exit_to"):
            return {"ok": True, "msg": f"已抵达{building['name']}"}
        return {"ok": True, "msg": f"进入{building['name']}"}

    def _change_region(self, target_id, tx, ty):
        p = self.state["player"]
        p["region"] = target_id
        p["x"] = tx
        p["y"] = ty
        region = get_region(target_id)
        self._advance_time(30)
        self._log(None, f"进入{region['name']}。{region['description']}", "travel")
        return {"ok": True, "msg": f"进入{region['name']}", "action": "region_change"}

    # ==================== 采集 ====================
    def gather(self, resource_id):
        w = self.state["world"]
        p = self.state["player"]
        for res in w["resources"]:
            if res["id"] == resource_id and res["available"]:
                if res["region"] != p["region"] or abs(res["x"]-p["x"])+abs(res["y"]-p["y"]) > 2:
                    return {"ok": False, "msg": "距离太远"}
                res["available"] = False
                res["respawn_at"] = w["game_time"] + res["respawn"]
                self._add_item(res["item"], 1)
                self._advance_time(5)
                m = get_material(res["item"])
                self._log(None, f"采集到{m['name']}×1", "gather")
                return {"ok": True, "msg": f"采集到{m['name']}×1", "item": res["item"]}
        return {"ok": False, "msg": "无此资源"}

    def cut_tree(self):
        p = self.state["player"]
        region = get_region(p["region"])
        if not region or region["type"] not in ("beast_mountain", "sect"):
            return {"ok": False, "msg": "此处无树可砍"}
        if region["type"] == "beast_mountain" or p["y"] > 30 or p["x"] < 10 or p["x"] > 50:
            self._add_item("wood_block", 1)
            p["trees_cut"] += 1
            self._advance_time(5)
            self._log(None, "砍倒一棵树，获得木材×1", "gather")
            if p["trees_cut"] % 5 == 0:
                self._log(None, "你感到树林中似乎有什么在注视你...", "warn")
            return {"ok": True, "msg": "砍倒一棵树，获得木材×1"}
        return {"ok": False, "msg": "此处无树可砍"}

    # ==================== 学习功法 ====================
    def learn_technique(self, tech_id):
        p = self.state["player"]
        if any(t["id"] == tech_id for t in p["techniques"]):
            return {"ok": False, "msg": "已学习此功法"}
        tech = get_technique(tech_id)
        if not tech:
            return {"ok": False, "msg": "功法不存在"}
        # 检查玉简
        slip_id = None
        for m in get_materials():
            if m.get("type") == "jade_slip" and m.get("teaches") == tech_id:
                slip_id = m["id"]
                break
        if slip_id and self._has_item(slip_id):
            self._remove_item(slip_id, 1)
        else:
            # 在藏经阁可学习基础功法
            if p["region"] != "qingyun_sect":
                return {"ok": False, "msg": "需要功法玉简或前往藏经阁学习"}
        p["techniques"].append({"id": tech_id, "exp": 0})
        if not p["active_technique"]:
            p["active_technique"] = tech_id
        self._advance_time(60)
        self._log(None, f"学会功法：{tech['name']}（{tech['completeness']*100:.0f}%完整度）", "learn")
        return {"ok": True, "msg": f"学会功法：{tech['name']}"}

    def activate_technique(self, tech_id):
        p = self.state["player"]
        if not any(t["id"] == tech_id for t in p["techniques"]):
            return {"ok": False, "msg": "未学习此功法"}
        p["active_technique"] = tech_id
        tech = get_technique(tech_id)
        return {"ok": True, "msg": f"激活功法：{tech['name']}"}

    # ==================== 逆道玉简 ====================
    def reverse_technique(self, tech_id, stage_idx):
        p = self.state["player"]
        if not self._has_item("reverse_jade"):
            return {"ok": False, "msg": "需要逆道玉简"}
        tech = get_technique(tech_id)
        if not tech or stage_idx >= len(tech["stages"]):
            return {"ok": False, "msg": "无效功法或阶段"}
        stage = tech["stages"][stage_idx]
        reversal = stage.get("reversal")
        if not reversal:
            return {"ok": False, "msg": "此阶段无逆修方案"}
        cost = reversal.get("cost", {})
        for item_id, qty in cost.items():
            if not self._has_item(item_id, qty):
                m = get_material(item_id)
                return {"ok": False, "msg": f"需要{m['name'] if m else item_id}×{qty}"}
        for item_id, qty in cost.items():
            self._remove_item(item_id, qty)
        if "reversed_stages" not in p:
            p["reversed_stages"] = {}
        if tech_id not in p["reversed_stages"]:
            p["reversed_stages"][tech_id] = {}
        p["reversed_stages"][tech_id][stage_idx] = True
        # 消除负面
        if "meridian_strain" in stage.get("defect", {}):
            p["attributes"]["meridian_strain"] = max(0, p["attributes"]["meridian_strain"] - 0.5)
            for m in p["body"]["meridians"]:
                p["body"]["meridians"][m]["integrity"] = min(100, p["body"]["meridians"][m]["integrity"] + 20)
        if "fire_poison" in stage.get("defect", {}):
            p["attributes"]["fire_poison"] = max(0, p["attributes"]["fire_poison"] - 0.3)
            p["body"]["meridians"]["督脉"]["blocked"] = False
        self._advance_time(120)
        self._log(None, f"以{reversal['method']}逆转{tech['name']}·{stage['name']}缺陷！{reversal['benefit']}", "reverse")
        # 逆修有业力代价
        self.add_karma(-10, "使用逆道玉简逆修", "cultivation")
        return {"ok": True, "msg": f"逆转成功！{reversal['benefit']}"}

    # ==================== 战斗系统 ====================
    def _start_combat(self, beast_spawn):
        p = self.state["player"]
        if p["hp"] < p["max_hp"] * 0.2:
            return {"ok": False, "msg": "HP过低，不宜战斗！"}
        beast_cfg = get_beast(beast_spawn["beast_id"])
        if not beast_cfg:
            return {"ok": False, "msg": "妖兽不存在"}
        # 境界差距检查：高阶妖兽打低阶玩家是秒杀
        beast_tier = beast_cfg["tier"]
        realm_idx = get_realm_index(p["realm"])
        # 警告
        if beast_tier > 4 and realm_idx < 12:  # 金丹以下遇5阶+
            self._log(None, "此妖兽境界远高于你，请慎重！", "warn")
        beast_spawn["hp"] = beast_cfg["hp"]
        beast_spawn["qi"] = beast_cfg["qi"]
        beast_spawn["cooldowns"] = {}
        p["in_combat"] = True
        p["combat_target"] = beast_spawn["id"]
        self._log(None, f"遭遇{beast_cfg['name']}！战斗开始！", "combat")
        return {
            "ok": True, "msg": f"遭遇{beast_cfg['name']}！",
            "action": "combat",
            "beast": {"name": beast_cfg["name"], "hp": beast_cfg["hp"], "max_hp": beast_cfg["hp"], "tier": beast_cfg["tier"], "element": beast_cfg.get("element", "")}
        }

    def combat_action(self, action, skill_idx=0, target_part="body", qi_allocation=0.5):
        """战斗行动
        action: attack/skill/item/flee
        target_part: body/dantian/head/limb（瞄准部位）
        qi_allocation: 灵气分配比例0-1
        """
        p = self.state["player"]
        if not p["in_combat"]:
            return {"ok": False, "msg": "未在战斗中"}
        beast_spawn = None
        for b in self.state["world"]["beasts"]:
            if b["id"] == p["combat_target"] and b["alive"]:
                beast_spawn = b
                break
        if not beast_spawn:
            p["in_combat"] = False
            return {"ok": False, "msg": "目标已消失"}
        beast_cfg = get_beast(beast_spawn["beast_id"])
        if action == "attack":
            return self._combat_player_attack(beast_spawn, beast_cfg, target_part, qi_allocation)
        elif action == "skill":
            return self._combat_player_skill(beast_spawn, beast_cfg, skill_idx, target_part, qi_allocation)
        elif action == "item":
            return {"ok": True, "msg": "请选择物品", "action": "use_item"}
        elif action == "flee":
            return self._combat_flee(beast_spawn, beast_cfg)
        return {"ok": False, "msg": "无效行动"}

    def _combat_player_attack(self, beast_spawn, beast_cfg, target_part, qi_allocation):
        p = self.state["player"]
        weapon = p["equipped"].get("weapon")
        weapon_dmg = 0
        if weapon:
            wm = get_material(weapon)
            if wm:
                weapon_dmg = wm["attrs"].get("damage", 0)
        base_dmg = p["attack"] + weapon_dmg
        # 灵气加成
        qi_used = int(p["qi"] * qi_allocation * 0.1)
        p["qi"] -= qi_used
        base_dmg += qi_used
        # 功法加成
        tech = None
        if p["active_technique"]:
            tech = get_technique(p["active_technique"])
        if tech:
            element = tech.get("element")
            attr_key = f"{element}_affinity"
            base_dmg += p["attributes"].get(attr_key, 0) * 0.5
        # 暴击
        crit = random.random() < 0.1
        if crit:
            base_dmg *= 1.5
        # 部位瞄准
        part_mult = {"body": 1.0, "head": 1.5, "dantian": 1.3, "limb": 0.8}.get(target_part, 1.0)
        base_dmg *= part_mult
        # 命中判定（神识 vs 速度）
        hit_rate = 0.9 + p["body"]["spirit"]["sharpness"] * 0.001 - beast_cfg["speed"] * 0.005
        if random.random() > hit_rate:
            return self._after_player_action(beast_spawn, beast_cfg, "你攻击落空！")
        dmg = max(1, int(base_dmg - beast_cfg["defense"] * 0.5))
        beast_spawn["hp"] -= dmg
        log = f"你攻击{self._part_name(target_part)}，造成{dmg}点伤害" + ("（暴击！）" if crit else "")
        # 部位效果
        if target_part == "dantian" and beast_spawn["hp"] > 0:
            beast_spawn["qi"] = max(0, beast_spawn["qi"] - 50)
            log += "，妖兽灵气运转不畅"
        elif target_part == "head" and random.random() < 0.2:
            log += "，妖兽短暂眩晕"
        result = self._after_player_action(beast_spawn, beast_cfg, log)
        return result

    def _combat_player_skill(self, beast_spawn, beast_cfg, skill_idx, target_part, qi_allocation):
        p = self.state["player"]
        if not p["active_technique"]:
            return {"ok": False, "msg": "未激活功法"}
        tech = get_technique(p["active_technique"])
        if not tech:
            return {"ok": False, "msg": "功法不存在"}
        skills = tech.get("combat_skills", [])
        if skill_idx >= len(skills):
            return {"ok": False, "msg": "无效技能"}
        skill = skills[skill_idx]
        unlock_realm = skill.get("unlock")
        if unlock_realm and get_realm_index(p["realm"]) < get_realm_index(unlock_realm):
            return {"ok": False, "msg": f"境界不足，需{get_realm_name(unlock_realm)}"}
        cost = int(skill.get("cost", 0) * qi_allocation * 2)
        if p["qi"] < cost:
            return {"ok": False, "msg": f"灵气不足，需要{cost}"}
        p["qi"] -= cost
        element = tech.get("element")
        attr_key = f"{element}_affinity"
        attr_val = p["attributes"].get(attr_key, 0)
        dmg_formula = skill.get("damage", "0")
        try:
            base_dmg = eval(dmg_formula, {"__builtins__": {}}, {attr_key: attr_val, "qi_capacity": p["max_qi"]})
        except:
            base_dmg = attr_val * 2
        # 灵气投入加成
        base_dmg *= (0.5 + qi_allocation)
        crit = random.random() < 0.15
        if crit:
            base_dmg *= 1.5
        # 部位加成
        part_mult = {"body": 1.0, "head": 1.5, "dantian": 1.3, "limb": 0.8}.get(target_part, 1.0)
        base_dmg *= part_mult
        dmg = max(1, int(base_dmg - beast_cfg["defense"] * 0.3))
        beast_spawn["hp"] -= dmg
        log = f"你施展【{skill.get('label', skill.get('name'))}】，造成{dmg}点伤害" + ("（暴击！）" if crit else "")
        # 元素克制
        if self._element_counter(element, beast_cfg.get("element")):
            extra = int(dmg * 0.5)
            beast_spawn["hp"] -= extra
            log += f"，属性克制额外{extra}伤害"
        result = self._after_player_action(beast_spawn, beast_cfg, log)
        return result

    def _part_name(self, part):
        return {"body": "躯体", "head": "头部", "dantian": "丹田", "limb": "肢体"}.get(part, part)

    def _element_counter(self, atk_el, def_el):
        return ELEMENT_COUNTERS.get(atk_el) == def_el

    def _after_player_action(self, beast_spawn, beast_cfg, log):
        p = self.state["player"]
        if beast_spawn["hp"] <= 0:
            return self._combat_victory(beast_spawn, beast_cfg)
        beast_log = self._beast_attack(beast_spawn, beast_cfg)
        if p["hp"] <= 0:
            return self._combat_defeat()
        return {
            "ok": True, "msg": log + "\n" + beast_log, "action": "combat",
            "player": {"hp": p["hp"], "max_hp": p["max_hp"], "qi": p["qi"], "max_qi": p["max_qi"]},
            "beast": {"name": beast_cfg["name"], "hp": max(0, beast_spawn["hp"]), "max_hp": beast_cfg["hp"], "tier": beast_cfg["tier"]}
        }

    def _beast_attack(self, beast_spawn, beast_cfg):
        p = self.state["player"]
        skills = beast_cfg["skills"]
        cooldowns = beast_spawn.setdefault("cooldowns", {})
        usable = []
        for i, s in enumerate(skills):
            if beast_spawn.get("qi", 0) >= s.get("cost", 0):
                cd = s.get("cooldown", 0)
                if cd == 0 or cooldowns.get(i, 0) <= 0:
                    usable.append((i, s))
        if not usable:
            usable = [(0, skills[0])]
        idx, skill = random.choice(usable)
        cd = skill.get("cooldown", 0)
        if cd > 0:
            cooldowns[idx] = cd
        for k in cooldowns:
            cooldowns[k] = max(0, cooldowns[k] - 1)
        beast_spawn["qi"] = beast_spawn.get("qi", 0) - skill.get("cost", 0)
        base_dmg = beast_cfg["attack"] * skill.get("damage_mult", 1.0)
        element = skill.get("element")
        if element:
            attr_key = f"{element}_affinity"
            base_dmg += beast_cfg.get(attr_key, 0) * 0.3
        armor = p["equipped"].get("armor")
        armor_def = 0
        if armor:
            am = get_material(armor)
            if am:
                armor_def = am["attrs"].get("defense", 0)
        dmg = max(1, int(base_dmg - (p["defense"] + armor_def) * 0.5))
        # 抗性
        if element == "fire" and any(b.get("type") == "fire_resist" for b in p.get("buffs", [])):
            dmg = int(dmg * 0.5)
        if element == "ice" and any(b.get("type") == "ice_resist" for b in p.get("buffs", [])):
            dmg = int(dmg * 0.5)
        p["hp"] -= dmg
        log = f"{beast_cfg['name']}施展【{skill['name']}】，对你造成{dmg}点伤害"
        if skill.get("burn"):
            p["buffs"].append({"type": "burn", "duration": 3, "dmg": 5})
            log += "，引燃！"
        if skill.get("poison"):
            p["buffs"].append({"type": "poison", "duration": 3, "dmg": 8})
            log += "，中毒！"
        if skill.get("stun"):
            log += "，但你躲开了！"
        return log

    def _combat_victory(self, beast_spawn, beast_cfg):
        p = self.state["player"]
        p["in_combat"] = False
        p["combat_target"] = None
        beast_spawn["alive"] = False
        beast_spawn["respawn_at"] = self.state["world"]["game_time"] + beast_spawn["respawn"]
        # PVP战斗特殊处理
        if beast_spawn.get("is_pvp"):
            opp = beast_spawn.get("pvp_data", {})
            ss = opp.get("reward_stones", 0)
            exp = opp.get("reward_exp", 0)
            self.add_spirit_stones(ss)
            p["realm_progress"] += exp / 1000.0
            self.add_karma(-30, f"PVP击杀{opp.get('name','')}", "murder")
            self._log(None, f"击败{opp.get('name','')}！获得{ss}灵石，经验+{exp}，业力-30", "victory")
            # 移除临时PVP对象
            if beast_spawn in self.state["world"]["beasts"]:
                self.state["world"]["beasts"].remove(beast_spawn)
            return {"ok": True, "msg": f"击败{opp.get('name','')}！获得{ss}灵石", "action": "victory"}
        drops = []
        for drop in beast_cfg["drops"]:
            if random.random() < drop["prob"]:
                qty = 1
                if "qty" in drop:
                    qty = random.randint(drop["qty"][0], drop["qty"][1])
                self._add_item(drop["item"], qty)
                m = get_material(drop["item"])
                drops.append(f"{m['name']}×{qty}")
        ss_low, ss_high = beast_cfg["spirit_stones"]
        ss = random.randint(ss_low, ss_high)
        self.add_spirit_stones(ss)
        drops.append(f"下品灵石×{ss}")
        exp = beast_cfg["exp"]
        p["realm_progress"] += exp / 1000.0
        p["kills"] += 1
        # 因果：杀妖兽 +5 业力（善）
        self.add_karma(5, f"猎杀{beast_cfg['name']}", "hunt")
        self._advance_time(5)
        msg = f"击败{beast_cfg['name']}！获得：{', '.join(drops)}。经验+{exp}"
        self._log(None, msg, "victory")
        if p["realm_progress"] >= 1.0:
            return {"ok": True, "msg": msg + "\n境界圆满，可尝试突破！", "action": "victory", "drops": drops, "exp": exp, "can_breakthrough": True}
        return {"ok": True, "msg": msg, "action": "victory", "drops": drops, "exp": exp}

    def _combat_defeat(self):
        p = self.state["player"]
        p["in_combat"] = False
        p["combat_target"] = None
        p["hp"] = 1
        # 损失部分物品（非玉简）
        for _ in range(min(3, len(p["inventory"]))):
            if p["inventory"]:
                inv = random.choice(p["inventory"])
                if inv["item_id"] != "reverse_jade":
                    loss_qty = min(inv["qty"], random.randint(1, 3))
                    self._remove_item(inv["item_id"], loss_qty)
        # 寿元损失（重伤）
        p["lifespan"] -= 1
        # 经脉损伤
        for m in p["body"]["meridians"]:
            p["body"]["meridians"][m]["integrity"] = max(0, p["body"]["meridians"][m]["integrity"] - 10)
        region = get_region(p["region"])
        if region:
            for b in region.get("buildings", []):
                if b.get("function") == "rest":
                    p["x"] = b["x"] + b["w"] // 2
                    p["y"] = b["y"] + b["h"] // 2
                    break
        self._advance_time(120)
        self._log(None, "你战败了！同伴将你救回，损失部分物品与1年寿元，经脉受损。", "defeat")
        return {"ok": False, "msg": "战败！损失部分物品与1年寿元，经脉受损"}

    def _combat_flee(self, beast_spawn, beast_cfg):
        p = self.state["player"]
        flee_rate = 0.5 + (p["speed"] - beast_cfg["speed"]) * 0.01
        if random.random() < flee_rate:
            p["in_combat"] = False
            p["combat_target"] = None
            self._advance_time(2)
            self._log(None, "成功逃跑！", "info")
            return {"ok": True, "msg": "成功逃跑！", "action": "flee"}
        else:
            beast_log = self._beast_attack(beast_spawn, beast_cfg)
            if p["hp"] <= 0:
                return self._combat_defeat()
            return {
                "ok": True, "msg": f"逃跑失败！\n{beast_log}", "action": "combat",
                "player": {"hp": p["hp"], "max_hp": p["max_hp"], "qi": p["qi"], "max_qi": p["max_qi"]},
                "beast": {"name": beast_cfg["name"], "hp": max(0, beast_spawn["hp"]), "max_hp": beast_cfg["hp"]}
            }

    def use_item_in_combat(self, item_id):
        p = self.state["player"]
        if not p["in_combat"]:
            return self.use_item(item_id)
        if not self._has_item(item_id):
            return {"ok": False, "msg": "无此物品"}
        m = get_material(item_id)
        if not m:
            return {"ok": False, "msg": "无效物品"}
        effect = m.get("effect", {})
        msg = f"使用{m['name']}。"
        if "heal_hp" in effect:
            heal = effect["heal_hp"]
            p["hp"] = min(p["max_hp"], p["hp"] + heal)
            msg += f"回复{heal}HP。"
        if "restore_qi" in effect:
            restore = effect["restore_qi"]
            p["qi"] = min(p["max_qi"], p["qi"] + restore)
            msg += f"回复{restore}灵气。"
        if "fire_resist" in effect:
            p["buffs"].append({"type": "fire_resist", "duration": effect.get("duration", 600)})
            msg += "获得火抗性。"
        if "ice_resist" in effect:
            p["buffs"].append({"type": "ice_resist", "duration": effect.get("duration", 600)})
            msg += "获得冰抗性。"
        if "attack_boost" in effect:
            p["buffs"].append({"type": "attack_boost", "duration": effect.get("duration", 300), "value": effect["attack_boost"]})
            msg += f"攻击+{effect['attack_boost']}。"
        if "damage" in effect:
            # 符箓伤害
            dmg = effect["damage"]
            for beast in self.state["world"]["beasts"]:
                if beast["id"] == p["combat_target"] and beast["alive"]:
                    beast["hp"] -= dmg
                    bc = get_beast(beast["beast_id"])
                    msg += f"\n对{bc['name']}造成{dmg}点{effect.get('element','')}属性伤害！"
                    if beast["hp"] <= 0:
                        self._remove_item(item_id, 1)
                        return self._combat_victory(beast, bc)
                    break
        self._remove_item(item_id, 1)
        self._advance_time(1)
        beast_spawn = None
        for b in self.state["world"]["beasts"]:
            if b["id"] == p["combat_target"] and b["alive"]:
                beast_spawn = b
                break
        if beast_spawn:
            beast_cfg = get_beast(beast_spawn["beast_id"])
            beast_log = self._beast_attack(beast_spawn, beast_cfg)
            if p["hp"] <= 0:
                return self._combat_defeat()
            return {
                "ok": True, "msg": msg + "\n" + beast_log, "action": "combat",
                "player": {"hp": p["hp"], "max_hp": p["max_hp"], "qi": p["qi"], "max_qi": p["max_qi"]},
                "beast": {"name": beast_cfg["name"], "hp": max(0, beast_spawn["hp"]), "max_hp": beast_cfg["hp"]}
            }
        return {"ok": True, "msg": msg}

    def use_item(self, item_id):
        p = self.state["player"]
        if not self._has_item(item_id):
            return {"ok": False, "msg": "无此物品"}
        m = get_material(item_id)
        if not m:
            return {"ok": False, "msg": "无效物品"}
        if m["type"] == "pill":
            effect = m.get("effect", {})
            msg = f"服用{m['name']}。"
            if "heal_hp" in effect:
                heal = effect["heal_hp"]
                p["hp"] = min(p["max_hp"], p["hp"] + heal)
                msg += f"回复{heal}HP。"
            if "restore_qi" in effect:
                p["qi"] = min(p["max_qi"], p["qi"] + restore)
                msg += f"回复{restore}灵气。"
            if "add_lifespan" in effect:
                p["lifespan"] += effect["add_lifespan"]
                msg += f"延寿{effect['add_lifespan']}年。"
            if "fire_resist" in effect:
                p["buffs"].append({"type": "fire_resist", "duration": effect.get("duration", 600)})
                msg += "获得火抗性。"
            if "ice_resist" in effect:
                p["buffs"].append({"type": "ice_resist", "duration": effect.get("duration", 600)})
                msg += "获得冰抗性。"
            if "meridian_repair" in effect:
                repair = effect["meridian_repair"]
                for mk in p["body"]["meridians"]:
                    p["body"]["meridians"][mk]["integrity"] = min(100, p["body"]["meridians"][mk]["integrity"] + repair)
                msg += f"经脉修复{repair}点。"
            if "dantian_repair" in effect:
                p["body"]["dantian"]["cracks"] = max(0, p["body"]["dantian"]["cracks"] - effect["dantian_repair"])
                msg += "丹田裂纹修复。"
            if "spirit_repair" in effect:
                p["body"]["spirit"]["resilience"] += effect["spirit_repair"]
                msg += f"神识修复{effect['spirit_repair']}点。"
            if "karma_cleanse" in effect:
                p["karma"] = max(0, p["karma"] - effect["karma_cleanse"])
                msg += f"消除{effect['karma_cleanse']}点业力。"
            self._remove_item(item_id, 1)
            self._advance_time(2)
            self._log(None, msg, "item")
            return {"ok": True, "msg": msg}
        if m["type"] == "weapon":
            return self.equip_item(item_id)
        if m["type"] == "armor":
            return self.equip_item(item_id)
        if m["type"] == "talisman":
            for b in self.state["world"]["beasts"]:
                if b["alive"] and b["region"] == p["region"] and abs(b["x"]-p["x"])+abs(b["y"]-p["y"]) <= 5:
                    return self._start_combat(b)
            return {"ok": False, "msg": "附近无敌"}
        if m["type"] == "jade_slip" and m.get("teaches"):
            return self.learn_technique(m["teaches"])
        return {"ok": False, "msg": "此物品无法使用"}

    def equip_item(self, item_id):
        p = self.state["player"]
        if not self._has_item(item_id):
            return {"ok": False, "msg": "无此物品"}
        m = get_material(item_id)
        if not m or m["type"] not in ("weapon", "armor"):
            return {"ok": False, "msg": "无法装备"}
        slot = "weapon" if m["type"] == "weapon" else "armor"
        old = p["equipped"].get(slot)
        if old:
            self._add_item(old, 1)
        self._remove_item(item_id, 1)
        p["equipped"][slot] = item_id
        self._recalc_player_attrs()
        self._log(None, f"装备{m['name']}", "item")
        return {"ok": True, "msg": f"装备{m['name']}"}

    def unequip_item(self, slot):
        p = self.state["player"]
        old = p["equipped"].get(slot)
        if not old:
            return {"ok": False, "msg": "无装备"}
        self._add_item(old, 1)
        p["equipped"][slot] = None
        self._recalc_player_attrs()
        return {"ok": True, "msg": "卸下装备"}

    def _recalc_player_attrs(self):
        p = self.state["player"]
        base_attack = 8
        base_defense = 3
        realm_idx = get_realm_index(p["realm"])
        realm = get_realm(p["realm"])
        if realm:
            base_attack = int(base_attack * realm.get("combat_mult", 1))
            base_defense = int(base_defense * realm.get("combat_mult", 1))
        if p["active_technique"]:
            tech = get_technique(p["active_technique"])
            if tech:
                for stage in tech["stages"]:
                    if get_realm_index(p["realm"]) >= get_realm_index(stage["realm_required"]):
                        eff = stage.get("effect", {})
                        if "attack_bonus" in eff:
                            base_attack += eff["attack_bonus"]
                        if "defense_bonus" in eff:
                            base_defense += eff["defense_bonus"]
        for slot in ("weapon", "armor"):
            item_id = p["equipped"].get(slot)
            if item_id:
                m = get_material(item_id)
                if m:
                    if m["type"] == "weapon":
                        base_attack += m["attrs"].get("damage", 0)
                    if m["type"] == "armor":
                        base_defense += m["attrs"].get("defense", 0)
        for b in p.get("buffs", []):
            if b["type"] == "attack_boost":
                base_attack += b.get("value", 0)
        # 肉身强度加成
        flesh = p["body"]["flesh"]
        base_defense += flesh["skin"]["toughness"] * 0.1 + flesh["muscle"]["strength"] * 0.05
        p["attack"] = int(base_attack)
        p["defense"] = int(base_defense)

    # ==================== 炼丹系统 ====================
    def get_alchemy_recipes(self):
        p = self.state["player"]
        recipes = get_pill_recipes()
        # 简化：所有丹方都可见，但需要材料才能炼
        return recipes

    def alchemy_craft(self, recipe_id, materials, process):
        p = self.state["player"]
        recipe = get_pill_recipe(recipe_id)
        if not recipe:
            return {"ok": False, "msg": "丹方不存在"}
        main_id = materials.get("main")
        if not main_id or not self._has_item(main_id):
            return {"ok": False, "msg": "主药缺失"}
        main_m = get_material(main_id)
        if main_m["type"] != recipe["inputs"]["main"]["type"]:
            return {"ok": False, "msg": "主药类型不符"}
        if main_m["tier"] < recipe["inputs"]["main"].get("min_tier", 1):
            return {"ok": False, "msg": "主药等阶不足"}
        aux_ids = materials.get("auxiliary", [])
        aux_required = recipe["inputs"].get("auxiliary", {})
        if aux_required and len(aux_ids) < aux_required.get("count", 0):
            return {"ok": False, "msg": "辅药数量不足"}
        for aid in aux_ids:
            if not self._has_item(aid):
                return {"ok": False, "msg": "辅药缺失"}
        cat_id = materials.get("catalyst")
        if "catalyst" in recipe["inputs"]:
            if not cat_id or not self._has_item(cat_id):
                return {"ok": False, "msg": "催化剂缺失"}
            cat_m = get_material(cat_id)
            cat_req = recipe["inputs"]["catalyst"]
            if cat_m["type"] != cat_req["type"] or cat_m["tier"] < cat_req.get("min_tier", 1):
                return {"ok": False, "msg": "催化剂不符"}
        temp = process.get("temperature", 0)
        dur = process.get("duration", 0)
        stir = process.get("stirring", 0)
        temp_opt = recipe["process"]["temperature"]["optimal"]
        temp_min = recipe["process"]["temperature"]["min"]
        temp_max = recipe["process"]["temperature"]["max"]
        dur_opt = recipe["process"]["duration"]["optimal"]
        stir_opt = recipe["process"]["stirring"]["optimal"]
        temp_score = max(0, 100 - abs(temp - temp_opt) * 0.5)
        dur_score = max(0, 100 - abs(dur - dur_opt) * 0.3)
        stir_score = max(0, 100 - abs(stir - stir_opt) * 20)
        quality_score = (temp_score + dur_score + stir_score) / 3
        toxicity = 0
        if temp > temp_max:
            toxicity = (temp - temp_max) * 0.2
            quality_score -= 20
        if temp < temp_min:
            quality_score -= 30
        if p["spiritual_root"] == "pseudo":
            quality_score -= 10
        # 丹田品质影响
        dantian_quality = p["body"]["dantian"]["quality"]
        if dantian_quality == "refined":
            quality_score += 5
        elif dantian_quality == "pure":
            quality_score += 15
        elif dantian_quality == "flawless":
            quality_score += 30
        if quality_score >= 95:
            quality, quality_name = 5, "完美"
        elif quality_score >= 80:
            quality, quality_name = 4, "极品"
        elif quality_score >= 60:
            quality, quality_name = 3, "上品"
        elif quality_score >= 40:
            quality, quality_name = 2, "中品"
        elif quality_score >= 20:
            quality, quality_name = 1, "下品"
        else:
            quality, quality_name = 0, "废丹"
        self._remove_item(main_id, 1)
        for aid in aux_ids:
            self._remove_item(aid, 1)
        if cat_id:
            self._remove_item(cat_id, 1)
        if quality == 0:
            msg = "炼丹失败，得到废丹！"
            self._add_item("wood_block", 1)
            self._log(None, msg, "alchemy_fail")
        else:
            pill_id = recipe["output"]["pill"]
            qty = recipe["output"].get("qty", 1)
            self._add_item(pill_id, qty)
            m = get_material(pill_id)
            msg = f"炼丹成功！获得{quality_name}{m['name']}×{qty}"
            if toxicity > 5:
                msg += f"（丹毒+{int(toxicity)}）"
            self._log(None, msg, "alchemy")
            p["pills_crafted"] += 1
        self._advance_time(int(dur))
        return {"ok": True, "msg": msg, "quality": quality, "quality_name": quality_name}

    # ==================== 交易系统 ====================
    def shop_list(self, shop_type):
        npcs = get_npcs_config()
        for n in npcs:
            if n.get("shop", {}).get("type") == shop_type:
                items = []
                w = self.state["world"]
                for iid in n["shop"]["items"]:
                    m = get_material(iid)
                    if m:
                        # 动态价格
                        price = w["market_prices"].get(iid, m["value"])
                        items.append({"item_id": iid, "name": m["name"], "price": price, "base_price": m["value"], "tier": m["tier"], "type": m["type"], "desc": m.get("desc", ""), "known": m.get("known", True)})
                return items
        return []

    def shop_buy(self, item_id, qty=1):
        p = self.state["player"]
        m = get_material(item_id)
        if not m:
            return {"ok": False, "msg": "物品不存在"}
        w = self.state["world"]
        price = w["market_prices"].get(item_id, m["value"]) * qty
        if self.get_spirit_stones_value() < price:
            return {"ok": False, "msg": f"灵石不足，需要{price}"}
        self.spend_spirit_stones(price)
        self._add_item(item_id, qty)
        self._advance_time(2)
        self._log(None, f"购买{m['name']}×{qty}，花费{price}灵石", "shop")
        return {"ok": True, "msg": f"购买{m['name']}×{qty}"}

    def shop_sell(self, item_id, qty=1):
        p = self.state["player"]
        if item_id == "reverse_jade":
            return {"ok": False, "msg": "此物不可出售"}
        if not self._has_item(item_id, qty):
            return {"ok": False, "msg": "物品不足"}
        m = get_material(item_id)
        if not m:
            return {"ok": False, "msg": "物品不存在"}
        w = self.state["world"]
        price = max(1, int(w["market_prices"].get(item_id, m["value"]) * 0.5)) * qty
        self._remove_item(item_id, qty)
        self.add_spirit_stones(price)
        self._advance_time(2)
        self._log(None, f"出售{m['name']}×{qty}，获得{price}灵石", "shop")
        return {"ok": True, "msg": f"出售{m['name']}×{qty}，获得{price}灵石"}

    # ==================== NPC交互 ====================
    def talk_to_npc(self, npc_id):
        p = self.state["player"]
        w = self.state["world"]
        npc = None
        for n in w["npcs"]:
            if n["id"] == npc_id and n["alive"]:
                npc = n
                break
        if not npc:
            return {"ok": False, "msg": "NPC不存在"}
        if npc["region"] != p["region"] or abs(npc["x"]-p["x"])+abs(npc["y"]-p["y"]) > 5:
            return {"ok": False, "msg": "距离太远，无法交谈"}
        cfg = get_npc_config(npc_id)
        rel = npc["relationship"]
        dialogue = cfg.get("dialogue", {})
        if rel < 0:
            msg = dialogue.get("low_relation", dialogue.get("default", "..."))
        elif rel >= 50:
            msg = dialogue.get("high_relation", dialogue.get("default", "..."))
        else:
            msg = dialogue.get("default", "...")
        if cfg.get("hostile") and rel < -10:
            return {"ok": True, "msg": msg, "action": "hostile", "npc_id": npc_id}
        if "shop" in cfg:
            return {"ok": True, "msg": msg, "action": "shop", "shop_type": cfg["shop"]["type"], "npc_id": npc_id}
        if "services" in cfg:
            return {"ok": True, "msg": msg, "action": "services", "services": cfg["services"], "npc_id": npc_id}
        quests = cfg.get("quests", [])
        if quests:
            return {"ok": True, "msg": msg, "action": "quest", "quests": quests, "npc_id": npc_id}
        return {"ok": True, "msg": msg, "npc_id": npc_id}

    def gift_to_npc(self, npc_id, item_id, qty=1):
        p = self.state["player"]
        if not self._has_item(item_id, qty):
            return {"ok": False, "msg": "物品不足"}
        m = get_material(item_id)
        if not m:
            return {"ok": False, "msg": "物品不存在"}
        for n in self.state["world"]["npcs"]:
            if n["id"] == npc_id:
                rel_gain = max(1, m["value"] // 10)
                n["relationship"] += rel_gain
                # 多维关系更新
                if "dimensions" in n:
                    n["dimensions"]["trust"] = min(100, n["dimensions"].get("trust", 0) + rel_gain)
                    n["dimensions"]["affection"] = min(100, n["dimensions"].get("affection", 0) + rel_gain // 2)
                self._remove_item(item_id, qty)
                self._advance_time(2)
                self._log(None, f"赠送{m['name']}×{qty}，关系+{rel_gain}", "social")
                return {"ok": True, "msg": f"赠送成功，关系+{rel_gain}", "relationship": n["relationship"]}
        return {"ok": False, "msg": "NPC不存在"}

    # ==================== 时间跳过 ====================
    def rest(self, hours):
        p = self.state["player"]
        if p["in_combat"]:
            return {"ok": False, "msg": "战斗中无法休息"}
        minutes = int(hours * 60)
        stage = self._get_lifespan_stage()
        regen_rate = 2 * (1 + stage.get("recovery_bonus", 0))
        p["hp"] = min(p["max_hp"], p["hp"] + int(minutes * regen_rate))
        p["qi"] = min(p["max_qi"], p["qi"] + int(minutes * regen_rate * 2))
        if p["active_technique"]:
            p["realm_progress"] += 0.005 * hours
        self._advance_time(minutes)
        self._log(None, f"打坐{hours}小时，HP/QI恢复", "rest")
        return {"ok": True, "msg": f"打坐{hours}小时，恢复完毕"}

    def seclusion(self, days):
        p = self.state["player"]
        if p["in_combat"]:
            return {"ok": False, "msg": "战斗中无法闭关"}
        if days > 30:
            return {"ok": False, "msg": "闭关时间过长，需要护法"}
        minutes = int(days * 24 * 60)
        if p["active_technique"]:
            tech = get_technique(p["active_technique"])
            if tech:
                speed = 0.5 * tech["completeness"]
                if p["spiritual_root"] == "pseudo":
                    speed *= 0.6
                region = get_region(p["region"])
                if region:
                    speed *= region["spirit_density"]
                stage = self._get_lifespan_stage()
                speed *= (1 + stage.get("cultivate_bonus", 0))
                progress_gain = speed * days * 24 / 10.0
                p["realm_progress"] += progress_gain
                realm_idx = get_realm_index(p["realm"])
                cur_stage = None
                for s in tech["stages"]:
                    if realm_idx >= get_realm_index(s["realm_required"]):
                        cur_stage = s
                if cur_stage:
                    defect = cur_stage.get("defect", {})
                    reversed_stages = p.get("reversed_stages", {})
                    is_reversed = reversed_stages.get(p["active_technique"], {}).get(tech["stages"].index(cur_stage), False)
                    if not is_reversed:
                        for k, v in defect.items():
                            if k == "meridian_strain":
                                p["attributes"]["meridian_strain"] += v * days * 24
                                for mk in p["body"]["meridians"]:
                                    if random.random() < 0.3:
                                        p["body"]["meridians"][mk]["integrity"] = max(0, p["body"]["meridians"][mk]["integrity"] - v * days * 24 * 10)
        p["hp"] = p["max_hp"]
        p["qi"] = p["max_qi"]
        self._advance_time(minutes)
        self._log(None, f"闭关{days}天，修为大增", "seclusion")
        if p["realm_progress"] >= 1.0:
            return {"ok": True, "msg": f"闭关{days}天结束，境界圆满！", "can_breakthrough": True}
        if p["lifespan"] <= 0:
            return {"ok": False, "msg": "闭关期间寿元耗尽，你坐化了。", "death": True}
        return {"ok": True, "msg": f"闭关{days}天结束"}

    # ==================== 种田系统 ====================
    def plant_seed(self, seed_id, plot_idx=0):
        """种植种子"""
        p = self.state["player"]
        if not self._has_item(seed_id):
            return {"ok": False, "msg": "无此种子"}
        m = get_material(seed_id)
        if not m or m["type"] != "seed":
            return {"ok": False, "msg": "非种子物品"}
        if len(p["farm_plots"]) <= plot_idx:
            while len(p["farm_plots"]) <= plot_idx:
                p["farm_plots"].append(None)
        if p["farm_plots"][plot_idx] is not None:
            return {"ok": False, "msg": "此处已有作物"}
        plant_id = m["attrs"]["plant_id"]
        grow_days = m["attrs"]["grow_days"]
        p["farm_plots"][plot_idx] = {
            "seed_id": seed_id,
            "plant_id": plant_id,
            "plant_time": self.state["world"]["game_time"],
            "harvest_time": self.state["world"]["game_time"] + grow_days * 24 * 60,
            "ready": False
        }
        self._remove_item(seed_id, 1)
        self._log(None, f"种下{m['name']}，预计{grow_days}日后成熟", "farm")
        return {"ok": True, "msg": f"种下{m['name']}"}

    def harvest_crop(self, plot_idx):
        """收获作物"""
        p = self.state["player"]
        if plot_idx >= len(p["farm_plots"]) or p["farm_plots"][plot_idx] is None:
            return {"ok": False, "msg": "此处无作物"}
        plot = p["farm_plots"][plot_idx]
        if self.state["world"]["game_time"] < plot["harvest_time"]:
            remaining = (plot["harvest_time"] - self.state["world"]["game_time"]) / (24 * 60)
            return {"ok": False, "msg": f"作物未成熟，还需{remaining:.1f}日"}
        self._add_item(plot["plant_id"], random.randint(1, 3))
        m = get_material(plot["plant_id"])
        p["farm_plots"][plot_idx] = None
        self._log(None, f"收获{m['name']}", "farm")
        return {"ok": True, "msg": f"收获{m['name']}"}

    def update_farm(self):
        """更新农田（检查成熟）"""
        p = self.state["player"]
        for plot in p["farm_plots"]:
            if plot and not plot["ready"]:
                if self.state["world"]["game_time"] >= plot["harvest_time"]:
                    plot["ready"] = True

    # ==================== 宠物系统 ====================
    def tame_beast(self, beast_spawn_id):
        """驯服妖兽"""
        p = self.state["player"]
        if not self._has_item("contract_talisman"):
            return {"ok": False, "msg": "需要契约符"}
        for b in self.state["world"]["beasts"]:
            if b["id"] == beast_spawn_id and b["alive"]:
                bc = get_beast(b["beast_id"])
                if not bc.get("tamable"):
                    return {"ok": False, "msg": "此妖兽不可驯服"}
                # 驯服成功率
                rate = 0.3 + p["body"]["spirit"]["sharpness"] * 0.005
                if random.random() < rate:
                    self._remove_item("contract_talisman", 1)
                    p["pets"].append({
                        "id": f"pet_{len(p['pets'])}",
                        "beast_id": bc["id"],
                        "name": bc["name"],
                        "tier": bc["tier"],
                        "hp": bc["hp"],
                        "attack": bc["attack"],
                        "loyalty": 50,
                        "exp": 0
                    })
                    b["alive"] = False
                    self._log(None, f"成功驯服{bc['name']}！", "tame")
                    return {"ok": True, "msg": f"驯服{bc['name']}成功！"}
                else:
                    self._remove_item("contract_talisman", 1)
                    self._log(None, "驯服失败，契约符消耗", "warn")
                    return {"ok": False, "msg": "驯服失败"}
        return {"ok": False, "msg": "无此妖兽"}

    # ==================== 状态查询 ====================
    def get_full_state(self):
        self.tick()
        self.update_farm()
        p = self.state["player"]
        self._recalc_player_attrs()
        # 可见实体
        visible_npcs = []
        for n in self.state["world"]["npcs"]:
            if n["alive"] and n["region"] == p["region"]:
                cfg = get_npc_config(n["id"])
                visible_npcs.append({
                    "id": n["id"], "name": cfg["name"], "title": cfg["title"],
                    "x": n["x"], "y": n["y"], "action": n["current_action"],
                    "relationship": n["relationship"]
                })
        visible_beasts = []
        for b in self.state["world"]["beasts"]:
            if b["alive"] and b["region"] == p["region"]:
                bc = get_beast(b["beast_id"])
                visible_beasts.append({
                    "id": b["id"], "name": bc["name"], "tier": bc["tier"],
                    "x": b["x"], "y": b["y"], "element": bc.get("element", "")
                })
        visible_resources = []
        for r in self.state["world"]["resources"]:
            if r["region"] == p["region"] and r["available"]:
                m = get_material(r["item"])
                visible_resources.append({
                    "id": r["id"], "item": r["item"], "name": m["name"] if m else r["item"],
                    "x": r["x"], "y": r["y"], "type": r["type"]
                })
        region = get_region(p["region"])
        # 库存
        inventory = []
        for inv in p["inventory"]:
            m = get_material(inv["item_id"])
            if m:
                inventory.append({
                    "item_id": inv["item_id"], "name": m["name"], "qty": inv["qty"],
                    "type": m["type"], "tier": m["tier"],
                    "value": m["value"], "desc": m.get("desc", ""),
                    "attrs": m.get("attrs", {}), "effect": m.get("effect", {}),
                    "rarity": m.get("rarity", "common"), "slot": m.get("slot"),
                    "teaches": m.get("teaches"), "known": m.get("known", True)
                })
        # 功法
        techniques = []
        for t in p["techniques"]:
            tc = get_technique(t["id"])
            if tc:
                reversed_stages = p.get("reversed_stages", {}).get(t["id"], {})
                techniques.append({
                    "id": t["id"], "name": tc["name"], "element": tc["element"],
                    "completeness": tc["completeness"], "desc": tc["desc"],
                    "stages": tc["stages"], "combat_skills": tc["combat_skills"],
                    "reversed_stages": reversed_stages
                })
        # 灵石
        ss = p["spirit_stones"]
        return {
            "player": {
                "name": p["name"], "realm": p["realm"], "realm_name": get_realm_name(p["realm"]),
                "realm_progress": p["realm_progress"], "comprehension": p["comprehension"],
                "age": round(p["age"], 1), "lifespan": round(p["lifespan"], 1),
                "hp": p["hp"], "max_hp": p["max_hp"], "qi": p["qi"], "max_qi": p["max_qi"],
                "attack": p["attack"], "defense": p["defense"], "speed": p["speed"],
                "spiritual_root": p["spiritual_root"],
                "body": p["body"],
                "techniques": techniques, "active_technique": p["active_technique"],
                "attributes": p["attributes"], "inventory": inventory,
                "equipped": p["equipped"],
                "x": p["x"], "y": p["y"], "region": p["region"],
                "spirit_stones": ss,
                "spirit_stones_value": self.get_spirit_stones_value(),
                "kills": p["kills"], "pills_crafted": p["pills_crafted"], "trees_cut": p["trees_cut"],
                "karma": p["karma"], "reputation": p["reputation"],
                "in_combat": p["in_combat"],
                "buffs": p.get("buffs", []),
                "has_reverse_jade": self._has_item("reverse_jade"),
                "pets": p.get("pets", []),
                "dao_companion": p.get("dao_companion"),
                "companions": p.get("companions", []),
                "farm_plots": p.get("farm_plots", []),
                "sect": p.get("sect"), "sect_position": p.get("sect_position")
            },
            "world": {
                "day": self.state["world"]["day"], "hour": self.state["world"]["hour"],
                "minute": self.state["world"]["minute"], "game_time": self.state["world"]["game_time"]
            },
            "region": {
                "id": region["id"], "name": region["name"], "type": region["type"],
                "width": region["width"], "height": region["height"],
                "description": region["description"], "spirit_density": region["spirit_density"],
                "buildings": region.get("buildings", []), "exits": region.get("exits", [])
            },
            "visible_npcs": visible_npcs, "visible_beasts": visible_beasts,
            "visible_resources": visible_resources,
            "log": self.state["log"][-30:]
        }

    def reset_game(self):
        self.state = self._new_game()
        self.save_state()
        return {"ok": True, "msg": "游戏已重置"}
