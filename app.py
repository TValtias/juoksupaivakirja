import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from utils import get_db_connection, strong_password
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route("/")
def index():
    return "Tähän tulee juoksupäiväkirja"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["Salasana"]
        password2 = request.form["Salasana uudestaan"]
        
        if not strong_password(password):
            return render_template("register.html", error="Salasanan tulee sisältää vähintään 8 merkkiä, numero ja erikoismerkki")

        if password != password2:
            return render_template("register.html", error="Salasanat eivät täsmää")
        else:
            hashing_pass = generate_password_hash(password)
        
        connecting = get_db_connection()
        try: 
            connecting.execute("INSERT INTO users (username, password) VALUES (?, ?)",
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
        username = request.form["käyttäjänimi"]
        password = request.form["Salasana"]

        with get_db_connection() as connecting:
            user = connecting.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/paivakirja")
        else:
            return render_template("login.html", error="Hupsis, tarkista käyttäjätunnus tai salasana")
        
    return render_template("login.html")
    


@app.route("/paivakirja")
def diary():
    if "user_id" not in session:
        return redirect("/login")
    
    connecting = get_db_connection()
    entries = connecting.execute(
        "SELECT * FROM entries WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()
    connecting.close()

    return render_template("paivakirja.html", entries=entries, username=session["username"])

@app.route("/uusijuoksu", methods=["POST"])
def add_entry():
    if "user_id" not in session:
        return redirect("/login")
    
    km = request.form["km"]
    m = request.form["m"]
    time = request.form["time"]
    terrain = request.form["terrain"]
    run_type = request.form["run_type"]
    race_name = request.form.get("race_name")

    connecting = get_db_connection()
    connecting.execute(
        """INSERT INTO entries (user_id, distance_km, distance_m, time, terrain, run_type, race_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session["user_id"], km, m, time, terrain, run_type, race_name)
    )
    
    connecting.commit()
    connecting.close()

    return redirect("/paivakirja")
    
    

@app.route("/kisat")
def competitions():
    return "Kisat tulossa pian!"

@app.route("/kayttaja/<int:page_id>")
def user_page(page_id):
    return "Käyttäjien sivut tulossa pian!"