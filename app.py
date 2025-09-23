import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from utils import get_db_connection, strong_password
import secrets

app = Flask(__name__)
app.secret_key = "2HW?ei123#4_HE034nw!-jU4Mn2&!?f"

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password2 = request.form["password2"]
        
        if not strong_password(password):
            return render_template("register.html", error="Salasanan tulee sisältää vähintään 8 merkkiä, numero ja erikoismerkki")

        if password != password2:
            return render_template("register.html", error="Salasanat eivät täsmää")
        else:
            hashing_pass = generate_password_hash(password)
        
        connecting = get_db_connection()
        try: 
            connecting.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashing_pass))
            connecting.commit()
        
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Joku toinen ehti ensin. Valitse toinen käyttäjänimi")
        except Exception as e:
            return render_template("register.html", error="Virhe rekisteröinnissä: " + str(e))
        finally:
            connecting.close()
        return redirect("/login")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method =="POST":
        username = request.form["username"]
        password = request.form["password"]

        with get_db_connection() as connecting:
            user = connecting.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["session_token"] = secrets.token_hex(16)
            return redirect(url_for("diary"))
        else:
            return render_template("login.html", error="Hupsis, käyttäjätunnus tai salasana eivät täsmää")
        
    return render_template("login.html")

@app.route("/logout",)
def logout():
    session.clear()
    return redirect("/login")
    

@app.route("/paivakirja")
def diary():
    if "user_id" not in session:
        return redirect("/login")
    
    with get_db_connection() as connecting:
        entries = connecting.execute(
            "SELECT * FROM entries WHERE user_id = ? ORDER BY created_at DESC",
            (session["user_id"],)
        ).fetchall()

    return render_template("paivakirja.html", entries=entries, username=session["username"])

@app.route("/uusijuoksu", methods=["GET", "POST"])
def add_entry():

    if "user_id" not in session:
        return redirect("/login")
    
    if request.method == "POST":
        km = request.form.get("km")
        m = request.form.get("m")
        runtime = request.form.get("runtime")
        terrain = request.form.get("terrain")
        run_type = request.form.get("run_type")
        race_name = request.form.get("race_name")
        other = request.form.get("other")

        if not km or not m or not runtime or not terrain or not run_type:
            with get_db_connection() as connecting:
                terrains = connecting.execute("SELECT name FROM terrains").fetchall()
                run_types = connecting.execute("SELECT name FROM run_types").fetchall()
            return render_template(
                "add_entry.html",
                error="Tarkista, että kaikki * merkityt kohdat on täytetty.",
                terrains = terrains,
                run_types= run_types
            )

        with get_db_connection() as connecting:
            connecting.execute(
                """INSERT INTO entries (user_id, distance_km, distance_m, runtime, terrain, run_type, race_name, other)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (session["user_id"], km, m, runtime, terrain, run_type, race_name, other)
            )
            connecting.commit()
        return redirect("/paivakirja")
    
    with get_db_connection() as connecting:
        terrains = connecting.execute("SELECT name FROM terrains").fetchall()
        run_types = connecting.execute("SELECT name FROM run_types").fetchall()
    return render_template("add_entry.html", terrains = terrains, run_types = run_types)
        
@app.route("/edit_entry/<int:entry_id>", methods=["GET", "POST"])

def edit_entry(entry_id):
    if "user_id" not in session:
        return redirect("login")
    
    with get_db_connection() as connecting:
        entry = connecting.execute(
            "SELECT * FROM entries WHERE id = ? AND user_id = ?",
            (entry_id, session["user_id"])
        ).fetchone()

        terrains = connecting.execute("SELECT name FROM terrains").fetchall()
        run_types = connecting.execute("SELECT name FROM run_types").fetchall()

    if entry is None:
        return "Muokattavaa merkintää ei löytynyt", 403
    
    if request.method == "POST":
        km = request.form.get("km")
        m = request.form.get("m")
        runtime = request.form.get("runtime")
        terrains = request.form.getlist("terrain")
        terrain = ",".join(terrains) if terrains else ""
        run_type = request.form.get("run_type")
        race_name = request.form.get("race_name")
        other = request.form.get("other")

        if not km or not m or not runtime or not terrain or not run_type:
            return render_template("edit_entry.html", entry=entry, error="Tarkista, että * merkityt kentät on täytetty.")
            
        with get_db_connection() as connecting:
            connecting.execute(
                """UPDATE entries
                    SET distance_km = ?, distance_m = ?, runtime = ?, terrain = ?, run_type = ?, race_name = ?, other = ?
                    WHERE id = ? AND user_id = ?""",
                    (km, m, runtime, terrain, run_type, race_name, other, entry_id, session["user_id"])
            )
            connecting.commit()
       
        return redirect("/paivakirja")

    return render_template("edit_entry.html", entry = entry, terrains = terrains, run_types = run_types)

@app.route("/delete_entry/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    if "user_id" not in session:
        return redirect("/login")
    
    with get_db_connection() as connecting:
        connecting.execute(
            "DELETE FROM entries WHERE id = ? AND user_id = ?",
            (entry_id, session["user_id"])
    )
    connecting.commit()
    return redirect("/paivakirja")
    
@app.route("/browseruns", methods=["GET"])
def browse_runs():

    km = request.args.get("km")
    terrain = request.args.get("terrain")
    run_type = request.args.get("run_type")
    username = request.args.get("username")


    search = """
            SELECT entries.*, users.username
            FROM entries
            JOIN users ON entries.user_id = users.id
            WHERE 1=1
            """
    search_conditions = []
    if km:
        search += " AND entries.distance_km = ?"
        search_conditions.append(int(km))
    if terrain:
        search += " AND entries.terrain = ?"
        search_conditions.append(terrain)
    if run_type:
        search += " AND entries.run_type = ?"
        search_conditions.append(run_type)
    if username:
        search += " AND users.username LIKE ?"
        search_conditions.append(f"%{username}%")

    search += " ORDER BY entries.created_at DESC"

    with get_db_connection() as connecting:
        runs = connecting.execute(search, search_conditions).fetchall()

    return render_template("browseruns.html", runs=runs)
    

@app.route("/kisat")
def competitions():
    with get_db_connection() as connecting:
        dif_competitions = connecting.execute("SELECT * FROM competitions").fetchall()
    return render_template("kisat.html", competitions=dif_competitions)

@app.route("/kayttaja/<int:page_id>")
def user_page(page_id):
    return "Käyttäjien sivut tulossa pian!"


if __name__ == "__main__":
    app.run(debug=True)