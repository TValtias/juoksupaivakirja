# Pylint-raportti
Pylint antaa seuraavan raportin sovelluksesta:

```
************* Module app
app.py:86:15: W0718: Catching too general exception Exception (broad-exception-caught)
************* Module queries
queries.py:47:0: R0913: Too many arguments (8/5) (too-many-arguments)
queries.py:47:0: R0917: Too many positional arguments (8/5) (too-many-positional-arguments)
queries.py:219:0: R0913: Too many arguments (9/5) (too-many-arguments)
queries.py:219:0: R0917: Too many positional arguments (9/5) (too-many-positional-arguments)

------------------------------------------------------------------
Your code has been rated at 9.87/10 (previous run: 9.87/10, +0.00)
```
Alla käyn läpi syyt, miksi näitä kohtia ei ole korjattu sovelluksessa.

---

## Liian yleinen poikkeuksen käsittely

Raportin ilmoitus:
```
app.py:86:15: W0718: Catching too general exception Exception (broad-exception-caught)
```

Huomauttaa, että rekisteröinnissä käytettävä Exception on liian yleinen. 

```python
try:
    create_user(username, hashing_pass)
except sqlite3.IntegrityError:
    return render_template(
        "register.html",
        errors=["Joku toinen ehti ensin. Valitse toinen käyttäjänimi"],
    )
except Exception as e:
    return render_template(
        "register.html",
        errors=[f"Virhe rekisteröinnissä: {e}"],
    )
```
 
Tässä tapauksessa se on kuitenkin tarkoituksellinen ja rajattu ratkaisu: <br>
create_user voi epäonnistua monesta eri syystä, eikä yksittäinen rekisteröintivirhe saa kaataa koko Flask-sovellusta. <br>
Kaikki virheet ohjataan samaan virhenäkymään, ja (tuotantokäytössä) ne tulisi lisäksi lokittaa tarkempaa diagnostiikkaa varten.

---

## Liikaa argumentteja funktioissa

Raportissa ilmenee seuraava:
```
queries.py:47:0: R0913: Too many arguments (8/5) (too-many-arguments)
queries.py:47:0: R0917: Too many positional arguments (8/5) (too-many-positional-arguments)
queries.py:219:0: R0913: Too many arguments (9/5) (too-many-arguments)
queries.py:219:0: R0917: Too many positional arguments (9/5) (too-many-positional-arguments))
```

Näillä viitataan esimerkiksi seuraaviin funktioihin: 

```python
def add_entry(user_id, km, m, runtime,
              terrain_id, run_type_id,
              competition_name, other):
```

sekä

```python
def update_entry(entry_id, user_id, km, m,
                 runtime, terrain_id, run_type_id,
                 competition_name, other):
```

add_entry ja update_entry ovat “rajakoodia” Flaskin ja SQL-tason välissä ja niiden parametrit vastaavat suoraan entries-taulun sarakkeita.
Tässä kohdassa selkein ratkaisu on, että kaikki kentät annetaan eksplisiittisinä parametreina. <br>
Jos funktio paketoitaisiin esim. dict-objektiin tai dataluokkaan, se monimutkaistaisi koodia ilman selvää hyötyä.


Käytössä on **nimetyt argumentit**, kuten add_entry kohdassa:
```python
add_entry(
    session["user_id"], km, m,
    runtime, terrain_id, run_type_id,
    competition_name, other
)
```

Nimetyillä argumenteilla vältytään siltä, että parametrit olisivat vaikeasti ymmärrettäviä.


