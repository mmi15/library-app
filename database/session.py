from database.db_config import SessionLocal

def get_session():
    return SessionLocal()

def get_or_create(session, Model, **kwargs):
    obj = session.query(Model).filter_by(**kwargs).first()
    if obj:
        return obj
    obj = Model(**kwargs)
    session.add(obj)
    session.flush()
    return obj