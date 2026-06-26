"""
数据生成器 Part 2: 区域、NPC、宗门、剧情
"""
import json
import os
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
random.seed(20260627)


def save(name, data):
    path = os.path.join(DATA_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  生成 {name}.json")


# ============================================================
# 6. 区域系统（多层嵌套，10个区域）
# ============================================================
regions = [
    {
        "id": "qingyun_sect", "name": "青云宗", "type": "sect",
        "parent": "tian_nan", "description": "正道宗门，灵气浓郁，护山大阵守护。新晋弟子修炼圣地。",
        "width": 64, "height": 48, "spirit_density": 0.9, "pvp_allowed": False,
        "buildings": [
            {"id": "main_hall", "name": "主殿", "x": 30, "y": 20, "w": 8, "h": 6, "function": "sect_master"},
            {"id": "alchemy_room", "name": "炼丹房", "x": 18, "y": 14, "w": 6, "h": 5, "function": "alchemy"},
            {"id": "forge_room", "name": "炼器房", "x": 42, "y": 14, "w": 6, "h": 5, "function": "forge"},
            {"id": "scripture_pavilion", "name": "藏经阁", "x": 18, "y": 30, "w": 6, "h": 5, "function": "learn"},
            {"id": "mission_hall", "name": "任务堂", "x": 42, "y": 30, "w": 6, "h": 5, "function": "mission"},
            {"id": "dormitory", "name": "弟子居", "x": 30, "y": 36, "w": 8, "h": 4, "function": "rest"},
            {"id": "farm", "name": "药园", "x": 10, "y": 24, "w": 6, "h": 4, "function": "farm"},
            {"id": "auction", "name": "拍卖行", "x": 50, "y": 24, "w": 6, "h": 4, "function": "auction"},
            {"id": "gate", "name": "山门", "x": 30, "y": 4, "w": 6, "h": 3, "function": "exit_to_market"}
        ],
        "resources": [
            {"type": "herb", "id": "res_1", "x": 8, "y": 10, "item": "yun_ling_grass", "respawn": 600},
            {"type": "herb", "id": "res_2", "x": 56, "y": 10, "item": "yun_ling_grass", "respawn": 600},
            {"type": "herb", "id": "res_3", "x": 6, "y": 38, "item": "qing_xin_lotus", "respawn": 900},
            {"type": "herb", "id": "res_4", "x": 58, "y": 38, "item": "qing_xin_lotus", "respawn": 900},
            {"type": "ore", "id": "res_5", "x": 4, "y": 24, "item": "han_iron", "respawn": 1200},
            {"type": "ore", "id": "res_6", "x": 60, "y": 24, "item": "ling_crystal", "respawn": 1500}
        ],
        "exits": [{"x": 30, "y": 4, "target": "fang_market", "tx": 30, "ty": 40}]
    },
    {
        "id": "fang_market", "name": "四方坊市", "type": "market",
        "parent": "tian_nan", "description": "商贾云集之地，禁止斗法。可在此买卖物品、获取情报。",
        "width": 64, "height": 48, "spirit_density": 0.5, "pvp_allowed": False,
        "buildings": [
            {"id": "auction_house", "name": "拍卖行", "x": 30, "y": 18, "w": 10, "h": 6, "function": "auction"},
            {"id": "herb_shop", "name": "百草堂", "x": 14, "y": 14, "w": 7, "h": 5, "function": "shop_herb"},
            {"id": "ore_shop", "name": "千锤铺", "x": 43, "y": 14, "w": 7, "h": 5, "function": "shop_ore"},
            {"id": "pill_shop", "name": "丹药阁", "x": 14, "y": 28, "w": 7, "h": 5, "function": "shop_pill"},
            {"id": "weapon_shop", "name": "兵器坊", "x": 43, "y": 28, "w": 7, "h": 5, "function": "shop_weapon"},
            {"id": "talisman_shop", "name": "符箓阁", "x": 28, "y": 38, "w": 8, "h": 4, "function": "shop_talisman"},
            {"id": "tavern", "name": "醉仙楼", "x": 26, "y": 34, "w": 12, "h": 5, "function": "tavern"},
            {"id": "guild_hall", "name": "公会堂", "x": 50, "y": 38, "w": 8, "h": 4, "function": "guild"},
            {"id": "gate_n", "name": "北门", "x": 30, "y": 4, "w": 6, "h": 3, "function": "exit_to_sect"},
            {"id": "gate_s", "name": "南门", "x": 30, "y": 42, "w": 6, "h": 3, "function": "exit_to_mountain"}
        ],
        "exits": [
            {"x": 30, "y": 4, "target": "qingyun_sect", "tx": 30, "ty": 6},
            {"x": 30, "y": 44, "target": "beast_mountain", "tx": 30, "ty": 6}
        ]
    },
    {
        "id": "beast_mountain", "name": "万妖山脉", "type": "beast_mountain",
        "parent": "tian_nan", "description": "妖兽栖息之地，灵药丰富但危机四伏。只有强者才能深入。",
        "width": 64, "height": 48, "spirit_density": 0.7, "pvp_allowed": True,
        "buildings": [
            {"id": "hunter_camp", "name": "猎户营地", "x": 30, "y": 6, "w": 8, "h": 4, "function": "rest"},
            {"id": "deep_cave", "name": "幽冥洞", "x": 12, "y": 36, "w": 6, "h": 5, "function": "dungeon"},
            {"id": "fire_peak", "name": "炎峰", "x": 50, "y": 12, "w": 6, "h": 5, "function": "fire_area"},
            {"id": "ice_lake", "name": "寒冰潭", "x": 50, "y": 36, "w": 6, "h": 5, "function": "ice_area"},
            {"id": "ancient_ruin", "name": "古遗迹", "x": 30, "y": 38, "w": 8, "h": 5, "function": "ruin"}
        ],
        "resources": [
            {"type": "herb", "id": "res_10", "x": 10, "y": 14, "item": "chi_yan_grass", "respawn": 800},
            {"type": "herb", "id": "res_11", "x": 54, "y": 14, "item": "chi_yan_grass", "respawn": 800},
            {"type": "herb", "id": "res_12", "x": 10, "y": 30, "item": "bing_lotus", "respawn": 1000},
            {"type": "herb", "id": "res_13", "x": 54, "y": 30, "item": "bing_lotus", "respawn": 1000},
            {"type": "herb", "id": "res_14", "x": 30, "y": 24, "item": "ling_zhi_100", "respawn": 1800},
            {"type": "ore", "id": "res_15", "x": 16, "y": 22, "item": "xuan_iron", "respawn": 1500},
            {"type": "ore", "id": "res_16", "x": 48, "y": 22, "item": "chi_copper", "respawn": 1400},
            {"type": "ore", "id": "res_17", "x": 30, "y": 38, "item": "ling_crystal", "respawn": 2000}
        ],
        "beast_spawns": [
            {"x": 26, "y": 10, "beast": "ye_tu", "respawn": 600},
            {"x": 34, "y": 10, "beast": "ye_tu", "respawn": 600},
            {"x": 22, "y": 14, "beast": "shan_lang", "respawn": 900},
            {"x": 38, "y": 14, "beast": "shan_lang", "respawn": 900},
            {"x": 26, "y": 18, "beast": "du_she", "respawn": 900},
            {"x": 34, "y": 18, "beast": "du_she", "respawn": 900},
            {"x": 14, "y": 12, "beast": "chiyan_tiger", "respawn": 1200},
            {"x": 50, "y": 12, "beast": "chiyan_tiger", "respawn": 1200},
            {"x": 14, "y": 36, "beast": "ice_wolf", "respawn": 1200},
            {"x": 50, "y": 36, "beast": "ice_wolf", "respawn": 1200},
            {"x": 30, "y": 28, "beast": "qingmu_snake", "respawn": 1500},
            {"x": 8, "y": 24, "beast": "jinjia_scorpion", "respawn": 1500},
            {"x": 56, "y": 24, "beast": "fengxing_leopard", "respawn": 1500}
        ],
        "exits": [{"x": 30, "y": 4, "target": "fang_market", "tx": 30, "ty": 42}]
    },
    {
        "id": "xue_se_jin_di", "name": "血色禁地", "type": "forbidden",
        "parent": "tian_nan", "description": "上古战场，灵药遍地但凶险异常。每30日开启一次。",
        "width": 48, "height": 48, "spirit_density": 1.2, "pvp_allowed": True,
        "buildings": [
            {"id": "entrance", "name": "禁地入口", "x": 22, "y": 4, "w": 4, "h": 3, "function": "rest"},
            {"id": "core_zone", "name": "核心区", "x": 20, "y": 24, "w": 8, "h": 6, "function": "ruin"}
        ],
        "resources": [
            {"type": "herb", "id": "res_20", "x": 8, "y": 12, "item": "bi_xue_grass", "respawn": 2000},
            {"type": "herb", "id": "res_21", "x": 38, "y": 12, "item": "ling_zhi_500", "respawn": 3000},
            {"type": "herb", "id": "res_22", "x": 8, "y": 36, "item": "ji_nian_grass", "respawn": 2500},
            {"type": "ore", "id": "res_23", "x": 38, "y": 36, "item": "star_iron", "respawn": 3500}
        ],
        "beast_spawns": [
            {"x": 12, "y": 18, "beast": "shi_jing_yi_wang", "respawn": 2400},
            {"x": 36, "y": 18, "beast": "mo_ying", "respawn": 2400},
            {"x": 24, "y": 30, "beast": "tian_jie_shou", "respawn": 3000}
        ],
        "exits": [{"x": 22, "y": 4, "target": "beast_mountain", "tx": 22, "ty": 44}],
        "open_cycle": 30, "open_duration": 3
    },
    {
        "id": "fan_ren_guo_du", "name": "凡人国度·洛京", "type": "mortal_kingdom",
        "parent": "tian_nan", "description": "凡人王都，灵气稀薄但繁华热闹。可历练心境、收集信仰。",
        "width": 64, "height": 48, "spirit_density": 0.1, "pvp_allowed": False,
        "buildings": [
            {"id": "palace", "name": "皇宫", "x": 28, "y": 14, "w": 10, "h": 8, "function": "mortal_palace"},
            {"id": "market", "name": "集市", "x": 14, "y": 28, "w": 10, "h": 6, "function": "mortal_market"},
            {"id": "tea_house", "name": "茶馆", "x": 40, "y": 28, "w": 8, "h": 4, "function": "tavern"},
            {"id": "school", "name": "书院", "x": 16, "y": 12, "w": 8, "h": 5, "function": "teach"},
            {"id": "clinic", "name": "医馆", "x": 40, "y": 12, "w": 8, "h": 5, "function": "heal_mortal"},
            {"id": "gate_n", "name": "北门", "x": 30, "y": 4, "w": 6, "h": 3, "function": "exit_to_market"}
        ],
        "exits": [{"x": 30, "y": 4, "target": "fang_market", "tx": 30, "ty": 44}]
    },
    {
        "id": "xu_kong_lie_feng", "name": "虚空裂缝", "type": "void_rift",
        "parent": "tian_nan", "description": "空间不稳定之处，蕴含天道碎片，可跨位面旅行。极度危险。",
        "width": 48, "height": 48, "spirit_density": 1.5, "pvp_allowed": True,
        "buildings": [
            {"id": "rift_core", "name": "裂缝核心", "x": 20, "y": 20, "w": 8, "h": 8, "function": "void_core"}
        ],
        "resources": [
            {"type": "ore", "id": "res_30", "x": 12, "y": 12, "item": "xu_kong_jing", "respawn": 5000},
            {"type": "ore", "id": "res_31", "x": 32, "y": 32, "item": "chen_jing_shi", "respawn": 5000}
        ],
        "beast_spawns": [
            {"x": 16, "y": 16, "beast": "mo_ying", "respawn": 3000},
            {"x": 30, "y": 30, "beast": "jiu_you_she", "respawn": 4000}
        ],
        "exits": [
            {"x": 24, "y": 4, "target": "beast_mountain", "tx": 24, "ty": 44},
            {"x": 24, "y": 44, "target": "ling_jie", "tx": 24, "ty": 4}
        ]
    },
    {
        "id": "ling_jie", "name": "灵界·云梦泽", "type": "spirit_realm",
        "parent": "ling_jie_plane", "description": "灵界一角，灵气浓郁百倍，仙人足迹所至。",
        "width": 64, "height": 64, "spirit_density": 5.0, "pvp_allowed": True,
        "buildings": [
            {"id": "spirit_palace", "name": "灵宫", "x": 28, "y": 28, "w": 10, "h": 8, "function": "spirit_palace"},
            {"id": "spirit_market", "name": "灵市", "x": 14, "y": 14, "w": 10, "h": 6, "function": "spirit_market"}
        ],
        "exits": [{"x": 30, "y": 4, "target": "xu_kong_lie_feng", "tx": 24, "ty": 40}]
    },
    {
        "id": "mo_yuan", "name": "魔渊", "type": "demon_realm",
        "parent": "tian_nan", "description": "魔修聚集之地，魔气浓郁，正道慎入。",
        "width": 48, "height": 48, "spirit_density": 1.0, "pvp_allowed": True,
        "buildings": [
            {"id": "demon_palace", "name": "魔主殿", "x": 20, "y": 20, "w": 8, "h": 8, "function": "demon_palace"},
            {"id": "demon_market", "name": "魔市", "x": 10, "y": 10, "w": 8, "h": 4, "function": "demon_market"}
        ],
        "beast_spawns": [
            {"x": 16, "y": 16, "beast": "mo_ying", "respawn": 1500},
            {"x": 30, "y": 30, "beast": "jiu_you_she", "respawn": 2000}
        ],
        "exits": [{"x": 24, "y": 4, "target": "xue_se_jin_di", "tx": 24, "ty": 44}]
    },
    {
        "id": "long_gong", "name": "东海龙宫", "type": "dragon_palace",
        "parent": "tian_nan", "description": "龙族祖地，海底深处，宝物无数但龙族守护。",
        "width": 64, "height": 48, "spirit_density": 3.0, "pvp_allowed": True,
        "buildings": [
            {"id": "dragon_throne", "name": "龙王宝座", "x": 28, "y": 22, "w": 10, "h": 8, "function": "dragon_throne"},
            {"id": "treasure_vault", "name": "龙宫宝库", "x": 14, "y": 14, "w": 8, "h": 6, "function": "treasure_vault"}
        ],
        "beast_spawns": [
            {"x": 16, "y": 16, "beast": "qing_long", "respawn": 10000}
        ],
        "exits": []
    },
    {
        "id": "tian_jie", "name": "天界·南天门", "type": "heaven_realm",
        "parent": "xian_jie_plane", "description": "仙人居住之地，凡人不可至。渡劫飞升后可入。",
        "width": 96, "height": 96, "spirit_density": 100.0, "pvp_allowed": False,
        "buildings": [
            {"id": "south_gate", "name": "南天门", "x": 40, "y": 10, "w": 16, "h": 8, "function": "heaven_gate"},
            {"id": "jade_pool", "name": "瑶池", "x": 20, "y": 40, "w": 12, "h": 8, "function": "jade_pool"},
            {"id": "ling_xiao", "name": "凌霄宝殿", "x": 40, "y": 50, "w": 16, "h": 10, "function": "ling_xiao"}
        ],
        "exits": []
    }
]
save("regions", {"regions": regions})


# ============================================================
# 7. NPC系统（30个，含剧情NPC）
# ============================================================
npcs = [
    # 青云宗
    {"id": "npc_master_qingyun", "name": "青云掌门", "title": "元婴期·掌门", "realm": "nascent_soul_1",
     "region": "qingyun_sect", "x": 34, "y": 23, "role": "sect_master",
     "schedule": {"06:00": "cultivate", "09:00": "audience", "12:00": "meditate", "14:00": "audience", "18:00": "cultivate", "21:00": "study", "23:00": "sleep"},
     "knowledge": {"reverse_jade": True, "player_progress": True, "ancient_records": True},
     "goals": ["maintain_sect", "find_talent"],
     "relationship": 30, "quests": [],
     "dialogue": {"default": "修行之路，重在心诚。你既得逆道玉简，便是天选之人，但切记不可逆天而行。",
                  "low_relation": "你资质平庸，老夫看在玉简份上才收你，切勿令老夫失望。",
                  "high_relation": "你进步神速，假以时日必成大器。"}},
    {"id": "npc_li_shixiong", "name": "李师兄", "title": "筑基后期·大师兄", "realm": "foundation_5",
     "region": "qingyun_sect", "x": 24, "y": 16, "role": "senior_disciple",
     "schedule": {"06:00": "wake_up", "07:00": "morning_cultivation", "09:00": "patrol", "12:00": "meal", "14:00": "practice", "18:00": "market", "21:00": "evening_cultivation", "23:00": "sleep"},
     "knowledge": {"player_killed_wang": False, "secret_cave_location": True},
     "goals": ["breakthrough_golden_core", "protect_sect"],
     "relationship": 20, "emotional_state": {"angry": 0, "jealous": 30, "grateful": 0},
     "quests": [{"id": "q_herb_collect", "name": "采药任务", "desc": "帮我采集5株云灵草", "type": "collect", "target": "yun_ling_grass", "count": 5, "reward": {"spirit_stones": 20, "exp": 30}}],
     "dialogue": {"default": "师弟初来乍到，有事尽管找我。我平日卯时打坐，午后练剑。",
                  "jealous": "哼，资质平平却得玉简认可，无非是运道好罢了。",
                  "grateful": "多谢师弟相助，这件皮甲赠你。"}},
    {"id": "npc_wang_shimei", "name": "王师妹", "title": "练气七层·炼丹弟子", "realm": "qi_refining_7",
     "region": "qingyun_sect", "x": 20, "y": 16, "role": "alchemist_disciple",
     "schedule": {"06:00": "wake_up", "07:00": "gather_herb", "09:00": "alchemy", "12:00": "meal", "14:00": "alchemy", "18:00": "study", "21:00": "cultivate", "23:00": "sleep"},
     "knowledge": {"pill_recipe": True, "market_news": True},
     "goals": ["learn_advanced_alchemy", "find_rare_herb"],
     "relationship": 25, "emotional_state": {"angry": 0, "jealous": 0, "grateful": 10},
     "quests": [{"id": "q_alchemy_help", "name": "炼丹材料", "desc": "帮我找3颗妖丹用于炼丹研究", "type": "collect", "target": "any_beast_core", "count": 3, "reward": {"pill": "qi_pill", "qty": 5, "exp": 40}}],
     "dialogue": {"default": "炼丹之道在于火候。师弟若想学，可来炼丹房旁观。",
                  "low_relation": "我现在很忙，请勿打扰。",
                  "high_relation": "师弟，这是我新研究的丹方，你看看。"}},
    {"id": "npc_zhang_tiejiang", "name": "张铁匠", "title": "筑基中期·炼器师", "realm": "foundation_3",
     "region": "qingyun_sect", "x": 44, "y": 16, "role": "blacksmith",
     "schedule": {"06:00": "wake_up", "07:00": "prepare", "09:00": "forge", "12:00": "meal", "14:00": "forge", "18:00": "market", "21:00": "rest", "23:00": "sleep"},
     "knowledge": {"ore_source": True, "weapon_recipe": True},
     "goals": ["forge_spirit_weapon", "find_star_iron"],
     "relationship": 15,
     "quests": [{"id": "q_ore_help", "name": "矿石采集", "desc": "采集5份玄铁矿", "type": "collect", "target": "xuan_iron", "count": 5, "reward": {"weapon": "iron_sword", "exp": 50}}],
     "dialogue": {"default": "锻造需要好材料，更需要好技术。",
                  "low_relation": "炼器房重地，闲人免进。",
                  "high_relation": "师弟，这把剑我为你打造的，拿去用。"}},
    {"id": "npc_zhao_zhanglao", "name": "赵长老", "title": "化神期·藏经阁守", "realm": "divine_transformation_1",
     "region": "qingyun_sect", "x": 20, "y": 32, "role": "elder_library",
     "schedule": {"06:00": "cultivate", "09:00": "library", "12:00": "meditate", "14:00": "library", "18:00": "teach", "21:00": "study", "23:00": "sleep"},
     "knowledge": {"ancient_records": True, "reverse_jade_history": True},
     "goals": ["preserve_knowledge", "find_successor"],
     "relationship": 20,
     "quests": [{"id": "q_knowledge_test", "name": "悟性考验", "desc": "回答长老的问题", "type": "quiz", "reward": {"technique": "fire_basic", "exp": 100}}],
     "dialogue": {"default": "藏经阁万卷藏书，皆上古传承。",
                  "low_relation": "你尚不够资格阅读深阁藏书。",
                  "high_relation": "逆道玉简，上古之物。你可愿听老夫讲述其来历？"}},
    {"id": "npc_sun_shidi", "name": "孙师弟", "title": "练气四层·同门", "realm": "qi_refining_4",
     "region": "qingyun_sect", "x": 32, "y": 38, "role": "junior_disciple",
     "schedule": {"06:00": "wake_up", "07:00": "cultivate", "09:00": "task", "12:00": "meal", "14:00": "practice", "18:00": "wander", "21:00": "cultivate", "23:00": "sleep"},
     "knowledge": {"sect_gossip": True},
     "goals": ["breakthrough_foundation", "befriend_player"],
     "relationship": 40, "emotional_state": {"angry": 0, "jealous": 0, "grateful": 20},
     "dialogue": {"default": "师兄！我也想去万妖山脉历练，带我一起吧？",
                  "high_relation": "师兄，这是我攒的灵石，你拿去买药。"}},
    # 四方坊市
    {"id": "npc_shopkeeper_herb", "name": "百草堂掌柜", "title": "筑基初期·商人", "realm": "foundation_1",
     "region": "fang_market", "x": 16, "y": 16, "role": "shopkeeper_herb",
     "schedule": {"06:00": "wake_up", "08:00": "open_shop", "12:00": "meal", "14:00": "open_shop", "18:00": "close_shop", "21:00": "rest", "23:00": "sleep"},
     "knowledge": {"herb_prices": True, "rare_herb_source": True},
     "goals": ["profit", "find_rare_herb"], "relationship": 10,
     "shop": {"type": "herb", "items": ["yun_ling_grass", "qing_xin_lotus", "chi_yan_grass", "bing_lotus", "ling_zhi_100", "wood_block", "bai_lu_grass", "zi_ye_grass"]},
     "dialogue": {"default": "客官要买什么？本店灵药货真价实。",
                  "high_relation": "老朋友来了，今日有批好货，便宜卖你。"}},
    {"id": "npc_shopkeeper_ore", "name": "千锤铺掌柜", "title": "筑基初期·商人", "realm": "foundation_1",
     "region": "fang_market", "x": 45, "y": 16, "role": "shopkeeper_ore",
     "schedule": {"06:00": "wake_up", "08:00": "open_shop", "12:00": "meal", "14:00": "open_shop", "18:00": "close_shop", "21:00": "rest", "23:00": "sleep"},
     "knowledge": {"ore_prices": True, "mine_location": True},
     "goals": ["profit"], "relationship": 10,
     "shop": {"type": "ore", "items": ["han_iron", "chi_copper", "xuan_iron", "ling_crystal", "purple_gold", "wu_jin_shi", "shan_jing_shi"]},
     "dialogue": {"default": "矿石、灵晶，应有尽有。",
                  "high_relation": "兄弟又来了，今日新到一批陨星铁。"}},
    {"id": "npc_shopkeeper_pill", "name": "丹药阁掌柜", "title": "金丹中期·炼丹大师", "realm": "golden_core_3",
     "region": "fang_market", "x": 16, "y": 30, "role": "shopkeeper_pill",
     "schedule": {"06:00": "wake_up", "08:00": "open_shop", "12:00": "meal", "14:00": "alchemy", "18:00": "open_shop", "21:00": "rest", "23:00": "sleep"},
     "knowledge": {"pill_prices": True, "pill_recipe": True},
     "goals": ["profit", "learn_recipe"], "relationship": 10,
     "shop": {"type": "pill", "items": ["qi_pill", "flesh_renew_pill", "fire_resist_pill", "ice_resist_pill", "foundation_pill", "detox_pill", "qi_gathering_pill", "swift_pill"]},
     "dialogue": {"default": "丹药固本培元，客官请便。",
                  "high_relation": "你这小辈炼丹天赋不错，这丹方送你研究。"}},
    {"id": "npc_shopkeeper_weapon", "name": "兵器坊掌柜", "title": "金丹中期·炼器大师", "realm": "golden_core_3",
     "region": "fang_market", "x": 45, "y": 30, "role": "shopkeeper_weapon",
     "schedule": {"06:00": "wake_up", "08:00": "open_shop", "12:00": "meal", "14:00": "forge", "18:00": "open_shop", "21:00": "rest", "23:00": "sleep"},
     "knowledge": {"weapon_prices": True}, "goals": ["profit", "find_star_iron"], "relationship": 10,
     "shop": {"type": "weapon", "items": ["iron_sword", "spirit_sword", "cloth_armor", "leather_armor", "spirit_armor", "wood_sword", "earth_sword"]},
     "dialogue": {"default": "刀剑无眼，客官选好。",
                  "high_relation": "老朋友，这把新打的灵纹剑，便宜给你。"}},
    {"id": "npc_shopkeeper_talisman", "name": "符箓阁掌柜", "title": "筑基后期·符箓师", "realm": "foundation_5",
     "region": "fang_market", "x": 30, "y": 38, "role": "shopkeeper_talisman",
     "schedule": {"06:00": "wake_up", "08:00": "open_shop", "12:00": "meal", "14:00": "craft", "18:00": "open_shop", "21:00": "rest", "23:00": "sleep"},
     "knowledge": {"talisman_prices": True}, "goals": ["profit"], "relationship": 10,
     "shop": {"type": "talisman", "items": ["talisman_fire", "talisman_ice", "talisman_heal", "talisman_shield", "talisman_escape", "talisman_wood", "talisman_metal"]},
     "dialogue": {"default": "符箓之道，在于一念之间。",
                  "high_relation": "道友，这护身符我亲手画的，送你。"}},
    {"id": "npc_innkeeper", "name": "醉仙楼掌柜", "title": "练气二层·凡人", "realm": "qi_refining_2",
     "region": "fang_market", "x": 30, "y": 36, "role": "innkeeper",
     "schedule": {"06:00": "wake_up", "08:00": "open_shop", "12:00": "meal", "14:00": "open_shop", "18:00": "open_shop", "22:00": "close_shop", "23:00": "sleep"},
     "knowledge": {"gossip": True, "secret_news": True}, "goals": ["profit", "gather_info"], "relationship": 15,
     "services": [{"name": "住宿", "cost": 5, "effect": "rest_full"}, {"name": "情报", "cost": 20, "effect": "info"}],
     "dialogue": {"default": "客官住店还是用饭？消息灵通，价格公道。",
                  "high_relation": "客官，最近听说万妖山脉深处有大能遗迹现世。"}},
    {"id": "npc_qing_gu", "name": "青姑", "title": "筑基中期·散修", "realm": "foundation_3",
     "region": "fang_market", "x": 32, "y": 24, "role": "wanderer",
     "schedule": {"06:00": "wake_up", "08:00": "market", "12:00": "meal", "14:00": "wander", "18:00": "tavern", "21:00": "rest", "23:00": "sleep"},
     "knowledge": {"auction_news": True, "treasure_rumor": True},
     "goals": ["find_treasure", "profit"], "relationship": 0,
     "dialogue": {"default": "道友也是来找宝物的？听说拍卖行下月有大动作。",
                  "high_relation": "道友，我打听到一处秘境入口，但需两人方能进入。"}},
    {"id": "npc_liu_lao", "name": "刘老汉", "title": "凡人·农夫", "realm": "mortal",
     "region": "fang_market", "x": 26, "y": 38, "role": "mortal",
     "schedule": {"05:00": "wake_up", "06:00": "farm", "12:00": "meal", "14:00": "farm", "18:00": "rest", "20:00": "sleep"},
     "knowledge": {"local_news": True, "ancient_legend": True}, "goals": ["survive"], "relationship": 0,
     "dialogue": {"default": "仙人老爷，老汉只是凡人，不懂修行之事。但祖上传说万妖山脉深处有上古仙人遗迹。",
                  "high_relation": "恩公，这点心意请收下。"}},
    # 万妖山脉
    {"id": "npc_hunter_wang", "name": "猎户老王", "title": "练气五层·散修", "realm": "qi_refining_5",
     "region": "beast_mountain", "x": 32, "y": 8, "role": "hunter",
     "schedule": {"06:00": "wake_up", "07:00": "hunt", "12:00": "rest", "14:00": "hunt", "18:00": "camp", "21:00": "rest", "23:00": "sleep"},
     "knowledge": {"beast_habits": True, "safe_route": True},
     "goals": ["survive", "find_rare_beast"], "relationship": 10,
     "quests": [{"id": "q_beast_bounty", "name": "妖兽悬赏", "desc": "猎杀2只赤焰虎", "type": "kill", "target": "chiyan_tiger", "count": 2, "reward": {"spirit_stones": 100, "exp": 80}}],
     "dialogue": {"default": "万妖山脉危险重重，道友小心。火系妖兽怕冰，冰系妖兽怕火。",
                  "high_relation": "兄弟，跟我来，我知道一处赤焰虎巢穴。"}},
    {"id": "npc_dark_cultivator", "name": "神秘黑衣人", "title": "金丹后期·魔修", "realm": "golden_core_5",
     "region": "beast_mountain", "x": 14, "y": 38, "role": "dark_cultivator",
     "schedule": {"00:00": "wander", "06:00": "hide", "12:00": "hide", "18:00": "wander", "23:00": "cultivate"},
     "knowledge": {"dark_technique": True, "forbidden_pill": True},
     "goals": ["steal_reverse_jade", "kill_talented_cultivator"],
     "relationship": -20, "emotional_state": {"angry": 30, "jealous": 50, "grateful": 0}, "hostile": True,
     "dialogue": {"default": "嘿嘿，逆道玉简在你这种废物手中，真是暴殄天物。交出来，饶你不死。",
                  "combat": "受死吧！"}},
    # 凡人国度
    {"id": "npc_emperor", "name": "洛京皇帝", "title": "凡人·皇帝", "realm": "mortal",
     "region": "fan_ren_guo_du", "x": 32, "y": 18, "role": "emperor",
     "schedule": {"05:00": "wake_up", "06:00": "court", "12:00": "meal", "14:00": "study", "18:00": "rest", "22:00": "sleep"},
     "knowledge": {"empire_secrets": True, "ancient_treasure": True},
     "goals": ["maintain_empire", "seek_immortality"], "relationship": 0,
     "dialogue": {"default": "仙长降临，蓬荜生辉。朕听闻仙长能延年益寿，不知可否赐教？",
                  "high_relation": "仙长救我王朝，朕愿以国库相赠。"}},
    {"id": "npc_doctor_li", "name": "李神医", "title": "练气九层·医修", "realm": "qi_refining_9",
     "region": "fan_ren_guo_du", "x": 42, "y": 14, "role": "doctor",
     "schedule": {"06:00": "wake_up", "07:00": "herb", "09:00": "heal", "12:00": "meal", "14:00": "heal", "18:00": "study", "21:00": "rest", "23:00": "sleep"},
     "knowledge": {"medicine": True, "rare_herb": True},
     "goals": ["heal_people", "find_successor"], "relationship": 10,
     "quests": [{"id": "q_heal_people", "name": "悬壶济世", "desc": "帮助李神医治疗10名病人", "type": "custom", "count": 10, "reward": {"exp": 100, "technique": "wood_basic"}}],
     "dialogue": {"default": "医者父母心。道友若有医术天赋，可学我这身本事。",
                  "high_relation": "道友心善，这本《青囊经》送你。"}},
    # 龙宫
    {"id": "npc_dragon_king", "name": "东海龙王", "title": "化神后期·龙族之主", "realm": "divine_transformation_5",
     "region": "long_gong", "x": 32, "y": 26, "role": "dragon_king",
     "schedule": {"06:00": "court", "12:00": "rest", "18:00": "cultivate", "22:00": "sleep"},
     "knowledge": {"ocean_secrets": True, "treasure_vault": True},
     "goals": ["protect_ocean", "find_daughter"], "relationship": 0,
     "dialogue": {"default": "龙族祖地，凡人勿入。你既来之，必有缘由。",
                  "high_relation": "道友救我女儿，龙宫宝库任你挑选。"}},
    # 魔渊
    {"id": "npc_demon_lord", "name": "魔渊之主", "title": "化神中期·魔主", "realm": "divine_transformation_3",
     "region": "mo_yuan", "x": 24, "y": 24, "role": "demon_lord",
     "schedule": {"00:00": "cultivate", "12:00": "court", "18:00": "wander"},
     "knowledge": {"demon_technique": True, "karma_secret": True},
     "goals": ["conquer_world", "gather_dark_cultivator"], "relationship": -50, "hostile": True,
     "dialogue": {"default": "嘿嘿，正道伪君子，来我魔渊做什么？想入魔道吗？",
                  "high_relation": "你既与我魔道为伍，这魔功便传你。"}},
    # 天界
    {"id": "npc_jade_emperor", "name": "玉帝", "title": "渡劫后期·天界之主", "realm": "tribulation_5",
     "region": "tian_jie", "x": 48, "y": 55, "role": "jade_emperor",
     "schedule": {"06:00": "court", "12:00": "rest", "18:00": "cultivate", "22:00": "sleep"},
     "knowledge": {"heaven_secrets": True, "all_realm_info": True},
     "goals": ["maintain_heaven"], "relationship": 0,
     "dialogue": {"default": "凡人修士，竟能飞升至此，汝之机缘不浅。",
                  "high_relation": "汝有大功于天界，赐汝仙籍。"}},
    # 随机生成的散修NPC（5个）
    {"id": "npc_random_1", "name": "云游道人", "title": "筑基初期·散修", "realm": "foundation_1",
     "region": "fang_market", "x": 20, "y": 24, "role": "wanderer",
     "schedule": {"06:00": "wake_up", "08:00": "wander", "12:00": "meal", "18:00": "tavern", "22:00": "sleep"},
     "knowledge": {"treasure_rumor": True}, "goals": ["find_treasure"], "relationship": 0,
     "dialogue": {"default": "贫道云游四方，道友可曾听闻什么宝物现世？"}},
    {"id": "npc_random_2", "name": "落魄书生", "title": "练气三层·读书人", "realm": "qi_refining_3",
     "region": "fan_ren_guo_du", "x": 18, "y": 14, "role": "scholar",
     "schedule": {"06:00": "wake_up", "07:00": "study", "12:00": "meal", "14:00": "study", "18:00": "tea", "22:00": "sleep"},
     "knowledge": {"ancient_books": True, "history": True}, "goals": ["pass_exam"], "relationship": 0,
     "dialogue": {"default": "书中自有黄金屋，书中自有颜如玉。道友可愿听我讲古？"}},
    {"id": "npc_random_3", "name": "神秘老者", "title": "？？·高人", "realm": "unknown",
     "region": "beast_mountain", "x": 30, "y": 30, "role": "mysterious_elder",
     "schedule": {"00:00": "meditate"},
     "knowledge": {"everything": True}, "goals": ["find_successor"], "relationship": 0,
     "dialogue": {"default": "天道有缺，万物皆可逆。年轻人，你可愿听老夫一言？",
                  "high_relation": "你是有缘人，这逆道残卷送你。"}},
    {"id": "npc_random_4", "name": "采药少女", "title": "练气一层·凡人", "realm": "qi_refining_1",
     "region": "beast_mountain", "x": 26, "y": 14, "role": "herb_gatherer",
     "schedule": {"06:00": "wake_up", "07:00": "gather_herb", "12:00": "rest", "14:00": "gather_herb", "18:00": "return", "22:00": "sleep"},
     "knowledge": {"herb_location": True}, "goals": ["gather_herb", "survive"], "relationship": 10,
     "dialogue": {"default": "道友小心，这山脉里有妖兽出没。"}} ,
    {"id": "npc_random_5", "name": "落难公主", "title": "凡人·皇族", "realm": "mortal",
     "region": "beast_mountain", "x": 18, "y": 20, "role": "princess",
     "schedule": {"06:00": "hide", "12:00": "hide", "18:00": "hide", "22:00": "sleep"},
     "knowledge": {"royal_secret": True}, "goals": ["escape", "find_help"], "relationship": 0,
     "dialogue": {"default": "仙长救我！我是洛京公主，被妖兽追杀至此。",
                  "high_relation": "仙长大恩大德，他日必当重谢。"}},
]
save("npcs", {"npcs": npcs})


# ============================================================
# 8. 宗门系统（10个宗门）
# ============================================================
sects = [
    {"id": "qingyun_sect_info", "name": "青云宗", "type": "orthodox", "alignment": "good",
     "realm_required": "qi_refining_1", "leader": "npc_master_qingyun",
     "description": "正道大宗，传承千年，掌门元婴期，门下弟子数千。",
     "positions": ["掌门", "长老", "执事", "内门弟子", "外门弟子", "记名弟子"],
     "benefits": {"spirit_density_bonus": 0.2, "technique_access": ["wood_basic", "fire_basic", "ice_basic", "metal_basic", "earth_basic"]},
     "rules": ["不得残害同门", "不得泄露宗门机密", "每月需完成门派任务"],
     "treasury": 100000, "members": 500},
    {"id": "blood_demon_sect", "name": "血魔宗", "type": "demon", "alignment": "evil",
     "realm_required": "foundation_1", "leader": "npc_demon_lord",
     "description": "魔道大宗，以血炼功，正道之敌。",
     "positions": ["魔主", "护法", "长老", "魔使", "魔子", "魔兵"],
     "benefits": {"cultivation_speed_bonus": 0.3, "karma_cost": -100},
     "rules": ["强者为尊", "弱肉强食"],
     "treasury": 50000, "members": 200},
    {"id": "dan_dao_zong", "name": "丹道宗", "type": "orthodox", "alignment": "neutral",
     "realm_required": "qi_refining_3", "leader": "npc_dan_master",
     "description": "专精炼丹的宗门，丹药天下第一。",
     "positions": ["宗主", "丹师", "丹徒", "杂役"],
     "benefits": {"alchemy_bonus": 0.3, "pill_access": True},
     "rules": ["不得私售宗门丹方"],
     "treasury": 200000, "members": 150},
    {"id": "qi_zong", "name": "器宗", "type": "orthodox", "alignment": "neutral",
     "realm_required": "qi_refining_3", "leader": "npc_qi_master",
     "description": "专精炼器的宗门，法器天下第一。",
     "positions": ["宗主", "器师", "器徒", "杂役"],
     "benefits": {"forge_bonus": 0.3, "weapon_access": True},
     "rules": ["不得私售宗门器方"],
     "treasury": 200000, "members": 150},
    {"id": "wan_yao_men", "name": "万兽门", "type": "neutral", "alignment": "neutral",
     "realm_required": "foundation_1", "leader": "npc_beast_master",
     "description": "专精御兽的宗门，与妖兽为友。",
     "positions": ["门主", "御兽师", "兽使", "杂役"],
     "benefits": {"tame_bonus": 0.3, "beast_access": True},
     "rules": ["不得残害门中灵兽"],
     "treasury": 80000, "members": 100},
    {"id": "jian_ge", "name": "剑阁", "type": "orthodox", "alignment": "good",
     "realm_required": "foundation_3", "leader": "npc_jian_master",
     "description": "剑修圣地，一剑破万法。",
     "positions": ["阁主", "剑师", "剑徒", "杂役"],
     "benefits": {"sword_bonus": 0.5, "attack_bonus": 0.2},
     "rules": ["剑在人在，剑毁人亡"],
     "treasury": 120000, "members": 80},
    {"id": "fu_zong", "name": "符箓宗", "type": "orthodox", "alignment": "neutral",
     "realm_required": "qi_refining_5", "leader": "npc_fu_master",
     "description": "专精符箓的宗门。",
     "positions": ["宗主", "符师", "符徒", "杂役"],
     "benefits": {"talisman_bonus": 0.3},
     "rules": ["不得伪造符箓"],
     "treasury": 100000, "members": 120},
    {"id": "zhen_fa_men", "name": "阵法门", "type": "orthodox", "alignment": "neutral",
     "realm_required": "foundation_1", "leader": "npc_zhen_master",
     "description": "专精阵法的宗门。",
     "positions": ["门主", "阵师", "阵徒", "杂役"],
     "benefits": {"formation_bonus": 0.3},
     "rules": ["不得私设杀阵"],
     "treasury": 90000, "members": 90},
    {"id": "hua_shen_men", "name": "化神门", "type": "orthodox", "alignment": "good",
     "realm_required": "golden_core_1", "leader": "npc_huashen_master",
     "description": "化神期才能加入的高阶宗门。",
     "positions": ["门主", "长老", "弟子"],
     "benefits": {"breakthrough_bonus": 0.2},
     "rules": ["不得下界作乱"],
     "treasury": 500000, "members": 30},
    {"id": "tian_ji_ge", "name": "天机阁", "type": "neutral", "alignment": "neutral",
     "realm_required": "foundation_5", "leader": "npc_tianji_master",
     "description": "知晓天下事的神秘组织，卖情报为生。",
     "positions": ["阁主", "天机师", "天机徒"],
     "benefits": {"info_access": True},
     "rules": ["不得泄露天机"],
     "treasury": 300000, "members": 50},
]
save("sects", {"sects": sects})


# ============================================================
# 9. 剧情/任务链（10条主线）
# ============================================================
storylines = [
    {"id": "main_reverse_jade", "name": "逆道玉简之谜", "chapters": [
        {"id": "ch1", "name": "玉简苏醒", "trigger": "game_start", "objective": "前往青云宗拜师", "reward": {"exp": 50}},
        {"id": "ch2", "name": "藏经阁寻秘", "trigger": "join_qingyun", "objective": "向赵长老请教玉简来历", "reward": {"exp": 100, "item": "wood_slip"}},
        {"id": "ch3", "name": "逆修之路", "trigger": "learn_technique", "objective": "使用玉简逆转功法缺陷", "reward": {"exp": 200}},
        {"id": "ch4", "name": "魔修觊觎", "trigger": "foundation_1", "objective": "击败前来抢夺的魔修", "reward": {"exp": 500, "item": "storage_ring_low"}},
        {"id": "ch5", "name": "天道碎片", "trigger": "golden_core_1", "objective": "寻找天道碎片", "reward": {"exp": 2000}}
    ]},
    {"id": "main_revenge", "name": "血色禁地之谜", "chapters": [
        {"id": "ch1", "name": "禁地开启", "trigger": "foundation_3", "objective": "进入血色禁地", "reward": {"exp": 300}},
        {"id": "ch2", "name": "上古战场", "trigger": "enter_xue_se", "objective": "探索古战场遗迹", "reward": {"exp": 500, "item": "star_iron"}},
        {"id": "ch3", "name": "传承之秘", "trigger": "find_relic", "objective": "获得上古传承", "reward": {"exp": 1000, "technique": "void_basic"}}
    ]},
    {"id": "main_dragon", "name": "龙宫寻宝", "chapters": [
        {"id": "ch1", "name": "海难", "trigger": "nascent_soul_1", "objective": "救助遇险的龙族", "reward": {"exp": 1000}},
        {"id": "ch2", "name": "龙宫赴宴", "trigger": "save_dragon", "objective": "前往龙宫", "reward": {"exp": 2000, "item": "dragon_scale"}},
        {"id": "ch3", "name": "宝库选择", "trigger": "enter_long_gong", "objective": "在龙宫宝库中选择一件宝物", "reward": {"item": "choice"}}
    ]},
    {"id": "side_mortal_kindness", "name": "凡人恩情", "chapters": [
        {"id": "ch1", "name": "救死扶伤", "trigger": "help_mortal", "objective": "救助一个凡人家庭", "reward": {"karma": 50}},
        {"id": "ch2", "name": "后裔成才", "trigger": "30_years_pass", "objective": "等待凡人后裔成长", "reward": {"karma": 100}},
        {"id": "ch3", "name": "回报之恩", "trigger": "50_years_pass", "objective": "接受后裔的报恩", "reward": {"exp": 5000, "item": "rare"}}
    ]},
    {"id": "side_sect_war", "name": "正魔大战", "chapters": [
        {"id": "ch1", "name": "导火索", "trigger": "kill_demon", "objective": "击败魔修", "reward": {"karma": 20}},
        {"id": "ch2", "name": "全面开战", "trigger": "sect_war_start", "objective": "参与正魔大战", "reward": {"exp": 3000}},
        {"id": "ch3", "name": "决战魔主", "trigger": "reach_demon_lord", "objective": "击败魔渊之主", "reward": {"exp": 10000, "item": "legendary"}}
    ]}
]
save("storylines", {"storylines": storylines})


# ============================================================
# 10. 因果链（15条）
# ============================================================
causal_chains = [
    {"id": "chain_betrayal", "name": "背叛之链", "trigger": "player_kills_sect_member",
     "steps": [
         {"trigger": "player_kills_sect_member", "delay": 0, "effect": "sect_relation=-100, bounty_posted=true", "log": "你杀了同门！宗门悬赏通缉你。"},
         {"trigger": "bounty_posted", "delay": "3_day", "effect": "spawn_bounty_hunters", "log": "悬赏引来赏金猎人。"},
         {"trigger": "player_kills_bounty_hunter", "delay": "1_day", "effect": "bounty_increase", "log": "赏金提高，更强追杀者出现。"},
         {"trigger": "player_survives_10_hunters", "delay": 0, "effect": "dark_sect_recruiter_visit", "log": "魔门使者前来招揽。"},
         {"trigger": "player_joins_dark_sect", "delay": "30_day", "effect": "sect_war", "log": "正魔大战爆发。"}
     ]},
    {"id": "chain_pill_leak", "name": "丹药泄密", "trigger": "player_crafts_rare_pill",
     "steps": [
         {"trigger": "player_crafts_rare_pill", "delay": 0, "effect": "rumor_spread", "log": "你炼出极品丹药的消息不胫而走。"},
         {"trigger": "rumor_spread", "delay": "1_day", "effect": "attract_greedy_npc", "log": "引来觊觎之人。"},
         {"trigger": "npc_demand_pill", "delay": "2_day", "effect": "choice:give_or_refuse", "log": "有人上门强索丹药。"}
     ]},
    {"id": "chain_revenge_son", "name": "复仇之子", "trigger": "player_kills_weak_npc",
     "steps": [
         {"trigger": "player_kills_weak_npc", "delay": 0, "effect": "record_victim", "log": "你击杀了一名看似普通的修士。"},
         {"trigger": "record_victim", "delay": "7_day", "effect": "strong_relative_seeks_revenge", "log": "死者长辈出手追杀。"},
         {"trigger": "player_kills_relative", "delay": "30_day", "effect": "sect_war_declared", "log": "死者宗门对你宣战。"}
     ]},
    {"id": "chain_butterfly_kindness", "name": "蝴蝶之恩", "trigger": "player_helps_mortal",
     "steps": [
         {"trigger": "player_helps_mortal", "delay": 0, "effect": "mortal_grateful", "log": "你帮助了一个凡人。"},
         {"trigger": "mortal_grateful", "delay": "365_day", "effect": "mortal_descendant_talent", "log": "凡人后裔展现修行天赋。"},
         {"trigger": "mortal_descendant_talent", "delay": "1825_day", "effect": "descendant_helps_player", "log": "当年的善举，今日得报。"}
     ]},
    {"id": "chain_deforestation", "name": "滥伐之祸", "trigger": "player_cuts_many_trees",
     "steps": [
         {"trigger": "player_cuts_many_trees", "delay": 0, "effect": "habitat_destroyed", "log": "你大量砍伐树木。"},
         {"trigger": "habitat_destroyed", "delay": "1_day", "effect": "tree_spirit_angry", "log": "树妖之灵苏醒。"},
         {"trigger": "tree_spirit_angry", "delay": "2_day", "effect": "tree_spirit_attack", "log": "树妖向你袭来。"}
     ]},
    {"id": "chain_pill_empire", "name": "丹药帝国", "trigger": "player_crafts_100_pills",
     "steps": [
         {"trigger": "player_crafts_100_pills", "delay": 0, "effect": "pill_master_reputation", "log": "你成为知名炼丹师。"},
         {"trigger": "pill_master_reputation", "delay": "30_day", "effect": "disciples_seek", "log": "有弟子前来拜师。"},
         {"trigger": "disciples_seek", "delay": "90_day", "effect": "establish_pill_sect", "log": "你建立了自己的丹道宗门。"}
     ]},
    {"id": "chain_beast_tide", "name": "兽潮预警", "trigger": "player_kills_50_beasts",
     "steps": [
         {"trigger": "player_kills_50_beasts", "delay": 0, "effect": "beast_anger_rising", "log": "妖兽似乎在集结。"},
         {"trigger": "beast_anger_rising", "delay": "7_day", "effect": "beast_tide_warning", "log": "兽潮将至！"},
         {"trigger": "beast_tide_warning", "delay": "3_day", "effect": "beast_tide_event", "log": "兽潮爆发！"}
     ]},
    {"id": "chain_dark_cultivator_ambush", "name": "魔修伏击", "trigger": "player_has_reverse_jade_visible",
     "steps": [
         {"trigger": "player_has_reverse_jade_visible", "delay": "30_day", "effect": "dark_cultivator_notice", "log": "魔修注意到了你。"},
         {"trigger": "dark_cultivator_notice", "delay": "7_day", "effect": "first_ambush", "log": "魔修前来试探。"},
         {"trigger": "player_survives_ambush", "delay": "30_day", "effect": "stronger_ambush", "log": "更强的魔修来袭。"}
     ]},
    {"id": "chain_breakthrough_master", "name": "突破之师", "trigger": "player_breakthrough_foundation",
     "steps": [
         {"trigger": "player_breakthrough_foundation", "delay": 0, "effect": "master_proud", "log": "师父为你骄傲。"},
         {"trigger": "master_proud", "delay": 0, "effect": "master_gift_technique", "log": "师父传授高阶功法。"}
     ]},
    {"id": "chain_lifespan_crisis", "name": "寿元危机", "trigger": "player_lifespan_below_20",
     "steps": [
         {"trigger": "player_lifespan_below_20", "delay": 0, "effect": "urgent_seek_pill", "log": "寿元将尽，必须立刻寻找延寿丹！"},
         {"trigger": "urgent_seek_pill", "delay": "10_day", "effect": "npc_offer_help", "log": "有人愿意帮你寻找延寿丹。"}
     ]}
]
save("causal_chains", {"causal_chains": causal_chains})


print("\nPart 2 数据生成完成！")
