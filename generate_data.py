
import random
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

# Make the generated dataset reproducible
random.seed(42)

# Save files in the same folder as this Python script
OUTPUT_DIR = Path(__file__).parent
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

suppliers = [
    ("SUP001", "Green Valley Supplies", "India", "Asia", "A"),
    ("SUP002", "Pacific Trade Co", "China", "Asia", "B"),
    ("SUP003", "Euro Goods Ltd", "Germany", "Europe", "A"),
    ("SUP004", "Global Parts Inc", "USA", "North America", "C"),
    ("SUP005", "Southern Logistics", "Australia", "Oceania", "B"),
    ("SUP006", "Nile Industrial Supply", "Egypt", "Africa", "B"),
    ("SUP007", "Sakura Components", "Japan", "Asia", "A"),
    ("SUP008", "Andes Materials", "Brazil", "South America", "C"),
]

transport_modes = ["Road", "Rail", "Sea", "Air"]

# Illustrative factors in kg CO2e per tonne-kilometre.
# These are synthetic demonstration values, not official factors.
emission_factors = {
    "Road": 0.10,
    "Rail": 0.025,
    "Sea": 0.015,
    "Air": 0.60,
}

origins = [
    "Mumbai", "Delhi", "Chennai", "Shanghai",
    "Berlin", "Los Angeles", "Tokyo", "Sydney"
]
destinations = [
    "Bengaluru", "Hyderabad", "Pune", "Kolkata",
    "Singapore", "London", "Toronto", "Dubai"
]

shipments = []
truth = []

start_date = date(2025, 1, 1)

for i in range(1, 501):
    shipment_id = f"SHP{i:04d}"
    supplier_id, *_ = random.choice(suppliers)
    mode = random.choice(transport_modes)

    distance = round(random.uniform(50, 5000), 2)
    weight = round(random.uniform(0.1, 25), 3)

    # Synthetic fuel-use estimate for demonstration.
    fuel = round(distance * weight * random.uniform(0.015, 0.04), 2)

    # Simplified emissions estimate: factor x weight x distance.
    emissions = round(
        emission_factors[mode] * weight * distance, 4
    )

    shipment_date = start_date + timedelta(
        days=random.randint(0, 364)
    )

    # Complete original values for future ML evaluation.
    truth.append({
        "SHIPMENT_ID": shipment_id,
        "TRUE_DISTANCE_KM": distance,
        "TRUE_WEIGHT_TONNES": weight,
        "TRUE_FUEL_LITRES": fuel,
        "TRUE_EMISSIONS_KG": emissions,
    })

    # Add some missing values to simulate incomplete records.
    observed_distance = (
        None if random.random() < 0.08 else distance
    )
    observed_weight = (
        None if random.random() < 0.08 else weight
    )
    observed_fuel = (
        None if random.random() < 0.08 else fuel
    )

    shipments.append({
        "SHIPMENT_ID": shipment_id,
        "SUPPLIER_ID": supplier_id,
        "ORIGIN": random.choice(origins),
        "DESTINATION": random.choice(destinations),
        "TRANSPORT_MODE": mode,
        "DISTANCE_KM": observed_distance,
        "WEIGHT_TONNES": observed_weight,
        "FUEL_LITRES": observed_fuel,
        "SHIPMENT_DATE": shipment_date.isoformat(),
    })

pd.DataFrame(shipments).to_csv(
    OUTPUT_DIR / "shipments.csv", index=False
)
pd.DataFrame(truth).to_csv(
    OUTPUT_DIR / "shipments_truth.csv", index=False
)
pd.DataFrame(suppliers, columns=[
    "SUPPLIER_ID", "SUPPLIER_NAME", "COUNTRY",
    "REGION", "SUSTAINABILITY_RATING"
]).to_csv(OUTPUT_DIR / "suppliers.csv", index=False)

pd.DataFrame([
    {
        "FACTOR_ID": f"FAC{i:03d}",
        "TRANSPORT_MODE": mode,
        "EMISSION_FACTOR": factor,
        "UNIT": "kg CO2e/tonne-km",
        "SOURCE": "Synthetic demonstration value",
    }
    for i, (mode, factor) in enumerate(
        emission_factors.items(), start=1
    )
]).to_csv(OUTPUT_DIR / "emission_factors.csv", index=False)

print("Dataset generation completed!")
print(f"Shipment records: {len(shipments)}")
print(f"Supplier records: {len(suppliers)}")
print("Files created:")
print("- shipments.csv")
print("- shipments_truth.csv")
print("- suppliers.csv")
print("- emission_factors.csv")
