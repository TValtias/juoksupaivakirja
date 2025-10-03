# juoksupaivakirja

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään sovellukseen juoksulenkkinsä tiedot päiväkirja-muodossa kirjauduttuaan sisään sivulla päiväkirja.
- Käyttäjä pystyy muokkaamaan ja poistamaan lisäämiään lenkkien tietoja päiväkirja-sivulla.
- Käyttäjä näkee sovellukseen lisätyt päiväkirjamerkinnöt Selaa -sivulla. Käyttäjä näkee sekä itse lisäämänsä että muiden käyttäjien lisäämät juoksulenkit ja pystyy hakemaan juoksulenkkejä eri filttereillä.
- Käyttäjä voi mennä katsomaan muiden käyttäjien päiväkirjoja ja kannustaa muita jäseniä.
- Käyttäjä voi katsoa omia ja muiden tilastoja pisimmästä juoksusta, kisojen määrästä ja kannustuksista joita on saanut muilta.
- Käyttäjä pystyy valitsemaan juoksulenkille yhden tai useamman luokittelun (kevyt lenkki, tavoitteellinen juoksu, kilpailuun tähtäävä, kisat) sekä eri maastot. Mahdolliset luokat ovat tietokannassa.
- Käyttäjä pystyy katsoa kisasivuja ja kommentoida niille. Käyttäjä pystyy katsomaan tilastoja TOP 10 parhaista kisa-ajoista.


OHJEET SOVELLUKSEN KOKEILUUN MAC,(Linux / Windows käyttäjillä saattaa olla hieman eri komennot):

Varmista, että sinulla on:
- python 3.10 +
- pip

  1.) Lataa repo:
     git clone <repo_url>
     cd juoksupaivakirja

  2.)Aktivoidaan virtuaaliympäristö:
    python3 -m venv venv
    source venv/bin/activate

  3.)Aktivoidaan tarvittavat riippuvuudet:
    pip install -r requirements.txt

  4.)Luo tietokanta:
    sqlite3 database.db < schema.sql
    sqlite3 database.db < seed_kisat.sql

  5.)Käynnistä:
    python3 app.py / flask run

  HUOM! Päiväkirjan käyttö (merkintöjen luonti, muokkaus, poisto) vaatii rekisteröinnin. Etusivu ja selaa toimivat ilman.
