from dataclasses import dataclass
from demoparser2 import DemoParser
import export_json
import hltv_rating
import parser
import trades
import utility
import json


@dataclass
class PlayerData:
    kills: int
    deaths: int
    assists: int
    kd: float

    def __init__(self):
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.kd = 0.0


tick_rate = 64
df = parser.demo.parse_player_info()
df_player_hurt = parser.demo.parse_event("player_hurt")
player_dict: dict[str, PlayerData] = {}
players = df
kills = parser.demo.parse_event(
    "player_death", player=["X", "Y"], other=["kills_total"]
)
utility_damage = utility.utility_damage()


def killfeed():
    for [_, kill] in kills.iterrows():
        attacker = kill["attacker_name"]
        victim = kill["user_name"]
        assister = kill.get("assister_name", None)

        # print(kill["attacker_name"], kill["weapon"], kill["user_name"])

        # Update player_dict with kills, deaths, assists
        player_dict[attacker].kills += 1
        player_dict[victim].deaths += 1
        if assister and assister != attacker:
            player_dict[assister].assists += 1


def kdratio():
    for [_, val] in player_dict.items():
        if val.deaths == 0:
            val.kd = val.kills
        else:
            val.kd = val.kills / val.deaths


def main():
    # Initialize player data and parse kills/assists
    for [_, player] in players.iterrows():
        player_dict[player["name"]] = PlayerData()

    # Process killfeed to update stats
    killfeed()
    kdratio()

    # Export data to JSON
    # export_json.export_killfeed_to_json("assets/killfeed_data.json", player_dict)
    # export_json.export_utility_damage_to_json("assets/utility_damage_data.json", utility_damage)

    # Process trades
    trades.check_if_death_is_traded()


if __name__ == "__main__":
    main()
