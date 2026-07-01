from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            method TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            schedule_date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )
    """)

    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        name = request.form["name"]
        ingredients = request.form["ingredients"]
        method = request.form["method"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO recipes (name, ingredients, method) VALUES (?, ?, ?)",
            (name, ingredients, method)
        )
        conn.commit()
        conn.close()

        return redirect("/recipes")

    return render_template("add_recipe.html")

@app.route("/recipes")
def recipes():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM recipes ORDER BY id DESC")
    recipes = cur.fetchall()
    conn.close()

    return render_template("recipes.html", recipes=recipes)

@app.route("/recipe/<int:id>")
def recipe_detail(id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name, ingredients, method FROM recipes WHERE id=?", (id,))
    recipe = cur.fetchone()
    conn.close()

    ingredients = [i.strip() for i in recipe[2].splitlines() if i.strip()]
    method = [m.strip() for m in recipe[3].splitlines() if m.strip()]

    return render_template(
        "recipe_detail.html",
        recipe=recipe,
        ingredients=ingredients,
        method=method
    )

@app.route("/delete_recipe/<int:id>")
def delete_recipe(id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM schedules WHERE recipe_id=?", (id,))
    cur.execute("DELETE FROM recipes WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/recipes")

@app.route("/add_schedule", methods=["GET", "POST"])
def add_schedule():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM recipes")
    recipes = cur.fetchall()
    conn.close()

    if request.method == "POST":
        recipe_id = request.form["recipe_id"]
        schedule_date = request.form["schedule_date"]
        meal_type = request.form["meal_type"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO schedules (recipe_id, schedule_date, meal_type) VALUES (?, ?, ?)",
            (recipe_id, schedule_date, meal_type)
        )
        conn.commit()
        conn.close()

        return redirect("/schedule")

    return render_template("add_schedule.html", recipes=recipes)

@app.route("/schedule")
def schedule():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT schedules.id, recipes.name, schedules.schedule_date, schedules.meal_type
        FROM schedules
        JOIN recipes ON schedules.recipe_id = recipes.id
        ORDER BY schedules.schedule_date ASC
    """)
    schedules = cur.fetchall()
    conn.close()

    return render_template("schedule.html", schedules=schedules)

@app.route("/delete_schedule/<int:id>")
def delete_schedule(id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM schedules WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/schedule")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)