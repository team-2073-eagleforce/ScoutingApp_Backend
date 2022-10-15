from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgresql://aenizrypyfymkm:9b3a3a0cbe70f863a09eb75d450b70aa2a0ea507b8dd1908e44201a25dff2b7a@ec2-52-3-60-53.compute-1.amazonaws.com:5432/d7qmk8f1htkfkv")
db = scoped_session(sessionmaker(bind=engine))
conn = db()

#db.execute('DELETE FROM scouting WHERE "matchnumber"=1 AND team=9973')
conn.commit()
