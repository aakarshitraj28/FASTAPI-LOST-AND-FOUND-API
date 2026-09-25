from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select

from database import engine, create_db_and_tables
from models import Event, Reservation


app = FastAPI(title="Event Reservation API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# 1. POST /events
@app.post("/events", response_model=Event)
def create_event(event: Event):
    with Session(engine) as session:
        session.add(event)
        session.commit()
        session.refresh(event)
        return event


# 2. GET /events
@app.get("/events", response_model=list[Event])
def get_events():
    with Session(engine) as session:
        return session.exec(select(Event)).all()


# 3. GET /events/{event_id}
@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: int):
    with Session(engine) as session:
        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        return event


# 4. PUT /events/{event_id}
@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: int, updated_event: Event):
    with Session(engine) as session:
        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        event.title = updated_event.title
        event.venue = updated_event.venue
        event.capacity = updated_event.capacity
        event.organizer = updated_event.organizer
        event.status = updated_event.status

        session.add(event)
        session.commit()
        session.refresh(event)

        return event


# 5. DELETE /events/{event_id}
@app.delete("/events/{event_id}")
def delete_event(event_id: int):
    with Session(engine) as session:
        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        session.delete(event)
        session.commit()

        return {"message": "Event deleted successfully"}


# 6. POST /events/{event_id}/reserve
@app.post("/events/{event_id}/reserve", response_model=Reservation)
def create_reservation(event_id: int, reservation: Reservation):
    with Session(engine) as session:

        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )

        if event.status != "Open":
            raise HTTPException(
                status_code=400,
                detail="Reservations are closed for this event"
            )

        booked = session.exec(
            select(Reservation).where(
                Reservation.event_id == event_id
            )
        ).all()

        if len(booked) >= event.capacity:
            raise HTTPException(
                status_code=400,
                detail="Event is full. No more reservations available"
            )

        reservation.event_id = event_id

        session.add(reservation)
        session.commit()
        session.refresh(reservation)

        return reservation


# 7. GET /events/{event_id}/reservations
@app.get("/events/{event_id}/reservations")
def get_event_reservations(event_id: int):
    with Session(engine) as session:

        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
            )

        reservations = session.exec(
            select(Reservation).where(
                Reservation.event_id == event_id
            )
        ).all()

        return reservations


# 8. DELETE /reservations/{reservation_id}
@app.delete("/reservations/{reservation_id}")
def cancel_reservation(reservation_id: int):
    with Session(engine) as session:

        reservation = session.get(Reservation, reservation_id)

        if not reservation:
            raise HTTPException(
                status_code=404,
                detail="Reservation not found"
            )

        session.delete(reservation)
        session.commit()

        return {"message": "Reservation cancelled successfully"}


# 9. GET /events/{event_id}/availability
@app.get("/events/{event_id}/availability")
def get_availability(event_id: int):
    with Session(engine) as session:

        event = session.get(Event, event_id)

        if not event:
            raise HTTPException(
                status_code=404,
                detail="Event not found"
    ``        )

        booked = len(
            session.exec(
                select(Reservation).where(
                    Reservation.event_id == event_id
                )
            ).all()
        )

        return {
            "capacity": event.capacity,
            "booked": booked,
            "remaining": event.capacity - booked
        }