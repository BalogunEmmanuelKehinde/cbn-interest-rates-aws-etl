import pdfplumber
import pandas as pd
import os
import glob

print("Batch conversion started...")

# -------------------------
# CONFIG
# -------------------------
RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")

# -------------------------
# CONSTANTS
# -------------------------
BANK_NAMES = [
    "ACCESS BANK", "ALPHA MORGAN BANK", "CITI BANK",
    "CORONATION MERCHANT BANK", "ECOBANK", "FBN QUEST MERCHANT BANK",
    "FCMB", "FIDELITY BANK", "FIRST BANK OF NIGERIA",
    "FSDH MERCHANT BANK", "GLOBUS BANK LTD", "GREENWICH MERCHANT BANK",
    "GUARANTY TRUST BANK", "KEYSTONE BANK LTD", "NOVA BANK",
    "OPTIMUS BANK", "PARALLEX BANK", "POLARIS BANK",
    "PREMIUM TRUST BANK", "PROVIDUS BANK", "RAND MERCHANT BANK NIG. LTD",
    "SIGNATURE BANK", "STANBIC IBTC", "STANDARD CHARTERED BANK",
    "STERLING BANK", "SUNTRUST BANK", "TATUM BANK",
    "UNITED BANK FOR AFRICA", "UNION BANK", "UNITY BANK",
    "WEMA BANK", "ZENITH BANK",
]

SECTOR_ROWS = {
    10: "AGRICULTURE, FORESTRY AND FISHING",
    12: "MINING & QUARRYING",
    14: "MANUFACTURING",
    16: "REAL ESTATE ACTIVITIES",
    18: "PUBLIC UTILITIES",
    20: "GENERAL COMMERCE",
    22: "TRANSPORTATION & STORAGE",
    24: "FINANCE & INSURANCE",
    26: "GENERAL",
    28: "GOVERNMENT",
    30: "WATER SUPPLY, SEWAGE, WASTE MANAGEMENT AND REMEDIATION",
    32: "CONSTRUCTION",
    34: "INFORMATION AND COMMUNICATION",
    36: "PROFESSIONAL, SCIENTIFIC AND TECHNICAL ACTIVITIES",
    38: "ADMINISTRATIVE AND SUPPORT SERVICE ACTIVITIES",
    40: "EDUCATION",
    42: "HUMAN HEALTH AND SOCIAL WORK ACTIVITIES",
    44: "ARTS, ENTERTAINMENT AND RECREATION",
    46: "ACTIVITIES OF EXTRATERRITORIAL ORGANIZATIONS AND BODIES",
    48: "POWER AND ENERGY",
    50: "CAPITAL MARKET",
    52: "OIL & GAS",
}

DEPOSIT_ROWS = {
    "demand_deposit_rate": 5,
    "savings_deposit_rate": 6,
    "time_deposit_rate": 7,
}

# -------------------------
# HELPERS
# -------------------------
def clean_rate(value):
    if pd.isna(value):
        return None
    s = str(value).replace(" ", "").strip()
    if s == "-" or s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None

def extract_date_from_filename(filename):
    base = os.path.basename(filename)
    date_str = base.replace("cbn_rates_", "").replace(".pdf", "")
    return date_str

def process_pdf(pdf_path):
    reporting_date = extract_date_from_filename(pdf_path)
    print(f"Processing: {pdf_path} → date: {reporting_date}")

    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table)
                all_tables.append(df)

    if not all_tables:
        print(f"  No tables found — skipping")
        return None, None

    raw_df = pd.concat(all_tables, ignore_index=True)
    data_cols = list(raw_df.columns[1:-1])

    # Deposit rates
    deposit_records = []
    for i, bank in enumerate(BANK_NAMES):
        if i >= len(data_cols):
            break
        col = data_cols[i]
        record = {"bank_name": bank, "reporting_date": reporting_date}
        for rate_name, row_idx in DEPOSIT_ROWS.items():
            try:
                record[rate_name] = clean_rate(raw_df.iloc[row_idx][col])
            except IndexError:
                record[rate_name] = None
        deposit_records.append(record)

    # Lending rates
    lending_records = []
    for prime_row, sector in SECTOR_ROWS.items():
        max_row = prime_row + 1
        for i, bank in enumerate(BANK_NAMES):
            if i >= len(data_cols):
                break
            col = data_cols[i]
            try:
                lending_records.append({
                    "bank_name": bank,
                    "sector": sector,
                    "prime_rate": clean_rate(raw_df.iloc[prime_row][col]),
                    "max_rate": clean_rate(raw_df.iloc[max_row][col]),
                    "reporting_date": reporting_date,
                })
            except IndexError:
                lending_records.append({
                    "bank_name": bank,
                    "sector": sector,
                    "prime_rate": None,
                    "max_rate": None,
                    "reporting_date": reporting_date,
                })

    return pd.DataFrame(deposit_records), pd.DataFrame(lending_records)

# -------------------------
# MAIN
# -------------------------
pdf_files = sorted(glob.glob(os.path.join(RAW_DIR, "cbn_rates_*.pdf")))
print(f"Found {len(pdf_files)} PDFs to process")

all_deposits = []
all_lending = []

for pdf_path in pdf_files:
    deposit_df, lending_df = process_pdf(pdf_path)
    if deposit_df is not None:
        all_deposits.append(deposit_df)
        all_lending.append(lending_df)

final_deposits = pd.concat(all_deposits, ignore_index=True)
final_lending = pd.concat(all_lending, ignore_index=True)

print(f"\nTotal deposit rows: {len(final_deposits)}")
print(f"Total lending rows: {len(final_lending)}")

# Save
final_deposits.to_csv(os.path.join(PROCESSED_DIR, "all_deposit_rates.csv"), index=False)
final_lending.to_csv(os.path.join(PROCESSED_DIR, "all_lending_rates.csv"), index=False)

print("\nDone! Files saved to data/processed/")
print("  → all_deposit_rates.csv")
print("  → all_lending_rates.csv")