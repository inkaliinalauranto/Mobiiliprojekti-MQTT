# Team 1 CoolBox mobiiliprojekti MQTT
Repon kopiointi:
- Clone with HTTPS
- PyCharmissa create from VCS

Virtuaaliympäristön luonti:
- python -m venv venv

Riippuvuuksien asennus:
- python -m pip install -r requirements.txt

Virtuaaliympäristön aktivointi:
- venv\Scripts\activate

Ympäristömuuttujat:

- luo .env-tiedosto
- kopioi sinne seuraavat muuttujat:

TOPIC=anna/topic/jonka/rakenne/nayttaa/talta

UN=kayttajatunnus

PW=salasanajossamyoserikoismerkki

HOST=URImuotoa.oleva.osoite

- vaihda muuttujien placeholder-arvot MQTT-videossa suoraan main.py-tiedostoon merkattuihin arvoihin ilman lainausmerkkejä
- jos epäselvyyksiä, Inka-Liina kertoo arvot