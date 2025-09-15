from flask import Flask, render_template, g, abort, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # доступ по именам колонок
    return g.db

@app.teardown_appcontext
def close_db(error):
    if "db" in g:
        g.db.close()

# Главная страница
@app.route("/")
def index():
    return render_template("index.html")

# Каталог модулей
@app.route("/catalog")
def catalog():
    db = get_db()
    modules = db.execute("SELECT * FROM modules").fetchall()
    return render_template("catalog.html", modules=modules)

# Страница отдельного модуля
@app.route("/module/<int:module_id>")
def module_detail(module_id):
    db = get_db()
    module = db.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    if module is None:
        abort(404)
    return render_template("module_detail.html", module=module)

# Конфигуратор модуля
@app.route("/module/<int:module_id>/configure", methods=["GET", "POST"])
def module_configurator(module_id):
    db = get_db()
    module = db.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
    if module is None:
        abort(404)

    materials = ["Пленка", "Пластик", "Эмаль"]
    hardware = ["Blum", "Hettich"]

    if request.method == "POST":
        # обработка данных формы
        return redirect(url_for("cart"))

    return render_template(
        "module_configurator.html",
        module=module,
        materials=materials,
        hardware=hardware,
    )

# Корзина
@app.route("/cart")
def cart():
    cart = [{"name": "Шкаф 600", "price": 5000}]
    summary = {"materials": 3000, "work": 1500, "discounts": -500, "total": 4000}
    return render_template("cart.html", cart=cart, summary=summary)

# Сохраненные расчеты
@app.route("/saved")
def saved_calculations():
    calculations = [{"id": 1}, {"id": 2}]
    return render_template("saved_calculations.html", calculations=calculations)

if __name__ == "__main__":
    app.run(debug=True)
