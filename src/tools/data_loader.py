import pandas as pd
from langchain_core.tools import tool
from src.config import DATA_DIR
import os

_DATA_PATH = os.path.join(DATA_DIR, "sample_data.csv")


def _load_df() -> pd.DataFrame:
    df = pd.read_csv(_DATA_PATH, parse_dates=["date"])
    return df


@tool
def query_sales_data(product_id: str | None = None, supplier: str | None = None) -> str:
    """Query supply chain sales data. Optionally filter by product_id (e.g. 'P001') or supplier (e.g. 'SupplierA').
    Returns a summary table of matching records."""
    df = _load_df()
    if product_id:
        df = df[df["product_id"] == product_id]
    if supplier:
        df = df[df["supplier"] == supplier]
    if df.empty:
        return "No data found for the given filters."
    return df.to_string(index=False)


@tool
def get_product_list() -> str:
    """Get a list of all products in the supply chain dataset with their IDs and names."""
    df = _load_df()
    products = df[["product_id", "product_name"]].drop_duplicates()
    return products.to_string(index=False)


@tool
def get_latest_inventory(product_id: str | None = None) -> str:
    """Get the most recent inventory snapshot for each product. Optionally filter by product_id.
    Shows stock_level, reorder_point, supplier, and lead_time_days."""
    df = _load_df()
    if product_id:
        df = df[df["product_id"] == product_id]
    latest = df.sort_values("date").groupby("product_id").last().reset_index()
    cols = ["product_id", "product_name", "date", "stock_level", "reorder_point", "supplier", "lead_time_days"]
    return latest[cols].to_string(index=False)


@tool
def get_supplier_summary() -> str:
    """Get a summary of all suppliers including products supplied, average lead times, and average unit costs."""
    df = _load_df()
    summaries = []
    for supplier, group in df.groupby("supplier"):
        products = group["product_name"].unique().tolist()
        avg_lead = group["lead_time_days"].mean()
        avg_cost = group["unit_cost"].mean()
        summaries.append(f"Supplier: {supplier}\n  Products: {', '.join(products)}\n  Avg Lead Time: {avg_lead:.1f} days\n  Avg Unit Cost: ${avg_cost:.2f}")
    return "\n\n".join(summaries)
