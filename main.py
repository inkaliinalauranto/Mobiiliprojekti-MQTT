from datetime import datetime
import certifi
import paho.mqtt.client as mqtt
import json
from dotenv import load_dotenv
import os
from sqlalchemy import text
from dw import get_dw
from insert_sensor_metadata import insert_sensor_metadata

''' Ennen MQTT Brokerista vastaanotettavien viestien käsittelemistä ja 
lisäämistä lisätään tietueet sensors_dim-tauluun.'''
insert_sensor_metadata()

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


def _get_dates_dim(_dw):
    _query = text("SELECT * FROM dates_dim;")
    rows = _dw.execute(_query).mappings().all()
    return rows


def _get_sensors_dim(_dw):
    _query = text("SELECT sensor_id, device_id, sensor_key FROM sensors_dim;")
    rows = _dw.execute(_query).mappings().all()
    return rows


def _get_date_key(msg_dt, dates):
    for d_dim in dates:
        if msg_dt.year == d_dim["year"] and msg_dt.month == d_dim["month"] and msg_dt.isocalendar().week == d_dim[
            "week"] and msg_dt.day == d_dim["day"] and msg_dt.hour == d_dim["hour"] and msg_dt.minute == d_dim[
            "min"] and msg_dt.second == d_dim["sec"] and msg_dt.microsecond == d_dim["ms"]:
            return d_dim["date_key"]
    return None


def _get_sensor_key(msg_sensor_id, msg_device_id, sensors_from_dw):
    for sensor in sensors_from_dw:
        if msg_sensor_id == sensor["sensor_id"] and msg_device_id == sensor["device_id"]:
            return sensor["sensor_key"]
    return None


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        with get_dw() as _dw:
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
                _dates_dim_query = text('INSERT INTO dates_dim (year, month, week, day, hour, min, sec, ms) VALUES ('
                                        ':year, :month, :week, :day, :hour, :min, :sec, :ms)')
                # Irroitetaan päivämäärän eri osat pistenotaation avulla:
                _dw.execute(_dates_dim_query,
                            {'year': dt.year, 'month': dt.month, 'week': dt.isocalendar().week, 'day': dt.day,
                             'hour': dt.hour, 'min': dt.minute, 'sec': dt.second, 'ms': dt.microsecond})
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
                    # print(f"LAITE_ID: {device_id_msg} | SENSORI_ID: {sensor_id_msg} | ARVO: {sensor_value} | "
                    #       f"MITTAUSHETKI: dt")
                    dates_dim = _get_dates_dim(_dw)
                    sensors_dim = _get_sensors_dim(_dw)
                    _date_key = _get_date_key(dt, dates_dim)
                    _sensor_key = _get_sensor_key(sensor_id_msg, device_id_msg, sensors_dim)

                    if _date_key is None or _sensor_key is None:
                        continue

                    _measurement_fact_query = text("INSERT INTO measurements_fact (sensor_key, date_key, value) "
                                                   "VALUES (:sensor_key, :date_key, :value)")
                    _dw.execute(_measurement_fact_query,
                                {"sensor_key": _sensor_key, "date_key": _date_key, "value": sensor_value})
                _dw.commit()

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
            except Exception as e1:
                print(e1)
                _dw.rollback()
                raise e1
    except Exception as e2:
        print(e2)


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
