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

'''Jos autorisointiongelmia ilmenee, tarkistetaan että ympäristömuuttujista 
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
        # Muunnetaan sekuntimuotoinen epoch päivämääräksi.
        dt = datetime.fromtimestamp(ts_in_sec)

        # Irroitetaan päivämäärän eri osat pistenotaation avulla:
        year = dt.year
        month = dt.month
        week = dt.isocalendar().week
        day = dt.day
        hour = dt.hour
        min = dt.minute
        sec = dt.second
        ms = dt.microsecond

        '''Haetaan tietosisällöstä laitteen nimi/id hakemalla 
        viesti-dictionaryn d-avaimen arvona olevan dictionaryn avaimen 
        nimi. Koska keys-funktio palauttaa haetun arvon objektin sisällä 
        olevaan listaan, muutetaan tulos tupleksi ja haetaan avaimen nimi 
        tuplen ainoasta eli ensimmäisestä alkiosta.'''
        device = tuple(payload['d'].keys())[0]
        # Haetaan tietosisällöstä tiedot laitteen sensoreista:
        sensor_data = payload['d'][device]
        # Haetaan laitteen sensoreiden nimet/tunnisteet:
        sensor_names = list(tuple(sensor_data.keys()))
        print(f"Uusi viesti:")
        '''Koska laitteissa voi olla useampia sensoreita, haetaan laitteen 
         sensoreiden arvot silmukassa. Lisätään samalla kunkin 
         sensorin tiedot tietokantaan.'''
        for sensor_name in sensor_names:
            sensor_value = sensor_data[sensor_name]['v']
            print(f"LAITE: {device} | SENSORI: {sensor_name} | ARVO: {sensor_value} | MITTAUSHETKI: {year}/{month}/{week}/{day}/{hour}/{min}/{sec}/{ms}")
            ###################################################################
            ''' Tähän sensor- ja -value-muuttujien arvojen sekä dt-muuttujan 
            osa-arvojen lisäys tietokantaan'''
            ###################################################################             
        # ''' Haetaan sensor-muuttujaan laitteessa olevan sensorin nimi/tunniste 
        # Juhanin tavalla, joka hakee ainoastaan laitteen ensimmäisen sensorin 
        # arvoineen'''
        # sensorJ = tuple(sensor_data.keys())[0]
        # # Haetaan laitteessa olevan sensorin arvo:
        # valueJ = sensor_data[sensorJ]['v']
        # print(f"Sensori: {sensorJ} | arvo: {valueJ} | mittaushetki: {dt}")
        # #######################################################################
        # ''' Tähän sensor- ja -value-muuttujien arvojen sekä dt-muuttujan 
        # osa-arvojen lisäys tietokantaan'''
        # ####################################################################### 
        print()       
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