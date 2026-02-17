from src.tools.data_loader import query_sales_data, get_product_list, get_latest_inventory, get_supplier_summary
from src.tools.forecasting import forecast_demand, calculate_days_of_supply
from src.tools.search import web_search
from src.tools.report_generator import generate_report

DEMAND_TOOLS = [query_sales_data, get_product_list, forecast_demand, generate_report]
INVENTORY_TOOLS = [get_latest_inventory, get_product_list, calculate_days_of_supply, generate_report]
SUPPLIER_TOOLS = [get_supplier_summary, query_sales_data, web_search, generate_report]
ALL_TOOLS = [query_sales_data, get_product_list, get_latest_inventory, get_supplier_summary,
             forecast_demand, calculate_days_of_supply, web_search, generate_report]
