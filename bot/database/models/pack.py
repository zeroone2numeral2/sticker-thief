from sqlalchemy import Column, String, Integer, Boolean

from ..base import Base, engine


class Pack(Base):
    __tablename__ = 'packs'

    pack_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    title = Column(String)
    name = Column(String)
    is_animated = Column(Boolean, default=False)

    def __init__(self, user_id, title, name, is_animated=False):
        self.user_id = user_id
        self.title = title
        self.name = name
        self.is_animated = is_animated


Base.metadata.create_all(engine)
