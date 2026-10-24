
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from hdbcli import dbapi

load_dotenv()

DATA_DIR = Path(__file__).parent

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

    # Load supplier records
    suppliers = pd.read_csv(DATA_DIR / "suppliers.csv")
    supplier_rows = [
        tuple(row)
        for row in suppliers.itertuples(index=False, name=None)
    ]

    cursor.executemany(
        """
        INSERT INTO CARBON.SUPPLIERS
        (SUPPLIER_ID, SUPPLIER_NAME, COUNTRY, REGION,
         SUSTAINABILITY_RATING)
        VALUES (?, ?, ?, ?, ?)
        """,
        supplier_rows,
    )

    # Load emission factors
    factors = pd.read_csv(DATA_DIR / "emission_factors.csv")
    factor_rows = [
        tuple(row)
        for row in factors.itertuples(index=False, name=None)
    ]

    cursor.executemany(
        """
        INSERT INTO CARBON.EMISSION_FACTORS
        (FACTOR_ID, TRANSPORT_MODE, EMISSION_FACTOR, UNIT, SOURCE)
        VALUES (?, ?, ?, ?, ?)
        """,
        factor_rows,
    )

    # Load shipments, converting missing values to SQL NULL
    shipments = pd.read_csv(DATA_DIR / "shipments.csv")
    shipments = shipments.astype(object).where(
        pd.notna(shipments), None
    )
    shipment_rows = [
        tuple(row)
        for row in shipments.itertuples(index=False, name=None)
    ]

    cursor.executemany(
        """
        INSERT INTO CARBON.SHIPMENTS
        (SHIPMENT_ID, SUPPLIER_ID, ORIGIN, DESTINATION,
         TRANSPORT_MODE, DISTANCE_KM, WEIGHT_TONNES,
         FUEL_LITRES, SHIPMENT_DATE)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        shipment_rows,
    )

    # Load the reference values used for later ML evaluation
    truth = pd.read_csv(DATA_DIR / "shipments_truth.csv")
    truth_rows = [
        tuple(row)
        for row in truth.itertuples(index=False, name=None)
    ]

    cursor.executemany(
        """
        INSERT INTO CARBON.SHIPMENTS_TRUTH
        (SHIPMENT_ID, TRUE_DISTANCE_KM, TRUE_WEIGHT_TONNES,
         TRUE_FUEL_LITRES, TRUE_EMISSIONS_KG)
        VALUES (?, ?, ?, ?, ?)
        """,
        truth_rows,
    )

    conn.commit()

    print("Data loaded successfully!")
    print("Suppliers:", len(supplier_rows))
    print("Emission factors:", len(factor_rows))
    print("Shipments:", len(shipment_rows))
    print("Shipment reference records:", len(truth_rows))

except Exception as e:
    if conn:
        conn.rollback()
    print("Data loading failed.")
    print("Error type:", type(e).__name__)
    print("Error details:", str(e))
    print("Check the error before trying the script again.")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
