import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+mysqlconnector://root:@localhost/tietokannan_nimi')
db_session = sessionmaker(bind=engine)


def get_connection():
    conn = db_session()
    return conn


@contextlib.contextmanager
def get_db():
    conn = None
    try:
        conn = db_session()
        yield conn
    finally:
        if conn is not None:
            conn.close()