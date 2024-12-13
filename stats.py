from pymongo import MongoClient
import matplotlib.pyplot as plt
import pandas as pd

# Connect to the local MongoDB instance
client = MongoClient("mongodb://localhost:27017/")
db = client["catan"]
collection = db["action_logs"]

# Query the collection
query = {"action": "BUILD_SETTLEMENT"}
fields = {"cost": 1, "turn_number": 1, "player_id": 1, "_id": 0}

cursor = collection.find(query, fields)

# Convert to a DataFrame for easy manipulation (optional but convenient)
df = pd.DataFrame(list(cursor))

# If the query returned no documents, ensure we have data before proceeding
if df.empty:
    print("No documents found for action = BUILD_SETTLEMENT.")
    exit(0)

# Group by player_id
grouped = df.groupby("player_id")

# Create one scatter plot per player_id
for player_id, group_data in grouped:
    # Sort by turn_number if desired (not strictly necessary)
    group_data = group_data.sort_values("turn_number")

    plt.figure(figsize=(8, 6))
    plt.scatter(group_data["turn_number"], group_data["cost"], alpha=0.7)
    plt.title(f"Cost vs Turn Number for Player ID: {player_id}")
    plt.xlabel("Turn Number")
    plt.ylabel("Cost")
    plt.grid(True)
    plt.show()
