from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "Tähän tulee juoksupäiväkirja"

@app.route("/login")
def login():
    return "Kirjautuminen tulossa pian!"

@app.route("/paivakirja")
def diary():
    return "Päiväkirja tulossa pian!"

@app.route("/kisat")
def competitions():
    return "Kisat tulossa pian!"

@app.route("/kayttaja/<int:page_id>")
def user_page(page_id):
    return "Käyttäjien sivut tulossa pian!"