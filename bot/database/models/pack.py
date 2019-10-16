from sqlalchemy import Column, String, Integer

from ..base import Base, engine


class Pack(Base):
    __tablename__ = 'packs'

    pack_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    title = Column(String)
    name = Column(String)

    def __init__(self, user_id, title, name):
        self.user_id = user_id
        self.title = title
        self.name = name


Base.metadata.create_all(engine)
