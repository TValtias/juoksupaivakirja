import secrets
import sqlite3
from flask import (
    Flask, redirect, render_template,
    request, session, url_for, abort
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
import config
from utils import strong_password, validate_entry_form, validate_runtime
from queries import (
    already_supported, add_support,
    get_top_results, get_competition, add_comments_competition,
    get_username, create_user, add_entry,
    get_entries, get_entry, get_max_distance,
    get_competition_count, get_support_count, search_runs,
    update_entry, delete_entry, get_competitions,
    get_comments_competition, get_terrains, get_run_types
)

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    """ Show's the applications main page"""
    return render_template("base.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """User's registration.
    GET shows the registration form
    POST validates user input and creates a new user.
    """
    if request.method == "POST":
        first_name = request.form.get("fname", "").strip()
        last_name = request.form.get("lname", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        errors = []
        if not first_name:
            errors.append("Etunimi puuttuu")

        if not last_name:
            errors.append("Sukunimi puuttuu")

        if not username:
            errors.append("Käyttäjänimi puuttuu")

        if not password:
            errors.append("Salasana puuttuu")

        elif not strong_password(password):
            errors.append(
                "Salasanan tulee sisältää vähintään 8 merkkiä, numeron ja erikoismerkin"
            )

        if password != password2:
            errors.append("Salasanat eivät täsmää")

        if errors:
            return render_template(
                "register.html",
                errors=errors,
                first_name=first_name,
                last_name=last_name,
                username=username
            )

        hashing_pass = generate_password_hash(password)
        try:
            create_user(username, hashing_pass)
        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                errors=["Joku toinen ehti ensin. Valitse toinen käyttäjänimi"],
                first_name=first_name,
                last_name=last_name,
            )
        except Exception as e:
            return render_template(
                "register.html",
                errors=[f"Virhe rekisteröinnissä: {e}"],
                first_name=first_name,
                last_name=last_name,
                username=username
            )

        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login.
    GET shows login page
    POST checks that username and password match, creates a session and CSRF-token
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = get_username(username)

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["csrf_token"] = secrets.token_hex(16)
            return redirect(url_for("diary"))
        return render_template(
                "login.html",
                error="Hupsis, käyttäjätunnus tai salasana eivät täsmää"
            )
    return render_template("login.html")

def check_csrf():
    """Checks that form's CSRF-token matches the session token. 
    Error 403 if it does not match."""
    token = request.form.get("csrf_token")
    if not token:
        abort(403)
    if token != session.get("csrf_token"):
        abort(403)

@app.route("/logout")
def logout():
    """Logs the person out. 
    Clears session and redirects to login page."""
    session.clear()
    return redirect("/login")

@app.route("/personal_diary")
def diary():
    """Shows's the person's running diary,
    including entries, supporters and statistics from runs."""
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    entries = get_entries(user_id)

    record_run = get_max_distance(user_id)
    competition_count = get_competition_count(user_id)
    support_count = get_support_count(user_id)

    return render_template(
        "personal_diary.html",
        entries=entries,
        username=session["username"],
        record_run=record_run,
        competition_count=competition_count,
        support_count=support_count
    )

@app.route("/new_run", methods=["GET", "POST"])
def add_entry_route():
    """Allows user to create new entries to running diary.
    GET shows form to add information regarding the run
    POST validates user input and saves it to database."""
    if "user_id" not in session:
        return redirect("/login")
    terrains = get_terrains()
    run_types = get_run_types()
    if request.method == "POST":
        check_csrf()
        km_str = request.form.get("km", "").strip()
        m_str = request.form.get("m", "").strip()
        runtime = request.form.get("runtime", "").strip()
        terrain_id = request.form.get("terrain_id")
        run_type_id = request.form.get("run_type_id")
        competition_id = request.form.get("competition_id", "").strip()
        other = request.form.get("other", "").strip()

        errors, km, m = validate_entry_form(
            km_str, m_str, runtime, terrain_id, run_type_id
        )

        if errors:
            return render_template(
                "add_entry.html",
                errors=errors,
                terrains=terrains,
                run_types=run_types,
                km=km,
                m=m,
                runtime=runtime,
                run_type=run_type_id,
                other=other,
                terrains_selected=[]
            )

        add_entry(
            session["user_id"], km, m,
            runtime, terrain_id, run_type_id,
            competition_id if competition_id else None, other
        )
        return redirect("/personal_diary")
    return render_template(
        "add_entry.html",
        terrains=terrains,
        run_types=run_types
    )

@app.route("/edit_entry/<int:entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
    """Allows user to edit entries in their running diary
    GET shows the form with existing information, allowing editing
    POST validates new user input and overwrites the earlier data with new input"""
    if "user_id" not in session:
        return redirect("/login")
    entry = get_entry(entry_id, session["user_id"])
    terrains = get_terrains()
    run_types = get_run_types()

    if entry is None:
        return "Muokattavaa merkintää ei löytynyt", 403
    
    if request.method == "POST":
        check_csrf()
        km_str = request.form.get("km", "").strip()
        m_str = request.form.get("m", "").strip()
        runtime = request.form.get("runtime", "").strip()
        terrain_id = request.form.get("terrain_id")
        run_type_id = request.form.get("run_type_id")
        competition_id = request.form.get("competition_id")
        other = request.form.get("other", "").strip()

        errors, km, m = validate_entry_form(
            km_str, m_str, runtime, terrain_id, run_type_id
        )

        if errors:
            return render_template(
                "edit_entry.html",
                errors=errors,
                entry=entry,
                terrains=terrains,
                run_types=run_types,
                km=km,
                m=m,
                runtime=runtime,
                run_type=run_type_id,
                other=other,
                terrains_selected=[]
            )

        update_entry(
            entry_id,
            session["user_id"],
            km,
            m,
            runtime,
            terrain_id,
            run_type_id,
            competition_id if competition_id else None,
            other
        )
        return redirect("/personal_diary")

    return render_template(
        "edit_entry.html",
        entry=entry,
        terrains=terrains,
        run_types=run_types
    )

@app.route("/delete_entry/<int:entry_id>", methods=["POST"])
def delete_entry_route(entry_id):
    """Allows user to delete existing entry from diary.
    Redirects back to diary after deletion."""
    if "user_id" not in session:
        return redirect("/login")
    check_csrf()

    delete_entry(entry_id, session["user_id"])

    return redirect("/personal_diary")

@app.route("/browseruns", methods=["GET"])
def browse_runs():
    """Allows users to search saved running entries based on search criteria"""
    km = request.args.get("km")
    terrain_id = request.args.getlist("terrain_id")
    run_type_id = request.args.get("run_type_id")
    username = request.args.get("username")

    runs = search_runs(
        km=km,
        terrain=terrain_id,
        run_type=run_type_id,
        username=username
    )

    return render_template(
        "browseruns.html",
        runs=runs,
        terrains=get_terrains(),
        run_types=get_run_types()
    )

@app.route("/competition")
def competitions():
    """Shows a listing of all competitions added to the site"""
    competition_list = get_competitions()
    return render_template(
        "competition.html",
        competitions=competition_list
    )

@app.route("/comp_page/<int:competition_id>", methods=["GET", "POST"])
def competition(competition_id):
    """Shows a page of individual competition.
    GET Shows the information of the competition, top runners and comments
    POST adds a comment to the competition page. Requires login."""
    if request.method == "POST":
        check_csrf()
        if "user_id" not in session:
            return redirect("/login")
        comment = request.form.get("comment", "").strip()
        if not comment:
            return redirect(
                url_for("competition", competition_id=competition_id))
        add_comments_competition(
            competition_id,
            session["user_id"],
            comment
        )
        return redirect(url_for("competition", competition_id=competition_id))

    competition_data = get_competition(competition_id)

    if competition_data is None:
        return "Kilpailua ei löytynyt", 404
    top_result = get_top_results(competition_id)

    comments = get_comments_competition(competition_id)
    return render_template(
        "comp_page.html",
        competition=competition_data,
        top_result=top_result,
        comments=comments
    )

@app.route("/kayttaja/<username>", methods=["GET", "POST"])
def user_page(username):
    """Shows user's public userpage, run etries and statistics.
    GET shows the profile information and checks if user has cheered/supported the profile
    POST let's the user cheer /support the runner with a button"""
    user = get_username(username)
    if not user:
        return "Käyttäjää ei löytynyt", 404
    user_id = user["id"]
    entries = get_entries(user_id)

    try:
        record_run = get_max_distance(user_id)
        competition_count = get_competition_count(user_id)
        support_count = get_support_count(user_id)

    except ValueError as e:
        return render_template(
            "error.html",
            error=str(e)
        )
    is_already_supported = False
    if "user_id" in session:
        is_already_supported = already_supported(session["user_id"], user["id"])

    if request.method == "POST":
        check_csrf()
        if "user_id" not in session:
            return redirect("/login")
        try:
            add_support(session["user_id"], user["id"])
        except sqlite3.IntegrityError:
            pass
        return redirect(url_for("user_page", username=username))

    return render_template(
        "user_page.html",
        profile_user=user,
        entries=entries,
        record_run=record_run,
        competition_count=competition_count,
        support_count=support_count,
        is_already_supported=is_already_supported
    )

if __name__ == "__main__":
    app.run()
