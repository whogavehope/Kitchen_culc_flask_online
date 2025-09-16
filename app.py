from flask import (
    Flask, render_template, g, abort,
    request, redirect, url_for, session, flash
)
import sqlite3
import json

app = Flask(__name__)
# Поменяй на свой секрет в проде
app.secret_key = "change_this_to_a_random_secret"

DATABASE = "database.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# --- Cart helpers (session) ---
def get_cart():
    return session.get("cart", [])

def save_cart(cart):
    session["cart"] = cart
    session.modified = True

def add_item_to_cart(item):
    cart = get_cart()
    cart.append(item)
    save_cart(cart)

def remove_item_from_cart(index):
    cart = get_cart()
    if 0 <= index < len(cart):
        cart.pop(index)
        save_cart(cart)

def clear_cart():
    session.pop("cart", None)

# --- Price calc helper ---
def compute_price(module_row, material_name, quantity, options):
    """
    Простая оценка цены:
    unit_price = base_price + material.price + prices.extra_price + labor.rate + options extras
    возвращает (unit_price, total_price)
    """
    db = get_db()
    base = module_row["base_price"] or 0.0

    mat_row = db.execute(
        "SELECT id, price FROM materials WHERE name = ?", (material_name,)
    ).fetchone()
    mat_price = mat_row["price"] if mat_row else 0.0

    extra_price = 0.0
    if mat_row:
        row = db.execute(
            "SELECT extra_price FROM prices WHERE module_id = ? AND material_id = ?",
            (module_row["id"], mat_row["id"]),
        ).fetchone()
        extra_price = row["extra_price"] if row else 0.0

    labor_row = db.execute(
        "SELECT rate FROM labor_rates WHERE module_id = ?", (module_row["id"],)
    ).fetchone()
    labor = labor_row["rate"] if labor_row else 0.0

    opts_extra = 0.0
    # простая логика цен на опции — можно изменить
    if options.get("frez"):
        opts_extra += 200.0
    if options.get("glass"):
        opts_extra += 400.0

    unit_price = base + mat_price + extra_price + labor + opts_extra
    total_price = unit_price * max(1, int(quantity))
    return round(unit_price, 2), round(total_price, 2)


# --- Routes ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/catalog")
def catalog():
    db = get_db()
    modules = db.execute("SELECT * FROM modules").fetchall()
    return render_template("catalog.html", modules=modules)

@app.route("/module/<int:module_id>")
def module_detail(module_id):
    db = get_db()
    module = db.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    if module is None:
        abort(404)
    return render_template("module_detail.html", module=module)

@app.route("/module/<int:module_id>/configure", methods=["GET", "POST"])
def module_configurator(module_id):
    db = get_db()
    module = db.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    if module is None:
        abort(404)

    # список материалов из БД (если пусто — дефолт)
    mats = db.execute("SELECT name FROM materials ORDER BY name").fetchall()
    materials = [r["name"] for r in mats] if mats else ["Пленка", "Пластик", "Эмаль"]
    hardware = ["Blum", "Hettich", "Другой"]

    if request.method == "POST":
        # читаем поля формы
        width = int(request.form.get("width") or 0)
        height = int(request.form.get("height") or 0)
        depth = int(request.form.get("depth") or (module["depth"] or 0))
        material = request.form.get("material")
        hardware_sel = request.form.get("hardware")
        quantity = int(request.form.get("quantity") or 1)
        frez = True if request.form.get("frez") else False
        glass = True if request.form.get("glass") else False

        options = {"hardware": hardware_sel, "frez": frez, "glass": glass}

        unit_price, total_price = compute_price(module, material, quantity, options)

        item = {
            "module_id": module["id"],
            "module_name": module["name"],
            "width": width,
            "height": height,
            "depth": depth,
            "material": material,
            "hardware": hardware_sel,
            "quantity": quantity,
            "options": options,
            "unit_price": unit_price,
            "total_price": total_price
        }

        add_item_to_cart(item)
        flash("Позиция добавлена в корзину")
        return redirect(url_for("cart"))

    return render_template(
        "module_configurator.html",
        module=module,
        materials=materials,
        hardware=hardware
    )

@app.route("/cart")
def cart():
    cart = get_cart()
    # подсчёт сводки
    materials_sum = sum(item.get("unit_price", 0) * item.get("quantity", 1) for item in cart)
    # доп. логика: считаем работу отдельно если надо; для примера возьмём labor в total уже включённый,
    # поэтому для сводки разделим на "materials" и "work" по простому правилу (пример)
    work = sum(0 for _ in cart)  # пока 0 — ты можешь добавить реальные ставки
    discounts = 0
    total = sum(item.get("total_price", 0) for item in cart) + work + discounts
    summary = {
        "materials": round(materials_sum, 2),
        "work": round(work, 2),
        "discounts": round(discounts, 2),
        "total": round(total, 2)
    }
    return render_template("cart.html", cart=cart, summary=summary)

@app.route("/cart/remove/<int:index>")
def cart_remove(index):
    remove_item_from_cart(index)
    flash("Позиция удалена")
    return redirect(url_for("cart"))

@app.route("/cart/clear")
def cart_clear():
    clear_cart()
    flash("Корзина очищена")
    return redirect(url_for("cart"))

@app.route("/cart/save", methods=["POST"])
def cart_save():
    cart = get_cart()
    if not cart:
        flash("Корзина пуста")
        return redirect(url_for("cart"))

    customer_name = request.form.get("customer_name") or "Клиент"
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO orders (customer_name) VALUES (?)", (customer_name,))
    order_id = cur.lastrowid

    for item in cart:
        # material id (если нет — создаём)
        mat = db.execute("SELECT id FROM materials WHERE name = ?", (item["material"],)).fetchone()
        if mat:
            material_id = mat["id"]
        else:
            # создаём с ценой 0, type "unknown"
            cur.execute("INSERT INTO materials (name, type, price) VALUES (?, ?, ?)", (item["material"], "unknown", 0.0))
            material_id = cur.lastrowid

        cur.execute(
            """INSERT INTO order_items
               (order_id, module_id, quantity, width, height, depth, material_id, price, options)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                order_id,
                item["module_id"],
                item["quantity"],
                item["width"],
                item["height"],
                item["depth"],
                material_id,
                item["total_price"],
                json.dumps(item.get("options", {}), ensure_ascii=False)
            )
        )

    db.commit()
    clear_cart()
    flash("Расчёт сохранён в заказе #{}".format(order_id))
    return redirect(url_for("order_detail", order_id=order_id))

@app.route("/saved")
def saved_calculations():
    db = get_db()
    rows = db.execute(
        """SELECT o.id, o.customer_name, o.created_at, COALESCE(SUM(oi.price),0) AS total
           FROM orders o
           LEFT JOIN order_items oi ON o.id = oi.order_id
           GROUP BY o.id
           ORDER BY o.created_at DESC"""
    ).fetchall()
    return render_template("saved_calculations.html", calculations=rows)

@app.route("/order/<int:order_id>")
def order_detail(order_id):
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        abort(404)
    items = db.execute(
        """SELECT oi.*, m.name AS module_name, mat.name AS material_name
           FROM order_items oi
           LEFT JOIN modules m ON oi.module_id = m.id
           LEFT JOIN materials mat ON oi.material_id = mat.id
           WHERE oi.order_id = ?""",
        (order_id,)
    ).fetchall()
    # парсим JSON options для отображения
    parsed_items = []
    for it in items:
        opts = {}
        try:
            opts = json.loads(it["options"]) if it["options"] else {}
        except Exception:
            opts = {}
        parsed_items.append(dict(it))
        parsed_items[-1]["options_parsed"] = opts

    return render_template("order_detail.html", order=order, items=parsed_items)

@app.route("/order/<int:order_id>/load")
def order_load(order_id):
    """
    Загружаем сохранённый расчёт обратно в корзину (в session).
    """
    db = get_db()
    items = db.execute("SELECT oi.*, mat.name AS material_name FROM order_items oi LEFT JOIN materials mat ON oi.material_id = mat.id WHERE oi.order_id = ?", (order_id,)).fetchall()
    if not items:
        flash("Нет позиций для этого расчёта")
        return redirect(url_for("saved_calculations"))

    new_cart = []
    for it in items:
        opts = {}
        try:
            opts = json.loads(it["options"]) if it["options"] else {}
        except Exception:
            opts = {}
        new_cart.append({
            "module_id": it["module_id"],
            "module_name": it.get("module_name") or f"Модуль {it['module_id']}",
            "width": it["width"],
            "height": it["height"],
            "depth": it["depth"],
            "material": it.get("material_name") or "",
            "quantity": it["quantity"],
            "options": opts,
            "unit_price": round((it["price"] or 0) / max(1, it["quantity"]), 2),
            "total_price": it["price"] or 0
        })

    save_cart(new_cart)
    flash("Расчёт загружен в корзину")
    return redirect(url_for("cart"))

if __name__ == "__main__":
    app.run(debug=True)