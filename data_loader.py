"""
《逆仙录·天道残卷》数据加载器
统一加载所有JSON配置，提供查询接口
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
_cache = {}


def _load(name):
    if name not in _cache:
        path = os.path.join(DATA_DIR, f"{name}.json")
        with open(path, "r", encoding="utf-8") as f:
            _cache[name] = json.load(f)
    return _cache[name]


def get_realms():
    return _load("realms")["realms"]


def get_realm(rid):
    for r in get_realms():
        if r["id"] == rid:
            return r
    return None


def get_realm_index(rid):
    for i, r in enumerate(get_realms()):
        if r["id"] == rid:
            return i
    return 0


def get_next_realm(rid):
    idx = get_realm_index(rid)
    realms = get_realms()
    if idx + 1 < len(realms):
        return realms[idx + 1]
    return None


def get_realm_name(rid):
    r = get_realm(rid)
    return r["name"] if r else "未知"


def get_realm_lifespan(rid):
    r = get_realm(rid)
    return r["lifespan"] if r else 120


def get_materials():
    return _load("materials")["materials"]


def get_material(mid):
    for m in get_materials():
        if m["id"] == mid:
            return m
    return None


def get_techniques():
    return _load("techniques")["techniques"]


def get_technique(tid):
    for t in get_techniques():
        if t["id"] == tid:
            return t
    return None


def get_pill_recipes():
    return _load("pills")["pill_recipes"]


def get_pill_recipe(rid):
    for r in get_pill_recipes():
        if r["id"] == rid:
            return r
    return None


def get_beasts():
    return _load("beasts")["beasts"]


def get_beast(bid):
    for b in get_beasts():
        if b["id"] == bid:
            return b
    return None


def get_regions():
    return _load("regions")["regions"]


def get_region(rid):
    for r in get_regions():
        if r["id"] == rid:
            return r
    return None


def get_npcs_config():
    return _load("npcs")["npcs"]


def get_npc_config(nid):
    for n in get_npcs_config():
        if n["id"] == nid:
            return n
    return None


def get_sects():
    return _load("sects")["sects"]


def get_sect(sid):
    for s in get_sects():
        if s["id"] == sid:
            return s
    return None


def get_storylines():
    return _load("storylines")["storylines"]


def get_causal_chains():
    return _load("causal_chains")["causal_chains"]


def get_forge_recipes():
    return _load("forge_recipes")["forge_recipes"]


def get_forge_recipe(fid):
    for r in get_forge_recipes():
        if r["id"] == fid:
            return r
    return None


def get_formations():
    return _load("formations")["formations"]


def get_formation(fid):
    for f in get_formations():
        if f["id"] == fid:
            return f
    return None


def get_auction_items():
    return _load("auction_items")["auction_items"]


def get_pvp_opponents():
    return _load("pvp_opponents")["pvp_opponents"]


def get_pvp_opponent(pid):
    for p in get_pvp_opponents():
        if p["id"] == pid:
            return p
    return None


def get_tribulations():
    return _load("tribulations")["tribulations"]


def get_tribulation(realm):
    for t in get_tribulations():
        if t["realm"] == realm:
            return t
    return None


# 经脉定义（12正经 + 8奇经）
MERIDIANS = [
    "任脉", "督脉", "冲脉", "带脉",
    "手太阴肺经", "手阳明大肠经", "足阳明胃经", "足太阴脾经",
    "手少阴心经", "手太阳小肠经", "足太阳膀胱经", "足少阴肾经",
    "手厥阴心包经", "手少阳三焦经", "足少阳胆经", "足厥阴肝经",
    "阳维脉", "阴维脉", "阳跷脉", "阴跷脉"
]

# 五脏对应五行
ORGANS = {
    "heart": {"element": "fire", "name": "心"},
    "liver": {"element": "wood", "name": "肝"},
    "spleen": {"element": "earth", "name": "脾"},
    "lung": {"element": "metal", "name": "肺"},
    "kidney": {"element": "water", "name": "肾"}
}

# 属性中文名
ATTR_NAMES = {
    "wood_affinity": "木属性亲和", "fire_affinity": "火属性亲和",
    "ice_affinity": "冰属性亲和", "metal_affinity": "金属性亲和",
    "earth_affinity": "土属性亲和", "wind_affinity": "风属性亲和",
    "thunder_affinity": "雷属性亲和", "light_affinity": "光属性亲和",
    "dark_affinity": "暗属性亲和", "void_affinity": "虚空属性亲和",
    "water_affinity": "水属性亲和", "soul_affinity": "神魂属性亲和",
    "spiritual_energy": "灵气", "meridian_strain": "经脉损伤",
    "fire_poison": "火毒", "cold_damage": "寒气"
}

# 元素克制关系
ELEMENT_COUNTERS = {
    "fire": "ice", "ice": "fire",
    "wood": "earth", "earth": "water", "water": "fire",
    "metal": "wood", "wind": "earth",
    "thunder": "water", "light": "dark", "dark": "light"
}

# 寿元阶段
LIFESPAN_STAGES = {
    "youth": {"range": (0, 30), "cultivate_bonus": 0.2, "recovery_bonus": 0.5, "name": "青年"},
    "prime": {"range": (30, 80), "cultivate_bonus": 0, "recovery_bonus": 0, "name": "壮年"},
    "decline": {"range": (80, 110), "cultivate_bonus": -0.3, "recovery_bonus": -0.3, "name": "衰朽"},
    "desperate": {"range": (110, 999), "cultivate_bonus": -0.5, "recovery_bonus": -0.5, "name": "暮年", "qi_deviation_risk": 2.0}
}
