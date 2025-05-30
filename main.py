from demoparser2 import DemoParser
from demo_data import DemoInfo, PlayerStatsManager

parser = DemoParser("./assets/save_clutch_testdemo.dem")


def main():
    demo_info = DemoInfo(parser)
    stats_manager = PlayerStatsManager(parser)

    demo_info.define_rounds(parser)

    stats_manager.declare_player(parser)

    print(f"Total Rounds Played: {demo_info.rounds}")
    print(f"Tick Rate: {demo_info.tick_rate}")
    print(f"Rounds:\n{demo_info.defined_rounds}")

    stats_manager.process_player_death(parser)
    # stats_manager.process_player_hurt(parser)
    # stats_manager.calculate_kd()
    # stats_manager.calculate_kast()
    # stats_manager.calculate_per_round_values(parser)
    # stats_manager.calculate_impact()
    # stats_manager.calculate_hltv2()
    # stats_manager.check_for_saves()

    # stats_manager.display_player_stats()

    stats_manager.switch_sides(parser)
    stats_manager.process_alive_at_round_end(parser)
    stats_manager.get_winner_of_rounds(parser)
    stats_manager.analyze_round_end_scenario(parser)


if __name__ == "__main__":
    main()
