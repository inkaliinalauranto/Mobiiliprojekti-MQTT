import json
from sqlalchemy import text
from dw import get_dw
import var_dump as vd


# SENSOREIDEN KUVAUKSIEN HAKU METADATASTA #####################################
def clear_tables(_dw):
    _clear_measurements_fact_query = text("DELETE FROM measurements_fact;")
    _dw.execute(_clear_measurements_fact_query)
    _clear_sensors_dim_query = text("DELETE FROM sensors_dim;")
    _dw.execute(_clear_sensors_dim_query)
    _clear_dates_dim_query = text("DELETE FROM dates_dim;")
    _dw.execute(_clear_dates_dim_query)
    _dw.commit()


def insert_sensor_metadata():
    '''Alustetaan lista, johon myöhemmin tallennetaan yksittäisen sensorin
    datarakenne yksittäiseksi dictionary-alkioksi.'''
    sensor_list = []
    with open('coolbox_metadata.json', 'r', encoding='UTF-8') as config_file:
        try:
            '''Muutetaan coolbox_metadatan sisältö dictionaryksi ja luetaan 
            dictionary metadata-muuttujaan:'''
            metadata = json.loads(config_file.read())
            with get_dw() as _dw:
                try:
                    # '''Poistetaan sensors_dim-taulussa jo olevat tietueet
                    # edeltävästi, jottei niitä tule tauluun kaksin kappalein.
                    # Viite-eheyden vuoksi on tätä ennen poistettava myös
                    # tietueet measurements_fact-taulusta, koska jokaiseen
                    # measurements_fact-taulun tietueeseen on viite jostakin
                    # sensors_dim-taulun tietueesta. Poistetaan myös tietueet
                    # dates_dimistä, koska taulussa olevia päivämääriä ei enää
                    # tarvita, kun niihin liittyvät sensoriarvot on poistettu.'''
                    # clear_tables(_dw)
                    _check_query = text("SELECT COUNT(*) FROM sensors_dim;")
                    result = _dw.execute(_check_query).fetchone()
                    _dw.commit()
                    row_count = result[0]
                    print(f"Tietueita taulussa: {row_count}")
                    if row_count <= 0:
                        devices = metadata['devices']
                        '''Python-dictionarylla on keys-niminen funktio, jolla saadaan 
                        haettua dictionaryn jokainen avain.'''
                        device_ids = devices.keys()
                        for device_id in device_ids:
                            # ''' Tarkistetaan, onko avain sellainen, jota ei voi
                            # kääntää numeroksi. Jos on, hypätään sen yli.
                            # [Ei kuitenkaan käytetä toimintoa, koska esimerkiksi
                            # aurinkopaneelin laite-id on merkkijono.] '''
                            # if not device_id.isnumeric():
                            #     continue
                            ''' Get-metodia on turvallisempi käyttää kuin arvon 
                            hakemista avaimella (devices[device_id]), koska 
                            get-metodilla ohjelma ei kaadu, jos device_id olisi 
                            esim. null'''
                            device = devices.get(device_id)
                            device_name = device['sd']
                            sensors = device['sensors']
                            if sensors == {}:
                                continue
                            sensor_ids = sensors.keys()
                            for sensor_id in sensor_ids:
                                sensor_info = sensors.get(sensor_id)
                                ''' Jos sensorista puuttuu yksikköavain, 
                                hypätään sen yli.'''
                                if "unit" not in sensor_info:
                                    continue
                                sensor_list.append({
                                    "device_id": device_id,
                                    "device_name": device_name,
                                    "sensor_id": sensor_id,
                                    "sensor_description": sensor_info["sd"],
                                    "unit": sensor_info["unit"]
                                })
                                _sensors_dim_query = text('INSERT INTO sensors_dim (sensor_id, sensor_name, device_id, '
                                                          'device_name, unit) VALUES (:sensor_id, :sensor_name, '
                                                          ':device_id, :device_name, :unit)')
                                _dw.execute(_sensors_dim_query, {'sensor_id': sensor_id,
                                                                 'sensor_name': sensor_info['sd'],
                                                                 'device_id': device_id,
                                                                 'device_name': device_name,
                                                                 'unit': sensor_info['unit']})
                        _dw.commit()
                except Exception as e:
                    print(e)
                    _dw.rollback()
                    raise e
        except Exception as e:
            print(e)
    # print(vd.var_dump(sensor_list))
    # print("\n", "ALKIOITA:", len(sensor_list))

