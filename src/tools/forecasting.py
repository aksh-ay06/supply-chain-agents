import pandas as pd
from langchain_core.tools import tool
from src.tools.data_loader import _load_df


@tool
def forecast_demand(product_id: str, window: int = 7) -> str:
    """Forecast demand for a product using moving average over the given window (default 7 days).
    Returns current average daily sales, 7-day forecast, and trend direction."""
    df = _load_df()
    product_df = df[df["product_id"] == product_id].sort_values("date")
    if product_df.empty:
        return f"No data found for product {product_id}."

    product_name = product_df["product_name"].iloc[0]
    sales = product_df["quantity_sold"]

    recent = sales.tail(window)
    earlier = sales.head(window)
    recent_avg = recent.mean()
    earlier_avg = earlier.mean()

    if recent_avg > earlier_avg * 1.05:
        trend = "up"
    elif recent_avg < earlier_avg * 0.95:
        trend = "down"
    else:
        trend = "stable"

    forecast_7d = recent_avg * 7

    return (
        f"Product: {product_name} ({product_id})\n"
        f"Avg Daily Sales (last {window} days): {recent_avg:.1f} units\n"
        f"Avg Daily Sales (first {window} days): {earlier_avg:.1f} units\n"
        f"7-Day Forecast: {forecast_7d:.0f} units\n"
        f"Trend: {trend}"
    )


@tool
def calculate_days_of_supply(product_id: str) -> str:
    """Calculate days of supply remaining for a product based on current stock and recent sales rate."""
    df = _load_df()
    product_df = df[df["product_id"] == product_id].sort_values("date")
    if product_df.empty:
        return f"No data found for product {product_id}."

    product_name = product_df["product_name"].iloc[0]
    latest = product_df.iloc[-1]
    avg_daily_sales = product_df["quantity_sold"].tail(7).mean()
    stock = latest["stock_level"]
    reorder_point = latest["reorder_point"]

    days_of_supply = stock / avg_daily_sales if avg_daily_sales > 0 else float("inf")

    if stock <= 0:
        risk = "critical"
    elif stock < reorder_point:
        risk = "warning"
    else:
        risk = "healthy"

    return (
        f"Product: {product_name} ({product_id})\n"
        f"Current Stock: {stock} units\n"
        f"Reorder Point: {reorder_point} units\n"
        f"Avg Daily Sales (7d): {avg_daily_sales:.1f} units\n"
        f"Days of Supply: {days_of_supply:.1f} days\n"
        f"Risk Level: {risk}"
    )
