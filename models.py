from sqlalchemy import Column, Integer, String
from database import Base


class AddressBook(Base):
    __tablename__ = "addressbook"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    lattitude = Column(Integer)
    longitude = Column(Integer)
