import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from utils import get_db_connection, strong_password
import secrets
import os


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(20))

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

        record_run = connecting.execute(
            "SELECT MAX(distance_km * 1000 + distance_m) AS max_distance FROM entries WHERE user_id = ?",
            (session['user_id'],)
        ).fetchone()['max_distance']

        competition_count = connecting.execute(
            "SELECT COUNT(*) AS cnt FROM entries WHERE user_id = ? AND race_name IS NOT NULL AND race_name !=''",
            (session["user_id"],)
        ).fetchone()["cnt"]

        support_count = connecting.execute(
            "SELECT COUNT(*) AS cnt FROM supports WHERE supported_id = ?",
            (session["user_id"],)
        ).fetchone()["cnt"]

    return render_template("paivakirja.html", entries=entries, username=session["username"], record_run=record_run, competition_count=competition_count, support_count=support_count)

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

@app.route("/kisa_sivu/<int:competition_id>", methods=["GET","POST"])
def competition(competition_id):
    if request.method == "POST":
        if "user_id" not in session:
            return redirect("login")
        comment = request.form.get("comment")
        if comment:
            with get_db_connection() as connecting:
                connecting.execute(
                    "INSERT INTO competition_comments (competition_id, user_id, comment) VALUES (?, ?, ?)",
                    (competition_id, session["user_id"], comment)
                )
                connecting.commit()
        return redirect(url_for("competition", competition_id=competition_id,))


    with get_db_connection() as connecting:
        competition = connecting.execute(
            "SELECT * FROM competitions WHERE id = ?", (competition_id,)
        ).fetchone()

        if competition is None:
            return "Kilpailua ei löytynyt", 404
        
        top_result = connecting.execute("""
            SELECT users.username, runtime
            FROM entries
            JOIN users ON entries.user_id = users.id
            WHERE race_name = ?
            ORDER BY runtime ASC
            LIMIT 10                            
        """, (competition['name'],)).fetchall()

        comments = connecting.execute("""
            SELECT competition_comments.comment, competition_comments.created_at, users.username
            FROM competition_comments
            JOIN users ON competition_comments.user_id = users.id
            WHERE competition_comments.competition_id = ?
            ORDER BY competition_comments.created_at DESC
            LIMIT 15
        """, (competition_id,)).fetchall()
    return render_template("kisa_sivu.html", competition=competition, top_result=top_result, comments=comments)


@app.route("/kayttaja/<username>", methods=["GET", "POST"])
def user_page(username):
    with get_db_connection() as connecting:
        user = connecting.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not user:
            return "Käyttäjää ei löytynyt", 404
        
        entries = connecting.execute(
            "SELECT * FROM entries WHERE user_id = ? ORDER BY created_at DESC",
            (user["id"],)
        ).fetchall()

        record_run = connecting.execute(
            "SELECT MAX(distance_km * 1000 + distance_m) AS max_distance FROM entries WHERE user_id = ?",
            (user["id"],)
        ).fetchone()['max_distance']

        competition_count = connecting.execute(
            "SELECT COUNT(*) AS cnt FROM entries WHERE user_id = ? AND race_name IS NOT NULL AND race_name !=''",
            (user["id"],)
        ).fetchone()["cnt"]

        support_count = connecting.execute(
            "SELECT COUNT(*) AS cnt FROM supports WHERE supported_id = ?",
            (user["id"],)
        ).fetchone()["cnt"]

        already_supported = False
        if "user_id" in session:
            row = connecting.execute(
                "SELECT 1 FROM supports WHERE supporter_id = ? AND supported_id = ?",
                (session["user_id"], user["id"])
            ).fetchone()
            already_supported = row is not None

    if request.method == "POST":
        if "user_id" not in session:
            return redirect("/login")
        with get_db_connection() as connecting:
            try:
                connecting.execute(
                    "INSERT INTO supports (supporter_id, supported_id) VALUES (?, ?)",
                    (session["user_id"], user["id"])
                )
                connecting.commit()
            except sqlite3.IntegrityError:
                pass
        return redirect(url_for("user_page", username=username))
    
    return render_template("user_page.html", profile_user=user, entries=entries, record_run=record_run, competition_count=competition_count, support_count=support_count, already_supported=already_supported)
        

if __name__ == "__main__":
    app.run(debug=True)