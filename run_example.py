"""Run the ETL and ELT comparison on the synthetic order snapshot."""

from etl_elt_example import compare_pipelines
from etl_elt_example.sample_data import EXPECTED_PAID_ORDERS, ORDERS


def main() -> None:
    result = compare_pipelines(ORDERS)
    if result.etl_orders != EXPECTED_PAID_ORDERS or result.elt_orders != EXPECTED_PAID_ORDERS:
        raise AssertionError("pipelines returned an unexpected prepared snapshot")
    if len(result.elt_raw_orders) != len(ORDERS):
        raise AssertionError("ELT did not retain the complete raw snapshot")

    print(f"etl_rows: {len(result.etl_orders)}")
    print(f"etl_total_cents: {result.etl_total_cents}")
    print(f"elt_rows: {len(result.elt_orders)}")
    print(f"elt_total_cents: {result.elt_total_cents}")
    print(f"same_result: {str(result.etl_orders == result.elt_orders).lower()}")


if __name__ == "__main__":
    main()
