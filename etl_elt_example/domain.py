"""Domain models shared by both pipelines."""

from dataclasses import dataclass
from enum import StrEnum


class OrderStatus(StrEnum):
    """Statuses accepted by the reporting pipeline."""

    PAID = "paid"
    CANCELLED = "cancelled"


class InvalidOrderError(ValueError):
    """Raised when a source snapshot violates the example contract."""


@dataclass(frozen=True, slots=True)
class SourceOrder:
    """Untrusted values as received from the source system."""

    order_id: str
    status: str
    amount_text: str


@dataclass(frozen=True, slots=True)
class ValidatedOrder:
    """Source order after application-side validation."""

    order_id: str
    status: OrderStatus
    amount_cents: int


@dataclass(frozen=True, slots=True)
class PaidOrder:
    """Prepared row stored in the reporting table."""

    order_id: str
    amount_cents: int
