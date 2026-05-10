BASE_PATH = "/Volumes/dev_project/bronze/source_system"

INGESTION_CONFIG = [
    {"source": "crm", "path": f"{BASE_PATH}/crm/cust_info/", "table": "crm_cust_info"},
    {"source": "crm", "path": f"{BASE_PATH}/crm/prd_info/", "table": "crm_prd_info"},
    {"source": "crm", "path": f"{BASE_PATH}/crm/sales_details/", "table": "crm_sales_details"},
    {"source": "erp", "path": f"{BASE_PATH}/erp/CUST_AZ12/", "table": "erp_cust_az12"},
    {"source": "erp", "path": f"{BASE_PATH}/erp/LOC_A101/", "table": "erp_loc_a101"},
    {"source": "erp", "path": f"{BASE_PATH}/erp/PX_CAT_G1V2/", "table": "erp_px_cat_g1v2"},
]