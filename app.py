import sqlite3
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from utils import get_db_connection, strong_password
import config
from queries import validate_runtime, already_supported, add_support, get_top_results, get_competition, add_comments_competition, get_username, create_user, add_entry, get_entries, get_entry, get_max_distance, get_competition_count, get_support_count, search_runs, update_entry, delete_entry, get_competitions, get_comments_competition, get_terrains, get_run_types


app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    return render_template("base.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("fname", "").strip()
        last_name = request.form.get("lname", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        
        if not first_name: 
            return render_template("register.html", error="Etunimi on pakollinen", first_name=first_name, last_name=last_name, username=username)

        if not last_name: 
            return render_template("register.html", error="Sukunimi on pakollinen", first_name=first_name, last_name=last_name, username=username)

        if not username: 
            return render_template("register.html", error="Käyttäjänimi on pakollinen", first_name=first_name, last_name=last_name, username=username)

        if not strong_password(password):
            return render_template("register.html", error="Salasanan tulee sisältää vähintään 8 merkkiä, numero ja erikoismerkki",
                                   first_name=first_name, last_name=last_name, username=username)

        if password != password2:
            return render_template("register.html", error="Salasanat eivät täsmää",
                                   first_name=first_name, last_name=last_name, username=username)
        else:
            hashing_pass = generate_password_hash(password)
        
        try: 
            create_user(username, hashing_pass)
        
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Joku toinen ehti ensin. Valitse toinen käyttäjänimi",
                                   first_name=first_name, last_name=last_name,)
        except Exception as e:
            return render_template("register.html", error="Virhe rekisteröinnissä: " + str(e),
                                first_name=first_name, last_name=last_name, username=username)

        return redirect("/login")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method =="POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_username(username)

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("diary"))
        else:
            return render_template("login.html", error="Hupsis, käyttäjätunnus tai salasana eivät täsmää")
        
    return render_template("login.html")

@app.route("/logout",)
def logout():
    session.clear()
    return redirect("/login")
    

@app.route("/personal_diary")
def diary():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]    
    entries = get_entries(user_id)

    record_run = get_max_distance(user_id)
    competition_count = get_competition_count(user_id)
    support_count = get_support_count(user_id)

    return render_template("personal_diary.html", entries=entries, username=session["username"], record_run=record_run, competition_count=competition_count, support_count=support_count)

@app.route("/new_run", methods=["GET", "POST"])
def add_entry_route():

    if "user_id" not in session:
        return redirect("/login")
    
    terrains = get_terrains()
    run_types = get_run_types()
    
    if request.method == "POST":
        km = request.form.get("km", "").strip()
        m = request.form.get("m", "").strip()
        runtime = request.form.get("runtime", "").strip()
        terrains_selected = request.form.getlist("terrain")
        terrain = ",".join(terrains_selected) if terrains_selected else ""
        run_type = request.form.get("run_type", "").strip()
        race_name = request.form.get("race_name", "").strip()
        other = request.form.get("other", "").strip()

        if not km or not m or not runtime or not terrain or not run_type:
            return render_template(
                "add_entry.html",
                error="Tarkista, että kaikki * merkityt kohdat on täytetty.",
                terrains = terrains,
                run_types= run_types
            )
        try:
            km = int(km)
            m = int(m)
            if km < 0 or m < 0:
                raise ValueError
        except ValueError:
            return render_template(
                "add_entry.html",
                error="Ilmoita matkan määrä numeroina.",
                terrains=terrains,
                run_types=run_types
            )

        add_entry(session["user_id"], km, m, runtime, terrain, run_type, race_name, other)
        return redirect("/personal_diary")
    
    return render_template("add_entry.html", terrains = terrains, run_types = run_types)
        
@app.route("/edit_entry/<int:entry_id>", methods=["GET", "POST"])

def edit_entry(entry_id):
    if "user_id" not in session:
        return redirect("/login")
    
    entry = get_entry(entry_id, session["user_id"])
    terrains = get_terrains()
    run_types = get_run_types()

    if entry is None:
        return "Muokattavaa merkintää ei löytynyt", 403
    
    if request.method == "POST":
        km_str = request.form.get("km", "").strip()
        m_str = request.form.get("m", "").strip()
        if not km_str.isdigit() or not m_str.isdigit():
            return render_template("edit_entry.html", entry=entry, terrains=terrains, run_types=run_types, error = "Ilmoita matkan määrä numeroina.")
        km = int(km_str)
        m = int(m_str)
        if km < 0 or m < 0:
            return render_template("edit_entry.html", entry=entry, terrains=terrains, run_types=run_types, error="Matkan määrä ei voi olla negatiivinen.")
        
        runtime = request.form.get("runtime", "").strip()
        try:
            validate_runtime(runtime)
        except ValueError as e:
            return render_template("edit_entry.html", entry=entry, terrains=terrains, run_types=run_types, error=str(e))
        terrains_selected = request.form.getlist("terrain")
        terrain = ",".join(terrains_selected) if terrains_selected else ""
        run_type = request.form.get("run_type", "").strip()
        race_name = request.form.get("race_name", "").strip()
        other = request.form.get("other", "").strip()


        if runtime == "" or not terrain or run_type == "":
            return render_template("edit_entry.html", entry=entry, terrains=terrains, run_types=run_types, error = "Tarkista, että * merkityt kentät on täytetty.")
        
            
        update_entry(entry_id, session["user_id"], km, m, runtime, terrain, run_type, race_name, other)
       
        return redirect("/personal_diary")

    return render_template("edit_entry.html", entry = entry, terrains = terrains, run_types = run_types)

@app.route("/delete_entry/<int:entry_id>", methods=["POST"])
def delete_entry_route(entry_id):
    if "user_id" not in session:
        return redirect("/login")
    
    delete_entry(entry_id, session["user_id"])

    return redirect("/personal_diary")
    
@app.route("/browseruns", methods=["GET"])
def browse_runs():
    km = request.args.get("km")
    terrain = request.args.getlist("terrain")
    run_type = request.args.get("run_type")
    username = request.args.get("username")

    runs = search_runs(km=km, terrain=terrain, run_type=run_type, username=username)

    return render_template("browseruns.html", runs=runs)
    

@app.route("/competition")
def competitions():
        competitions = get_competitions()
        return render_template("competition.html", competitions = competitions)

@app.route("/comp_page/<int:competition_id>", methods=["GET","POST"])
def competition(competition_id):
    if request.method == "POST":
        if "user_id" not in session:
            return redirect("/login")
        comment = request.form.get("comment", "").strip()
        if not comment:
            return redirect(url_for("competition", competition_id=competition_id))
        
        add_comments_competition(competition_id, session["user_id"], comment)
        return redirect(url_for("competition", competition_id=competition_id,))


    competition = get_competition(competition_id)

    if competition is None:
        return "Kilpailua ei löytynyt", 404
        
    top_result = get_top_results(competition["name"])

    comments = get_comments_competition(competition_id)
    return render_template("comp_page.html", competition=competition, top_result=top_result, comments=comments)


@app.route("/kayttaja/<username>", methods=["GET", "POST"])
def user_page(username):
    user = get_username(username)
    if not user:
        return "Käyttäjää ei löytynyt", 404
    
    user_id = user["id"]    
    entries = get_entries(user_id)
    try:
        record_run = get_max_distance(user_id)
        competition_count = get_competition_count(user_id)
        support_count = get_support_count(user_id)

    except Exception as e:
        return render_template("error.html", error=str(e))
    
    is_already_supported = False
    if "user_id" in session:
        is_already_supported = already_supported(session["user_id"], user["id"])

    if request.method == "POST":
        if "user_id" not in session:
            return redirect("/login")
        try:
            add_support(session["user_id"], user["id"])
        except sqlite3.IntegrityError:
            pass
        return redirect(url_for("user_page", username=username))

    return render_template("user_page.html", profile_user=user, entries=entries, record_run=record_run, competition_count=competition_count, support_count=support_count, is_already_supported=is_already_supported)
        

if __name__ == "__main__":
    app.run(debug=True)