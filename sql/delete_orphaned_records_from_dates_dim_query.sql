-- Kysely orpojen tietueiden poistamiseen dates_dim-taulusta.
-- Kopioi alla oleva ja suorita se cooldev_olap-tietokannassa.

DELETE FROM dates_dim WHERE date_key NOT IN
    (SELECT date_key FROM
         (SELECT date_key FROM heating_consumptions_fact
          UNION
          SELECT date_key FROM lighting_consumptions_fact
          UNION
          SELECT date_key FROM measurements_fact
          UNION
          SELECT date_key FROM outlets_consumptions_fact
          UNION
          SELECT date_key FROM productions_fact
          UNION
          SELECT date_key FROM temperatures_fact
          UNION
          SELECT date_key FROM total_consumptions_fact)
    AS all_dates);