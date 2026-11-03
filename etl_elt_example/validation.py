"""Application-side validation used by the ETL path."""

from collections.abc import Iterable

from etl_elt_example.domain import InvalidOrderError, OrderStatus, SourceOrder, ValidatedOrder


def validate_order(order: SourceOrder) -> ValidatedOrder:
    """Validate one untrusted source row and convert its amount to integer cents."""

    if not 1 <= len(order.order_id) <= 64:
        raise InvalidOrderError("order_id must contain between 1 and 64 characters")

    try:
        status = OrderStatus(order.status)
    except ValueError as error:
        raise InvalidOrderError(f"unknown order status: {order.status!r}") from error

    amount = order.amount_text
    if not (1 <= len(amount) <= 9 and amount.isascii() and amount.isdecimal()):
        raise InvalidOrderError("amount must contain between 1 and 9 ASCII digits")

    return ValidatedOrder(order_id=order.order_id, status=status, amount_cents=int(amount))


def validate_snapshot(orders: Iterable[SourceOrder]) -> tuple[ValidatedOrder, ...]:
    """Validate a full snapshot and reject duplicate order identifiers."""

    validated: list[ValidatedOrder] = []
    seen_ids: set[str] = set()
    for order in orders:
        if order.order_id in seen_ids:
            raise InvalidOrderError(f"duplicate order_id: {order.order_id!r}")
        seen_ids.add(order.order_id)
        validated.append(validate_order(order))
    return tuple(validated)
