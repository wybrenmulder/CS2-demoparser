from dataclasses import dataclass
from demoparser2 import DemoParser
import export_json
import trades
import utility
import json


@dataclass
class PlayerData:
    kills: int
    deaths: int
    assists: int
    kd: float
    weapon_kills: dict[str, int]

    def __init__(self):
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.kd = 0.0
        self.weapon_kills = {}


demo = DemoParser("./assets/testdemo.dem")
tick_rate = 64
df = demo.parse_player_info()
df_player_hurt = demo.parse_event("player_hurt")
player_dict: dict[str, PlayerData] = {}
players = df
kills = demo.parse_event("player_death", player=["X", "Y"], other=["kills_total"])
utility_damage = utility.utility_damage()


def killfeed():
    for [_, kill] in kills.iterrows():
        # print(kill["attacker_name"], kill["weapon"], kill["user_name"])
        player_dict[kill["attacker_name"]].kills += 1
        player_dict[kill["user_name"]].deaths += 1
        if kill["assister_name"] is not None:
            player_dict[kill["assister_name"]].assists += 1

        if kill["weapon"] not in player_dict[kill["attacker_name"]].weapon_kills:
            player_dict[kill["attacker_name"]].weapon_kills[kill["weapon"]] = 0

        player_dict[kill["attacker_name"]].weapon_kills[kill["weapon"]] += 1


def kdratio():
    for [_, val] in player_dict.items():
        if val.deaths == 0:
            val.kd = val.kills
        else:
            val.kd = val.kills / val.deaths


def export_killfeed_to_json(filename: str):
    serializable_data = {
        player_name: {
            "kills": player_data.kills,
            "deaths": player_data.deaths,
            "assists": player_data.assists,
            "kd": player_data.kd,
            "weapon_kills": player_data.weapon_kills,
        }
        for player_name, player_data in player_dict.items()
    }

    with open(filename, "w") as json_file:
        json.dump(serializable_data, json_file, indent=4)


def main():
    # print(kills)

    for [_, player] in players.iterrows():
        # print(player)
        player_dict[player["name"]] = PlayerData()

    killfeed()
    kdratio()

    export_json.export_killfeed_to_json("assets/killfeed_data.json", player_dict)
    export_json.export_utility_damage_to_json(
        "assets/utility_damage_data.json", utility_damage
    )

    # trades.check_if_death_is_traded()


if __name__ == "__main__":
    main()
