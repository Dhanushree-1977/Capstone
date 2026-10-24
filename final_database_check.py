
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

tables = [
    "SUPPLIERS",
    "EMISSION_FACTORS",
    "SHIPMENTS",
    "SHIPMENTS_TRUTH",
    "EMISSION_RESULTS",
    "FORECASTS",
    "ALTERNATIVES",
    "CHAT_LOGS",
]

try:
    cursor = conn.cursor()

    print("FINAL CARBON DATABASE CHECK")
    print("---------------------------")

    for table in tables:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM SYS.TABLES
            WHERE SCHEMA_NAME = 'CARBON'
              AND TABLE_NAME = ?
            """,
            (table,),
        )

        exists = cursor.fetchone()[0] > 0

        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM CARBON.{table}")
            count = cursor.fetchone()[0]
            print(f"{table}: EXISTS, {count} records")
        else:
            print(f"{table}: MISSING")

    cursor.close()
finally:
    conn.close()
