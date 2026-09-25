from typing import Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    venue: str
    capacity: int
    organizer: str
    status: str

    @field_validator("title", "venue", "organizer")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field must not be empty")
        return value

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Capacity must be greater than 0")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip().capitalize()
        if value not in {"Open", "Closed"}:
            raise ValueError("Status must be Open or Closed")
        return value


class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int
    student_name: str
    roll_number: str
    email: EmailStr

    @field_validator("student_name", "roll_number")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field must not be empty")
        return value