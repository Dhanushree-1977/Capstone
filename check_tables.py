
import os
from dotenv import load_dotenv
from hdbcli import dbapi

load_dotenv()

conn = dbapi.connect(
    address=os.getenv("HANA_HOST"),
    port=int(os.getenv("HANA_PORT", "443")),
    user=os.getenv("HANA_USER"),
    password=os.getenv("HANA_PASSWORD"),
    encrypt=True,
    sslValidateCertificate=True,
)

try:
    cursor = conn.cursor()

    tables = [
    "SUPPLIERS",
    "EMISSION_FACTORS",
    "SHIPMENTS",
    "SHIPMENTS_TRUTH",
    "EMISSION_RESULTS",
]

    print("DATABASE VERIFICATION")
    print("---------------------")

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM CARBON.{table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")

    cursor.execute("""
        SELECT COUNT(*)
        FROM CARBON.SHIPMENTS
        WHERE DISTANCE_KM IS NULL
           OR WEIGHT_TONNES IS NULL
           OR FUEL_LITRES IS NULL
    """)
    missing_count = cursor.fetchone()[0]
    print("Shipments with at least one missing value:", missing_count)

    cursor.close()
finally:
    conn.close()
