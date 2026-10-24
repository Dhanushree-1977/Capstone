
import os
from datetime import date
from dotenv import load_dotenv
from hdbcli import dbapi

load_dotenv()

conn = None
cursor = None

try:
    conn = dbapi.connect(
        address=os.getenv("HANA_HOST"),
        port=int(os.getenv("HANA_PORT", "443")),
        user=os.getenv("HANA_USER"),
        password=os.getenv("HANA_PASSWORD"),
        encrypt=True,
        sslValidateCertificate=True,
    )

    cursor = conn.cursor()

    # Read shipments that have the measurements needed for calculation
    cursor.execute("""
        SELECT
            S.SHIPMENT_ID,
            S.DISTANCE_KM,
            S.WEIGHT_TONNES,
            S.TRANSPORT_MODE,
            E.EMISSION_FACTOR
        FROM CARBON.SHIPMENTS S
        JOIN CARBON.EMISSION_FACTORS E
          ON S.TRANSPORT_MODE = E.TRANSPORT_MODE
        WHERE S.DISTANCE_KM IS NOT NULL
          AND S.WEIGHT_TONNES IS NOT NULL
    """)

    shipments = cursor.fetchall()
    results = []

    for shipment in shipments:
        shipment_id = shipment[0]
        distance = float(shipment[1])
        weight = float(shipment[2])
        transport_mode = shipment[3]
        factor = float(shipment[4])

        # Simplified demonstration formula
        emissions = distance * weight * factor

        # Emissions per tonne-kilometre
        tonne_km = distance * weight
        emissions_per_tonne_km = (
            emissions / tonne_km if tonne_km > 0 else 0
        )

        results.append((
            f"RES{len(results) + 1:04d}",
            shipment_id,
            round(emissions, 4),
            round(emissions_per_tonne_km, 6),
            date.today(),
            "Synthetic transport-mode factor"
        ))

    if results:
        cursor.executemany("""
            INSERT INTO CARBON.EMISSION_RESULTS
            (RESULT_ID, SHIPMENT_ID, TOTAL_EMISSIONS_KG,
             EMISSIONS_PER_TONNE_KM, CALCULATION_DATE,
             CALCULATION_METHOD)
            VALUES (?, ?, ?, ?, ?, ?)
        """, results)

    conn.commit()

    print("Emission calculation completed!")
    print("Shipments processed:", len(results))
    print("Emission results saved to CARBON.EMISSION_RESULTS")

except Exception as e:
    if conn:
        conn.rollback()
    print("Emission calculation failed.")
    print("Error type:", type(e).__name__)
    print("Error details:", str(e))

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
