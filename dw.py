import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+mysqlconnector://root:@localhost/tietokannan_nimi')
dw_session = sessionmaker(bind=engine)


def get_connection():
    conn = dw_session()
    return conn


@contextlib.contextmanager
def get_dw():
    conn = None
    try:
        conn = dw_session()
        yield conn
    finally:
        if conn is not None:
            conn.close()

