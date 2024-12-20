from demoparser2 import DemoParser
from demo_data import DemoInfo, PlayerStatsManager

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
    stats_manager.check_for_saves()

    stats_manager.display_player_stats()

    demo_info = DemoInfo(parser)
    demo_info.is_bomb_planted_in_preceding_round(parser)
    demo_info.bomb_planted_test_message(parser)


if __name__ == "__main__":
    main()
