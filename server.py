"""
《逆仙录·天道残卷》Flask服务器
集成用户系统、API接口、静态资源服务
"""
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import os
import threading
from user_system import register, login, get_user, list_users, delete_user, list_player_saves, delete_player_save
from engine import GameEngine

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = "shattered_dao_secret_2026"
CORS(app, supports_credentials=True)

# 引擎实例缓存（按用户ID）
_engines = {}
_engines_lock = threading.Lock()


def get_engine():
    """获取当前用户的引擎实例"""
    user_id = session.get("user_id")
    if not user_id:
        return None
    with _engines_lock:
        if user_id not in _engines:
            _engines[user_id] = GameEngine(user_id=user_id, username=session.get("username", ""))
        return _engines[user_id]


def require_auth(func):
    """登录验证装饰器"""
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"ok": False, "msg": "请先登录"})
        return func(*args, **kwargs)
    return wrapper


def require_admin(func):
    """管理员验证装饰器"""
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"ok": False, "msg": "请先登录"})
        if not session.get("is_admin"):
            return jsonify({"ok": False, "msg": "需要管理员权限"})
        return func(*args, **kwargs)
    return wrapper


# ==================== 静态资源 ====================
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def static_files(path):
    if os.path.exists(os.path.join("static", path)):
        return send_from_directory("static", path)
    return send_from_directory("static", "index.html")


# ==================== 用户系统 ====================
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    r = register(data.get("username", ""), data.get("password", ""))
    if r["ok"]:
        session["user_id"] = r["user_id"]
        session["username"] = r["username"]
        session["is_admin"] = r["is_admin"]
    return jsonify(r)


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    r = login(data.get("username", ""), data.get("password", ""))
    if r["ok"]:
        session["user_id"] = r["user_id"]
        session["username"] = r["username"]
        session["is_admin"] = r["is_admin"]
    return jsonify(r)


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True, "msg": "已登出"})


@app.route("/api/me", methods=["GET"])
def api_me():
    if not session.get("user_id"):
        return jsonify({"ok": False, "msg": "未登录"})
    user = get_user(session["user_id"])
    if not user:
        session.clear()
        return jsonify({"ok": False, "msg": "用户不存在"})
    return jsonify({"ok": True, "user": user, "is_admin": session.get("is_admin", 0)})


@app.route("/api/users", methods=["GET"])
@require_admin
def api_users():
    return jsonify({"ok": True, "users": list_users()})


@app.route("/api/users/<int:uid>", methods=["DELETE"])
@require_admin
def api_delete_user(uid):
    if uid == session.get("user_id"):
        return jsonify({"ok": False, "msg": "不能删除自己"})
    return jsonify(delete_user(uid))


@app.route("/api/saves", methods=["GET"])
@require_auth
def api_saves():
    saves = list_player_saves(session["user_id"])
    return jsonify({"ok": True, "saves": saves})


@app.route("/api/saves/<save_name>", methods=["DELETE"])
@require_auth
def api_delete_save(save_name):
    delete_player_save(session["user_id"], save_name)
    return jsonify({"ok": True, "msg": "存档已删除"})


# ==================== 游戏API ====================
@app.route("/api/state", methods=["GET"])
@require_auth
def get_state():
    eng = get_engine()
    if not eng:
        return jsonify({"ok": False, "msg": "引擎未初始化"})
    return jsonify(eng.get_full_state())


@app.route("/api/move", methods=["POST"])
@require_auth
def move():
    data = request.json
    return jsonify(get_engine().move_player(data.get("direction")))


@app.route("/api/move_to", methods=["POST"])
@require_auth
def move_to():
    data = request.json
    return jsonify(get_engine().move_player_to(data.get("x"), data.get("y")))


@app.route("/api/gather", methods=["POST"])
@require_auth
def gather():
    return jsonify(get_engine().gather(request.json.get("resource_id")))


@app.route("/api/cut_tree", methods=["POST"])
@require_auth
def cut_tree():
    return jsonify(get_engine().cut_tree())


@app.route("/api/cultivate", methods=["POST"])
@require_auth
def cultivate():
    data = request.json
    return jsonify(get_engine().cultivate(
        data.get("hours", 1),
        data.get("location", "sect"),
        data.get("cycles", 3),
        data.get("use_pill"),
        data.get("use_formation")
    ))


@app.route("/api/breakthrough", methods=["POST"])
@require_auth
def breakthrough():
    data = request.json
    return jsonify(get_engine().try_breakthrough(data.get("method", "water_grind")))


@app.route("/api/rest", methods=["POST"])
@require_auth
def rest():
    return jsonify(get_engine().rest(request.json.get("hours", 1)))


@app.route("/api/seclusion", methods=["POST"])
@require_auth
def seclusion():
    return jsonify(get_engine().seclusion(request.json.get("days", 1)))


@app.route("/api/learn_technique", methods=["POST"])
@require_auth
def learn_technique():
    return jsonify(get_engine().learn_technique(request.json.get("tech_id")))


@app.route("/api/activate_technique", methods=["POST"])
@require_auth
def activate_technique():
    return jsonify(get_engine().activate_technique(request.json.get("tech_id")))


@app.route("/api/reverse_technique", methods=["POST"])
@require_auth
def reverse_technique():
    data = request.json
    return jsonify(get_engine().reverse_technique(data.get("tech_id"), data.get("stage_idx")))


@app.route("/api/combat_action", methods=["POST"])
@require_auth
def combat_action():
    data = request.json
    return jsonify(get_engine().combat_action(
        data.get("action"),
        data.get("skill_idx", 0),
        data.get("target_part", "body"),
        data.get("qi_allocation", 0.5)
    ))


@app.route("/api/use_item_combat", methods=["POST"])
@require_auth
def use_item_combat():
    return jsonify(get_engine().use_item_in_combat(request.json.get("item_id")))


@app.route("/api/use_item", methods=["POST"])
@require_auth
def use_item():
    return jsonify(get_engine().use_item(request.json.get("item_id")))


@app.route("/api/equip_item", methods=["POST"])
@require_auth
def equip_item():
    return jsonify(get_engine().equip_item(request.json.get("item_id")))


@app.route("/api/unequip_item", methods=["POST"])
@require_auth
def unequip_item():
    return jsonify(get_engine().unequip_item(request.json.get("slot")))


@app.route("/api/alchemy_recipes", methods=["GET"])
@require_auth
def alchemy_recipes():
    return jsonify(get_engine().get_alchemy_recipes())


@app.route("/api/alchemy_craft", methods=["POST"])
@require_auth
def alchemy_craft():
    data = request.json
    return jsonify(get_engine().alchemy_craft(data.get("recipe_id"), data.get("materials", {}), data.get("process", {})))


@app.route("/api/shop_list", methods=["GET"])
@require_auth
def shop_list():
    return jsonify(get_engine().shop_list(request.args.get("type")))


@app.route("/api/shop_buy", methods=["POST"])
@require_auth
def shop_buy():
    data = request.json
    return jsonify(get_engine().shop_buy(data.get("item_id"), data.get("qty", 1)))


@app.route("/api/shop_sell", methods=["POST"])
@require_auth
def shop_sell():
    data = request.json
    return jsonify(get_engine().shop_sell(data.get("item_id"), data.get("qty", 1)))


@app.route("/api/talk_npc", methods=["POST"])
@require_auth
def talk_npc():
    return jsonify(get_engine().talk_to_npc(request.json.get("npc_id")))


@app.route("/api/gift_npc", methods=["POST"])
@require_auth
def gift_npc():
    data = request.json
    return jsonify(get_engine().gift_to_npc(data.get("npc_id"), data.get("item_id"), data.get("qty", 1)))


@app.route("/api/plant_seed", methods=["POST"])
@require_auth
def plant_seed():
    data = request.json
    return jsonify(get_engine().plant_seed(data.get("seed_id"), data.get("plot_idx", 0)))


@app.route("/api/harvest", methods=["POST"])
@require_auth
def harvest():
    return jsonify(get_engine().harvest_crop(request.json.get("plot_idx", 0)))


@app.route("/api/tame_beast", methods=["POST"])
@require_auth
def tame_beast():
    return jsonify(get_engine().tame_beast(request.json.get("beast_id")))


@app.route("/api/reset", methods=["POST"])
@require_auth
def reset():
    return jsonify(get_engine().reset_game())


# ==================== 扩展系统API ====================
# 炼器
@app.route("/api/forge_recipes", methods=["GET"])
@require_auth
def forge_recipes():
    return jsonify(get_engine().get_forge_recipes())


@app.route("/api/forge_craft", methods=["POST"])
@require_auth
def forge_craft():
    data = request.json
    return jsonify(get_engine().forge_craft(data.get("recipe_id"), data.get("materials", {}), data.get("process", {})))


# 阵法
@app.route("/api/formations", methods=["GET"])
@require_auth
def formations():
    return jsonify(get_engine().get_formations_list())


@app.route("/api/set_formation", methods=["POST"])
@require_auth
def set_formation():
    return jsonify(get_engine().set_formation(request.json.get("formation_id")))


@app.route("/api/break_formation", methods=["POST"])
@require_auth
def break_formation():
    return jsonify(get_engine().break_formation(request.json.get("formation_id")))


# 道侣
@app.route("/api/propose_companion", methods=["POST"])
@require_auth
def propose_companion():
    return jsonify(get_engine().propose_dao_companion(request.json.get("npc_id")))


@app.route("/api/dual_cultivate", methods=["POST"])
@require_auth
def dual_cultivate():
    return jsonify(get_engine().dual_cultivate(request.json.get("hours", 1)))


@app.route("/api/betray_companion", methods=["POST"])
@require_auth
def betray_companion():
    return jsonify(get_engine().betray_companion())


# 转世
@app.route("/api/choose_reincarnation", methods=["POST"])
@require_auth
def choose_reincarnation():
    return jsonify(get_engine().choose_reincarnation(request.json.get("choice")))


# 天劫
@app.route("/api/trigger_tribulation", methods=["POST"])
@require_auth
def trigger_tribulation():
    return jsonify(get_engine().trigger_tribulation())


@app.route("/api/tribulation_round", methods=["POST"])
@require_auth
def tribulation_round():
    data = request.json
    return jsonify(get_engine().tribulation_round(data.get("action", "endure"), data.get("use_item")))


# 剧情
@app.route("/api/story_progress", methods=["GET"])
@require_auth
def story_progress():
    return jsonify({"ok": True, "progress": get_engine().get_story_progress(), "storylines": get_storylines_data()})


# 拍卖
@app.route("/api/auction_list", methods=["GET"])
@require_auth
def auction_list():
    return jsonify(get_engine().get_auction_list())


@app.route("/api/auction_bid", methods=["POST"])
@require_auth
def auction_bid():
    data = request.json
    return jsonify(get_engine().auction_bid(data.get("auc_id"), data.get("bid_price")))


# PVP
@app.route("/api/pvp_list", methods=["GET"])
@require_auth
def pvp_list():
    return jsonify(get_engine().get_pvp_list())


@app.route("/api/start_pvp", methods=["POST"])
@require_auth
def start_pvp():
    return jsonify(get_engine().start_pvp(request.json.get("opp_id")))


# 宗门战
@app.route("/api/start_sect_war", methods=["POST"])
@require_auth
def start_sect_war():
    return jsonify(get_engine().start_sect_war())


@app.route("/api/join_sect_war", methods=["POST"])
@require_auth
def join_sect_war():
    return jsonify(get_engine().join_sect_war())


# ==================== 角色创建/开局 ====================
@app.route("/api/character_status", methods=["GET"])
@require_auth
def character_status():
    eng = get_engine()
    return jsonify({"ok": True, "created": eng.is_character_created()})


@app.route("/api/create_character", methods=["POST"])
@require_auth
def create_character():
    data = request.json
    return jsonify(get_engine().create_character(data.get("name",""), data.get("spiritual_root","pseudo"), data.get("start_technique","wood_basic")))


# 采药小游戏
@app.route("/api/gather_herb_start", methods=["POST"])
@require_auth
def gather_herb_start():
    return jsonify(get_engine().gather_herb_minigame(request.json.get("resource_id")))


@app.route("/api/gather_herb_complete", methods=["POST"])
@require_auth
def gather_herb_complete():
    data = request.json
    return jsonify(get_engine().gather_herb_complete(data.get("resource_id"), data.get("timing_score", 50)))


# 突破小游戏
@app.route("/api/breakthrough_minigame_start", methods=["POST"])
@require_auth
def breakthrough_minigame_start():
    return jsonify(get_engine().breakthrough_minigame_start(request.json.get("method","water_grind")))


@app.route("/api/breakthrough_minigame_complete", methods=["POST"])
@require_auth
def breakthrough_minigame_complete():
    data = request.json
    return jsonify(get_engine().breakthrough_minigame_complete(data.get("method","water_grind"), data.get("scores",[])))


# 拍卖刷新
@app.route("/api/refresh_auction", methods=["POST"])
@require_auth
def refresh_auction():
    return jsonify(get_engine().refresh_auction())


# ==================== 管理员后台 ====================
@app.route("/api/admin/stats", methods=["GET"])
@require_admin
def admin_stats():
    """管理后台统计"""
    from data_loader import (get_materials, get_techniques, get_pill_recipes,
                             get_beasts, get_regions, get_npcs_config, get_sects, get_storylines)
    return jsonify({
        "ok": True,
        "stats": {
            "users": len(list_users()),
            "materials": len(get_materials()),
            "techniques": len(get_techniques()),
            "pill_recipes": len(get_pill_recipes()),
            "beasts": len(get_beasts()),
            "regions": len(get_regions()),
            "npcs": len(get_npcs_config()),
            "sects": len(get_sects()),
            "storylines": len(get_storylines())
        }
    })


@app.route("/api/admin/users", methods=["GET"])
@require_admin
def admin_users():
    return jsonify({"ok": True, "users": list_users()})


@app.route("/api/admin/give_item", methods=["POST"])
@require_admin
def admin_give_item():
    """给指定玩家发放物品"""
    data = request.json
    target_uid = data.get("user_id")
    item_id = data.get("item_id")
    qty = data.get("qty", 1)
    from user_system import load_player_state, save_player_state
    import json as _json
    state_json = load_player_state(target_uid)
    if not state_json:
        return jsonify({"ok": False, "msg": "玩家无存档"})
    state = _json.loads(state_json)
    inv = state["player"]["inventory"]
    found = False
    for i in inv:
        if i["item_id"] == item_id:
            i["qty"] += qty
            found = True
            break
    if not found:
        inv.append({"item_id": item_id, "qty": qty})
    save_player_state(target_uid, _json.dumps(state, ensure_ascii=False))
    return jsonify({"ok": True, "msg": f"已发放{item_id}×{qty}给用户{target_uid}"})


@app.route("/api/admin/set_realm", methods=["POST"])
@require_admin
def admin_set_realm():
    """设置玩家境界"""
    data = request.json
    target_uid = data.get("user_id")
    realm = data.get("realm")
    from user_system import load_player_state, save_player_state
    from data_loader import get_realm
    import json as _json
    state_json = load_player_state(target_uid)
    if not state_json:
        return jsonify({"ok": False, "msg": "玩家无存档"})
    state = _json.loads(state_json)
    r = get_realm(realm)
    if not r:
        return jsonify({"ok": False, "msg": "无效境界"})
    state["player"]["realm"] = realm
    state["player"]["realm_progress"] = 0.0
    state["player"]["lifespan"] = max(state["player"]["lifespan"], r["lifespan"])
    save_player_state(target_uid, _json.dumps(state, ensure_ascii=False))
    return jsonify({"ok": True, "msg": f"已设置用户{target_uid}境界为{r['name']}"})


@app.route("/api/admin/add_spirit_stones", methods=["POST"])
@require_admin
def admin_add_stones():
    """给玩家加灵石"""
    data = request.json
    target_uid = data.get("user_id")
    amount = data.get("amount", 100)
    from user_system import load_player_state, save_player_state
    import json as _json
    state_json = load_player_state(target_uid)
    if not state_json:
        return jsonify({"ok": False, "msg": "玩家无存档"})
    state = _json.loads(state_json)
    state["player"]["spirit_stones"]["low"] += amount
    save_player_state(target_uid, _json.dumps(state, ensure_ascii=False))
    return jsonify({"ok": True, "msg": f"已发放{amount}下品灵石给用户{target_uid}"})


@app.route("/api/admin/broadcast", methods=["POST"])
@require_admin
def admin_broadcast():
    """全服公告（写入所有玩家日志）"""
    data = request.json
    msg = data.get("msg", "")
    from user_system import list_player_saves, load_player_state, save_player_state
    import json as _json, time
    count = 0
    for save in list_player_saves(0):  # 占位，实际遍历所有用户
        pass
    # 简化：遍历所有用户
    for u in list_users():
        state_json = load_player_state(u["id"])
        if state_json:
            state = _json.loads(state_json)
            state["log"].append({"t": state["world"]["game_time"], "msg": f"【全服公告】{msg}", "level": "event"})
            save_player_state(u["id"], _json.dumps(state, ensure_ascii=False))
            count += 1
    return jsonify({"ok": True, "msg": f"公告已发送给{count}位玩家"})


@app.route("/api/admin/data/<data_type>", methods=["GET"])
@require_admin
def admin_view_data(data_type):
    """查看数据"""
    from data_loader import _load
    valid = ["materials","techniques","pills","beasts","regions","npcs","sects","storylines","causal_chains","forge_recipes","formations","auction_items","pvp_opponents","tribulations","realms"]
    if data_type not in valid:
        return jsonify({"ok": False, "msg": "无效数据类型"})
    return jsonify({"ok": True, "data": _load(data_type)})


def get_storylines_data():
    from data_loader import get_storylines
    return get_storylines()


if __name__ == "__main__":
    print("=" * 60)
    print("  《逆仙录·天道残卷》服务启动")
    print("  访问 http://localhost:5000 开始游戏")
    print("  默认管理员: admin / admin123")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
