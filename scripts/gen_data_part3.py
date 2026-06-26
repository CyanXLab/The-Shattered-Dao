"""
数据生成器 Part 3: 炼器配方、阵法、剧情任务、拍卖物品、PVP对手
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def save(name, data):
    path = os.path.join(DATA_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  生成 {name}.json")


# ============================================================
# 11. 炼器配方系统（15种武器/防具）
# ============================================================
forge_recipes = [
    {
        "id": "forge_iron_sword", "name": "铁剑", "tier": 1, "output": "iron_sword",
        "inputs": {
            "core": {"type": "ore", "min_tier": 1, "count": 2},
            "handle": {"type": "misc", "id": "wood_block", "count": 1}
        },
        "process": {
            "smelting": {"min": 200, "max": 500, "optimal": 350},
            "hammering": {"min": 5, "max": 15, "optimal": 10},
            "quenching": {"liquid": "water", "duration": {"min": 3, "max": 10, "optimal": 5}}
        },
        "desc": "凡铁所铸，新手用剑。"
    },
    {
        "id": "forge_spirit_sword", "name": "灵纹剑", "tier": 3, "output": "spirit_sword",
        "inputs": {
            "core": {"type": "ore", "min_tier": 3, "count": 2},
            "edge": {"type": "ore", "min_tier": 2, "count": 1},
            "handle": {"type": "misc", "id": "wood_block", "count": 2},
            "inscription": {"type": "ore", "id": "ling_crystal", "count": 1}
        },
        "process": {
            "smelting": {"min": 400, "max": 800, "optimal": 600},
            "hammering": {"min": 10, "max": 25, "optimal": 18},
            "quenching": {"liquid": "spirit_water", "duration": {"min": 5, "max": 15, "optimal": 10}}
        },
        "desc": "刻有灵纹，可灌注灵气。"
    },
    {
        "id": "forge_fire_sword", "name": "赤焰剑", "tier": 4, "output": "fire_sword",
        "inputs": {
            "core": {"type": "ore", "min_tier": 3, "count": 2},
            "edge": {"type": "beast_part", "min_tier": 3, "element": "fire", "count": 1},
            "handle": {"type": "misc", "id": "wood_block", "count": 2},
            "inscription": {"type": "ore", "id": "huo_jing", "count": 1}
        },
        "process": {
            "smelting": {"min": 600, "max": 1000, "optimal": 800},
            "hammering": {"min": 15, "max": 30, "optimal": 22},
            "quenching": {"liquid": "fire_essence", "duration": {"min": 8, "max": 18, "optimal": 12}}
        },
        "desc": "蕴含火灵，挥之生焰。"
    },
    {
        "id": "forge_ice_sword", "name": "寒冰剑", "tier": 4, "output": "ice_sword",
        "inputs": {
            "core": {"type": "ore", "min_tier": 3, "count": 2},
            "edge": {"type": "beast_part", "min_tier": 3, "element": "ice", "count": 1},
            "handle": {"type": "misc", "id": "wood_block", "count": 2},
            "inscription": {"type": "ore", "id": "bing_jing", "count": 1}
        },
        "process": {
            "smelting": {"min": 500, "max": 900, "optimal": 700},
            "hammering": {"min": 15, "max": 30, "optimal": 22},
            "quenching": {"liquid": "ice_essence", "duration": {"min": 8, "max": 18, "optimal": 12}}
        },
        "desc": "寒气逼人，斩之冻髓。"
    },
    {
        "id": "forge_thunder_sword", "name": "雷霆剑", "tier": 5, "output": "thunder_sword",
        "inputs": {
            "core": {"type": "ore", "min_tier": 4, "count": 2},
            "edge": {"type": "ore", "min_tier": 4, "count": 1},
            "handle": {"type": "misc", "id": "yang_soul_wood", "count": 1},
            "inscription": {"type": "ore", "id": "lei_jing", "count": 1}
        },
        "process": {
            "smelting": {"min": 700, "max": 1100, "optimal": 900},
            "hammering": {"min": 20, "max": 40, "optimal": 30},
            "quenching": {"liquid": "thunder_essence", "duration": {"min": 10, "max": 20, "optimal": 15}}
        },
        "desc": "雷霆所凝，斩之麻痹。"
    },
    {
        "id": "forge_leather_armor", "name": "皮甲", "tier": 2, "output": "leather_armor",
        "inputs": {
            "core": {"type": "misc", "id": "leather", "count": 3},
            "lining": {"type": "misc", "id": "wood_block", "count": 1}
        },
        "process": {
            "smelting": {"min": 100, "max": 300, "optimal": 200},
            "hammering": {"min": 5, "max": 12, "optimal": 8},
            "quenching": {"liquid": "oil", "duration": {"min": 3, "max": 8, "optimal": 5}}
        },
        "desc": "兽皮所制，轻便耐用。"
    },
    {
        "id": "forge_spirit_armor", "name": "灵纹甲", "tier": 3, "output": "spirit_armor",
        "inputs": {
            "core": {"type": "ore", "min_tier": 3, "count": 3},
            "lining": {"type": "misc", "id": "leather", "count": 2},
            "inscription": {"type": "ore", "id": "ling_crystal", "count": 1}
        },
        "process": {
            "smelting": {"min": 400, "max": 800, "optimal": 600},
            "hammering": {"min": 12, "max": 25, "optimal": 18},
            "quenching": {"liquid": "spirit_water", "duration": {"min": 5, "max": 12, "optimal": 8}}
        },
        "desc": "刻有灵纹，可御灵气。"
    },
    {
        "id": "forge_dragon_sword", "name": "青龙剑", "tier": 6, "output": "dragon_sword",
        "inputs": {
            "core": {"type": "ore", "min_tier": 5, "count": 3},
            "edge": {"type": "beast_part", "min_tier": 6, "element": "wood", "count": 1},
            "handle": {"type": "beast_part", "min_tier": 6, "count": 1},
            "inscription": {"type": "ore", "id": "xian_tie", "count": 1}
        },
        "process": {
            "smelting": {"min": 900, "max": 1300, "optimal": 1100},
            "hammering": {"min": 30, "max": 50, "optimal": 40},
            "quenching": {"liquid": "dragon_blood", "duration": {"min": 15, "max": 25, "optimal": 20}}
        },
        "desc": "青龙之魂所附，威力绝伦。"
    },
    {
        "id": "forge_void_sword", "name": "虚空剑", "tier": 6, "output": "void_sword",
        "inputs": {
            "core": {"type": "ore", "min_tier": 5, "count": 3},
            "edge": {"type": "ore", "id": "xu_kong_jing", "count": 1},
            "handle": {"type": "misc", "id": "yang_soul_wood", "count": 2},
            "inscription": {"type": "ore", "id": "chen_jing_shi", "count": 1}
        },
        "process": {
            "smelting": {"min": 800, "max": 1200, "optimal": 1000},
            "hammering": {"min": 25, "max": 45, "optimal": 35},
            "quenching": {"liquid": "void_essence", "duration": {"min": 12, "max": 22, "optimal": 17}}
        },
        "desc": "虚空所化，可破空间。"
    },
    {
        "id": "forge_bone_sword", "name": "白骨剑", "tier": 4, "output": "bone_sword",
        "inputs": {
            "core": {"type": "beast_part", "min_tier": 3, "count": 2},
            "edge": {"type": "beast_part", "min_tier": 4, "count": 1},
            "handle": {"type": "misc", "id": "wood_block", "count": 1}
        },
        "process": {
            "smelting": {"min": 300, "max": 700, "optimal": 500},
            "hammering": {"min": 12, "max": 25, "optimal": 18},
            "quenching": {"liquid": "blood", "duration": {"min": 5, "max": 12, "optimal": 8}}
        },
        "desc": "妖骨所制，阴气重。"
    },
    {
        "id": "forge_poison_sword", "name": "碧毒剑", "tier": 3, "output": "poison_sword",
        "inputs": {
            "core": {"type": "ore", "min_tier": 2, "count": 2},
            "edge": {"type": "beast_part", "min_tier": 3, "count": 1},
            "poison": {"type": "herb", "min_tier": 3, "count": 2}
        },
        "process": {
            "smelting": {"min": 300, "max": 600, "optimal": 450},
            "hammering": {"min": 10, "max": 20, "optimal": 15},
            "quenching": {"liquid": "poison", "duration": {"min": 5, "max": 12, "optimal": 8}}
        },
        "desc": "淬毒之剑，斩之中毒。"
    },
    {
        "id": "forge_crystal_sword", "name": "水晶剑", "tier": 3, "output": "crystal_sword",
        "inputs": {
            "core": {"type": "ore", "id": "ling_crystal", "count": 3},
            "handle": {"type": "misc", "id": "wood_block", "count": 1}
        },
        "process": {
            "smelting": {"min": 250, "max": 550, "optimal": 400},
            "hammering": {"min": 8, "max": 18, "optimal": 13},
            "quenching": {"liquid": "spirit_water", "duration": {"min": 4, "max": 10, "optimal": 7}}
        },
        "desc": "灵晶所制，灵气传导佳。"
    },
    {
        "id": "forge_fire_armor", "name": "赤焰甲", "tier": 4, "output": "fire_armor",
        "inputs": {
            "core": {"type": "ore", "min_tier": 3, "count": 3},
            "lining": {"type": "beast_part", "min_tier": 3, "element": "fire", "count": 1},
            "inscription": {"type": "ore", "id": "huo_jing", "count": 1}
        },
        "process": {
            "smelting": {"min": 600, "max": 1000, "optimal": 800},
            "hammering": {"min": 15, "max": 30, "optimal": 22},
            "quenching": {"liquid": "fire_essence", "duration": {"min": 8, "max": 18, "optimal": 12}}
        },
        "desc": "火抗加成，火焰不侵。"
    },
    {
        "id": "forge_demon_sword", "name": "魔剑·血煞", "tier": 6, "output": "demon_sword",
        "inputs": {
            "core": {"type": "ore", "id": "mo_tie", "count": 2},
            "edge": {"type": "beast_part", "min_tier": 6, "element": "dark", "count": 1},
            "handle": {"type": "misc", "id": "yang_soul_wood", "count": 1},
            "inscription": {"type": "ore", "id": "an_jing", "count": 1}
        },
        "process": {
            "smelting": {"min": 700, "max": 1100, "optimal": 900},
            "hammering": {"min": 25, "max": 45, "optimal": 35},
            "quenching": {"liquid": "demon_blood", "duration": {"min": 12, "max": 22, "optimal": 17}}
        },
        "desc": "魔气所凝，斩之吸血，但损业力。"
    },
    {
        "id": "forge_black_turtle_armor", "name": "玄武甲", "tier": 7, "output": "black_turtle_armor",
        "inputs": {
            "core": {"type": "beast_part", "id": "black_turtle_shell", "count": 2},
            "lining": {"type": "ore", "id": "xian_tie", "count": 1},
            "inscription": {"type": "ore", "id": "chen_jing_shi", "count": 2}
        },
        "process": {
            "smelting": {"min": 1000, "max": 1400, "optimal": 1200},
            "hammering": {"min": 40, "max": 60, "optimal": 50},
            "quenching": {"liquid": "celestial_water", "duration": {"min": 20, "max": 30, "optimal": 25}}
        },
        "desc": "玄武之甲，万法不侵。"
    }
]
save("forge_recipes", {"forge_recipes": forge_recipes})


# ============================================================
# 12. 阵法系统（12种阵法）
# ============================================================
formations = [
    {
        "id": "spirit_gather_array", "name": "聚灵阵", "tier": 2, "type": "auxiliary",
        "effect": {"cultivate_bonus": 0.3, "qi_regen": 5},
        "duration": 600, "spirit_stone_cost": 5,
        "materials": [{"item": "spirit_gather_flag", "count": 4}],
        "break_difficulty": 30,
        "desc": "聚集天地灵气，修炼效率+30%。需4面聚灵阵旗。"
    },
    {
        "id": "defense_array", "name": "护身阵", "tier": 2, "type": "defense",
        "effect": {"defense_boost": 50, "damage_reduce": 0.3},
        "duration": 600, "spirit_stone_cost": 5,
        "materials": [{"item": "defense_flag", "count": 4}],
        "break_difficulty": 35,
        "desc": "布设防护，减伤30%。需4面护身阵旗。"
    },
    {
        "id": "kill_array", "name": "杀阵·诛仙", "tier": 4, "type": "attack",
        "effect": {"damage": 200, "element": "metal"},
        "duration": 300, "spirit_stone_cost": 20,
        "materials": [{"item": "kill_flag", "count": 8}],
        "break_difficulty": 70,
        "desc": "杀伐之阵，每秒对范围内敌人造成200点伤害。需8面杀阵阵旗。"
    },
    {
        "id": "illusion_array", "name": "幻阵·迷踪", "tier": 3, "type": "control",
        "effect": {"stun": True, "confuse": True},
        "duration": 300, "spirit_stone_cost": 10,
        "materials": [{"item": "illusion_flag", "count": 6}],
        "break_difficulty": 50,
        "desc": "迷惑敌人，使其无法行动。需6面幻阵阵旗。"
    },
    {
        "id": "time_array", "name": "时间阵", "tier": 6, "type": "special",
        "effect": {"time_ratio": 365},  # 内1日=外1年
        "duration": -1, "spirit_stone_cost": 1000,
        "materials": [{"item": "time_disk", "count": 1}],
        "break_difficulty": 100,
        "desc": "时间法宝，内部1日=外部1年。需时间阵盘。维护消耗巨大。"
    },
    {
        "id": "five_element_array", "name": "五行阵", "tier": 5, "type": "composite",
        "effect": {"all_affinity": 50, "cultivate_bonus": 0.5},
        "duration": 600, "spirit_stone_cost": 50,
        "materials": [{"item": "spirit_gather_flag", "count": 5}],
        "break_difficulty": 80,
        "desc": "五行相生相克，全方位提升。需5面不同属性阵旗。"
    },
    {
        "id": "lock_sky_array", "name": "锁天阵", "tier": 6, "type": "trap",
        "effect": {"prevent_escape": True, "seal_qi": 0.5},
        "duration": 300, "spirit_stone_cost": 80,
        "materials": [{"item": "kill_flag", "count": 12}],
        "break_difficulty": 90,
        "desc": "封锁空间，禁止遁逃，封印50%灵气。需12面杀阵阵旗。"
    },
    {
        "id": "fire_array", "name": "烈火阵", "tier": 3, "type": "attack",
        "effect": {"damage": 100, "element": "fire", "burn": True},
        "duration": 300, "spirit_stone_cost": 15,
        "materials": [{"item": "kill_flag", "count": 4}],
        "break_difficulty": 45,
        "desc": "烈火焚烧，每秒造成100点火属性伤害。"
    },
    {
        "id": "ice_array", "name": "寒冰阵", "tier": 3, "type": "control",
        "effect": {"damage": 80, "element": "ice", "slow": True},
        "duration": 300, "spirit_stone_cost": 15,
        "materials": [{"item": "kill_flag", "count": 4}],
        "break_difficulty": 45,
        "desc": "寒冰封锁，减速并造成冰属性伤害。"
    },
    {
        "id": "thunder_array", "name": "九霄雷阵", "tier": 5, "type": "attack",
        "effect": {"damage": 300, "element": "thunder", "stun": True},
        "duration": 300, "spirit_stone_cost": 40,
        "materials": [{"item": "kill_disk", "count": 1}],
        "break_difficulty": 75,
        "desc": "九霄雷降，造成300点雷属性伤害并眩晕。"
    },
    {
        "id": "soul_array", "name": "诛魂阵", "tier": 5, "type": "soul",
        "effect": {"soul_damage": 100, "confuse": True},
        "duration": 300, "spirit_stone_cost": 50,
        "materials": [{"item": "illusion_flag", "count": 8}],
        "break_difficulty": 85,
        "desc": "专伤神魂，造成100点神魂伤害并混乱。"
    },
    {
        "id": "celestial_array", "name": "天罡阵", "tier": 7, "type": "ultimate",
        "effect": {"all_boost": 100, "invincible": True},
        "duration": 60, "spirit_stone_cost": 500,
        "materials": [{"item": "time_disk", "count": 1}, {"item": "kill_disk", "count": 1}],
        "break_difficulty": 200,
        "desc": "天罡正气，60秒无敌。极品阵法。"
    }
]
save("formations", {"formations": formations})


# ============================================================
# 13. 完整剧情任务线（5条主线，每条5-7章）
# ============================================================
storylines_full = [
    {
        "id": "main_reverse_jade", "name": "逆道玉简之谜", "type": "main",
        "desc": "探索逆道玉简的来历，揭开天道崩碎的真相。",
        "chapters": [
            {
                "id": "ch1", "name": "玉简苏醒", "trigger": "game_start",
                "objective": "前往青云宗拜师", "target_npc": "npc_master_qingyun",
                "reward": {"exp": 50, "karma": 10},
                "desc": "你醒来时手握逆道玉简，必须找到师父指引修行之路。"
            },
            {
                "id": "ch2", "name": "藏经阁寻秘", "trigger": "join_qingyun",
                "objective": "向赵长老请教玉简来历", "target_npc": "npc_zhao_zhanglao",
                "precondition": {"realm": "qi_refining_3"},
                "reward": {"exp": 100, "item": "wood_slip"},
                "desc": "赵长老博古通今，或许知道玉简的来历。"
            },
            {
                "id": "ch3", "name": "逆修之路", "trigger": "learn_technique",
                "objective": "使用玉简逆转功法缺陷", "target_action": "reverse_technique",
                "precondition": {"realm": "qi_refining_5"},
                "reward": {"exp": 200, "karma": -10},
                "desc": "玉简之力可逆天道，试试逆转功法缺陷。"
            },
            {
                "id": "ch4", "name": "魔修觊觎", "trigger": "foundation_1",
                "objective": "击败前来抢夺玉简的魔修", "target_beast": "npc_dark_cultivator",
                "precondition": {"realm": "foundation_1"},
                "reward": {"exp": 500, "item": "storage_ring_low"},
                "desc": "玉简消息走漏，魔修前来抢夺。必须击败他！"
            },
            {
                "id": "ch5", "name": "天道碎片", "trigger": "golden_core_1",
                "objective": "在虚空裂缝寻找天道碎片", "target_region": "xu_kong_lie_feng",
                "precondition": {"realm": "golden_core_1"},
                "reward": {"exp": 2000, "item": "dao_fragment"},
                "desc": "传说天道碎片散落万界，虚空裂缝中或许有线索。"
            },
            {
                "id": "ch6", "name": "天道之秘", "trigger": "nascent_soul_1",
                "objective": "集齐3块天道碎片，参悟天道", "target_item_count": {"dao_fragment": 3},
                "precondition": {"realm": "nascent_soul_1"},
                "reward": {"exp": 10000, "technique": "void_basic"},
                "desc": "天道崩碎的真相，或许就藏在碎片之中。"
            }
        ]
    },
    {
        "id": "main_revenge", "name": "血色禁地之谜", "type": "main",
        "desc": "探索上古战场血色禁地，获得失传传承。",
        "chapters": [
            {
                "id": "ch1", "name": "禁地开启", "trigger": "foundation_3",
                "objective": "进入血色禁地", "target_region": "xue_se_jin_di",
                "precondition": {"realm": "foundation_3"},
                "reward": {"exp": 300},
                "desc": "血色禁地每30日开启一次，机缘难得。"
            },
            {
                "id": "ch2", "name": "上古战场", "trigger": "enter_xue_se",
                "objective": "探索古战场遗迹，找到上古传承", "target_building": "core_zone",
                "reward": {"exp": 500, "item": "star_iron"},
                "desc": "禁地核心区有上古战场遗迹，传说有大能传承。"
            },
            {
                "id": "ch3", "name": "传承之试", "trigger": "find_relic",
                "objective": "通过传承考验", "target_beast": "tian_jie_shou",
                "reward": {"exp": 1000, "karma": -50},
                "desc": "传承被天劫兽守护，必须击败它。"
            },
            {
                "id": "ch4", "name": "踏天之道", "trigger": "golden_core_5",
                "objective": "获得上古传承", "target_action": "claim_relic",
                "precondition": {"realm": "golden_core_5"},
                "reward": {"exp": 5000, "technique": "void_basic"},
                "desc": "传承蕴含踏天之道，逆天而行的真正功法。"
            }
        ]
    },
    {
        "id": "main_dragon", "name": "龙宫寻宝", "type": "main",
        "desc": "救助龙族，前往龙宫获取至宝。",
        "chapters": [
            {
                "id": "ch1", "name": "海难", "trigger": "nascent_soul_1",
                "objective": "救助遇险的龙族", "target_npc": "npc_dragon_princess",
                "precondition": {"realm": "nascent_soul_1"},
                "reward": {"exp": 1000, "karma": 50},
                "desc": "东海传来龙族遇险的消息，速去救援。"
            },
            {
                "id": "ch2", "name": "龙宫赴宴", "trigger": "save_dragon",
                "objective": "前往龙宫", "target_region": "long_gong",
                "reward": {"exp": 2000, "item": "dragon_scale"},
                "desc": "龙王感谢你救女之恩，邀你赴龙宫宴。"
            },
            {
                "id": "ch3", "name": "宝库选择", "trigger": "enter_long_gong",
                "objective": "在龙宫宝库中选择一件宝物", "target_action": "choose_treasure",
                "reward": {"item": "choice"},
                "desc": "龙宫宝库任你挑选一件，是龙鳞、龙角还是龙珠？"
            }
        ]
    },
    {
        "id": "main_sect_war", "name": "正魔大战", "type": "main",
        "desc": "正魔两道爆发大战，你的选择将影响天下格局。",
        "chapters": [
            {
                "id": "ch1", "name": "导火索", "trigger": "kill_demon",
                "objective": "击败魔修，拯救被掳的凡人", "target_beast": "npc_dark_cultivator",
                "precondition": {"realm": "foundation_5"},
                "reward": {"karma": 50, "exp": 500},
                "desc": "魔修掳掠凡人，你必须出手阻止。"
            },
            {
                "id": "ch2", "name": "宗门征召", "trigger": "sect_war_start",
                "objective": "响应宗门征召，加入正道联军", "target_npc": "npc_master_qingyun",
                "precondition": {"realm": "golden_core_1"},
                "reward": {"exp": 1000, "reputation": 100},
                "desc": "正魔大战一触即发，宗门征召弟子参战。"
            },
            {
                "id": "ch3", "name": "前线作战", "trigger": "join_war",
                "objective": "击杀5名魔修", "target_kill_count": 5,
                "reward": {"exp": 3000, "karma": 20},
                "desc": "前线战事吃紧，多杀魔修以振军心。"
            },
            {
                "id": "ch4", "name": "决战魔主", "trigger": "reach_demon_lord",
                "objective": "前往魔渊，击败魔渊之主", "target_npc": "npc_demon_lord",
                "precondition": {"realm": "divine_transformation_1"},
                "reward": {"exp": 10000, "item": "legendary", "karma": 100},
                "desc": "魔渊之主是魔道之首，唯有击败他才能终结大战。"
            }
        ]
    },
    {
        "id": "side_mortal_kindness", "name": "凡人恩情", "type": "side",
        "desc": "一次善举，多年后的回报。体现修仙者的人情味。",
        "chapters": [
            {
                "id": "ch1", "name": "救死扶伤", "trigger": "help_mortal",
                "objective": "救助凡人国度的一个家庭", "target_npc": "npc_liu_lao",
                "reward": {"karma": 50, "exp": 100},
                "desc": "凡人刘老汉一家贫病交加，你的一念之仁或成大因果。"
            },
            {
                "id": "ch2", "name": "凡人后裔", "trigger": "30_years_pass",
                "objective": "等待30年，看凡人后裔成长", "target_action": "wait_time",
                "precondition": {"time_pass": 30 * 365},
                "reward": {"karma": 100},
                "desc": "30年后，当年救下的孩童已长大成人。"
            },
            {
                "id": "ch3", "name": "天才出世", "trigger": "50_years_pass",
                "objective": "刘家后裔展现修行天赋", "target_action": "check_descendant",
                "precondition": {"time_pass": 50 * 365},
                "reward": {"karma": 100},
                "desc": "刘家后裔竟有修行天赋，被宗门收入门下。"
            },
            {
                "id": "ch4", "name": "回报之恩", "trigger": "100_years_pass",
                "objective": "接受后裔的报恩", "target_npc": "npc_liu_descendant",
                "precondition": {"time_pass": 100 * 365},
                "reward": {"exp": 5000, "item": "rare"},
                "desc": "百年之后，当年善举终得回报。刘家后裔已成一方大能，前来报恩。"
            }
        ]
    }
]
save("storylines", {"storylines": storylines_full})


# ============================================================
# 14. 拍卖物品（高价值稀有物品）
# ============================================================
auction_items = [
    {"id": "auc_1", "item_id": "storage_ring_mid", "base_price": 5000, "tier": 5, "desc": "中品储物戒，100格空间。"},
    {"id": "auc_2", "item_id": "star_iron", "base_price": 400, "tier": 5, "desc": "天外陨铁，炼器极品。"},
    {"id": "auc_3", "item_id": "feng_xi_grass", "base_price": 350, "tier": 5, "desc": "凤栖草，传闻凤凰栖息之地生长。"},
    {"id": "auc_4", "item_id": "ling_zhi_500", "base_price": 600, "tier": 5, "desc": "五百年灵芝，延寿神效。"},
    {"id": "auc_5", "item_id": "foundation_pill", "base_price": 500, "tier": 3, "desc": "筑基丹，突破筑基必备。"},
    {"id": "auc_6", "item_id": "golden_core_pill", "base_price": 1500, "tier": 4, "desc": "结金丹，突破金丹必备。"},
    {"id": "auc_7", "item_id": "lifespan_pill", "base_price": 2000, "tier": 4, "desc": "延寿丹，延寿10年。"},
    {"id": "auc_8", "item_id": "thunder_sword", "base_price": 1800, "tier": 5, "desc": "雷霆剑，斩之麻痹。"},
    {"id": "auc_9", "item_id": "dragon_armor", "base_price": 4500, "tier": 6, "desc": "青龙甲，防御无双。"},
    {"id": "auc_10", "item_id": "time_disk", "base_price": 8000, "tier": 6, "desc": "时间阵盘，1日=1年。"},
    {"id": "auc_11", "item_id": "dantian_pill", "base_price": 3000, "tier": 5, "desc": "补天丹，修复丹田裂纹。"},
    {"id": "auc_12", "item_id": "tribulation_pill", "base_price": 5000, "tier": 6, "desc": "渡劫丹，渡劫必备。"},
    {"id": "auc_13", "item_id": "reverse_jade", "base_price": 100000, "tier": 9, "desc": "逆道玉简（仿品），蕴含逆天之道。"},
    {"id": "auc_14", "item_id": "phoenix_feather", "base_price": 4500, "tier": 7, "desc": "凤翎，含涅槃意。"},
    {"id": "auc_15", "item_id": "qilin_horn", "base_price": 5000, "tier": 7, "desc": "麒麟角，仙家至宝。"},
    {"id": "auc_16", "item_id": "immortal_sword", "base_price": 50000, "tier": 7, "desc": "仙剑·诛仙，上古仙剑。"},
    {"id": "auc_17", "item_id": "nine_turn_pill", "base_price": 50000, "tier": 7, "desc": "九转金丹，仙丹。"},
    {"id": "auc_18", "item_id": "storage_ring_high", "base_price": 50000, "tier": 7, "desc": "上品储物戒，500格空间。"}
]
save("auction_items", {"auction_items": auction_items})


# ============================================================
# 15. PVP对手（散修NPC，可挑战）
# ============================================================
pvp_opponents = [
    {"id": "pvp_1", "name": "落魄散修", "realm": "qi_refining_7", "hp": 200, "attack": 25, "defense": 15,
     "reward_stones": 50, "reward_exp": 100, "location": "fang_market", "desc": "一名落魄的散修，看着很好欺负。"},
    {"id": "pvp_2", "name": "狂妄少主", "realm": "foundation_3", "hp": 800, "attack": 60, "defense": 40,
     "reward_stones": 300, "reward_exp": 500, "location": "fang_market", "desc": "某小宗门的少主，目中无人。"},
    {"id": "pvp_3", "name": "邪修血煞", "realm": "foundation_5", "hp": 1200, "attack": 80, "defense": 50,
     "reward_stones": 500, "reward_exp": 800, "location": "beast_mountain", "desc": "邪修一名，杀人越货。"},
    {"id": "pvp_4", "name": "剑修青衣", "realm": "golden_core_1", "hp": 3000, "attack": 150, "defense": 80,
     "reward_stones": 2000, "reward_exp": 2000, "location": "fang_market", "desc": "剑修高手，挑战各路修士。"},
    {"id": "pvp_5", "name": "魔修黑袍", "realm": "golden_core_5", "hp": 5000, "attack": 200, "defense": 120,
     "reward_stones": 5000, "reward_exp": 5000, "location": "mo_yuan", "desc": "魔修黑袍，实力深不可测。"},
    {"id": "pvp_6", "name": "散仙无名", "realm": "nascent_soul_1", "hp": 20000, "attack": 400, "defense": 250,
     "reward_stones": 20000, "reward_exp": 20000, "location": "xu_kong_lie_feng", "desc": "渡劫失败的散仙，实力强悍。"},
    {"id": "pvp_7", "name": "天骄·凌霄", "realm": "nascent_soul_3", "hp": 35000, "attack": 600, "defense": 350,
     "reward_stones": 50000, "reward_exp": 50000, "location": "ling_jie", "desc": "天界下凡的天骄，万中无一。"},
    {"id": "pvp_8", "name": "古修士·残魂", "realm": "divine_transformation_1", "hp": 100000, "attack": 1500, "defense": 800,
     "reward_stones": 200000, "reward_exp": 200000, "location": "xue_se_jin_di", "desc": "上古修士残魂，实力恐怖。"}
]
save("pvp_opponents", {"pvp_opponents": pvp_opponents})


# ============================================================
# 16. 天劫系统（5种天劫）
# ============================================================
heavenly_tribulations = [
    {
        "id": "trib_foundation", "name": "筑基天劫", "realm": "foundation_1",
        "rounds": 3, "damage_per_round": 100, "element": "thunder",
        "desc": "突破筑基时降下的天劫，3道雷劫，每道100伤害。"
    },
    {
        "id": "trib_golden_core", "name": "结丹天劫", "realm": "golden_core_1",
        "rounds": 5, "damage_per_round": 300, "element": "thunder",
        "desc": "突破金丹时降下的天劫，5道雷劫，每道300伤害。"
    },
    {
        "id": "trib_nascent_soul", "name": "化婴天劫", "realm": "nascent_soul_1",
        "rounds": 9, "damage_per_round": 1000, "element": "thunder",
        "desc": "突破元婴时降下的九重天劫，9道雷劫，每道1000伤害。"
    },
    {
        "id": "trib_divine", "name": "化神天劫", "realm": "divine_transformation_1",
        "rounds": 18, "damage_per_round": 3000, "element": "thunder",
        "desc": "突破化神时降下的十八重天劫，极其凶险。"
    },
    {
        "id": "trib_void", "name": "炼虚天劫", "realm": "void_refining_1",
        "rounds": 27, "damage_per_round": 10000, "element": "thunder",
        "desc": "突破炼虚时降下的二十七重天劫，九死一生。"
    }
]
save("tribulations", {"tribulations": heavenly_tribulations})


print("\nPart 3 数据生成完成！")
