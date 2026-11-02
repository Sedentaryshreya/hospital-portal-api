from datetime import datetime
from enum import Enum
from typing import Optional
from fastapi import FastAPI, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.models import Booking

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Hospital Portal - Incoming Ambulances")

class AmbulanceStatus(str, Enum):
    DISPATCHED = "DISPATCHED"
    EN_ROUTE = "EN_ROUTE"
    NEARBY = "NEARBY"

INCOMING = [s.value for s in AmbulanceStatus]

def to_dict(b: Booking):
    return {
        "bookingId": b.booking_code,
        "emergencyType": b.emergency_type,
        "ambulanceStatus": b.ambulance_status,
        "expectedArrival": b.expected_arrival.isoformat() if b.expected_arrival else None,
    }

@app.get("/api/hospital/incoming-ambulances")
def list_incoming(
    x_hospital_id: int = Header(...),
    status: Optional[AmbulanceStatus] = None,
    arrival_from: Optional[datetime] = None,
    arrival_to: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if arrival_from and arrival_to and arrival_to < arrival_from:
        raise HTTPException(400, "arrival_to must not be before arrival_from")

    q = db.query(Booking).filter(
        Booking.hospital_id == x_hospital_id,
        Booking.ambulance_status.in_(INCOMING),
    )
    if status:
        q = q.filter(Booking.ambulance_status == status.value)
    if arrival_from:
        q = q.filter(Booking.expected_arrival >= arrival_from)
    if arrival_to:
        q = q.filter(Booking.expected_arrival <= arrival_to)

    total = q.count()
    rows = (q.order_by(Booking.expected_arrival.is_(None),
                       Booking.expected_arrival.asc(),
                       Booking.id.asc())
              .offset((page - 1) * limit).limit(limit).all())
    return {"data": [to_dict(r) for r in rows],
            "page": page, "limit": limit, "total": total}

@app.get("/api/hospital/incoming-ambulances/{booking_id}")
def get_incoming(booking_id: int, x_hospital_id: int = Header(...),
                 db: Session = Depends(get_db)):
    b = db.query(Booking).filter(Booking.id == booking_id,
                                 Booking.hospital_id == x_hospital_id).first()
    if b is None:
        raise HTTPException(404, "Incoming ambulance not found")
    return to_dict(b)