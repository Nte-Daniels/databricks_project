# Bike Lakehouse — Medallion Architecture Pipeline (Incremental Load)

## The Problem

A bike retailer selling through both online and physical stores was running two separate systems — a CRM for customer and sales data, and an ERP for product and location data. Neither talked to the other.

Finance couldn't trust the numbers because the same records appeared in both systems with slight differences. Analysts couldn't build reports because there was no single place where everything lived together. And when the CEO asked "how much did we sell last month?", the answer depended on which system you looked at.

This pipeline fixes that. It pulls data from both systems, cleans it, resolves the inconsistencies, and produces three ready-to-use tables that give a single, consistent view of customers, products, and sales.

---

## What It Produces

By the time this pipeline finishes, three tables are available for reporting and dashboards:

**Customers** — every customer with their location, demographics, and account history. No duplicates, no conflicting records.

**Products** — the full product catalogue with categories and pricing, including historical versions so analysts can see what a product cost at any point in time.

**Sales** — 60,398 transactions linked to the correct customer and product, ready to slice by region, category, date, or any other dimension.

---

## How It Works

The pipeline runs in three stages — Bronze, Silver, and Gold. Think of it as a production line.

**Bronze** is raw storage. Data comes in from CSV files and gets saved exactly as-is, with a timestamp and source tag. Nothing gets changed or deleted. If something goes wrong downstream, the original data is always there.

**Silver** is where cleaning happens. Duplicates get removed. Dates get fixed. Abbreviations get standardised. Customer and product records get versioned — so if a customer changes their address or a product price changes, the old record is preserved alongside the new one. No history is lost.

**Gold** is what analysts and executives actually use. The cleaned Silver tables get joined together into three final tables: one for customers, one for products, one for sales. These are the tables that feed dashboards and reports.

```
Raw CSV files
      ↓
   Bronze  (store everything as-is)
      ↓
   Silver  (clean, deduplicate, version)
      ↓
    Gold   (join and model for reporting)
```

The pipeline runs automatically every night at 2:00 AM so the data is fresh by the time anyone sits down to work in the morning.

---

## Tech Stack

- **Databricks** — compute and orchestration
- **PySpark** — all transformations
- **Delta Lake** — storage format across all layers
- **Unity Catalog** — data governance and table management
- **Databricks Workflows** — pipeline scheduling and DAG orchestration
- **GitHub** — version control

---

## Folder Structure

```
bike_lakehouse/
├── Code/
│   ├── bronze/
│   │   ├── Bronze.ipynb          # Incremental ingestion for all 6 source tables
│   │   └── bronze_config.py      # Table config — paths, sources, table names
│   ├── silver/
│   │   ├── silver_crm_cust_info.ipynb       # SCD2
│   │   ├── silver_crm_prd_info.ipynb        # SCD2
│   │   ├── silver_crm_sales_details.ipynb   # Incremental append
│   │   ├── silver_erp_cust_az12.ipynb       # Overwrite
│   │   ├── silver_erp_loc_a101.ipynb        # Overwrite
│   │   └── silver_erp_px_cat_g1v2.ipynb     # Overwrite
│   ├── gold/
│   │   ├── gold_dim_customers.ipynb
│   │   ├── gold_dim_products.ipynb
│   │   └── gold_fact_sales.ipynb
│   └── workflows/
├── Datasets/
└── README.md
```

---

## Data Sources

Six tables ingested from two source systems:

| Source | Table | What It Contains |
|---|---|---|
| CRM | `crm_cust_info` | Customer names, gender, marital status |
| CRM | `crm_prd_info` | Product catalogue with pricing history |
| CRM | `crm_sales_details` | Sales transactions |
| ERP | `erp_cust_az12` | Customer birthdates and gender |
| ERP | `erp_loc_a101` | Customer country |
| ERP | `erp_px_cat_g1v2` | Product category reference |

---

## Key Engineering Decisions

**Incremental ingestion** — Bronze never re-processes files it has already seen. Each run checks which files are new and only loads those.

**SCD Type 2 for dimensions** — customer and product records are versioned, not overwritten. When a product price changes, the old record is closed and a new one is created. History is permanent.

**Hash-based change detection** — instead of comparing every column manually, the pipeline hashes the business columns and compares hashes. If the hash changes, a new version is created. If it doesn't, the record is skipped.

**Deterministic surrogate keys** — every record gets a SHA-256 key derived from its natural key and date. Unlike auto-increment IDs, these are consistent across re-runs — re-running the pipeline produces the same keys every time.

---

## How to Run

### Prerequisites
- Databricks workspace with Unity Catalog enabled
- Catalog `dev_project` with schemas `bronze`, `silver`, `gold`
- Source CSV files in `dbfs:/Volumes/dev_project/bronze/source_system/`

### Manual run
Run notebooks in order: Bronze → Silver → Gold.

### Automated run
The pipeline runs as a Databricks Workflow (`bike_lakehouse_pipeline`) on a daily schedule at 02:00 AM. Bronze runs first. All six Silver tables run in parallel after Bronze completes. Gold dimensions run after their Silver dependencies finish. `fact_sales` runs last.

---

## Catalog

```
dev_project
├── bronze
│   ├── crm_cust_info
│   ├── crm_prd_info
│   ├── crm_sales_details
│   ├── erp_cust_az12
│   ├── erp_loc_a101
│   └── erp_px_cat_g1v2
├── silver
│   ├── customer_info
│   ├── crm_prd_info
│   ├── crm_sales_details
│   ├── erp_cust_az12
│   ├── erp_loc_a101
│   └── erp_px_cat_g1v2
└── gold
    ├── dim_customers
    ├── dim_products
    └── fact_sales
```
