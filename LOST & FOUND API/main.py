from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select

from database import create_db_and_tables, engine
from models import Item


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="College Lost & Found API",
    description="A FastAPI-based Lost & Found management system",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "message": "College Lost & Found API is running"
    }


# 1. POST /items
@app.post("/items", response_model=Item, status_code=201)
def create_item(item: Item):
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)

        return item


# 2. GET /items
@app.get("/items", response_model=list[Item])
def get_items():
    with Session(engine) as session:
        items = session.exec(select(Item)).all()

        return items


# 3. GET /items/{item_id}
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)

        if not item:
            raise HTTPException(
                status_code=404,
                detail="Item not found"
            )

        return item


# 4. PUT /items/{item_id}
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item):
    with Session(engine) as session:
        existing_item = session.get(Item, item_id)

        if not existing_item:
            raise HTTPException(
                status_code=404,
                detail="Item not found"
            )

        existing_item.title = updated_item.title
        existing_item.description = updated_item.description
        existing_item.category = updated_item.category
        existing_item.location = updated_item.location
        existing_item.reported_by = updated_item.reported_by
        existing_item.status = updated_item.status

        session.add(existing_item)
        session.commit()
        session.refresh(existing_item)

        return existing_item


# 5. DELETE /items/{item_id}
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)

        if not item:
            raise HTTPException(
                status_code=404,
                detail="Item not found"
            )

        session.delete(item)
        session.commit()

        return {
            "message": "Item deleted successfully",
            "item_id": item_id
        }


# 6. GET /items/status/{status}
@app.get("/items/status/{status}", response_model=list[Item])
def get_items_by_status(status: str):
    status = status.strip().capitalize()

    allowed_statuses = {"Lost", "Found", "Returned"}

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Status must be Lost, Found, or Returned"
        )

    with Session(engine) as session:
        statement = select(Item).where(Item.status == status)
        items = session.exec(statement).all()

        return items


# 7. GET /items/category/{category}
@app.get("/items/category/{category}", response_model=list[Item])
def get_items_by_category(category: str):
    with Session(engine) as session:
        statement = select(Item).where(
            Item.category == category
        )

        items = session.exec(statement).all()

        return items