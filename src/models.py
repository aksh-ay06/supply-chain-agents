from __future__ import annotations
from pydantic import BaseModel, Field


class DemandForecast(BaseModel):
    product_id: str
    product_name: str
    current_avg_daily_sales: float
    forecast_next_7d: float
    trend: str = Field(description="up, down, or stable")
    notes: str = ""


class InventoryAlert(BaseModel):
    product_id: str
    product_name: str
    current_stock: int
    reorder_point: int
    avg_daily_sales: float
    days_of_supply: float
    risk_level: str = Field(description="critical, warning, or healthy")
    recommendation: str = ""


class SupplierReport(BaseModel):
    supplier: str
    products_supplied: list[str]
    avg_lead_time_days: float
    avg_unit_cost: float
    reliability_notes: str = ""
