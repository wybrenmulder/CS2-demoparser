from demoparser2 import DemoParser
from demo_data import DemoInfo, PlayerStatsManager

# parser = DemoParser("./assets/testdemo.dem")
parser = DemoParser("./assets/save_clutch_testdemo.dem")


def main():
    demo_info = DemoInfo(parser)

    print(f"Total Rounds Played: {demo_info.rounds}")
    print(f"Tick Rate: {demo_info.tick_rate}")
    print(f"Rounds:\n{demo_info.defined_rounds}")

    stats_manager = PlayerStatsManager(parser)
    stats_manager.process_player_death(parser)
    stats_manager.process_player_hurt(parser)
    stats_manager.calculate_kd()
    stats_manager.calculate_kast()
    stats_manager.calculate_per_round_values(parser)
    stats_manager.calculate_impact()
    stats_manager.calculate_hltv2()

    stats_manager.display_player_stats()


if __name__ == "__main__":
    main()
