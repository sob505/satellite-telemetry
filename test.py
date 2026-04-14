import pandas as pd

# Load the satellite telemetry data
data = pd.read_csv("../data/sample_telemetry_data.csv")

# Find the maximum altitude
max_altitude = data["Altitude"].max()

print("Maximum altitude:", max_altitude)

