"""Typed ETL and ELT example built on SQLite."""

from etl_elt_example.demo import ComparisonResult, compare_pipelines
from etl_elt_example.domain import InvalidOrderError, PaidOrder, SourceOrder
from etl_elt_example.pipelines import run_elt, run_etl
from etl_elt_example.storage import OrderDatabase

__all__ = [
    "ComparisonResult",
    "InvalidOrderError",
    "OrderDatabase",
    "PaidOrder",
    "SourceOrder",
    "compare_pipelines",
    "run_elt",
    "run_etl",
]
