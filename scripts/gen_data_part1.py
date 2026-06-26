"""
《逆仙录·天道残卷》数据生成器
程序化生成丰富的游戏数据（材料/功法/丹药/妖兽/区域/NPC/宗门）
基于种子可复现，类似鬼谷八荒的随机生成方式
"""
import json
import os
import random
import hashlib

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 固定主种子，保证数据可复现
MASTER_SEED = 20260626
random.seed(MASTER_SEED)


def save(name, data):
    path = os.path.join(DATA_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  生成 {name}.json: {len(data) if isinstance(data, list) else len(data.keys())} 条")


# ============================================================
# 1. 境界定义
# ============================================================
REALMS = [
    # id, 名称, 寿元上限, 灵气容量倍数, 攻防倍数
    ("qi_refining_1", "练气一层", 120, 1, 1),
    ("qi_refining_2", "练气二层", 120, 1.2, 1.1),
    ("qi_refining_3", "练气三层", 120, 1.5, 1.2),
    ("qi_refining_4", "练气四层", 120, 1.8, 1.3),
    ("qi_refining_5", "练气五层", 120, 2.2, 1.5),
    ("qi_refining_6", "练气六层", 120, 2.6, 1.7),
    ("qi_refining_7", "练气七层", 120, 3.0, 1.9),
    ("qi_refining_8", "练气八层", 120, 3.5, 2.1),
    ("qi_refining_9", "练气九层", 120, 4.0, 2.3),
    ("foundation_1", "筑基初期", 200, 8, 4),
    ("foundation_3", "筑基中期", 200, 12, 5),
    ("foundation_5", "筑基后期", 200, 16, 6),
    ("foundation_7", "筑基大圆满", 200, 20, 7),
    ("golden_core_1", "金丹初期", 500, 40, 12),
    ("golden_core_3", "金丹中期", 500, 60, 15),
    ("golden_core_5", "金丹后期", 500, 80, 18),
    ("golden_core_9", "金丹大圆满", 500, 100, 22),
    ("nascent_soul_1", "元婴初期", 1000, 200, 35),
    ("nascent_soul_3", "元婴中期", 1000, 300, 45),
    ("nascent_soul_5", "元婴后期", 1000, 400, 55),
    ("divine_transformation_1", "化神初期", 3000, 800, 90),
    ("divine_transformation_3", "化神中期", 3000, 1200, 120),
    ("divine_transformation_5", "化神后期", 3000, 1600, 150),
    ("void_refining_1", "炼虚初期", 10000, 3000, 250),
    ("void_refining_3", "炼虚中期", 10000, 5000, 350),
    ("void_refining_5", "炼虚后期", 10000, 8000, 500),
    ("body_integration_1", "合体初期", 30000, 15000, 800),
    ("body_integration_3", "合体中期", 30000, 25000, 1200),
    ("body_integration_5", "合体后期", 30000, 40000, 1800),
    ("mahayana_1", "大乘初期", 100000, 80000, 3000),
    ("mahayana_3", "大乘中期", 100000, 150000, 5000),
    ("mahayana_5", "大乘后期", 100000, 250000, 8000),
    ("tribulation_1", "渡劫初期", 500000, 500000, 15000),
    ("tribulation_3", "渡劫中期", 500000, 800000, 25000),
    ("tribulation_5", "渡劫后期", 500000, 1200000, 40000),
]

save("realms", {
    "realms": [{"id": r[0], "name": r[1], "lifespan": r[2], "qi_mult": r[3], "combat_mult": r[4]} for r in REALMS]
})


# ============================================================
# 2. 材料系统（100+ 种）
# ============================================================
def gen_materials():
    materials = []

    # --- 草药（40种，1-7阶） ---
    herbs = [
        # (id, 名, 阶, 主属性, 属性值, 灵气, 价值, 稀有度, 描述)
        ("yun_ling_grass", "云灵草", 1, "wood", 10, 20, 5, "common", "最常见灵草，山谷湿润处生长，含微弱木灵气。"),
        ("qing_xin_lotus", "清心莲", 2, "water", 15, 35, 15, "common", "白色莲花，服之可清心宁神，是炼制安神丹的主药。"),
        ("chi_yan_grass", "赤炎草", 2, "fire", 25, 30, 18, "common", "生于火山附近，叶红如焰，触之灼手。"),
        ("bing_lotus", "冰莲", 3, "ice", 35, 50, 40, "uncommon", "极寒之地生长，花开如冰雕，可解火毒。"),
        ("ling_zhi_100", "百年灵芝", 3, "wood", 40, 80, 80, "uncommon", "百年灵气滋养，可延寿炼丹。"),
        ("long_xu_grass", "龙须草", 4, "wood", 50, 70, 200, "rare", "形似龙须，传闻龙族路过所留，炼丹佳品。"),
        ("feng_xi_grass", "凤栖草", 5, "fire", 80, 100, 350, "epic", "传闻凤凰栖息之地生长，含涅槃之意。"),
        ("ling_zhi_500", "五百年灵芝", 5, "wood", 80, 250, 600, "epic", "五百年灵气所钟，延寿神效。"),
        ("ji_nian_grass", "寂灭草", 6, "soul", 100, 200, 1200, "epic", "生于古战场，含死气与寂灭之意，慎用。"),
        ("tai_sui_grass", "太岁草", 7, "earth", 150, 400, 3000, "legendary", "传闻肉灵芝遗种，服之可重塑肉身。"),
        ("xuan_bing_grass", "玄冰草", 3, "ice", 40, 55, 60, "uncommon", "万年冰川所生，寒气逼人。"),
        ("jiuyou_grass", "九幽草", 6, "dark", 90, 180, 1500, "epic", "九幽冥土所生，可通幽冥，极阴之物。"),
        ("san_qing_grass", "三清草", 5, "light", 70, 120, 800, "epic", "三清道场遗种，炼制道丹主药。"),
        ("wu_wei_grass", "五味草", 2, "wood", 18, 25, 12, "common", "五味俱全，调和诸药。"),
        ("zi_xia_grass", "紫霞草", 4, "light", 60, 90, 280, "rare", "紫气东来所化，炼制紫霞丹。"),
        ("tai_yin_grass", "太阴草", 4, "ice", 55, 85, 250, "rare", "月华所钟，阴气极重。"),
        ("tai_yang_grass", "太阳草", 4, "fire", 55, 85, 250, "rare", "日华所钟，阳气极盛。"),
        ("hun_dun_grass", "混沌草", 7, "void", 200, 500, 5000, "legendary", "天地初开遗留，混沌之气所化。"),
        ("xian_zhi_1000", "千年灵芝", 6, "wood", 120, 400, 2500, "legendary", "千年灵气所钟，仙药之流。"),
        ("bi_xue_grass", "碧血草", 3, "fire", 35, 45, 55, "uncommon", "古战场鲜血所养，煞气重。"),
        # 新增 20 种草药
        ("bai_lu_grass", "白露草", 1, "water", 8, 15, 4, "common", "晨露所凝，清凉润喉。"),
        ("zi_ye_grass", "紫叶草", 1, "wood", 9, 18, 5, "common", "紫色叶片，常见炼丹辅药。"),
        ("han_yan_grass", "寒烟草", 2, "ice", 20, 28, 14, "common", "生于阴寒之地，叶带白霜。"),
        ("lie_yan_grass", "烈焰草", 2, "fire", 22, 30, 16, "common", "叶红似火，灼热异常。"),
        ("feng_yin_grass", "风音草", 2, "wind", 18, 25, 13, "common", "风吹之有声，可炼音波功法。"),
        ("lei_xin_grass", "雷芯草", 3, "thunder", 35, 50, 65, "uncommon", "雷击之地所生，含雷意。"),
        ("dian_xin_grass", "电芯草", 3, "thunder", 32, 45, 60, "uncommon", "雷电所钟，触之麻手。"),
        ("he_shou_wu", "何首乌", 3, "wood", 45, 70, 90, "uncommon", "百年首乌，延年益寿。"),
        ("ren_shen_grass", "人参果", 4, "wood", 60, 100, 220, "rare", "三千年一开花，三千年一结果。"),
        ("xian_tao_grass", "仙桃草", 5, "wood", 90, 150, 700, "epic", "仙桃园所遗，服之延寿百年。"),
        ("bi_an_grass", "彼岸花", 5, "soul", 80, 130, 650, "epic", "黄泉路边所开，通阴阳。"),
        ("mo_zhi_grass", "魔芝草", 5, "dark", 75, 120, 580, "epic", "魔气所生，魔修挚爱。"),
        ("fo_xin_grass", "佛心草", 5, "light", 78, 125, 600, "epic", "佛门圣物，可镇压心魔。"),
        ("dao_zhong_grass", "道种草", 6, "void", 110, 200, 1800, "epic", "大道种子所化，悟道佳品。"),
        ("xian_yi_grass", "仙意草", 6, "light", 105, 190, 1600, "epic", "仙气所钟，凡人不可近。"),
        ("mo_yi_grass", "魔意草", 6, "dark", 105, 190, 1600, "epic", "魔意所聚，正修慎用。"),
        ("tian_xin_grass", "天心草", 7, "void", 180, 450, 4500, "legendary", "天心所钟，传说可窥天道。"),
        ("di_xin_grass", "地心草", 7, "earth", 175, 440, 4200, "legendary", "地心火脉所生，至刚至阳。"),
        ("xian_luan_grass", "仙鸾草", 7, "light", 185, 460, 4800, "legendary", "仙鸾所食，仙家灵草。"),
        ("mo_long_grass", "魔龙草", 7, "dark", 185, 460, 4800, "legendary", "魔龙所养，至阴至煞。"),
    ]
    for hid, name, tier, elem, val, qi, price, rar, desc in herbs:
        attrs = {"spiritual_energy": qi}
        attrs[f"{elem}_affinity"] = val
        attrs["freshness"] = 100
        materials.append({
            "id": hid, "name": name, "type": "herb", "tier": tier,
            "element": elem, "attrs": attrs,
            "value": price, "rarity": rar, "desc": desc,
            "known": tier <= 2  # 1-2阶默认已知，3+需学习
        })

    # --- 矿石（30种） ---
    ores = [
        ("han_iron", "寒铁矿", 2, "ice", 60, 20, "寒气森森，炼器基础材料。"),
        ("chi_copper", "赤铜矿", 2, "fire", 50, 22, "赤红如血，火属性材料。"),
        ("xuan_iron", "玄铁矿", 3, "metal", 80, 60, "深黑色，硬度极高，炼器上品。"),
        ("ling_crystal", "灵晶石", 3, "spirit", 70, 80, "蕴含灵气，可作阵法核心。"),
        ("purple_gold", "紫金", 4, "metal", 90, 180, "紫光闪闪，灵气传导极佳。"),
        ("star_iron", "陨星铁", 5, "metal", 120, 400, "天外陨铁，含星力。"),
        ("tian_yuan_iron", "天元铁", 6, "metal", 160, 1500, "天地元气所凝，至坚。"),
        ("xian_yin_shi", "仙银石", 7, "metal", 220, 4500, "仙家遗物，银光夺目。"),
        ("bing_jing", "冰晶", 3, "ice", 70, 70, "千年寒冰所化，可炼冰系法宝。"),
        ("huo_jing", "火晶", 3, "fire", 70, 70, "地心火脉所结，可炼火系法宝。"),
        ("lei_jing", "雷晶", 4, "thunder", 90, 200, "雷霆所凝，威力惊人。"),
        ("feng_jing", "风晶", 4, "wind", 85, 180, "飓风核心，速度加成。"),
        ("an_jing", "暗晶", 5, "dark", 110, 380, "暗影所聚，魔修钟爱。"),
        ("guang_jing", "光晶", 5, "light", 110, 380, "光辉所凝，正修至宝。"),
        ("xu_kong_jing", "虚空晶", 6, "void", 150, 1400, "虚空所化，可破空间。"),
        ("long_lin_shi", "龙鳞石", 5, "metal", 130, 500, "传闻龙鳞所化，至坚至韧。"),
        ("feng_yu_shi", "凤羽石", 5, "fire", 130, 500, "传闻凤羽所化，含涅槃意。"),
        ("hu_qiu_shi", "虎丘石", 4, "earth", 95, 220, "虎形山丘所产，土属性。"),
        ("she_tu_shi", "蛇土石", 4, "earth", 90, 200, "蛇盘之地所产，含毒。"),
        ("wu_jin_shi", "乌金石", 3, "metal", 75, 75, "黑色金属，坚硬。"),
        ("bai_yin_shi", "白银石", 2, "metal", 55, 25, "白银矿，常见。"),
        ("huang_jin_shi", "黄金石", 3, "metal", 78, 90, "黄金矿，价值较高。"),
        ("shan_jing_shi", "山精石", 4, "earth", 95, 230, "山岳精华所凝。"),
        ("shui_jing_shi", "水精石", 3, "water", 72, 72, "水底所产，灵气清澈。"),
        ("mu_jing_shi", "木精石", 3, "wood", 72, 72, "古木所产，含木灵气。"),
        ("ri_jing_shi", "日精石", 5, "light", 120, 420, "日华所钟。"),
        ("yue_jing_shi", "月精石", 5, "ice", 120, 420, "月华所钟。"),
        ("chen_jing_shi", "辰精石", 6, "void", 145, 1300, "星辰之力所凝。"),
        ("xian_tie", "仙铁", 7, "metal", 200, 4000, "仙家所用之铁。"),
        ("mo_tie", "魔铁", 6, "dark", 155, 1400, "魔气所侵之铁。"),
    ]
    for oid, name, tier, elem, hardness, price, desc in ores:
        materials.append({
            "id": oid, "name": name, "type": "ore", "tier": tier,
            "element": elem, "attrs": {"hardness": hardness, "toughness": int(hardness * 0.8), "durability": 100},
            "value": price, "rarity": "common" if tier <= 2 else ("uncommon" if tier <= 3 else ("rare" if tier <= 4 else ("epic" if tier <= 6 else "legendary"))),
            "desc": desc, "known": tier <= 3
        })

    # --- 妖兽材料（25种） ---
    beast_parts = [
        ("tiger_fur", "赤焰虎皮", 3, "fire", 30, 25, 50, "赤焰虎之皮，火抗加成。"),
        ("tiger_claw", "虎爪", 3, "fire", 50, 0, 45, "锋利异常，可炼利器。"),
        ("tiger_core", "赤焰虎妖丹", 3, "fire", 60, 80, 150, "蕴含虎之精魄与火灵气。"),
        ("wolf_fur", "冰狼皮", 3, "ice", 30, 22, 48, "冰狼之皮，冰抗加成。"),
        ("wolf_core", "冰狼妖丹", 3, "ice", 60, 80, 150, "蕴含狼之精魄与冰灵气。"),
        ("snake_core", "青木蟒妖丹", 4, "wood", 70, 100, 280, "蕴含蟒之精魄与木灵气。"),
        ("scorpion_core", "金甲蝎妖丹", 4, "metal", 70, 100, 280, "蕴含蝎之精魄与金灵气。"),
        ("leopard_core", "风行豹妖丹", 4, "wind", 70, 100, 280, "蕴含豹之精魄与风灵气。"),
        ("dragon_scale", "蛟龙鳞", 6, "water", 200, 300, 2500, "蛟龙之鳞，至坚至韧，水属性。"),
        ("phoenix_feather", "凤翎", 7, "fire", 250, 350, 4500, "凤凰之羽，含涅槃意，至宝。"),
        ("fox_tail", "九尾狐尾", 5, "illusion", 100, 150, 800, "九尾狐之尾，幻术佳品。"),
        ("basilisk_eye", "蛇怪之眼", 4, "earth", 80, 120, 320, "蛇怪之眼，可炼摄魂法宝。"),
        ("qilin_horn", "麒麟角", 7, "light", 240, 400, 5000, "麒麟之角，仙家至宝。"),
        ("black_turtle_shell", "玄武甲", 7, "water", 260, 350, 4800, "玄武之甲，防御无双。"),
        ("white_tiger_fang", "白虎牙", 6, "metal", 180, 280, 2200, "白虎之牙，锐利无匹。"),
        ("azure_dragon_whisker", "青龙须", 6, "wood", 170, 260, 2000, "青龙之须，木属性圣物。"),
        ("vermillion_bird_feather", "朱雀羽", 7, "fire", 255, 380, 4900, "朱雀之羽，火属性至宝。"),
        ("snake_gallbladder", "蟒蛇胆", 4, "wood", 75, 110, 300, "可炼明目丹。"),
        ("bear_paw", "熊掌", 3, "earth", 50, 0, 60, "猛熊之掌，可炼大力丹。"),
        ("eagle_claw", "鹰爪", 3, "wind", 55, 0, 55, "苍鹰之爪，锐利。"),
        ("centipede_core", "蜈蚣妖丹", 4, "earth", 65, 95, 260, "百足蜈蚣之丹，含毒。"),
        ("spider_silk", "蛛丝", 3, "wind", 40, 0, 70, "妖蛛之丝，坚韧异常。"),
        ("bat_wing", "蝙蝠翼", 2, "dark", 25, 0, 20, "夜行蝙蝠之翼。"),
        ("rhino_horn", "犀角", 4, "earth", 85, 0, 200, "灵犀之角，可解百毒。"),
        ("deer_antler", "鹿茸", 3, "wood", 50, 60, 90, "灵鹿之茸，大补。"),
    ]
    for pid, name, tier, elem, val, qi, price, desc in beast_parts:
        attrs = {f"{elem}_affinity": val}
        if qi > 0:
            attrs["spiritual_energy"] = qi
        attrs["beast_core_quality"] = tier
        materials.append({
            "id": pid, "name": name, "type": "beast_part", "tier": tier,
            "element": elem, "attrs": attrs,
            "value": price, "rarity": "common" if tier <= 2 else ("uncommon" if tier <= 3 else ("rare" if tier <= 4 else ("epic" if tier <= 6 else "legendary"))),
            "desc": desc, "known": tier <= 3
        })

    # --- 丹药（25种） ---
    pills = [
        ("qi_pill", "回气丹", 1, {"restore_qi": 30}, 10, "common", "恢复30点灵气，新手必备。"),
        ("flesh_renew_pill", "续骨丹", 2, {"heal_hp": 50}, 30, "common", "恢复50点气血，治愈外伤。"),
        ("foundation_pill", "筑基丹", 3, {"breakthrough_assist": 0.3}, 500, "rare", "突破筑基时使用，成功率+30%。"),
        ("golden_core_pill", "结金丹", 4, {"breakthrough_assist": 0.4}, 1500, "epic", "突破金丹时使用，成功率+40%。"),
        ("lifespan_pill", "延寿丹", 4, {"add_lifespan": 10}, 2000, "epic", "延寿10年，每类限服3次。"),
        ("fire_resist_pill", "避火丹", 2, {"fire_resist": 50, "duration": 600}, 80, "uncommon", "火抗+50，持续10分钟。"),
        ("ice_resist_pill", "避寒丹", 2, {"ice_resist": 50, "duration": 600}, 80, "uncommon", "冰抗+50，持续10分钟。"),
        ("fury_pill", "狂暴丹", 3, {"attack_boost": 30, "duration": 300}, 200, "rare", "攻击+30，5分钟，副作用：力竭。"),
        ("qi_gathering_pill", "聚气丹", 2, {"cultivate_bonus": 0.2}, 100, "uncommon", "修炼时服用，效率+20%。"),
        ("comprehension_pill", "悟道丹", 4, {"comprehension_boost": 50}, 800, "rare", "悟性+50，持续1小时。"),
        ("detox_pill", "解毒丹", 2, {"detox": 100}, 50, "common", "解除一般毒素。"),
        ("fire_toxin_pill", "清火丹", 3, {"cure_fire_toxin": 1}, 200, "rare", "清除火毒。"),
        ("meridian_pill", "通脉丹", 3, {"meridian_repair": 20}, 300, "rare", "修复经脉20点。"),
        ("dantian_pill", "补天丹", 5, {"dantian_repair": 1}, 3000, "legendary", "修复丹田裂纹1处。"),
        ("foundation_rebuild_pill", "重塑丹", 6, {"rebuild_dantian": 1}, 8000, "legendary", "重塑丹田，逆天之药。"),
        ("spirit_pill", "养神丹", 3, {"spirit_repair": 20}, 250, "rare", "修复神识20点。"),
        ("flesh_pill", "锻体丹", 3, {"flesh_boost": 10}, 200, "rare", "肉身强度+10。"),
        ("invisible_pill", "隐身丹", 4, {"invisible": 600}, 500, "rare", "隐身10分钟。"),
        ("swift_pill", "神行丹", 2, {"speed_boost": 30, "duration": 600}, 60, "common", "速度+30%。"),
        ("power_pill", "力大丹", 2, {"strength_boost": 20, "duration": 600}, 50, "common", "力量+20。"),
        ("heart_devil_pill", "破心魔丹", 5, {"heart_devil_resist": 0.5}, 2000, "epic", "突破时心魔概率-50%。"),
        ("karma_pill", "消业丹", 5, {"karma_cleanse": 100}, 2500, "epic", "消除100点业力。"),
        ("reincarnation_pill", "轮回丹", 7, {"reincarnation_keep": 0.5}, 10000, "legendary", "转世保留50%记忆。"),
        ("tribulation_pill", "渡劫丹", 6, {"tribulation_resist": 0.3}, 5000, "legendary", "渡劫成功率+30%。"),
        ("nine_turn_pill", "九转金丹", 7, {"all_boost": 50, "add_lifespan": 100}, 50000, "legendary", "仙丹，全方位提升，延寿百年。"),
    ]
    for pid, name, tier, effect, price, rar, desc in pills:
        materials.append({
            "id": pid, "name": name, "type": "pill", "tier": tier,
            "attrs": {}, "effect": effect,
            "value": price, "rarity": rar, "desc": desc, "known": tier <= 3
        })

    # --- 武器（20种） ---
    weapons = [
        ("iron_sword", "铁剑", 1, {"damage": 15, "sharpness": 20, "durability": 100}, 30, "common", "凡铁所铸，新手用剑。"),
        ("spirit_sword", "灵纹剑", 3, {"damage": 50, "sharpness": 60, "qi_channeling": 30, "durability": 150}, 300, "uncommon", "刻有灵纹，可灌注灵气。"),
        ("fire_sword", "赤焰剑", 4, {"damage": 80, "fire_affinity": 40, "sharpness": 80, "qi_channeling": 50, "durability": 180}, 800, "rare", "蕴含火灵，挥之生焰。"),
        ("ice_sword", "寒冰剑", 4, {"damage": 75, "ice_affinity": 40, "sharpness": 75, "qi_channeling": 50, "durability": 180}, 800, "rare", "寒气逼人，斩之冻髓。"),
        ("thunder_sword", "雷霆剑", 5, {"damage": 120, "thunder_affinity": 60, "sharpness": 100, "qi_channeling": 80, "durability": 220}, 1800, "epic", "雷霆所凝，斩之麻痹。"),
        ("wind_sword", "风行剑", 4, {"damage": 70, "wind_affinity": 35, "speed_boost": 10, "sharpness": 80, "qi_channeling": 50, "durability": 180}, 750, "rare", "轻盈如风，速度加成。"),
        ("dragon_sword", "青龙剑", 6, {"damage": 200, "wood_affinity": 100, "sharpness": 150, "qi_channeling": 120, "durability": 300}, 5000, "legendary", "青龙之魂所附，威力绝伦。"),
        ("phoenix_sword", "朱雀剑", 6, {"damage": 220, "fire_affinity": 120, "sharpness": 160, "qi_channeling": 130, "durability": 320}, 6000, "legendary", "朱雀之魂所附，涅槃重生。"),
        ("immortal_sword", "仙剑·诛仙", 7, {"damage": 500, "all_affinity": 200, "sharpness": 300, "qi_channeling": 250, "durability": 500}, 50000, "legendary", "上古仙剑，斩仙屠魔。"),
        ("demon_sword", "魔剑·血煞", 6, {"damage": 250, "dark_affinity": 150, "sharpness": 180, "qi_channeling": 100, "durability": 280, "side_effect": "karma"}, 5500, "legendary", "魔气所凝，斩之吸血，但损业力。"),
        ("wood_sword", "青木剑", 2, {"damage": 25, "wood_affinity": 15, "sharpness": 30, "durability": 80}, 80, "common", "青木所制，木属性。"),
        ("earth_sword", "厚土剑", 2, {"damage": 30, "earth_affinity": 18, "sharpness": 25, "durability": 120}, 90, "common", "厚土所铸，坚固耐用。"),
        ("metal_sword", "庚金剑", 3, {"damage": 60, "metal_affinity": 30, "sharpness": 70, "durability": 160}, 350, "uncommon", "庚金所铸，锋利异常。"),
        ("void_sword", "虚空剑", 6, {"damage": 180, "void_affinity": 100, "sharpness": 140, "qi_channeling": 110, "durability": 280}, 4500, "legendary", "虚空所化，可破空间。"),
        ("light_sword", "光明剑", 5, {"damage": 130, "light_affinity": 70, "sharpness": 110, "qi_channeling": 90, "durability": 240}, 2000, "epic", "光明所凝，破邪显正。"),
        ("dark_sword", "暗影剑", 5, {"damage": 140, "dark_affinity": 75, "sharpness": 100, "qi_channeling": 80, "durability": 220}, 1900, "epic", "暗影所聚，杀人无形。"),
        ("poison_sword", "碧毒剑", 3, {"damage": 50, "poison": 30, "sharpness": 55, "durability": 140}, 320, "uncommon", "淬毒之剑，斩之中毒。"),
        ("soul_sword", "诛魂剑", 5, {"damage": 110, "soul_attack": 50, "sharpness": 90, "qi_channeling": 70, "durability": 200}, 1700, "epic", "专伤神魂，防不胜防。"),
        ("bone_sword", "白骨剑", 4, {"damage": 85, "dark_affinity": 30, "sharpness": 75, "durability": 170}, 700, "rare", "妖骨所制，阴气重。"),
        ("crystal_sword", "水晶剑", 3, {"damage": 55, "spiritual_conductivity": 50, "sharpness": 65, "qi_channeling": 40, "durability": 130}, 380, "uncommon", "灵晶所制，灵气传导佳。"),
    ]
    for wid, name, tier, attrs, price, rar, desc in weapons:
        attrs["slot"] = "weapon"
        materials.append({
            "id": wid, "name": name, "type": "weapon", "tier": tier,
            "attrs": attrs, "value": price, "rarity": rar, "desc": desc, "known": tier <= 3
        })

    # --- 防具（15种） ---
    armors = [
        ("cloth_armor", "布衣", 1, {"defense": 5, "durability": 80}, 15, "common", "普通布衣，聊胜于无。"),
        ("leather_armor", "皮甲", 2, {"defense": 20, "durability": 100}, 60, "common", "兽皮所制，轻便耐用。"),
        ("spirit_armor", "灵纹甲", 3, {"defense": 50, "qi_channeling": 20, "durability": 150}, 280, "uncommon", "刻有灵纹，可御灵气。"),
        ("fire_armor", "赤焰甲", 4, {"defense": 80, "fire_resist": 30, "qi_channeling": 30, "durability": 200}, 700, "rare", "火抗加成，火焰不侵。"),
        ("ice_armor", "寒冰甲", 4, {"defense": 80, "ice_resist": 30, "qi_channeling": 30, "durability": 200}, 700, "rare", "冰抗加成，寒气不侵。"),
        ("thunder_armor", "雷霆甲", 5, {"defense": 120, "thunder_resist": 40, "qi_channeling": 50, "durability": 240}, 1600, "epic", "雷霆所凝，雷击不伤。"),
        ("dragon_armor", "青龙甲", 6, {"defense": 200, "wood_resist": 50, "qi_channeling": 100, "durability": 300}, 4500, "legendary", "青龙之鳞所制，防御无双。"),
        ("phoenix_armor", "朱雀甲", 6, {"defense": 220, "fire_resist": 80, "qi_channeling": 110, "durability": 320}, 5500, "legendary", "朱雀之羽所制，烈火不侵。"),
        ("black_turtle_armor", "玄武甲", 7, {"defense": 350, "all_resist": 50, "qi_channeling": 180, "durability": 500}, 30000, "legendary", "玄武之甲，万法不侵。"),
        ("demon_armor", "血煞甲", 5, {"defense": 130, "dark_resist": 40, "qi_channeling": 60, "durability": 240, "side_effect": "karma"}, 1800, "epic", "魔气所凝，防御强悍但损业力。"),
        ("wood_armor", "青木甲", 2, {"defense": 25, "wood_resist": 15, "durability": 90}, 70, "common", "青木所制，木属性。"),
        ("earth_armor", "厚土甲", 3, {"defense": 60, "earth_resist": 25, "durability": 180}, 320, "uncommon", "厚土所铸，最为坚固。"),
        ("metal_armor", "庚金甲", 4, {"defense": 90, "metal_resist": 30, "qi_channeling": 25, "durability": 220}, 750, "rare", "庚金所铸，重甲。"),
        ("light_armor", "光明甲", 5, {"defense": 125, "light_resist": 50, "qi_channeling": 80, "durability": 240}, 1900, "epic", "光明所凝，邪魔不侵。"),
        ("spirit_robe", "道袍", 3, {"defense": 35, "qi_channeling": 40, "all_affinity": 5, "durability": 120}, 300, "uncommon", "道门法袍，灵气流畅。"),
    ]
    for aid, name, tier, attrs, price, rar, desc in armors:
        attrs["slot"] = "armor"
        materials.append({
            "id": aid, "name": name, "type": "armor", "tier": tier,
            "attrs": attrs, "value": price, "rarity": rar, "desc": desc, "known": tier <= 3
        })

    # --- 符箓（15种） ---
    talismans = [
        ("talisman_fire", "火灵符", 2, {"damage": 40, "element": "fire"}, 50, "uncommon", "释放火球，造成40点火属性伤害。"),
        ("talisman_ice", "冰灵符", 2, {"damage": 40, "element": "ice"}, 50, "uncommon", "释放冰锥，造成40点冰属性伤害。"),
        ("talisman_thunder", "雷灵符", 3, {"damage": 70, "element": "thunder"}, 120, "rare", "释放雷电，造成70点雷属性伤害。"),
        ("talisman_heal", "回春符", 2, {"heal_hp": 80}, 60, "uncommon", "恢复80点气血。"),
        ("talisman_shield", "护身符", 3, {"shield": 100, "duration": 300}, 100, "rare", "护盾100点，5分钟。"),
        ("talisman_escape", "遁地符", 3, {"escape": True}, 150, "rare", "紧急遁地，脱离战斗。"),
        ("talisman_invisible", "隐身符", 4, {"invisible": 300}, 300, "rare", "隐身5分钟。"),
        ("talisman_summon", "召唤符", 4, {"summon_tier": 3}, 400, "rare", "召唤3阶妖兽助战。"),
        ("talisman_seal", "封印符", 5, {"seal_target": True}, 800, "epic", "封印目标3回合。"),
        ("talisman_explode", "爆裂符", 3, {"damage": 120, "aoe": True}, 180, "rare", "爆炸造成120点AOE伤害。"),
        ("talisman_wood", "木灵符", 2, {"damage": 35, "element": "wood"}, 45, "uncommon", "释放藤蔓，造成35点木属性伤害。"),
        ("talisman_metal", "金灵符", 2, {"damage": 38, "element": "metal"}, 48, "uncommon", "释放金刃，造成38点金属性伤害。"),
        ("talisman_earth", "土灵符", 2, {"damage": 36, "element": "earth"}, 46, "uncommon", "释放落石，造成36点土属性伤害。"),
        ("talisman_wind", "风灵符", 2, {"damage": 34, "element": "wind"}, 44, "uncommon", "释放风刃，造成34点风属性伤害。"),
        ("talisman_soul", "诛魂符", 5, {"soul_damage": 80}, 700, "epic", "专伤神魂，造成80点神魂伤害。"),
    ]
    for tid, name, tier, effect, price, rar, desc in talismans:
        materials.append({
            "id": tid, "name": name, "type": "talisman", "tier": tier,
            "attrs": {"uses": 1}, "effect": effect,
            "value": price, "rarity": rar, "desc": desc, "known": tier <= 3
        })

    # --- 灵石（4种） ---
    stones = [
        ("spirit_stone_low", "下品灵石", 1, 10, 1, "common", "下品灵石，杂质较多，修炼效率较低。"),
        ("spirit_stone_mid", "中品灵石", 3, 100, 100, "uncommon", "中品灵石，1:100兑换下品。"),
        ("spirit_stone_high", "上品灵石", 5, 1000, 10000, "rare", "上品灵石，1:100兑换中品。"),
        ("spirit_stone_top", "极品灵石", 7, 10000, 1000000, "legendary", "极品灵石，有价无市。"),
    ]
    for sid, name, tier, qi, price, rar, desc in stones:
        materials.append({
            "id": sid, "name": name, "type": "spirit_stone", "tier": tier,
            "attrs": {"spiritual_energy": qi},
            "value": price, "rarity": rar, "desc": desc, "known": True
        })

    # --- 杂物（10种） ---
    misc = [
        ("wood_block", "木材", 1, {"wood_affinity": 5, "durability": 30}, 2, "common", "普通木材。"),
        ("leather", "兽皮", 1, {"durability": 40, "defense": 5}, 5, "common", "普通兽皮。"),
        ("yang_soul_wood", "养魂木", 4, {"soul_nourish": 50, "wood_affinity": 30}, 200, "rare", "滋养神魂之木。"),
        ("storage_ring_low", "储物戒·下品", 3, {"storage_slots": 20}, 500, "rare", "储物空间20格。"),
        ("storage_ring_mid", "储物戒·中品", 5, {"storage_slots": 100}, 5000, "epic", "储物空间100格。"),
        ("storage_ring_high", "储物戒·上品", 7, {"storage_slots": 500}, 50000, "legendary", "储物空间500格。"),
        ("contract_talisman", "契约符", 3, {"tame_power": 50}, 200, "rare", "驯服妖兽用。"),
        ("sound_transmit_talisman", "传音符", 2, {"range": 1000}, 30, "common", "千里传音。"),
        ("jade_slip_blank", "空白玉简", 2, {"storage": 1}, 50, "common", "可记录功法/丹方。"),
        ("reverse_jade", "逆道玉简", 9, {"reverse_power": 100}, 0, "legendary", "可逆转功法缺陷，蕴含逆天之道。"),
    ]
    for mid, name, tier, attrs, price, rar, desc in misc:
        attrs["durability"] = attrs.get("durability", 100)
        materials.append({
            "id": mid, "name": name, "type": "misc", "tier": tier,
            "attrs": attrs, "value": price, "rarity": rar, "desc": desc,
            "known": True
        })

    # --- 功法玉简（10种） ---
    slips = [
        ("wood_slip", "青木诀玉简", 3, "wood_basic", 500, "rare", "记载青木诀。"),
        ("fire_slip", "焚天诀玉简", 3, "fire_basic", 500, "rare", "记载焚天诀。"),
        ("ice_slip", "冰魄诀玉简", 3, "ice_basic", 500, "rare", "记载冰魄诀。"),
        ("metal_slip", "庚金诀玉简", 3, "metal_basic", 500, "rare", "记载庚金诀。"),
        ("earth_slip", "厚土诀玉简", 3, "earth_basic", 500, "rare", "记载厚土诀。"),
        ("wind_slip", "御风诀玉简", 4, "wind_basic", 800, "rare", "记载御风诀。"),
        ("thunder_slip", "九霄雷诀玉简", 5, "thunder_basic", 2000, "epic", "记载九霄雷诀。"),
        ("light_slip", "光明诀玉简", 5, "light_basic", 2000, "epic", "记载光明诀。"),
        ("dark_slip", "九幽诀玉简", 5, "dark_basic", 2000, "epic", "记载九幽诀。"),
        ("void_slip", "虚空诀玉简", 6, "void_basic", 5000, "epic", "记载虚空诀。"),
    ]
    for sid, name, tier, teaches, price, rar, desc in slips:
        materials.append({
            "id": sid, "name": name, "type": "jade_slip", "tier": tier,
            "attrs": {}, "teaches": teaches,
            "value": price, "rarity": rar, "desc": desc, "known": True
        })

    # --- 阵旗阵盘（8种） ---
    formations_items = [
        ("spirit_gather_flag", "聚灵阵旗", 3, {"formation": "spirit_gather", "power": 30}, 200, "rare", "布设聚灵阵用。"),
        ("spirit_gather_disk", "聚灵阵盘", 4, {"formation": "spirit_gather", "power": 60}, 800, "rare", "完整聚灵阵阵盘。"),
        ("defense_flag", "护身阵旗", 3, {"formation": "defense", "power": 30}, 250, "rare", "布设护身阵用。"),
        ("defense_disk", "护身阵盘", 4, {"formation": "defense", "power": 60}, 900, "rare", "完整护身阵阵盘。"),
        ("kill_flag", "杀阵阵旗", 4, {"formation": "kill", "power": 50}, 600, "rare", "布设杀阵用。"),
        ("kill_disk", "杀阵阵盘", 5, {"formation": "kill", "power": 100}, 2500, "epic", "完整杀阵阵盘。"),
        ("illusion_flag", "幻阵阵旗", 4, {"formation": "illusion", "power": 40}, 500, "rare", "布设幻阵用。"),
        ("time_disk", "时间阵盘", 6, {"formation": "time", "power": 10}, 8000, "legendary", "时间阵盘，1日=1年。"),
    ]
    for fid, name, tier, attrs, price, rar, desc in formations_items:
        materials.append({
            "id": fid, "name": name, "type": "formation", "tier": tier,
            "attrs": attrs, "value": price, "rarity": rar, "desc": desc, "known": tier <= 3
        })

    # --- 种子（10种，用于种田） ---
    seeds = [
        ("seed_yun_ling", "云灵草种子", 1, "yun_ling_grass", 50, 10, "common", "种下后5日成熟。"),
        ("seed_qing_xin", "清心莲种子", 2, "qing_xin_lotus", 80, 30, "common", "种下后8日成熟。"),
        ("seed_chi_yan", "赤炎草种子", 2, "chi_yan_grass", 80, 30, "common", "种下后8日成熟。"),
        ("seed_bing_lotus", "冰莲种子", 3, "bing_lotus", 120, 80, "uncommon", "种下后12日成熟。"),
        ("seed_ling_zhi", "灵芝种子", 3, "ling_zhi_100", 150, 100, "uncommon", "种下后15日成熟。"),
        ("seed_long_xu", "龙须草种子", 4, "long_xu_grass", 200, 250, "rare", "种下后20日成熟。"),
        ("seed_feng_xi", "凤栖草种子", 5, "feng_xi_grass", 300, 500, "epic", "种下后30日成熟。"),
        ("seed_he_shou_wu", "何首乌种子", 3, "he_shou_wu", 130, 90, "uncommon", "种下后15日成熟。"),
        ("seed_bai_lu", "白露草种子", 1, "bai_lu_grass", 45, 8, "common", "种下后5日成熟。"),
        ("seed_zi_ye", "紫叶草种子", 1, "zi_ye_grass", 45, 8, "common", "种下后5日成熟。"),
    ]
    for sid, name, tier, plant_id, grow_days, price, rar, desc in seeds:
        materials.append({
            "id": sid, "name": name, "type": "seed", "tier": tier,
            "attrs": {"plant_id": plant_id, "grow_days": grow_days},
            "value": price, "rarity": rar, "desc": desc, "known": True
        })

    return materials


all_materials = gen_materials()
save("materials", {"materials": all_materials})


# ============================================================
# 3. 功法系统（10种，每种5阶段+5技能）
# ============================================================
def gen_techniques():
    techniques = []
    tech_data = [
        ("wood_basic", "青木诀", "wood", 3, 0.7, "木属性基础功法，以生生不息之意炼气，温和平稳。完整度七成，久练经脉有损。"),
        ("fire_basic", "焚天诀", "fire", 3, 0.65, "火属性功法，霸道凌厉，攻伐无双。残缺较多，火毒易攻心。"),
        ("ice_basic", "冰魄诀", "ice", 3, 0.75, "冰属性功法，阴寒凝练，攻守兼备。"),
        ("metal_basic", "庚金诀", "metal", 3, 0.72, "金属性功法，锋锐凌厉，攻伐刚猛。"),
        ("earth_basic", "厚土诀", "earth", 3, 0.78, "土属性功法，厚重绵长，防御无双。"),
        ("wind_basic", "御风诀", "wind", 4, 0.7, "风属性功法，轻灵飘逸，速度加成。"),
        ("thunder_basic", "九霄雷诀", "thunder", 5, 0.6, "雷属性功法，至刚至阳，威力绝伦。残缺严重，雷劫风险。"),
        ("light_basic", "光明诀", "light", 5, 0.75, "光属性功法，破邪显正，正修至宝。"),
        ("dark_basic", "九幽诀", "dark", 5, 0.68, "暗属性功法，阴煞凌厉，魔修挚爱。修炼损业力。"),
        ("void_basic", "虚空诀", "void", 6, 0.55, "虚空属性功法，可破空间，至高功法。残缺严重。"),
    ]
    for tid, name, elem, tier, completeness, desc in tech_data:
        stages = [
            {"name": "引气入体", "realm_required": "qi_refining_1", "effect": {"qi_capacity": 50, f"{elem}_affinity": 10},
             "defect": {"meridian_strain": 0.03 + 0.01 * (tier - 3)},
             "reversal": {"method": f"配合{elem}系灵物调和", "cost": {"yun_ling_grass" if elem == "wood" else "qing_xin_lotus": 1}, "benefit": "消除负面，修炼速度+10%"}},
            {"name": "凝气成丹", "realm_required": "foundation_1", "effect": {"qi_capacity": 200, f"{elem}_affinity": 25},
             "defect": {"meridian_strain": 0.04 + 0.01 * (tier - 3)},
             "reversal": {"method": "需对应灵物强化", "cost": {"ling_zhi_100": 1}, "benefit": "消除负面，属性+20%"}},
            {"name": "化气为婴", "realm_required": "golden_core_1", "effect": {"qi_capacity": 800, f"{elem}_affinity": 60},
             "defect": {"meridian_strain": 0.05 + 0.01 * (tier - 3)},
             "reversal": {"method": "需高阶灵物养神", "cost": {"yang_soul_wood": 1}, "benefit": "消除负面，额外+30年寿元"}},
            {"name": "元神出窍", "realm_required": "nascent_soul_1", "effect": {"qi_capacity": 3000, f"{elem}_affinity": 150, "spirit_range": 20},
             "defect": {"spirit_strain": 0.04},
             "reversal": {"method": "需仙品灵物", "cost": {"xian_zhi_1000": 1}, "benefit": "消除负面，神识+50%"}},
            {"name": "合道成真", "realm_required": "divine_transformation_1", "effect": {"qi_capacity": 10000, f"{elem}_affinity": 400, "all_affinity": 50},
             "defect": {"karma_strain": 0.05},
             "reversal": {"method": "需悟道", "cost": {"dao_zhong_grass": 1}, "benefit": "消除负面，全方位提升"}},
        ]
        skills = [
            {"name": f"{elem}_strike", "label": f"{'木刺术' if elem=='wood' else '火球术' if elem=='fire' else '冰锥术' if elem=='ice' else '金刃术' if elem=='metal' else '落石术' if elem=='earth' else '风刃' if elem=='wind' else '雷霆' if elem=='thunder' else '光弹' if elem=='light' else '暗影' if elem=='dark' else '虚空斩'}",
             "unlock": "qi_refining_3", "cost": 10, "damage": f"{elem}_affinity * 1.5", "type": "attack"},
            {"name": f"{elem}_burst", "label": f"{'缠绕藤' if elem=='wood' else '焚天掌' if elem=='fire' else '冰封万里' if elem=='ice' else '剑气斩' if elem=='metal' else '地裂术' if elem=='earth' else '龙卷' if elem=='wind' else '九霄雷' if elem=='thunder' else '光明破' if elem=='light' else '九幽噬' if elem=='dark' else '虚空裂'}",
             "unlock": "foundation_5", "cost": 50, "damage": f"{elem}_affinity * 5", "type": "attack", "aoe": True},
            {"name": f"{elem}_shield", "label": f"{'木盾' if elem=='wood' else '火墙' if elem=='fire' else '冰甲' if elem=='ice' else '金刚不坏' if elem=='metal' else '土盾' if elem=='earth' else '风壁' if elem=='wind' else '雷盾' if elem=='thunder' else '光盾' if elem=='light' else '暗影遁' if elem=='dark' else '虚空障'}",
             "unlock": "foundation_7", "cost": 40, "type": "defense", "effect": "减伤50% 3回合"},
            {"name": f"{elem}_ultimate", "label": f"{'万木归元' if elem=='wood' else '业火红莲' if elem=='fire' else '九幽寒冰' if elem=='ice' else '万剑归宗' if elem=='metal' else '山岳压顶' if elem=='earth' else '风暴之眼' if elem=='wind' else '万雷天降' if elem=='thunder' else '审判之光' if elem=='light' else '九幽地狱' if elem=='dark' else '虚空湮灭'}",
             "unlock": "golden_core_5", "cost": 200, "damage": f"{elem}_affinity * 15", "type": "attack", "aoe": True},
            {"name": f"{elem}_domain", "label": f"{'青木领域' if elem=='wood' else '焚天领域' if elem=='fire' else '冰魄领域' if elem=='ice' else '庚金领域' if elem=='metal' else '厚土领域' if elem=='earth' else '御风领域' if elem=='wind' else '九霄领域' if elem=='thunder' else '光明领域' if elem=='light' else '九幽领域' if elem=='dark' else '虚空领域'}",
             "unlock": "nascent_soul_5", "cost": 500, "type": "domain", "effect": "领域展开，全属性+30%"},
        ]
        techniques.append({
            "id": tid, "name": name, "element": elem, "tier": tier,
            "completeness": completeness, "desc": desc,
            "stages": stages, "combat_skills": skills
        })
    return techniques


save("techniques", {"techniques": gen_techniques()})


# ============================================================
# 4. 丹方系统（25种）
# ============================================================
def gen_pill_recipes():
    recipes = [
        {"id": "recipe_qi_pill", "name": "回气丹", "tier": 1,
         "inputs": {"main": {"type": "herb", "min_tier": 1, "count": 1},
                    "auxiliary": {"type": "spirit_stone", "min_tier": 1, "count": 1}},
         "process": {"temperature": {"min": 100, "max": 400, "optimal": 250},
                     "duration": {"min": 60, "max": 180, "optimal": 120},
                     "stirring": {"min": 1, "max": 3, "optimal": 2}},
         "output": {"pill": "qi_pill", "qty": 2}},
        {"id": "recipe_flesh_pill", "name": "续骨丹", "tier": 2,
         "inputs": {"main": {"type": "herb", "min_tier": 2, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 1, "count": 2},
                    "catalyst": {"type": "beast_part", "min_tier": 2, "count": 1}},
         "process": {"temperature": {"min": 200, "max": 500, "optimal": 350},
                     "duration": {"min": 90, "max": 240, "optimal": 150},
                     "stirring": {"min": 2, "max": 4, "optimal": 3}},
         "output": {"pill": "flesh_renew_pill", "qty": 1}},
        {"id": "recipe_fire_resist", "name": "避火丹", "tier": 2,
         "inputs": {"main": {"type": "herb", "element": "ice", "min_tier": 2, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 1, "count": 2},
                    "catalyst": {"type": "spirit_stone", "min_tier": 2, "count": 1}},
         "process": {"temperature": {"min": 150, "max": 450, "optimal": 300},
                     "duration": {"min": 90, "max": 240, "optimal": 150},
                     "stirring": {"min": 2, "max": 4, "optimal": 3}},
         "output": {"pill": "fire_resist_pill", "qty": 1}},
        {"id": "recipe_ice_resist", "name": "避寒丹", "tier": 2,
         "inputs": {"main": {"type": "herb", "element": "fire", "min_tier": 2, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 1, "count": 2},
                    "catalyst": {"type": "spirit_stone", "min_tier": 2, "count": 1}},
         "process": {"temperature": {"min": 200, "max": 600, "optimal": 400},
                     "duration": {"min": 90, "max": 240, "optimal": 150},
                     "stirring": {"min": 2, "max": 4, "optimal": 3}},
         "output": {"pill": "ice_resist_pill", "qty": 1}},
        {"id": "recipe_foundation_pill", "name": "筑基丹", "tier": 3,
         "inputs": {"main": {"type": "herb", "min_tier": 3, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 2, "count": 2},
                    "catalyst": {"type": "beast_core", "min_tier": 3, "count": 1}},
         "process": {"temperature": {"min": 300, "max": 700, "optimal": 500},
                     "duration": {"min": 120, "max": 300, "optimal": 200},
                     "stirring": {"min": 3, "max": 5, "optimal": 4}},
         "output": {"pill": "foundation_pill", "qty": 1}},
        {"id": "recipe_golden_pill", "name": "结金丹", "tier": 4,
         "inputs": {"main": {"type": "herb", "min_tier": 4, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 3, "count": 2},
                    "catalyst": {"type": "beast_core", "min_tier": 4, "count": 1}},
         "process": {"temperature": {"min": 400, "max": 800, "optimal": 600},
                     "duration": {"min": 180, "max": 360, "optimal": 240},
                     "stirring": {"min": 3, "max": 5, "optimal": 4}},
         "output": {"pill": "golden_core_pill", "qty": 1}},
        {"id": "recipe_lifespan_pill", "name": "延寿丹", "tier": 4,
         "inputs": {"main": {"type": "herb", "min_tier": 4, "attrs": "lifespan_ext", "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 3, "count": 2},
                    "catalyst": {"type": "beast_core", "min_tier": 4, "count": 1}},
         "process": {"temperature": {"min": 350, "max": 750, "optimal": 550},
                     "duration": {"min": 180, "max": 360, "optimal": 240},
                     "stirring": {"min": 3, "max": 5, "optimal": 4}},
         "output": {"pill": "lifespan_pill", "qty": 1}},
        {"id": "recipe_qi_gathering_pill", "name": "聚气丹", "tier": 2,
         "inputs": {"main": {"type": "herb", "min_tier": 2, "count": 1},
                    "auxiliary": {"type": "spirit_stone", "min_tier": 1, "count": 2}},
         "process": {"temperature": {"min": 150, "max": 450, "optimal": 300},
                     "duration": {"min": 90, "max": 180, "optimal": 120},
                     "stirring": {"min": 2, "max": 4, "optimal": 3}},
         "output": {"pill": "qi_gathering_pill", "qty": 2}},
        {"id": "recipe_comprehension_pill", "name": "悟道丹", "tier": 4,
         "inputs": {"main": {"type": "herb", "element": "light", "min_tier": 4, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 3, "count": 2},
                    "catalyst": {"type": "beast_core", "min_tier": 4, "count": 1}},
         "process": {"temperature": {"min": 300, "max": 700, "optimal": 500},
                     "duration": {"min": 180, "max": 360, "optimal": 240},
                     "stirring": {"min": 3, "max": 5, "optimal": 4}},
         "output": {"pill": "comprehension_pill", "qty": 1}},
        {"id": "recipe_detox_pill", "name": "解毒丹", "tier": 2,
         "inputs": {"main": {"type": "herb", "element": "wood", "min_tier": 2, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 1, "count": 2}},
         "process": {"temperature": {"min": 150, "max": 450, "optimal": 300},
                     "duration": {"min": 90, "max": 180, "optimal": 120},
                     "stirring": {"min": 2, "max": 4, "optimal": 3}},
         "output": {"pill": "detox_pill", "qty": 2}},
        {"id": "recipe_fire_toxin_pill", "name": "清火丹", "tier": 3,
         "inputs": {"main": {"type": "herb", "element": "ice", "min_tier": 3, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 2, "count": 2}},
         "process": {"temperature": {"min": 200, "max": 500, "optimal": 350},
                     "duration": {"min": 120, "max": 240, "optimal": 180},
                     "stirring": {"min": 2, "max": 4, "optimal": 3}},
         "output": {"pill": "fire_toxin_pill", "qty": 1}},
        {"id": "recipe_meridian_pill", "name": "通脉丹", "tier": 3,
         "inputs": {"main": {"type": "herb", "min_tier": 3, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 2, "count": 2},
                    "catalyst": {"type": "beast_core", "min_tier": 3, "count": 1}},
         "process": {"temperature": {"min": 250, "max": 600, "optimal": 425},
                     "duration": {"min": 120, "max": 300, "optimal": 200},
                     "stirring": {"min": 3, "max": 5, "optimal": 4}},
         "output": {"pill": "meridian_pill", "qty": 1}},
        {"id": "recipe_spirit_pill", "name": "养神丹", "tier": 3,
         "inputs": {"main": {"type": "misc", "id": "yang_soul_wood", "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 2, "count": 2}},
         "process": {"temperature": {"min": 200, "max": 500, "optimal": 350},
                     "duration": {"min": 120, "max": 240, "optimal": 180},
                     "stirring": {"min": 2, "max": 4, "optimal": 3}},
         "output": {"pill": "spirit_pill", "qty": 1}},
        {"id": "recipe_flesh_pill", "name": "锻体丹", "tier": 3,
         "inputs": {"main": {"type": "beast_part", "min_tier": 3, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 2, "count": 2}},
         "process": {"temperature": {"min": 250, "max": 600, "optimal": 425},
                     "duration": {"min": 120, "max": 240, "optimal": 180},
                     "stirring": {"min": 3, "max": 5, "optimal": 4}},
         "output": {"pill": "flesh_pill", "qty": 1}},
        {"id": "recipe_swift_pill", "name": "神行丹", "tier": 2,
         "inputs": {"main": {"type": "herb", "element": "wind", "min_tier": 2, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 1, "count": 2}},
         "process": {"temperature": {"min": 150, "max": 450, "optimal": 300},
                     "duration": {"min": 90, "max": 180, "optimal": 120},
                     "stirring": {"min": 2, "max": 4, "optimal": 3}},
         "output": {"pill": "swift_pill", "qty": 2}},
        {"id": "recipe_dantian_pill", "name": "补天丹", "tier": 5,
         "inputs": {"main": {"type": "herb", "min_tier": 5, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 4, "count": 2},
                    "catalyst": {"type": "beast_core", "min_tier": 5, "count": 1}},
         "process": {"temperature": {"min": 400, "max": 800, "optimal": 600},
                     "duration": {"min": 240, "max": 480, "optimal": 360},
                     "stirring": {"min": 4, "max": 6, "optimal": 5}},
         "output": {"pill": "dantian_pill", "qty": 1}},
        {"id": "recipe_tribulation_pill", "name": "渡劫丹", "tier": 6,
         "inputs": {"main": {"type": "herb", "min_tier": 6, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 5, "count": 3},
                    "catalyst": {"type": "beast_core", "min_tier": 6, "count": 1}},
         "process": {"temperature": {"min": 500, "max": 900, "optimal": 700},
                     "duration": {"min": 300, "max": 600, "optimal": 450},
                     "stirring": {"min": 4, "max": 6, "optimal": 5}},
         "output": {"pill": "tribulation_pill", "qty": 1}},
        {"id": "recipe_nine_turn_pill", "name": "九转金丹", "tier": 7,
         "inputs": {"main": {"type": "herb", "min_tier": 7, "count": 2},
                    "auxiliary": {"type": "herb", "min_tier": 6, "count": 3},
                    "catalyst": {"type": "beast_core", "min_tier": 7, "count": 1}},
         "process": {"temperature": {"min": 600, "max": 1000, "optimal": 800},
                     "duration": {"min": 480, "max": 960, "optimal": 720},
                     "stirring": {"min": 5, "max": 7, "optimal": 6}},
         "output": {"pill": "nine_turn_pill", "qty": 1}},
        {"id": "recipe_heart_devil_pill", "name": "破心魔丹", "tier": 5,
         "inputs": {"main": {"type": "herb", "element": "light", "min_tier": 5, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 4, "count": 2}},
         "process": {"temperature": {"min": 350, "max": 700, "optimal": 525},
                     "duration": {"min": 240, "max": 480, "optimal": 360},
                     "stirring": {"min": 3, "max": 5, "optimal": 4}},
         "output": {"pill": "heart_devil_pill", "qty": 1}},
        {"id": "recipe_karma_pill", "name": "消业丹", "tier": 5,
         "inputs": {"main": {"type": "herb", "min_tier": 5, "count": 1},
                    "auxiliary": {"type": "herb", "min_tier": 4, "count": 2},
                    "catalyst": {"type": "spirit_stone", "min_tier": 3, "count": 3}},
         "process": {"temperature": {"min": 300, "max": 700, "optimal": 500},
                     "duration": {"min": 240, "max": 480, "optimal": 360},
                     "stirring": {"min": 3, "max": 5, "optimal": 4}},
         "output": {"pill": "karma_pill", "qty": 1}},
    ]
    return recipes


save("pills", {"pill_recipes": gen_pill_recipes()})


# ============================================================
# 5. 妖兽数据（25种）
# ============================================================
def gen_beasts():
    beasts = [
        # id, 名, 阶, 元素, HP, 攻, 防, 速, QI, 技能, 掉落, 经验, 灵石, 驯服
        ("ye_tu", "灵兔", 1, "wood", 50, 8, 3, 15, 20,
         [{"name": "撕咬", "damage_mult": 1.0, "cost": 0}, {"name": "急速突袭", "damage_mult": 1.3, "cost": 10}],
         [("leather", 0.7), ("yun_ling_grass", 0.3)], 15, [1, 3], True, "凡人国度"),
        ("shan_lang", "山狼", 2, "wind", 120, 18, 8, 25, 50,
         [{"name": "撕咬", "damage_mult": 1.0, "cost": 0}, {"name": "风刃", "damage_mult": 1.4, "cost": 20, "element": "wind"},
          {"name": "狼群嚎叫", "damage_mult": 1.2, "cost": 30, "cooldown": 3}],
         [("leather", 0.9), ("wolf_core", 0.5)], 35, [2, 5], True, "万妖山脉外围"),
        ("du_she", "碧磷蛇", 2, "wood", 100, 20, 6, 20, 60,
         [{"name": "撕咬", "damage_mult": 1.0, "cost": 0, "poison": True},
          {"name": "毒液喷射", "damage_mult": 1.3, "cost": 25, "element": "wood", "poison": True},
          {"name": "缠绕", "damage_mult": 0.8, "cost": 15, "stun": True, "cooldown": 2}],
         [("leather", 0.8), ("snake_gallbladder", 0.6), ("qing_xin_lotus", 0.2)], 40, [2, 5], False, "万妖山脉"),
        ("chiyan_tiger", "赤焰虎", 3, "fire", 300, 35, 20, 30, 200,
         [{"name": "撕咬", "damage_mult": 1.0, "cost": 0},
          {"name": "火焰喷射", "damage_mult": 1.5, "cost": 30, "element": "fire", "burn": True},
          {"name": "虎王之怒", "damage_mult": 2.0, "cost": 60, "element": "fire", "cooldown": 3}],
         [("tiger_fur", 0.9), ("tiger_claw", 0.6), ("tiger_core", 0.7), ("chi_yan_grass", 0.3)], 80, [3, 8], True, "万妖山脉炎峰"),
        ("ice_wolf", "冰狼", 3, "ice", 280, 38, 18, 40, 180,
         [{"name": "撕咬", "damage_mult": 1.0, "cost": 0},
          {"name": "冰锥术", "damage_mult": 1.4, "cost": 25, "element": "ice", "slow": True},
          {"name": "冰封狼嚎", "damage_mult": 1.8, "cost": 50, "element": "ice", "freeze": True, "cooldown": 3}],
         [("wolf_fur", 0.9), ("wolf_core", 0.7), ("bing_lotus", 0.3)], 80, [3, 8], True, "万妖山脉寒冰潭"),
        ("qingmu_snake", "青木蟒", 4, "wood", 500, 45, 30, 25, 300,
         [{"name": "缠绕", "damage_mult": 1.0, "cost": 0, "stun": True},
          {"name": "毒液喷射", "damage_mult": 1.3, "cost": 30, "element": "wood", "poison": True},
          {"name": "蟒尾横扫", "damage_mult": 1.7, "cost": 50, "aoe": True, "cooldown": 2}],
         [("leather", 0.9), ("snake_core", 0.8), ("long_xu_grass", 0.4)], 150, [8, 18], False, "万妖山脉深处"),
        ("jinjia_scorpion", "金甲蝎", 4, "metal", 600, 40, 50, 20, 250,
         [{"name": "钳击", "damage_mult": 1.0, "cost": 0},
          {"name": "尾刺", "damage_mult": 1.4, "cost": 25, "poison": True},
          {"name": "金甲护体", "damage_mult": 0, "cost": 40, "defense_boost": 30, "cooldown": 3}],
         [("leather", 0.9), ("scorpion_core", 0.8), ("xuan_iron", 0.5)], 150, [8, 18], False, "万妖山脉矿洞"),
        ("fengxing_leopard", "风行豹", 4, "wind", 380, 55, 22, 70, 220,
         [{"name": "利爪", "damage_mult": 1.0, "cost": 0},
          {"name": "风刃", "damage_mult": 1.5, "cost": 30, "element": "wind"},
          {"name": "疾风突袭", "damage_mult": 2.2, "cost": 60, "element": "wind", "double_attack": True, "cooldown": 3}],
         [("leather", 0.9), ("leopard_core", 0.8), ("ling_crystal", 0.4)], 150, [8, 18], False, "万妖山脉平原"),
        ("leiying", "雷鹰", 4, "thunder", 320, 60, 18, 65, 240,
         [{"name": "利爪", "damage_mult": 1.0, "cost": 0},
          {"name": "雷电", "damage_mult": 1.6, "cost": 35, "element": "thunder", "stun": True},
          {"name": "雷暴", "damage_mult": 2.0, "cost": 70, "element": "thunder", "aoe": True, "cooldown": 3}],
         [("eagle_claw", 0.8), ("lei_jing", 0.5)], 160, [8, 20], True, "万妖山脉高峰"),
        ("xiong_feng", "凶蜂", 2, "wind", 80, 15, 5, 35, 30,
         [{"name": "蛰刺", "damage_mult": 1.0, "cost": 0, "poison": True},
          {"name": "蜂群", "damage_mult": 1.3, "cost": 15, "aoe": True}],
         [("leather", 0.3), ("feng_yin_grass", 0.2)], 25, [1, 3], False, "万妖山脉林间"),
        ("shi_jing_yi_wang", "食晶蚁王", 5, "earth", 1000, 70, 60, 30, 500,
         [{"name": "钳咬", "damage_mult": 1.0, "cost": 0},
          {"name": "土崩击", "damage_mult": 1.6, "cost": 40, "element": "earth"},
          {"name": "蚁群召唤", "damage_mult": 1.2, "cost": 80, "summon": True, "cooldown": 4},
          {"name": "晶化护甲", "damage_mult": 0, "cost": 60, "defense_boost": 80, "cooldown": 3}],
         [("ling_crystal", 1.0, [2, 4]), ("star_iron", 0.5), ("spirit_stone_mid", 0.8, [1, 3])], 300, [20, 50], False, "万妖山脉矿洞深处"),
        ("huo_long", "火龙", 6, "fire", 3000, 200, 100, 80, 2000,
         [{"name": "龙爪", "damage_mult": 1.5, "cost": 0},
          {"name": "龙息", "damage_mult": 2.0, "cost": 200, "element": "fire", "aoe": True, "burn": True},
          {"name": "龙威", "damage_mult": 0, "cost": 300, "stun": True, "aoe": True, "cooldown": 5},
          {"name": "龙吟", "damage_mult": 1.8, "cost": 400, "aoe": True, "cooldown": 3}],
         [("dragon_scale", 1.0, [3, 6]), ("spirit_stone_high", 0.8, [2, 5])], 800, [100, 200], False, "火龙洞"),
        ("bing_long", "冰龙", 6, "ice", 3200, 190, 110, 70, 2000,
         [{"name": "龙爪", "damage_mult": 1.5, "cost": 0},
          {"name": "冰息", "damage_mult": 2.0, "cost": 200, "element": "ice", "aoe": True, "freeze": True},
          {"name": "龙威", "damage_mult": 0, "cost": 300, "stun": True, "aoe": True, "cooldown": 5}],
         [("dragon_scale", 1.0, [3, 6]), ("bing_jing", 0.8, [5, 10])], 800, [100, 200], False, "冰龙窟"),
        ("jiu_you_she", "九幽蛇", 6, "dark", 2500, 220, 90, 90, 1800,
         [{"name": "撕咬", "damage_mult": 1.5, "cost": 0, "poison": True},
          {"name": "九幽毒雾", "damage_mult": 1.8, "cost": 250, "element": "dark", "aoe": True, "poison": True},
          {"name": "灵魂吞噬", "damage_mult": 2.2, "cost": 350, "soul_damage": True, "cooldown": 3}],
         [("snake_core", 1.0), ("jiuyou_grass", 0.5), ("spirit_stone_high", 0.5, [1, 3])], 700, [80, 180], False, "九幽冥土"),
        ("jin_chi_peng", "金翅鹏", 5, "wind", 1500, 120, 70, 120, 800,
         [{"name": "鹏击", "damage_mult": 1.5, "cost": 0},
          {"name": "金翅斩", "damage_mult": 2.0, "cost": 150, "element": "metal"},
          {"name": "风暴", "damage_mult": 1.8, "cost": 200, "element": "wind", "aoe": True, "cooldown": 3}],
         [("eagle_claw", 1.0, [2, 4]), ("purple_gold", 0.6), ("spirit_stone_high", 0.3, [1, 2])], 400, [30, 80], False, "高空云海"),
        ("xuan_wu", "玄武", 7, "water", 8000, 350, 400, 50, 5000,
         [{"name": "玄武撞击", "damage_mult": 1.5, "cost": 0},
          {"name": "水流斩", "damage_mult": 2.0, "cost": 500, "element": "water", "aoe": True},
          {"name": "玄武甲", "damage_mult": 0, "cost": 800, "defense_boost": 200, "cooldown": 5},
          {"name": "水神领域", "damage_mult": 2.5, "cost": 1500, "element": "water", "domain": True, "cooldown": 10}],
         [("black_turtle_shell", 1.0, [2, 4]), ("spirit_stone_top", 0.3, [1, 2])], 2000, [500, 1000], False, "北海深渊"),
        ("qing_long", "青龙", 7, "wood", 7500, 380, 320, 100, 5000,
         [{"name": "龙爪", "damage_mult": 1.5, "cost": 0},
          {"name": "青木领域", "damage_mult": 2.0, "cost": 800, "element": "wood", "domain": True},
          {"name": "神龙摆尾", "damage_mult": 2.2, "cost": 1000, "aoe": True, "cooldown": 3}],
         [("azure_dragon_whisker", 1.0, [2, 4]), ("dragon_scale", 1.0, [3, 6]), ("spirit_stone_top", 0.3, [1, 2])], 2000, [500, 1000], False, "东海龙宫"),
        ("zhu_que", "朱雀", 7, "fire", 7000, 420, 280, 120, 5000,
         [{"name": "朱雀啄", "damage_mult": 1.5, "cost": 0},
          {"name": "涅槃火焰", "damage_mult": 2.5, "cost": 1000, "element": "fire", "aoe": True, "burn": True, "cooldown": 3},
          {"name": "凤凰涅槃", "damage_mult": 0, "cost": 2000, "heal_self": True, "cooldown": 10}],
         [("vermillion_bird_feather", 1.0, [2, 4]), ("feng_xi_grass", 0.5), ("spirit_stone_top", 0.3, [1, 2])], 2000, [500, 1000], False, "南方火山"),
        ("bai_hu", "白虎", 7, "metal", 7800, 450, 300, 110, 5000,
         [{"name": "虎啸", "damage_mult": 1.5, "cost": 0},
          {"name": "庚金剑气", "damage_mult": 2.5, "cost": 1000, "element": "metal", "armor_pierce": True},
          {"name": "白虎领域", "damage_mult": 2.0, "cost": 1500, "element": "metal", "domain": True, "cooldown": 8}],
         [("white_tiger_fang", 1.0, [2, 4]), ("star_iron", 0.8, [2, 5]), ("spirit_stone_top", 0.3, [1, 2])], 2000, [500, 1000], False, "西方白虎岭"),
        ("qi_lin", "麒麟", 7, "light", 8500, 400, 350, 90, 5500,
         [{"name": "麒麟踏", "damage_mult": 1.5, "cost": 0},
          {"name": "圣光", "damage_mult": 2.0, "cost": 800, "element": "light", "aoe": True},
          {"name": "麒麟瑞气", "damage_mult": 0, "cost": 1500, "heal_self": True, "karma_boost": True, "cooldown": 8}],
         [("qilin_horn", 1.0, [1, 2]), ("spirit_stone_top", 0.5, [1, 3])], 2500, [600, 1200], False, "麒麟圣地"),
        ("jiu_you_mo_long", "九幽魔龙", 7, "dark", 9000, 480, 320, 100, 6000,
         [{"name": "魔龙爪", "damage_mult": 1.5, "cost": 0},
          {"name": "九幽领域", "damage_mult": 2.5, "cost": 1200, "element": "dark", "domain": True, "soul_damage": True, "cooldown": 8},
          {"name": "魔龙吞噬", "damage_mult": 2.0, "cost": 1000, "absorb": True}],
         [("mo_long_grass", 0.8), ("mo_tie", 1.0, [3, 6]), ("spirit_stone_top", 0.4, [2, 4])], 3000, [800, 1500], False, "九幽魔渊"),
        ("tian_jie_shou", "天劫兽", 6, "thunder", 5000, 250, 180, 90, 3000,
         [{"name": "雷击", "damage_mult": 1.5, "cost": 0, "element": "thunder"},
          {"name": "天劫降临", "damage_mult": 2.5, "cost": 800, "element": "thunder", "aoe": True, "cooldown": 5}],
         [("lei_jing", 1.0, [3, 6]), ("spirit_stone_high", 0.8, [3, 8])], 1500, [200, 400], False, "天劫之地"),
        ("xian_jian_jing", "剑灵精", 5, "metal", 2000, 150, 100, 80, 1000,
         [{"name": "剑气斩", "damage_mult": 1.5, "cost": 0},
          {"name": "万剑归宗", "damage_mult": 2.5, "cost": 300, "element": "metal", "aoe": True, "cooldown": 3}],
         [("spirit_sword", 0.3), ("purple_gold", 0.5), ("spirit_stone_mid", 1.0, [3, 8])], 600, [50, 120], False, "古剑冢"),
        ("mo_ying", "魔影", 5, "dark", 1800, 140, 80, 100, 800,
         [{"name": "暗影爪", "damage_mult": 1.3, "cost": 0},
          {"name": "暗影吞噬", "damage_mult": 1.8, "cost": 200, "element": "dark"},
          {"name": "影分身", "damage_mult": 0, "cost": 250, "summon": True, "cooldown": 5}],
         [("mo_zhi_grass", 0.3), ("spirit_stone_mid", 0.8, [2, 5])], 500, [40, 100], False, "魔气浓郁之地"),
    ]
    result = []
    for b in beasts:
        bid, name, tier, elem, hp, atk, defe, spd, qi, skills, drops, exp, ss, tamable, habitat = b
        formatted_drops = []
        for d in drops:
            if len(d) == 2:
                formatted_drops.append({"item": d[0], "prob": d[1]})
            else:
                formatted_drops.append({"item": d[0], "prob": d[1], "qty": d[2]})
        result.append({
            "id": bid, "name": name, "tier": tier, "element": elem,
            "hp": hp, "attack": atk, "defense": defe, "speed": spd, "qi": qi,
            "skills": skills, "drops": formatted_drops,
            "exp": exp, "spirit_stones": ss, "tamable": tamable,
            "habitat": habitat,
            "desc": f"{name}，{tier}阶{elem}属性妖兽，栖息于{habitat}。"
        })
    return result


save("beasts", {"beasts": gen_beasts()})


print("\n数据生成完成！")
print(f"总材料数: {len(all_materials)}")
