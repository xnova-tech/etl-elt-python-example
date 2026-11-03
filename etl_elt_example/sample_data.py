"""Synthetic snapshot used by the executable example and tests."""

from etl_elt_example.domain import PaidOrder, SourceOrder

ORDERS = (
    SourceOrder(order_id="o-101", status="paid", amount_text="1200"),
    SourceOrder(order_id="o-102", status="paid", amount_text="2300"),
    SourceOrder(order_id="o-103", status="cancelled", amount_text="900"),
)

EXPECTED_PAID_ORDERS = (
    PaidOrder(order_id="o-101", amount_cents=1200),
    PaidOrder(order_id="o-102", amount_cents=2300),
)
