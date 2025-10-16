"""save_json.py"""
import json
from datetime import datetime
from typing import Dict, List
import os

json_dir = "fhir_data/json"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def save_json_to_local(data_store: Dict[str, List[Dict]]) -> None:
    """Saves categorized JSON data to local file system."""
    for category in data_store:
        print(f"This {category} saved in following location")
        print(f"Location : {json_dir}/{category}/")
        json_local(
            data_store[category],
            category,
            f"{category}_{timestamp}.json"
        )

def json_local(data: List[Dict], folder_name: str, filename: str) -> None:
    """Writes JSON data to a local subfolder and prints metadata."""
    local_path = os.path.join(json_dir, folder_name)
    os.makedirs(local_path, exist_ok=True)

    file_path = os.path.join(local_path, filename)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        file_size_kb = round(os.path.getsize(file_path) / 1024, 2)
        print(f"File: {os.path.basename(file_path)}")
        print(f"Size: {file_size_kb} KB")
        print(f"Data saved successfully to {file_path}\n")

    except Exception as e:
        print(f"Failed to save data locally: {e}")