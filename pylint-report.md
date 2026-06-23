# Pylint-raportti

Tässä on jätetty tarkoituksella pois seed.py, sillä tätä käytetään vain tehokkuuden testauksessa.

Pylint antaa seuraavan raportin sovelluksesta:

```
************* Module app
app.py:100:15: W0718: Catching too general exception Exception (broad-exception-caught)
************* Module queries
queries.py:47:0: R0913: Too many arguments (8/5) (too-many-arguments)
queries.py:47:0: R0917: Too many positional arguments (8/5) (too-many-positional-arguments)
queries.py:219:0: R0913: Too many arguments (9/5) (too-many-arguments)
queries.py:219:0: R0917: Too many positional arguments (9/5) (too-many-positional-arguments)
queries.py:272:0: R0913: Too many arguments (7/5) (too-many-arguments)
queries.py:272:0: R0917: Too many positional arguments (7/5) (too-many-positional-arguments)
queries.py:272:0: R0914: Too many local variables (27/15) (too-many-locals)
queries.py:338:8: R1730: Consider using 'page = min(page, page_count)' instead of unnecessary if block (consider-using-min-builtin)

------------------------------------------------------------------
Your code has been rated at 9.78/10
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



```python
def update_entry(entry_id, user_id, km, m,
                 runtime, terrain_id, run_type_id,
                 competition_name, other):
```
sekä
```python
def search_runs_paginated(km=None, terrain=None, run_type=None,
                          username=None, competition_name=None,
                          page=1, page_size=20):
```
add_entry ja update_entry ovat “rajakoodia” Flaskin ja SQL-tason välissä ja niiden parametrit vastaavat suoraan entries-taulun sarakkeita.
Tässä kohdassa selkein ratkaisu on, että kaikki kentät annetaan eksplisiittisinä parametreina. <br>
Jos funktio paketoitaisiin esim. dict-objektiin tai dataluokkaan, se monimutkaistaisi koodia ilman selvää hyötyä.
Search_runs_paginated tukee useita hakuehtoja ja sivutusta. Kaikki parametrit ovat oleellisia.


Käytössä on **nimetyt argumentit**, kuten add_entry kohdassa:
```python
add_entry(
    session["user_id"], km, m,
    runtime, terrain_id, run_type_id,
    competition_name, other
)
```

Nimetyillä argumenteilla vältytään siltä, että parametrit olisivat vaikeasti ymmärrettäviä.

---

## Liikaa paikallisia muuttujia


```
queries.py:272:0: R0914: Too many local variables (27/15) (too-many-locals)
```
Pylint viittaa tällä search_runs_paginated funktioon, jolla on useita paikallisia muuttujia. Tämä ei muuteta, sillä tämä funktio muodostaa dynaamisen SQL-hakukyselyn, joka sisältää esimerkiksi hakuehtojen rakentamisen, parametrien validoinnin ja tulosten haun.

Paikallisten muuttujien suuri määrä johtuu siitä, että SQL-kysely on jaettu loogisiin vaiheisiin (luettavuuden parantamiseksi) ja jokainen vaihe tarvitsee oman välituloksen.
Tarkoitus on välttää monimutkaista “yhden rivin SQL-rakennetta”

Vaikka muuttujia on paljon, ne tekevät koodista ylläpidettävämmän ja selkeämmän.


---

## Ehdotus sivutuksesta

```
queries.py:338:8: R1730: Consider using 'page = min(page, page_count)'
```
Pylint ehdottaa ehdottaa min()-funktion käyttöä, mutta nykyinen muoto on tarkoituksellisesti valittu, koska se tekee ehdosta eksplisiittisen ja helpommin ymmärrettävän aloittelijalle(minulle).
if-rakenne on johdonmukainen muun validointilogiikan kanssa (esim. muut if-checkit samassa funktiossa).
Koodin tarkoitus on olla helposti luettavaa, jonka priorisoin tässä lyhyyden yli.

