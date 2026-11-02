from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.database import Base

class Hospital(Base):
    __tablename__ = "hospitals"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    booking_code = Column(String, unique=True, nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    emergency_type = Column(String, nullable=False)
    ambulance_status = Column(String, nullable=False)
    expected_arrival = Column(DateTime, nullable=True)