"""SQLAlchemy ORM 模型。"""
from sqlalchemy import Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Stock(Base):
    __tablename__ = "stocks"

    code: Mapped[str] = mapped_column(String(12), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    industry: Mapped[str] = mapped_column(String(64), default="未知")


class DailyPrice(Base):
    __tablename__ = "daily_prices"
    __table_args__ = (UniqueConstraint("date", "code", name="uq_daily_prices_date_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[Date] = mapped_column(Date, index=True)
    code: Mapped[str] = mapped_column(ForeignKey("stocks.code"), index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)


class Financial(Base):
    __tablename__ = "financials"

    code: Mapped[str] = mapped_column(ForeignKey("stocks.code"), primary_key=True)
    roe: Mapped[float] = mapped_column(Float, default=0.0)
    roa: Mapped[float] = mapped_column(Float, default=0.0)
    pe: Mapped[float] = mapped_column(Float, default=0.0)
    pb: Mapped[float] = mapped_column(Float, default=0.0)
    ps: Mapped[float] = mapped_column(Float, default=0.0)
    revenue_growth: Mapped[float] = mapped_column(Float, default=0.0)
    market_cap: Mapped[float] = mapped_column(Float, default=0.0)


class Factor(Base):
    __tablename__ = "factors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[Date] = mapped_column(Date, index=True)
    code: Mapped[str] = mapped_column(ForeignKey("stocks.code"), index=True)
    factor_name: Mapped[str] = mapped_column(String(64), index=True)
    factor_value: Mapped[float] = mapped_column(Float)
