from datetime import datetime, timedelta
from app.database import Base, engine, SessionLocal
from app.models import Hospital, Booking

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(Hospital).count() == 0:
        now = datetime.now()
        db.add_all([Hospital(id=1, name="Test Hospital A"),
                    Hospital(id=2, name="Test Hospital B")])
        db.add_all([
            Booking(booking_code="BK-1001", hospital_id=1, emergency_type="Cardiac",
                    ambulance_status="EN_ROUTE", expected_arrival=now + timedelta(minutes=10)),
            Booking(booking_code="BK-1002", hospital_id=1, emergency_type="Accident",
                    ambulance_status="DISPATCHED", expected_arrival=now + timedelta(minutes=25)),
            Booking(booking_code="BK-1003", hospital_id=1, emergency_type="Stroke",
                    ambulance_status="NEARBY", expected_arrival=None),
            Booking(booking_code="BK-1004", hospital_id=1, emergency_type="Burns",
                    ambulance_status="ARRIVED", expected_arrival=now - timedelta(minutes=5)),
            Booking(booking_code="BK-2001", hospital_id=2, emergency_type="Cardiac",
                    ambulance_status="EN_ROUTE", expected_arrival=now + timedelta(minutes=15)),
        ])
        db.commit()
    db.close()

if __name__ == "__main__":
    seed()