"""Application service that compares both pipeline orders on one snapshot."""

from collections.abc import Iterable
from dataclasses import dataclass

from etl_elt_example.domain import PaidOrder, SourceOrder
from etl_elt_example.pipelines import run_elt, run_etl
from etl_elt_example.storage import OrderDatabase


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    """Observed rows from the ETL and ELT runs."""

    etl_orders: tuple[PaidOrder, ...]
    elt_orders: tuple[PaidOrder, ...]
    elt_raw_orders: tuple[SourceOrder, ...]

    @property
    def etl_total_cents(self) -> int:
        return sum(order.amount_cents for order in self.etl_orders)

    @property
    def elt_total_cents(self) -> int:
        return sum(order.amount_cents for order in self.elt_orders)


def compare_pipelines(orders: Iterable[SourceOrder]) -> ComparisonResult:
    """Run both approaches against independent in-memory databases."""

    snapshot = tuple(orders)
    with (
        OrderDatabase.in_memory(include_raw=False) as etl_database,
        OrderDatabase.in_memory(include_raw=True) as elt_database,
    ):
        run_etl(etl_database, snapshot)
        run_elt(elt_database, snapshot)
        return ComparisonResult(
            etl_orders=etl_database.paid_orders(),
            elt_orders=elt_database.paid_orders(),
            elt_raw_orders=elt_database.raw_orders(),
        )
