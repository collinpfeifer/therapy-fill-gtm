import os
import json

# Function to read therapist data from JSON files (with arrays) and remove duplicates
def load_therapist_data(data_dir: str):
    therapists = []
    seen_uuids_ids = set()  # Set to track unique UUID and ID pairs

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            with open(os.path.join(data_dir, filename), "r") as file:
                try:
                    data = json.load(file)
                    if isinstance(data, list):  # Check if the JSON is an array
                        for therapist in data:
                            therapist_uuid = therapist.get("uuid")
                            therapist_id = therapist.get("id")

                            if (therapist_uuid, therapist_id) in seen_uuids_ids:
                                continue  # Skip duplicate entry

                            seen_uuids_ids.add((therapist_uuid, therapist_id))
                            therapists.append(therapist)
                    else:
                        print(f"Skipping non-array JSON file: {filename}")
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON file: {filename}")
