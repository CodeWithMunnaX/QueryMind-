"""SQLAlchemy ORM models."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(100))
    order_date: Mapped[date] = mapped_column(Date)
    customer_id: Mapped[str] = mapped_column(String(100))
    customer_name: Mapped[str] = mapped_column(String(255))
    country: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    region: Mapped[str] = mapped_column(String(100))
    product_id: Mapped[str] = mapped_column(String(100))
    product_name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    sub_category: Mapped[str] = mapped_column(String(100))
    sales: Mapped[float] = mapped_column(Numeric(12, 2))
    quantity: Mapped[int] = mapped_column(Integer)
    discount: Mapped[float] = mapped_column(Numeric(5, 2))
    profit: Mapped[float] = mapped_column(Numeric(12, 2))

    __table_args__ = (
        Index("ix_sales_order_date", "order_date"),
        Index("ix_sales_region", "region"),
        Index("ix_sales_category", "category"),
        Index("ix_sales_product_name", "product_name"),
    )


class QueryHistory(Base):
    """Stores every question asked so it can be replayed from the history panel."""

    __tablename__ = "query_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    conversation_id: Mapped[str] = mapped_column(String(100), index=True)
    question: Mapped[str] = mapped_column(String)
    sql: Mapped[str | None] = mapped_column(String, nullable=True)
    answer: Mapped[str | None] = mapped_column(String, nullable=True)
    chart_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ok")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_history_created_at", "created_at"),)


class ConversationMessage(Base):
    """Stores raw chat turns per conversation for follow-up-question context."""

    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    conversation_id: Mapped[str] = mapped_column(String(100), index=True)
    role: Mapped[str] = mapped_column(String(20))  # "user" | "assistant"
    content: Mapped[str] = mapped_column(String)
    sql: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
