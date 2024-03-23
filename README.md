# Team 1 CoolBox mobiiliprojekti MQTT
## Tietokanta
- Tämä MQTT-softa toimii seuraavaa fyysistä mallia noudattavan tietokannan kanssa:

![img.png](img.png)

## Repon kopiointi:
- Clone with HTTPS
- PyCharmissa create from VCS

## Virtuaaliympäristön luonti:
- python -m venv venv

## Riippuvuuksien asennus:
- python -m pip install -r requirements.txt

## Virtuaaliympäristön aktivointi:
- venv\Scripts\activate

## Ympäristömuuttujat:

- Luo .env-tiedosto
- Kopioi sinne seuraavat muuttujat:

TOPIC=anna/topic/jonka/rakenne/nayttaa/talta

UN=kayttajatunnus

PW=salasanajossamyoserikoismerkki

HOST=URImuotoa.oleva.osoite

DW=driver://kayttaja:salasana@localhost/tietokannan_nimi

- Vaihda neljän ensimmäisen muuttujan placeholder-arvot MQTT-videossa suoraan main.py-tiedostoon merkattuihin arvoihin ilman lainausmerkkejä
- Vaihda viimeisen muuttujan placeholder-arvot vastaamaan paikalliselle palvelimelle tekemäsi tietokannan tietoja
- Jos epäselvyyksiä, Inka-Liina kertoo arvot
