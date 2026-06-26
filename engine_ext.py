"""
《逆仙录·天道残卷》引擎扩展模块
包含: 炼器系统、阵法系统、道侣系统、转世系统、天劫系统、剧情任务、拍卖、PVP
"""
import json
import random
from data_loader import (
    get_forge_recipes, get_forge_recipe, get_formations, get_formation,
    get_auction_items, get_pvp_opponents, get_pvp_opponent,
    get_tribulations, get_tribulation, get_storylines,
    get_realm_index, get_realm_name, get_realm, get_next_realm,
    get_material, get_beast
)


class EngineExtension:
    """引擎扩展，混入到GameEngine中"""

    # ==================== 炼器系统 ====================
    def get_forge_recipes(self):
        return get_forge_recipes()

    def forge_craft(self, recipe_id, materials, process):
        """炼器
        materials: {core, edge, handle, inscription, lining, poison}
        process: {smelting, hammering, quenching_duration}
        """
        p = self.state["player"]
        recipe = get_forge_recipe(recipe_id)
        if not recipe:
            return {"ok": False, "msg": "器方不存在"}
        # 检查材料
        inputs = recipe["inputs"]
        for slot, req in inputs.items():
            provided = materials.get(slot)
            if not provided:
                return {"ok": False, "msg": f"缺少{slot}材料"}
            if not self._has_item(provided):
                return {"ok": False, "msg": f"材料不足: {provided}"}
            m = get_material(provided)
            if not m:
                return {"ok": False, "msg": f"无效材料: {provided}"}
            if "type" in req and m["type"] != req["type"]:
                return {"ok": False, "msg": f"{slot}类型不符"}
            if "min_tier" in req and m["tier"] < req["min_tier"]:
                return {"ok": False, "msg": f"{slot}等阶不足"}
            if "id" in req and m["id"] != req["id"]:
                return {"ok": False, "msg": f"{slot}材料不符"}
        # 计算品质
        proc = recipe["process"]
        smelt = process.get("smelting", 0)
        hammer = process.get("hammering", 0)
        quench = process.get("quenching_duration", 0)
        smelt_opt = proc["smelting"]["optimal"]
        smelt_min = proc["smelting"]["min"]
        smelt_max = proc["smelting"]["max"]
        hammer_opt = proc["hammering"]["optimal"]
        quench_opt = proc["quenching"]["duration"]["optimal"]
        quench_min = proc["quenching"]["duration"]["min"]
        quench_max = proc["quenching"]["duration"]["max"]
        smelt_score = max(0, 100 - abs(smelt - smelt_opt) * 0.3)
        hammer_score = max(0, 100 - abs(hammer - hammer_opt) * 5)
        quench_score = max(0, 100 - abs(quench - quench_opt) * 10)
        quality_score = (smelt_score + hammer_score + quench_score) / 3
        if smelt > smelt_max:
            quality_score -= 30  # 烧毁
        if smelt < smelt_min:
            quality_score -= 40  # 未熔
        if p["spiritual_root"] == "pseudo":
            quality_score -= 10
        # 神识影响
        spirit_sharp = p["body"]["spirit"]["sharpness"]
        quality_score += spirit_sharp * 0.2
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
            quality, quality_name = 0, "废品"
        # 扣除材料
        for slot in inputs:
            self._remove_item(materials[slot], 1)
        if quality == 0:
            msg = "炼器失败，得到废铁！"
            self._add_item("wood_block", 1)
            self._log(None, msg, "forge_fail")
        else:
            output_id = recipe["output"]
            self._add_item(output_id, 1)
            m = get_material(output_id)
            msg = f"炼器成功！获得{quality_name}{m['name']}"
            self._log(None, msg, "forge")
            # 完美品质可能诞生器灵
            if quality == 5 and random.random() < 0.3:
                msg += "（武器诞生器灵！）"
                self._log(None, "★ 武器诞生器灵！此器有灵，可成长！", "forge")
        self._advance_time(60)
        return {"ok": True, "msg": msg, "quality": quality, "quality_name": quality_name}

    # ==================== 阵法系统 ====================
    def get_formations_list(self):
        return get_formations()

    def set_formation(self, formation_id):
        """布阵"""
        p = self.state["player"]
        form = get_formation(formation_id)
        if not form:
            return {"ok": False, "msg": "阵法不存在"}
        # 检查材料
        for mat_req in form["materials"]:
            if not self._has_item(mat_req["item"], mat_req["count"]):
                m = get_material(mat_req["item"])
                return {"ok": False, "msg": f"需要{m['name'] if m else mat_req['item']}×{mat_req['count']}"}
        # 检查灵石
        if self.get_spirit_stones_value() < form["spirit_stone_cost"]:
            return {"ok": False, "msg": f"灵石不足，需要{form['spirit_stone_cost']}"}
        # 扣除
        for mat_req in form["materials"]:
            self._remove_item(mat_req["item"], mat_req["count"])
        self.spend_spirit_stones(form["spirit_stone_cost"])
        # 设置阵法buff
        effect = form["effect"]
        buff = {
            "type": "formation",
            "formation_id": formation_id,
            "name": form["name"],
            "effect": effect,
            "duration": form["duration"],
            "remaining": form["duration"]
        }
        p["buffs"].append(buff)
        self._advance_time(30)
        self._log(None, f"布设{form['name']}！{form['desc']}", "formation")
        return {"ok": True, "msg": f"布设{form['name']}成功！"}

    def break_formation(self, formation_id):
        """破阵（需神识）"""
        p = self.state["player"]
        form = get_formation(formation_id)
        if not form:
            return {"ok": False, "msg": "阵法不存在"}
        difficulty = form["break_difficulty"]
        spirit_power = p["body"]["spirit"]["sharpness"] + p["body"]["spirit"]["range"]
        # 破阵成功率
        success_rate = min(0.95, spirit_power / (difficulty + spirit_power))
        self._advance_time(15)
        if random.random() < success_rate:
            self._log(None, f"成功破除{form['name']}！", "formation")
            return {"ok": True, "msg": f"成功破除{form['name']}！"}
        else:
            # 破阵失败受反噬
            dmg = int(difficulty * 0.5)
            p["hp"] = max(1, p["hp"] - dmg)
            self._log(None, f"破阵失败！遭受反噬，损失{dmg}HP", "warn")
            return {"ok": False, "msg": f"破阵失败！损失{dmg}HP"}

    # ==================== 道侣系统 ====================
    def propose_dao_companion(self, npc_id):
        """求婚"""
        p = self.state["player"]
        npc = None
        for n in self.state["world"]["npcs"]:
            if n["id"] == npc_id and n["alive"]:
                npc = n
                break
        if not npc:
            return {"ok": False, "msg": "NPC不存在"}
        # 检查关系
        if npc["relationship"] < 80:
            return {"ok": False, "msg": f"关系不足（需80以上，当前{npc['relationship']}）"}
        if p.get("dao_companion"):
            return {"ok": False, "msg": "你已有道侣"}
        # 性别检查（简化：不限制）
        # NPC同意概率
        agree_rate = min(0.95, npc["relationship"] / 100)
        if random.random() < agree_rate:
            p["dao_companion"] = npc_id
            cfg = self._get_npc_config(npc_id)
            self._log(None, f"★ {cfg['name']}答应与你结为道侣！大道同行，可双修共进。", "dao_companion")
            self.add_karma(20, "结为道侣", "heart")
            return {"ok": True, "msg": f"{cfg['name']}答应了！你们结为道侣。"}
        else:
            self._log(None, f"对方婉拒了你的求婚...", "warn")
            return {"ok": False, "msg": "对方婉拒了"}

    def dual_cultivate(self, hours=1):
        """双修"""
        p = self.state["player"]
        if not p.get("dao_companion"):
            return {"ok": False, "msg": "无道侣，无法双修"}
        npc_id = p["dao_companion"]
        npc = None
        for n in self.state["world"]["npcs"]:
            if n["id"] == npc_id:
                npc = n
                break
        if not npc or not npc["alive"]:
            return {"ok": False, "msg": "道侣不在"}
        cfg = self._get_npc_config(npc_id)
        # 双修效率加成
        bonus = 1.5
        if p["active_technique"]:
            tech = self._get_technique(p["active_technique"])
            if tech:
                speed = 0.5 * tech["completeness"] * bonus
                if p["spiritual_root"] == "pseudo":
                    speed *= 0.6
                progress = speed * hours / 10.0
                p["realm_progress"] += progress
                p["qi"] = min(p["max_qi"], p["qi"] + int(hours * 20))
                p["hp"] = min(p["max_hp"], p["hp"] + int(hours * 10))
                # 道侣也提升关系
                npc["relationship"] = min(100, npc["relationship"] + 1)
                self._advance_time(int(hours * 60))
                self._log(None, f"与{cfg['name']}双修{hours}小时，修为+{progress*100:.1f}%", "dual_cultivate")
                return {"ok": True, "msg": f"双修{hours}小时，修为大增"}
        return {"ok": False, "msg": "需激活功法"}

    def betray_companion(self):
        """背叛道侣"""
        p = self.state["player"]
        if not p.get("dao_companion"):
            return {"ok": False, "msg": "无道侣"}
        npc_id = p["dao_companion"]
        cfg = self._get_npc_config(npc_id)
        p["dao_companion"] = None
        # 关系急剧下降
        for n in self.state["world"]["npcs"]:
            if n["id"] == npc_id:
                n["relationship"] = -100
                n["dimensions"]["trust"] = 0
                n["dimensions"]["affection"] = 0
                break
        # 巨大业力损失
        self.add_karma(-200, f"背叛道侣{cfg['name']}", "betrayal")
        self._log(None, f"★ 你背叛了道侣{cfg['name']}！业力大损，可能招致复仇。", "warn")
        return {"ok": True, "msg": f"你背叛了{cfg['name']}，业力-200"}

    def _get_npc_config(self, npc_id):
        from data_loader import get_npc_config
        return get_npc_config(npc_id)

    def _get_technique(self, tid):
        from data_loader import get_technique
        return get_technique(tid)

    # ==================== 转世系统 ====================
    def on_death(self, cause="battle"):
        """玩家死亡处理"""
        p = self.state["player"]
        if p.get("reincarnating"):
            return {"ok": False, "msg": "已在转世流程中"}
        p["reincarnating"] = True
        p["death_cause"] = cause
        self._log(None, "★ 你已陨落。但修仙之路未尽，尚有三条路可选...", "death")
        return {
            "ok": True,
            "msg": "你已陨落",
            "action": "death",
            "options": [
                {"id": "possess", "name": "夺舍", "desc": "夺取他人肉身，成功率低，神魂受损", "risk": "high"},
                {"id": "reincarnate", "name": "转世轮回", "desc": "保留部分记忆重修，新身体随机", "risk": "medium"},
                {"id": "scatter_immortal", "name": "兵解为散仙", "desc": "肉身毁灭，神魂修炼，实力强但无法飞升", "risk": "low"}
            ]
        }

    def choose_reincarnation(self, choice):
        """选择转世方式"""
        p = self.state["player"]
        if not p.get("reincarnating"):
            return {"ok": False, "msg": "未在转世流程"}
        if choice == "possess":
            # 夺舍：成功率取决于神识
            spirit = p["body"]["spirit"]["resilience"]
            rate = min(0.7, spirit / 200)
            if random.random() < rate:
                # 成功：保留修为，神魂受损
                p["body"]["spirit"]["resilience"] = max(10, spirit - 50)
                p["body"]["spirit"]["soul_fragments"] += 1
                p["hp"] = p["max_hp"]
                p["qi"] = p["max_qi"]
                p["lifespan"] = get_realm(p["realm"])["lifespan"] if get_realm(p["realm"]) else 120
                p["reincarnating"] = False
                self.add_karma(-100, "夺舍他人肉身", "murder")
                self._log(None, "★ 夺舍成功！你占据了新的肉身，但神魂受损。", "reverse")
                return {"ok": True, "msg": "夺舍成功！神魂受损，业力-100"}
            else:
                # 失败：神魂俱灭
                p["reincarnating"] = False
                self._log(None, "夺舍失败，神魂俱灭！游戏结束。", "death")
                return {"ok": False, "msg": "夺舍失败，神魂俱灭。游戏结束。", "game_over": True}
        elif choice == "reincarnate":
            # 转世：保留50%记忆，新身体随机
            old_realm_idx = get_realm_index(p["realm"])
            # 业力影响新身体资质
            karma = p["karma"]
            if karma > 500:
                new_root = random.choice(["true", "heavenly"])
            elif karma > 0:
                new_root = random.choice(["false", "true"])
            else:
                new_root = random.choice(["pseudo", "false"])
            # 保留部分修为（降2个境界）
            new_realm_idx = max(0, old_realm_idx - 4)
            realms = self._get_realms_list()
            p["realm"] = realms[new_realm_idx]["id"]
            p["realm_progress"] = 0
            p["age"] = 0
            p["lifespan"] = realms[new_realm_idx]["lifespan"]
            p["spiritual_root"] = new_root
            p["hp"] = 80
            p["max_hp"] = 80
            p["qi"] = 50
            p["max_qi"] = 200
            p["reincarnating"] = False
            # 保留逆道玉简
            if not self._has_item("reverse_jade"):
                self._add_item("reverse_jade", 1)
            self._log(None, f"★ 转世成功！新身体资质：{new_root}，修为倒退但保留记忆。", "reverse")
            return {"ok": True, "msg": f"转世成功！新资质：{new_root}"}
        elif choice == "scatter_immortal":
            # 兵解散仙：肉身毁灭，神魂修炼
            p["scatter_immortal"] = True
            p["hp"] = p["max_hp"]
            p["qi"] = p["max_qi"]
            p["reincarnating"] = False
            # 散仙实力强但无法飞升
            p["attack"] = int(p["attack"] * 1.5)
            p["defense"] = int(p["defense"] * 1.5)
            self._log(None, "★ 兵解成功！你成为散仙，实力增强但无法飞升。", "reverse")
            return {"ok": True, "msg": "兵解为散仙！实力+50%，但无法飞升。"}
        return {"ok": False, "msg": "无效选择"}

    def _get_realms_list(self):
        from data_loader import get_realms
        return get_realms()

    # ==================== 天劫系统 ====================
    def trigger_tribulation(self):
        """触发天劫（突破大境界时）"""
        p = self.state["player"]
        next_realm = get_next_realm(p["realm"])
        if not next_realm:
            return {"ok": False, "msg": "已达境界上限"}
        trib = get_tribulation(next_realm["id"])
        if not trib:
            # 无天劫，直接突破
            return self.try_breakthrough("water_grind")
        # 业力影响天劫强度
        karma_mult = 1.0
        if p["karma"] < -500:
            karma_mult = 1.5
            self._log(None, "业力深重，天劫强度+50%！", "warn")
        elif p["karma"] > 500:
            karma_mult = 0.7
            self._log(None, "善业深厚，天劫强度-30%！", "info")
        return {
            "ok": True,
            "action": "tribulation",
            "tribulation": {
                "name": trib["name"],
                "rounds": trib["rounds"],
                "damage": int(trib["damage_per_round"] * karma_mult),
                "element": trib["element"],
                "desc": trib["desc"]
            }
        }

    def tribulation_round(self, action="endure", use_item=None):
        """渡劫一回合
        action: endure(硬抗) / dodge(闪避) / item(用物品)
        """
        p = self.state["player"]
        trib_state = p.get("tribulation_state")
        if not trib_state:
            return {"ok": False, "msg": "未在渡劫"}
        damage = trib_state["damage"]
        if action == "endure":
            # 硬抗：全额伤害，但有几率减免
            reduce = random.uniform(0, 0.3)
            actual_dmg = int(damage * (1 - reduce))
            p["hp"] -= actual_dmg
            log = f"第{trib_state['current_round']}/{trib_state['rounds']}道天劫！硬抗造成{actual_dmg}伤害"
            if reduce > 0.2:
                log += "（法宝护身减免部分伤害）"
        elif action == "dodge":
            # 闪避：50%几率完全躲避，失败则受1.5倍伤害
            if random.random() < 0.5:
                actual_dmg = 0
                log = f"第{trib_state['current_round']}道天劫！成功闪避！"
            else:
                actual_dmg = int(damage * 1.5)
                p["hp"] -= actual_dmg
                log = f"第{trib_state['current_round']}道天劫！闪避失败，承受{actual_dmg}伤害"
        elif action == "item":
            if use_item and self._has_item(use_item):
                m = get_material(use_item)
                if m and m["type"] == "talisman":
                    effect = m.get("effect", {})
                    if "shield" in effect:
                        # 护盾抵消
                        absorbed = min(effect["shield"], damage)
                        actual_dmg = damage - absorbed
                        p["hp"] -= actual_dmg
                        log = f"第{trib_state['current_round']}道天劫！{m['name']}吸收{absorbed}伤害，实际{actual_dmg}"
                        self._remove_item(use_item, 1)
                    else:
                        log = f"{m['name']}无法用于渡劫"
                        actual_dmg = damage
                        p["hp"] -= actual_dmg
                else:
                    log = "无效物品"
                    actual_dmg = damage
                    p["hp"] -= actual_dmg
            else:
                log = "无此物品"
                actual_dmg = damage
                p["hp"] -= actual_dmg
        self._log(None, log, "tribulation")
        # 检查死亡
        if p["hp"] <= 0:
            p["tribulation_state"] = None
            self._log(None, "渡劫失败，身死道消！", "death")
            return self.on_death("tribulation")
        # 下一回合
        trib_state["current_round"] += 1
        if trib_state["current_round"] > trib_state["rounds"]:
            # 渡劫成功
            p["tribulation_state"] = None
            return self._tribulation_success()
        return {
            "ok": True,
            "action": "tribulation",
            "msg": log,
            "player_hp": p["hp"],
            "current_round": trib_state["current_round"],
            "rounds": trib_state["rounds"]
        }

    def _tribulation_success(self):
        """渡劫成功"""
        p = self.state["player"]
        next_realm = get_next_realm(p["realm"])
        p["realm"] = next_realm["id"]
        p["realm_progress"] = 0.0
        p["max_hp"] = int(p["max_hp"] * 2)
        p["hp"] = p["max_hp"]
        p["max_qi"] = int(p["max_qi"] * 2)
        p["qi"] = p["max_qi"]
        p["lifespan"] = next_realm["lifespan"]
        self._log(None, f"★ 渡劫成功！现在境界：{next_realm['name']}，寿元上限：{next_realm['lifespan']}年", "breakthrough")
        self.add_karma(50, "渡劫成功", "cultivation")
        return {"ok": True, "msg": f"渡劫成功！现在境界：{next_realm['name']}", "breakthrough": True}

    # ==================== 剧情任务系统 ====================
    def get_story_progress(self):
        """获取剧情进度"""
        p = self.state["player"]
        return p.get("story_progress", {})

    def check_story_triggers(self):
        """检查剧情触发"""
        p = self.state["player"]
        if "story_progress" not in p:
            p["story_progress"] = {}
        for story in get_storylines():
            sid = story["id"]
            if sid not in p["story_progress"]:
                p["story_progress"][sid] = 0
            chapter_idx = p["story_progress"][sid]
            if chapter_idx >= len(story["chapters"]):
                continue
            chapter = story["chapters"][chapter_idx]
            # 检查触发条件
            if self._check_chapter_trigger(chapter):
                p["story_progress"][sid] = chapter_idx + 1
                # 发放奖励
                self._grant_chapter_reward(story, chapter)
                self._log(None, f"【剧情】{story['name']}·{chapter['name']} 完成！", "story")
                # 检查下一章
                if p["story_progress"][sid] < len(story["chapters"]):
                    next_ch = story["chapters"][p["story_progress"][sid]]
                    self._log(None, f"【新任务】{next_ch['name']}：{next_ch['desc']}", "story")

    def _check_chapter_trigger(self, chapter):
        """检查章节触发条件"""
        p = self.state["player"]
        trigger = chapter.get("trigger", "")
        # 前置条件
        precond = chapter.get("precondition", {})
        if "realm" in precond:
            if get_realm_index(p["realm"]) < get_realm_index(precond["realm"]):
                return False
        if "time_pass" in precond:
            if p["age"] * 365 < precond["time_pass"]:
                return False
        # 触发条件
        if trigger == "game_start":
            return True
        if trigger == "join_qingyun":
            return p.get("sect") == "qingyun_sect_info" or p["region"] == "qingyun_sect"
        if trigger == "learn_technique":
            return len(p["techniques"]) > 0
        if trigger == "foundation_1":
            return p["realm"].startswith("foundation")
        if trigger == "golden_core_1":
            return p["realm"].startswith("golden_core")
        if trigger == "nascent_soul_1":
            return p["realm"].startswith("nascent_soul")
        if trigger == "foundation_3":
            return get_realm_index(p["realm"]) >= get_realm_index("foundation_3")
        if trigger == "golden_core_5":
            return get_realm_index(p["realm"]) >= get_realm_index("golden_core_5")
        if trigger == "kill_demon":
            return any(k.get("killed_demon") for k in [p])
        if trigger == "enter_xue_se":
            return p["region"] == "xue_se_jin_di"
        if trigger == "find_relic":
            return p.get("found_relic", False)
        if trigger == "save_dragon":
            return p.get("saved_dragon", False)
        if trigger == "enter_long_gong":
            return p["region"] == "long_gong"
        if trigger == "sect_war_start":
            return self.state["flags"].get("sect_war", False)
        if trigger == "join_war":
            return p.get("joined_war", False)
        if trigger == "reach_demon_lord":
            return p["region"] == "mo_yuan"
        if trigger == "help_mortal":
            return p["mortal_helped"]
        if trigger.startswith("30_years_pass") or trigger.startswith("50_years_pass") or trigger.startswith("100_years_pass"):
            years = int(trigger.split("_")[0])
            return p["age"] >= years
        return False

    def _grant_chapter_reward(self, story, chapter):
        """发放章节奖励"""
        p = self.state["player"]
        reward = chapter.get("reward", {})
        if "exp" in reward:
            p["realm_progress"] += reward["exp"] / 1000.0
        if "karma" in reward:
            self.add_karma(reward["karma"], f"剧情：{chapter['name']}", "story")
        if "item" in reward:
            if reward["item"] != "choice" and reward["item"] != "rare" and reward["item"] != "legendary":
                self._add_item(reward["item"], 1)
            else:
                # 随机稀有物品
                rare_items = ["star_iron", "feng_xi_grass", "ling_zhi_500", "storage_ring_low"]
                self._add_item(random.choice(rare_items), 1)
        if "technique" in reward:
            if not any(t["id"] == reward["technique"] for t in p["techniques"]):
                p["techniques"].append({"id": reward["technique"], "exp": 0})
        if "reputation" in reward:
            p["reputation"] += reward["reputation"]

    # ==================== 拍卖系统 ====================
    def auction_bid(self, auc_id, bid_price):
        """竞拍"""
        p = self.state["player"]
        items = get_auction_items()
        auc = None
        for a in items:
            if a["id"] == auc_id:
                auc = a
                break
        if not auc:
            return {"ok": False, "msg": "拍卖物品不存在"}
        current_price = int(auc["base_price"] * random.uniform(0.8, 1.5))
        if bid_price < current_price:
            return {"ok": False, "msg": f"出价过低，当前价{current_price}"}
        if self.get_spirit_stones_value() < bid_price:
            return {"ok": False, "msg": "灵石不足"}
        # 竞拍成功概率（出价越高越可能成功）
        success_rate = min(0.95, 0.5 + (bid_price - current_price) / current_price * 0.3)
        if random.random() < success_rate:
            self.spend_spirit_stones(bid_price)
            self._add_item(auc["item_id"], 1)
            m = get_material(auc["item_id"])
            self._log(None, f"★ 拍卖成功！以{bid_price}灵石获得{m['name']}", "auction")
            return {"ok": True, "msg": f"竞拍成功！获得{m['name']}"}
        else:
            # 被别人拍走
            self._log(None, "拍卖失败，物品被他人拍走", "warn")
            return {"ok": False, "msg": "拍卖失败，物品被他人以更高价拍走"}

    # ==================== PVP系统 ====================
    def get_pvp_list(self):
        """获取可挑战PVP对手"""
        p = self.state["player"]
        opponents = get_pvp_opponents()
        result = []
        for opp in opponents:
            # 只显示实力相近的对手
            opp_realm_idx = get_realm_index(opp["realm"])
            my_realm_idx = get_realm_index(p["realm"])
            if abs(opp_realm_idx - my_realm_idx) <= 4:
                result.append({
                    "id": opp["id"],
                    "name": opp["name"],
                    "realm": get_realm_name(opp["realm"]),
                    "hp": opp["hp"],
                    "desc": opp["desc"],
                    "reward_stones": opp["reward_stones"],
                    "reward_exp": opp["reward_exp"]
                })
        return result

    def start_pvp(self, opp_id):
        """开始PVP战斗"""
        p = self.state["player"]
        opp = get_pvp_opponent(opp_id)
        if not opp:
            return {"ok": False, "msg": "对手不存在"}
        # 创建临时妖兽式战斗对象
        self.state["world"]["beasts"].append({
            "id": f"pvp_{opp_id}",
            "region": p["region"],
            "x": p["x"], "y": p["y"],
            "home_x": p["x"], "home_y": p["y"],
            "beast_id": opp_id,
            "respawn": 999999,
            "alive": True,
            "hp": opp["hp"],
            "is_pvp": True,
            "pvp_data": opp
        })
        # 直接开始战斗
        for b in self.state["world"]["beasts"]:
            if b["id"] == f"pvp_{opp_id}":
                p["in_combat"] = True
                p["combat_target"] = b["id"]
                self._log(None, f"与{opp['name']}展开决斗！", "combat")
                return {
                    "ok": True, "msg": f"与{opp['name']}展开决斗！",
                    "action": "combat",
                    "beast": {"name": opp["name"], "hp": opp["hp"], "max_hp": opp["hp"], "tier": 0, "element": ""}
                }
        return {"ok": False, "msg": "PVP启动失败"}

    # ==================== 宗门战 ====================
    def start_sect_war(self):
        """发起宗门战（简化版）"""
        p = self.state["player"]
        if not p.get("sect"):
            return {"ok": False, "msg": "未加入宗门"}
        if self.get_spirit_stones_value() < 1000:
            return {"ok": False, "msg": "宗门战需要1000灵石军费"}
        self.spend_spirit_stones(1000)
        self.state["flags"]["sect_war"] = True
        self._log(None, "★ 宗门战爆发！正魔两道全面开战！", "event")
        return {"ok": True, "msg": "宗门战已发起！"}

    def join_sect_war(self):
        """加入宗门战"""
        p = self.state["player"]
        if not self.state["flags"].get("sect_war"):
            return {"ok": False, "msg": "当前无宗门战"}
        p["joined_war"] = True
        self._log(None, "你加入了正道联军，奔赴前线。", "event")
        return {"ok": True, "msg": "已加入宗门战"}
