from __future__ import annotations

from pydantic import BaseModel
from sqlalchemy import Column, String, ForeignKey, Enum, Numeric, JSON, Integer, select, Sequence
from sqlalchemy.orm import relationship
from ocpp.v16.enums import ChargePointStatus

from core.database import Model


class Account(Model):
    __tablename__ = "accounts"

    name = Column(String(48), nullable=False, unique=True)
    locations = relationship("Location",
                             back_populates="account",
                             lazy="joined")
    transactions = relationship("Transaction",
                                 back_populates="account",
                                 lazy="joined")

    def __repr__(self) -> str:
        return f"Account: {self.name}, {self.id}, active={self.is_active}"


class Location(Model):
    __tablename__ = "locations"

    name = Column(String(48), nullable=False, unique=True)
    city = Column(String(48), nullable=False)
    address1 = Column(String(48), nullable=False)
    address2 = Column(String(100), nullable=True)
    comment = Column(String(200), nullable=True)

    charge_points = relationship("ChargePoint",
                                 back_populates="location",
                                 lazy="joined")
    account_id = Column(String, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    account = relationship("Account", back_populates="locations", lazy='joined')

    charge_points_count = None

    def __repr__(self) -> str:
        return f"Location: {self.name}, {self.city}, {self.id}"


class ChargePoint(Model):
    __tablename__ = "charge_points"

    description = Column(String(48), nullable=True)
    status = Column(Enum(ChargePointStatus), default=ChargePointStatus.unavailable, index=True)
    manufacturer = Column(String, nullable=False)
    latitude = Column(Numeric, nullable=True)
    longitude = Column(Numeric, nullable=True)
    serial_number = Column(String, nullable=False, unique=True)
    comment = Column(String, nullable=True)
    model = Column(String, nullable=False)
    password = Column(String, nullable=True)
    connectors = Column(JSON, default=dict())

    location_id = Column(String, ForeignKey("locations.id"), nullable=False)
    location = relationship("Location", back_populates="charge_points", lazy="joined")

    def __repr__(self):
        return f"ChargePoint (id={self.id}, status={self.status}, location={self.location})"


class Transaction(Model):
    __tablename__ = "transactions"
    transaction_id_seq = Sequence("transaction_id_seq")

    city = Column(String, nullable=False)
    vehicle = Column(String, nullable=False)
    address = Column(String, nullable=False)
    meter_start = Column(Integer, nullable=False)
    meter_stop = Column(Integer, nullable=True)
    charge_point = Column(String, nullable=False)
    transaction_id = Column(Integer, transaction_id_seq, server_default=transaction_id_seq.next_value())

    account_id = Column(String, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    account = relationship("Account", back_populates="transactions", lazy='joined')


class AuthData(BaseModel):
    password: str
