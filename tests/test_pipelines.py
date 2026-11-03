"""Regression and negative controls for both pipeline orders."""

import sqlite3
from collections.abc import Callable, Iterable
from dataclasses import dataclass

import pytest

from etl_elt_example import InvalidOrderError, OrderDatabase, SourceOrder, compare_pipelines, run_elt, run_etl
from etl_elt_example.sample_data import EXPECTED_PAID_ORDERS, ORDERS

PipelineRunner = Callable[[OrderDatabase, Iterable[SourceOrder]], None]


@dataclass(frozen=True, slots=True)
class PipelineCase:
    name: str
    include_raw: bool
    run: PipelineRunner


PIPELINES = (
    PipelineCase(name="etl", include_raw=False, run=run_etl),
    PipelineCase(name="elt", include_raw=True, run=run_elt),
)

INVALID_SNAPSHOTS = (
    pytest.param(
        (ORDERS[0], SourceOrder("o-102", "paid", "12oops"), ORDERS[2]),
        id="invalid-amount",
    ),
    pytest.param(
        (ORDERS[0], SourceOrder("o-102", "refunded", "2300"), ORDERS[2]),
        id="unknown-status",
    ),
    pytest.param(
        (ORDERS[0], SourceOrder("o-101", "paid", "2300"), ORDERS[2]),
        id="duplicate-id",
    ),
    pytest.param(
        (ORDERS[0], SourceOrder("", "paid", "2300"), ORDERS[2]),
        id="empty-id",
    ),
)


def test_both_pipelines_return_the_same_prepared_snapshot() -> None:
    result = compare_pipelines(ORDERS)

    assert result.etl_orders == EXPECTED_PAID_ORDERS
    assert result.elt_orders == EXPECTED_PAID_ORDERS
    assert result.elt_raw_orders == ORDERS
    assert result.etl_total_cents == 3500
    assert result.elt_total_cents == 3500


@pytest.mark.parametrize("pipeline", PIPELINES, ids=lambda pipeline: pipeline.name)
def test_replaying_the_same_snapshot_is_stable(pipeline: PipelineCase) -> None:
    with OrderDatabase.in_memory(include_raw=pipeline.include_raw) as database:
        pipeline.run(database, ORDERS)
        first_result = database.paid_orders()

        pipeline.run(database, ORDERS)

        assert database.paid_orders() == first_result


@pytest.mark.parametrize("pipeline", PIPELINES, ids=lambda pipeline: pipeline.name)
@pytest.mark.parametrize("invalid_snapshot", INVALID_SNAPSHOTS)
def test_invalid_snapshot_rolls_back_both_layers(
    pipeline: PipelineCase,
    invalid_snapshot: tuple[SourceOrder, ...],
) -> None:
    with OrderDatabase.in_memory(include_raw=pipeline.include_raw) as database:
        pipeline.run(database, ORDERS)
        paid_before = database.paid_orders()
        raw_before = database.raw_orders() if pipeline.include_raw else ()

        with pytest.raises(InvalidOrderError):
            pipeline.run(database, invalid_snapshot)

        assert database.paid_orders() == paid_before
        if pipeline.include_raw:
            assert database.raw_orders() == raw_before


def test_sqlite_cast_alone_does_not_validate_the_whole_string() -> None:
    with sqlite3.connect(":memory:") as connection:
        value = connection.execute("SELECT CAST('12oops' AS INTEGER)").fetchone()

    assert value == (12,)
