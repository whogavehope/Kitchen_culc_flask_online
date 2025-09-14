from flask import Flask, render_template, g, abort
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # чтобы обращаться по именам колонок
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

if __name__ == "__main__":
    app.run(debug=True)
