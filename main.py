from datetime import datetime
import certifi
import paho.mqtt.client as mqtt
import json
from dotenv import load_dotenv
import os


# Kerrotaan tiedosto, josta salaiset ympäristömuuttujat haetaan: 
load_dotenv(dotenv_path=".env")

# Haetaan jokainen ympäristömuuttuja omaan muuttujaansa:
topic = os.environ.get("TOPIC")
username = os.environ.get("UN")
password = os.environ.get("PW")
host = os.environ.get("HOST")

'''Jos autorisointiongelmia ilmenee, tarkistetaan että ympäristömuuttujiin 
on haettu oikeat arvot:'''
print(topic)
print(username)
print(password)
print(host + "\n")


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # Topic, johon julkaisut tulevat:
    client.subscribe(topic)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        # Muutetaan yksittäisen viestin tietosisältö dictionary-muotoon
        payload = json.loads(msg.payload)
        '''Muutetaan aikaleima/epoch luettavaan päivämäärämuotoon. Koska 
         muunnoksessa käytetään datetimen fromtimestamp-funktiota, on 
         aikaleima muutettava ensin millisekunneista sekunneiksi. Koska 
         tietokannassa on sarake myös mikrosekunneille, ei pyöristetä 
         yksikkömuunnoksen osamäärää (ei käytetä Python integer 
         divisionia).  '''
        ts_in_sec = payload['ts'] / 1000
        '''Muunnetaan sekuntimuotoinen epoch päivämääräksi. Päivämäärän 
         eri osat saadaan dt-muuttujaan tallennetusta päivämäärästä irti 
         pistenotaation avulla (dt.year, dt.isocalendar().week).'''
        dt = datetime.fromtimestamp(ts_in_sec)
        '''Haetaan tietosisällöstä laitteen nimi/id hakemalla 
        viesti-dictionaryn d-avaimen arvona olevan dictionaryn avaimen 
        nimi. Koska keys-funktio palauttaa haetun arvon objektin sisällä 
        olevaan listaan, muutetaan tulos tupleksi ja haetaan avaimen nimi 
        tuplen ainoasta eli ensimmäisestä alkiosta.'''
        device = tuple(payload['d'].keys())[0]
        # Haetaan tietosisällöstä tiedot laitteen sensoreista:
        sensor_data = payload['d'][device]
        # Haetaan sensor-muuttujaan laitteessa olevan sensorin nimi/tunniste
        sensor = tuple(sensor_data.keys())[0]
        '''Koska laitteissa voi olla useampia sensoreita, pitäisi laitteen 
         sensoreiden nimet/tunnisteet hakea silmukassa, jossa myös parsitut 
         tiedot tallennettaisiin tietokantaan alla kommentoidulla tavalla. '''
        # sensors = list(tuple(sensor_data.keys()))
        # for sensor in sensors:
        #     value = sensor['v']
        #     # INSERT --> sensor, value ja dt pilkottuna
        value = sensor_data[sensor]['v']
        print(f"Sensori: {sensor} | arvo: {value} | mittaushetki: {dt}")

        #######################################################################
        ''' Tähän sensor- ja -value-muuttujien arvojen sekä dt-muuttujan 
        osa-arvojen lisäys tietokantaan'''
        #######################################################################        
    except Exception as e:
        print(e)


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

# Käyttäjänimi ja salasana:
mqttc.username_pw_set(username, password)
'''Koska käytetään suojattua yhteyttä (portti 8883), on kutsuttava 
tls_set-funktiota, jonka parametriksi on asetettava certifi-kirjaston 
where-funktiokutsu.'''
mqttc.tls_set(certifi.where())
# Määritellään viesteille host, portti ja ping-aika:
mqttc.connect(host, 8883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqttc.loop_forever()