from datetime import datetime
import certifi
import paho.mqtt.client as mqtt
import json
from dotenv import load_dotenv
import os
import var_dump as vd

# TIETORAKENTEEN HAKU METADATASTA #############################################
sensor_list = []

with open('coolbox_metadata.json', 'r', encoding='UTF-8') as config_file:
    '''Muuetaan coolbox_metadatan sisältö dictionaryksi ja luetaan 
    dictionary metadata-muuttujaan:'''
    metadata = json.loads(config_file.read())
    devices = metadata['devices']
    '''Python-dictionarylla on keys-niminen funktio, jolla saadaan 
    kaikki dictionaryn avaimet'''
    device_ids = devices.keys()
    for device_id in device_ids:
        # # Tarkistetaan, onko avain sellainen, jota ei voi kääntää numeroksi:
        # # Ei kuitenkaan käytetä toimintoa, koska esimerkiksi aurinkopaneelin
        # # laite-id on merkkijono
        # if not device_id.isnumeric():
        #     continue
        # Get on turvallisempi käyttää kuin devices[device_id], koska se ei kaadu, jos device_id on esim. null
        device = devices.get(device_id)
        # Laitteen nimi on sd-avaimen arvo:
        device_name = device['sd']
        sensors = device['sensors']
        if sensors == {}:
            continue
        sensor_ids = sensors.keys()
        # Esim. palovaroittimessa on kolme sensoria
        for sensor_id in sensor_ids:
            sensor_info = sensors.get(sensor_id)
            # Jos sensorista puuttuu yksikkö, hypätään sen yli
            if "unit" not in sensor_info:
                continue
            sensor_list.append({
                "device_id": device_id,
                "device_name": device_name,
                "sensor_id": sensor_id,
                "sensor_description": sensor_info["sd"],
                "unit": sensor_info["unit"]
            })

# print(vd.var_dump(sensor_list))
# print("\n", "ALKIOITA:", len(sensor_list))
###############################################################################


# MQTT-VIESTIN KÄSITTELY ######################################################

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
        device_id_msg = tuple(payload['d'].keys())[0]
        # Haetaan tietosisällöstä tiedot laitteen sensoreista:
        sensor_data = payload['d'][device_id_msg]
        # Haetaan laitteen sensoreiden nimet/tunnisteet:
        sensor_ids_msg = list(tuple(sensor_data.keys()))
        '''Koska laitteissa voi olla useampia sensoreita, haetaan laitteen 
         sensoreiden arvot silmukassa. Lisätään samalla kunkin 
         sensorin tiedot tietokantaan.'''
        for sensor_id_msg in sensor_ids_msg:
            sensor_value = sensor_data[sensor_id_msg]['v']
            # print(f"LAITE_ID: {device_id_msg} | SENSORI_ID: {sensor_id_msg} | ARVO: {sensor_value} | MITTAUSHETKI: {year}/{month}/{week}/{day}/{hour}/{min}/{sec}/{ms}")
            for sensor_metadata in sensor_list:
                if sensor_metadata["sensor_id"] == sensor_id_msg and sensor_metadata["device_id"] == device_id_msg:
                    print("sensors_dim-tauluun lisättävät tiedot saapuneesta viestistä:")
                    print("sensor_key: tietokanta hoitaa")
                    print(f"sensor_id: {sensor_id_msg}")
                    print(f"sensor_name: {sensor_metadata['sensor_description']}")
                    print(f"device_id: {device_id_msg}")
                    print(f"device_name: {sensor_metadata['device_name']}")
                    print(f"unit: {sensor_metadata['unit']}")
                    print()
                    print("measurements_fact-tauluun lisättävä tieto saapuneesta viestistä:")
                    print(f"value: {sensor_value}")
                    print("\n" + "-----------------------------------------------------------------" + "\n")
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
###############################################################################
