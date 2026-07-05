CBN DMB Interest Rates Pipeline | AWS ETL + Power BI

<img width="740" height="413" alt="dashboard" src="https://github.com/user-attachments/assets/a66a4218-9faf-4733-8b43-0189a4e45f21" />


Overview

An end-to-end data engineering pipeline that extracts, transforms, and loads Central Bank of Nigeria (CBN) Deposit Money Bank (DMB) weekly interest rate data into AWS cloud infrastructure, culminating in an interactive Power BI dashboard for analysis.

Problem Statement

CBN publishes weekly lending and deposit rates for all 32 Deposit Money Banks in Nigeria as PDF reports. This data is valuable for businesses, investors, and individuals making financial decisions — but it's locked in unstructured PDFs with no easy way to analyze trends over time.

This pipeline automates the extraction, transformation, and visualization of 12 weeks of CBN rate data (January — March 2026).

Architecture

CBN PDF Reports → Local Python Parser → CSV Files
→ AWS S3 (Raw) → AWS Glue ETL Job → AWS S3 (Processed)
→ AWS Glue Crawler → AWS Glue Data Catalog
→ AWS Athena → Power BI Dashboard (via ODBC)

Key Findings


Coronation Merchant Bank offers the lowest prime lending rate at 19.50% — nearly 8% cheaper than the Q1 average of 26.32%
NOVA Bank offers the highest time deposit rate at 19.66% — best return for savers in Q1 2026
Capital Market & Extraterritorial sectors attract the highest prime rates (~27.7%), while Manufacturing gets the cheapest credit (~24.8%)
Standard Chartered Bank offers the lowest savings rate at just 2.69% — nearly 3x worse than the best option (FSDH at 8.25%)
Prime lending rates rose steadily from 26.0% → 26.5% across Q1 2026
Only 12 of 32 banks reported demand deposit rates — 20 banks don't offer this product


Tech Stack

LayerTechnologyData ExtractionPython, pdfplumberCloud StorageAWS S3ETLAWS Glue (Python Shell)Query EngineAWS AthenaData CatalogAWS Glue Data CatalogVisualizationMicrosoft Power BILanguagePython 3, SQL

Dataset


Source: Central Bank of Nigeria (CBN) official weekly publications
Period: January 2, 2026 — March 20, 2026 (12 weeks)
Banks covered: 32 Deposit Money Banks (DMBs)
Deposit rows: 384 (32 banks × 12 weeks)
Lending rows: 8,448 (32 banks × 22 sectors × 12 weeks)


Dashboard Pages


Overview — KPI cards, sector lending rates, savings rate by bank, rate trend over time
Lending Rates Analysis — Prime rate by sector, max rate by sector, prime vs max comparison
Deposit Rates Analysis — Savings, demand, and time deposit rates by bank
Bank Spotlight — Best bank per sector (lowest prime rate) — interactive matrix
Rate Trends — Prime, savings, and max rate movement across Q1 2026


Project Structure

cbn-rates-aws-etl/
├── scripts/
│   └── batch_convert.py      # Local PDF → CSV converter (12 PDFs)
├── data/
│   └── processed/
│       ├── all_deposit_rates.csv
│       └── all_lending_rates.csv
├── cbn_rates_dashboard.pbix  # Power BI dashboard file
└── README.md

AWS Infrastructure


S3 Buckets: cbn-rates-raw-2026 (PDFs + CSVs), cbn-rates-processed-2026 (cleaned data)
Glue Job: cbn-rates-etl — reads CSVs from S3, transforms, writes to processed bucket
Glue Crawler: cbn-rates-crawler — catalogs processed data
Athena Database: cbn_rates_db — tables: deposit_rates, lending_rates


How to Run


Clone the repo
Install dependencies: pip install pdfplumber pandas
Place CBN PDF files in data/raw/ named as cbn_rates_YYYY-MM-DD.pdf
Run: python scripts/batch_convert.py
Upload CSVs to S3 and trigger the Glue job
Query via Athena or connect Power BI via ODBC


Author

Emmanuel Balogun | Data Analyst
GitHub • LinkedIn
