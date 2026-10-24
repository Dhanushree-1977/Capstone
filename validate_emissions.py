
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

    cursor.execute("""
        SELECT
            COUNT(*) AS RESULT_COUNT,
            COUNT(DISTINCT SHIPMENT_ID) AS UNIQUE_SHIPMENTS,
            MIN(TOTAL_EMISSIONS_KG) AS MIN_EMISSIONS,
            MAX(TOTAL_EMISSIONS_KG) AS MAX_EMISSIONS,
            SUM(TOTAL_EMISSIONS_KG) AS TOTAL_EMISSIONS
        FROM CARBON.EMISSION_RESULTS
    """)

    result = cursor.fetchone()

    print("EMISSION VALIDATION")
    print("-------------------")
    print("Total results:", result[0])
    print("Unique shipments:", result[1])
    print("Minimum emissions (kg CO2e):", result[2])
    print("Maximum emissions (kg CO2e):", result[3])
    print("Total emissions (kg CO2e):", result[4])

    cursor.execute("""
        SELECT COUNT(*)
        FROM CARBON.EMISSION_RESULTS R
        LEFT JOIN CARBON.SHIPMENTS S
          ON R.SHIPMENT_ID = S.SHIPMENT_ID
        WHERE S.SHIPMENT_ID IS NULL
    """)

    print("Results without matching shipments:", cursor.fetchone()[0])

    cursor.close()
finally:
    conn.close()
