import contextlib
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Kerrotaan tiedosto, josta salainen ympäristömuuttuja haetaan:
load_dotenv(dotenv_path=".env")

# Haetaan ympäristömuuttuja, johon tietokannan URI on tallennettu:
dw_uri = os.environ.get("DW")

engine = create_engine(dw_uri)
dw_session = sessionmaker(bind=engine)


@contextlib.contextmanager
def get_dw():
    conn = None
    try:
        conn = dw_session()
        yield conn
    finally:
        if conn is not None:
            conn.close()

