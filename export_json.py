import json


def export_killfeed_to_json(filename: str, player_dict: dict):
    serializable_data = {
        player_name: {
            "kills": player_data.kills,
            "deaths": player_data.deaths,
            "assists": player_data.assists,
            "kd": player_data.kd,
        }
        for player_name, player_data in player_dict.items()
    }

    with open(filename, "w") as json_file:
        json.dump(serializable_data, json_file, indent=4)

    print(f"Data successfully exported to {filename}")


def export_utility_damage_to_json(filename: str, total_damage: list):
    # Ensure total_damage is a list of dictionaries

    # Prepare the serializable data
    serializable_data = {
        entry["player"]: {
            "he_damage": entry["he_damage"],
            "molotov_damage": entry["molotov_damage"],
            "utility_damage": entry["utility_damage"],
        }
        for entry in total_damage
    }

    # Write to JSON file
    with open(filename, "w") as json_file:
        json.dump(serializable_data, json_file, indent=4)

    print(f"Data successfully exported to {filename}")
