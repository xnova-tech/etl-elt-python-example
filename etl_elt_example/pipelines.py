"""ETL and ELT orchestration over the same storage contract."""

from collections.abc import Iterable

from etl_elt_example.domain import OrderStatus, PaidOrder, SourceOrder
from etl_elt_example.storage import OrderDatabase
from etl_elt_example.validation import validate_snapshot


def run_etl(database: OrderDatabase, orders: Iterable[SourceOrder]) -> None:
    """Validate and transform in Python before loading the prepared table."""

    validated = validate_snapshot(orders)
    paid_orders = tuple(
        PaidOrder(order_id=order.order_id, amount_cents=order.amount_cents)
        for order in validated
        if order.status is OrderStatus.PAID
    )
    database.replace_paid_orders(paid_orders)


def run_elt(database: OrderDatabase, orders: Iterable[SourceOrder]) -> None:
    """Load raw values first and transform them inside SQLite."""

    database.replace_raw_orders_and_transform(tuple(orders))
