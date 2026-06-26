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


if __name__ == "__main__":
    print("=" * 60)
    print("  《逆仙录·天道残卷》服务启动")
    print("  访问 http://localhost:5000 开始游戏")
    print("  默认管理员: admin / admin123")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
