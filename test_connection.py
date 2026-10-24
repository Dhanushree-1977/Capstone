
import os
from dotenv import load_dotenv
from hdbcli import dbapi

load_dotenv()

conn = None

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
    cursor.execute("SELECT CURRENT_USER, CURRENT_SCHEMA FROM DUMMY")
    result = cursor.fetchone()

    print("Connection successful!")
    print("Database login verified.")
    print("Current schema:", result[1])

    cursor.close()

except Exception as e:
    print("Connection failed.")
    print("Error type:", type(e).__name__)
    print("Error details:", str(e))

finally:
    if conn:
        conn.close()
