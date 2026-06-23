# juoksupaivakirja

## Sovelluksen ominaisuudet

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään sovellukseen juoksulenkkinsä tiedot päiväkirja-muodossa kirjauduttuaan sisään sivulla päiväkirja.
- Käyttäjä pystyy muokkaamaan ja poistamaan lisäämiään lenkkien tietoja päiväkirja-sivulla.
- Käyttäjä näkee sovellukseen lisätyt päiväkirjamerkinnöt Selaa -sivulla. Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät juoksulenkit ja pystyy hakemaan juoksulenkkejä eri filttereillä.
- Käyttäjä voi mennä katsomaan muiden käyttäjien päiväkirjoja ja kannustaa muita jäseniä (myös itsensä kannustus sallittu!).
- Käyttäjä voi katsoa omia ja muiden tilastoja pisimmästä juoksusta, kisojen määrästä ja kannustuksista joita on saanut muilta.
- Käyttäjä pystyy valitsemaan juoksulenkille yhden tai useamman luokittelun (kevyt lenkki, tavoitteellinen juoksu, kilpailuun tähtäävä, kisat) sekä eri maastot. Mahdolliset luokat ovat tietokannassa.
- Käyttäjä pystyy katsoa kisasivuja ja käydä keskustelua muiden kanssa niistä kommenttialueella. Käyttäjä pystyy katsomaan tilastoja TOP 10 parhaista kisa-ajoista.

---

## Asennusohjeet

### Vaatimukset

- python 3.10 +
- pip

###  1.) Lataa repo:
```bash
     git clone <repo_url>
     cd juoksupaivakirja
```

 ### 2.)Aktivoidaan virtuaaliympäristö:
 ```bash
    python3 -m venv venv
    source venv/bin/activate
```

 ### 3.)Aktivoidaan tarvittavat riippuvuudet:
  ```bash  
    pip install -r requirements.txt
```

 ### 4.)Luo tietokanta:
 ```bash
    sqlite3 database.db < schema.sql
    sqlite3 database.db < seed_kisat.sql
```

 ### 5.)Käynnistä:
 ```bash
    flask run
```

  **HUOM!** Päiväkirjan käyttö (merkintöjen luonti, muokkaus, poisto) vaatii rekisteröinnin. Etusivu, kisat ja selaa toimivat ilman.

---

## Suuren datamäärän testiraportti
Luotu seed.py, joka luo 
- 100 000 käyttäjää
- 1 000 000 päiväkirjamerkintää
- 500 Uutta kilpailua.


Sivutus on tehty sivulle browseruns, jonka kautta haetaan eri käyttäjien tekemiä päiväkirjamerkintöjä. 
Jokainen haku tuottaa 20 tulosta, joita voi selata painikkeilla "Seuraava" ja "Edellinen".

Jo luomisvaiheessa tehty päätös rajoittaa jokaisen kilpailun kommenttikenttä 15 viimeisimpään viestiin sai minut muuttamaan testauksen viesteistä kilpailujen määrään.

Jätän pois kuvien lataamiseen kuluneen ajan, ellei se ole dramaattisesti pidempi.
```
elapsed time: 0.01 s
127.0.0.1 - - [23/Jun/2026 17:12:00] "GET / HTTP/1.1" 200 -
elapsed time: 0.01 s
127.0.0.1 - - [23/Jun/2026 17:13:43] "GET /register HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [23/Jun/2026 17:14:20] "GET /login HTTP/1.1" 200 -
elapsed time: 0.01 s
127.0.0.1 - - [23/Jun/2026 17:14:44] "GET /personal_diary HTTP/1.1" 200 -
elapsed time: 2.13 s
127.0.0.1 - - [23/Jun/2026 17:15:29] "GET /browseruns HTTP/1.1" 200 -
elapsed time: 1.7 s
127.0.0.1 - - [23/Jun/2026 17:16:18] "GET /browseruns?username=alias&km=&competition_name= HTTP/1.1" 200 -
elapsed time: 0.02 s
127.0.0.1 - - [23/Jun/2026 17:16:39] "GET /competition HTTP/1.1" 200 -
elapsed time: 0.02 s
127.0.0.1 - - [23/Jun/2026 17:17:15] "GET /kayttaja/user82305 HTTP/1.1" 200 -
```
Näin suurella tietomäärällä testatessa haku hidastuu, mutta ei ole mahdoton käyttää. 


Lisäsin indeksejä, jolloin tulokset ovat seuraavanlaisia:
```
elapsed time: 0.01 s
127.0.0.1 - - [23/Jun/2026 17:41:27] "GET / HTTP/1.1" 200 -
elapsed time: 0.01 s
127.0.0.1 - - [23/Jun/2026 17:42:14] "GET /register HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [23/Jun/2026 17:42:33] "GET /login HTTP/1.1" 200 -
elapsed time: 0.01 s
127.0.0.1 - - [23/Jun/2026 17:42:43] "GET /personal_diary HTTP/1.1" 200 -
elapsed time: 1.21 s
127.0.0.1 - - [23/Jun/2026 17:43:54] "GET /browseruns HTTP/1.1" 200 -
elapsed time: 0.95 s
127.0.0.1 - - [23/Jun/2026 17:44:43] "GET /browseruns?username=user1000&km=&competition_name= HTTP/1.1" 200 -
elapsed time: 0.02 s
127.0.0.1 - - [23/Jun/2026 17:45:14] "GET /competition HTTP/1.1" 200 -
elapsed time: 0.01 s
127.0.0.1 - - [23/Jun/2026 17:45:36] "GET /kayttaja/user10001 HTTP/1.1" 200 -
```
Kuten tuloksista nähdään, indeksien käyttö nopeutti käyttöä melkein puolittamalla ajan, mutta tulos ei siltikään ole täysin ideaali.

---
