from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    description: str
    category: str
    location: str
    reported_by: str
    status: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title must not be empty")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 5:
            raise ValueError("Description must contain meaningful text")

        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip().capitalize()

        allowed_statuses = {"Lost", "Found", "Returned"}

        if value not in allowed_statuses:
            raise ValueError("Status must be Lost, Found, or Returned")

        return value

    @field_validator("category", "location", "reported_by")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field is required")

        return value