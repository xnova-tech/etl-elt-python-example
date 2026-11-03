"""SQLite storage boundary for raw and prepared order snapshots."""

import sqlite3
from collections.abc import Sequence
from types import TracebackType

from etl_elt_example.domain import InvalidOrderError, PaidOrder, SourceOrder

PAID_TABLE = """
CREATE TABLE paid_orders (
    order_id TEXT PRIMARY KEY CHECK (length(order_id) BETWEEN 1 AND 64),
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0)
)
"""

RAW_TABLE = """
CREATE TABLE raw_orders (
    order_id TEXT PRIMARY KEY CHECK (length(order_id) BETWEEN 1 AND 64),
    status TEXT NOT NULL,
    amount_text TEXT NOT NULL
)
"""


class OrderDatabase:
    """Small repository that owns one SQLite connection."""

    def __init__(self, connection: sqlite3.Connection, *, include_raw: bool) -> None:
        self._connection = connection
        self._include_raw = include_raw

    @classmethod
    def in_memory(cls, *, include_raw: bool) -> "OrderDatabase":
        """Create an isolated in-memory database for one pipeline run."""

        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.execute(PAID_TABLE)
        if include_raw:
            connection.execute(RAW_TABLE)
        return cls(connection, include_raw=include_raw)

    def __enter__(self) -> "OrderDatabase":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()

    def replace_paid_orders(self, orders: Sequence[PaidOrder]) -> None:
        """Atomically replace the prepared reporting snapshot."""

        with self._connection:
            self._connection.execute("DELETE FROM paid_orders")
            self._connection.executemany(
                "INSERT INTO paid_orders (order_id, amount_cents) VALUES (?, ?)",
                ((order.order_id, order.amount_cents) for order in orders),
            )

    def replace_raw_orders_and_transform(self, orders: Sequence[SourceOrder]) -> None:
        """Load raw strings, validate them in SQLite, then rebuild the prepared table."""

        if not self._include_raw:
            raise RuntimeError("raw_orders is not available in this database")

        try:
            with self._connection:
                self._connection.execute("DELETE FROM raw_orders")
                self._connection.executemany(
                    "INSERT INTO raw_orders (order_id, status, amount_text) VALUES (?, ?, ?)",
                    ((order.order_id, order.status, order.amount_text) for order in orders),
                )
                invalid_rows = self._connection.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM raw_orders
                    WHERE status NOT IN ('paid', 'cancelled')
                       OR length(amount_text) NOT BETWEEN 1 AND 9
                       OR amount_text GLOB '*[^0-9]*'
                    """
                ).fetchone()
                if invalid_rows is None or int(invalid_rows["count"]) != 0:
                    raise InvalidOrderError("raw snapshot contains an invalid order")

                self._connection.execute("DELETE FROM paid_orders")
                self._connection.execute(
                    """
                    INSERT INTO paid_orders (order_id, amount_cents)
                    SELECT order_id, CAST(amount_text AS INTEGER)
                    FROM raw_orders
                    WHERE status = 'paid'
                    """
                )
        except sqlite3.IntegrityError as error:
            raise InvalidOrderError("raw snapshot violates database constraints") from error

    def paid_orders(self) -> tuple[PaidOrder, ...]:
        rows = self._connection.execute("SELECT order_id, amount_cents FROM paid_orders ORDER BY order_id").fetchall()
        return tuple(PaidOrder(order_id=str(row["order_id"]), amount_cents=int(row["amount_cents"])) for row in rows)

    def raw_orders(self) -> tuple[SourceOrder, ...]:
        if not self._include_raw:
            raise RuntimeError("raw_orders is not available in this database")
        rows = self._connection.execute(
            "SELECT order_id, status, amount_text FROM raw_orders ORDER BY order_id"
        ).fetchall()
        return tuple(
            SourceOrder(
                order_id=str(row["order_id"]),
                status=str(row["status"]),
                amount_text=str(row["amount_text"]),
            )
            for row in rows
        )
