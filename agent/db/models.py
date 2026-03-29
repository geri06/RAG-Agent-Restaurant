"""
Database Models — agent/db/models.py

Defines the shape of our tables using SQLAlchemy ORM.

WHY ORM?
  Instead of writing raw SQL strings, we define Python classes.
  SQLAlchemy translates them to SQL automatically.
  This means auto-completion, type safety, and no typos in SQL.

TABLES:
  - Restaurant : one row per restaurant client
  - Invoice    : one invoice per delivery (weekly)
  - LineItem   : individual ingredient lines within an invoice
"""

import datetime
from sqlalchemy import ForeignKey, Numeric, String, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """All ORM models inherit from this class."""
    pass


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)

    # One restaurant has many invoices
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="restaurant")

    def __repr__(self) -> str:
        return f"<Restaurant id={self.id} name={self.name!r}>"


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"))
    issued_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    # Many invoices belong to one restaurant
    restaurant: Mapped["Restaurant"] = relationship(back_populates="invoices")
    # One invoice has many line items
    line_items: Mapped[list["LineItem"]] = relationship(back_populates="invoice")

    def __repr__(self) -> str:
        return f"<Invoice id={self.id} restaurant_id={self.restaurant_id}>"


class LineItem(Base):
    __tablename__ = "line_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    ingredient: Mapped[str] = mapped_column(String(100), nullable=False)
    # Use Numeric for money — never float (floating-point rounding errors)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    quantity_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    invoice: Mapped["Invoice"] = relationship(back_populates="line_items")

    def __repr__(self) -> str:
        return f"<LineItem ingredient={self.ingredient!r} price={self.unit_price}>"
