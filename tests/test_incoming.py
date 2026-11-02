from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models import Hospital, Booking

engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                       poolclass=StaticPool)
TestSession = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def override_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_db

db = TestSession()
now = datetime.utcnow()
db.add_all([Hospital(id=1, name="A"), Hospital(id=2, name="B")])
db.add_all([
    Booking(id=1, booking_code="T1", hospital_id=1, emergency_type="Cardiac",
            ambulance_status="EN_ROUTE", expected_arrival=now + timedelta(minutes=10)),
    Booking(id=2, booking_code="T2", hospital_id=1, emergency_type="Accident",
            ambulance_status="DISPATCHED", expected_arrival=now + timedelta(minutes=30)),
    Booking(id=3, booking_code="T3", hospital_id=1, emergency_type="Burns",
            ambulance_status="ARRIVED", expected_arrival=now),
    Booking(id=4, booking_code="T4", hospital_id=2, emergency_type="Stroke",
            ambulance_status="EN_ROUTE", expected_arrival=now + timedelta(minutes=5)),
])
db.commit()
db.close()

client = TestClient(app)
H1 = {"x-hospital-id": "1"}

def test_only_own_hospital_and_incoming():
    r = client.get("/api/hospital/incoming-ambulances", headers=H1)
    assert r.status_code == 200
    assert [x["bookingId"] for x in r.json()["data"]] == ["T1", "T2"]

def test_status_filter():
    r = client.get("/api/hospital/incoming-ambulances?status=EN_ROUTE", headers=H1)
    assert [x["bookingId"] for x in r.json()["data"]] == ["T1"]

def test_invalid_status():
    r = client.get("/api/hospital/incoming-ambulances?status=abc", headers=H1)
    assert r.status_code == 422

def test_pagination():
    r = client.get("/api/hospital/incoming-ambulances?page=2&limit=1", headers=H1)
    assert [x["bookingId"] for x in r.json()["data"]] == ["T2"]
    assert r.json()["total"] == 2

def test_bad_page():
    r = client.get("/api/hospital/incoming-ambulances?page=0", headers=H1)
    assert r.status_code == 422

def test_empty_result():
    r = client.get("/api/hospital/incoming-ambulances?status=NEARBY", headers=H1)
    assert r.status_code == 200 and r.json()["data"] == []

def test_detail_ok():
    r = client.get("/api/hospital/incoming-ambulances/1", headers=H1)
    assert r.status_code == 200 and r.json()["bookingId"] == "T1"

def test_detail_unknown_id():
    assert client.get("/api/hospital/incoming-ambulances/999", headers=H1).status_code == 404

def test_detail_other_hospital():
    assert client.get("/api/hospital/incoming-ambulances/4", headers=H1).status_code == 404